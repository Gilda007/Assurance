
# contacts_view.py - Version redesign complet avec UI moderne
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QLineEdit, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QFileDialog, QScrollArea,
    QSizePolicy, QDialog, QComboBox, QMenu, QTextEdit,
    QStackedWidget, QSplitter, QToolBar
)
from PySide6.QtCore import Qt, QTimer, Signal, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor, QAction, QBrush, QPalette, QIcon

from addons.Automobiles.security.access_control import Permissions, SecurityManager
from addons.Automobiles.views.contact_form_view import ContactForm
from addons.Automobiles.reports.pdf_generator import generate_contact_pdf
from core.logger import logger
from core.workers.database_worker import async_query


class ContactListView(QWidget):
    """Interface professionnelle redesign pour la gestion des contacts"""
    
    contact_selected = Signal(object)
    contact_updated = Signal()
    
    def __init__(self, controller, current_user):
        super().__init__()
        self.controller = controller
        self.current_user = current_user
        self._data_loaded = False
        self.all_contacts = []
        self.filtered_contacts = []
        self.selected_contacts = []
        self.is_dark_mode = False
        
        self.setup_ui()
        self.apply_security_policy()
        self.load_contacts()
        self.setup_shortcuts()
    
    def setup_ui(self):
        """Configuration de l'interface redesign"""
        # Widget principal avec fond gradient
        main_widget = QWidget()
        main_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8fafc, stop:1 #e2e8f0);
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
        """)
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Scroll principal
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
        """)
        
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        self.container_layout = QVBoxLayout(container)
        self.container_layout.setContentsMargins(32, 24, 32, 24)
        self.container_layout.setSpacing(20)
        
        # Sections redesign
        self._create_modern_header()
        self._create_quick_actions()
        self._create_modern_search()
        self._create_modern_stats()
        self._create_modern_table()
        self._create_status_bar()
        
        self.scroll_area.setWidget(container)
        main_layout.addWidget(self.scroll_area)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(main_widget)
    
    def _create_modern_header(self):
        """En-tête moderne avec illustration"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0f172a, stop:0.5 #1e293b, stop:1 #0f172a);
                border-radius: 20px;
                padding: 0px;
            }
        """)
        header.setFixedHeight(140)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(36, 20, 36, 20)
        
        # Section gauche - Titre
        left_section = QVBoxLayout()
        left_section.setSpacing(6)
        
        title = QLabel("👥 Contacts")
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: 700;
            color: white;
            letter-spacing: -0.5px;
        """)
        
        subtitle = QLabel("Gérez votre réseau professionnel en toute simplicité")
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #94a3b8;
            font-weight: 400;
        """)
        
        left_section.addWidget(title)
        left_section.addWidget(subtitle)
        
        # Section droite - Compteurs
        right_section = QHBoxLayout()
        right_section.setSpacing(16)
        
        # Compteur total
        self.total_badge = self._create_badge("📊", "0", "Total")
        
        # Compteur actifs
        self.active_badge = self._create_badge("🟢", "0", "Actifs")
        
        right_section.addWidget(self.total_badge)
        right_section.addWidget(self.active_badge)
        
        layout.addLayout(left_section)
        layout.addStretch()
        layout.addLayout(right_section)
        
        self.container_layout.addWidget(header)
    
    def _create_badge(self, icon, count, label):
        """Crée un badge de compteur"""
        badge = QFrame()
        badge.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.08);
                border-radius: 16px;
                padding: 8px 16px;
                border: 1px solid rgba(255,255,255,0.05);
            }
        """)
        
        layout = QHBoxLayout(badge)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(10)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 18px;")
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
        
        count_label = QLabel(count)
        count_label.setStyleSheet("""
            font-size: 20px;
            font-weight: 700;
            color: white;
        """)
        count_label.setObjectName(f"badge_{label.lower()}")
        
        name_label = QLabel(label)
        name_label.setStyleSheet("""
            font-size: 11px;
            color: #94a3b8;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        
        text_layout.addWidget(count_label)
        text_layout.addWidget(name_label)
        
        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        
        return badge
    
    def _create_quick_actions(self):
        """Barre d'actions rapides"""
        actions_frame = QFrame()
        actions_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        actions_frame.setFixedHeight(72)
        
        layout = QHBoxLayout(actions_frame)
        layout.setContentsMargins(24, 12, 24, 12)
        layout.setSpacing(8)
        
        # Boutons d'action principaux
        self.add_btn = self._create_icon_button("➕", "Nouveau", "#3b82f6")
        self.add_btn.clicked.connect(self.on_add_contact)
        
        self.edit_btn = self._create_icon_button("✏️", "Modifier", "#8b5cf6")
        self.edit_btn.clicked.connect(self.on_edit_contact)
        self.edit_btn.setEnabled(False)
        
        self.delete_btn = self._create_icon_button("🗑️", "Supprimer", "#ef4444")
        self.delete_btn.clicked.connect(self.on_delete_contact)
        self.delete_btn.setEnabled(False)
        
        self.duplicate_btn = self._create_icon_button("📋", "Dupliquer", "#6b7280")
        self.duplicate_btn.clicked.connect(self.duplicate_contact)
        self.duplicate_btn.setEnabled(False)
        
        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("background: #e2e8f0; max-width: 1px;")
        sep.setFixedWidth(1)
        
        # Boutons d'export
        self.export_csv_btn = self._create_icon_button("📄", "CSV", "#059669")
        self.export_csv_btn.clicked.connect(self.export_to_csv)
        
        self.export_pdf_btn = self._create_icon_button("📑", "PDF", "#dc2626")
        self.export_pdf_btn.clicked.connect(self.export_to_pdf)
        
        self.import_btn = self._create_icon_button("📥", "Importer", "#f59e0b")
        self.import_btn.clicked.connect(self.import_contacts)
        
        # Séparateur
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.VLine)
        sep2.setStyleSheet("background: #e2e8f0; max-width: 1px;")
        sep2.setFixedWidth(1)
        
        # Actions supplémentaires
        self.audit_btn = self._create_icon_button("📜", "Audit", "#6b7280")
        self.audit_btn.clicked.connect(self.show_audit_logs)
        
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setFixedSize(44, 44)
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.setToolTip("Basculer le thème")
        self.theme_btn.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                border-radius: 12px;
                font-size: 18px;
                border: 1px solid #e2e8f0;
            }
            QPushButton:hover {
                background: #e2e8f0;
            }
        """)
        self.theme_btn.clicked.connect(self.toggle_theme)
        
        self.refresh_btn = self._create_icon_button("🔄", "Actualiser", "#6b7280")
        self.refresh_btn.clicked.connect(self.load_contacts)
        
        layout.addWidget(self.add_btn)
        layout.addWidget(self.edit_btn)
        layout.addWidget(self.delete_btn)
        layout.addWidget(self.duplicate_btn)
        layout.addWidget(sep)
        layout.addWidget(self.export_csv_btn)
        layout.addWidget(self.export_pdf_btn)
        layout.addWidget(self.import_btn)
        layout.addWidget(sep2)
        layout.addWidget(self.audit_btn)
        layout.addWidget(self.theme_btn)
        layout.addWidget(self.refresh_btn)
        layout.addStretch()
        
        # Sélection info
        self.selection_label = QLabel("")
        self.selection_label.setStyleSheet("""
            color: #64748b;
            font-size: 13px;
            font-weight: 500;
        """)
        layout.addWidget(self.selection_label)
        
        self.container_layout.addWidget(actions_frame)
    
    def _create_icon_button(self, icon, text, color):
        """Crée un bouton avec icône et texte"""
        btn = QPushButton()
        btn.setFixedHeight(48)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border-radius: 12px;
                padding: 0px 16px;
                font-weight: 500;
                font-size: 13px;
                color: #334155;
            }}
            QPushButton:hover {{
                background: {color}15;
                color: {color};
            }}
            QPushButton:disabled {{
                color: #cbd5e1;
            }}
        """)
        
        layout = QHBoxLayout(btn)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(8)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 16px;")
        
        text_label = QLabel(text)
        text_label.setStyleSheet("font-size: 13px;")
        
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        
        return btn
    
    def _create_modern_search(self):
        """Barre de recherche moderne"""
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        layout = QVBoxLayout(search_frame)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        # Ligne de recherche
        search_row = QHBoxLayout()
        search_row.setSpacing(12)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher un contact...")
        self.search_input.setMinimumHeight(48)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 0px 16px;
                font-size: 14px;
                background: #f8fafc;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                background: white;
            }
        """)
        self.search_input.textChanged.connect(self.on_search)
        search_row.addWidget(self.search_input)
        
        # Filtres rapides
        filters_row = QHBoxLayout()
        filters_row.setSpacing(12)
        
        # Filtre type
        type_layout = QVBoxLayout()
        type_layout.setSpacing(4)
        type_label = QLabel("Type")
        type_label.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600;")
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Tous", "Assuré", "Prospect", "Partenaire", "Fournisseur"])
        self.type_filter.setMinimumHeight(40)
        self.type_filter.setStyleSheet("""
            QComboBox {
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 0px 12px;
                background: #f8fafc;
                min-width: 120px;
            }
            QComboBox:hover {
                border-color: #94a3b8;
            }
            QComboBox:focus {
                border-color: #3b82f6;
            }
        """)
        self.type_filter.currentTextChanged.connect(self.on_filter_changed)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_filter)
        
        # Filtre statut
        status_layout = QVBoxLayout()
        status_layout.setSpacing(4)
        status_label = QLabel("Statut")
        status_label.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600;")
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Tous", "Actif", "Inactif", "En attente"])
        self.status_filter.setMinimumHeight(40)
        self.status_filter.setStyleSheet("""
            QComboBox {
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 0px 12px;
                background: #f8fafc;
                min-width: 120px;
            }
            QComboBox:hover {
                border-color: #94a3b8;
            }
            QComboBox:focus {
                border-color: #3b82f6;
            }
        """)
        self.status_filter.currentTextChanged.connect(self.on_filter_changed)
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_filter)
        
        # Filtre date
        date_layout = QVBoxLayout()
        date_layout.setSpacing(4)
        date_label = QLabel("Période")
        date_label.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600;")
        self.date_filter = QComboBox()
        self.date_filter.addItems(["Toutes", "Aujourd'hui", "Cette semaine", "Ce mois"])
        self.date_filter.setMinimumHeight(40)
        self.date_filter.setStyleSheet("""
            QComboBox {
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 0px 12px;
                background: #f8fafc;
                min-width: 140px;
            }
            QComboBox:hover {
                border-color: #94a3b8;
            }
            QComboBox:focus {
                border-color: #3b82f6;
            }
        """)
        self.date_filter.currentTextChanged.connect(self.on_filter_changed)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_filter)
        
        # Bouton reset
        reset_btn = QPushButton("🔄 Réinitialiser")
        reset_btn.setMinimumHeight(40)
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 0px 20px;
                font-weight: 600;
                color: #475569;
            }
            QPushButton:hover {
                background: #e2e8f0;
            }
        """)
        reset_btn.clicked.connect(self.reset_filters)
        
        filters_row.addLayout(type_layout)
        filters_row.addLayout(status_layout)
        filters_row.addLayout(date_layout)
        filters_row.addStretch()
        filters_row.addWidget(reset_btn)
        
        layout.addLayout(search_row)
        layout.addLayout(filters_row)
        
        self.container_layout.addWidget(search_frame)
    
    def _create_modern_stats(self):
        """Tableau de bord statistiques moderne"""
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        layout = QVBoxLayout(stats_frame)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        # En-tête
        header_layout = QHBoxLayout()
        title = QLabel("📊 Statistiques")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #0f172a;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Cartes
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)
        
        stats_data = [
            ("total", "Total contacts", "👥", "#3b82f6"),
            ("assures", "Assurés", "✅", "#10b981"),
            ("prospects", "Prospects", "🎯", "#f59e0b"),
            ("actifs", "Actifs", "⭐", "#8b5cf6")
        ]
        
        self.stats_cards = {}
        for key, label, icon, color in stats_data:
            card = self._create_modern_stat_card(icon, label, "0", color)
            cards_layout.addWidget(card)
            self.stats_cards[key] = card
        
        layout.addLayout(cards_layout)
        self.container_layout.addWidget(stats_frame)
    
    def _create_modern_stat_card(self, icon, label, value, color):
        """Crée une carte statistique moderne"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {color}08;
                border: 1px solid {color}20;
                border-radius: 12px;
            }}
        """)
        card.setMinimumHeight(80)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)
        
        # Icône
        icon_container = QFrame()
        icon_container.setStyleSheet(f"""
            QFrame {{
                background: {color}15;
                border-radius: 12px;
                padding: 8px;
            }}
        """)
        icon_container.setFixedSize(48, 48)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        icon_layout.addWidget(icon_label)
        
        # Texte
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 800;
            color: {color};
        """)
        # Correction : utiliser label comme nom d'objet, pas key
        value_label.setObjectName(f"stat_{label.lower().replace(' ', '_')}")
        
        name_label = QLabel(label)
        name_label.setStyleSheet("""
            font-size: 12px;
            color: #64748b;
            font-weight: 500;
        """)
        
        text_layout.addWidget(value_label)
        text_layout.addWidget(name_label)
        
        layout.addWidget(icon_container)
        layout.addLayout(text_layout)
        layout.addStretch()
        
        return card

    def _create_modern_table(self):
        """Tableau moderne avec design épuré"""
        table_container = QFrame()
        table_container.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        layout = QVBoxLayout(table_container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # En-tête du tableau
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: transparent;
                border-bottom: 1px solid #e2e8f0;
                padding: 16px 24px;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 16, 24, 16)
        
        title = QLabel("📋 Liste des contacts")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #0f172a;
        """)
        
        info = QLabel("💡 Cliquez sur un contact pour voir les détails")
        info.setStyleSheet("""
            font-size: 12px;
            color: #94a3b8;
        """)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(info)
        
        layout.addWidget(header)
        
        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "CONTACT", "TÉLÉPHONE", "EMAIL", "TYPE", "STATUT", "ACTIONS"
        ])
        
        # Configuration
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setAlternatingRowColors(False)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Style moderne
        self.table.setStyleSheet("""
            QTableWidget {
                background: transparent;
                border: none;
                outline: none;
                gridline-color: transparent;
            }
            QTableWidget::item {
                padding: 12px 16px;
                border-bottom: 1px solid #f1f5f9;
                font-size: 13px;
                color: #1e293b;
            }
            QTableWidget::item:selected {
                background: #eff6ff;
                color: #1e293b;
            }
            QTableWidget::item:hover:!selected {
                background: #f8fafc;
            }
            QHeaderView::section {
                background: #f8fafc;
                padding: 12px 16px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: 700;
                font-size: 11px;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
        """)
        
        # Largeurs
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(1, 240)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 260)
        self.table.setColumnWidth(4, 110)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 130)
        
        # Signaux
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        self.table.setMinimumHeight(400)
        layout.addWidget(self.table)
        
        # Pied
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background: transparent;
                border-top: 1px solid #e2e8f0;
                padding: 12px 24px;
            }
        """)
        
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(24, 12, 24, 12)
        
        self.total_rows_label = QLabel("0 contact(s) affiché(s)")
        self.total_rows_label.setStyleSheet("color: #64748b; font-size: 13px;")
        
        footer_layout.addWidget(self.total_rows_label)
        footer_layout.addStretch()
        
        layout.addWidget(footer)
        self.container_layout.addWidget(table_container)

    def on_item_double_clicked(self, item):
        row = item.row()
        if row < len(self.filtered_contacts):
            self.view_contact(self.filtered_contacts[row])
    
    # ==================== CRUD ====================
    
    def _create_contact_card(self, contact):
        """Crée une carte de contact avec avatar"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Avatar avec initiales
        initials = ""
        if contact.prenom:
            initials += contact.prenom[0].upper()
        if contact.nom:
            initials += contact.nom[0].upper()
        initials = initials or "?"
        
        colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"]
        color = colors[contact.id % len(colors)] if contact.id else colors[0]
        
        avatar = QLabel(initials)
        avatar.setFixedSize(40, 40)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(f"""
            background: {color};
            color: white;
            border-radius: 20px;
            font-weight: 700;
            font-size: 14px;
        """)
        
        # Nom
        name = f"{contact.nom or ''} {contact.prenom or ''}".strip()
        name_label = QLabel(name or "—")
        name_label.setStyleSheet("""
            font-weight: 600;
            font-size: 14px;
            color: #0f172a;
        """)
        
        layout.addWidget(avatar)
        layout.addWidget(name_label)
        layout.addStretch()
        
        return widget
    
    def _create_modern_action_buttons(self, contact):
        """Boutons d'action modernes"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Style commun des boutons
        btn_style = """
            QPushButton {
                background: transparent;
                border-radius: 8px;
                font-size: 14px;
                padding: 4px;
                min-width: 30px;
                min-height: 30px;
            }
            QPushButton:hover {
                background: %s;
            }
        """
        
        # Voir
        view_btn = QPushButton("👁")
        view_btn.setToolTip("Voir les détails")
        view_btn.setStyleSheet(btn_style % "#f1f5f9")
        view_btn.clicked.connect(lambda: self.view_contact(contact))
        
        # Modifier
        edit_btn = QPushButton("✏️")
        edit_btn.setToolTip("Modifier")
        edit_btn.setStyleSheet(btn_style % "#eff6ff")
        edit_btn.clicked.connect(lambda: self.edit_contact(contact))
        
        # Note
        note_btn = QPushButton("📝")
        note_btn.setToolTip("Ajouter une note")
        note_btn.setStyleSheet(btn_style % "#fffbeb")
        note_btn.clicked.connect(lambda: self.add_quick_note(contact))
        
        # Supprimer
        delete_btn = QPushButton("🗑")
        delete_btn.setToolTip("Supprimer")
        delete_btn.setStyleSheet(btn_style % "#fef2f2")
        delete_btn.clicked.connect(lambda: self.delete_contact(contact))
        
        layout.addWidget(view_btn)
        layout.addWidget(edit_btn)
        layout.addWidget(note_btn)
        layout.addWidget(delete_btn)
        layout.setAlignment(Qt.AlignCenter)
        
        return widget
    
    def _create_status_bar(self):
        """Barre de statut moderne"""
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        status_frame.setFixedHeight(56)
        
        layout = QHBoxLayout(status_frame)
        layout.setContentsMargins(24, 8, 24, 8)
        layout.setSpacing(20)
        
        # Statut
        self.status_label = QLabel("✅ Prêt")
        self.status_label.setStyleSheet("""
            color: #10b981;
            font-size: 13px;
            font-weight: 500;
        """)
        
        # Info
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #64748b; font-size: 13px;")
        
        # Dernière mise à jour
        self.last_update_label = QLabel("")
        self.last_update_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.info_label)
        layout.addStretch()
        layout.addWidget(self.last_update_label)
        
        self.container_layout.addWidget(status_frame)
    
    # ==================== FONCTIONS MÉTIER ====================
    
    def load_contacts(self):
        """Charge les contacts"""
        try:
            self.set_status("Chargement des contacts...", "info")
            self.all_contacts = self.controller.contacts.get_all_contacts()
            self.filtered_contacts = self.all_contacts.copy()
            self.display_contacts()
            self.update_statistics()
            self.update_last_update_time()
            
            count = len(self.all_contacts)
            self.set_status(f"{count} contact(s) chargé(s)", "success")
            self.info_label.setText(f"Total: {count} contacts")
            logger.info(f"Contacts chargés: {count}")
            
        except Exception as e:
            self.set_status(f"Erreur: {str(e)}", "error")
            logger.error(f"Erreur chargement contacts: {e}")
    
    def display_contacts(self):
        """Affiche les contacts"""
        self.table.setRowCount(0)
        count = len(self.filtered_contacts)
        self.total_rows_label.setText(f"{count} contact(s) affiché(s)")
        
        for row, contact in enumerate(self.filtered_contacts):
            self.table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(contact.id))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, id_item)
            
            # Contact avec avatar
            contact_widget = self._create_contact_card(contact)
            self.table.setCellWidget(row, 1, contact_widget)
            
            # Téléphone
            phone_item = QTableWidgetItem(contact.telephone or "—")
            self.table.setItem(row, 2, phone_item)
            
            # Email
            email_item = QTableWidgetItem(contact.email or "—")
            self.table.setItem(row, 3, email_item)
            
            # Type
            type_item = QTableWidgetItem(contact.type_client or "—")
            type_item.setForeground(self._get_type_color(contact.type_client))
            type_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, type_item)
            
            # Statut
            status = contact.vip_status or "Actif"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(self._get_status_color(status))
            status_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, status_item)
            
            # Actions
            actions_widget = self._create_modern_action_buttons(contact)
            self.table.setCellWidget(row, 6, actions_widget)
            
            self.table.setRowHeight(row, 64)
    
    def update_statistics(self):
        """Met à jour les statistiques"""
        total = len(self.filtered_contacts)
        assures = len([c for c in self.filtered_contacts if (c.type_client or "") == "Assuré"])
        prospects = len([c for c in self.filtered_contacts if (c.type_client or "") == "Prospect"])
        actifs = len([c for c in self.filtered_contacts if (c.vip_status or "Actif") == "Actif"])
        
        # Mettre à jour les badges
        self._update_stat_card("total", str(total))
        self._update_stat_card("assures", str(assures))
        self._update_stat_card("prospects", str(prospects))
        self._update_stat_card("actifs", str(actifs))
        
        # Mettre à jour les badges d'en-tête
        total_badge = self.findChild(QFrame, "total_badge")
        if total_badge:
            count_label = total_badge.findChild(QLabel, "badge_total")
            if count_label:
                count_label.setText(str(total))
        
        active_badge = self.findChild(QFrame, "active_badge")
        if active_badge:
            count_label = active_badge.findChild(QLabel, "badge_actifs")
            if count_label:
                count_label.setText(str(actifs))
    
    def _update_stat_card(self, key, value):
        """Met à jour une carte statistique"""
        card = self.stats_cards.get(key)
        if card:
            value_label = card.findChild(QLabel, f"stat_{key}")
            if value_label:
                value_label.setText(value)
    
    def on_selection_changed(self):
        """Gère la sélection"""
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
        self.duplicate_btn.setEnabled(count == 1)
        
        if count > 0:
            self.selection_label.setText(f"✓ {count} sélectionné(s)")
        else:
            self.selection_label.setText("")
        
        if count == 1:
            self.contact_selected.emit(self.selected_contacts[0])
    
    # ==================== ACTIONS ====================
    
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
    
    def duplicate_contact(self):
        if len(self.selected_contacts) == 1:
            contact = self.selected_contacts[0]
            new_data = {
                'nom': contact.nom + " (Copie)" if contact.nom else "Copie",
                'prenom': contact.prenom,
                'telephone': contact.telephone,
                'email': contact.email,
                'type_client': contact.type_client,
                'vip_status': contact.vip_status
            }
            result = self.controller.contacts.create_contact(new_data)
            if result:
                self.load_contacts()
                self.set_status("Contact dupliqué avec succès", "success")
    
    def import_contacts(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Importer des contacts",
            "", "CSV Files (*.csv);;Excel Files (*.xlsx *.xls)"
        )
        if path:
            try:
                count = self.controller.contacts.import_from_file(path)
                self.load_contacts()
                self.set_status(f"{count} contact(s) importé(s)", "success")
            except Exception as e:
                self.set_status(f"Erreur d'import: {str(e)}", "error")
    
    def add_quick_note(self, contact):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"📝 Note - {contact.nom}")
        dialog.resize(500, 300)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        info = QLabel(f"Contact: {contact.nom} {contact.prenom or ''}")
        info.setStyleSheet("font-weight: 600; color: #0f172a;")
        layout.addWidget(info)
        
        note_input = QTextEdit()
        note_input.setPlaceholderText("Écrivez votre note ici...")
        note_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 12px;
                font-size: 13px;
            }
            QTextEdit:focus {
                border-color: #3b82f6;
            }
        """)
        layout.addWidget(note_input)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                border: none;
                border-radius: 10px;
                padding: 10px 24px;
                font-weight: 500;
                color: #475569;
            }
            QPushButton:hover {
                background: #e2e8f0;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                border: none;
                border-radius: 10px;
                padding: 10px 24px;
                font-weight: 600;
                color: white;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        
        def on_save():
            note = note_input.toPlainText().strip()
            if note:
                self.controller.contacts.add_note(contact.id, note)
                self.set_status("Note ajoutée", "success")
                dialog.accept()
            else:
                QMessageBox.warning(dialog, "Attention", "Veuillez écrire une note.")
        
        save_btn.clicked.connect(on_save)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec_()
    
    # ==================== EXPORTS ====================
    
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
                    writer.writerow(["ID", "Nom", "Prénom", "Téléphone", "Email", "Type", "Statut"])
                    for c in self.filtered_contacts:
                        writer.writerow([
                            c.id, c.nom or "", c.prenom or "", c.telephone or "",
                            c.email or "", c.type_client or "", c.vip_status or "Actif"
                        ])
                self.set_status(f"Export CSV réussi", "success")
            except Exception as e:
                self.set_status(f"Erreur export: {str(e)}", "error")
    
    def export_to_pdf(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter en PDF",
            f"contacts_{datetime.now().strftime('%Y%m%d')}.pdf",
            "PDF Files (*.pdf)"
        )
        if path:
            try:
                contacts_data = [{
                    'id': c.id, 'nom': c.nom, 'prenom': c.prenom,
                    'telephone': c.telephone, 'email': c.email,
                    'type': c.type_client, 'statut': c.vip_status
                } for c in self.filtered_contacts]
                
                stats = {
                    'total': len(contacts_data),
                    'assures': len([c for c in contacts_data if c['type'] == "Assuré"]),
                    'prospects': len([c for c in contacts_data if c['type'] == "Prospect"]),
                    'actifs': len([c for c in contacts_data if c['statut'] == "Actif"])
                }
                
                generate_contact_pdf(path, contacts_data, stats)
                self.set_status(f"Export PDF réussi", "success")
            except Exception as e:
                self.set_status(f"Erreur export: {str(e)}", "error")
    
    def show_audit_logs(self):
        try:
            logs = self.controller.contacts.get_audit_logs()
            if not logs:
                QMessageBox.information(self, "Audit", "Aucun historique disponible")
                return
            
            dialog = QDialog(self)
            dialog.setWindowTitle("📜 Journal d'audit")
            dialog.resize(1100, 700)
            
            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(24, 24, 24, 24)
            layout.setSpacing(16)
            
            title = QLabel("📜 Historique des actions")
            title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0f172a;")
            layout.addWidget(title)
            
            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["Date", "Action", "Utilisateur", "Détails"])
            table.setAlternatingRowColors(True)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setShowGrid(False)
            table.verticalHeader().setVisible(False)
            table.setStyleSheet("""
                QTableWidget {
                    border: 1px solid #e2e8f0;
                    border-radius: 12px;
                }
                QHeaderView::section {
                    background: #f8fafc;
                    padding: 12px;
                    font-weight: 600;
                }
                QTableWidget::item {
                    padding: 12px;
                }
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
            close_btn.setStyleSheet("""
                QPushButton {
                    background: #3b82f6;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 12px;
                    font-weight: 600;
                    min-height: 48px;
                }
                QPushButton:hover {
                    background: #2563eb;
                }
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
        
        row = item.row()
        if row >= len(self.filtered_contacts):
            return
        
        contact = self.filtered_contacts[row]
        
        view_action = QAction("👁️ Voir les détails", self)
        view_action.triggered.connect(lambda: self.view_contact(contact))
        
        edit_action = QAction("✏️ Modifier", self)
        edit_action.triggered.connect(lambda: self.edit_contact(contact))
        
        note_action = QAction("📝 Ajouter une note", self)
        note_action.triggered.connect(lambda: self.add_quick_note(contact))
        
        duplicate_action = QAction("📋 Dupliquer", self)
        duplicate_action.triggered.connect(lambda: self.duplicate_single_contact(contact))
        
        delete_action = QAction("🗑️ Supprimer", self)
        delete_action.triggered.connect(lambda: self.delete_contact(contact))
        
        menu.addAction(view_action)
        menu.addAction(edit_action)
        menu.addSeparator()
        menu.addAction(note_action)
        menu.addAction(duplicate_action)
        menu.addSeparator()
        menu.addAction(delete_action)
        
        menu.exec_(self.table.viewport().mapToGlobal(position))
    
    def duplicate_single_contact(self, contact):
        new_data = {
            'nom': contact.nom + " (Copie)" if contact.nom else "Copie",
            'prenom': contact.prenom,
            'telephone': contact.telephone,
            'email': contact.email,
            'type_client': contact.type_client,
            'vip_status': contact.vip_status
        }
        result = self.controller.contacts.create_contact(new_data)
        if result:
            self.load_contacts()
            self.set_status("Contact dupliqué", "success")
    
    # ==================== FILTRES ====================
    
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
        
        if type_filter != "Tous":
            filtered = [c for c in filtered if (c.type_client or "") == type_filter]
        
        if status_filter != "Tous":
            filtered = [c for c in filtered if (c.vip_status or "Actif") == status_filter]
        
        if date_filter != "Toutes":
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
            search_text in (contact.email or "").lower()
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
    
    # ==================== THÈME ====================
    
    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            self._apply_dark_theme()
            self.theme_btn.setText("☀️")
        else:
            self._apply_light_theme()
            self.theme_btn.setText("🌙")
    
    def _apply_dark_theme(self):
        self.setStyleSheet("""
            QWidget {
                background: #0f172a;
                color: #e2e8f0;
            }
            QFrame {
                background: #1e293b;
                border-color: #334155;
            }
            QLineEdit, QComboBox {
                background: #1e293b;
                border-color: #334155;
                color: #e2e8f0;
            }
            QTableWidget {
                background: #1e293b;
                color: #e2e8f0;
            }
            QTableWidget::item {
                border-bottom: 1px solid #334155;
                color: #e2e8f0;
            }
            QHeaderView::section {
                background: #0f172a;
                color: #94a3b8;
            }
            QPushButton {
                color: #e2e8f0;
            }
            QLabel {
                color: #e2e8f0;
            }
        """)
    
    def _apply_light_theme(self):
        self.setup_ui()
    
    # ==================== UTILITAIRES ====================
    
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
        
        duplicate_shortcut = QAction(self)
        duplicate_shortcut.setShortcut("Ctrl+D")
        duplicate_shortcut.triggered.connect(self.duplicate_contact)
        self.addAction(duplicate_shortcut)