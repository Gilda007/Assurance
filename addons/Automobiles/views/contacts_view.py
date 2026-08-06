
"""
Gestion des Contacts - Interface moderne et professionnelle
"""

import os
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QLineEdit, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QFileDialog, QScrollArea,
    QSizePolicy, QDialog, QComboBox, QMenu, QTextEdit,
    QGridLayout, QSplitter, QToolButton, QProgressBar
)
from PySide6.QtCore import Qt, QTimer, Signal, QSize, QMargins
from PySide6.QtGui import QFont, QColor, QAction, QBrush, QPainter
from PySide6.QtCharts import (
    QChart, QChartView, QPieSeries, QBarSeries, QBarSet,
    QBarCategoryAxis, QValueAxis
)

from addons.Automobiles.security.access_control import Permissions, SecurityManager
from addons.Automobiles.views.contact_form_view import ContactForm
from addons.Automobiles.reports.pdf_generator import generate_contact_pdf
from core.logger import logger
from core.workers.database_worker import async_query


class ContactListView(QWidget):
    """Interface moderne de gestion des contacts"""
    
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
        
        self.setup_ui()
        self.apply_security_policy()
        self.load_contacts()
        self.setup_shortcuts()
    
    def setup_ui(self):
        """Configure l'interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setStyleSheet("background: #f5f7fa;")
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(24, 20, 24, 20)
        container_layout.setSpacing(16)
        
        # En-tête
        self._create_header(container_layout)
        
        # Barre d'outils
        self._create_toolbar(container_layout)
        
        # Statistiques
        self._create_stats(container_layout)
        
        # Tableau
        self._create_table(container_layout)
        
        # Barre de statut
        self._create_status_bar(container_layout)
        
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
    
    def _create_header(self, parent_layout):
        """Crée l'en-tête"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border-radius: 12px;
                border: 1px solid #e8edf2;
                padding: 16px 24px;
            }
        """)
        
        layout = QHBoxLayout(header)
        
        # Titre
        title_layout = QVBoxLayout()
        title = QLabel("👥 Contacts")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #1a202c; background: transparent; border: none;")
        
        subtitle = QLabel("Gérez vos contacts, clients et prospects")
        subtitle.setStyleSheet("font-size: 13px; color: #718096; background: transparent; border: none;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        # Compteurs
        counter_layout = QHBoxLayout()
        counter_layout.setSpacing(20)
        
        self.total_label = self._create_counter("📊", "0", "Total")
        self.active_label = self._create_counter("🟢", "0", "Actifs")
        
        counter_layout.addWidget(self.total_label)
        counter_layout.addWidget(self.active_label)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        layout.addLayout(counter_layout)
        
        parent_layout.addWidget(header)
    
    def _create_counter(self, icon, count, label):
        """Crée un compteur"""
        container = QFrame()
        container.setStyleSheet("background: transparent; border: none;")
        
        layout = QHBoxLayout(container)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 16px; background: transparent; border: none;")
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
        
        count_label = QLabel(count)
        count_label.setStyleSheet("font-size: 16px; font-weight: 700; color: #1a202c; background: transparent; border: none;")
        count_label.setObjectName(f"counter_{label.lower()}")
        
        name_label = QLabel(label)
        name_label.setStyleSheet("font-size: 10px; color: #718096; text-transform: uppercase; letter-spacing: 0.5px; background: transparent; border: none;")
        
        text_layout.addWidget(count_label)
        text_layout.addWidget(name_label)
        
        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        
        return container
    
    def _create_toolbar(self, parent_layout):
        """Crée la barre d'outils"""
        toolbar = QFrame()
        toolbar.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border-radius: 12px;
                border: 1px solid #e8edf2;
                padding: 12px 20px;
            }
        """)
        
        layout = QHBoxLayout(toolbar)
        layout.setSpacing(10)
        
        # Boutons
        self.btn_add = self._create_btn("➕ Nouveau", "#48bb78")
        self.btn_add.clicked.connect(self.on_add_contact)
        
        self.btn_edit = self._create_btn("✏️ Modifier", "#4299e1")
        self.btn_edit.clicked.connect(self.on_edit_contact)
        self.btn_edit.setEnabled(False)
        
        self.btn_delete = self._create_btn("🗑️ Supprimer", "#fc8181")
        self.btn_delete.clicked.connect(self.on_delete_contact)
        self.btn_delete.setEnabled(False)
        
        self.btn_duplicate = self._create_btn("📋 Dupliquer", "#9f7aea")
        self.btn_duplicate.clicked.connect(self.duplicate_contact)
        self.btn_duplicate.setEnabled(False)
        
        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("background: #e8edf2; max-width: 1px;")
        sep.setFixedWidth(1)
        layout.addWidget(sep)
        
        # Export
        self.btn_export_csv = self._create_btn("📄 CSV", "#ed8936")
        self.btn_export_csv.clicked.connect(self.export_to_csv)
        
        self.btn_export_pdf = self._create_btn("📑 PDF", "#e53e3e")
        self.btn_export_pdf.clicked.connect(self.export_to_pdf)
        
        self.btn_import = self._create_btn("📥 Importer", "#38b2ac")
        self.btn_import.clicked.connect(self.import_contacts)
        
        # Séparateur
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.VLine)
        sep2.setStyleSheet("background: #e8edf2; max-width: 1px;")
        sep2.setFixedWidth(1)
        layout.addWidget(sep2)
        
        # Audit
        self.btn_audit = self._create_btn("📜 Audit", "#805ad5")
        self.btn_audit.clicked.connect(self.show_audit_logs)
        
        # Actualiser
        self.btn_refresh = self._create_btn("🔄 Actualiser", "#718096")
        self.btn_refresh.clicked.connect(self.load_contacts)
        
        layout.addWidget(self.btn_add)
        layout.addWidget(self.btn_edit)
        layout.addWidget(self.btn_delete)
        layout.addWidget(self.btn_duplicate)
        layout.addWidget(sep)
        layout.addWidget(self.btn_export_csv)
        layout.addWidget(self.btn_export_pdf)
        layout.addWidget(self.btn_import)
        layout.addWidget(sep2)
        layout.addWidget(self.btn_audit)
        layout.addWidget(self.btn_refresh)
        
        layout.addStretch()
        
        # Sélection
        self.selection_label = QLabel("")
        self.selection_label.setStyleSheet("color: #718096; font-size: 13px; background: transparent; border: none;")
        layout.addWidget(self.selection_label)
        
        # Recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher...")
        self.search_input.setMinimumWidth(200)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 14px;
                background: #f7fafc;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #4299e1;
                background: #ffffff;
            }
        """)
        self.search_input.textChanged.connect(self.on_search)
        layout.addWidget(self.search_input)
        
        # Filtres - Mise à jour des types
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Tous", "Souscripteur", "Chauffeur", "Particulier", "Société"])
        self.filter_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                background: #f7fafc;
                font-size: 13px;
                min-width: 120px;
            }
            QComboBox:focus {
                border-color: #4299e1;
            }
        """)
        self.filter_combo.currentTextChanged.connect(self.on_filter_changed)
        layout.addWidget(self.filter_combo)
        
        parent_layout.addWidget(toolbar)
    
    def _create_btn(self, text, color):
        """Crée un bouton stylisé"""
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: #2d3748;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 14px;
                font-weight: 500;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {color};
                color: white;
                border-color: {color};
            }}
            QPushButton:disabled {{
                color: #a0aec0;
                border-color: #e2e8f0;
            }}
        """)
        return btn
    
    def _create_stats(self, parent_layout):
        """Crée les statistiques"""
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border-radius: 12px;
                border: 1px solid #e8edf2;
                padding: 16px 20px;
            }
        """)
        
        layout = QHBoxLayout(stats_frame)
        layout.setSpacing(16)
        
        # Cartes de stats - Mise à jour
        stats_data = [
            ("total", "👥", "Total", "#4299e1"),
            ("souscripteurs", "📋", "Souscripteurs", "#48bb78"),
            ("chauffeurs", "🚗", "Chauffeurs", "#ed8936"),
            ("actifs", "⭐", "Actifs", "#9f7aea")
        ]
        
        self.stats_cards = {}
        for key, icon, label, color in stats_data:
            card = self._create_stat_card(icon, label, "0", color)
            layout.addWidget(card)
            self.stats_cards[key] = card
        
        layout.addStretch()
        
        parent_layout.addWidget(stats_frame)
    
    def _create_stat_card(self, icon, label, value, color):
        """Crée une carte de statistique"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {color}08;
                border: 1px solid {color}20;
                border-radius: 10px;
                padding: 10px 16px;
                min-width: 100px;
            }}
        """)
        
        layout = QHBoxLayout(card)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 8, 12, 8)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 20px; background: transparent; border: none;")
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 700;
            color: {color};
            background: transparent;
            border: none;
        """)
        value_label.setObjectName(f"stat_{label.lower()}")
        
        name_label = QLabel(label)
        name_label.setStyleSheet("""
            font-size: 11px;
            color: #718096;
            background: transparent;
            border: none;
        """)
        
        text_layout.addWidget(value_label)
        text_layout.addWidget(name_label)
        
        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        
        return card
    
    def _create_table(self, parent_layout):
        """Crée le tableau"""
        table_container = QFrame()
        table_container.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border-radius: 12px;
                border: 1px solid #e8edf2;
            }
        """)
        
        layout = QVBoxLayout(table_container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # En-tête du tableau
        header = QFrame()
        header.setStyleSheet("background: transparent; border-bottom: 1px solid #e8edf2; padding: 12px 20px;")
        
        header_layout = QHBoxLayout(header)
        
        title = QLabel("📋 Liste des contacts")
        title.setStyleSheet("font-size: 14px; font-weight: 600; color: #1a202c; background: transparent; border: none;")
        
        info = QLabel("Double-cliquez pour voir les détails")
        info.setStyleSheet("font-size: 11px; color: #a0aec0; background: transparent; border: none;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(info)
        
        layout.addWidget(header)
        
        # Tableau - Mise à jour des colonnes
        self.table = QTableWidget()
        self.table.setColumnCount(8)  # Augmenté pour inclure le type
        self.table.setHorizontalHeaderLabels([
            "ID", "CONTACT", "TÉLÉPHONE", "EMAIL", "TYPE", "NATURE", "STATUT", "ACTIONS"
        ])
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        self.table.setStyleSheet("""
            QTableWidget {
                background: transparent;
                border: none;
                outline: none;
                gridline-color: transparent;
                alternate-background-color: #fafbfc;
            }
            QTableWidget::item {
                padding: 12px 12px;
                border-bottom: 1px solid #f0f2f5;
                font-size: 13px;
                color: #2d3748;
            }
            QTableWidget::item:selected {
                background: #ebf4ff;
                color: #1a202c;
            }
            QTableWidget::item:hover {
                background: #f7fafc;
            }
            QHeaderView::section {
                background: #f7fafc;
                padding: 10px 12px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: 600;
                font-size: 11px;
                color: #4a5568;
                text-transform: uppercase;
                letter-spacing: 0.3px;
            }
        """)
        
        # Ajustement des largeurs de colonnes
        self.table.setColumnWidth(0, 50)    # ID
        self.table.setColumnWidth(1, 200)   # CONTACT
        self.table.setColumnWidth(2, 140)   # TÉLÉPHONE
        self.table.setColumnWidth(3, 200)   # EMAIL
        self.table.setColumnWidth(4, 110)   # TYPE
        self.table.setColumnWidth(5, 100)   # NATURE
        self.table.setColumnWidth(6, 100)   # STATUT
        self.table.setColumnWidth(7, 140)   # ACTIONS
        
        # Les colonnes extensibles
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        self.table.setMinimumHeight(400)
        layout.addWidget(self.table)
        
        # Pied
        footer = QFrame()
        footer.setStyleSheet("background: transparent; border-top: 1px solid #e8edf2; padding: 8px 20px;")
        
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        
        self.total_rows_label = QLabel("0 contact(s)")
        self.total_rows_label.setStyleSheet("color: #718096; font-size: 12px; background: transparent; border: none;")
        
        footer_layout.addWidget(self.total_rows_label)
        footer_layout.addStretch()
        
        layout.addWidget(footer)
        
        parent_layout.addWidget(table_container)
    
    def _create_status_bar(self, parent_layout):
        """Crée la barre de statut"""
        status_bar = QFrame()
        status_bar.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border-radius: 12px;
                border: 1px solid #e8edf2;
                padding: 8px 20px;
            }
        """)
        
        layout = QHBoxLayout(status_bar)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.status_label = QLabel("✅ Prêt")
        self.status_label.setStyleSheet("color: #48bb78; font-size: 13px; font-weight: 500; background: transparent; border: none;")
        
        self.last_update_label = QLabel("")
        self.last_update_label.setStyleSheet("color: #a0aec0; font-size: 11px; background: transparent; border: none;")
        
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.last_update_label)
        
        parent_layout.addWidget(status_bar)
    
    # def _create_avatar(self, contact):
    #     """Crée un avatar avec initiales"""
    #     initials = ""
    #     if contact.prenom:
    #         initials += contact.prenom[0].upper()
    #     if contact.nom:
    #         initials += contact.nom[0].upper()
    #     initials = initials or "?"
        
    #     colors = ["#4299e1", "#48bb78", "#ed8936", "#fc8181", "#9f7aea", "#38b2ac"]
    #     color = colors[contact.id % len(colors)] if contact.id else colors[0]
        
    #     avatar = QLabel(initials)
    #     avatar.setFixedSize(36, 36)
    #     avatar.setAlignment(Qt.AlignCenter)
    #     avatar.setStyleSheet(f"""
    #         background: {color};
    #         color: white;
    #         border-radius: 18px;
    #         font-weight: 700;
    #         font-size: 13px;
    #     """)
    #     return avatar
    
    def _create_avatar(self, item):
        """Crée un avatar avec initiales"""
        # ✅ Récupérer nom et prénom correctement
        nom = getattr(item, 'nom', '')
        prenom = getattr(item, 'prenom', '')
        
        if not nom and hasattr(item, 'data'):
            data = getattr(item, 'data', None)
            if data:
                nom = getattr(data, 'nom', '')
                prenom = getattr(data, 'prenom', '')
        
        initials = ""
        if prenom:
            initials += prenom[0].upper()
        if nom:
            initials += nom[0].upper()
        initials = initials or "?"
        
        # ✅ Couleur différente selon le type
        display_type = getattr(item, 'display_type', 'Souscripteur')
        if display_type == "Chauffeur":
            color = "#ed8936"  # Orange
        else:
            color = "#4299e1"  # Bleu
        
        avatar = QLabel(initials)
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(f"""
            background: {color};
            color: white;
            border-radius: 18px;
            font-weight: 700;
            font-size: 13px;
        """)
        return avatar

    def _create_action_buttons(self, item):
        """Crée les boutons d'action"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)
        
        btn_style = """
            QPushButton {
                background: transparent;
                border-radius: 6px;
                font-size: 13px;
                padding: 4px;
                min-width: 28px;
                min-height: 28px;
                border: none;
            }
            QPushButton:hover {
                background: %s;
            }
        """
        
        # ✅ Voir
        btn_view = QPushButton("👁")
        btn_view.setToolTip("Voir les détails")
        btn_view.setStyleSheet(btn_style % "#ebf4ff")
        btn_view.clicked.connect(lambda: self.view_contact(item))
        
        # ✅ Modifier
        btn_edit = QPushButton("✏️")
        btn_edit.setToolTip("Modifier")
        btn_edit.setStyleSheet(btn_style % "#fefcbf")
        btn_edit.clicked.connect(lambda: self.edit_contact(item))
        
        # ✅ Note
        btn_note = QPushButton("📝")
        btn_note.setToolTip("Ajouter une note")
        btn_note.setStyleSheet(btn_style % "#c6f6d5")
        btn_note.clicked.connect(lambda: self.add_quick_note(item))
        
        # ✅ Supprimer
        btn_delete = QPushButton("🗑")
        btn_delete.setToolTip("Supprimer")
        btn_delete.setStyleSheet(btn_style % "#fed7d7")
        btn_delete.clicked.connect(lambda: self.delete_contact(item))
        
        layout.addWidget(btn_view)
        layout.addWidget(btn_edit)
        layout.addWidget(btn_note)
        layout.addWidget(btn_delete)
        
        return container

    # def _create_action_buttons(self, contact):
    #     """Crée les boutons d'action"""
    #     container = QWidget()
    #     layout = QHBoxLayout(container)
    #     layout.setContentsMargins(0, 0, 0, 0)
    #     layout.setSpacing(4)
    #     layout.setAlignment(Qt.AlignCenter)
        
    #     btn_style = """
    #         QPushButton {
    #             background: transparent;
    #             border-radius: 6px;
    #             font-size: 13px;
    #             padding: 4px;
    #             min-width: 28px;
    #             min-height: 28px;
    #             border: none;
    #         }
    #         QPushButton:hover {
    #             background: %s;
    #         }
    #     """
        
    #     # Voir
    #     btn_view = QPushButton("👁")
    #     btn_view.setToolTip("Voir les détails")
    #     btn_view.setStyleSheet(btn_style % "#ebf4ff")
    #     btn_view.clicked.connect(lambda: self.view_contact(contact))
        
    #     # Modifier
    #     btn_edit = QPushButton("✏️")
    #     btn_edit.setToolTip("Modifier")
    #     btn_edit.setStyleSheet(btn_style % "#fefcbf")
    #     btn_edit.clicked.connect(lambda: self.edit_contact(contact))
        
    #     # Note
    #     btn_note = QPushButton("📝")
    #     btn_note.setToolTip("Ajouter une note")
    #     btn_note.setStyleSheet(btn_style % "#c6f6d5")
    #     btn_note.clicked.connect(lambda: self.add_quick_note(contact))
        
    #     # Supprimer
    #     btn_delete = QPushButton("🗑")
    #     btn_delete.setToolTip("Supprimer")
    #     btn_delete.setStyleSheet(btn_style % "#fed7d7")
    #     btn_delete.clicked.connect(lambda: self.delete_contact(contact))
        
    #     layout.addWidget(btn_view)
    #     layout.addWidget(btn_edit)
    #     layout.addWidget(btn_note)
    #     layout.addWidget(btn_delete)
        
    #     return container
    
    # ============================================================
    # FONCTIONS MÉTIER
    # ============================================================
    
    # def load_contacts(self):
    #     """Charge les contacts"""
    #     try:
    #         self.set_status("Chargement...", "info")
    #         self.all_contacts = self.controller.contacts.get_all_contacts()
    #         self.filtered_contacts = self.all_contacts.copy()
    #         self.display_contacts()
    #         self.update_statistics()
    #         self.update_last_update_time()
            
    #         count = len(self.all_contacts)
    #         self.set_status(f"{count} contact(s) chargé(s)", "success")
            
    #     except Exception as e:
    #         self.set_status(f"Erreur: {str(e)}", "error")
    #         logger.error(f"Erreur chargement contacts: {e}")
    
    def load_contacts(self):
        """Charge les contacts (souscripteurs + chauffeurs)"""
        try:
            self.set_status("Chargement...", "info")
            
            # ✅ Forcer le rechargement
            from core.workers.query_cache import query_cache
            query_cache.invalidate('all_contacts_drivers')
            query_cache.invalidate('contacts_all')
            
            self.all_contacts = self.controller.contacts.get_all_contacts_with_drivers(force_refresh=True)
            self.filtered_contacts = self.all_contacts.copy()
            
            # ✅ Log de débogage
            print(f"🔍 {len(self.all_contacts)} entrées chargées")
            for i, entry in enumerate(self.all_contacts):
                print(f"   {i}: {entry.display_type} - {entry.nom} (ID: {entry.id})")
            
            self.display_contacts()
            self.update_statistics()
            self.update_last_update_time()
            
            count = len(self.all_contacts)
            self.set_status(f"{count} contact(s) chargé(s)", "success")
            
        except Exception as e:
            self.set_status(f"Erreur: {str(e)}", "error")
            logger.error(f"Erreur chargement contacts: {e}")
            import traceback
            traceback.print_exc()

    # def display_contacts(self):
    #     """Affiche les contacts"""
    #     self.table.setRowCount(0)
    #     count = len(self.filtered_contacts)
    #     self.total_rows_label.setText(f"{count} contact(s)")
        
    #     for row, contact in enumerate(self.filtered_contacts):
    #         self.table.insertRow(row)
            
    #         # ID
    #         id_item = QTableWidgetItem(str(contact.id))
    #         id_item.setTextAlignment(Qt.AlignCenter)
    #         self.table.setItem(row, 0, id_item)
            
    #         # Contact (avatar + nom)
    #         contact_widget = QWidget()
    #         contact_layout = QHBoxLayout(contact_widget)
    #         contact_layout.setContentsMargins(0, 0, 0, 0)
    #         contact_layout.setSpacing(10)
            
    #         avatar = self._create_avatar(contact)
    #         contact_layout.addWidget(avatar)
            
    #         name = f"{contact.nom or ''} {contact.prenom or ''}".strip()
    #         name_label = QLabel(name or "—")
    #         name_label.setStyleSheet("font-weight: 600; font-size: 13px; color: #1a202c; background: transparent; border: none;")
    #         contact_layout.addWidget(name_label)
    #         contact_layout.addStretch()
            
    #         self.table.setCellWidget(row, 1, contact_widget)
            
    #         # Téléphone
    #         self.table.setItem(row, 2, QTableWidgetItem(contact.telephone or "—"))
            
    #         # Email
    #         self.table.setItem(row, 3, QTableWidgetItem(contact.email or "—"))
            
    #         # Type (Souscripteur/Chauffeur)
    #         type_item = QTableWidgetItem(contact.type_client or "—")
    #         type_item.setTextAlignment(Qt.AlignCenter)
    #         type_item.setForeground(self._get_type_color(contact.type_client))
    #         self.table.setItem(row, 4, type_item)
            
    #         # Nature (Particulier/Société)
    #         nature_item = QTableWidgetItem(contact.nature or "—")
    #         nature_item.setTextAlignment(Qt.AlignCenter)
    #         nature_item.setForeground(self._get_nature_color(contact.nature))
    #         self.table.setItem(row, 5, nature_item)
            
    #         # Statut
    #         status = contact.statut or "Actif"
    #         status_item = QTableWidgetItem(status)
    #         status_item.setTextAlignment(Qt.AlignCenter)
    #         status_item.setForeground(self._get_status_color(status))
    #         self.table.setItem(row, 6, status_item)
            
    #         # Actions
    #         actions = self._create_action_buttons(contact)
    #         self.table.setCellWidget(row, 7, actions)
            
    #         self.table.setRowHeight(row, 56)

    def display_contacts(self):
        """Affiche les contacts (souscripteurs et chauffeurs)"""
        self.table.setRowCount(0)
        count = len(self.filtered_contacts)
        self.total_rows_label.setText(f"{count} contact(s)")
        
        print(f"🔍 Affichage de {count} contacts")
        
        for row, item in enumerate(self.filtered_contacts):
            try:
                self.table.insertRow(row)
                
                # ✅ ID
                id_value = getattr(item, 'id', None) or getattr(item, 'data', None)
                if hasattr(id_value, 'id'):
                    id_value = id_value.id
                id_item = QTableWidgetItem(str(id_value or '—'))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 0, id_item)
                
                # ✅ Contact (avatar + nom)
                contact_widget = QWidget()
                contact_layout = QHBoxLayout(contact_widget)
                contact_layout.setContentsMargins(0, 0, 0, 0)
                contact_layout.setSpacing(10)
                
                avatar = self._create_avatar(item)
                contact_layout.addWidget(avatar)
                
                # ✅ Récupérer le nom correctement
                nom = getattr(item, 'nom', '')
                prenom = getattr(item, 'prenom', '')
                if not nom and hasattr(item, 'data'):
                    # Si c'est un ContactListItem, récupérer depuis data
                    data = getattr(item, 'data', None)
                    if data:
                        nom = getattr(data, 'nom', '')
                        prenom = getattr(data, 'prenom', '')
                
                name = f"{nom or ''} {prenom or ''}".strip()
                name_label = QLabel(name or "—")
                name_label.setStyleSheet("font-weight: 600; font-size: 13px; color: #1a202c; background: transparent; border: none;")
                contact_layout.addWidget(name_label)
                contact_layout.addStretch()
                
                self.table.setCellWidget(row, 1, contact_widget)
                
                # ✅ Téléphone
                telephone = getattr(item, 'telephone', '')
                if not telephone and hasattr(item, 'data'):
                    telephone = getattr(item.data, 'telephone', '')
                self.table.setItem(row, 2, QTableWidgetItem(telephone or "—"))
                
                # ✅ Email
                email = getattr(item, 'email', '')
                if not email and hasattr(item, 'data'):
                    email = getattr(item.data, 'email', '')
                self.table.setItem(row, 3, QTableWidgetItem(email or "—"))
                
                # ✅ Type
                display_type = getattr(item, 'display_type', 'Souscripteur')
                if not display_type and hasattr(item, 'data'):
                    display_type = 'Souscripteur'
                type_item = QTableWidgetItem(display_type)
                type_item.setTextAlignment(Qt.AlignCenter)
                type_item.setForeground(self._get_type_color(display_type))
                self.table.setItem(row, 4, type_item)
                
                # ✅ Nature
                nature = getattr(item, 'nature', '')
                if not nature and hasattr(item, 'data'):
                    nature = getattr(item.data, 'nature', '')
                nature_item = QTableWidgetItem(nature or "—")
                nature_item.setTextAlignment(Qt.AlignCenter)
                nature_item.setForeground(self._get_nature_color(nature))
                self.table.setItem(row, 5, nature_item)
                
                # ✅ Statut
                statut = getattr(item, 'statut', 'Actif')
                if not statut and hasattr(item, 'data'):
                    statut = getattr(item.data, 'statut', 'Actif')
                status_item = QTableWidgetItem(statut)
                status_item.setTextAlignment(Qt.AlignCenter)
                status_item.setForeground(self._get_status_color(statut))
                self.table.setItem(row, 6, status_item)
                
                # ✅ Actions
                actions = self._create_action_buttons(item)
                self.table.setCellWidget(row, 7, actions)
                
                self.table.setRowHeight(row, 56)
                
            except Exception as e:
                print(f"❌ Erreur à la ligne {row}: {e}")
                import traceback
                traceback.print_exc()

    # def update_statistics(self):
    #     """Met à jour les statistiques"""
    #     total = len(self.filtered_contacts)
    #     souscripteurs = len([c for c in self.filtered_contacts if (c.type_client or "") == "Souscripteur"])
    #     chauffeurs = len([c for c in self.filtered_contacts if (c.type_client or "") == "Chauffeur"])
    #     actifs = len([c for c in self.filtered_contacts if (c.statut or "Actif") == "Actif"])
        
    #     self._update_stat_card("total", str(total))
    #     self._update_stat_card("souscripteurs", str(souscripteurs))
    #     self._update_stat_card("chauffeurs", str(chauffeurs))
    #     self._update_stat_card("actifs", str(actifs))
        
    #     # Mettre à jour les compteurs
    #     self._update_counter("total", str(total))
    #     self._update_counter("actifs", str(actifs))

    def update_statistics(self):
        """Met à jour les statistiques"""
        total = len(self.filtered_contacts)
        
        # Compter les souscripteurs (contacts)
        souscripteurs = len([e for e in self.filtered_contacts if getattr(e, 'display_type', '') == "Souscripteur" or getattr(e, 'source', '') == 'contact'])
        
        # Compter les chauffeurs (drivers)
        chauffeurs = len([e for e in self.filtered_contacts if getattr(e, 'display_type', '') == "Chauffeur" or getattr(e, 'source', '') == 'driver'])
        
        # Compter les actifs
        actifs = 0
        for e in self.filtered_contacts:
            statut = getattr(e, 'statut', 'Actif')
            if statut == "Actif":
                actifs += 1
        
        self._update_stat_card("total", str(total))
        self._update_stat_card("souscripteurs", str(souscripteurs))
        self._update_stat_card("chauffeurs", str(chauffeurs))
        self._update_stat_card("actifs", str(actifs))
        
        # Mettre à jour les compteurs
        self._update_counter("total", str(total))
        self._update_counter("actifs", str(actifs))

    def _update_stat_card(self, key, value):
        """Met à jour une carte statistique"""
        card = self.stats_cards.get(key)
        if card:
            for label in card.findChildren(QLabel):
                if label.objectName().startswith("stat_"):
                    label.setText(value)
                    break
    
    def _update_counter(self, key, value):
        """Met à jour un compteur"""
        for label in self.findChildren(QLabel):
            if label.objectName() == f"counter_{key}":
                label.setText(value)
                break
    
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
        self.btn_edit.setEnabled(count == 1)
        self.btn_delete.setEnabled(count > 0)
        self.btn_duplicate.setEnabled(count == 1)
        
        self.selection_label.setText(f"{count} sélectionné(s)" if count > 0 else "")
        
        if count == 1:
            self.contact_selected.emit(self.selected_contacts[0])
    
    def on_item_double_clicked(self, item):
        """Double-clic pour voir les détails"""
        row = item.row()
        if row < len(self.filtered_contacts):
            self.view_contact(self.filtered_contacts[row])
    
    def on_search(self):
        """Recherche"""
        self.apply_filters()
    
    def on_filter_changed(self):
        """Filtre"""
        self.apply_filters()
    
    # def apply_filters(self):
    #     """Applique les filtres"""
    #     search_text = self.search_input.text().strip().lower()
    #     filter_text = self.filter_combo.currentText()
        
    #     filtered = self.all_contacts.copy()
        
    #     if search_text:
    #         filtered = [c for c in filtered if self._matches_search(c, search_text)]
        
    #     if filter_text != "Tous":
    #         if filter_text in ["Souscripteur", "Chauffeur"]:
    #             filtered = [c for c in filtered if (c.type_client or "") == filter_text]
    #         elif filter_text in ["Particulier", "Société"]:
    #             filtered = [c for c in filtered if (c.nature or "") == filter_text]
        
    #     self.filtered_contacts = filtered
    #     self.display_contacts()
    #     self.update_statistics()
    #     self.set_status(f"{len(filtered)} contact(s) trouvé(s)", "info")
    
    def apply_filters(self):
        """Applique les filtres"""
        search_text = self.search_input.text().strip().lower()
        filter_text = self.filter_combo.currentText()
        
        filtered = self.all_contacts.copy()
        
        if search_text:
            filtered = [e for e in filtered if self._matches_search(e, search_text)]
        
        if filter_text != "Tous":
            if filter_text == "Souscripteur":
                filtered = [e for e in filtered if getattr(e, 'display_type', '') == "Souscripteur" or getattr(e, 'source', '') == 'contact']
            elif filter_text == "Chauffeur":
                filtered = [e for e in filtered if getattr(e, 'display_type', '') == "Chauffeur" or getattr(e, 'source', '') == 'driver']
            elif filter_text in ["Particulier", "Société"]:
                filtered = [e for e in filtered if getattr(e, 'nature', '') == filter_text]
        
        self.filtered_contacts = filtered
        self.display_contacts()
        self.update_statistics()
        self.set_status(f"{len(filtered)} contact(s) trouvé(s)", "info")

    # def _matches_search(self, contact, search_text):
    #     """Vérifie si le contact correspond à la recherche"""
    #     return any([
    #         search_text in (contact.nom or "").lower(),
    #         search_text in (contact.prenom or "").lower(),
    #         search_text in (contact.telephone or "").lower(),
    #         search_text in (contact.email or "").lower(),
    #         search_text in (contact.type_client or "").lower(),
    #         search_text in (contact.nature or "").lower(),
    #         search_text in (contact.code_client or "").lower(),
    #         search_text in (contact.code_chauffeur or "").lower()
    #     ])
    
    def _matches_search(self, entry, search_text):
        """Vérifie si l'entrée correspond à la recherche"""
        # ✅ Récupérer les valeurs avec gestion de None
        nom = getattr(entry, 'nom', '') or ''
        prenom = getattr(entry, 'prenom', '') or ''
        telephone = getattr(entry, 'telephone', '') or ''
        email = getattr(entry, 'email', '') or ''
        
        # Pour les contacts
        type_client = getattr(entry, 'type_client', '') or ''
        nature = getattr(entry, 'nature', '') or ''
        code_client = getattr(entry, 'code_client', '') or ''
        code_chauffeur = getattr(entry, 'code_chauffeur', '') or ''
        
        # Pour les chauffeurs
        display_type = getattr(entry, 'display_type', '') or ''
        specialite = getattr(entry, 'specialite', '') or ''
        
        # Convertir en minuscules pour la recherche
        search_lower = search_text.lower()
        
        return any([
            search_lower in nom.lower(),
            search_lower in prenom.lower(),
            search_lower in telephone.lower(),
            search_lower in email.lower(),
            search_lower in type_client.lower(),
            search_lower in nature.lower(),
            search_lower in code_client.lower(),
            search_lower in code_chauffeur.lower(),
            search_lower in display_type.lower(),
            search_lower in specialite.lower()
        ])

    # ============================================================
    # CRUD
    # ============================================================
    
    def on_add_contact(self):
        """Ajoute un contact"""
        # ✅ Passer le bon contrôleur
        dialog = ContactForm(self.controller, parent=self)
        if dialog.exec_():
            # ✅ Récupérer les données via la méthode corrigée
            data = dialog._get_data()
            contact, success, message = self.controller.contacts.create_contact(data)
            if success:
                self.load_contacts()
                self.set_status("Contact ajouté", "success")
            else:
                self.set_status(f"Erreur: {message}", "error")
    
    def on_edit_contact(self):
        """Modifie un contact"""
        if len(self.selected_contacts) == 1:
            self.edit_contact(self.selected_contacts[0])
    
    def edit_contact(self, contact):
        """Modifie un contact"""
        fresh_contact = self.controller.contacts.get_contact_by_id(contact.id)
        if fresh_contact:
            # ✅ Passer le bon contrôleur
            dialog = ContactForm(self.controller, fresh_contact, parent=self, mode="edit")
            if dialog.exec_():
                self.load_contacts()
                self.contact_updated.emit()
                self.set_status("Contact modifié", "success")
    
    def view_contact(self, contact):
        """Voir les détails d'un contact"""
        from addons.Automobiles.views.contact_detail_view import ContactDetailView
        dialog = ContactDetailView(self.controller, contact, self)
        dialog.contact_updated.connect(self.load_contacts)
        dialog.exec_()
    
    def delete_contact(self, contact):
        """Supprime un contact"""
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
                self.set_status("Contact supprimé", "success")
    
    def on_delete_contact(self):
        """Supprime plusieurs contacts"""
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
        """Duplique un contact"""
        if len(self.selected_contacts) == 1:
            contact = self.selected_contacts[0]
            new_data = {
                'nom': contact.nom + " (Copie)" if contact.nom else "Copie",
                'prenom': contact.prenom,
                'telephone': contact.telephone,
                'email': contact.email,
                'type_client': contact.type_client,
                'nature': contact.nature,
                'statut': contact.statut,
                'code_client': contact.code_client + "_COPY" if contact.code_client else None,
                'code_chauffeur': contact.code_chauffeur + "_COPY" if contact.code_chauffeur else None
            }
            contact, success, message = self.controller.contacts.create_contact(new_data)
            if success:
                self.load_contacts()
                self.set_status("Contact dupliqué", "success")
    
    def import_contacts(self):
        """Importe des contacts"""
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
        """Ajoute une note rapide"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"📝 Note - {contact.nom}")
        dialog.resize(450, 250)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        
        info = QLabel(f"Contact: {contact.nom} {contact.prenom or ''}")
        info.setStyleSheet("font-weight: 600; color: #1a202c; background: transparent; border: none;")
        layout.addWidget(info)
        
        note_input = QTextEdit()
        note_input.setPlaceholderText("Écrivez votre note ici...")
        note_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
            }
            QTextEdit:focus {
                border-color: #4299e1;
            }
        """)
        layout.addWidget(note_input)
        
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: #f7fafc;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #edf2f7;
            }
        """)
        btn_cancel.clicked.connect(dialog.reject)
        
        btn_save = QPushButton("💾 Enregistrer")
        btn_save.setStyleSheet("""
            QPushButton {
                background: #4299e1;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #3182ce;
            }
        """)
        
        def on_save():
            note = note_input.toPlainText().strip()
            if note:
                # ✅ Utiliser la méthode existante ou ajouter une méthode add_note
                self.controller.contacts.log_contact_action(
                    action="NOTE_ADDED",
                    contact_id=contact.id,
                    details=note
                )
                self.set_status("Note ajoutée", "success")
                dialog.accept()
            else:
                QMessageBox.warning(dialog, "Attention", "Veuillez écrire une note.")
        
        btn_save.clicked.connect(on_save)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)
        
        dialog.exec_()
    
    # ============================================================
    # EXPORTS
    # ============================================================
    
    def export_to_csv(self):
        """Exporte en CSV"""
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
                    writer.writerow(["ID", "Nom", "Prénom", "Téléphone", "Email", "Type", "Nature", "Statut"])
                    for c in self.filtered_contacts:
                        writer.writerow([
                            c.id, c.nom or "", c.prenom or "", c.telephone or "",
                            c.email or "", c.type_client or "", c.nature or "", c.statut or "Actif"
                        ])
                self.set_status("Export CSV réussi", "success")
            except Exception as e:
                self.set_status(f"Erreur export: {str(e)}", "error")
    
    def export_to_pdf(self):
        """Exporte en PDF"""
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
                    'type': c.type_client, 'nature': c.nature, 'statut': c.statut
                } for c in self.filtered_contacts]
                
                stats = {
                    'total': len(contacts_data),
                    'souscripteurs': len([c for c in contacts_data if c['type'] == "Souscripteur"]),
                    'chauffeurs': len([c for c in contacts_data if c['type'] == "Chauffeur"]),
                    'actifs': len([c for c in contacts_data if c['statut'] == "Actif"])
                }
                
                generate_contact_pdf(path, contacts_data, stats)
                self.set_status("Export PDF réussi", "success")
            except Exception as e:
                self.set_status(f"Erreur export: {str(e)}", "error")
    
    def show_audit_logs(self):
        """Affiche les logs d'audit"""
        try:
            logs = self.controller.contacts.get_audit_logs()
            if not logs:
                QMessageBox.information(self, "Audit", "Aucun historique disponible")
                return
            
            dialog = QDialog(self)
            dialog.setWindowTitle("📜 Journal d'audit")
            dialog.resize(1000, 600)
            
            layout = QVBoxLayout(dialog)
            layout.setSpacing(12)
            
            title = QLabel("📜 Historique des actions")
            title.setStyleSheet("font-size: 18px; font-weight: 700; color: #1a202c; background: transparent; border: none;")
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
                    border-radius: 8px;
                }
                QHeaderView::section {
                    background: #f7fafc;
                    padding: 10px;
                    font-weight: 600;
                }
                QTableWidget::item {
                    padding: 10px;
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
            table.setColumnWidth(0, 160)
            table.setColumnWidth(1, 120)
            table.setColumnWidth(2, 100)
            
            layout.addWidget(table)
            
            btn_close = QPushButton("Fermer")
            btn_close.setStyleSheet("""
                QPushButton {
                    background: #4299e1;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: #3182ce;
                }
            """)
            btn_close.clicked.connect(dialog.accept)
            layout.addWidget(btn_close)
            
            dialog.exec_()
        except Exception as e:
            self.set_status(f"Erreur: {str(e)}", "error")
    
    def show_context_menu(self, position):
        """Affiche le menu contextuel"""
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background: #ebf4ff;
            }
        """)
        
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
        """Duplique un contact spécifique"""
        new_data = {
            'nom': contact.nom + " (Copie)" if contact.nom else "Copie",
            'prenom': contact.prenom,
            'telephone': contact.telephone,
            'email': contact.email,
            'type_client': contact.type_client,
            'nature': contact.nature,
            'statut': contact.statut
        }
        contact, success, message = self.controller.contacts.create_contact(new_data)
        if success:
            self.load_contacts()
            self.set_status("Contact dupliqué", "success")
    
    # ============================================================
    # UTILITAIRES
    # ============================================================
    
    def _get_type_color(self, contact_type):
        """Couleur selon le type de client"""
        colors = {
            "Souscripteur": QColor("#48bb78"),
            "Chauffeur": QColor("#ed8936"),
            "Assuré": QColor("#48bb78"),
            "Prospect": QColor("#ed8936"),
            "Partenaire": QColor("#9f7aea"),
            "Fournisseur": QColor("#38b2ac")
        }
        return colors.get(contact_type, QColor("#718096"))
    
    def _get_nature_color(self, nature):
        """Couleur selon la nature"""
        colors = {
            "Particulier": QColor("#4299e1"),
            "Société": QColor("#9f7aea"),
            "Personne Physique": QColor("#4299e1"),
            "Personne Morale": QColor("#9f7aea")
        }
        return colors.get(nature, QColor("#718096"))
    
    def _get_status_color(self, status):
        """Couleur selon le statut"""
        colors = {
            "Actif": QColor("#48bb78"),
            "Inactif": QColor("#fc8181"),
            "En attente": QColor("#ed8936"),
            "Suspendu": QColor("#ed8936")
        }
        return colors.get(status, QColor("#718096"))
    
    def set_status(self, message, msg_type="info"):
        """Définit le message de statut"""
        icons = {"success": "✅", "error": "❌", "info": "ℹ️", "warning": "⚠️"}
        colors = {"success": "#48bb78", "error": "#fc8181", "info": "#4299e1", "warning": "#ed8936"}
        
        self.status_label.setText(f"{icons.get(msg_type, 'ℹ️')} {message}")
        self.status_label.setStyleSheet(f"color: {colors.get(msg_type, '#718096')}; font-size: 13px; font-weight: 500; background: transparent; border: none;")
        
        if msg_type != "error":
            QTimer.singleShot(3000, lambda: self.status_label.setText("✅ Prêt"))
    
    def update_last_update_time(self):
        """Met à jour l'heure de dernière mise à jour"""
        self.last_update_label.setText(f"Dernière mise à jour: {datetime.now().strftime('%H:%M:%S')}")
    
    def apply_security_policy(self):
        """Applique la politique de sécurité"""
        if hasattr(self.current_user, 'role'):
            role = self.current_user.role
            if not SecurityManager.has_permission(role, Permissions.CONTACT_ADD):
                self.btn_add.setVisible(False)
            if not SecurityManager.has_permission(role, Permissions.CONTACT_EDIT):
                self.btn_edit.setVisible(False)
            if not SecurityManager.has_permission(role, Permissions.CONTACT_DELETE):
                self.btn_delete.setVisible(False)
            if not SecurityManager.has_permission(role, Permissions.AUDIT_VIEW):
                self.btn_audit.setVisible(False)
    
    def refresh(self):
        """Rafraîchit la vue"""
        self.load_contacts()

    def get_driver_by_id(self, driver_id):
        """Récupère un chauffeur par son ID"""
        try:
            from addons.Automobiles.models.driver_models import Driver
            return self.db.query(Driver).filter(Driver.id == driver_id).first()
        except Exception as e:
            print(f"Erreur get_driver_by_id: {e}")
            return None

    def delete_driver(self, driver_id):
        """Supprime un chauffeur"""
        try:
            from addons.Automobiles.models.driver_models import Driver
            driver = self.db.query(Driver).filter(Driver.id == driver_id).first()
            if driver:
                self.db.delete(driver)
                self.db.commit()
                return True
            return False
        except Exception as e:
            print(f"Erreur delete_driver: {e}")
            self.db.rollback()
            return False
    
    def setup_shortcuts(self):
        """Configure les raccourcis clavier"""
        shortcuts = [
            ("Ctrl+N", self.on_add_contact),
            ("Ctrl+E", self.on_edit_contact),
            ("Delete", self.on_delete_contact),
            ("Ctrl+R", self.load_contacts),
            ("Ctrl+F", lambda: self.search_input.setFocus()),
            ("Ctrl+D", self.duplicate_contact),
        ]
        for key, callback in shortcuts:
            action = QAction(self)
            action.setShortcut(key)
            action.triggered.connect(callback)
            self.addAction(action)