# contacts_view.py - Version avec boutons compacts (icônes uniquement)
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QLineEdit, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QFileDialog, QScrollArea,
    QSizePolicy, QDialog, QComboBox, QMenu
)
from PySide6.QtCore import Qt, QTimer, Signal, QSize
from PySide6.QtGui import QFont, QColor, QAction, QBrush

from addons.Automobiles.security.access_control import Permissions, SecurityManager
from addons.Automobiles.views.contact_form_view import ContactForm
from addons.Automobiles.reports.pdf_generator import generate_contact_pdf
from core.logger import logger


class ContactListView(QWidget):
    """Interface professionnelle pour la gestion des contacts"""
    
    contact_selected = Signal(object)
    contact_updated = Signal()
    
    def __init__(self, controller, current_user):
        super().__init__()
        self.controller = controller
        self.current_user = current_user
        self.all_contacts = []
        self.filtered_contacts = []
        self.selected_contacts = []
        
        self.setup_ui()
        self.apply_security_policy()
        self.load_contacts()
        self.setup_shortcuts()
    
    def setup_ui(self):
        """Configure l'interface utilisateur avec ScrollArea"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Scroll area principale
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #f0f2f5;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #e4e7eb;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #cbd5e1;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #94a3b8;
            }
        """)
        
        container = QWidget()
        container.setStyleSheet("background-color: #f0f2f5;")
        self.container_layout = QVBoxLayout(container)
        self.container_layout.setContentsMargins(24, 24, 24, 24)
        self.container_layout.setSpacing(24)
        
        # Sections
        self._create_header()
        self._create_search_bar()
        self._create_stats_panel()
        self._create_toolbar()
        self._create_enhanced_table()
        self._create_status_bar()
        
        self.container_layout.addSpacing(20)
        self.scroll_area.setWidget(container)
        main_layout.addWidget(self.scroll_area)
        self._apply_global_style()
    
    def _apply_global_style(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f2f5;
                font-family: 'Segoe UI', 'Roboto', sans-serif;
                font-size: 13px;
            }
            QFrame {
                background-color: white;
                border-radius: 12px;
            }
            QLineEdit, QComboBox {
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 10px 14px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #3b82f6;
                outline: none;
            }
            QPushButton {
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #f8fafc;
            }
        """)
    
    def _create_header(self):
        header_frame = QFrame()
        header_frame.setMinimumHeight(120)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e293b, stop:1 #0f172a);
                border-radius: 16px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 20, 30, 20)
        
        title_container = QVBoxLayout()
        title_container.setSpacing(8)
        
        title = QLabel("📇 Gestion des Contacts")
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: white;")
        
        subtitle = QLabel("Gérez efficacement tous vos contacts, clients et prospects")
        subtitle.setStyleSheet("font-size: 14px; color: #94a3b8;")
        
        title_container.addWidget(title)
        title_container.addWidget(subtitle)
        
        self.counter_label = QLabel("0 contact(s)")
        self.counter_label.setStyleSheet("""
            background-color: #3b82f6;
            color: white;
            padding: 10px 24px;
            border-radius: 30px;
            font-weight: 600;
            font-size: 15px;
        """)
        
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        header_layout.addWidget(self.counter_label)
        
        self.container_layout.addWidget(header_frame)
    
    def _create_search_bar(self):
        search_frame = QFrame()
        search_frame.setStyleSheet("QFrame { background-color: white; border-radius: 12px; }")
        
        search_layout = QVBoxLayout(search_frame)
        search_layout.setContentsMargins(20, 20, 20, 20)
        search_layout.setSpacing(15)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par nom, téléphone, email, adresse...")
        self.search_input.setMinimumHeight(45)
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_input)
        
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(15)
        
        type_container = QVBoxLayout()
        type_container.setSpacing(5)
        type_label = QLabel("Type de contact")
        type_label.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600;")
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Tous les types", "Assuré", "Prospect", "Partenaire", "Fournisseur"])
        self.type_filter.setMinimumHeight(40)
        self.type_filter.currentTextChanged.connect(self.on_filter_changed)
        type_container.addWidget(type_label)
        type_container.addWidget(self.type_filter)
        
        status_container = QVBoxLayout()
        status_container.setSpacing(5)
        status_label = QLabel("Statut")
        status_label.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600;")
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Tous les statuts", "Actif", "Inactif", "En attente"])
        self.status_filter.setMinimumHeight(40)
        self.status_filter.currentTextChanged.connect(self.on_filter_changed)
        status_container.addWidget(status_label)
        status_container.addWidget(self.status_filter)
        
        date_container = QVBoxLayout()
        date_container.setSpacing(5)
        date_label = QLabel("Date de création")
        date_label.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600;")
        self.date_filter = QComboBox()
        self.date_filter.addItems(["Toutes les dates", "Aujourd'hui", "Cette semaine", "Ce mois", "Cette année"])
        self.date_filter.setMinimumHeight(40)
        self.date_filter.currentTextChanged.connect(self.on_filter_changed)
        date_container.addWidget(date_label)
        date_container.addWidget(self.date_filter)
        
        reset_btn = QPushButton("🔄 Réinitialiser")
        reset_btn.setMinimumHeight(40)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #475569;
                font-weight: 600;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        reset_btn.clicked.connect(self.reset_filters)
        
        filters_layout.addLayout(type_container, 1)
        filters_layout.addLayout(status_container, 1)
        filters_layout.addLayout(date_container, 1)
        filters_layout.addWidget(reset_btn, 1)
        
        search_layout.addLayout(filters_layout)
        self.container_layout.addWidget(search_frame)
    
    def _create_stats_panel(self):
        stats_frame = QFrame()
        stats_frame.setStyleSheet("QFrame { background-color: white; border-radius: 12px; }")
        
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setContentsMargins(20, 20, 20, 20)
        stats_layout.setSpacing(15)
        
        stats_title = QLabel("📊 Tableau de bord")
        stats_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #1e293b;")
        stats_layout.addWidget(stats_title)
        
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        
        self.stats_cards = {}
        stats_data = [
            ("total", "Total", "📊", "#3b82f6"),
            ("assures", "Assurés", "✅", "#10b981"),
            ("prospects", "Prospects", "🎯", "#f59e0b"),
            ("actifs", "Actifs", "⭐", "#8b5cf6")
        ]
        
        for stat_key, label, icon, color in stats_data:
            card = self._create_stat_card(icon, label, "0", color, stat_key)
            cards_layout.addWidget(card)
            self.stats_cards[stat_key] = card
        
        quick_export = QPushButton("📎 Export rapide")
        quick_export.setMinimumHeight(50)
        quick_export.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #059669; }
        """)
        quick_export.clicked.connect(self.export_to_csv)
        cards_layout.addWidget(quick_export)
        
        stats_layout.addLayout(cards_layout)
        self.container_layout.addWidget(stats_frame)
    
    def _create_stat_card(self, icon, label, value, color, stat_key):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color}08;
                border: 1px solid {color}20;
                border-radius: 12px;
            }}
        """)
        card.setMinimumHeight(100)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 36px;")
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 800;
            color: {color};
        """)
        value_label.setObjectName(f"stat_{stat_key}")
        
        name_label = QLabel(label)
        name_label.setStyleSheet("font-size: 12px; color: #6b7280; font-weight: 500;")
        
        text_layout.addWidget(value_label)
        text_layout.addWidget(name_label)
        
        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        layout.addStretch()
        
        return card
    
    def _create_toolbar(self):
        toolbar_frame = QFrame()
        toolbar_frame.setStyleSheet("QFrame { background-color: white; border-radius: 12px; }")
        
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(20, 15, 20, 15)
        toolbar_layout.setSpacing(12)
        
        self.add_btn = self._create_action_button("➕ Nouveau contact", "#3b82f6")
        self.add_btn.clicked.connect(self.on_add_contact)
        
        self.edit_btn = self._create_action_button("✏️ Modifier", "#8b5cf6")
        self.edit_btn.clicked.connect(self.on_edit_contact)
        self.edit_btn.setEnabled(False)
        
        self.delete_btn = self._create_action_button("🗑️ Supprimer", "#ef4444")
        self.delete_btn.clicked.connect(self.on_delete_contact)
        self.delete_btn.setEnabled(False)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet("background-color: #e5e7eb; max-width: 1px;")
        separator.setFixedWidth(1)
        
        self.export_csv_btn = self._create_action_button("📄 CSV", "#6b7280")
        self.export_csv_btn.clicked.connect(self.export_to_csv)
        
        self.export_pdf_btn = self._create_action_button("📑 PDF", "#6b7280")
        self.export_pdf_btn.clicked.connect(self.export_to_pdf)
        
        refresh_btn = self._create_action_button("🔄 Actualiser", "#6b7280")
        refresh_btn.clicked.connect(self.load_contacts)
        
        self.audit_btn = self._create_action_button("📜 Audit", "#6b7280")
        self.audit_btn.clicked.connect(self.show_audit_logs)
        
        toolbar_layout.addWidget(self.add_btn)
        toolbar_layout.addWidget(self.edit_btn)
        toolbar_layout.addWidget(self.delete_btn)
        toolbar_layout.addWidget(separator)
        toolbar_layout.addWidget(self.export_csv_btn)
        toolbar_layout.addWidget(self.export_pdf_btn)
        toolbar_layout.addWidget(refresh_btn)
        toolbar_layout.addWidget(self.audit_btn)
        toolbar_layout.addStretch()
        
        self.selection_label = QLabel("")
        self.selection_label.setStyleSheet("color: #64748b; font-size: 13px; font-weight: 500;")
        toolbar_layout.addWidget(self.selection_label)
        
        self.container_layout.addWidget(toolbar_frame)
    
    def _create_action_button(self, text, color):
        btn = QPushButton(text)
        btn.setMinimumHeight(42)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:disabled {{
                background-color: #cbd5e1;
                color: #94a3b8;
            }}
        """)
        return btn
    
    def _create_enhanced_table(self):
        """Crée un tableau avec des boutons compacts (icônes uniquement)"""
        
        table_container = QFrame()
        table_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
            }
        """)
        
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # En-tête du tableau
        table_header = QFrame()
        table_header.setStyleSheet("background-color: transparent; border-bottom: 1px solid #e5e7eb;")
        header_layout = QHBoxLayout(table_header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        table_title = QLabel("📋 Liste des contacts")
        table_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #1e293b;")
        
        self.select_info_label = QLabel("💡 Sélection multiple: Ctrl+clic ou Shift+clic")
        self.select_info_label.setStyleSheet("font-size: 11px; color: #94a3b8;")
        
        header_layout.addWidget(table_title)
        header_layout.addStretch()
        header_layout.addWidget(self.select_info_label)
        
        table_layout.addWidget(table_header)
        
        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "NOM COMPLET", "TÉLÉPHONE", "EMAIL", "TYPE", "STATUT", "DATE", "ACTIONS"
        ])
        
        # Configuration
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Style du tableau
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                gridline-color: transparent;
                outline: none;
            }
            QTableWidget::item {
                padding: 14px 12px;
                border-bottom: 1px solid #f1f5f9;
                font-size: 13px;
            }
            QTableWidget::item:selected {
                background-color: #eff6ff;
                color: #1e293b;
            }
            QTableWidget::item:hover {
                background-color: #f8fafc;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 14px 12px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: 700;
                font-size: 12px;
                color: #475569;
                text-transform: uppercase;
                letter-spacing: 0.3px;
            }
        """)
        
        # Largeurs des colonnes
        self.table.setColumnWidth(0, 60)   # ID
        self.table.setColumnWidth(1, 220)  # Nom
        self.table.setColumnWidth(2, 150)  # Téléphone
        self.table.setColumnWidth(3, 260)  # Email
        self.table.setColumnWidth(4, 110)  # Type
        self.table.setColumnWidth(5, 100)  # Statut
        self.table.setColumnWidth(6, 110)  # Date
        self.table.setColumnWidth(7, 110)  # Actions (réduite pour icônes)
        
        # Connecter les signaux
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setMinimumHeight(450)
        
        table_layout.addWidget(self.table)
        
        # Pied du tableau
        table_footer = QFrame()
        table_footer.setStyleSheet("background-color: transparent; border-top: 1px solid #e5e7eb;")
        footer_layout = QHBoxLayout(table_footer)
        footer_layout.setContentsMargins(20, 10, 20, 10)
        
        self.total_rows_label = QLabel("Affichage de 0 contact")
        self.total_rows_label.setStyleSheet("color: #64748b; font-size: 12px;")
        
        footer_layout.addWidget(self.total_rows_label)
        footer_layout.addStretch()
        
        table_layout.addWidget(table_footer)
        
        self.container_layout.addWidget(table_container)
    
    def _create_compact_action_buttons(self, contact):
        """Crée des boutons d'action compacts (icônes uniquement)"""
        widget = QWidget()
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Bouton VOIR - icône uniquement
        view_btn = QPushButton("👁️")
        view_btn.setFixedSize(34, 34)
        view_btn.setCursor(Qt.PointingHandCursor)
        view_btn.setToolTip("Voir les détails (Ctrl+clic)")
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #475569;
                border-radius: 8px;
                font-size: 16px;
                font-weight: normal;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #8b5cf6;
                color: white;
            }
        """)
        view_btn.clicked.connect(lambda: self.view_contact(contact))
        
        # Bouton MODIFIER - icône uniquement
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(34, 34)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setToolTip("Modifier le contact (Ctrl+E)")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #475569;
                border-radius: 8px;
                font-size: 16px;
                font-weight: normal;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #3b82f6;
                color: white;
            }
        """)
        edit_btn.clicked.connect(lambda: self.edit_contact(contact))
        
        # Bouton SUPPRIMER - icône uniquement
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(34, 34)
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setToolTip("Supprimer le contact (Suppr)")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #475569;
                border-radius: 8px;
                font-size: 16px;
                font-weight: normal;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #ef4444;
                color: white;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_contact(contact))
        
        layout.addWidget(view_btn)
        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)

        layout.setAlignment(Qt.AlignCenter)

        # Appliquer le layout
        widget.setLayout(layout)
        
        return widget
    
    def _create_status_bar(self):
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(20, 12, 20, 12)
        
        self.status_label = QLabel("✅ Prêt")
        self.status_label.setStyleSheet("color: #10b981; font-size: 13px; font-weight: 500;")
        
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #64748b; font-size: 12px;")
        
        self.last_update_label = QLabel("")
        self.last_update_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.info_label)
        status_layout.addStretch()
        status_layout.addWidget(self.last_update_label)
        
        self.container_layout.addWidget(status_frame)
    
    def setup_shortcuts(self):
        new_shortcut = QAction(self)
        new_shortcut.setShortcut("Ctrl+N")
        new_shortcut.triggered.connect(self.on_add_contact)
        self.addAction(new_shortcut)
        
        edit_shortcut = QAction(self)
        edit_shortcut.setShortcut("Ctrl+E")
        edit_shortcut.triggered.connect(self.on_edit_contact)
        self.addAction(edit_shortcut)
        
        delete_shortcut = QAction(self)
        delete_shortcut.setShortcut("Delete")
        delete_shortcut.triggered.connect(self.on_delete_contact)
        self.addAction(delete_shortcut)
        
        refresh_shortcut = QAction(self)
        refresh_shortcut.setShortcut("Ctrl+R")
        refresh_shortcut.triggered.connect(self.load_contacts)
        self.addAction(refresh_shortcut)
        
        search_shortcut = QAction(self)
        search_shortcut.setShortcut("Ctrl+F")
        search_shortcut.triggered.connect(lambda: self.search_input.setFocus())
        self.addAction(search_shortcut)
    
    def load_contacts(self):
        try:
            self.set_status("Chargement des contacts...", "info")
            self.all_contacts = self.controller.contacts.get_all_contacts()
            self.filtered_contacts = self.all_contacts.copy()
            self.display_contacts()
            self.update_statistics()
            self.update_last_update_time()
            
            count = len(self.all_contacts)
            self.set_status(f"{count} contact(s) chargé(s) avec succès", "success")
            self.info_label.setText(f"Total: {count} contacts")
            logger.info(f"Contacts chargés: {count}")
            
        except Exception as e:
            self.set_status(f"Erreur: {str(e)}", "error")
            logger.error(f"Erreur chargement contacts: {e}")
    
    def display_contacts(self):
        """Affiche les contacts avec boutons compacts"""
        self.table.setRowCount(0)
        self.counter_label.setText(f"{len(self.filtered_contacts)} contact(s)")
        self.total_rows_label.setText(f"Affichage de {len(self.filtered_contacts)} contact(s)")
        
        for row, contact in enumerate(self.filtered_contacts):
            self.table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(contact.id))
            id_item.setTextAlignment(Qt.AlignCenter)
            id_item.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row, 0, id_item)
            
            # Nom complet
            name = f"{contact.nom or ''} {contact.prenom or ''}".strip()
            name_item = QTableWidgetItem(name or "—")
            name_item.setFont(QFont("Segoe UI", 11, QFont.Bold))
            name_item.setForeground(QBrush(QColor("#1e293b")))
            self.table.setItem(row, 1, name_item)
            
            # Téléphone
            phone_item = QTableWidgetItem(contact.telephone or "—")
            phone_item.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row, 2, phone_item)
            
            # Email
            email_item = QTableWidgetItem(contact.email or "—")
            email_item.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row, 3, email_item)
            
            # Type
            type_item = QTableWidgetItem(contact.type_client or "—")
            type_item.setForeground(self._get_type_color(contact.type_client))
            type_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            type_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, type_item)
            
            # Statut
            status = contact.vip_status or "Actif"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(self._get_status_color(status))
            status_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            status_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, status_item)
            
            # Date création
            date_str = contact.created_at.strftime("%d/%m/%Y") if contact.created_at else "—"
            date_item = QTableWidgetItem(date_str)
            date_item.setTextAlignment(Qt.AlignCenter)
            date_item.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row, 6, date_item)
            
            # Actions avec boutons compacts (icônes uniquement)
            actions_widget = self._create_compact_action_buttons(contact)
            self.table.setCellWidget(row, 7, actions_widget)
            
            # Hauteur de ligne réduite pour les icônes
            self.table.setRowHeight(row, 52)
    
    def on_search(self):
        self.apply_filters()
    
    def on_filter_changed(self):
        self.apply_filters()
    
    def apply_filters(self):
        search_text = self.search_input.text().strip().lower()
        type_filter = self.type_filter.currentText()
        status_filter = self.status_filter.currentText()
        date_filter = self.date_filter.currentText()
        
        filtered = self.all_contacts.copy()
        
        if search_text:
            filtered = [c for c in filtered if self._matches_search(c, search_text)]
        
        if type_filter != "Tous les types":
            filtered = [c for c in filtered if (c.type_client or "") == type_filter]
        
        if status_filter != "Tous les statuts":
            filtered = [c for c in filtered if (c.vip_status or "Actif") == status_filter]
        
        if date_filter != "Toutes les dates":
            filtered = self._apply_date_filter(filtered, date_filter)
        
        self.filtered_contacts = filtered
        self.display_contacts()
        self.update_statistics()
        self.set_status(f"{len(filtered)} contact(s) trouvé(s)", "info")
    
    def _matches_search(self, contact, search_text):
        return any([
            search_text in (contact.nom or "").lower(),
            search_text in (contact.prenom or "").lower(),
            search_text in (contact.telephone or "").lower(),
            search_text in (contact.email or "").lower(),
            search_text in (contact.type_client or "").lower()
        ])
    
    def _apply_date_filter(self, contacts, date_filter):
        from datetime import datetime, timedelta
        
        now = datetime.now()
        today = now.date()
        
        if date_filter == "Aujourd'hui":
            return [c for c in contacts if c.created_at and c.created_at.date() == today]
        elif date_filter == "Cette semaine":
            week_start = today - timedelta(days=today.weekday())
            return [c for c in contacts if c.created_at and c.created_at.date() >= week_start]
        elif date_filter == "Ce mois":
            return [c for c in contacts if c.created_at and c.created_at.month == now.month and c.created_at.year == now.year]
        elif date_filter == "Cette année":
            return [c for c in contacts if c.created_at and c.created_at.year == now.year]
        
        return contacts
    
    def reset_filters(self):
        self.search_input.clear()
        self.type_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self.date_filter.setCurrentIndex(0)
        self.filtered_contacts = self.all_contacts.copy()
        self.display_contacts()
        self.update_statistics()
        self.set_status("Filtres réinitialisés", "info")
    
    def update_statistics(self):
        total = len(self.filtered_contacts)
        assures = len([c for c in self.filtered_contacts if (c.type_client or "") == "Assuré"])
        prospects = len([c for c in self.filtered_contacts if (c.type_client or "") == "Prospect"])
        actifs = len([c for c in self.filtered_contacts if (c.vip_status or "Actif") == "Actif"])
        
        self._update_stat_card("total", str(total))
        self._update_stat_card("assures", str(assures))
        self._update_stat_card("prospects", str(prospects))
        self._update_stat_card("actifs", str(actifs))
    
    def _update_stat_card(self, key, value):
        card = self.stats_cards.get(key)
        if card:
            value_label = card.findChild(QLabel, f"stat_{key}")
            if value_label:
                value_label.setText(value)
    
    def on_selection_changed(self):
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        
        self.selected_contacts = []
        for row in selected_rows:
            if row < len(self.filtered_contacts):
                self.selected_contacts.append(self.filtered_contacts[row])
        
        count = len(self.selected_contacts)
        self.edit_btn.setEnabled(count == 1)
        self.delete_btn.setEnabled(count > 0)
        
        if count > 0:
            self.selection_label.setText(f"✓ {count} contact(s) sélectionné(s)")
        else:
            self.selection_label.setText("")
        
        if count == 1:
            self.contact_selected.emit(self.selected_contacts[0])
    
    def on_item_double_clicked(self, item):
        row = item.row()
        if row < len(self.filtered_contacts):
            self.view_contact(self.filtered_contacts[row])
    
    def on_add_contact(self):
        dialog = ContactForm(self)
        if dialog.exec_():
            data = dialog.get_data()
            result = self.controller.contacts.create_contact(data)
            if result:
                self.load_contacts()
                self.set_status("Contact ajouté avec succès", "success")
    
    def on_edit_contact(self):
        if len(self.selected_contacts) == 1:
            self.edit_contact(self.selected_contacts[0])
    
    def edit_contact(self, contact):
        fresh_contact = self.controller.contacts.get_contact_by_id(contact.id)
        if fresh_contact:
            dialog = ContactForm(self, fresh_contact)
            if dialog.exec_():
                self.load_contacts()
                self.contact_updated.emit()
                self.set_status("Contact modifié avec succès", "success")
    
    def view_contact(self, contact):
        from addons.Automobiles.views.contact_detail_view import ContactDetailView
        dialog = ContactDetailView(self.controller, contact, self)
        dialog.contact_updated.connect(self.load_contacts)
        dialog.exec_()
    
    def on_delete_contact(self):
        if not self.selected_contacts:
            return
        
        count = len(self.selected_contacts)
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Confirmation")
        
        if count == 1:
            contact = self.selected_contacts[0]
            name = f"{contact.nom} {contact.prenom or ''}".strip()
            msg.setText(f"Supprimer le contact '{name}' ?")
        else:
            msg.setText(f"Supprimer {count} contacts ?")
        
        msg.setInformativeText("Cette action est irréversible.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        
        if msg.exec() == QMessageBox.Yes:
            success_count = 0
            for contact in self.selected_contacts:
                if self.controller.contacts.delete_contact(contact.id):
                    success_count += 1
            
            self.load_contacts()
            self.set_status(f"{success_count} contact(s) supprimé(s)", "success")
    
    def delete_contact(self, contact):
        name = f"{contact.nom} {contact.prenom or ''}".strip()
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Confirmation")
        msg.setText(f"Supprimer le contact '{name}' ?")
        msg.setInformativeText("Cette action est irréversible.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        
        if msg.exec() == QMessageBox.Yes:
            if self.controller.contacts.delete_contact(contact.id):
                self.load_contacts()
                self.set_status("Contact supprimé avec succès", "success")
    
    def export_to_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter les contacts", 
            f"contacts_{datetime.now().strftime('%Y%m%d')}.csv", 
            "CSV Files (*.csv)"
        )
        
        if path:
            try:
                import csv
                with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Nom", "Prénom", "Téléphone", "Email", "Type", "Statut", "Date création"])
                    
                    for c in self.filtered_contacts:
                        writer.writerow([
                            c.id, c.nom or "", c.prenom or "", c.telephone or "",
                            c.email or "", c.type_client or "", c.vip_status or "Actif",
                            c.created_at.strftime("%d/%m/%Y") if c.created_at else ""
                        ])
                
                self.set_status(f"Export CSV réussi: {os.path.basename(path)}", "success")
                logger.info(f"Export CSV: {len(self.filtered_contacts)} contacts")
                
            except Exception as e:
                self.set_status(f"Erreur export CSV: {str(e)}", "error")
    
    def export_to_pdf(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter les contacts en PDF",
            f"contacts_{datetime.now().strftime('%Y%m%d')}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if path:
            try:
                contacts_data = []
                for c in self.filtered_contacts:
                    contacts_data.append({
                        'id': c.id, 'nom': c.nom, 'prenom': c.prenom,
                        'telephone': c.telephone, 'email': c.email,
                        'type': c.type_client, 'statut': c.vip_status,
                        'date_creation': c.created_at
                    })
                
                stats = {
                    'total': len(contacts_data),
                    'assures': len([c for c in contacts_data if c['type'] == "Assuré"]),
                    'prospects': len([c for c in contacts_data if c['type'] == "Prospect"]),
                    'actifs': len([c for c in contacts_data if c['statut'] == "Actif"])
                }
                
                generate_contact_pdf(path, contacts_data, stats)
                self.set_status(f"Export PDF réussi: {os.path.basename(path)}", "success")
                logger.info(f"Export PDF: {len(contacts_data)} contacts")
                
            except Exception as e:
                self.set_status(f"Erreur export PDF: {str(e)}", "error")
    
    def show_audit_logs(self):
        try:
            logs = self.controller.contacts.get_audit_logs()
            
            if not logs:
                QMessageBox.information(self, "Audit", "Aucun historique d'audit disponible")
                return
            
            dialog = QDialog(self)
            dialog.setWindowTitle("📜 Journal d'audit")
            dialog.resize(1100, 700)
            dialog.setStyleSheet("background-color: white;")
            
            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(25, 25, 25, 25)
            layout.setSpacing(20)
            
            title = QLabel("📜 Historique des actions")
            title.setStyleSheet("font-size: 20px; font-weight: 700; color: #1e293b;")
            layout.addWidget(title)
            
            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["Date", "Action", "Utilisateur", "Détails"])
            table.setAlternatingRowColors(True)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setShowGrid(False)
            table.verticalHeader().setVisible(False)
            
            table.setStyleSheet("""
                QTableWidget { border: 1px solid #e5e7eb; border-radius: 10px; }
                QHeaderView::section { background-color: #f9fafb; padding: 12px; font-weight: 600; }
                QTableWidget::item { padding: 12px; }
            """)
            
            table.setRowCount(len(logs))
            for i, log in enumerate(logs):
                date_str = log.created_at.strftime("%d/%m/%Y %H:%M:%S") if log.created_at else "—"
                table.setItem(i, 0, QTableWidgetItem(date_str))
                table.setItem(i, 1, QTableWidgetItem(log.action or "—"))
                table.setItem(i, 2, QTableWidgetItem(f"ID: {log.user_id or '?'}"))
                table.setItem(i, 3, QTableWidgetItem(log.details or "—"))
            
            table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
            table.setColumnWidth(0, 180)
            table.setColumnWidth(1, 140)
            table.setColumnWidth(2, 100)
            
            layout.addWidget(table)
            
            close_btn = QPushButton("Fermer")
            close_btn.setMinimumHeight(45)
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3b82f6;
                    color: white;
                    padding: 12px 25px;
                    font-weight: 600;
                    border-radius: 10px;
                }
                QPushButton:hover { background-color: #2563eb; }
            """)
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)
            
            dialog.exec_()
            
        except Exception as e:
            self.set_status(f"Erreur: {str(e)}", "error")
    
    def show_context_menu(self, position):
        menu = QMenu()
        
        item = self.table.itemAt(position)
        if not item:
            return
        
        view_action = QAction("👁️ Voir les détails", self)
        view_action.triggered.connect(lambda: self.on_item_double_clicked(item))
        
        edit_action = QAction("✏️ Modifier", self)
        edit_action.triggered.connect(self.on_edit_contact)
        
        delete_action = QAction("🗑️ Supprimer", self)
        delete_action.triggered.connect(self.on_delete_contact)
        
        menu.addAction(view_action)
        menu.addAction(edit_action)
        menu.addSeparator()
        menu.addAction(delete_action)
        
        menu.exec_(self.table.viewport().mapToGlobal(position))
    
    def _get_type_color(self, contact_type):
        colors = {
            "Assuré": QColor("#10b981"),
            "Prospect": QColor("#f59e0b"),
            "Partenaire": QColor("#8b5cf6"),
            "Fournisseur": QColor("#06b6d4")
        }
        return colors.get(contact_type, QColor("#64748b"))
    
    def _get_status_color(self, status):
        colors = {
            "Actif": QColor("#10b981"),
            "Inactif": QColor("#ef4444"),
            "En attente": QColor("#f59e0b")
        }
        return colors.get(status, QColor("#64748b"))
    
    def set_status(self, message, msg_type="info"):
        icons = {"success": "✅", "error": "❌", "info": "ℹ️", "warning": "⚠️"}
        colors = {"success": "#10b981", "error": "#ef4444", "info": "#3b82f6", "warning": "#f59e0b"}
        
        self.status_label.setText(f"{icons.get(msg_type, 'ℹ️')} {message}")
        self.status_label.setStyleSheet(f"color: {colors.get(msg_type, '#64748b')}; font-size: 13px; font-weight: 500;")
        
        if msg_type != "error":
            QTimer.singleShot(3000, lambda: self.status_label.setText("✅ Prêt"))
    
    def update_last_update_time(self):
        self.last_update_label.setText(f"Dernière mise à jour: {datetime.now().strftime('%H:%M:%S')}")
    
    def apply_security_policy(self):
        if hasattr(self.current_user, 'role'):
            role = self.current_user.role
            
            if not SecurityManager.has_permission(role, Permissions.CONTACT_ADD):
                self.add_btn.setVisible(False)
            if not SecurityManager.has_permission(role, Permissions.CONTACT_EDIT):
                self.edit_btn.setVisible(False)
            if not SecurityManager.has_permission(role, Permissions.CONTACT_DELETE):
                self.delete_btn.setVisible(False)
            if not SecurityManager.has_permission(role, Permissions.AUDIT_VIEW):
                self.audit_btn.setVisible(False)
            if not SecurityManager.has_permission(role, Permissions.EXPORT_PDF):
                self.export_pdf_btn.setVisible(False)
    
    def refresh(self):
        self.load_contacts()