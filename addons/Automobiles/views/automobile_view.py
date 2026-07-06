# addons/Automobiles/views/automobile_view.py
"""
Vue Gestion du Parc & Flottes - Version améliorée
Design épuré avec couleurs douces et tableaux optimisés
"""

from PySide6.QtWidgets import (
    QDialog, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, 
    QHeaderView, QFileDialog, QLineEdit, QFrame, QTabWidget,
    QGraphicsDropShadowEffect, QComboBox, QDateEdit, QGroupBox,
    QGridLayout, QScrollArea, QMenu, QToolButton, QSplitter,
    QProgressBar, QStatusBar, QCheckBox, QSpinBox
)
from PySide6.QtCore import Qt, QTimer, QMargins, QSize, Signal, QMargins
from PySide6.QtGui import QColor, QFont, QPainter, QAction, QIcon
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis

from addons.Automobiles.views.audit_auto_view import AuditLogDialog
from addons.Automobiles.views.flotte_form_view import FleetForm
from addons.Automobiles.views.automobile_form_view import VehicleForm
from addons.Automobiles.views.vehicle_detail_view import VehicleDetailView
from core.logger import logger
from core.workers.database_worker import async_query
from core.workers.workers_base import async_executor
from core.workers.loading_widget import LoadingOverlay
from core.widgets.global_loader import get_global_loader

import os
from datetime import datetime, timedelta


class VehiculeModuleView(QWidget):
    """Vue améliorée pour la gestion du parc et des flottes"""
    
    vehicle_updated = Signal()
    fleet_updated = Signal()
    
    def __init__(self, controller, current_user):
        super().__init__()
        self.controller = controller
        self.session = getattr(controller, 'session', controller)
        self.current_user = current_user
        self._current_filter = "all"
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._apply_search)
        
        # Style moderne avec couleurs douces
        self.table_style = """
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #e8edf2;
                border-radius: 10px;
                gridline-color: transparent;
                alternate-background-color: #fafbfc;
                font-size: 13px;
                padding: 0px;
            }
            QHeaderView::section {
                background-color: #f5f7fa;
                padding: 14px 12px;
                border: none;
                border-bottom: 1px solid #e8edf2;
                font-weight: 600;
                font-size: 11px;
                color: #5a6a7a;
                text-transform: uppercase;
                letter-spacing: 0.3px;
            }
            QTableWidget::item {
                border-bottom: 1px solid #f0f2f5;
                padding: 14px 8px;
                color: #2d3748;
            }
            QTableWidget::item:selected {
                background-color: #ebf4ff;
                color: #2d3748;
            }
            QTableWidget::item:hover {
                background-color: #f7fafc;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f2f5;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0aec0;
            }
        """
        
        self.loading_overlay = LoadingOverlay(self)
        self.setup_ui()
        
        # Chargement initial
        self.load_vehicles_async()
        self.load_fleets_async()
        self.load_dashboard_stats()

    def setup_ui(self):
        """Configure l'interface utilisateur"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setStyleSheet("background: #f7f9fc;")
        
        # En-tête épuré
        self._create_header()
        
        # Barre d'outils
        self._create_toolbar()
        
        # Contenu
        self._create_content()
        
        # Barre de statut
        self._create_status_bar()
    
    def _create_header(self):
        """Crée un en-tête épuré"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: #ffffff;
                padding: 12px 24px;
                border-bottom: 1px solid #e8edf2;
            }
        """)
        header.setMinimumHeight(70)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Titre
        title = QLabel("🚗 Gestion du Parc & Flottes")
        title.setStyleSheet("""
            color: #1a202c;
            font-size: 20px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        
        # Statistiques
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.total_vehicles_label = self._create_stat_label("🚗", "0", "Véhicules")
        self.active_vehicles_label = self._create_stat_label("✅", "0", "Actifs")
        self.total_fleets_label = self._create_stat_label("📁", "0", "Flottes")
        
        stats_layout.addWidget(self.total_vehicles_label)
        stats_layout.addWidget(self.active_vehicles_label)
        stats_layout.addWidget(self.total_fleets_label)
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addLayout(stats_layout)
        
        self.main_layout.addWidget(header)
    
    def _create_stat_label(self, icon, count, label):
        """Crée une étiquette de statistique"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
                padding: 4px 8px;
            }
        """)
        
        layout = QHBoxLayout(container)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 14px; background: transparent; border: none;")
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
        
        count_label = QLabel(count)
        count_label.setStyleSheet("""
            color: #2d3748;
            font-size: 16px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        count_label.setObjectName(f"header_{label.lower()}")
        
        name_label = QLabel(label)
        name_label.setStyleSheet("""
            color: #718096;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            background: transparent;
            border: none;
        """)
        
        text_layout.addWidget(count_label)
        text_layout.addWidget(name_label)
        
        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        
        return container
    
    def _create_toolbar(self):
        """Crée la barre d'outils"""
        toolbar = QFrame()
        toolbar.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border-bottom: 1px solid #e8edf2;
                padding: 8px 24px;
            }
        """)
        
        layout = QHBoxLayout(toolbar)
        layout.setSpacing(10)
        
        # Boutons d'action
        self.btn_add_vehicle = QPushButton("➕ Ajouter Véhicule")
        self.btn_add_vehicle.setStyleSheet("""
            QPushButton {
                background: #48bb78;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 18px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #38a169;
            }
        """)
        self.btn_add_vehicle.clicked.connect(self.on_add_vehicle_click)
        
        self.btn_add_fleet = QPushButton("📁 Nouvelle Flotte")
        self.btn_add_fleet.setStyleSheet("""
            QPushButton {
                background: #4299e1;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 18px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #3182ce;
            }
        """)
        self.btn_add_fleet.clicked.connect(self.on_add_fleet_click)
        
        self.btn_audit = QPushButton("📋 Audit")
        self.btn_audit.setStyleSheet("""
            QPushButton {
                background: #9f7aea;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 18px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #805ad5;
            }
        """)
        self.btn_audit.clicked.connect(self.on_audit_clicked)
        
        layout.addWidget(self.btn_add_vehicle)
        layout.addWidget(self.btn_add_fleet)
        layout.addWidget(self.btn_audit)
        
        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("background: #e8edf2; max-width: 1px;")
        sep.setFixedWidth(1)
        layout.addWidget(sep)
        
        # Filtre
        layout.addWidget(QLabel("Filtre:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Tous", "Actifs", "Inactifs", "En maintenance"])
        self.filter_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 6px 12px;
                background: #f7fafc;
                min-width: 120px;
                color: #2d3748;
            }
            QComboBox:hover {
                border-color: #cbd5e0;
            }
        """)
        self.filter_combo.currentTextChanged.connect(self._on_filter_changed)
        layout.addWidget(self.filter_combo)
        
        layout.addStretch()
        
        # Recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher...")
        self.search_input.setMinimumWidth(250)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px 14px;
                background: #f7fafc;
                color: #2d3748;
            }
            QLineEdit:focus {
                border-color: #4299e1;
                background: #ffffff;
            }
        """)
        self.search_input.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_input)
        
        # Export
        self.btn_export = QPushButton("📤 Export")
        self.btn_export.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
                color: #4a5568;
            }
            QPushButton:hover {
                background: #f7fafc;
            }
        """)
        self.btn_export.clicked.connect(self._show_export_menu)
        layout.addWidget(self.btn_export)
        
        self.main_layout.addWidget(toolbar)
    
    def _create_content(self):
        """Crée le contenu principal"""
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { 
                border: 1px solid #e8edf2; 
                background: #f7f9fc; 
                border-radius: 0px 0px 10px 10px;
            }
            QTabBar::tab {
                background: #edf2f7;
                color: #4a5568;
                padding: 10px 22px;
                border: 1px solid #e8edf2;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
                font-weight: 600;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                color: #2d3748;
                border-bottom-color: #ffffff;
            }
            QTabBar::tab:hover:!selected {
                background: #e2e8f0;
            }
        """)
        
        # Onglet Parc Automobile
        self.tab_vehicules = QWidget()
        self._setup_tab_vehicules()
        
        # Onglet Flottes
        self.tab_flottes = QWidget()
        self._setup_tab_flottes()
        
        # Onglet Statistiques
        self.tab_stats = QWidget()
        self._setup_tab_stats()
        
        self.tabs.addTab(self.tab_vehicules, "🚗 Parc Automobile")
        self.tabs.addTab(self.tab_flottes, "🏢 Gestion des Flottes")
        self.tabs.addTab(self.tab_stats, "📊 Statistiques")
        
        self.main_layout.addWidget(self.tabs)
    
    def _setup_tab_vehicules(self):
        """Configure l'onglet des véhicules"""
        layout = QVBoxLayout(self.tab_vehicules)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        self.table_vehicules = QTableWidget(0, 7)
        self.table_vehicules.setHorizontalHeaderLabels([
            "Plaque", "Marque", "Propriétaire", "Prime Émise", 
            "Valeur Neuve", "Valeur Vénale", "Actions"
        ])
        self.table_vehicules.setStyleSheet(self.table_style)
        self.table_vehicules.horizontalHeader().setStretchLastSection(False)
        self.table_vehicules.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_vehicules.verticalHeader().setDefaultSectionSize(60)
        self.table_vehicules.setMinimumHeight(400)
        
        layout.addWidget(self.table_vehicules)
    
    def _setup_tab_flottes(self):
        """Configure l'onglet des flottes"""
        layout = QVBoxLayout(self.tab_flottes)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        self.table_flottes = QTableWidget(0, 7)
        self.table_flottes.setHorizontalHeaderLabels([
            "Code", "Nom Flotte", "Propriétaire", "Type Gestion", 
            "Remise (%)", "Date Création", "Actions"
        ])
        self.table_flottes.setStyleSheet(self.table_style)
        self.table_flottes.horizontalHeader().setStretchLastSection(False)
        self.table_flottes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_flottes.verticalHeader().setDefaultSectionSize(60)
        self.table_flottes.setMinimumHeight(400)
        
        layout.addWidget(self.table_flottes)
    
    def _setup_tab_stats(self):
        """Configure l'onglet des statistiques"""
        layout = QVBoxLayout(self.tab_stats)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(16)
        
        # Grille de stats
        stats_grid = QGridLayout()
        stats_grid.setSpacing(12)
        
        stats_data = [
            ("total_vehicles", "🚗", "Total Véhicules", "0", "#4299e1"),
            ("active_vehicles", "✅", "Véhicules Actifs", "0", "#48bb78"),
            ("total_contracts", "📄", "Contrats", "0", "#9f7aea"),
            ("total_clients", "👥", "Clients", "0", "#ed8936"),
        ]
        
        self.stat_cards = {}
        for i, (key, icon, title, value, color) in enumerate(stats_data):
            card = self._create_stat_card(icon, title, value, color)
            stats_grid.addWidget(card, i // 2, i % 2)
            self.stat_cards[key] = card
        
        content_layout.addLayout(stats_grid)
        
        # Graphiques
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(16)
        
        self.status_chart = self._create_status_chart()
        charts_layout.addWidget(self.status_chart, 1)
        
        self.brand_chart = self._create_brand_chart()
        charts_layout.addWidget(self.brand_chart, 1)
        
        content_layout.addLayout(charts_layout)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
    
    def _create_stat_card(self, icon, title, value, color):
        """Crée une carte de statistique"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {color}08;
                border: 1px solid {color}20;
                border-radius: 10px;
                padding: 14px;
            }}
        """)
        
        layout = QHBoxLayout(card)
        layout.setSpacing(14)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 28px; background: transparent; border: none;")
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 700;
            color: {color};
            background: transparent;
            border: none;
        """)
        value_label.setObjectName(f"stat_{title.lower().replace(' ', '_')}")
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 12px;
            color: #718096;
            background: transparent;
            border: none;
        """)
        
        text_layout.addWidget(value_label)
        text_layout.addWidget(title_label)
        
        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        layout.addStretch()
        
        return card
    
    def _create_status_chart(self):
        """Crée un graphique des statuts"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border-radius: 10px;
                border: 1px solid #e8edf2;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        title = QLabel("📊 Statut des véhicules")
        title.setStyleSheet("""
            font-weight: 600;
            font-size: 14px;
            color: #2d3748;
            background: transparent;
            border: none;
        """)
        layout.addWidget(title)
        
        # Graphique à barres horizontal
        series = QBarSeries()
        
        bar_set = QBarSet("Statut")
        bar_set.append([80, 15, 5])
        bar_set.setColor(QColor("#4299e1"))
        
        series.append(bar_set)
        series.setBarWidth(0.6)
        
        chart = QChart()
        chart.addSeries(series)
        chart.setBackgroundVisible(False)
        
        axis_x = QBarCategoryAxis()
        axis_x.append(["Actifs", "Maintenance", "Inactifs"])
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, 100)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        chart.legend().setVisible(False)
        chart.setMargins(QMargins(5, 5, 5, 5))
        
        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)
        view.setStyleSheet("background: transparent; border: none;")
        view.setMinimumHeight(180)
        
        layout.addWidget(view)
        
        return card
    
    def _create_brand_chart(self):
        """Crée un graphique des marques"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border-radius: 10px;
                border: 1px solid #e8edf2;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        title = QLabel("🏷️ Marques principales")
        title.setStyleSheet("""
            font-weight: 600;
            font-size: 14px;
            color: #2d3748;
            background: transparent;
            border: none;
        """)
        layout.addWidget(title)
        
        # Camembert des marques
        series = QPieSeries()
        series.append("Toyota", 25)
        series.append("Renault", 20)
        series.append("Peugeot", 18)
        series.append("Mercedes", 15)
        series.append("Autres", 22)
        
        colors = ["#4299e1", "#48bb78", "#ed8936", "#9f7aea", "#a0aec0"]
        for i, slice in enumerate(series.slices()):
            slice.setColor(QColor(colors[i % len(colors)]))
            slice.setLabelVisible(True)
            slice.setLabel(f"{slice.value()}%")
        
        chart = QChart()
        chart.addSeries(series)
        chart.setBackgroundVisible(False)
        chart.legend().setAlignment(Qt.AlignBottom)
        chart.setMargins(QMargins(5, 5, 5, 5))
        
        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)
        view.setStyleSheet("background: transparent; border: none;")
        view.setMinimumHeight(180)
        
        layout.addWidget(view)
        
        return card
    
    def _create_status_bar(self):
        """Crée une barre de statut"""
        status_bar = QFrame()
        status_bar.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border-top: 1px solid #e8edf2;
                padding: 6px 24px;
            }
        """)
        
        layout = QHBoxLayout(status_bar)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.status_label = QLabel("✅ Prêt")
        self.status_label.setStyleSheet("""
            color: #718096;
            font-size: 13px;
            background: transparent;
            border: none;
        """)
        
        self.last_update_label = QLabel(f"Dernière mise à jour: {datetime.now().strftime('%H:%M:%S')}")
        self.last_update_label.setStyleSheet("""
            color: #a0aec0;
            font-size: 11px;
            background: transparent;
            border: none;
        """)
        
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.last_update_label)
        
        self.main_layout.addWidget(status_bar)
    
    def _create_fleet_actions_menu(self, fleet):
        """Crée un menu d'actions pour les flottes"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: white;
                border: 1px solid #e8edf2;
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
        
        view_action = QAction("👁️ Voir détails", self)
        view_action.triggered.connect(lambda: self.handle_fleet_action(fleet, "view"))
        menu.addAction(view_action)
        
        edit_action = QAction("✏️ Modifier", self)
        edit_action.triggered.connect(lambda: self.handle_fleet_action(fleet, "edit"))
        menu.addAction(edit_action)
        
        print_action = QAction("📄 Imprimer état", self)
        print_action.triggered.connect(lambda: self.on_print_fleet_click(fleet))
        menu.addAction(print_action)
        
        return menu
    
    def _show_export_menu(self):
        """Affiche le menu d'export"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: white;
                border: 1px solid #e8edf2;
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
        
        export_csv = QAction("📄 Exporter en CSV", self)
        export_csv.triggered.connect(lambda: self._export_data("csv"))
        menu.addAction(export_csv)
        
        export_excel = QAction("📊 Exporter en Excel", self)
        export_excel.triggered.connect(lambda: self._export_data("excel"))
        menu.addAction(export_excel)
        
        export_pdf = QAction("📑 Exporter en PDF", self)
        export_pdf.triggered.connect(lambda: self._export_data("pdf"))
        menu.addAction(export_pdf)
        
        menu.exec_(self.btn_export.mapToGlobal(self.btn_export.rect().bottomLeft()))
    
    def _export_data(self, format_type):
        """Exporte les données"""
        try:
            path, _ = QFileDialog.getSaveFileName(
                self,
                f"Exporter les données ({format_type.upper()})",
                f"parc_auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}",
                f"{format_type.upper()} (*.{format_type})"
            )
            
            if path:
                QMessageBox.information(self, "Succès", f"Données exportées vers {path}")
                
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur d'export: {e}")
    
    def _on_filter_changed(self, filter_text):
        """Gère le changement de filtre"""
        self._current_filter = filter_text.lower()
        self._apply_search()
    
    def _on_search_changed(self):
        """Gère le changement de recherche"""
        self._search_timer.stop()
        self._search_timer.start(300)
    
    def _apply_search(self):
        """Applique la recherche et les filtres"""
        search_text = self.search_input.text().lower()
        filter_text = self._current_filter
        
        for row in range(self.table_vehicules.rowCount()):
            show = True
            
            if filter_text != "tous":
                status_item = self.table_vehicules.item(row, 4)
                if status_item:
                    status = status_item.text().lower()
                    if filter_text == "actifs" and status != "actif":
                        show = False
                    elif filter_text == "inactifs" and status != "inactif":
                        show = False
                    elif filter_text == "en maintenance" and status != "en maintenance":
                        show = False
            
            if show and search_text:
                match = False
                for col in range(self.table_vehicules.columnCount() - 1):
                    item = self.table_vehicules.item(row, col)
                    if item and search_text in item.text().lower():
                        match = True
                        break
                show = match
            
            self.table_vehicules.setRowHidden(row, not show)
    
    # ========================================================================
    # MÉTHODES DE CHARGEMENT
    # ========================================================================
    
    def load_vehicles_async(self):
        """Charge les véhicules"""
        async_query.execute(
            self.controller.vehicles.get_all_vehicles,
            on_finished=self._on_vehicles_loaded,
            on_error=self._on_load_error,
            show_loader=True,
            loader_message="Chargement des véhicules..."
        )
    
    def _on_vehicles_loaded(self, vehicles):
        """Callback après chargement des véhicules"""
        self._display_vehicles(vehicles)
        self._update_stats(vehicles)
        self.last_update_label.setText(f"Dernière mise à jour: {datetime.now().strftime('%H:%M:%S')}")
    
    def _display_vehicles(self, vehicles):
        """Affiche les véhicules"""
        self.table_vehicules.setRowCount(0)
        
        for row_idx, vehicle in enumerate(vehicles):
            self.table_vehicules.insertRow(row_idx)
            
            self.table_vehicules.setItem(row_idx, 0, QTableWidgetItem(str(vehicle.immatriculation)))
            self.table_vehicules.setItem(row_idx, 1, QTableWidgetItem(str(vehicle.marque)))
            
            owner_name = vehicle.owner.nom if vehicle.owner else "N/A"
            self.table_vehicules.setItem(row_idx, 2, QTableWidgetItem(owner_name))
            
            price = getattr(vehicle, 'prime_emise', 0) or 0
            self.table_vehicules.setItem(row_idx, 3, QTableWidgetItem(f"{price:,.0f} FCFA".replace(",", " ")))
            
            valeur_neuf = getattr(vehicle, 'valeur_neuf', 0) or 0
            self.table_vehicules.setItem(row_idx, 4, QTableWidgetItem(f"{valeur_neuf:,.0f}".replace(",", " ")))
            
            valeur_venale = getattr(vehicle, 'valeur_venale', 0) or 0
            self.table_vehicules.setItem(row_idx, 5, QTableWidgetItem(f"{valeur_venale:,.0f}".replace(",", " ")))
            
            self._set_vehicle_actions(row_idx, vehicle)
        
        self.table_vehicules.resizeColumnsToContents()
        self._apply_search()
    
    def _set_vehicle_actions(self, row, vehicle):
        """Crée les boutons d'action"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)
        
        # Bouton Voir
        view_btn = QPushButton("👁️")
        view_btn.setFixedSize(32, 32)
        view_btn.setToolTip("Voir les détails")
        view_btn.setStyleSheet("""
            QPushButton {
                background: #ebf4ff;
                border-radius: 6px;
                font-size: 13px;
                border: none;
                color: #2d3748;
            }
            QPushButton:hover {
                background: #4299e1;
                color: white;
            }
        """)
        view_btn.clicked.connect(lambda: self.show_detail_vehicle(vehicle))
        
        # Bouton Modifier
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(32, 32)
        edit_btn.setToolTip("Modifier")
        edit_btn.setStyleSheet("""
            QPushButton {
                background: #fefcbf;
                border-radius: 6px;
                font-size: 13px;
                border: none;
                color: #2d3748;
            }
            QPushButton:hover {
                background: #ecc94b;
                color: white;
            }
        """)
        edit_btn.clicked.connect(lambda: self.on_edit_vehicle(vehicle))
        
        # Bouton Supprimer
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(32, 32)
        delete_btn.setToolTip("Archiver")
        delete_btn.setStyleSheet("""
            QPushButton {
                background: #fed7d7;
                border-radius: 6px;
                font-size: 13px;
                border: none;
                color: #2d3748;
            }
            QPushButton:hover {
                background: #fc8181;
                color: white;
            }
        """)
        delete_btn.clicked.connect(lambda: self.on_delete_vehicle(vehicle))
        
        layout.addWidget(view_btn)
        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        
        self.table_vehicules.setCellWidget(row, 6, container)
    
    def load_fleets_async(self):
        """Charge les flottes"""
        async_query.execute(
            self.controller.fleets.get_all_fleets,
            on_finished=self._on_fleets_loaded,
            on_error=self._on_load_error,
            show_loader=True,
            loader_message="Chargement des flottes..."
        )
    
    def _on_fleets_loaded(self, fleets):
        """Callback après chargement des flottes"""
        self._display_fleets(fleets)
    
    def _display_fleets(self, fleets):
        """Affiche les flottes"""
        self.table_flottes.setRowCount(0)
        
        for row, fleet in enumerate(fleets):
            self.table_flottes.insertRow(row)
            
            self.table_flottes.setItem(row, 0, QTableWidgetItem(str(fleet.code_flotte or "")))
            self.table_flottes.setItem(row, 1, QTableWidgetItem(str(fleet.nom_flotte or "")))
            
            owner_name = fleet.owner.nom if fleet.owner else "N/A"
            self.table_flottes.setItem(row, 2, QTableWidgetItem(owner_name))
            
            self.table_flottes.setItem(row, 3, QTableWidgetItem(str(fleet.type_gestion or "")))
            
            remise = f"{fleet.remise_flotte}%" if fleet.remise_flotte else "0%"
            self.table_flottes.setItem(row, 4, QTableWidgetItem(remise))
            
            date_str = fleet.created_at.strftime("%d/%m/%Y") if fleet.created_at else "---"
            self.table_flottes.setItem(row, 5, QTableWidgetItem(date_str))
            
            self._set_fleet_actions(row, fleet)
        
        self.table_flottes.resizeColumnsToContents()
    
    def _set_fleet_actions(self, row, fleet):
        """Crée les boutons d'action pour une flotte"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)
        
        # Bouton Voir
        view_btn = QPushButton("👁️")
        view_btn.setFixedSize(32, 32)
        view_btn.setToolTip("Voir les détails")
        view_btn.setStyleSheet("""
            QPushButton {
                background: #ebf4ff;
                border-radius: 6px;
                font-size: 13px;
                border: none;
                color: #2d3748;
            }
            QPushButton:hover {
                background: #4299e1;
                color: white;
            }
        """)
        view_btn.clicked.connect(lambda: self.handle_fleet_action(fleet, "view"))
        
        # Bouton Modifier
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(32, 32)
        edit_btn.setToolTip("Modifier")
        edit_btn.setStyleSheet("""
            QPushButton {
                background: #fefcbf;
                border-radius: 6px;
                font-size: 13px;
                border: none;
                color: #2d3748;
            }
            QPushButton:hover {
                background: #ecc94b;
                color: white;
            }
        """)
        edit_btn.clicked.connect(lambda: self.handle_fleet_action(fleet, "edit"))
        
        # Bouton Imprimer
        print_btn = QPushButton("📄")
        print_btn.setFixedSize(32, 32)
        print_btn.setToolTip("Imprimer l'état")
        print_btn.setStyleSheet("""
            QPushButton {
                background: #c6f6d5;
                border-radius: 6px;
                font-size: 13px;
                border: none;
                color: #2d3748;
            }
            QPushButton:hover {
                background: #48bb78;
                color: white;
            }
        """)
        print_btn.clicked.connect(lambda: self.on_print_fleet_click(fleet))
        
        # Bouton Plus
        more_btn = QPushButton("⋯")
        more_btn.setFixedSize(32, 32)
        more_btn.setToolTip("Plus d'actions")
        more_btn.setStyleSheet("""
            QPushButton {
                background: #edf2f7;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
                border: none;
                color: #2d3748;
            }
            QPushButton:hover {
                background: #a0aec0;
                color: white;
            }
        """)
        more_btn.clicked.connect(lambda: self._show_fleet_menu(fleet, more_btn))
        
        layout.addWidget(view_btn)
        layout.addWidget(edit_btn)
        layout.addWidget(print_btn)
        layout.addWidget(more_btn)
        
        self.table_flottes.setCellWidget(row, 6, container)
    
    def _show_fleet_menu(self, fleet, button):
        """Affiche le menu contextuel"""
        menu = self._create_fleet_actions_menu(fleet)
        menu.exec_(button.mapToGlobal(button.rect().bottomLeft()))
    
    def _update_stats(self, vehicles):
        """Met à jour les statistiques"""
        total = len(vehicles)
        active = sum(1 for v in vehicles if getattr(v, 'statut', '') == 'ACTIF')
        
        for label in self.findChildren(QLabel):
            if label.objectName() == "header_véhicules":
                label.setText(str(total))
            elif label.objectName() == "header_actifs":
                label.setText(str(active))
    
    def _on_load_error(self, error):
        """Gère les erreurs de chargement"""
        QMessageBox.warning(self, "Erreur", f"Erreur de chargement: {error}")
    
    def load_dashboard_stats(self):
        """Charge les statistiques"""
        try:
            if hasattr(self.controller, 'vehicles'):
                stats = self.controller.vehicles.get_vehicle_stats()
                self._update_dashboard_stats(stats)
        except Exception as e:
            logger.error(f"Erreur chargement stats: {e}")
    
    def _update_dashboard_stats(self, stats):
        """Met à jour les statistiques"""
        try:
            if "total_vehicles" in self.stat_cards:
                self._update_stat_card("total_vehicles", stats.get('total', 0))
            if "active_vehicles" in self.stat_cards:
                self._update_stat_card("active_vehicles", stats.get('active', 0))
        except Exception as e:
            logger.error(f"Erreur mise à jour stats: {e}")
    
    def _update_stat_card(self, key, value):
        """Met à jour une carte statistique"""
        if key in self.stat_cards:
            card = self.stat_cards[key]
            for label in card.findChildren(QLabel):
                if label.objectName().startswith("stat_"):
                    label.setText(str(value))
                    break
    
    # ========================================================================
    # ACTIONS
    # ========================================================================
    
    def on_add_vehicle_click(self):
        """Ajout d'un véhicule"""
        contacts = self.controller.fleets.get_all_contacts_for_combo()
        dialog = VehicleForm(
            controller=self.controller,
            contacts_list=contacts,
            current_user=getattr(self, 'current_user', None),
            mode="add"
        )
        if dialog.exec():
            self.load_vehicles_async()
    
    def on_add_fleet_click(self):
        """Ajout d'une flotte"""
        contacts = self.controller.fleets.get_all_contacts_for_combo()
        compagnies = self.controller.fleets.get_all_compagnies_for_combo()
        
        dialog = FleetForm(
            controller=self.controller,
            current_fleet=None,
            mode="add",
            contacts_list=contacts,
            compagnies_list=compagnies
        )
        if dialog.exec():
            self.load_fleets_async()
    
    def handle_fleet_action(self, fleet, mode):
        """Gère les actions sur les flottes"""
        if not fleet:
            return
        
        contacts = self.controller.fleets.get_all_contacts_for_combo()
        compagnies = self.controller.fleets.get_all_compagnies_for_combo()
        
        dialog = FleetForm(
            controller=self.controller,
            current_fleet=fleet,
            mode=mode,
            contacts_list=contacts,
            compagnies_list=compagnies
        )
        
        if dialog.exec():
            self.load_fleets_async()
    
    def on_print_fleet_click(self, fleet):
        """Imprime l'état d'une flotte"""
        if not fleet:
            return
        
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer l'État de Couverture de Flotte",
            f"ETAT_COUVERTURE_{fleet.nom_flotte}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            "Documents PDF (*.pdf)"
        )
        
        if path:
            QMessageBox.information(self, "Succès", f"PDF généré: {path}")
    
    def on_audit_clicked(self):
        """Ouvre le journal d'audit"""
        dialog = AuditLogDialog(controller=self.controller.vehicles, parent=self)
        dialog.exec()
    
    def on_edit_vehicle(self, vehicle):
        """Modifie un véhicule"""
        from core.widgets.global_loader import get_global_loader
        loader = get_global_loader()
        loader.show_loading("Chargement du véhicule...")
        
        def load_vehicle():
            from core.database import SessionLocal
            session = SessionLocal()
            try:
                from addons.Automobiles.controllers.automobile_controller import VehicleController
                vehicle_ctrl = VehicleController(session)
                return vehicle_ctrl.get_vehicle_with_relations(vehicle.id)
            finally:
                session.close()
        
        def on_loaded(vehicle_with_relations):
            loader.hide_loading()
            if not vehicle_with_relations:
                QMessageBox.warning(self, "Erreur", "Impossible de charger le véhicule.")
                return
            
            dialog = VehicleForm(
                controller=self.controller,
                vehicle_to_edit=vehicle_with_relations,
                current_user=getattr(self, 'current_user', None),
                mode="edit"
            )
            if dialog.exec():
                self.load_vehicles_async()
        
        async_query.execute(
            load_vehicle,
            on_finished=on_loaded,
            on_error=self._on_load_error,
            show_loader=False
        )
    
    def on_delete_vehicle(self, vehicle):
        """Supprime un véhicule"""
        confirm = QMessageBox.question(
            self, "Confirmation",
            f"Souhaitez-vous vraiment archiver le véhicule {vehicle.immatriculation} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            get_global_loader().show_loading("Archivage en cours...")
            
            def delete():
                user_id = getattr(self.current_user, 'id', 1)
                return self.controller.vehicles.deactivate_vehicle(vehicle.id, user_id)
            
            async_query.execute(
                delete,
                on_finished=lambda result: self._on_delete_finished(result, vehicle),
                on_error=self._on_load_error
            )
    
    def _on_delete_finished(self, result, vehicle):
        """Callback après suppression"""
        get_global_loader().hide_loading()
        success, message = result
        if success:
            QMessageBox.information(self, "Succès", f"Véhicule {vehicle.immatriculation} archivé")
            self.load_vehicles_async()
        else:
            QMessageBox.critical(self, "Erreur", message)
    
    def show_detail_vehicle(self, vehicle):
        """Affiche les détails d'un véhicule"""
        get_global_loader().show_loading("Chargement des détails...")
        
        def load_details():
            from core.database import SessionLocal
            session = SessionLocal()
            try:
                from addons.Automobiles.controllers.automobile_controller import VehicleController
                vehicle_ctrl = VehicleController(session)
                # print(f'voici les informations sur le véhicule: {vehicle_ctrl.get_vehicle_details_data(vehicle.id)}')
                return vehicle_ctrl.get_vehicle_details_data(vehicle.id)
            finally:
                session.close()
        
        def on_loaded(data):
            get_global_loader().hide_loading()
            if not data:
                QMessageBox.warning(self, "Erreur", "Impossible de charger les détails.")
                return
            
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Fiche Véhicule : {data['immatriculation']}")
            dialog.setMinimumSize(950, 750)
            
            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(0, 0, 0, 0)
            
            detail_view = VehicleDetailView(vehicle_data=data, controller=self.controller)
            layout.addWidget(detail_view)
            
            if hasattr(detail_view, 'btn_back'):
                detail_view.btn_back.clicked.connect(dialog.close)
            
            dialog.exec()
        
        async_query.execute(
            load_details,
            on_finished=on_loaded,
            on_error=self._on_load_error,
            show_loader=False
        )
    
    def refresh_data(self):
        """Rafraîchit toutes les données"""
        self.load_vehicles_async()
        self.load_fleets_async()
        self.load_dashboard_stats()
    
    def closeEvent(self, event):
        """Nettoie les ressources"""
        self._search_timer.stop()
        super().closeEvent(event)