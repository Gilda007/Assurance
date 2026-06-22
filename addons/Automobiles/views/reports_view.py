# # addons/Automobiles/views/reports_view.py
# import os
# from datetime import datetime, timedelta
# from PySide6.QtWidgets import (
#     QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
#     QFrame, QComboBox, QDateEdit, QLineEdit, QTableWidget,
#     QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog,
#     QScrollArea, QTabWidget, QGridLayout, QGroupBox, QTextEdit,
#     QProgressBar, QSplitter, QCheckBox, QSpinBox
# )
# from PySide6.QtCore import Qt, QTimer, Signal, QDate, QDateTime
# from PySide6.QtGui import QFont, QColor, QBrush, QPixmap, QIcon, QPainter
# from PySide6.QtCharts import QChartView, QChart, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QLineSeries

# from core.logger import logger
# from core.workers.database_worker import async_query


# class ModernReportCard(QFrame):
#     """Carte moderne pour les statistiques des rapports"""
    
#     clicked = Signal(str)
    
#     def __init__(self, title, value, icon, color, subtitle=None, trend=None):
#         super().__init__()
#         self.setFixedHeight(120)
#         self.setCursor(Qt.PointingHandCursor)
#         self.setStyleSheet(f"""
#             QFrame {{
#                 background: white;
#                 border-radius: 16px;
#                 border: 1px solid #e2e8f0;
#             }}
#             QFrame:hover {{
#                 border-color: {color};
#                 background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
#                     stop:0 white, stop:1 {color}08);
#             }}
#         """)
        
#         layout = QHBoxLayout(self)
#         layout.setContentsMargins(20, 15, 20, 15)
#         layout.setSpacing(15)
        
#         # Icône
#         icon_container = QFrame()
#         icon_container.setFixedSize(50, 50)
#         icon_container.setStyleSheet(f"""
#             QFrame {{
#                 background: {color}15;
#                 border-radius: 14px;
#             }}
#         """)
#         icon_layout = QVBoxLayout(icon_container)
#         icon_layout.setAlignment(Qt.AlignCenter)
#         icon_label = QLabel(icon)
#         icon_label.setStyleSheet(f"font-size: 24px; background: transparent;")
#         icon_layout.addWidget(icon_label)
        
#         # Infos
#         info_layout = QVBoxLayout()
#         info_layout.setSpacing(5)
        
#         value_label = QLabel(str(value))
#         value_label.setStyleSheet(f"""
#             font-size: 28px;
#             font-weight: 800;
#             color: {color};
#         """)
#         value_label.setObjectName("value")
        
#         title_label = QLabel(title)
#         title_label.setStyleSheet("color: #64748b; font-size: 13px; font-weight: 500;")
        
#         info_layout.addWidget(value_label)
#         info_layout.addWidget(title_label)
        
#         if subtitle:
#             subtitle_label = QLabel(subtitle)
#             subtitle_label.setStyleSheet("color: #94a3b8; font-size: 10px;")
#             info_layout.addWidget(subtitle_label)
        
#         layout.addWidget(icon_container)
#         layout.addLayout(info_layout)
#         layout.addStretch()
        
#         if trend:
#             trend_label = QLabel(trend)
#             if trend.startswith('+'):
#                 trend_label.setStyleSheet("color: #10b981; font-size: 12px; font-weight: 600;")
#                 trend_label.setText(f"▲ {trend}")
#             elif trend.startswith('-'):
#                 trend_label.setStyleSheet("color: #ef4444; font-size: 12px; font-weight: 600;")
#                 trend_label.setText(f"▼ {trend}")
#             else:
#                 trend_label.setStyleSheet("color: #64748b; font-size: 12px;")
#             layout.addWidget(trend_label)
        
#         self.value_label = value_label
#         self.title = title
    
#     def update_value(self, value):
#         self.value_label.setText(str(value))


# class ReportView(QWidget):
#     """Vue principale des rapports - Version améliorée"""
    
#     def __init__(self, session, current_user):
#         super().__init__()
#         from addons.Automobiles.controllers.reports_controller import ReportsController
        
#         # Récupérer l'ID de l'utilisateur
#         if hasattr(current_user, 'id'):
#             user_id = current_user.id
#         elif isinstance(current_user, int):
#             user_id = current_user
#         else:
#             user_id = 1
        
#         # Créer le contrôleur
#         self.controller = ReportsController(session=session, current_user_id=user_id)
#         self.current_user = current_user
#         self.current_report_data = None
#         self.charts = {}
        
#         self.setup_ui()
#         self.setup_shortcuts()
#         self.load_dashboard_stats()
    
#     def setup_ui(self):
#         main_layout = QVBoxLayout(self)
#         main_layout.setContentsMargins(0, 0, 0, 0)
#         main_layout.setSpacing(0)
        
#         # Scroll area
#         scroll = QScrollArea()
#         scroll.setWidgetResizable(True)
#         scroll.setFrameShape(QFrame.NoFrame)
#         scroll.setStyleSheet("QScrollArea { background-color: #f0f2f5; border: none; }")
        
#         container = QWidget()
#         container.setStyleSheet("background-color: #f0f2f5;")
#         container_layout = QVBoxLayout(container)
#         container_layout.setContentsMargins(24, 24, 24, 24)
#         container_layout.setSpacing(24)
        
#         # Header amélioré
#         container_layout.addWidget(self._create_enhanced_header())
        
#         # Dashboard de statistiques
#         container_layout.addWidget(self._create_stats_dashboard())
        
#         # Quick actions
#         container_layout.addWidget(self._create_quick_actions())
        
#         # Onglets des rapports
#         self.tab_widget = QTabWidget()
#         self.tab_widget.setStyleSheet("""
#             QTabWidget::pane {
#                 background: white;
#                 border-radius: 16px;
#                 border: 1px solid #e2e8f0;
#             }
#             QTabBar::tab {
#                 background: #f1f5f9;
#                 padding: 12px 28px;
#                 margin-right: 6px;
#                 border-radius: 10px;
#                 font-weight: 600;
#                 font-size: 13px;
#             }
#             QTabBar::tab:selected {
#                 background: #3b82f6;
#                 color: white;
#             }
#             QTabBar::tab:hover {
#                 background: #e2e8f0;
#             }
#         """)
        
#         # Ajout des onglets
#         self.tab_widget.addTab(self._create_enhanced_contacts_tab(), "👥 Contacts")
#         self.tab_widget.addTab(self._create_enhanced_vehicles_tab(), "🚗 Véhicules")
#         self.tab_widget.addTab(self._create_enhanced_financial_tab(), "💰 Financier")
#         self.tab_widget.addTab(self._create_enhanced_fleets_tab(), "🏢 Flottes")
#         self.tab_widget.addTab(self._create_enhanced_compagnies_tab(), "🏛️ Compagnies")
#         self.tab_widget.addTab(self._create_enhanced_activity_tab(), "📊 Activité")
#         self.tab_widget.addTab(self._create_enhanced_top_performers_tab(), "⭐ Top Performers")
#         self.tab_widget.addTab(self._create_enhanced_expiring_tab(), "⚠️ Échéances")
#         self.tab_widget.addTab(self._create_enhanced_charts_tab(), "📈 Graphiques")
        
#         container_layout.addWidget(self.tab_widget)
        
#         scroll.setWidget(container)
#         main_layout.addWidget(scroll)
    
#     def _create_enhanced_header(self):
#         header = QFrame()
#         header.setStyleSheet("""
#             QFrame {
#                 background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
#                     stop:0 #1e293b, stop:1 #0f172a);
#                 border-radius: 20px;
#             }
#         """)
#         header.setMinimumHeight(120)
        
#         layout = QHBoxLayout(header)
#         layout.setContentsMargins(30, 20, 30, 20)
        
#         # Partie gauche
#         left_layout = QVBoxLayout()
#         title = QLabel("📊 Centre de Rapports & Analytics")
#         title.setStyleSheet("font-size: 26px; font-weight: 800; color: white; letter-spacing: -0.5px;")
        
#         subtitle = QLabel("Analysez vos données, générez des rapports personnalisés et exportez-les")
#         subtitle.setStyleSheet("font-size: 14px; color: #94a3b8;")
        
#         left_layout.addWidget(title)
#         left_layout.addWidget(subtitle)
        
#         # Partie droite
#         right_layout = QHBoxLayout()
#         right_layout.setSpacing(15)
        
#         # Date rapide
#         self.quick_date = QComboBox()
#         self.quick_date.addItems([
#             "Aujourd'hui", "Cette semaine", "Ce mois", "Ce trimestre", "Cette année"
#         ])
#         self.quick_date.setStyleSheet("""
#             QComboBox {
#                 background: rgba(255,255,255,0.1);
#                 color: white;
#                 border: 1px solid rgba(255,255,255,0.2);
#                 border-radius: 10px;
#                 padding: 8px 16px;
#                 min-width: 140px;
#             }
#             QComboBox::drop-down { border: none; }
#             QComboBox QAbstractItemView {
#                 background: #1e293b;
#                 color: white;
#                 selection-background-color: #3b82f6;
#             }
#         """)
#         self.quick_date.currentTextChanged.connect(self.on_quick_date_changed)
#         right_layout.addWidget(self.quick_date)
        
#         # Bouton export global
#         global_export_btn = QPushButton("📎 Export global")
#         global_export_btn.setStyleSheet("""
#             QPushButton {
#                 background: #10b981;
#                 color: white;
#                 border: none;
#                 border-radius: 10px;
#                 padding: 8px 20px;
#                 font-weight: 600;
#             }
#             QPushButton:hover { background: #059669; }
#         """)
#         global_export_btn.clicked.connect(self.export_global_report)
#         right_layout.addWidget(global_export_btn)
        
#         layout.addLayout(left_layout)
#         layout.addStretch()
#         layout.addLayout(right_layout)
        
#         return header
    
#     def _create_stats_dashboard(self):
#         """Crée le dashboard de statistiques avec cartes modernes"""
#         stats_widget = QWidget()
#         layout = QGridLayout(stats_widget)
#         layout.setSpacing(20)
        
#         # Cartes de statistiques
#         stats_data = [
#             ("Total contacts", "0", "👥", "#3b82f6", "contacts_count"),
#             ("Véhicules", "0", "🚗", "#10b981", "vehicles_count"),
#             ("Contrats actifs", "0", "📄", "#f59e0b", "contracts_count"),
#             ("Prime totale", "0 FCFA", "💰", "#8b5cf6", "total_premium"),
#             ("Clients VIP", "0", "⭐", "#ec4899", "vip_count"),
#             ("Taux satisfaction", "0%", "😊", "#06b6d4", "satisfaction")
#         ]
        
#         self.stats_cards = {}
#         for i, (title, value, icon, color, key) in enumerate(stats_data):
#             card = ModernReportCard(title, value, icon, color)
#             layout.addWidget(card, i // 3, i % 3)
#             self.stats_cards[key] = card
        
#         return stats_widget
    
#     def _create_quick_actions(self):
#         """Crée la barre d'actions rapides"""
#         actions_frame = QFrame()
#         actions_frame.setStyleSheet("""
#             QFrame {
#                 background: white;
#                 border-radius: 16px;
#                 border: 1px solid #e2e8f0;
#             }
#         """)
        
#         layout = QHBoxLayout(actions_frame)
#         layout.setContentsMargins(20, 15, 20, 15)
#         layout.setSpacing(20)
        
#         actions = [
#             ("📧", "Envoyer par email", self.send_report_email),
#             ("📊", "Tableau de bord", self.show_dashboard),
#             ("📅", "Planifier rapport", self.schedule_report),
#             ("🔔", "Alertes", self.show_alerts),
#             ("⚙️", "Préférences", self.show_preferences)
#         ]
        
#         for icon, text, callback in actions:
#             btn = QPushButton(f"{icon} {text}")
#             btn.setStyleSheet("""
#                 QPushButton {
#                     background: #f8fafc;
#                     border: 1px solid #e2e8f0;
#                     border-radius: 10px;
#                     padding: 8px 16px;
#                     font-weight: 500;
#                 }
#                 QPushButton:hover {
#                     background: #eff6ff;
#                     border-color: #3b82f6;
#                     color: #3b82f6;
#                 }
#             """)
#             btn.clicked.connect(callback)
#             layout.addWidget(btn)
        
#         layout.addStretch()
        
#         # Barre de recherche
#         self.search_report = QLineEdit()
#         self.search_report.setPlaceholderText("🔍 Rechercher un rapport...")
#         self.search_report.setStyleSheet("""
#             QLineEdit {
#                 border: 1px solid #e2e8f0;
#                 border-radius: 10px;
#                 padding: 8px 16px;
#                 min-width: 250px;
#             }
#             QLineEdit:focus { border-color: #3b82f6; }
#         """)
#         layout.addWidget(self.search_report)
        
#         return actions_frame
    
#     def _create_enhanced_contacts_tab(self):
#         """Onglet contacts amélioré avec aperçu graphique"""
#         tab = QWidget()
#         layout = QVBoxLayout(tab)
#         layout.setSpacing(20)
        
#         # Splitter pour graphique et filtres
#         splitter = QSplitter(Qt.Horizontal)
        
#         # Panneau gauche - Filtres
#         left_panel = QWidget()
#         left_layout = QVBoxLayout(left_panel)
#         left_layout.setSpacing(15)
        
#         # Filtres avancés
#         filters_group = QGroupBox("🔍 Filtres avancés")
#         filters_group.setStyleSheet("""
#             QGroupBox {
#                 font-weight: 700;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 12px;
#                 margin-top: 12px;
#                 padding-top: 12px;
#             }
#             QGroupBox::title {
#                 subcontrol-origin: margin;
#                 left: 16px;
#                 padding: 0 8px;
#             }
#         """)
#         filters_layout = QGridLayout(filters_group)
#         filters_layout.setSpacing(12)
        
#         # Date début
#         filters_layout.addWidget(QLabel("Date début:"), 0, 0)
#         self.contacts_date_debut = QDateEdit()
#         self.contacts_date_debut.setDate(QDate.currentDate().addMonths(-1))
#         self.contacts_date_debut.setCalendarPopup(True)
#         filters_layout.addWidget(self.contacts_date_debut, 0, 1)
        
#         # Date fin
#         filters_layout.addWidget(QLabel("Date fin:"), 1, 0)
#         self.contacts_date_fin = QDateEdit()
#         self.contacts_date_fin.setDate(QDate.currentDate())
#         self.contacts_date_fin.setCalendarPopup(True)
#         filters_layout.addWidget(self.contacts_date_fin, 1, 1)
        
#         # Type de contact
#         filters_layout.addWidget(QLabel("Type:"), 2, 0)
#         self.contacts_type = QComboBox()
#         self.contacts_type.addItems(["Tous", "Assuré", "Prospect", "Partenaire", "Fournisseur"])
#         filters_layout.addWidget(self.contacts_type, 2, 1)
        
#         # Statut
#         filters_layout.addWidget(QLabel("Statut:"), 3, 0)
#         self.contacts_status = QComboBox()
#         self.contacts_status.addItems(["Tous", "Actif", "Inactif", "En attente"])
#         filters_layout.addWidget(self.contacts_status, 3, 1)
        
#         left_layout.addWidget(filters_group)
        
#         # Boutons
#         btn_generate = QPushButton("📊 Générer le rapport")
#         btn_generate.setStyleSheet("""
#             QPushButton {
#                 background: #3b82f6;
#                 color: white;
#                 border-radius: 10px;
#                 padding: 12px;
#                 font-weight: 600;
#             }
#             QPushButton:hover { background: #2563eb; }
#         """)
#         btn_generate.clicked.connect(lambda: self.generate_report('contacts'))
#         left_layout.addWidget(btn_generate)
        
#         left_layout.addStretch()
        
#         # Panneau droit - Résultats
#         right_panel = QWidget()
#         right_layout = QVBoxLayout(right_panel)
        
#         # Mini graphique
#         self.contacts_chart = QChartView()
#         self.contacts_chart.setFixedHeight(200)
#         self.contacts_chart.setStyleSheet("background: #f8fafc; border-radius: 12px;")
#         right_layout.addWidget(self.contacts_chart)
        
#         # Résultat texte
#         self.contacts_result = QTextEdit()
#         self.contacts_result.setReadOnly(True)
#         self.contacts_result.setStyleSheet("""
#             QTextEdit {
#                 font-family: monospace;
#                 font-size: 12px;
#                 background: #1e1e2e;
#                 color: #cdd6f4;
#                 border-radius: 12px;
#                 padding: 16px;
#             }
#         """)
#         right_layout.addWidget(self.contacts_result)
        
#         splitter.addWidget(left_panel)
#         splitter.addWidget(right_panel)
#         splitter.setSizes([300, 700])
        
#         layout.addWidget(splitter)
        
#         # Boutons d'export
#         export_layout = QHBoxLayout()
#         export_layout.addStretch()
        
#         export_csv = QPushButton("📄 Exporter CSV")
#         export_csv.setStyleSheet("padding: 10px 20px;")
#         export_csv.clicked.connect(lambda: self.export_report('csv', 'contacts'))
        
#         export_pdf = QPushButton("📑 Exporter PDF")
#         export_pdf.setStyleSheet("padding: 10px 20px;")
#         export_pdf.clicked.connect(lambda: self.export_report('pdf', 'contacts'))
        
#         export_layout.addWidget(export_csv)
#         export_layout.addWidget(export_pdf)
#         layout.addLayout(export_layout)
        
#         return tab
    
#     def _create_enhanced_vehicles_tab(self):
#         """Onglet véhicules amélioré"""
#         tab = QWidget()
#         layout = QVBoxLayout(tab)
#         layout.setSpacing(20)
        
#         # Ligne de filtres
#         filters_layout = QHBoxLayout()
#         filters_layout.setSpacing(15)
        
#         # Date début
#         self.vehicles_date_debut = QDateEdit()
#         self.vehicles_date_debut.setDate(QDate.currentDate().addMonths(-1))
#         self.vehicles_date_debut.setCalendarPopup(True)
#         self._add_filter_row(filters_layout, "Du:", self.vehicles_date_debut)
        
#         # Date fin
#         self.vehicles_date_fin = QDateEdit()
#         self.vehicles_date_fin.setDate(QDate.currentDate())
#         self.vehicles_date_fin.setCalendarPopup(True)
#         self._add_filter_row(filters_layout, "Au:", self.vehicles_date_fin)
        
#         # Statut
#         self.vehicles_status = QComboBox()
#         self.vehicles_status.addItems(["Tous", "ACTIF", "EXPIRE", "EN_ATTENTE"])
#         self._add_filter_row(filters_layout, "Statut:", self.vehicles_status)
        
#         # Catégorie
#         self.vehicles_category = QComboBox()
#         self.vehicles_category.addItems(["Toutes", "VP", "VU", "PL", "VL"])
#         self._add_filter_row(filters_layout, "Catégorie:", self.vehicles_category)
        
#         layout.addLayout(filters_layout)
        
#         # Tableau des résultats
#         self.vehicles_table = QTableWidget()
#         self.vehicles_table.setColumnCount(8)
#         self.vehicles_table.setHorizontalHeaderLabels([
#             "ID", "Immatriculation", "Marque", "Modèle", "Catégorie", "Statut", "Prime", "Actions"
#         ])
#         self.vehicles_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
#         self.vehicles_table.setAlternatingRowColors(True)
#         self.vehicles_table.setSelectionBehavior(QTableWidget.SelectRows)
#         layout.addWidget(self.vehicles_table)
        
#         # Boutons
#         btn_layout = QHBoxLayout()
        
#         generate_btn = QPushButton("🔍 Rechercher")
#         generate_btn.setStyleSheet("background: #3b82f6; color: white; padding: 10px 20px; font-weight: 600;")
#         generate_btn.clicked.connect(lambda: self.generate_report('vehicles'))
        
#         export_csv_btn = QPushButton("📄 Exporter CSV")
#         export_csv_btn.clicked.connect(lambda: self.export_report('csv', 'vehicles'))
        
#         export_pdf_btn = QPushButton("📑 Exporter PDF")
#         export_pdf_btn.clicked.connect(lambda: self.export_report('pdf', 'vehicles'))
        
#         btn_layout.addWidget(generate_btn)
#         btn_layout.addStretch()
#         btn_layout.addWidget(export_csv_btn)
#         btn_layout.addWidget(export_pdf_btn)
#         layout.addLayout(btn_layout)
        
#         return tab
    
#     def _create_enhanced_financial_tab(self):
#         """Onglet financier amélioré avec graphiques"""
#         tab = QWidget()
#         layout = QVBoxLayout(tab)
#         layout.setSpacing(20)
        
#         # Filtres
#         filters_layout = QHBoxLayout()
        
#         self.financial_date_debut = QDateEdit()
#         self.financial_date_debut.setDate(QDate.currentDate().addMonths(-1))
#         self.financial_date_debut.setCalendarPopup(True)
#         self._add_filter_row(filters_layout, "Du:", self.financial_date_debut)
        
#         self.financial_date_fin = QDateEdit()
#         self.financial_date_fin.setDate(QDate.currentDate())
#         self.financial_date_fin.setCalendarPopup(True)
#         self._add_filter_row(filters_layout, "Au:", self.financial_date_fin)
        
#         self.financial_period = QComboBox()
#         self.financial_period.addItems(["Jour", "Mois", "Année"])
#         self._add_filter_row(filters_layout, "Période:", self.financial_period)
        
#         layout.addLayout(filters_layout)
        
#         # Graphique
#         self.financial_chart = QChartView()
#         self.financial_chart.setFixedHeight(300)
#         self.financial_chart.setStyleSheet("background: white; border-radius: 12px;")
#         layout.addWidget(self.financial_chart)
        
#         # Résultat texte
#         self.financial_result = QTextEdit()
#         self.financial_result.setReadOnly(True)
#         self.financial_result.setStyleSheet("""
#             QTextEdit {
#                 font-family: monospace;
#                 font-size: 12px;
#                 background: #1e1e2e;
#                 color: #cdd6f4;
#                 border-radius: 12px;
#                 padding: 16px;
#                 min-height: 200px;
#             }
#         """)
#         layout.addWidget(self.financial_result)
        
#         # Boutons
#         btn_layout = QHBoxLayout()
#         generate_btn = QPushButton("📊 Générer")
#         generate_btn.setStyleSheet("background: #3b82f6; color: white; padding: 10px 20px;")
#         generate_btn.clicked.connect(lambda: self.generate_report('financial'))
        
#         export_csv_btn = QPushButton("📄 CSV")
#         export_csv_btn.clicked.connect(lambda: self.export_report('csv', 'financial'))
        
#         export_pdf_btn = QPushButton("📑 PDF")
#         export_pdf_btn.clicked.connect(lambda: self.export_report('pdf', 'financial'))
        
#         btn_layout.addWidget(generate_btn)
#         btn_layout.addStretch()
#         btn_layout.addWidget(export_csv_btn)
#         btn_layout.addWidget(export_pdf_btn)
#         layout.addLayout(btn_layout)
        
#         return tab
    
#     def _create_enhanced_fleets_tab(self):
#         """Onglet flottes amélioré"""
#         tab = QWidget()
#         layout = QVBoxLayout(tab)
#         layout.setSpacing(20)
        
#         # Tableau
#         self.fleets_table = QTableWidget()
#         self.fleets_table.setColumnCount(5)
#         self.fleets_table.setHorizontalHeaderLabels(["ID", "Nom", "Véhicules", "Prime totale", "Actions"])
#         self.fleets_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
#         self.fleets_table.setAlternatingRowColors(True)
#         layout.addWidget(self.fleets_table)
        
#         # Boutons
#         btn_layout = QHBoxLayout()
#         generate_btn = QPushButton("📊 Générer le rapport")
#         generate_btn.clicked.connect(lambda: self.generate_report('fleets'))
        
#         export_csv_btn = QPushButton("📄 Exporter CSV")
#         export_csv_btn.clicked.connect(lambda: self.export_report('csv', 'fleets'))
        
#         export_pdf_btn = QPushButton("📑 Exporter PDF")
#         export_pdf_btn.clicked.connect(lambda: self.export_report('pdf', 'fleets'))
        
#         btn_layout.addWidget(generate_btn)
#         btn_layout.addStretch()
#         btn_layout.addWidget(export_csv_btn)
#         btn_layout.addWidget(export_pdf_btn)
#         layout.addLayout(btn_layout)
        
#         return tab
    
#     def _create_enhanced_compagnies_tab(self):
#         """Onglet compagnies amélioré"""
#         tab = QWidget()
#         layout = QVBoxLayout(tab)
#         layout.setSpacing(20)
        
#         # Tableau
#         self.compagnies_table = QTableWidget()
#         self.compagnies_table.setColumnCount(5)
#         self.compagnies_table.setHorizontalHeaderLabels(["ID", "Nom", "Code", "Véhicules", "Prime totale"])
#         self.compagnies_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
#         self.compagnies_table.setAlternatingRowColors(True)
#         layout.addWidget(self.compagnies_table)
        
#         # Boutons
#         btn_layout = QHBoxLayout()
#         generate_btn = QPushButton("📊 Générer le rapport")
#         generate_btn.clicked.connect(lambda: self.generate_report('compagnies'))
        
#         export_csv_btn = QPushButton("📄 Exporter CSV")
#         export_csv_btn.clicked.connect(lambda: self.export_report('csv', 'compagnies'))
        
#         export_pdf_btn = QPushButton("📑 Exporter PDF")
#         export_pdf_btn.clicked.connect(lambda: self.export_report('pdf', 'compagnies'))
        
#         btn_layout.addWidget(generate_btn)
#         btn_layout.addStretch()
#         btn_layout.addWidget(export_csv_btn)
#         btn_layout.addWidget(export_pdf_btn)
#         layout.addLayout(btn_layout)
        
#         return tab
    
#     def _create_enhanced_activity_tab(self):
#         """Onglet activité amélioré"""
#         tab = QWidget()
#         layout = QVBoxLayout(tab)
#         layout.setSpacing(20)
        
#         # Filtres
#         filters_layout = QHBoxLayout()
        
#         self.activity_days = QComboBox()
#         self.activity_days.addItems(["30 jours", "60 jours", "90 jours", "180 jours", "365 jours"])
#         self._add_filter_row(filters_layout, "Période:", self.activity_days)
        
#         layout.addLayout(filters_layout)
        
#         # Graphique d'activité
#         self.activity_chart = QChartView()
#         self.activity_chart.setFixedHeight(250)
#         self.activity_chart.setStyleSheet("background: white; border-radius: 12px;")
#         layout.addWidget(self.activity_chart)
        
#         # Résultat
#         self.activity_result = QTextEdit()
#         self.activity_result.setReadOnly(True)
#         self.activity_result.setStyleSheet("""
#             QTextEdit {
#                 font-family: monospace;
#                 font-size: 12px;
#                 background: #1e1e2e;
#                 color: #cdd6f4;
#                 border-radius: 12px;
#                 padding: 16px;
#                 min-height: 200px;
#             }
#         """)
#         layout.addWidget(self.activity_result)
        
#         # Boutons
#         btn_layout = QHBoxLayout()
#         generate_btn = QPushButton("📊 Générer")
#         generate_btn.clicked.connect(lambda: self.generate_report('activity'))
        
#         export_csv_btn = QPushButton("📄 CSV")
#         export_csv_btn.clicked.connect(lambda: self.export_report('csv', 'activity'))
        
#         export_pdf_btn = QPushButton("📑 PDF")
#         export_pdf_btn.clicked.connect(lambda: self.export_report('pdf', 'activity'))
        
#         btn_layout.addWidget(generate_btn)
#         btn_layout.addStretch()
#         btn_layout.addWidget(export_csv_btn)
#         btn_layout.addWidget(export_pdf_btn)
#         layout.addLayout(btn_layout)
        
#         return tab
    
#     def _create_enhanced_top_performers_tab(self):
#         """Onglet top performers amélioré"""
#         tab = QWidget()
#         layout = QVBoxLayout(tab)
#         layout.setSpacing(20)
        
#         # Filtres
#         filters_layout = QHBoxLayout()
        
#         self.top_limit = QSpinBox()
#         self.top_limit.setRange(5, 100)
#         self.top_limit.setValue(10)
#         self._add_filter_row(filters_layout, "Limite:", self.top_limit)
        
#         layout.addLayout(filters_layout)
        
#         # Graphique
#         self.top_chart = QChartView()
#         self.top_chart.setFixedHeight(250)
#         self.top_chart.setStyleSheet("background: white; border-radius: 12px;")
#         layout.addWidget(self.top_chart)
        
#         # Résultat
#         self.top_performers_result = QTextEdit()
#         self.top_performers_result.setReadOnly(True)
#         self.top_performers_result.setStyleSheet("""
#             QTextEdit {
#                 font-family: monospace;
#                 font-size: 12px;
#                 background: #1e1e2e;
#                 color: #cdd6f4;
#                 border-radius: 12px;
#                 padding: 16px;
#                 min-height: 200px;
#             }
#         """)
#         layout.addWidget(self.top_performers_result)
        
#         # Boutons
#         btn_layout = QHBoxLayout()
#         generate_btn = QPushButton("📊 Générer")
#         generate_btn.clicked.connect(lambda: self.generate_report('top_performers'))
        
#         export_csv_btn = QPushButton("📄 CSV")
#         export_csv_btn.clicked.connect(lambda: self.export_report('csv', 'top_performers'))
        
#         export_pdf_btn = QPushButton("📑 PDF")
#         export_pdf_btn.clicked.connect(lambda: self.export_report('pdf', 'top_performers'))
        
#         btn_layout.addWidget(generate_btn)
#         btn_layout.addStretch()
#         btn_layout.addWidget(export_csv_btn)
#         btn_layout.addWidget(export_pdf_btn)
#         layout.addLayout(btn_layout)
        
#         return tab
    
#     def _create_enhanced_expiring_tab(self):
#         """Onglet échéances amélioré"""
#         tab = QWidget()
#         layout = QVBoxLayout(tab)
#         layout.setSpacing(20)
        
#         # Filtres
#         filters_layout = QHBoxLayout()
        
#         self.expiring_days = QComboBox()
#         self.expiring_days.addItems(["30 jours", "60 jours", "90 jours", "180 jours"])
#         self._add_filter_row(filters_layout, "Période:", self.expiring_days)
        
#         layout.addLayout(filters_layout)
        
#         # Tableau
#         self.expiring_table = QTableWidget()
#         self.expiring_table.setColumnCount(6)
#         self.expiring_table.setHorizontalHeaderLabels([
#             "ID", "Police", "Client", "Date fin", "Jours restants", "Montant"
#         ])
#         self.expiring_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
#         self.expiring_table.setAlternatingRowColors(True)
#         layout.addWidget(self.expiring_table)
        
#         # Boutons
#         btn_layout = QHBoxLayout()
#         generate_btn = QPushButton("📊 Générer")
#         generate_btn.clicked.connect(lambda: self.generate_report('expiring'))
        
#         export_csv_btn = QPushButton("📄 CSV")
#         export_csv_btn.clicked.connect(lambda: self.export_report('csv', 'expiring'))
        
#         export_pdf_btn = QPushButton("📑 PDF")
#         export_pdf_btn.clicked.connect(lambda: self.export_report('pdf', 'expiring'))
        
#         btn_layout.addWidget(generate_btn)
#         btn_layout.addStretch()
#         btn_layout.addWidget(export_csv_btn)
#         btn_layout.addWidget(export_pdf_btn)
#         layout.addLayout(btn_layout)
        
#         return tab
    
#     def _create_enhanced_charts_tab(self):
#         """Onglet graphiques avancés"""
#         tab = QWidget()
#         layout = QVBoxLayout(tab)
#         layout.setSpacing(20)
        
#         # Sélecteur de graphique
#         chart_selector = QHBoxLayout()
#         chart_selector.addWidget(QLabel("Type de graphique:"))
        
#         self.chart_type = QComboBox()
#         self.chart_type.addItems([
#             "Évolution des primes", "Répartition par catégorie", "Top clients",
#             "Tendance mensuelle", "Performance par marque", "Répartition par zone"
#         ])
#         chart_selector.addWidget(self.chart_type)
#         chart_selector.addStretch()
        
#         # Bouton générer
#         generate_chart_btn = QPushButton("Générer le graphique")
#         generate_chart_btn.setStyleSheet("background: #3b82f6; color: white; padding: 8px 16px;")
#         generate_chart_btn.clicked.connect(self.generate_chart)
#         chart_selector.addWidget(generate_chart_btn)
        
#         layout.addLayout(chart_selector)
        
#         # Zone du graphique
#         self.dynamic_chart = QChartView()
#         self.dynamic_chart.setFixedHeight(400)
#         self.dynamic_chart.setStyleSheet("background: white; border-radius: 16px;")
#         layout.addWidget(self.dynamic_chart)
        
#         # Légende/Stats
#         self.chart_stats = QTextEdit()
#         self.chart_stats.setReadOnly(True)
#         self.chart_stats.setMaximumHeight(150)
#         self.chart_stats.setStyleSheet("""
#             QTextEdit {
#                 background: #f8fafc;
#                 border-radius: 12px;
#                 padding: 12px;
#                 font-size: 12px;
#             }
#         """)
#         layout.addWidget(self.chart_stats)
        
#         return tab
    
#     def _add_filter_row(self, layout, label, widget):
#         """Ajoute une ligne de filtre dans un layout horizontal"""
#         layout.addWidget(QLabel(label))
#         layout.addWidget(widget)
    
#     def generate_chart(self):
#         """Génère le graphique sélectionné"""
#         chart_type = self.chart_type.currentText()
        
#         if chart_type == "Évolution des primes":
#             self._create_premium_evolution_chart()
#         elif chart_type == "Répartition par catégorie":
#             self._create_category_pie_chart()
#         elif chart_type == "Top clients":
#             self._create_top_clients_chart()
#         elif chart_type == "Tendance mensuelle":
#             self._create_monthly_trend_chart()
#         elif chart_type == "Performance par marque":
#             self._create_brand_performance_chart()
#         elif chart_type == "Répartition par zone":
#             self._create_zone_distribution_chart()
    
#     def _create_premium_evolution_chart(self):
#         """Crée un graphique d'évolution des primes"""
#         chart = QChart()
#         series = QLineSeries()
#         series.setName("Évolution des primes")
        
#         # Données simulées (à remplacer par des données réelles)
#         data = [125000, 138000, 152000, 162000, 175000, 185000, 192000, 198000, 205000, 212000]
#         for i, value in enumerate(data):
#             series.append(i, value)
        
#         chart.addSeries(series)
#         chart.setTitle("Évolution des primes (FCFA)")
#         chart.createDefaultAxes()
#         chart.legend().setVisible(True)
#         chart.legend().setAlignment(Qt.AlignBottom)
        
#         self.dynamic_chart.setChart(chart)
#         self.dynamic_chart.setRenderHint(QPainter.Antialiasing)
        
#         stats_text = f"""
# 📊 Évolution des primes
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 📈 Prime minimale: 125 000 FCFA
# 📈 Prime maximale: 212 000 FCFA
# 📊 Prime moyenne: 175 400 FCFA
# 📈 Croissance: +69.6% sur la période
# """
#         self.chart_stats.setText(stats_text)
    
#     def _create_category_pie_chart(self):
#         """Crée un graphique en secteurs par catégorie"""
#         chart = QChart()
#         series = QPieSeries()
#         series.setName("Répartition par catégorie")
        
#         # Données simulées
#         categories = [
#             ("VP (Particuliers)", 45),
#             ("VU (Utilitaires)", 30),
#             ("PL (Poids lourds)", 15),
#             ("VL (Véhicules luxe)", 10)
#         ]
        
#         for name, value in categories:
#             slice = series.append(name, value)
#             slice.setLabelVisible(True)
#             slice.setLabel(f"{name}\n{value}%")
        
#         chart.addSeries(series)
#         chart.setTitle("Répartition des véhicules par catégorie")
#         chart.legend().setVisible(True)
#         chart.legend().setAlignment(Qt.AlignBottom)
        
#         self.dynamic_chart.setChart(chart)
#         self.dynamic_chart.setRenderHint(QPainter.Antialiasing)
        
#         stats_text = f"""
# 📊 Répartition par catégorie
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 🚗 VP (Particuliers): 45% - {45} véhicules
# 🚐 VU (Utilitaires): 30% - {30} véhicules
# 🚛 PL (Poids lourds): 15% - {15} véhicules
# ✨ VL (Véhicules luxe): 10% - {10} véhicules
# """
#         self.chart_stats.setText(stats_text)
    
#     def _create_top_clients_chart(self):
#         """Crée un graphique des top clients"""
#         chart = QChart()
#         series = QBarSeries()
#         series.setName("Nombre de véhicules")
        
#         bar_set = QBarSet("Véhicules")
#         bar_set.append([25, 18, 15, 12, 10, 8, 7, 5])
#         series.append(bar_set)
        
#         chart.addSeries(series)
#         chart.setTitle("Top clients par nombre de véhicules")
        
#         axis_x = QBarCategoryAxis()
#         axis_x.append(["Client A", "Client B", "Client C", "Client D", "Client E", "Client F", "Client G", "Client H"])
#         chart.addAxis(axis_x, Qt.AlignBottom)
#         series.attachAxis(axis_x)
        
#         axis_y = QValueAxis()
#         axis_y.setRange(0, 30)
#         chart.addAxis(axis_y, Qt.AlignLeft)
#         series.attachAxis(axis_y)
        
#         self.dynamic_chart.setChart(chart)
#         self.dynamic_chart.setRenderHint(QPainter.Antialiasing)
        
#         stats_text = f"""
# 🏆 Top clients
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 🥇 Client A: 25 véhicules - Prime totale: 12 500 000 FCFA
# 🥈 Client B: 18 véhicules - Prime totale: 9 000 000 FCFA
# 🥉 Client C: 15 véhicules - Prime totale: 7 500 000 FCFA
# """
#         self.chart_stats.setText(stats_text)
    
#     def _create_monthly_trend_chart(self):
#         """Crée un graphique de tendance mensuelle"""
#         chart = QChart()
#         series = QLineSeries()
#         series.setName("Tendance mensuelle")
        
#         # Données simulées
#         months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"]
#         values = [45, 52, 48, 55, 62, 58, 65, 72, 78, 85, 82, 90]
        
#         for i, value in enumerate(values):
#             series.append(i, value)
        
#         chart.addSeries(series)
#         chart.setTitle("Tendance mensuelle des immatriculations")
        
#         axis_x = QBarCategoryAxis()
#         axis_x.append(months)
#         chart.addAxis(axis_x, Qt.AlignBottom)
#         series.attachAxis(axis_x)
        
#         axis_y = QValueAxis()
#         axis_y.setRange(0, 100)
#         chart.addAxis(axis_y, Qt.AlignLeft)
#         series.attachAxis(axis_y)
        
#         self.dynamic_chart.setChart(chart)
#         self.dynamic_chart.setRenderHint(QPainter.Antialiasing)
        
#         stats_text = f"""
# 📈 Tendance mensuelle
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 📊 Moyenne mensuelle: 62 immatriculations
# 📈 Meilleur mois: Décembre (90 immatriculations)
# 📉 Mois le plus bas: Janvier (45 immatriculations)
# 📊 Croissance annuelle: +100% (de 45 à 90)
# """
#         self.chart_stats.setText(stats_text)
    
#     def _create_brand_performance_chart(self):
#         """Crée un graphique de performance par marque"""
#         chart = QChart()
#         series = QBarSeries()
#         series.setName("Nombre de véhicules")
        
#         bar_set = QBarSet("Véhicules")
#         bar_set.append([35, 28, 22, 18, 15, 12])
#         series.append(bar_set)
        
#         chart.addSeries(series)
#         chart.setTitle("Performance par marque")
        
#         axis_x = QBarCategoryAxis()
#         axis_x.append(["Toyota", "Renault", "Peugeot", "Mitsubishi", "Mercedes", "Autres"])
#         chart.addAxis(axis_x, Qt.AlignBottom)
#         series.attachAxis(axis_x)
        
#         axis_y = QValueAxis()
#         axis_y.setRange(0, 40)
#         chart.addAxis(axis_y, Qt.AlignLeft)
#         series.attachAxis(axis_y)
        
#         self.dynamic_chart.setChart(chart)
#         self.dynamic_chart.setRenderHint(QPainter.Antialiasing)
        
#         stats_text = f"""
# 🏭 Performance par marque
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 🚗 Toyota: 35 véhicules (25%) - Leader du marché
# 🚙 Renault: 28 véhicules (20%)
# 🚘 Peugeot: 22 véhicules (16%)
# """
#         self.chart_stats.setText(stats_text)
    
#     def _create_zone_distribution_chart(self):
#         """Crée un graphique de répartition par zone"""
#         chart = QChart()
#         series = QPieSeries()
#         series.setName("Répartition par zone")
        
#         zones = [
#             ("Zone A (Urbain)", 55),
#             ("Zone B (Périurbain)", 30),
#             ("Zone C (Rural)", 15)
#         ]
        
#         for name, value in zones:
#             slice = series.append(name, value)
#             slice.setLabelVisible(True)
#             slice.setLabel(f"{name}\n{value}%")
        
#         chart.addSeries(series)
#         chart.setTitle("Répartition géographique des véhicules")
#         chart.legend().setVisible(True)
#         chart.legend().setAlignment(Qt.AlignBottom)
        
#         self.dynamic_chart.setChart(chart)
#         self.dynamic_chart.setRenderHint(QPainter.Antialiasing)
        
#         stats_text = f"""
# 🗺️ Répartition par zone tarifaire
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 🏙️ Zone A (Urbain): 55% - Primes plus élevées
# 🏘️ Zone B (Périurbain): 30% - Primes modérées
# 🌾 Zone C (Rural): 15% - Primes réduites
# """
#         self.chart_stats.setText(stats_text)
    
#     def generate_report(self, report_type):
#         """Génère un rapport selon le type"""
#         filters = self._get_filters_for_report(report_type)
        
#         report_methods = {
#             'contacts': (self.controller.get_contacts_report, self._display_contacts_report),
#             'vehicles': (self.controller.get_vehicles_report, self._display_vehicles_report),
#             'financial': (self.controller.get_financial_report, self._display_financial_report),
#             'fleets': (self.controller.get_fleets_report, self._display_fleets_report),
#             'compagnies': (self.controller.get_compagnies_report, self._display_compagnies_report),
#             'activity': (self.controller.get_activity_report, self._display_activity_report),
#             'top_performers': (self.controller.get_top_performers_report, self._display_top_performers_report),
#             'expiring': (self.controller.get_expiring_contracts_report, self._display_expiring_report)
#         }
        
#         if report_type not in report_methods:
#             return
        
#         method, display_func = report_methods[report_type]
        
#         async_query.execute(
#             lambda: method(**filters),
#             on_finished=lambda data: display_func(data),
#             on_error=lambda e: self._show_error(e),
#             show_loader=True,
#             loader_message="Génération du rapport..."
#         )
    
#     def _get_filters_for_report(self, report_type):
#         """Récupère les filtres pour un type de rapport spécifique"""
#         filters = {}
        
#         if report_type == 'contacts':
#             filters['date_start'] = self.contacts_date_debut.date().toPython()
#             filters['date_end'] = self.contacts_date_fin.date().toPython()
#             filters['type_contact'] = self.contacts_type.currentText()
#             filters['status'] = self.contacts_status.currentText()
        
#         elif report_type == 'vehicles':
#             filters['date_start'] = self.vehicles_date_debut.date().toPython()
#             filters['date_end'] = self.vehicles_date_fin.date().toPython()
#             filters['status'] = self.vehicles_status.currentText()
#             filters['category'] = self.vehicles_category.currentText()
        
#         elif report_type == 'financial':
#             filters['date_start'] = self.financial_date_debut.date().toPython()
#             filters['date_end'] = self.financial_date_fin.date().toPython()
#             filters['period'] = self.financial_period.currentText().lower()
        
#         elif report_type == 'activity':
#             days_text = self.activity_days.currentText()
#             filters['days'] = int(days_text.split()[0])
        
#         elif report_type == 'top_performers':
#             filters['limit'] = self.top_limit.value()
        
#         elif report_type == 'expiring':
#             days_text = self.expiring_days.currentText()
#             filters['days'] = int(days_text.split()[0])
        
#         return filters
    
#     def _display_contacts_report(self, data):
#         """Affiche le rapport des contacts"""
#         if hasattr(self, 'contacts_result'):
#             self._display_text_report(self.contacts_result, data)
        
#         # Créer le graphique associé
#         self._create_contacts_chart(data)
    
#     def _display_vehicles_report(self, data):
#         """Affiche le rapport des véhicules dans le tableau"""
#         if hasattr(self, 'vehicles_table'):
#             self.vehicles_table.setRowCount(0)
            
#             for i, vehicle in enumerate(data.get('data', [])):
#                 self.vehicles_table.insertRow(i)
#                 self.vehicles_table.setItem(i, 0, QTableWidgetItem(str(vehicle.id)))
#                 self.vehicles_table.setItem(i, 1, QTableWidgetItem(vehicle.immatriculation or ""))
#                 self.vehicles_table.setItem(i, 2, QTableWidgetItem(vehicle.marque or ""))
#                 self.vehicles_table.setItem(i, 3, QTableWidgetItem(vehicle.modele or ""))
#                 self.vehicles_table.setItem(i, 4, QTableWidgetItem(vehicle.categorie or ""))
                
#                 status_item = QTableWidgetItem(vehicle.statut or "")
#                 if vehicle.statut == "ACTIF":
#                     status_item.setForeground(QBrush(QColor("#10b981")))
#                 elif vehicle.statut == "EXPIRE":
#                     status_item.setForeground(QBrush(QColor("#ef4444")))
#                 self.vehicles_table.setItem(i, 5, status_item)
                
#                 prime_item = QTableWidgetItem(f"{vehicle.prime_nette:,.0f} FCFA" if vehicle.prime_nette else "0 FCFA")
#                 prime_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
#                 self.vehicles_table.setItem(i, 6, prime_item)
                
#                 # Bouton voir détails
#                 view_btn = QPushButton("👁️")
#                 view_btn.setFixedSize(30, 25)
#                 self.vehicles_table.setCellWidget(i, 7, view_btn)
            
#             self.vehicles_table.resizeColumnsToContents()
    
#     def _display_financial_report(self, data):
#         """Affiche le rapport financier"""
#         if hasattr(self, 'financial_result'):
#             self._display_text_report(self.financial_result, data)
        
#         # Créer le graphique financier
#         self._create_financial_chart(data)
    
#     def _display_fleets_report(self, data):
#         """Affiche le rapport des flottes"""
#         if hasattr(self, 'fleets_table'):
#             self.fleets_table.setRowCount(0)
            
#             for i, fleet_data in enumerate(data.get('data', [])):
#                 fleet = fleet_data.get('fleet')
#                 self.fleets_table.insertRow(i)
#                 self.fleets_table.setItem(i, 0, QTableWidgetItem(str(getattr(fleet, 'id', ''))))
#                 self.fleets_table.setItem(i, 1, QTableWidgetItem(getattr(fleet, 'nom_flotte', '')))
#                 self.fleets_table.setItem(i, 2, QTableWidgetItem(str(fleet_data.get('vehicle_count', 0))))
#                 self.fleets_table.setItem(i, 3, QTableWidgetItem(f"{fleet_data.get('total_prime', 0):,.0f} FCFA"))
                
#                 view_btn = QPushButton("👁️")
#                 view_btn.setFixedSize(30, 25)
#                 self.fleets_table.setCellWidget(i, 4, view_btn)
    
#     def _display_compagnies_report(self, data):
#         """Affiche le rapport des compagnies"""
#         if hasattr(self, 'compagnies_table'):
#             self.compagnies_table.setRowCount(0)
            
#             for i, cie_data in enumerate(data.get('data', [])):
#                 cie = cie_data.get('compagnie')
#                 self.compagnies_table.insertRow(i)
#                 self.compagnies_table.setItem(i, 0, QTableWidgetItem(str(getattr(cie, 'id', ''))))
#                 self.compagnies_table.setItem(i, 1, QTableWidgetItem(getattr(cie, 'nom', '')))
#                 self.compagnies_table.setItem(i, 2, QTableWidgetItem(getattr(cie, 'code', '')))
#                 self.compagnies_table.setItem(i, 3, QTableWidgetItem(str(cie_data.get('vehicle_count', 0))))
#                 self.compagnies_table.setItem(i, 4, QTableWidgetItem(f"{cie_data.get('total_prime', 0):,.0f} FCFA"))
    
#     def _display_activity_report(self, data):
#         """Affiche le rapport d'activité"""
#         if hasattr(self, 'activity_result'):
#             self._display_text_report(self.activity_result, data)
        
#         # Créer le graphique d'activité
#         self._create_activity_chart(data)
    
#     def _display_top_performers_report(self, data):
#         """Affiche le rapport top performers"""
#         if hasattr(self, 'top_performers_result'):
#             self._display_text_report(self.top_performers_result, data)
        
#         # Créer le graphique top performers
#         self._create_top_performers_chart(data)
    
#     def _display_expiring_report(self, data):
#         """Affiche le rapport des échéances"""
#         if hasattr(self, 'expiring_table'):
#             self.expiring_table.setRowCount(0)
            
#             today = datetime.now().date()
            
#             for i, contrat in enumerate(data.get('data', [])):
#                 self.expiring_table.insertRow(i)
#                 self.expiring_table.setItem(i, 0, QTableWidgetItem(str(getattr(contrat, 'id', ''))))
#                 self.expiring_table.setItem(i, 1, QTableWidgetItem(getattr(contrat, 'numero_police', '')))
#                 self.expiring_table.setItem(i, 2, QTableWidgetItem(getattr(contrat, 'proprietaire_nom', '')))
                
#                 date_fin = contrat.date_fin if hasattr(contrat, 'date_fin') else None
#                 date_fin_str = date_fin.strftime("%d/%m/%Y") if date_fin else ""
#                 self.expiring_table.setItem(i, 3, QTableWidgetItem(date_fin_str))
                
#                 if date_fin:
#                     days_left = (date_fin - today).days
#                     days_item = QTableWidgetItem(str(days_left))
#                     if days_left <= 7:
#                         days_item.setForeground(QBrush(QColor("#ef4444")))
#                     elif days_left <= 30:
#                         days_item.setForeground(QBrush(QColor("#f59e0b")))
#                     else:
#                         days_item.setForeground(QBrush(QColor("#10b981")))
#                     self.expiring_table.setItem(i, 4, days_item)
#                 else:
#                     self.expiring_table.setItem(i, 4, QTableWidgetItem("-"))
                
#                 montant = getattr(contrat, 'prime_totale_ttc', 0)
#                 self.expiring_table.setItem(i, 5, QTableWidgetItem(f"{montant:,.0f} FCFA"))
    
#     def _display_text_report(self, text_edit, data):
#         """Affiche un rapport texte dans un QTextEdit"""
#         if not text_edit:
#             return
        
#         text = f"""
# ╔══════════════════════════════════════════════════════════════════╗
# ║                    {data.get('title', 'Rapport')}                    ║
# ╚══════════════════════════════════════════════════════════════════╝

# 📅 Généré le: {data.get('generated_at', datetime.now()).strftime('%d/%m/%Y à %H:%M:%S')}

# """
#         if 'stats' in data:
#             text += "┌─────────────────────────────────────────────────────────────────┐\n"
#             text += "│                        STATISTIQUES                             │\n"
#             text += "├─────────────────────────────────────────────────────────────────┤\n"
#             for key, value in data['stats'].items():
#                 key_label = key.replace('_', ' ').capitalize()
#                 text += f"│  {key_label:<20} : {value:<45} │\n"
#             text += "└─────────────────────────────────────────────────────────────────┘\n"
        
#         text_edit.setText(text)
    
#     def _create_contacts_chart(self, data):
#         """Crée un graphique pour les contacts"""
#         stats = data.get('stats', {})
        
#         chart = QChart()
#         series = QPieSeries()
#         series.setName("Répartition des contacts")
        
#         for label in ['assures', 'prospects', 'partenaires']:
#             value = stats.get(label, 0)
#             if value > 0:
#                 label_name = {
#                     'assures': 'Assurés',
#                     'prospects': 'Prospects',
#                     'partenaires': 'Partenaires'
#                 }.get(label, label)
#                 series.append(label_name, value)
        
#         chart.addSeries(series)
#         chart.setTitle("Répartition des contacts")
#         chart.legend().setVisible(True)
#         chart.legend().setAlignment(Qt.AlignBottom)
        
#         if hasattr(self, 'contacts_chart'):
#             self.contacts_chart.setChart(chart)
#             self.contacts_chart.setRenderHint(QPainter.Antialiasing)
    
#     def _create_financial_chart(self, data):
#         """Crée un graphique financier"""
#         stats = data.get('stats', {})
        
#         chart = QChart()
#         series = QBarSeries()
#         series.setName("Montants (FCFA)")
        
#         bar_set = QBarSet("Montants")
#         bar_set.append([
#             stats.get('total_primes', 0) / 1000000,
#             stats.get('total_paid', 0) / 1000000,
#             stats.get('pending_paid', 0) / 1000000
#         ])
#         series.append(bar_set)
        
#         chart.addSeries(series)
#         chart.setTitle("Synthèse financière (millions FCFA)")
        
#         axis_x = QBarCategoryAxis()
#         axis_x.append(["Primes totales", "Encaissé", "Reste à encaisser"])
#         chart.addAxis(axis_x, Qt.AlignBottom)
#         series.attachAxis(axis_x)
        
#         axis_y = QValueAxis()
#         axis_y.setTitleText("Millions FCFA")
#         chart.addAxis(axis_y, Qt.AlignLeft)
#         series.attachAxis(axis_y)
        
#         if hasattr(self, 'financial_chart'):
#             self.financial_chart.setChart(chart)
#             self.financial_chart.setRenderHint(QPainter.Antialiasing)
    
#     def _create_activity_chart(self, data):
#         """Crée un graphique d'activité"""
#         activity_data = data.get('data', {})
        
#         chart = QChart()
#         series = QBarSeries()
#         series.setName("Nouveaux éléments")
        
#         bar_set = QBarSet("Quantité")
#         bar_set.append([
#             activity_data.get('new_contacts', 0),
#             activity_data.get('new_vehicles', 0),
#             activity_data.get('new_contrats', 0)
#         ])
#         series.append(bar_set)
        
#         chart.addSeries(series)
#         chart.setTitle("Activité récente")
        
#         axis_x = QBarCategoryAxis()
#         axis_x.append(["Contacts", "Véhicules", "Contrats"])
#         chart.addAxis(axis_x, Qt.AlignBottom)
#         series.attachAxis(axis_x)
        
#         axis_y = QValueAxis()
#         axis_y.setTitleText("Nombre")
#         chart.addAxis(axis_y, Qt.AlignLeft)
#         series.attachAxis(axis_y)
        
#         if hasattr(self, 'activity_chart'):
#             self.activity_chart.setChart(chart)
#             self.activity_chart.setRenderHint(QPainter.Antialiasing)
    
#     def _create_top_performers_chart(self, data):
#         """Crée un graphique des top performers"""
#         top_clients = data.get('data', {}).get('top_clients', [])[:10]
        
#         chart = QChart()
#         series = QBarSeries()
#         series.setName("Nombre de véhicules")
        
#         bar_set = QBarSet("Véhicules")
#         values = [getattr(c, 'vehicle_count', 0) for c in top_clients]
#         bar_set.append(values)
#         series.append(bar_set)
        
#         chart.addSeries(series)
#         chart.setTitle("Top clients par nombre de véhicules")
        
#         axis_x = QBarCategoryAxis()
#         labels = [f"{getattr(c, 'prenom', '')} {getattr(c, 'nom', '')[:10]}" for c in top_clients]
#         axis_x.append(labels)
#         chart.addAxis(axis_x, Qt.AlignBottom)
#         series.attachAxis(axis_x)
        
#         axis_y = QValueAxis()
#         axis_y.setTitleText("Nombre de véhicules")
#         chart.addAxis(axis_y, Qt.AlignLeft)
#         series.attachAxis(axis_y)
        
#         if hasattr(self, 'top_chart'):
#             self.top_chart.setChart(chart)
#             self.top_chart.setRenderHint(QPainter.Antialiasing)
    
#     def load_dashboard_stats(self):
#         """Charge les statistiques du tableau de bord"""
#         async_query.execute(
#             self.controller.get_activity_report,
#             on_finished=self._update_dashboard_stats,
#             on_error=lambda e: logger.error(f"Erreur chargement stats: {e}")
#         )
    
#     def _update_dashboard_stats(self, data):
#         """Met à jour les cartes de statistiques"""
#         activity_data = data.get('data', {})
        
#         if 'contacts_count' in self.stats_cards:
#             self.stats_cards['contacts_count'].update_value(activity_data.get('new_contacts', 0))
    
#     def export_report(self, format_type, report_type):
#         """Exporte le rapport actuel"""
#         if not self.current_report_data:
#             QMessageBox.warning(self, "Aucune donnée", "Veuillez d'abord générer un rapport")
#             return
        
#         filename = f"rapport_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
        
#         if format_type == 'csv':
#             path, _ = QFileDialog.getSaveFileName(self, "Enregistrer le rapport", filename, "CSV (*.csv)")
#             if path:
#                 import csv
#                 with open(path, 'w', newline='', encoding='utf-8-sig') as f:
#                     writer = csv.writer(f)
#                     writer.writerow([f"Rapport généré le {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"])
#                     writer.writerow([])
                    
#                     # Headers
#                     if report_type == 'contacts' and 'data' in self.current_report_data:
#                         writer.writerow(["ID", "Nom", "Prénom", "Téléphone", "Email", "Type", "Statut"])
#                         for c in self.current_report_data['data'][:100]:
#                             writer.writerow([
#                                 c.id, c.nom or "", c.prenom or "", c.telephone or "",
#                                 c.email or "", c.type_client or "", c.vip_status or ""
#                             ])
                
#                 QMessageBox.information(self, "Succès", f"Rapport exporté: {path}")
        
#         elif format_type == 'pdf':
#             path, _ = QFileDialog.getSaveFileName(self, "Enregistrer le rapport", filename, "PDF (*.pdf)")
#             if path:
#                 try:
#                     self.controller.export_to_pdf(self.current_report_data, path)
#                     QMessageBox.information(self, "Succès", f"Rapport exporté: {path}")
#                 except Exception as e:
#                     QMessageBox.warning(self, "Erreur", f"Erreur lors de l'export PDF: {e}")
    
#     def export_global_report(self):
#         """Exporte un rapport global (toutes les catégories)"""
#         QMessageBox.information(self, "Export global", "Cette fonctionnalité sera disponible prochainement")
    
#     def send_report_email(self):
#         """Envoie le rapport par email"""
#         QMessageBox.information(self, "Envoi email", "Cette fonctionnalité sera disponible prochainement")
    
#     def show_dashboard(self):
#         """Affiche le tableau de bord des rapports"""
#         self.tab_widget.setCurrentIndex(0)
    
#     def schedule_report(self):
#         """Planifie l'envoi d'un rapport"""
#         QMessageBox.information(self, "Planification", "Cette fonctionnalité sera disponible prochainement")
    
#     def show_alerts(self):
#         """Affiche les alertes"""
#         QMessageBox.information(self, "Alertes", "Aucune nouvelle alerte")
    
#     def show_preferences(self):
#         """Affiche les préférences des rapports"""
#         QMessageBox.information(self, "Préférences", "Cette fonctionnalité sera disponible prochainement")
    
#     def on_quick_date_changed(self, text):
#         """Change la période des rapports selon la sélection rapide"""
#         today = QDate.currentDate()
        
#         if text == "Aujourd'hui":
#             start = today
#             end = today
#         elif text == "Cette semaine":
#             start = today.addDays(-today.dayOfWeek() + 1)
#             end = today
#         elif text == "Ce mois":
#             start = QDate(today.year(), today.month(), 1)
#             end = today
#         elif text == "Ce trimestre":
#             quarter = (today.month() - 1) // 3
#             start = QDate(today.year(), quarter * 3 + 1, 1)
#             end = today
#         elif text == "Cette année":
#             start = QDate(today.year(), 1, 1)
#             end = today
#         else:
#             return
        
#         # Mettre à jour tous les filtres de date
#         if hasattr(self, 'contacts_date_debut'):
#             self.contacts_date_debut.setDate(start)
#             self.contacts_date_fin.setDate(end)
#         if hasattr(self, 'vehicles_date_debut'):
#             self.vehicles_date_debut.setDate(start)
#             self.vehicles_date_fin.setDate(end)
#         if hasattr(self, 'financial_date_debut'):
#             self.financial_date_debut.setDate(start)
#             self.financial_date_fin.setDate(end)
    
#     def _show_error(self, error):
#         """Affiche une erreur"""
#         QMessageBox.warning(self, "Erreur", f"Erreur lors de la génération du rapport: {error}")
    
#     def setup_shortcuts(self):
#         """Configure les raccourcis clavier"""
#         from PySide6.QtGui import QAction, QKeySequence
        
#         refresh_action = QAction(self)
#         refresh_action.setShortcut(QKeySequence("Ctrl+R"))
#         refresh_action.triggered.connect(lambda: self.generate_report('contacts'))
#         self.addAction(refresh_action)
        
#         search_action = QAction(self)
#         search_action.setShortcut(QKeySequence("Ctrl+F"))
#         search_action.triggered.connect(lambda: self.search_report.setFocus())
#         self.addAction(search_action)

# addons/Automobiles/views/report_view.py
"""
Vue des rapports et statistiques
Design professionnel avec graphiques et analyses
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QComboBox, QDateEdit, QGroupBox, QGridLayout,
    QScrollArea, QProgressBar, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt, QDate, QDateTime, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtCharts import (
    QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis,
    QValueAxis, QLineSeries, QPieSeries, QPieSlice
)

from datetime import datetime, timedelta
from typing import Dict, Any, List

from addons.Automobiles.views.style import Colors, Fonts, Spacing
from addons.Automobiles.views.widgets.modern_card import ModernCard


class ReportView(QWidget):
    """Vue des rapports et statistiques"""
    
    def __init__(self, controller, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.activity_metrics = {}
        self.setup_ui()
        self.load_reports()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.LG)
        
        # En-tête avec filtres
        self.setup_filters()
        layout.addWidget(self.filters_card)
        
        # Zone scrollable pour les rapports
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(Spacing.XL)
        
        # Rapport d'activité
        self.setup_activity_report()
        content_layout.addWidget(self.activity_card)
        
        # Graphiques
        row1 = QHBoxLayout()
        row1.setSpacing(Spacing.XL)
        
        self.setup_contracts_chart()
        self.setup_revenue_chart()
        
        row1.addWidget(self.contracts_chart_card)
        row1.addWidget(self.revenue_chart_card)
        content_layout.addLayout(row1)
        
        # Top véhicules/conducteurs
        row2 = QHBoxLayout()
        row2.setSpacing(Spacing.XL)
        
        self.setup_top_vehicles()
        self.setup_top_clients()
        
        row2.addWidget(self.top_vehicles_card)
        row2.addWidget(self.top_clients_card)
        content_layout.addLayout(row2)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Barre de statut
        self.setup_status_bar()
        layout.addWidget(self.status_bar)
    
    def setup_filters(self):
        """Configure les filtres de rapport"""
        self.filters_card = ModernCard(title="Filtres du rapport", icon="🔍")
        
        filters_layout = QGridLayout()
        filters_layout.setSpacing(Spacing.MD)
        
        # Période
        filters_layout.addWidget(QLabel("Période:"), 0, 0)
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Ce mois", "Mois dernier", "Ce trimestre", "Cette année", "Personnalisé"])
        self.period_combo.currentTextChanged.connect(self.on_period_change)
        filters_layout.addWidget(self.period_combo, 0, 1)
        
        # Date début
        filters_layout.addWidget(QLabel("Du:"), 1, 0)
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.start_date.dateChanged.connect(self.on_date_change)
        filters_layout.addWidget(self.start_date, 1, 1)
        
        # Date fin
        filters_layout.addWidget(QLabel("Au:"), 2, 0)
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.dateChanged.connect(self.on_date_change)
        filters_layout.addWidget(self.end_date, 2, 1)
        
        # Bouton générer
        self.generate_btn = QPushButton("🔄 Générer le rapport")
        self.generate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.PRIMARY};
                border-radius: 10px;
                padding: 10px 20px;
            }}
        """)
        self.generate_btn.clicked.connect(self.generate_report)
        filters_layout.addWidget(self.generate_btn, 3, 0, 1, 2)
        
        self.filters_card.add_layout(filters_layout)
    
    def setup_activity_report(self):
        """Configure le rapport d'activité"""
        self.activity_card = ModernCard(title="Rapport d'activité", icon="📈")
        
        activity_layout = QGridLayout()
        activity_layout.setSpacing(Spacing.MD)
        
        # Métriques principales
        metrics = [
            ("📄 Nouveaux contrats", "0", Colors.PRIMARY),
            ("👥 Nouveaux clients", "0", Colors.SUCCESS),
            ("🚗 Nouveaux véhicules", "0", Colors.INFO),
            ("💰 Chiffre d'affaires", "0 XAF", Colors.WARNING)
        ]
        
        for i, (label, value, color) in enumerate(metrics):
            metric_widget = QWidget()
            metric_layout = QVBoxLayout(metric_widget)
            
            value_label = QLabel(value)
            value_label.setStyleSheet(f"""
                font-size: {Fonts.H2}px;
                font-weight: {Fonts.BOLD};
                color: {color};
            """)
            
            label_label = QLabel(label)
            label_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
            
            metric_layout.addWidget(value_label)
            metric_layout.addWidget(label_label)
            
            activity_layout.addWidget(metric_widget, i // 2, i % 2)
            self.activity_metrics[label] = value_label
        
        self.activity_card.add_layout(activity_layout)
    
    def setup_contracts_chart(self):
        """Configure le graphique des contrats"""
        self.contracts_chart_card = ModernCard(title="Évolution des contrats", icon="📊")
        
        self.contracts_chart_view = QChartView()
        self.contracts_chart_view.setMinimumHeight(300)
        self.contracts_chart_view.setRenderHint(QPainter.Antialiasing)
        
        self.contracts_chart = QChart()
        self.contracts_chart.setBackgroundVisible(False)
        self.contracts_chart_view.setChart(self.contracts_chart)
        
        self.contracts_chart_card.add_widget(self.contracts_chart_view)
    
    def setup_revenue_chart(self):
        """Configure le graphique des revenus"""
        self.revenue_chart_card = ModernCard(title="Revenus mensuels", icon="💰")
        
        self.revenue_chart_view = QChartView()
        self.revenue_chart_view.setMinimumHeight(300)
        self.revenue_chart_view.setRenderHint(QPainter.Antialiasing)
        
        self.revenue_chart = QChart()
        self.revenue_chart.setBackgroundVisible(False)
        self.revenue_chart_view.setChart(self.revenue_chart)
        
        self.revenue_chart_card.add_widget(self.revenue_chart_view)
    
    def setup_top_vehicles(self):
        """Configure le top des véhicules"""
        self.top_vehicles_card = ModernCard(title="Top 5 véhicules assurés", icon="🚗")
        
        self.top_vehicles_table = QTableWidget()
        self.top_vehicles_table.setColumnCount(3)
        self.top_vehicles_table.setHorizontalHeaderLabels(["Véhicule", "Contrats", "Prime totale"])
        self.top_vehicles_table.setAlternatingRowColors(True)
        
        self.top_vehicles_card.add_widget(self.top_vehicles_table)
    
    def setup_top_clients(self):
        """Configure le top des clients"""
        self.top_clients_card = ModernCard(title="Top 5 clients", icon="👥")
        
        self.top_clients_table = QTableWidget()
        self.top_clients_table.setColumnCount(3)
        self.top_clients_table.setHorizontalHeaderLabels(["Client", "Contrats", "Prime totale"])
        self.top_clients_table.setAlternatingRowColors(True)
        
        self.top_clients_card.add_widget(self.top_clients_table)
    
    def setup_status_bar(self):
        """Configure la barre de statut"""
        self.status_bar = QFrame()
        self.status_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.GRAY_50};
                border-radius: 10px;
            }}
        """)
        
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM)
        
        self.status_label = QLabel("Prêt")
        self.status_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setVisible(False)
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.progress_bar)
    
    def load_reports(self):
        """Charge les rapports initiaux"""
        self.generate_report()
    
    def generate_report(self):
        """Génère le rapport avec les filtres actuels"""
        self.status_label.setText("Génération du rapport...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        
        # Simuler un chargement
        import time
        from PySide6.QtCore import QTimer
        
        def process():
            try:
                # Récupérer les dates
                start = self.start_date.date().toPython()
                end = self.end_date.date().toPython()
                
                # Récupérer les données via le contrôleur
                if hasattr(self.controller, 'get_activity_report'):
                    data = self.controller.get_activity_report(start, end)
                    self.update_activity_report(data)
                
                # Mettre à jour les graphiques
                self.update_contracts_chart()
                self.update_revenue_chart()
                self.update_top_vehicles()
                self.update_top_clients()
                
                self.status_label.setText(f"Rapport généré: {start.strftime('%d/%m/%Y')} - {end.strftime('%d/%m/%Y')}")
                
            except Exception as e:
                self.status_label.setText(f"Erreur: {str(e)}")
                QMessageBox.warning(self, "Erreur", f"Erreur lors de la génération: {e}")
            finally:
                self.progress_bar.setVisible(False)
        
        # Animation de progression
        for i in range(101):
            QTimer.singleShot(i * 20, lambda v=i: self.progress_bar.setValue(v))
        
        QTimer.singleShot(2000, process)
    
    def update_activity_report(self, data: Dict[str, Any]):
        """Met à jour le rapport d'activité"""
        self.activity_metrics["📄 Nouveaux contrats"].setText(str(data.get('new_contracts', 0)))
        self.activity_metrics["👥 Nouveaux clients"].setText(str(data.get('new_contacts', 0)))
        self.activity_metrics["🚗 Nouveaux véhicules"].setText(str(data.get('new_vehicles', 0)))
        self.activity_metrics["💰 Chiffre d'affaires"].setText(f"XAF {data.get('total_premium', 0):,.0f}".replace(",", " "))
    
    # def update_contracts_chart(self):
    #     """Met à jour le graphique des contrats"""
    #     # Données simulées
    #     months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin"]
    #     values = [12, 15, 18, 22, 25, 30]
        
    #     series = QLineSeries()
    #     for i, (month, value) in enumerate(zip(months, values)):
    #         series.append(i, value)
        
    #     series.setColor(QColor(Colors.PRIMARY))
    #     series.setPen(QColor(Colors.PRIMARY), 2)
        
    #     self.contracts_chart.removeAllSeries()
    #     self.contracts_chart.addSeries(series)
        
    #     # Axe X
    #     axis_x = QBarCategoryAxis()
    #     axis_x.append(months)
    #     self.contracts_chart.addAxis(axis_x, Qt.AlignBottom)
    #     series.attachAxis(axis_x)
        
    #     # Axe Y
    #     axis_y = QValueAxis()
    #     axis_y.setRange(0, 50)
    #     axis_y.setTitleText("Nombre de contrats")
    #     self.contracts_chart.addAxis(axis_y, Qt.AlignLeft)
    #     series.attachAxis(axis_y)
        
    #     self.contracts_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
    
    def update_contracts_chart(self):
        """Met à jour le graphique des contrats"""
        months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin"]
        values = [12, 15, 18, 22, 25, 30]
        
        series = QLineSeries()
        for i, (month, value) in enumerate(zip(months, values)):
            series.append(i, value)
        
        # CORRECTION: setPen prend un seul argument QPen
        pen = QPen(QColor(Colors.PRIMARY))
        pen.setWidth(2)
        series.setPen(pen)
        
        self.contracts_chart.removeAllSeries()
        self.contracts_chart.addSeries(series)
        
        # Axe X
        axis_x = QBarCategoryAxis()
        axis_x.append(months)
        self.contracts_chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        # Axe Y
        axis_y = QValueAxis()
        axis_y.setRange(0, 50)
        axis_y.setTitleText("Nombre de contrats")
        self.contracts_chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        self.contracts_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

    def update_revenue_chart(self):
        """Met à jour le graphique des revenus"""
        months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin"]
        values = [500000, 650000, 720000, 890000, 950000, 1100000]
        
        bar_set = QBarSet("Revenus (XAF)")
        for value in values:
            bar_set.append(value)
        
        bar_set.setColor(QColor(Colors.SUCCESS))
        
        series = QBarSeries()
        series.append(bar_set)
        series.setBarWidth(0.6)
        
        self.revenue_chart.removeAllSeries()
        self.revenue_chart.addSeries(series)
        
        axis_x = QBarCategoryAxis()
        axis_x.append(months)
        self.revenue_chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, 1500000)
        axis_y.setTitleText("Revenus (XAF)")
        self.revenue_chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        self.revenue_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
    
    def update_top_vehicles(self):
        """Met à jour le top des véhicules"""
        data = [
            ("LS-123-AB", 3, 450000),
            ("LT-456-CD", 2, 320000),
            ("LE-789-EF", 2, 280000),
            ("LZ-012-GH", 1, 150000),
            ("LM-345-IJ", 1, 120000)
        ]
        
        self.top_vehicles_table.setRowCount(len(data))
        for row, (plate, count, premium) in enumerate(data):
            self.top_vehicles_table.setItem(row, 0, QTableWidgetItem(plate))
            self.top_vehicles_table.setItem(row, 1, QTableWidgetItem(str(count)))
            self.top_vehicles_table.setItem(row, 2, QTableWidgetItem(f"XAF {premium:,.0f}".replace(",", " ")))
        
        self.top_vehicles_table.resizeColumnsToContents()
    
    def update_top_clients(self):
        """Met à jour le top des clients"""
        data = [
            ("Jean Dupont", 3, 450000),
            ("Marie Camara", 2, 320000),
            ("Société ABC", 2, 280000),
            ("Paul FOTSO", 1, 150000),
            ("Entreprise XYZ", 1, 120000)
        ]
        
        self.top_clients_table.setRowCount(len(data))
        for row, (name, count, premium) in enumerate(data):
            self.top_clients_table.setItem(row, 0, QTableWidgetItem(name))
            self.top_clients_table.setItem(row, 1, QTableWidgetItem(str(count)))
            self.top_clients_table.setItem(row, 2, QTableWidgetItem(f"XAF {premium:,.0f}".replace(",", " ")))
        
        self.top_clients_table.resizeColumnsToContents()
    
    def on_period_change(self):
        """Change la période de rapport"""
        period = self.period_combo.currentText()
        today = QDate.currentDate()
        
        if period == "Ce mois":
            self.start_date.setDate(QDate(today.year(), today.month(), 1))
            self.end_date.setDate(today)
        elif period == "Mois dernier":
            last_month = today.addMonths(-1)
            self.start_date.setDate(QDate(last_month.year(), last_month.month(), 1))
            self.end_date.setDate(QDate(last_month.year(), last_month.month(), last_month.daysInMonth()))
        elif period == "Ce trimestre":
            quarter_month = ((today.month() - 1) // 3) * 3 + 1
            self.start_date.setDate(QDate(today.year(), quarter_month, 1))
            self.end_date.setDate(today)
        elif period == "Cette année":
            self.start_date.setDate(QDate(today.year(), 1, 1))
            self.end_date.setDate(today)
        
        self.generate_report()
    
    def on_date_change(self):
        """Change les dates personnalisées"""
        self.period_combo.setCurrentText("Personnalisé")
    
    def refresh_data(self):
        """Rafraîchit les données"""
        self.generate_report()