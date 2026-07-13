# # contacts_view.py - Version améliorée avec toutes les fonctionnalités
# import os
# from datetime import datetime
# from PySide6.QtWidgets import (
#     QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
#     QFrame, QLineEdit, QTableWidget, QTableWidgetItem, 
#     QHeaderView, QMessageBox, QFileDialog, QScrollArea,
#     QSizePolicy, QDialog, QComboBox, QMenu, QTextEdit, QCheckBox
# )
# from PySide6.QtCore import Qt, QTimer, Signal, QSize
# from PySide6.QtGui import QFont, QColor, QAction, QBrush

# from addons.Automobiles.security.access_control import Permissions, SecurityManager
# from addons.Automobiles.views.contact_form_view import ContactForm
# from addons.Automobiles.reports.pdf_generator import generate_contact_pdf
# from core.logger import logger
# from core.workers.database_worker import async_query


# class ContactListView(QWidget):
#     """Interface professionnelle pour la gestion des contacts"""
    
#     contact_selected = Signal(object)
#     contact_updated = Signal()
    
#     def __init__(self, controller, current_user):
#         super().__init__()
#         self.controller = controller
#         self.current_user = current_user
#         self._data_loaded = False
#         self.all_contacts = []
#         self.filtered_contacts = []
#         self.selected_contacts = []
#         self.dark_mode = False
        
#         self.setup_ui()
#         self.apply_security_policy()
#         self.load_contacts()
#         self.setup_shortcuts()
#         self.setup_advanced_shortcuts()

#     def showEvent(self, event):
#         """Appelé quand la vue est affichée"""
#         super().showEvent(event)
#         if not self._data_loaded:
#             self._data_loaded = True
#             QTimer.singleShot(50, self.load_contacts_async)

#     def load_contacts_async(self):
#         """Charge les contacts de manière asynchrone"""
#         async_query.execute(
#             self.controller.contacts.get_all,
#             on_finished=self.on_contacts_loaded,
#             on_error=self.on_load_error,
#             show_loader=True,
#             loader_message="Chargement des contacts..."
#         )
    
#     def setup_ui(self):
#         """Configure l'interface utilisateur avec ScrollArea"""
#         main_layout = QVBoxLayout(self)
#         main_layout.setContentsMargins(0, 0, 0, 0)
#         main_layout.setSpacing(0)
        
#         # Scroll area principale
#         self.scroll_area = QScrollArea()
#         self.scroll_area.setWidgetResizable(True)
#         self.scroll_area.setFrameShape(QFrame.NoFrame)
#         self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
#         self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
#         self.scroll_area.setStyleSheet("""
#             QScrollArea {
#                 background-color: #f0f2f5;
#                 border: none;
#             }
#             QScrollBar:vertical {
#                 background-color: #e4e7eb;
#                 width: 10px;
#                 border-radius: 5px;
#             }
#             QScrollBar::handle:vertical {
#                 background-color: #cbd5e1;
#                 border-radius: 5px;
#                 min-height: 30px;
#             }
#             QScrollBar::handle:vertical:hover {
#                 background-color: #94a3b8;
#             }
#         """)
        
#         container = QWidget()
#         container.setStyleSheet("background-color: #f0f2f5;")
#         self.container_layout = QVBoxLayout(container)
#         self.container_layout.setContentsMargins(24, 24, 24, 24)
#         self.container_layout.setSpacing(24)
        
#         # Sections
#         self._create_header()
#         self._create_search_bar()
#         self._create_stats_panel()
#         self._create_toolbar()
#         self._create_enhanced_table()
#         self._create_status_bar()
        
#         self.container_layout.addSpacing(20)
#         self.scroll_area.setWidget(container)
#         main_layout.addWidget(self.scroll_area)
#         self._apply_global_style()
    
#     def _apply_global_style(self):
#         self.setStyleSheet("""
#             QWidget {
#                 background-color: #f0f2f5;
#                 font-family: 'Segoe UI', 'Roboto', sans-serif;
#                 font-size: 13px;
#             }
#             QFrame {
#                 background-color: white;
#                 border-radius: 12px;
#             }
#             QLineEdit, QComboBox {
#                 border: 1px solid #e2e8f0;
#                 border-radius: 10px;
#                 padding: 10px 14px;
#                 background-color: white;
#                 font-size: 13px;
#             }
#             QLineEdit:focus, QComboBox:focus {
#                 border-color: #3b82f6;
#                 outline: none;
#             }
#             QPushButton {
#                 border: none;
#                 border-radius: 8px;
#                 padding: 8px 16px;
#                 font-weight: 500;
#             }
#             QPushButton:hover {
#                 background-color: #f8fafc;
#             }
#         """)
    
#     def _create_header(self):
#         header_frame = QFrame()
#         header_frame.setMinimumHeight(120)
#         header_frame.setStyleSheet("""
#             QFrame {
#                 background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
#                     stop:0 #1e293b, stop:1 #0f172a);
#                 border-radius: 16px;
#             }
#         """)
        
#         header_layout = QHBoxLayout(header_frame)
#         header_layout.setContentsMargins(30, 20, 30, 20)
        
#         title_container = QVBoxLayout()
#         title_container.setSpacing(8)
        
#         title = QLabel("📇 Gestion des Contacts")
#         title.setStyleSheet("font-size: 28px; font-weight: 700; color: white;")
        
#         subtitle = QLabel("Gérez efficacement tous vos contacts, clients et prospects")
#         subtitle.setStyleSheet("font-size: 14px; color: #94a3b8;")
        
#         title_container.addWidget(title)
#         title_container.addWidget(subtitle)
        
#         self.counter_label = QLabel("0 contact(s)")
#         self.counter_label.setStyleSheet("""
#             background-color: #3b82f6;
#             color: white;
#             padding: 10px 24px;
#             border-radius: 30px;
#             font-weight: 600;
#             font-size: 15px;
#         """)
        
#         header_layout.addLayout(title_container)
#         header_layout.addStretch()
#         header_layout.addWidget(self.counter_label)
        
#         self.container_layout.addWidget(header_frame)
    
#     def _create_search_bar(self):
#         search_frame = QFrame()
#         search_frame.setStyleSheet("QFrame { background-color: white; border-radius: 12px; }")
        
#         self.search_layout = QVBoxLayout(search_frame)
#         self.search_layout.setContentsMargins(20, 20, 20, 20)
#         self.search_layout.setSpacing(15)
        
#         self.search_input = QLineEdit()
#         self.search_input.setPlaceholderText("🔍 Rechercher par nom, téléphone, email, adresse...")
#         self.search_input.setMinimumHeight(45)
#         self.search_input.textChanged.connect(self.on_search)
#         self.search_layout.addWidget(self.search_input)
        
#         filters_layout = QHBoxLayout()
#         filters_layout.setSpacing(15)
        
#         type_container = QVBoxLayout()
#         type_container.setSpacing(5)
#         type_label = QLabel("Type de contact")
#         type_label.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600;")
#         self.type_filter = QComboBox()
#         self.type_filter.addItems(["Tous les types", "Assuré", "Prospect", "Partenaire", "Fournisseur"])
#         self.type_filter.setMinimumHeight(40)
#         self.type_filter.currentTextChanged.connect(self.on_filter_changed)
#         type_container.addWidget(type_label)
#         type_container.addWidget(self.type_filter)
        
#         status_container = QVBoxLayout()
#         status_container.setSpacing(5)
#         status_label = QLabel("Statut")
#         status_label.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600;")
#         self.status_filter = QComboBox()
#         self.status_filter.addItems(["Tous les statuts", "Actif", "Inactif", "En attente"])
#         self.status_filter.setMinimumHeight(40)
#         self.status_filter.currentTextChanged.connect(self.on_filter_changed)
#         status_container.addWidget(status_label)
#         status_container.addWidget(self.status_filter)
        
#         date_container = QVBoxLayout()
#         date_container.setSpacing(5)
#         date_label = QLabel("Date de création")
#         date_label.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600;")
#         self.date_filter = QComboBox()
#         self.date_filter.addItems(["Toutes les dates", "Aujourd'hui", "Cette semaine", "Ce mois", "Cette année"])
#         self.date_filter.setMinimumHeight(40)
#         self.date_filter.currentTextChanged.connect(self.on_filter_changed)
#         date_container.addWidget(date_label)
#         date_container.addWidget(self.date_filter)
        
#         reset_btn = QPushButton("🔄 Réinitialiser")
#         reset_btn.setMinimumHeight(40)
#         reset_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: #f1f5f9;
#                 color: #475569;
#                 font-weight: 600;
#                 margin-top: 20px;
#             }
#             QPushButton:hover {
#                 background-color: #e2e8f0;
#             }
#         """)
#         reset_btn.clicked.connect(self.reset_filters)
        
#         filters_layout.addLayout(type_container, 1)
#         filters_layout.addLayout(status_container, 1)
#         filters_layout.addLayout(date_container, 1)
#         filters_layout.addWidget(reset_btn, 1)
        
#         self.search_layout.addLayout(filters_layout)
        
#         # Ajout des filtres avancés
#         self._create_advanced_filters()
        
#         self.container_layout.addWidget(search_frame)
    
#     def _create_advanced_filters(self):
#         """Ajoute des filtres avancés"""
#         advanced_layout = QHBoxLayout()
#         advanced_layout.setSpacing(15)
        
#         # Filtre par tag
#         tag_container = QVBoxLayout()
#         tag_container.setSpacing(5)
#         tag_label = QLabel("Tag")
#         tag_label.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600;")
#         self.tag_filter = QComboBox()
#         self.tag_filter.addItems(["Tous les tags", "VIP", "Urgent", "À suivre", "Important"])
#         self.tag_filter.setMinimumHeight(40)
#         self.tag_filter.currentTextChanged.connect(self.on_filter_changed)
#         tag_container.addWidget(tag_label)
#         tag_container.addWidget(self.tag_filter)
        
#         # Filtre par anniversaire
#         birthday_container = QVBoxLayout()
#         birthday_container.setSpacing(5)
#         birthday_label = QLabel("Anniversaire")
#         birthday_label.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600;")
#         self.birthday_filter = QComboBox()
#         self.birthday_filter.addItems(["Tous", "🎂 Ce mois", "🎂 Ce trimestre"])
#         self.birthday_filter.setMinimumHeight(40)
#         self.birthday_filter.currentTextChanged.connect(self.on_filter_changed)
#         birthday_container.addWidget(birthday_label)
#         birthday_container.addWidget(self.birthday_filter)
        
#         advanced_layout.addLayout(tag_container, 1)
#         advanced_layout.addLayout(birthday_container, 1)
#         advanced_layout.addStretch()
        
#         self.search_layout.addLayout(advanced_layout)
    
#     def _create_stats_panel(self):
#         stats_frame = QFrame()
#         stats_frame.setStyleSheet("QFrame { background-color: white; border-radius: 12px; }")
        
#         stats_layout = QVBoxLayout(stats_frame)
#         stats_layout.setContentsMargins(20, 20, 20, 20)
#         stats_layout.setSpacing(15)
        
#         stats_title = QLabel("📊 Tableau de bord")
#         stats_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #1e293b;")
#         stats_layout.addWidget(stats_title)
        
#         cards_layout = QHBoxLayout()
#         cards_layout.setSpacing(20)
        
#         self.stats_cards = {}
#         stats_data = [
#             ("total", "Total", "📊", "#3b82f6"),
#             ("assures", "Assurés", "✅", "#10b981"),
#             ("prospects", "Prospects", "🎯", "#f59e0b"),
#             ("actifs", "Actifs", "⭐", "#8b5cf6")
#         ]
        
#         for stat_key, label, icon, color in stats_data:
#             card = self._create_stat_card(icon, label, "0", color, stat_key)
#             cards_layout.addWidget(card)
#             self.stats_cards[stat_key] = card
        
#         quick_export = QPushButton("📎 Export rapide")
#         quick_export.setMinimumHeight(50)
#         quick_export.setStyleSheet("""
#             QPushButton {
#                 background-color: #10b981;
#                 color: white;
#                 font-weight: 600;
#                 font-size: 14px;
#             }
#             QPushButton:hover { background-color: #059669; }
#         """)
#         quick_export.clicked.connect(self.export_to_csv)
#         cards_layout.addWidget(quick_export)
        
#         stats_layout.addLayout(cards_layout)
#         self.container_layout.addWidget(stats_frame)
    
#     def _create_stat_card(self, icon, label, value, color, stat_key):
#         card = QFrame()
#         card.setStyleSheet(f"""
#             QFrame {{
#                 background-color: {color}08;
#                 border: 1px solid {color}20;
#                 border-radius: 12px;
#             }}
#         """)
#         card.setMinimumHeight(100)
        
#         layout = QHBoxLayout(card)
#         layout.setContentsMargins(20, 15, 20, 15)
#         layout.setSpacing(15)
        
#         icon_label = QLabel(icon)
#         icon_label.setStyleSheet(f"font-size: 36px;")
        
#         text_layout = QVBoxLayout()
#         text_layout.setSpacing(5)
        
#         value_label = QLabel(value)
#         value_label.setStyleSheet(f"""
#             font-size: 28px;
#             font-weight: 800;
#             color: {color};
#         """)
#         value_label.setObjectName(f"stat_{stat_key}")
        
#         name_label = QLabel(label)
#         name_label.setStyleSheet("font-size: 12px; color: #6b7280; font-weight: 500;")
        
#         text_layout.addWidget(value_label)
#         text_layout.addWidget(name_label)
        
#         layout.addWidget(icon_label)
#         layout.addLayout(text_layout)
#         layout.addStretch()
        
#         return card
    
#     def _create_toolbar(self):
#         toolbar_frame = QFrame()
#         toolbar_frame.setStyleSheet("QFrame { background-color: white; border-radius: 12px; }")
        
#         self.toolbar_layout = QHBoxLayout(toolbar_frame)
#         self.toolbar_layout.setContentsMargins(20, 15, 20, 15)
#         self.toolbar_layout.setSpacing(12)
        
#         # Boutons principaux
#         self.add_btn = self._create_action_button("➕ Nouveau contact", "#3b82f6")
#         self.add_btn.clicked.connect(self.on_add_contact)
        
#         self.edit_btn = self._create_action_button("✏️ Modifier", "#8b5cf6")
#         self.edit_btn.clicked.connect(self.on_edit_contact)
#         self.edit_btn.setEnabled(False)
        
#         self.delete_btn = self._create_action_button("🗑️ Supprimer", "#ef4444")
#         self.delete_btn.clicked.connect(self.on_delete_contact)
#         self.delete_btn.setEnabled(False)
        
#         separator1 = QFrame()
#         separator1.setFrameShape(QFrame.VLine)
#         separator1.setStyleSheet("background-color: #e5e7eb; max-width: 1px;")
#         separator1.setFixedWidth(1)
        
#         # Nouveaux boutons
#         self.import_btn = self._create_action_button("📥 Importer", "#059669")
#         self.import_btn.clicked.connect(self.import_contacts)
        
#         self.duplicate_btn = self._create_action_button("📋 Dupliquer", "#6b7280")
#         self.duplicate_btn.clicked.connect(self.duplicate_contact)
#         self.duplicate_btn.setEnabled(False)
        
#         separator2 = QFrame()
#         separator2.setFrameShape(QFrame.VLine)
#         separator2.setStyleSheet("background-color: #e5e7eb; max-width: 1px;")
#         separator2.setFixedWidth(1)
        
#         self.export_csv_btn = self._create_action_button("📄 CSV", "#6b7280")
#         self.export_csv_btn.clicked.connect(self.export_to_csv)
        
#         self.export_pdf_btn = self._create_action_button("📑 PDF", "#6b7280")
#         self.export_pdf_btn.clicked.connect(self.export_to_pdf)
        
#         refresh_btn = self._create_action_button("🔄 Actualiser", "#6b7280")
#         refresh_btn.clicked.connect(self.load_contacts)
        
#         self.audit_btn = self._create_action_button("📜 Audit", "#6b7280")
#         self.audit_btn.clicked.connect(self.show_audit_logs)
        
#         separator3 = QFrame()
#         separator3.setFrameShape(QFrame.VLine)
#         separator3.setStyleSheet("background-color: #e5e7eb; max-width: 1px;")
#         separator3.setFixedWidth(1)
        
#         # Bouton de thème
#         self.theme_btn = QPushButton("🌙")
#         self.theme_btn.setFixedSize(42, 42)
#         self.theme_btn.setToolTip("Basculer le thème (Ctrl+T)")
#         self.theme_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: #f1f5f9;
#                 border-radius: 10px;
#                 font-size: 18px;
#             }
#             QPushButton:hover {
#                 background-color: #e2e8f0;
#             }
#         """)
#         self.theme_btn.clicked.connect(self.toggle_theme)
        
#         # Ajout des boutons à la toolbar
#         self.toolbar_layout.addWidget(self.add_btn)
#         self.toolbar_layout.addWidget(self.edit_btn)
#         self.toolbar_layout.addWidget(self.delete_btn)
#         self.toolbar_layout.addWidget(separator1)
#         self.toolbar_layout.addWidget(self.import_btn)
#         self.toolbar_layout.addWidget(self.duplicate_btn)
#         self.toolbar_layout.addWidget(separator2)
#         self.toolbar_layout.addWidget(self.export_csv_btn)
#         self.toolbar_layout.addWidget(self.export_pdf_btn)
#         self.toolbar_layout.addWidget(refresh_btn)
#         self.toolbar_layout.addWidget(self.audit_btn)
#         self.toolbar_layout.addWidget(separator3)
#         self.toolbar_layout.addWidget(self.theme_btn)
#         self.toolbar_layout.addStretch()
        
#         self.selection_label = QLabel("")
#         self.selection_label.setStyleSheet("color: #64748b; font-size: 13px; font-weight: 500;")
#         self.toolbar_layout.addWidget(self.selection_label)
        
#         self.container_layout.addWidget(toolbar_frame)
    
#     def on_load_error(self, error):
#         """Gère les erreurs"""
#         QMessageBox.warning(self, "Erreur", f"Erreur de chargement: {error}")

#     def _create_action_button(self, text, color):
#         btn = QPushButton(text)
#         btn.setMinimumHeight(42)
#         btn.setStyleSheet(f"""
#             QPushButton {{
#                 background-color: {color};
#                 color: white;
#                 padding: 10px 20px;
#                 font-weight: 600;
#                 font-size: 13px;
#                 border-radius: 10px;
#             }}
#             QPushButton:hover {{
#                 background-color: {color}dd;
#             }}
#             QPushButton:disabled {{
#                 background-color: #cbd5e1;
#                 color: #94a3b8;
#             }}
#         """)
#         return btn
    
#     def _create_enhanced_table(self):
#         """Crée un tableau avec des boutons compacts et avatars"""
        
#         table_container = QFrame()
#         table_container.setStyleSheet("""
#             QFrame {
#                 background-color: white;
#                 border-radius: 16px;
#             }
#         """)
        
#         table_layout = QVBoxLayout(table_container)
#         table_layout.setContentsMargins(0, 0, 0, 0)
        
#         # En-tête du tableau
#         table_header = QFrame()
#         table_header.setStyleSheet("background-color: transparent; border-bottom: 1px solid #e5e7eb;")
#         header_layout = QHBoxLayout(table_header)
#         header_layout.setContentsMargins(20, 15, 20, 15)
        
#         table_title = QLabel("📋 Liste des contacts")
#         table_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #1e293b;")
        
#         self.select_info_label = QLabel("💡 Sélection multiple: Ctrl+clic ou Shift+clic")
#         self.select_info_label.setStyleSheet("font-size: 11px; color: #94a3b8;")
        
#         header_layout.addWidget(table_title)
#         header_layout.addStretch()
#         header_layout.addWidget(self.select_info_label)
        
#         table_layout.addWidget(table_header)
        
#         # Tableau
#         self.table = QTableWidget()
#         self.table.setColumnCount(8)
#         self.table.setHorizontalHeaderLabels([
#             "ID", "CONTACT", "TÉLÉPHONE", "EMAIL", "TYPE", "STATUT", "DATE", "ACTIONS"
#         ])
        
#         # Configuration
#         self.table.setSelectionBehavior(QTableWidget.SelectRows)
#         self.table.setSelectionMode(QTableWidget.ExtendedSelection)
#         self.table.setAlternatingRowColors(True)
#         self.table.setShowGrid(False)
#         self.table.verticalHeader().setVisible(False)
#         self.table.setSortingEnabled(True)
#         self.table.setContextMenuPolicy(Qt.CustomContextMenu)
#         self.table.customContextMenuRequested.connect(self.show_context_menu)
        
#         # Style du tableau
#         self.table.setStyleSheet("""
#             QTableWidget {
#                 background-color: white;
#                 border: none;
#                 gridline-color: transparent;
#                 outline: none;
#             }
#             QTableWidget::item {
#                 padding: 14px 12px;
#                 border-bottom: 1px solid #f1f5f9;
#                 font-size: 13px;
#             }
#             QTableWidget::item:selected {
#                 background-color: #eff6ff;
#                 color: #1e293b;
#             }
#             QTableWidget::item:hover {
#                 background-color: #f8fafc;
#             }
#             QHeaderView::section {
#                 background-color: #f8fafc;
#                 padding: 14px 12px;
#                 border: none;
#                 border-bottom: 2px solid #e2e8f0;
#                 font-weight: 700;
#                 font-size: 12px;
#                 color: #475569;
#                 text-transform: uppercase;
#                 letter-spacing: 0.3px;
#             }
#         """)
        
#         # Largeurs des colonnes
#         self.table.setColumnWidth(0, 60)   # ID
#         self.table.setColumnWidth(1, 240)  # Contact (avec avatar)
#         self.table.setColumnWidth(2, 150)  # Téléphone
#         self.table.setColumnWidth(3, 260)  # Email
#         self.table.setColumnWidth(4, 110)  # Type
#         self.table.setColumnWidth(5, 100)  # Statut
#         self.table.setColumnWidth(6, 110)  # Date
#         self.table.setColumnWidth(7, 140)  # Actions (plus large pour 4 boutons)
        
#         # Connecter les signaux
#         self.table.itemSelectionChanged.connect(self.on_selection_changed)
#         self.table.itemDoubleClicked.connect(self.on_item_double_clicked)
        
#         self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
#         self.table.horizontalHeader().setStretchLastSection(False)
#         self.table.setMinimumHeight(450)
        
#         table_layout.addWidget(self.table)
        
#         # Pied du tableau
#         table_footer = QFrame()
#         table_footer.setStyleSheet("background-color: transparent; border-top: 1px solid #e5e7eb;")
#         footer_layout = QHBoxLayout(table_footer)
#         footer_layout.setContentsMargins(20, 10, 20, 10)
        
#         self.total_rows_label = QLabel("Affichage de 0 contact")
#         self.total_rows_label.setStyleSheet("color: #64748b; font-size: 12px;")
        
#         footer_layout.addWidget(self.total_rows_label)
#         footer_layout.addStretch()
        
#         table_layout.addWidget(table_footer)
        
#         self.container_layout.addWidget(table_container)
    
#     def _create_contact_avatar(self, contact):
#         """Crée un avatar circulaire avec les initiales"""
#         widget = QWidget()
#         layout = QHBoxLayout(widget)
#         layout.setContentsMargins(0, 0, 0, 0)
        
#         # Initiales
#         initials = ""
#         if contact.prenom:
#             initials += contact.prenom[0].upper()
#         if contact.nom:
#             initials += contact.nom[0].upper()
#         initials = initials or "?"
        
#         # Couleur basée sur l'ID
#         colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"]
#         color = colors[contact.id % len(colors)] if contact.id else colors[0]
        
#         label = QLabel(initials)
#         label.setFixedSize(36, 36)
#         label.setAlignment(Qt.AlignCenter)
#         label.setStyleSheet(f"""
#             background-color: {color};
#             color: white;
#             border-radius: 18px;
#             font-weight: bold;
#             font-size: 14px;
#         """)
        
#         layout.addWidget(label)
#         return widget
    
#     def _create_compact_action_buttons(self, contact):
#         """Crée des boutons d'action compacts avec note rapide"""
#         widget = QWidget()
        
#         layout = QHBoxLayout(widget)
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.setSpacing(3)
        
#         # Bouton VOIR
#         view_btn = QPushButton("👁️")
#         view_btn.setFixedSize(30, 30)
#         view_btn.setCursor(Qt.PointingHandCursor)
#         view_btn.setToolTip("Voir les détails")
#         view_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: #f1f5f9;
#                 color: #475569;
#                 border-radius: 6px;
#                 font-size: 14px;
#                 padding: 0px;
#             }
#             QPushButton:hover {
#                 background-color: #8b5cf6;
#                 color: white;
#             }
#         """)
#         view_btn.clicked.connect(lambda: self.view_contact(contact))
        
#         # Bouton MODIFIER
#         edit_btn = QPushButton("✏️")
#         edit_btn.setFixedSize(30, 30)
#         edit_btn.setCursor(Qt.PointingHandCursor)
#         edit_btn.setToolTip("Modifier le contact")
#         edit_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: #f1f5f9;
#                 color: #475569;
#                 border-radius: 6px;
#                 font-size: 14px;
#                 padding: 0px;
#             }
#             QPushButton:hover {
#                 background-color: #3b82f6;
#                 color: white;
#             }
#         """)
#         edit_btn.clicked.connect(lambda: self.edit_contact(contact))
        
#         # Bouton NOTE RAPIDE
#         note_btn = QPushButton("📝")
#         note_btn.setFixedSize(30, 30)
#         note_btn.setCursor(Qt.PointingHandCursor)
#         note_btn.setToolTip("Ajouter une note rapide")
#         note_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: #f1f5f9;
#                 color: #475569;
#                 border-radius: 6px;
#                 font-size: 14px;
#                 padding: 0px;
#             }
#             QPushButton:hover {
#                 background-color: #f59e0b;
#                 color: white;
#             }
#         """)
#         note_btn.clicked.connect(lambda: self.add_quick_note(contact))
        
#         # Bouton SUPPRIMER
#         delete_btn = QPushButton("🗑️")
#         delete_btn.setFixedSize(30, 30)
#         delete_btn.setCursor(Qt.PointingHandCursor)
#         delete_btn.setToolTip("Supprimer le contact")
#         delete_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: #f1f5f9;
#                 color: #475569;
#                 border-radius: 6px;
#                 font-size: 14px;
#                 padding: 0px;
#             }
#             QPushButton:hover {
#                 background-color: #ef4444;
#                 color: white;
#             }
#         """)
#         delete_btn.clicked.connect(lambda: self.delete_contact(contact))
        
#         layout.addWidget(view_btn)
#         layout.addWidget(edit_btn)
#         layout.addWidget(note_btn)
#         layout.addWidget(delete_btn)
#         layout.setAlignment(Qt.AlignCenter)
        
#         widget.setLayout(layout)
#         return widget
    
#     def _create_status_bar(self):
#         status_frame = QFrame()
#         status_frame.setStyleSheet("""
#             QFrame {
#                 background-color: #f8fafc;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 12px;
#             }
#         """)
        
#         status_layout = QHBoxLayout(status_frame)
#         status_layout.setContentsMargins(20, 12, 20, 12)
        
#         self.status_label = QLabel("✅ Prêt")
#         self.status_label.setStyleSheet("color: #10b981; font-size: 13px; font-weight: 500;")
        
#         self.info_label = QLabel("")
#         self.info_label.setStyleSheet("color: #64748b; font-size: 12px;")
        
#         self.last_update_label = QLabel("")
#         self.last_update_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
        
#         status_layout.addWidget(self.status_label)
#         status_layout.addWidget(self.info_label)
#         status_layout.addStretch()
#         status_layout.addWidget(self.last_update_label)
        
#         self.container_layout.addWidget(status_frame)
    
#     # ==================== RACCOURCIS CLAVIER ====================
    
#     def setup_shortcuts(self):
#         new_shortcut = QAction(self)
#         new_shortcut.setShortcut("Ctrl+N")
#         new_shortcut.triggered.connect(self.on_add_contact)
#         self.addAction(new_shortcut)
        
#         edit_shortcut = QAction(self)
#         edit_shortcut.setShortcut("Ctrl+E")
#         edit_shortcut.triggered.connect(self.on_edit_contact)
#         self.addAction(edit_shortcut)
        
#         delete_shortcut = QAction(self)
#         delete_shortcut.setShortcut("Delete")
#         delete_shortcut.triggered.connect(self.on_delete_contact)
#         self.addAction(delete_shortcut)
        
#         refresh_shortcut = QAction(self)
#         refresh_shortcut.setShortcut("Ctrl+R")
#         refresh_shortcut.triggered.connect(self.load_contacts)
#         self.addAction(refresh_shortcut)
        
#         search_shortcut = QAction(self)
#         search_shortcut.setShortcut("Ctrl+F")
#         search_shortcut.triggered.connect(lambda: self.search_input.setFocus())
#         self.addAction(search_shortcut)
    
#     def setup_advanced_shortcuts(self):
#         """Ajoute des raccourcis clavier avancés"""
#         # Ctrl+D pour dupliquer
#         duplicate_shortcut = QAction(self)
#         duplicate_shortcut.setShortcut("Ctrl+D")
#         duplicate_shortcut.triggered.connect(self.duplicate_contact)
#         self.addAction(duplicate_shortcut)
        
#         # Ctrl+Shift+I pour importer
#         import_shortcut = QAction(self)
#         import_shortcut.setShortcut("Ctrl+Shift+I")
#         import_shortcut.triggered.connect(self.import_contacts)
#         self.addAction(import_shortcut)
        
#         # Ctrl+T pour basculer le thème
#         theme_shortcut = QAction(self)
#         theme_shortcut.setShortcut("Ctrl+T")
#         theme_shortcut.triggered.connect(self.toggle_theme)
#         self.addAction(theme_shortcut)
        
#         # F2 pour renommer/éditer
#         edit_shortcut = QAction(self)
#         edit_shortcut.setShortcut("F2")
#         edit_shortcut.triggered.connect(self.on_edit_contact)
#         self.addAction(edit_shortcut)
    
#     # ==================== GESTION DES CONTACTS ====================
    
#     def on_contacts_loaded(self, contacts):
#         """Callback quand les contacts sont chargés"""
#         self.all_contacts = contacts
#         self.filtered_contacts = contacts.copy()
        
#         self.display_contacts()
#         self.update_statistics()
#         self.update_last_update_time()
        
#         count = len(contacts)
#         self.counter_label.setText(f"{count} contact(s)")
#         self.total_rows_label.setText(f"Affichage de {count} contact(s)")
#         self.set_status(f"{count} contact(s) chargé(s) avec succès", "success")
#         self.info_label.setText(f"Total: {count} contacts")
#         logger.info(f"Contacts chargés: {count}")
    
#     def on_contacts_error(self, error):
#         """Callback en cas d'erreur de chargement"""
#         QMessageBox.warning(self, "Erreur", f"Erreur de chargement des contacts: {error}")

#     def load_contacts(self):
#         try:
#             self.set_status("Chargement des contacts...", "info")
#             self.all_contacts = self.controller.contacts.get_all_contacts()
#             self.filtered_contacts = self.all_contacts.copy()
#             self.display_contacts()
#             self.update_statistics()
#             self.update_last_update_time()
            
#             count = len(self.all_contacts)
#             self.set_status(f"{count} contact(s) chargé(s) avec succès", "success")
#             self.info_label.setText(f"Total: {count} contacts")
#             logger.info(f"Contacts chargés: {count}")
            
#         except Exception as e:
#             self.set_status(f"Erreur: {str(e)}", "error")
#             logger.error(f"Erreur chargement contacts: {e}")
    
#     def display_contacts(self):
#         """Affiche les contacts avec avatars et boutons compacts"""
#         self.table.setRowCount(0)
#         self.counter_label.setText(f"{len(self.filtered_contacts)} contact(s)")
#         self.total_rows_label.setText(f"Affichage de {len(self.filtered_contacts)} contact(s)")
        
#         for row, contact in enumerate(self.filtered_contacts):
#             self.table.insertRow(row)
            
#             # ID
#             id_item = QTableWidgetItem(str(contact.id))
#             id_item.setTextAlignment(Qt.AlignCenter)
#             id_item.setFont(QFont("Segoe UI", 10))
#             self.table.setItem(row, 0, id_item)
            
#             # Nom complet avec avatar
#             name_widget = QWidget()
#             name_layout = QHBoxLayout(name_widget)
#             name_layout.setContentsMargins(0, 0, 0, 0)
#             name_layout.setSpacing(8)
            
#             avatar = self._create_contact_avatar(contact)
#             name_layout.addWidget(avatar)
            
#             name = f"{contact.nom or ''} {contact.prenom or ''}".strip()
#             name_label = QLabel(name or "—")
#             name_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
#             name_label.setStyleSheet("color: #1e293b;")
#             name_layout.addWidget(name_label)
#             name_layout.addStretch()
            
#             self.table.setCellWidget(row, 1, name_widget)
            
#             # Téléphone
#             phone_item = QTableWidgetItem(contact.telephone or "—")
#             phone_item.setFont(QFont("Segoe UI", 10))
#             self.table.setItem(row, 2, phone_item)
            
#             # Email
#             email_item = QTableWidgetItem(contact.email or "—")
#             email_item.setFont(QFont("Segoe UI", 10))
#             self.table.setItem(row, 3, email_item)
            
#             # Type
#             type_item = QTableWidgetItem(contact.type_client or "—")
#             type_item.setForeground(self._get_type_color(contact.type_client))
#             type_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
#             type_item.setTextAlignment(Qt.AlignCenter)
#             self.table.setItem(row, 4, type_item)
            
#             # Statut
#             status = contact.vip_status or "Actif"
#             status_item = QTableWidgetItem(status)
#             status_item.setForeground(self._get_status_color(status))
#             status_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
#             status_item.setTextAlignment(Qt.AlignCenter)
#             self.table.setItem(row, 5, status_item)
            
#             # Date création
#             date_str = contact.created_at.strftime("%d/%m/%Y") if contact.created_at else "—"
#             date_item = QTableWidgetItem(date_str)
#             date_item.setTextAlignment(Qt.AlignCenter)
#             date_item.setFont(QFont("Segoe UI", 10))
#             self.table.setItem(row, 6, date_item)
            
#             # Actions avec boutons compacts
#             actions_widget = self._create_compact_action_buttons(contact)
#             self.table.setCellWidget(row, 7, actions_widget)
            
#             self.table.setRowHeight(row, 56)
    
#     # ==================== FILTRES ET RECHERCHE ====================
    
#     def on_search(self):
#         self.apply_filters()
    
#     def on_filter_changed(self):
#         self.apply_filters()
    
#     def apply_filters(self):
#         search_text = self.search_input.text().strip().lower()
#         type_filter = self.type_filter.currentText()
#         status_filter = self.status_filter.currentText()
#         date_filter = self.date_filter.currentText()
#         tag_filter = self.tag_filter.currentText()
#         birthday_filter = self.birthday_filter.currentText()
        
#         filtered = self.all_contacts.copy()
        
#         if search_text:
#             filtered = [c for c in filtered if self._matches_search(c, search_text)]
        
#         if type_filter != "Tous les types":
#             filtered = [c for c in filtered if (c.type_client or "") == type_filter]
        
#         if status_filter != "Tous les statuts":
#             filtered = [c for c in filtered if (c.vip_status or "Actif") == status_filter]
        
#         if date_filter != "Toutes les dates":
#             filtered = self._apply_date_filter(filtered, date_filter)
        
#         if tag_filter != "Tous les tags":
#             # Simuler un filtre par tag (à adapter selon votre modèle)
#             filtered = [c for c in filtered if hasattr(c, 'tag') and c.tag == tag_filter]
        
#         if birthday_filter != "Tous":
#             # Simuler un filtre d'anniversaire
#             filtered = [c for c in filtered if hasattr(c, 'birthday') and c.birthday]
        
#         self.filtered_contacts = filtered
#         self.display_contacts()
#         self.update_statistics()
#         self.set_status(f"{len(filtered)} contact(s) trouvé(s)", "info")
    
#     def _matches_search(self, contact, search_text):
#         return any([
#             search_text in (contact.nom or "").lower(),
#             search_text in (contact.prenom or "").lower(),
#             search_text in (contact.telephone or "").lower(),
#             search_text in (contact.email or "").lower(),
#             search_text in (contact.type_client or "").lower()
#         ])
    
#     def _apply_date_filter(self, contacts, date_filter):
#         from datetime import datetime, timedelta
        
#         now = datetime.now()
#         today = now.date()
        
#         if date_filter == "Aujourd'hui":
#             return [c for c in contacts if c.created_at and c.created_at.date() == today]
#         elif date_filter == "Cette semaine":
#             week_start = today - timedelta(days=today.weekday())
#             return [c for c in contacts if c.created_at and c.created_at.date() >= week_start]
#         elif date_filter == "Ce mois":
#             return [c for c in contacts if c.created_at and c.created_at.month == now.month and c.created_at.year == now.year]
#         elif date_filter == "Cette année":
#             return [c for c in contacts if c.created_at and c.created_at.year == now.year]
        
#         return contacts
    
#     def reset_filters(self):
#         self.search_input.clear()
#         self.type_filter.setCurrentIndex(0)
#         self.status_filter.setCurrentIndex(0)
#         self.date_filter.setCurrentIndex(0)
#         self.tag_filter.setCurrentIndex(0)
#         self.birthday_filter.setCurrentIndex(0)
#         self.filtered_contacts = self.all_contacts.copy()
#         self.display_contacts()
#         self.update_statistics()
#         self.set_status("Filtres réinitialisés", "info")
    
#     # ==================== STATISTIQUES ====================
    
#     def update_statistics(self):
#         total = len(self.filtered_contacts)
#         assures = len([c for c in self.filtered_contacts if (c.type_client or "") == "Assuré"])
#         prospects = len([c for c in self.filtered_contacts if (c.type_client or "") == "Prospect"])
#         actifs = len([c for c in self.filtered_contacts if (c.vip_status or "Actif") == "Actif"])
        
#         self._update_stat_card("total", str(total))
#         self._update_stat_card("assures", str(assures))
#         self._update_stat_card("prospects", str(prospects))
#         self._update_stat_card("actifs", str(actifs))
    
#     def _update_stat_card(self, key, value):
#         card = self.stats_cards.get(key)
#         if card:
#             value_label = card.findChild(QLabel, f"stat_{key}")
#             if value_label:
#                 value_label.setText(value)
    
#     # ==================== SÉLECTION ====================
    
#     def on_selection_changed(self):
#         selected_rows = set()
#         for item in self.table.selectedItems():
#             selected_rows.add(item.row())
        
#         self.selected_contacts = []
#         for row in selected_rows:
#             if row < len(self.filtered_contacts):
#                 self.selected_contacts.append(self.filtered_contacts[row])
        
#         count = len(self.selected_contacts)
#         self.edit_btn.setEnabled(count == 1)
#         self.delete_btn.setEnabled(count > 0)
#         self.duplicate_btn.setEnabled(count == 1)
        
#         if count > 0:
#             self.selection_label.setText(f"✓ {count} contact(s) sélectionné(s)")
#         else:
#             self.selection_label.setText("")
        
#         if count == 1:
#             self.contact_selected.emit(self.selected_contacts[0])
    
#     def on_item_double_clicked(self, item):
#         row = item.row()
#         if row < len(self.filtered_contacts):
#             self.view_contact(self.filtered_contacts[row])
    
#     # ==================== CRUD ====================
    
#     def on_add_contact(self):
#         dialog = ContactForm(self)
#         if dialog.exec_():
#             data = dialog.get_data()
#             result = self.controller.contacts.create_contact(data)
#             if result:
#                 self.load_contacts()
#                 self.set_status("Contact ajouté avec succès", "success")
    
#     def on_edit_contact(self):
#         if len(self.selected_contacts) == 1:
#             self.edit_contact(self.selected_contacts[0])
    
#     def edit_contact(self, contact):
#         fresh_contact = self.controller.contacts.get_contact_by_id(contact.id)
#         if fresh_contact:
#             dialog = ContactForm(self, fresh_contact)
#             if dialog.exec_():
#                 self.load_contacts()
#                 self.contact_updated.emit()
#                 self.set_status("Contact modifié avec succès", "success")
    
#     def view_contact(self, contact):
#         from addons.Automobiles.views.contact_detail_view import ContactDetailView
#         dialog = ContactDetailView(self.controller, contact, self)
#         dialog.contact_updated.connect(self.load_contacts)
#         dialog.exec_()
    
#     def delete_contact(self, contact):
#         name = f"{contact.nom} {contact.prenom or ''}".strip()
        
#         msg = QMessageBox(self)
#         msg.setIcon(QMessageBox.Question)
#         msg.setWindowTitle("Confirmation")
#         msg.setText(f"Supprimer le contact '{name}' ?")
#         msg.setInformativeText("Cette action est irréversible.")
#         msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
#         msg.setDefaultButton(QMessageBox.No)
        
#         if msg.exec() == QMessageBox.Yes:
#             if self.controller.contacts.delete_contact(contact.id):
#                 self.load_contacts()
#                 self.set_status("Contact supprimé avec succès", "success")
    
#     def on_delete_contact(self):
#         if not self.selected_contacts:
#             return
        
#         count = len(self.selected_contacts)
#         msg = QMessageBox(self)
#         msg.setIcon(QMessageBox.Question)
#         msg.setWindowTitle("Confirmation")
        
#         if count == 1:
#             contact = self.selected_contacts[0]
#             name = f"{contact.nom} {contact.prenom or ''}".strip()
#             msg.setText(f"Supprimer le contact '{name}' ?")
#         else:
#             msg.setText(f"Supprimer {count} contacts ?")
        
#         msg.setInformativeText("Cette action est irréversible.")
#         msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
#         msg.setDefaultButton(QMessageBox.No)
        
#         if msg.exec() == QMessageBox.Yes:
#             success_count = 0
#             for contact in self.selected_contacts:
#                 if self.controller.contacts.delete_contact(contact.id):
#                     success_count += 1
            
#             self.load_contacts()
#             self.set_status(f"{success_count} contact(s) supprimé(s)", "success")
    
#     def duplicate_contact(self):
#         """Duplique le contact sélectionné"""
#         if len(self.selected_contacts) == 1:
#             contact = self.selected_contacts[0]
            
#             # Créer une copie avec "(Copie)" dans le nom
#             new_data = {
#                 'nom': contact.nom + " (Copie)" if contact.nom else "Copie",
#                 'prenom': contact.prenom,
#                 'telephone': contact.telephone,
#                 'email': contact.email,
#                 'type_client': contact.type_client,
#                 'vip_status': contact.vip_status
#             }
            
#             result = self.controller.contacts.create_contact(new_data)
#             if result:
#                 self.load_contacts()
#                 self.set_status("Contact dupliqué avec succès", "success")
    
#     def import_contacts(self):
#         """Importe des contacts depuis CSV/Excel"""
#         path, _ = QFileDialog.getOpenFileName(
#             self, "Importer des contacts",
#             "", "CSV Files (*.csv);;Excel Files (*.xlsx *.xls)"
#         )
        
#         if path:
#             try:
#                 # À adapter selon votre contrôleur
#                 count = self.controller.contacts.import_from_file(path)
#                 self.load_contacts()
#                 self.set_status(f"{count} contact(s) importé(s) avec succès", "success")
#             except Exception as e:
#                 self.set_status(f"Erreur d'import: {str(e)}", "error")
    
#     def add_quick_note(self, contact):
#         """Ajoute une note rapide à un contact"""
#         dialog = QDialog(self)
#         dialog.setWindowTitle(f"📝 Note rapide - {contact.nom}")
#         dialog.resize(500, 300)
        
#         layout = QVBoxLayout(dialog)
#         layout.setContentsMargins(20, 20, 20, 20)
#         layout.setSpacing(15)
        
#         info_label = QLabel(f"Contact: {contact.nom} {contact.prenom or ''}")
#         info_label.setStyleSheet("font-weight: 600; color: #1e293b;")
#         layout.addWidget(info_label)
        
#         note_input = QTextEdit()
#         note_input.setPlaceholderText("Écrivez votre note ici...")
#         note_input.setStyleSheet("""
#             QTextEdit {
#                 border: 1px solid #e2e8f0;
#                 border-radius: 10px;
#                 padding: 10px;
#                 font-size: 13px;
#             }
#             QTextEdit:focus {
#                 border-color: #3b82f6;
#             }
#         """)
#         layout.addWidget(note_input)
        
#         btn_layout = QHBoxLayout()
#         btn_layout.setSpacing(10)
        
#         cancel_btn = QPushButton("Annuler")
#         cancel_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: #f1f5f9;
#                 color: #475569;
#                 padding: 10px 20px;
#                 border-radius: 8px;
#             }
#             QPushButton:hover {
#                 background-color: #e2e8f0;
#             }
#         """)
#         cancel_btn.clicked.connect(dialog.reject)
        
#         save_btn = QPushButton("💾 Enregistrer")
#         save_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: #3b82f6;
#                 color: white;
#                 padding: 10px 20px;
#                 border-radius: 8px;
#                 font-weight: 600;
#             }
#             QPushButton:hover {
#                 background-color: #2563eb;
#             }
#         """)
        
#         def on_save():
#             note = note_input.toPlainText().strip()
#             if note:
#                 # À adapter selon votre modèle
#                 self.controller.contacts.add_note(contact.id, note)
#                 self.set_status("Note ajoutée avec succès", "success")
#                 dialog.accept()
#             else:
#                 QMessageBox.warning(dialog, "Attention", "Veuillez écrire une note avant d'enregistrer.")
        
#         save_btn.clicked.connect(on_save)
        
#         btn_layout.addStretch()
#         btn_layout.addWidget(cancel_btn)
#         btn_layout.addWidget(save_btn)
#         layout.addLayout(btn_layout)
        
#         dialog.exec_()
    
#     # ==================== EXPORTS ====================
    
#     def export_to_csv(self):
#         path, _ = QFileDialog.getSaveFileName(
#             self, "Exporter les contacts", 
#             f"contacts_{datetime.now().strftime('%Y%m%d')}.csv", 
#             "CSV Files (*.csv)"
#         )
        
#         if path:
#             try:
#                 import csv
#                 with open(path, 'w', newline='', encoding='utf-8-sig') as f:
#                     writer = csv.writer(f)
#                     writer.writerow(["ID", "Nom", "Prénom", "Téléphone", "Email", "Type", "Statut", "Date création"])
                    
#                     for c in self.filtered_contacts:
#                         writer.writerow([
#                             c.id, c.nom or "", c.prenom or "", c.telephone or "",
#                             c.email or "", c.type_client or "", c.vip_status or "Actif",
#                             c.created_at.strftime("%d/%m/%Y") if c.created_at else ""
#                         ])
                
#                 self.set_status(f"Export CSV réussi: {os.path.basename(path)}", "success")
#                 logger.info(f"Export CSV: {len(self.filtered_contacts)} contacts")
                
#             except Exception as e:
#                 self.set_status(f"Erreur export CSV: {str(e)}", "error")
    
#     def export_to_pdf(self):
#         path, _ = QFileDialog.getSaveFileName(
#             self, "Exporter les contacts en PDF",
#             f"contacts_{datetime.now().strftime('%Y%m%d')}.pdf",
#             "PDF Files (*.pdf)"
#         )
        
#         if path:
#             try:
#                 contacts_data = []
#                 for c in self.filtered_contacts:
#                     contacts_data.append({
#                         'id': c.id, 'nom': c.nom, 'prenom': c.prenom,
#                         'telephone': c.telephone, 'email': c.email,
#                         'type': c.type_client, 'statut': c.vip_status,
#                         'date_creation': c.created_at
#                     })
                
#                 stats = {
#                     'total': len(contacts_data),
#                     'assures': len([c for c in contacts_data if c['type'] == "Assuré"]),
#                     'prospects': len([c for c in contacts_data if c['type'] == "Prospect"]),
#                     'actifs': len([c for c in contacts_data if c['statut'] == "Actif"])
#                 }
                
#                 generate_contact_pdf(path, contacts_data, stats)
#                 self.set_status(f"Export PDF réussi: {os.path.basename(path)}", "success")
#                 logger.info(f"Export PDF: {len(contacts_data)} contacts")
                
#             except Exception as e:
#                 self.set_status(f"Erreur export PDF: {str(e)}", "error")
    
#     # ==================== AUDIT ====================
    
#     def show_audit_logs(self):
#         try:
#             logs = self.controller.contacts.get_audit_logs()
            
#             if not logs:
#                 QMessageBox.information(self, "Audit", "Aucun historique d'audit disponible")
#                 return
            
#             dialog = QDialog(self)
#             dialog.setWindowTitle("📜 Journal d'audit")
#             dialog.resize(1100, 700)
#             dialog.setStyleSheet("background-color: white;")
            
#             layout = QVBoxLayout(dialog)
#             layout.setContentsMargins(25, 25, 25, 25)
#             layout.setSpacing(20)
            
#             title = QLabel("📜 Historique des actions")
#             title.setStyleSheet("font-size: 20px; font-weight: 700; color: #1e293b;")
#             layout.addWidget(title)
            
#             table = QTableWidget()
#             table.setColumnCount(4)
#             table.setHorizontalHeaderLabels(["Date", "Action", "Utilisateur", "Détails"])
#             table.setAlternatingRowColors(True)
#             table.setSelectionBehavior(QTableWidget.SelectRows)
#             table.setShowGrid(False)
#             table.verticalHeader().setVisible(False)
            
#             table.setStyleSheet("""
#                 QTableWidget { border: 1px solid #e5e7eb; border-radius: 10px; }
#                 QHeaderView::section { background-color: #f9fafb; padding: 12px; font-weight: 600; }
#                 QTableWidget::item { padding: 12px; }
#             """)
            
#             table.setRowCount(len(logs))
#             for i, log in enumerate(logs):
#                 date_str = log.created_at.strftime("%d/%m/%Y %H:%M:%S") if log.created_at else "—"
#                 table.setItem(i, 0, QTableWidgetItem(date_str))
#                 table.setItem(i, 1, QTableWidgetItem(log.action or "—"))
#                 table.setItem(i, 2, QTableWidgetItem(f"ID: {log.user_id or '?'}"))
#                 table.setItem(i, 3, QTableWidgetItem(log.details or "—"))
            
#             table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
#             table.setColumnWidth(0, 180)
#             table.setColumnWidth(1, 140)
#             table.setColumnWidth(2, 100)
            
#             layout.addWidget(table)
            
#             close_btn = QPushButton("Fermer")
#             close_btn.setMinimumHeight(45)
#             close_btn.setStyleSheet("""
#                 QPushButton {
#                     background-color: #3b82f6;
#                     color: white;
#                     padding: 12px 25px;
#                     font-weight: 600;
#                     border-radius: 10px;
#                 }
#                 QPushButton:hover { background-color: #2563eb; }
#             """)
#             close_btn.clicked.connect(dialog.accept)
#             layout.addWidget(close_btn)
            
#             dialog.exec_()
            
#         except Exception as e:
#             self.set_status(f"Erreur: {str(e)}", "error")
    
#     # ==================== MENU CONTEXTUEL ====================
    
#     def show_context_menu(self, position):
#         menu = QMenu()
        
#         item = self.table.itemAt(position)
#         if not item:
#             return
        
#         row = item.row()
#         if row >= len(self.filtered_contacts):
#             return
        
#         contact = self.filtered_contacts[row]
        
#         view_action = QAction("👁️ Voir les détails", self)
#         view_action.triggered.connect(lambda: self.view_contact(contact))
        
#         edit_action = QAction("✏️ Modifier", self)
#         edit_action.triggered.connect(lambda: self.edit_contact(contact))
        
#         note_action = QAction("📝 Ajouter une note", self)
#         note_action.triggered.connect(lambda: self.add_quick_note(contact))
        
#         duplicate_action = QAction("📋 Dupliquer", self)
#         duplicate_action.triggered.connect(lambda: self.duplicate_single_contact(contact))
        
#         delete_action = QAction("🗑️ Supprimer", self)
#         delete_action.triggered.connect(lambda: self.delete_contact(contact))
        
#         menu.addAction(view_action)
#         menu.addAction(edit_action)
#         menu.addSeparator()
#         menu.addAction(note_action)
#         menu.addAction(duplicate_action)
#         menu.addSeparator()
#         menu.addAction(delete_action)
        
#         menu.exec_(self.table.viewport().mapToGlobal(position))
    
#     def duplicate_single_contact(self, contact):
#         """Duplique un contact spécifique"""
#         new_data = {
#             'nom': contact.nom + " (Copie)" if contact.nom else "Copie",
#             'prenom': contact.prenom,
#             'telephone': contact.telephone,
#             'email': contact.email,
#             'type_client': contact.type_client,
#             'vip_status': contact.vip_status
#         }
        
#         result = self.controller.contacts.create_contact(new_data)
#         if result:
#             self.load_contacts()
#             self.set_status("Contact dupliqué avec succès", "success")
    
#     # ==================== THÈME ====================
    
#     def toggle_theme(self):
#         """Bascule entre thème clair et sombre"""
#         self.dark_mode = not self.dark_mode
        
#         if self.dark_mode:
#             self._apply_dark_theme()
#             self.theme_btn.setText("☀️")
#             self.theme_btn.setToolTip("Basculer vers le thème clair (Ctrl+T)")
#         else:
#             self._apply_global_style()
#             self.theme_btn.setText("🌙")
#             self.theme_btn.setToolTip("Basculer vers le thème sombre (Ctrl+T)")
    
#     def _apply_dark_theme(self):
#         """Applique le thème sombre"""
#         self.setStyleSheet("""
#             QWidget {
#                 background-color: #1a1a2e;
#                 color: #e2e8f0;
#             }
#             QFrame {
#                 background-color: #16213e;
#                 border-radius: 12px;
#             }
#             QScrollArea {
#                 background-color: #1a1a2e;
#             }
#             QLineEdit, QComboBox {
#                 background-color: #0f3460;
#                 color: #e2e8f0;
#                 border: 1px solid #1a1a2e;
#             }
#             QLineEdit:focus, QComboBox:focus {
#                 border-color: #3b82f6;
#             }
#             QTableWidget {
#                 background-color: #16213e;
#                 color: #e2e8f0;
#             }
#             QTableWidget::item {
#                 border-bottom: 1px solid #1a1a2e;
#             }
#             QTableWidget::item:selected {
#                 background-color: #1a3a6e;
#             }
#             QHeaderView::section {
#                 background-color: #0f3460;
#                 color: #94a3b8;
#                 border-bottom: 2px solid #1a1a2e;
#             }
#             QPushButton:hover {
#                 background-color: #1a3a6e;
#             }
#             QLabel {
#                 color: #e2e8f0;
#             }
#         """)
    
#     # ==================== UTILITAIRES ====================
    
#     def _get_type_color(self, contact_type):
#         colors = {
#             "Assuré": QColor("#10b981"),
#             "Prospect": QColor("#f59e0b"),
#             "Partenaire": QColor("#8b5cf6"),
#             "Fournisseur": QColor("#06b6d4")
#         }
#         return colors.get(contact_type, QColor("#64748b"))
    
#     def _get_status_color(self, status):
#         colors = {
#             "Actif": QColor("#10b981"),
#             "Inactif": QColor("#ef4444"),
#             "En attente": QColor("#f59e0b")
#         }
#         return colors.get(status, QColor("#64748b"))
    
#     def set_status(self, message, msg_type="info"):
#         icons = {"success": "✅", "error": "❌", "info": "ℹ️", "warning": "⚠️"}
#         colors = {"success": "#10b981", "error": "#ef4444", "info": "#3b82f6", "warning": "#f59e0b"}
        
#         self.status_label.setText(f"{icons.get(msg_type, 'ℹ️')} {message}")
#         self.status_label.setStyleSheet(f"color: {colors.get(msg_type, '#64748b')}; font-size: 13px; font-weight: 500;")
        
#         if msg_type != "error":
#             QTimer.singleShot(3000, lambda: self.status_label.setText("✅ Prêt"))
    
#     def update_last_update_time(self):
#         self.last_update_label.setText(f"Dernière mise à jour: {datetime.now().strftime('%H:%M:%S')}")
    
#     def apply_security_policy(self):
#         if hasattr(self.current_user, 'role'):
#             role = self.current_user.role
            
#             if not SecurityManager.has_permission(role, Permissions.CONTACT_ADD):
#                 self.add_btn.setVisible(False)
#             if not SecurityManager.has_permission(role, Permissions.CONTACT_EDIT):
#                 self.edit_btn.setVisible(False)
#             if not SecurityManager.has_permission(role, Permissions.CONTACT_DELETE):
#                 self.delete_btn.setVisible(False)
#             if not SecurityManager.has_permission(role, Permissions.AUDIT_VIEW):
#                 self.audit_btn.setVisible(False)
#             if not SecurityManager.has_permission(role, Permissions.EXPORT_PDF):
#                 self.export_pdf_btn.setVisible(False)
    
#     def refresh(self):
#         self.load_contacts()


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
        self.addAction(duplicate_shortcut)# contacts_view.py - Interface de gestion des contacts redesign
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
        
        # Filtres
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Tous", "Assuré", "Prospect", "Partenaire", "Fournisseur"])
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
        
        # Cartes de stats
        stats_data = [
            ("total", "👥", "Total", "#4299e1"),
            ("assures", "✅", "Assurés", "#48bb78"),
            ("prospects", "🎯", "Prospects", "#ed8936"),
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
        
        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "CONTACT", "TÉLÉPHONE", "EMAIL", "TYPE", "STATUT", "ACTIONS"
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
        
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 220)
        self.table.setColumnWidth(2, 140)
        self.table.setColumnWidth(3, 220)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 140)
        
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
    
    def _create_avatar(self, contact):
        """Crée un avatar avec initiales"""
        initials = ""
        if contact.prenom:
            initials += contact.prenom[0].upper()
        if contact.nom:
            initials += contact.nom[0].upper()
        initials = initials or "?"
        
        colors = ["#4299e1", "#48bb78", "#ed8936", "#fc8181", "#9f7aea", "#38b2ac"]
        color = colors[contact.id % len(colors)] if contact.id else colors[0]
        
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
    
    def _create_action_buttons(self, contact):
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
        
        # Voir
        btn_view = QPushButton("👁")
        btn_view.setToolTip("Voir les détails")
        btn_view.setStyleSheet(btn_style % "#ebf4ff")
        btn_view.clicked.connect(lambda: self.view_contact(contact))
        
        # Modifier
        btn_edit = QPushButton("✏️")
        btn_edit.setToolTip("Modifier")
        btn_edit.setStyleSheet(btn_style % "#fefcbf")
        btn_edit.clicked.connect(lambda: self.edit_contact(contact))
        
        # Note
        btn_note = QPushButton("📝")
        btn_note.setToolTip("Ajouter une note")
        btn_note.setStyleSheet(btn_style % "#c6f6d5")
        btn_note.clicked.connect(lambda: self.add_quick_note(contact))
        
        # Supprimer
        btn_delete = QPushButton("🗑")
        btn_delete.setToolTip("Supprimer")
        btn_delete.setStyleSheet(btn_style % "#fed7d7")
        btn_delete.clicked.connect(lambda: self.delete_contact(contact))
        
        layout.addWidget(btn_view)
        layout.addWidget(btn_edit)
        layout.addWidget(btn_note)
        layout.addWidget(btn_delete)
        
        return container
    
    # ============================================================
    # FONCTIONS MÉTIER
    # ============================================================
    
    def load_contacts(self):
        """Charge les contacts"""
        try:
            self.set_status("Chargement...", "info")
            self.all_contacts = self.controller.contacts.get_all_contacts()
            self.filtered_contacts = self.all_contacts.copy()
            self.display_contacts()
            self.update_statistics()
            self.update_last_update_time()
            
            count = len(self.all_contacts)
            self.set_status(f"{count} contact(s) chargé(s)", "success")
            
        except Exception as e:
            self.set_status(f"Erreur: {str(e)}", "error")
            logger.error(f"Erreur chargement contacts: {e}")
    
    def display_contacts(self):
        """Affiche les contacts"""
        self.table.setRowCount(0)
        count = len(self.filtered_contacts)
        self.total_rows_label.setText(f"{count} contact(s)")
        
        for row, contact in enumerate(self.filtered_contacts):
            self.table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(contact.id))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, id_item)
            
            # Contact (avatar + nom)
            contact_widget = QWidget()
            contact_layout = QHBoxLayout(contact_widget)
            contact_layout.setContentsMargins(0, 0, 0, 0)
            contact_layout.setSpacing(10)
            
            avatar = self._create_avatar(contact)
            contact_layout.addWidget(avatar)
            
            name = f"{contact.nom or ''} {contact.prenom or ''}".strip()
            name_label = QLabel(name or "—")
            name_label.setStyleSheet("font-weight: 600; font-size: 13px; color: #1a202c; background: transparent; border: none;")
            contact_layout.addWidget(name_label)
            contact_layout.addStretch()
            
            self.table.setCellWidget(row, 1, contact_widget)
            
            # Téléphone
            self.table.setItem(row, 2, QTableWidgetItem(contact.telephone or "—"))
            
            # Email
            self.table.setItem(row, 3, QTableWidgetItem(contact.email or "—"))
            
            # Type
            type_item = QTableWidgetItem(contact.type_client or "—")
            type_item.setTextAlignment(Qt.AlignCenter)
            type_item.setForeground(self._get_type_color(contact.type_client))
            self.table.setItem(row, 4, type_item)
            
            # Statut
            status = contact.vip_status or "Actif"
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setForeground(self._get_status_color(status))
            self.table.setItem(row, 5, status_item)
            
            # Actions
            actions = self._create_action_buttons(contact)
            self.table.setCellWidget(row, 6, actions)
            
            self.table.setRowHeight(row, 56)
    
    def update_statistics(self):
        """Met à jour les statistiques"""
        total = len(self.filtered_contacts)
        assures = len([c for c in self.filtered_contacts if (c.type_client or "") == "Assuré"])
        prospects = len([c for c in self.filtered_contacts if (c.type_client or "") == "Prospect"])
        actifs = len([c for c in self.filtered_contacts if (c.vip_status or "Actif") == "Actif"])
        
        self._update_stat_card("total", str(total))
        self._update_stat_card("assures", str(assures))
        self._update_stat_card("prospects", str(prospects))
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
    
    def apply_filters(self):
        """Applique les filtres"""
        search_text = self.search_input.text().strip().lower()
        type_filter = self.filter_combo.currentText()
        
        filtered = self.all_contacts.copy()
        
        if search_text:
            filtered = [c for c in filtered if self._matches_search(c, search_text)]
        
        if type_filter != "Tous":
            filtered = [c for c in filtered if (c.type_client or "") == type_filter]
        
        self.filtered_contacts = filtered
        self.display_contacts()
        self.update_statistics()
        self.set_status(f"{len(filtered)} contact(s) trouvé(s)", "info")
    
    def _matches_search(self, contact, search_text):
        """Vérifie si le contact correspond à la recherche"""
        return any([
            search_text in (contact.nom or "").lower(),
            search_text in (contact.prenom or "").lower(),
            search_text in (contact.telephone or "").lower(),
            search_text in (contact.email or "").lower()
        ])
    
    # ============================================================
    # CRUD
    # ============================================================
    
    def on_add_contact(self):
        """Ajoute un contact"""
        dialog = ContactForm(self)
        if dialog.exec_():
            data = dialog.get_data()
            result = self.controller.contacts.create_contact(data)
            if result:
                self.load_contacts()
                self.set_status("Contact ajouté", "success")
    
    def on_edit_contact(self):
        """Modifie un contact"""
        if len(self.selected_contacts) == 1:
            self.edit_contact(self.selected_contacts[0])
    
    def edit_contact(self, contact):
        """Modifie un contact"""
        fresh_contact = self.controller.contacts.get_contact_by_id(contact.id)
        if fresh_contact:
            dialog = ContactForm(self, fresh_contact)
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
                'vip_status': contact.vip_status
            }
            result = self.controller.contacts.create_contact(new_data)
            if result:
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
                self.controller.contacts.add_note(contact.id, note)
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
                    writer.writerow(["ID", "Nom", "Prénom", "Téléphone", "Email", "Type", "Statut"])
                    for c in self.filtered_contacts:
                        writer.writerow([
                            c.id, c.nom or "", c.prenom or "", c.telephone or "",
                            c.email or "", c.type_client or "", c.vip_status or "Actif"
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
                    'type': c.type_client, 'statut': c.vip_status
                } for c in self.filtered_contacts]
                
                stats = {
                    'total': len(contacts_data),
                    'assures': len([c for c in contacts_data if c['type'] == "Assuré"]),
                    'prospects': len([c for c in contacts_data if c['type'] == "Prospect"]),
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
            'vip_status': contact.vip_status
        }
        result = self.controller.contacts.create_contact(new_data)
        if result:
            self.load_contacts()
            self.set_status("Contact dupliqué", "success")
    
    # ============================================================
    # UTILITAIRES
    # ============================================================
    
    def _get_type_color(self, contact_type):
        """Couleur selon le type"""
        colors = {
            "Assuré": QColor("#48bb78"),
            "Prospect": QColor("#ed8936"),
            "Partenaire": QColor("#9f7aea"),
            "Fournisseur": QColor("#38b2ac")
        }
        return colors.get(contact_type, QColor("#718096"))
    
    def _get_status_color(self, status):
        """Couleur selon le statut"""
        colors = {
            "Actif": QColor("#48bb78"),
            "Inactif": QColor("#fc8181"),
            "En attente": QColor("#ed8936")
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
            # if not SecurityManager.has_permission(role, Permissions.EXPORT_PDF):
            #     self.btn_export_pdf.setVisible(False)
    
    def refresh(self):
        """Rafraîchit la vue"""
        self.load_contacts()
    
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