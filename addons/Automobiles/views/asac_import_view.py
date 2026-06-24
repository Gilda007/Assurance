# addons/Automobiles/views/asac_import_view.py
# Version avec QTabWidget pour organiser les sections

"""
Interface d'export ASAC en masse - Avec organisation en onglets
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QFileDialog, QMessageBox, QGroupBox,
    QGridLayout, QCheckBox, QComboBox, QLineEdit,
    QTextEdit, QTabWidget, QScrollArea, QSplitter,
    QDialog, QDateEdit, QFormLayout, QSizePolicy,
    QTreeWidget, QTreeWidgetItem
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QDateTime, QSettings
from PySide6.QtGui import QColor, QFont, QTextCursor, QPalette

from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import time
import requests

from addons.Automobiles.views.style import Colors, Fonts, Spacing
from addons.Automobiles.views.widgets.modern_card import ModernCard
from addons.Automobiles.views.asac_manager import ExportWorker, ConfigDialog


class ASACImportView(QWidget):
    """Vue d'export ASAC en masse - Organisation en onglets"""
    
    def __init__(self, controller, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.vehicles_data = []
        self.fleets_data = []
        self.contacts_data = []
        self.export_worker = None
        self.export_results = []
        self.settings = QSettings("LOMETA", "ASAC")
        self.selected_vehicles = []
        self._updating_selection = False
        self.export_logs = []
        
        self.setup_ui()
        self.load_config()
        self.load_all_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.LG)
        
        # En-tête
        header = self._create_header()
        layout.addWidget(header)
        
        # Barre d'outils
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)
        
        # Onglets principaux
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                background: white;
            }
            QTabBar::tab {
                padding: 12px 24px;
                margin-right: 4px;
                font-weight: 600;
                font-size: 13px;
                border-radius: 8px 8px 0 0;
            }
            QTabBar::tab:selected {
                background: #2563eb;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: #f1f5f9;
            }
        """)
        
        # Onglet 1: Véhicules
        vehicles_tab = self._create_vehicles_tab()
        self.tab_widget.addTab(vehicles_tab, "🚗 Véhicules")
        
        # Onglet 2: Flottes
        fleets_tab = self._create_fleets_tab()
        self.tab_widget.addTab(fleets_tab, "🏢 Flottes")
        
        # Onglet 3: Contacts
        contacts_tab = self._create_contacts_tab()
        self.tab_widget.addTab(contacts_tab, "👤 Contacts")
        
        # Onglet 4: Logs
        logs_tab = self._create_logs_tab()
        self.tab_widget.addTab(logs_tab, "📝 Logs")
        
        layout.addWidget(self.tab_widget, 1)
        
        # Barre de progression
        self.progress_card = self._create_progress_card()
        layout.addWidget(self.progress_card)
        
        # Pied de page
        footer = self._create_footer()
        layout.addWidget(footer)
    
    def _create_header(self):
        """Crée l'en-tête"""
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: {Colors.WHITE};
                border: 1px solid {Colors.BORDER};
                border-radius: 16px;
                padding: 20px;
            }}
        """)
        
        layout = QHBoxLayout(header)
        layout.setSpacing(Spacing.XL)
        
        # Titre
        title_container = QVBoxLayout()
        title = QLabel("📤 Export ASAC en masse")
        title.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {Colors.TEXT_PRIMARY};")
        subtitle = QLabel("Exportez vos véhicules, flottes et contacts vers le serveur ASAC")
        subtitle.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
        title_container.addWidget(title)
        title_container.addWidget(subtitle)
        layout.addLayout(title_container, 1)
        
        # Statistiques
        stats_container = QHBoxLayout()
        stats_container.setSpacing(Spacing.LG)
        
        self.stats_total = self._create_stat_item("📊", "0", "Total")
        self.stats_pending = self._create_stat_item("⏳", "0", "En attente")
        self.stats_success = self._create_stat_item("✅", "0", "Exportés")
        self.stats_error = self._create_stat_item("❌", "0", "Erreurs")
        
        stats_container.addWidget(self.stats_total)
        stats_container.addWidget(self.stats_pending)
        stats_container.addWidget(self.stats_success)
        stats_container.addWidget(self.stats_error)
        
        layout.addLayout(stats_container)
        
        return header
    
    def _create_stat_item(self, icon, value, label):
        """Crée un élément de statistique"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background: {Colors.GRAY_50};
                border-radius: 12px;
                padding: 8px 16px;
            }}
        """)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignCenter)
        
        value_lbl = QLabel(f"{icon} {value}")
        value_lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 18px; font-weight: 700;")
        value_lbl.setObjectName("value")
        
        label_lbl = QLabel(label)
        label_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 11px;")
        
        layout.addWidget(value_lbl)
        layout.addWidget(label_lbl)
        
        widget.value_label = value_lbl
        
        return widget
    
    def _create_toolbar(self):
        """Crée la barre d'outils"""
        toolbar = QFrame()
        toolbar.setStyleSheet(f"""
            QFrame {{
                background: {Colors.WHITE};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
                padding: 8px;
            }}
        """)
        
        layout = QHBoxLayout(toolbar)
        layout.setSpacing(Spacing.MD)
        
        # Boutons d'action
        self.btn_export = self._create_tool_button("📤 Exporter sélection", Colors.PRIMARY, "#ffffff")
        self.btn_export.clicked.connect(self.start_export)
        
        self.btn_config = self._create_tool_button("⚙️ Configuration", Colors.GRAY_100, Colors.TEXT_PRIMARY)
        self.btn_config.clicked.connect(self.open_config)
        
        self.btn_refresh = self._create_tool_button("🔄 Rafraîchir", Colors.GRAY_100, Colors.TEXT_PRIMARY)
        self.btn_refresh.clicked.connect(self.load_all_data)
        
        self.btn_reset = self._create_tool_button("🔄 Réinitialiser", Colors.GRAY_100, Colors.TEXT_PRIMARY)
        self.btn_reset.clicked.connect(self.reset_export_status)
        
        self.btn_clear_logs = self._create_tool_button("🗑️ Effacer les logs", Colors.GRAY_100, Colors.TEXT_PRIMARY)
        self.btn_clear_logs.clicked.connect(self.clear_logs)
        
        layout.addWidget(self.btn_export)
        layout.addWidget(self.btn_config)
        layout.addWidget(self.btn_refresh)
        layout.addWidget(self.btn_reset)
        layout.addWidget(self.btn_clear_logs)
        
        layout.addStretch()
        
        # Filtres
        filter_container = QHBoxLayout()
        filter_container.setSpacing(Spacing.SM)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher...")
        self.search_input.setFixedWidth(200)
        self.search_input.textChanged.connect(self.filter_vehicles)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #2563eb;
            }
        """)
        filter_container.addWidget(self.search_input)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Tous", "À exporter", "Exporté", "Erreur"])
        self.status_filter.setFixedWidth(130)
        self.status_filter.currentTextChanged.connect(self.filter_vehicles)
        self.status_filter.setStyleSheet("""
            QComboBox {
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QComboBox:focus {
                border-color: #2563eb;
            }
        """)
        filter_container.addWidget(self.status_filter)
        
        self.select_all_cb = QCheckBox("Tout sélectionner")
        self.select_all_cb.stateChanged.connect(self.toggle_select_all)
        self.select_all_cb.setStyleSheet("font-size: 13px;")
        filter_container.addWidget(self.select_all_cb)
        
        self.selected_count = QLabel("0 sélectionné(s)")
        self.selected_count.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
        filter_container.addWidget(self.selected_count)
        
        layout.addLayout(filter_container)
        
        return toolbar
    
    def _create_tool_button(self, text, bg_color, text_color):
        """Crée un bouton d'outil stylisé"""
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: {bg_color}dd;
            }}
        """)
        return btn
    
    # ============================================================
    # ONGLET 1: VÉHICULES
    # ============================================================
    
    def _create_vehicles_tab(self):
        """Crée l'onglet des véhicules"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Tableau des véhicules
        self.vehicles_table = QTableWidget()
        self.vehicles_table.setColumnCount(9)
        self.vehicles_table.setHorizontalHeaderLabels([
            " ", "Immatriculation", "Marque", "Modèle", "Catégorie",
            "Statut ASAC", "Date export", "Erreur", "Actions"
        ])
        
        self.vehicles_table.setStyleSheet("""
            QTableWidget {
                border: none;
                background: transparent;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item {
                padding: 14px 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background: #eef2ff;
            }
            QHeaderView::section {
                background: #f8fafc;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                padding: 12px 8px;
                font-weight: 600;
                color: #64748b;
                font-size: 11px;
                text-transform: uppercase;
            }
        """)

        # ✅ Configuration pour que le tableau s'étende
        self.vehicles_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.vehicles_table.horizontalHeader().setStretchLastSection(True)
        self.vehicles_table.verticalHeader().setDefaultSectionSize(55)
        self.vehicles_table.verticalHeader().setMinimumSectionSize(45)
        self.vehicles_table.setAlternatingRowColors(True)
        self.vehicles_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.vehicles_table.verticalHeader().setVisible(False)
        self.vehicles_table.setMinimumHeight(400)
        
        self.vehicles_table.setColumnWidth(0, 50)
        self.vehicles_table.setColumnWidth(1, 170)
        self.vehicles_table.setColumnWidth(2, 130)
        self.vehicles_table.setColumnWidth(3, 130)
        self.vehicles_table.setColumnWidth(4, 110)
        self.vehicles_table.setColumnWidth(5, 140)
        self.vehicles_table.setColumnWidth(6, 120)
        self.vehicles_table.setColumnWidth(7, 180)
        self.vehicles_table.setColumnWidth(8, 100)
        
        self.vehicles_table.verticalHeader().setDefaultSectionSize(55)
        self.vehicles_table.setAlternatingRowColors(True)
        self.vehicles_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.vehicles_table.verticalHeader().setVisible(False)
        self.vehicles_table.setMinimumHeight(400)
        
        self.vehicles_table.horizontalHeader().sectionClicked.connect(self._on_vehicles_header_clicked)
        
        layout.addWidget(self.vehicles_table)
        
        # Pied du tableau
        footer = QHBoxLayout()
        footer.setContentsMargins(16, 8, 16, 12)
        
        self.table_info = QLabel("")
        self.table_info.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        footer.addWidget(self.table_info)
        footer.addStretch()
        
        # Légende
        legend_items = [
            ("🟢", "Exporté", Colors.SUCCESS),
            ("🟡", "À exporter", Colors.WARNING),
            ("🔴", "Erreur", Colors.DANGER)
        ]
        
        for dot, label, color in legend_items:
            item = QLabel(f"{dot} {label}")
            item.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 500;")
            footer.addWidget(item)
        
        layout.addLayout(footer)
        
        return tab
    
    def _on_vehicles_header_clicked(self, index):
        """Gère le clic sur l'en-tête du tableau des véhicules"""
        if index == 0:
            all_checked = True
            for row in range(self.vehicles_table.rowCount()):
                checkbox_widget = self.vehicles_table.cellWidget(row, 0)
                if checkbox_widget:
                    checkbox = checkbox_widget.findChild(QCheckBox)
                    if checkbox and not checkbox.isChecked():
                        all_checked = False
                        break
            
            new_state = not all_checked
            for row in range(self.vehicles_table.rowCount()):
                checkbox_widget = self.vehicles_table.cellWidget(row, 0)
                if checkbox_widget:
                    checkbox = checkbox_widget.findChild(QCheckBox)
                    if checkbox:
                        checkbox.setChecked(new_state)
                        if row < len(self.vehicles_data):
                            self.vehicles_data[row]['selected'] = new_state
            
            self._update_selected_count()
            self._update_select_all_state()
    
    # ============================================================
    # ONGLET 2: FLOTTES
    # ============================================================
    
    def _create_fleets_tab(self):
        """Crée l'onglet des flottes"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Barre de recherche
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(16, 8, 16, 8)
        
        self.fleet_search = QLineEdit()
        self.fleet_search.setPlaceholderText("🔍 Rechercher une flotte...")
        self.fleet_search.textChanged.connect(self.filter_fleets)
        self.fleet_search.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #2563eb;
            }
        """)
        search_layout.addWidget(self.fleet_search)
        search_layout.addStretch()
        
        # Compteur
        self.fleet_count = QLabel("0 flottes")
        self.fleet_count.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        search_layout.addWidget(self.fleet_count)
        
        layout.addLayout(search_layout)
        
        # Tableau des flottes
        self.fleets_table = QTableWidget()
        self.fleets_table.setColumnCount(6)
        self.fleets_table.setHorizontalHeaderLabels([
            "Nom", "Véhicules", "Réduction", "Statut ASAC", "Date export", "Actions"
        ])
        
        self.fleets_table.setStyleSheet("""
            QTableWidget {
                border: none;
                background: transparent;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item {
                padding: 14px 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background: #eef2ff;
            }
            QHeaderView::section {
                background: #f8fafc;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                padding: 12px 8px;
                font-weight: 600;
                color: #64748b;
                font-size: 11px;
                text-transform: uppercase;
            }
        """)

        # ✅ Configuration pour que le tableau s'étende
        self.fleets_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.fleets_table.horizontalHeader().setStretchLastSection(True)
        self.fleets_table.verticalHeader().setDefaultSectionSize(50)
        self.fleets_table.verticalHeader().setMinimumSectionSize(40)
        self.fleets_table.setAlternatingRowColors(True)
        self.fleets_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.fleets_table.verticalHeader().setVisible(False)
        self.fleets_table.setMinimumHeight(300)
        
        self.fleets_table.verticalHeader().setDefaultSectionSize(50)
        self.fleets_table.setAlternatingRowColors(True)
        self.fleets_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.fleets_table.verticalHeader().setVisible(False)
        self.fleets_table.setMinimumHeight(300)
        
        layout.addWidget(self.fleets_table)
        
        return tab
    
    # ============================================================
    # ONGLET 3: CONTACTS
    # ============================================================
    
    def _create_contacts_tab(self):
        """Crée l'onglet des contacts"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Barre de recherche
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(16, 8, 16, 8)
        
        self.contact_search = QLineEdit()
        self.contact_search.setPlaceholderText("🔍 Rechercher un contact...")
        self.contact_search.textChanged.connect(self.filter_contacts)
        self.contact_search.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #2563eb;
            }
        """)
        search_layout.addWidget(self.contact_search)
        search_layout.addStretch()
        
        self.contact_count = QLabel("0 contacts")
        self.contact_count.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        search_layout.addWidget(self.contact_count)
        
        layout.addLayout(search_layout)
        
        # Tableau des contacts
        self.contacts_table = QTableWidget()
        self.contacts_table.setColumnCount(6)
        self.contacts_table.setHorizontalHeaderLabels([
            "Nom", "Prénom", "Téléphone", "Email", "Statut ASAC", "Actions"
        ])
        
        self.contacts_table.setStyleSheet("""
            QTableWidget {
                border: none;
                background: transparent;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item {
                padding: 14px 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background: #eef2ff;
            }
            QHeaderView::section {
                background: #f8fafc;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                padding: 12px 8px;
                font-weight: 600;
                color: #64748b;
                font-size: 11px;
                text-transform: uppercase;
            }
        """)

        # ✅ Configuration pour que le tableau s'étende
        self.contacts_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.contacts_table.horizontalHeader().setStretchLastSection(True)
        self.contacts_table.verticalHeader().setDefaultSectionSize(50)
        self.contacts_table.verticalHeader().setMinimumSectionSize(40)
        self.contacts_table.setAlternatingRowColors(True)
        self.contacts_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.contacts_table.verticalHeader().setVisible(False)
        self.contacts_table.setMinimumHeight(300)
        
        self.contacts_table.verticalHeader().setDefaultSectionSize(50)
        self.contacts_table.setAlternatingRowColors(True)
        self.contacts_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.contacts_table.verticalHeader().setVisible(False)
        self.contacts_table.setMinimumHeight(300)
        
        layout.addWidget(self.contacts_table)
        
        return tab
    
    # ============================================================
    # ONGLET 4: LOGS
    # ============================================================
    
    def _create_logs_tab(self):
        """Crée l'onglet des logs"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Barre d'outils des logs
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(16, 8, 16, 8)
        
        toolbar.addWidget(QLabel("Filtrer:"))
        
        self.log_filter = QComboBox()
        self.log_filter.addItems(["Tous", "✅ Succès", "⚠️ Avertissement", "❌ Erreur"])
        self.log_filter.setFixedWidth(150)
        self.log_filter.currentTextChanged.connect(self.filter_logs)
        self.log_filter.setStyleSheet("""
            QComboBox {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 12px;
            }
        """)
        toolbar.addWidget(self.log_filter)
        
        toolbar.addStretch()
        
        self.log_count = QLabel("0 messages")
        self.log_count.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        toolbar.addWidget(self.log_count)
        
        layout.addLayout(toolbar)
        
        # Zone de logs
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setFont(QFont("Courier New", 10))
        self.logs_text.setStyleSheet("""
            QTextEdit {
                background: #1e293b;
                color: #e2e8f0;
                border: none;
                padding: 16px;
                font-family: 'Courier New', monospace;
            }
        """)
        self.logs_text.setMinimumHeight(300)
        
        layout.addWidget(self.logs_text)
        
        return tab
    
    # ============================================================
    # PROGRESS CARD
    # ============================================================
    
    def _create_progress_card(self):
        """Crée la carte de progression"""
        card = ModernCard(title="⏳ Progression de l'export", icon="📊")
        card.setVisible(False)
        
        layout = QVBoxLayout()
        layout.setSpacing(Spacing.SM)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: {Colors.GRAY_100};
            }}
            QProgressBar::chunk {{
                background: {Colors.PRIMARY};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(self.progress_bar)
        
        status_layout = QHBoxLayout()
        self.progress_status = QLabel("Prêt")
        self.progress_status.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
        status_layout.addWidget(self.progress_status)
        status_layout.addStretch()
        self.progress_count = QLabel("0 / 0")
        self.progress_count.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px; font-weight: 600;")
        status_layout.addWidget(self.progress_count)
        
        layout.addLayout(status_layout)
        card.add_layout(layout)
        
        return card
    
    def _create_footer(self):
        """Crée le pied de page"""
        footer = QFrame()
        footer.setStyleSheet(f"""
            QFrame {{
                background: {Colors.WHITE};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
                padding: 8px 16px;
            }}
        """)
        
        layout = QHBoxLayout(footer)
        
        # Icône de statut
        self.status_icon = QLabel("●")
        self.status_icon.setStyleSheet("color: #10b981; font-size: 10px;")
        layout.addWidget(self.status_icon)
        
        self.status_label = QLabel("Prêt")
        self.status_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Quota info
        quota_label = QLabel("⏱️ Quota: 60 requêtes/minute")
        quota_label.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 11px;")
        layout.addWidget(quota_label)
        
        return footer
    
    # ============================================================
    # POPULATE TABLES
    # ============================================================
    
    def populate_vehicles_table(self):
        """Remplit le tableau des véhicules"""
        self.vehicles_table.setRowCount(len(self.vehicles_data))
        
        status_config = {
            'success': {'bg': '#d1fae5', 'color': '#059669', 'label': '✅ Exporté'},
            'error': {'bg': '#fee2e2', 'color': '#dc2626', 'label': '❌ Erreur'},
            'pending': {'bg': '#fef3c7', 'color': '#d97706', 'label': '⏳ À exporter'},
            'in_progress': {'bg': '#dbeafe', 'color': '#2563eb', 'label': '🔄 En cours...'}
        }
        
        for row, vehicle in enumerate(self.vehicles_data):
            # Checkbox
            checkbox_widget = QWidget()
            checkbox_widget.setStyleSheet("background: transparent;")
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            
            checkbox = QCheckBox()
            checkbox.setChecked(vehicle.get('selected', False))
            checkbox.setStyleSheet("""
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                    border-radius: 4px;
                    border: 2px solid #cbd5e1;
                    background: white;
                }
                QCheckBox::indicator:checked {
                    background-color: #2563eb;
                    border-color: #2563eb;
                }
            """)
            checkbox.stateChanged.connect(lambda state, r=row: self._on_vehicle_selected(r))
            checkbox_layout.addWidget(checkbox)
            self.vehicles_table.setCellWidget(row, 0, checkbox_widget)
            
            # Immatriculation
            immat_item = QTableWidgetItem(vehicle.get('immatriculation', '-'))
            immat_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            immat_item.setForeground(QColor(Colors.PRIMARY))
            self.vehicles_table.setItem(row, 1, immat_item)
            
            # Marque
            self.vehicles_table.setItem(row, 2, QTableWidgetItem(vehicle.get('marque', '-')))
            
            # Modèle
            self.vehicles_table.setItem(row, 3, QTableWidgetItem(vehicle.get('modele', '-')))
            
            # Catégorie
            cat_item = QTableWidgetItem(vehicle.get('categorie', '-'))
            cat_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            self.vehicles_table.setItem(row, 4, cat_item)
            
            # Statut ASAC
            status = vehicle.get('asac_status', 'pending')
            config = status_config.get(status, status_config['pending'])
            
            status_widget = QFrame()
            status_widget.setStyleSheet(f"""
                QFrame {{
                    background: {config['bg']};
                    border-radius: 12px;
                    padding: 6px 14px;
                }}
            """)
            status_layout = QHBoxLayout(status_widget)
            status_layout.setContentsMargins(8, 6, 8, 6)
            status_layout.setAlignment(Qt.AlignCenter)
            
            status_label = QLabel(config['label'])
            status_label.setStyleSheet(f"color: {config['color']}; font-weight: 600; font-size: 13px;")
            status_layout.addWidget(status_label)
            self.vehicles_table.setCellWidget(row, 5, status_widget)
            
            # Date export
            date_item = QTableWidgetItem(vehicle.get('export_date', '-'))
            date_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            self.vehicles_table.setItem(row, 6, date_item)
            
            # Erreur
            error_msg = vehicle.get('error_message', '')
            error_item = QTableWidgetItem(error_msg[:50] + '...' if len(error_msg) > 50 else error_msg)
            if error_msg:
                error_item.setForeground(QColor(Colors.DANGER))
                error_item.setToolTip(error_msg)
            else:
                error_item.setText('-')
                error_item.setForeground(QColor(Colors.TEXT_MUTED))
            self.vehicles_table.setItem(row, 7, error_item)
            
            # Actions
            actions_widget = self._create_actions_widget(row)
            self.vehicles_table.setCellWidget(row, 8, actions_widget)
        
        self.vehicles_table.resizeColumnsToContents()
        self._update_stats()
        self._update_selected_count()
    
    def _create_actions_widget(self, row):
        """Crée les boutons d'action"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)
        
        # Bouton Aperçu
        preview_btn = QPushButton("👁️")
        preview_btn.setFixedSize(34, 34)
        preview_btn.setToolTip("Voir les détails")
        preview_btn.setStyleSheet("""
            QPushButton {
                background: #e0f2fe;
                border: none;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #bae6fd;
            }
        """)
        preview_btn.clicked.connect(lambda: self.view_vehicle_details(row))
        
        # Bouton Exporter
        export_btn = QPushButton("📤")
        export_btn.setFixedSize(34, 34)
        export_btn.setToolTip("Exporter ce véhicule")
        export_btn.setStyleSheet("""
            QPushButton {
                background: #d1fae5;
                border: none;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #a7f3d0;
            }
        """)
        export_btn.clicked.connect(lambda: self.export_single_vehicle(row))
        
        layout.addWidget(preview_btn)
        layout.addWidget(export_btn)
        
        return widget
    
    def populate_fleets_table(self):
        """Remplit le tableau des flottes"""
        self.fleets_table.setRowCount(len(self.fleets_data))
        
        for row, fleet in enumerate(self.fleets_data):
            self.fleets_table.setItem(row, 0, QTableWidgetItem(fleet.get('nom', '-')))
            self.fleets_table.setItem(row, 1, QTableWidgetItem(str(fleet.get('nb_vehicules', 0))))
            self.fleets_table.setItem(row, 2, QTableWidgetItem(f"{fleet.get('remise', 0)}%"))
            
            status = fleet.get('asac_status', 'pending')
            status_label = "✅ Exporté" if status == 'success' else "⏳ À exporter" if status == 'pending' else "❌ Erreur"
            status_item = QTableWidgetItem(status_label)
            color = Colors.SUCCESS if status == 'success' else Colors.WARNING if status == 'pending' else Colors.DANGER
            status_item.setForeground(QColor(color))
            self.fleets_table.setItem(row, 3, status_item)
            
            self.fleets_table.setItem(row, 4, QTableWidgetItem(fleet.get('export_date', '-')))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 2, 4, 2)
            actions_layout.setAlignment(Qt.AlignCenter)
            
            export_btn = QPushButton("📤")
            export_btn.setFixedSize(30, 30)
            export_btn.setToolTip("Exporter cette flotte")
            export_btn.setStyleSheet("""
                QPushButton {
                    background: #d1fae5;
                    border: none;
                    border-radius: 6px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: #a7f3d0;
                }
            """)
            actions_layout.addWidget(export_btn)
            
            self.fleets_table.setCellWidget(row, 5, actions_widget)
        
        self.fleets_table.resizeColumnsToContents()
        self.fleet_count.setText(f"{len(self.fleets_data)} flottes")
    
    def populate_contacts_table(self):
        """Remplit le tableau des contacts"""
        self.contacts_table.setRowCount(len(self.contacts_data))
        
        for row, contact in enumerate(self.contacts_data):
            self.contacts_table.setItem(row, 0, QTableWidgetItem(contact.get('nom', '-')))
            self.contacts_table.setItem(row, 1, QTableWidgetItem(contact.get('prenom', '-')))
            self.contacts_table.setItem(row, 2, QTableWidgetItem(contact.get('telephone', '-')))
            self.contacts_table.setItem(row, 3, QTableWidgetItem(contact.get('email', '-')))
            
            status = contact.get('asac_status', 'pending')
            status_label = "✅ Exporté" if status == 'success' else "⏳ À exporter" if status == 'pending' else "❌ Erreur"
            status_item = QTableWidgetItem(status_label)
            color = Colors.SUCCESS if status == 'success' else Colors.WARNING if status == 'pending' else Colors.DANGER
            status_item.setForeground(QColor(color))
            self.contacts_table.setItem(row, 4, status_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 2, 4, 2)
            actions_layout.setAlignment(Qt.AlignCenter)
            
            export_btn = QPushButton("📤")
            export_btn.setFixedSize(30, 30)
            export_btn.setToolTip("Exporter ce contact")
            export_btn.setStyleSheet("""
                QPushButton {
                    background: #d1fae5;
                    border: none;
                    border-radius: 6px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: #a7f3d0;
                }
            """)
            actions_layout.addWidget(export_btn)
            
            self.contacts_table.setCellWidget(row, 5, actions_widget)
        
        self.contacts_table.resizeColumnsToContents()
        self.contact_count.setText(f"{len(self.contacts_data)} contacts")
    
    # ============================================================
    # GESTION DE LA SÉLECTION
    # ============================================================
    
    def _on_vehicle_selected(self, row):
        """Gère la sélection d'un véhicule"""
        if self._updating_selection:
            return
        
        checkbox_widget = self.vehicles_table.cellWidget(row, 0)
        if not checkbox_widget:
            return
        
        checkbox = checkbox_widget.findChild(QCheckBox)
        if not checkbox:
            return
        
        self.vehicles_data[row]['selected'] = checkbox.isChecked()
        self._update_selected_count()
        self._update_select_all_state()
    
    def _update_selected_count(self):
        """Met à jour le compteur de sélection"""
        count = sum(1 for v in self.vehicles_data if v.get('selected', False))
        self.selected_count.setText(f"{count} sélectionné(s)")
        self.btn_export.setText(f"📤 Exporter ({count})" if count > 0 else "📤 Exporter sélection")
        self.btn_export.setEnabled(count > 0)
    
    def _update_select_all_state(self):
        """Met à jour l'état du bouton 'Tout sélectionner'"""
        total = len(self.vehicles_data)
        selected = sum(1 for v in self.vehicles_data if v.get('selected', False))
        
        if total == 0:
            return
        
        self._updating_selection = True
        if selected == total:
            self.select_all_cb.setCheckState(Qt.Checked)
        elif selected == 0:
            self.select_all_cb.setCheckState(Qt.Unchecked)
        else:
            self.select_all_cb.setCheckState(Qt.PartiallyChecked)
        self._updating_selection = False
    
    def toggle_select_all(self, state):
        """Sélectionne/désélectionne tous les véhicules"""
        if self._updating_selection:
            return
        
        checked = state == Qt.CheckState.Checked
        
        for row in range(self.vehicles_table.rowCount()):
            checkbox_widget = self.vehicles_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(checked)
                    self.vehicles_data[row]['selected'] = checked
        
        self._update_selected_count()
    
    # ============================================================
    # FILTRES
    # ============================================================
    
    def filter_vehicles(self):
        """Filtre les véhicules"""
        search = self.search_input.text().lower()
        status = self.status_filter.currentText()
        
        for row in range(self.vehicles_table.rowCount()):
            visible = True
            
            if search:
                immat = self.vehicles_table.item(row, 1)
                if immat:
                    visible = search in immat.text().lower()
            
            if visible and status != "Tous":
                status_widget = self.vehicles_table.cellWidget(row, 5)
                if status_widget:
                    status_label = status_widget.findChild(QLabel)
                    if status_label:
                        visible = status in status_label.text()
            
            self.vehicles_table.setRowHidden(row, not visible)
    
    def filter_fleets(self):
        """Filtre les flottes"""
        search = self.fleet_search.text().lower()
        for row in range(self.fleets_table.rowCount()):
            visible = True
            if search:
                nom = self.fleets_table.item(row, 0)
                if nom:
                    visible = search in nom.text().lower()
            self.fleets_table.setRowHidden(row, not visible)
    
    def filter_contacts(self):
        """Filtre les contacts"""
        search = self.contact_search.text().lower()
        for row in range(self.contacts_table.rowCount()):
            visible = True
            if search:
                nom = self.contacts_table.item(row, 0)
                prenom = self.contacts_table.item(row, 1)
                if nom or prenom:
                    visible = (nom and search in nom.text().lower()) or (prenom and search in prenom.text().lower())
            self.contacts_table.setRowHidden(row, not visible)
    
    # ============================================================
    # LOGS
    # ============================================================
    
    def add_log(self, message, level="INFO"):
        """Ajoute un message dans les logs"""
        colors = {
            "INFO": "#94a3b8",
            "SUCCESS": "#10b981",
            "WARNING": "#f59e0b",
            "ERROR": "#ef4444"
        }
        color = colors.get(level, "#94a3b8")
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        level_icons = {
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "INFO": "ℹ️"
        }
        icon = level_icons.get(level, "ℹ️")
        
        formatted = f'<span style="color: #64748b;">[{timestamp}]</span> <span style="color: {color};">{icon} {message}</span><br>'
        
        self.logs_text.append(formatted)
        cursor = self.logs_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.logs_text.setTextCursor(cursor)
        
        self.export_logs.append({
            'timestamp': timestamp,
            'message': message,
            'level': level,
            'html': formatted
        })
        
        self.log_count.setText(f"{len(self.export_logs)} messages")
    
    def filter_logs(self):
        """Filtre les logs par niveau"""
        filter_text = self.log_filter.currentText()
        
        if filter_text == "Tous":
            self.logs_text.clear()
            for log in self.export_logs:
                self.logs_text.append(log['html'])
        else:
            level_map = {
                "✅ Succès": "SUCCESS",
                "⚠️ Avertissement": "WARNING",
                "❌ Erreur": "ERROR"
            }
            target_level = level_map.get(filter_text, "")
            
            self.logs_text.clear()
            for log in self.export_logs:
                if log['level'] == target_level:
                    self.logs_text.append(log['html'])
        
        cursor = self.logs_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.logs_text.setTextCursor(cursor)
    
    def clear_logs(self):
        """Efface les logs"""
        self.logs_text.clear()
        self.export_logs = []
        self.log_count.setText("0 messages")
        self.add_log("🗑️ Logs effacés", "INFO")
    
    # ============================================================
    # EXPORT
    # ============================================================
    
    def start_export(self):
        """Démarre l'export en masse"""
        selected = [v for v in self.vehicles_data if v.get('selected', False)]
        
        if not selected:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner au moins un véhicule.")
            return
        
        config = self.load_config()
        if not config["url"] or not config["app_key"]:
            QMessageBox.warning(self, "Configuration manquante", "Veuillez configurer le serveur ASAC.")
            self.open_config()
            return
        
        reply = QMessageBox.question(
            self, "Confirmation d'export",
            f"Voulez-vous exporter {len(selected)} véhicules vers ASAC ?\n\n"
            f"⚠️ Limite: 60 requêtes par minute.\n"
            f"Temps estimé: ~{len(selected)} secondes",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._start_bulk_export(selected, config)
    
    def export_single_vehicle(self, row):
        """Exporte un seul véhicule"""
        if row < len(self.vehicles_data):
            vehicle = self.vehicles_data[row]
            config = self.load_config()
            
            if not config["url"] or not config["app_key"]:
                QMessageBox.warning(self, "Configuration manquante", "Veuillez configurer le serveur ASAC.")
                self.open_config()
                return
            
            self._start_bulk_export([vehicle], config)
    
    def _start_bulk_export(self, vehicles, config):
        """Démarre l'export en masse"""
        self.progress_card.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_status.setText("Export en cours...")
        self.progress_count.setText(f"0 / {len(vehicles)}")
        self.set_status("⏳ Export en cours...", "info")
        self.add_log(f"🚀 Démarrage de l'export de {len(vehicles)} véhicules", "INFO")
        
        options = {'skip_duplicates': True}
        
        self.export_worker = BulkExportWorker(vehicles, config, options)
        self.export_worker.progress_updated.connect(self._update_export_progress)
        self.export_worker.log_updated.connect(self.add_log)
        self.export_worker.finished.connect(self._on_export_finished)
        self.export_worker.error.connect(self._on_export_error)
        self.export_worker.vehicle_result.connect(self._on_vehicle_result)
        self.export_worker.start()
        
        self.btn_export.setEnabled(False)
    
    def _update_export_progress(self, current, total, status):
        """Met à jour la progression"""
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
        self.progress_status.setText(status)
        self.progress_count.setText(f"{current} / {total}")
        self.set_status(f"⏳ {status}", "info")
    
    def _on_vehicle_result(self, vehicle_data, result):
        """Traite le résultat d'un véhicule exporté"""
        immat = vehicle_data.get('immatriculation', 'N/A')
        
        if result.get('success'):
            self.add_log(f"✅ {immat}: {result.get('message', 'Exporté avec succès')}", "SUCCESS")
            for v in self.vehicles_data:
                if v.get('immatriculation') == immat:
                    v['asac_status'] = 'success'
                    v['export_date'] = datetime.now().strftime("%d/%m/%Y")
                    v['error_message'] = ''
                    break
        else:
            error_msg = result.get('error', 'Erreur inconnue')
            self.add_log(f"❌ {immat}: {error_msg}", "ERROR")
            for v in self.vehicles_data:
                if v.get('immatriculation') == immat:
                    v['asac_status'] = 'error'
                    v['error_message'] = error_msg
                    break
    
    def _on_export_finished(self, results):
        """Appelé à la fin de l'export"""
        self.btn_export.setEnabled(True)
        self.progress_card.setVisible(False)
        
        self._save_export_history(results)
        self.load_all_data()
        
        summary = (
            f"📊 Export ASAC terminé!\n\n"
            f"✅ Réussis: {results['success']}\n"
            f"⏭️ Ignorés: {results['skipped']}\n"
            f"❌ Échecs: {results['failed']}\n"
            f"📦 Total: {results['total']}"
        )
        
        self.add_log("=" * 50, "INFO")
        self.add_log(summary, "SUCCESS")
        self.add_log("=" * 50, "INFO")
        self.set_status("✅ Export terminé", "success")
        
        if results['failed'] > 0:
            errors = "\n".join(results['errors'][:5])
            QMessageBox.warning(self, "Export terminé avec erreurs", f"{summary}\n\n❌ Erreurs:\n{errors}")
        else:
            QMessageBox.information(self, "Export réussi", summary)
    
    def _on_export_error(self, error_msg):
        """Appelé en cas d'erreur d'export"""
        self.btn_export.setEnabled(True)
        self.progress_card.setVisible(False)
        self.add_log(f"❌ Erreur d'export: {error_msg}", "ERROR")
        self.set_status(f"❌ Erreur: {error_msg}", "error")
        QMessageBox.critical(self, "Erreur", f"Erreur d'export: {error_msg}")
    
    def _save_export_history(self, results):
        """Sauvegarde l'historique d'export"""
        for detail in results.get('details', []):
            vehicle = detail.get('vehicle', {})
            vehicle_id = vehicle.get('id')
            if vehicle_id:
                history = self.settings.value(f"asac_history_{vehicle_id}", [])
                if isinstance(history, str):
                    try:
                        history = json.loads(history)
                    except:
                        history = []
                
                history.insert(0, {
                    'date': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    'status': detail.get('status', 'pending').lower(),
                    'message': detail.get('message', ''),
                    'reference': detail.get('reference', '')
                })
                
                history = history[:20]
                self.settings.setValue(f"asac_history_{vehicle_id}", json.dumps(history))
    
    # ============================================================
    # CHARGEMENT DES DONNÉES
    # ============================================================
    
    def load_all_data(self):
        """Charge toutes les données"""
        self.load_vehicles_from_db()
        self.load_fleets_from_db()
        self.load_contacts_from_db()
    
    def load_vehicles_from_db(self):
        """Charge les véhicules depuis la base de données"""
        try:
            from addons.Automobiles.models.automobile_models import Vehicle
            from sqlalchemy.orm import joinedload
            
            vehicles = self.controller.session.query(Vehicle).options(
                joinedload(Vehicle.fleet),
                joinedload(Vehicle.owner)
            ).filter(Vehicle.is_active == True).all()
            
            self.vehicles_data = []
            for vehicle in vehicles:
                asac_status, export_date = self._get_vehicle_asac_status(vehicle.id)
                
                self.vehicles_data.append({
                    'id': vehicle.id,
                    'immatriculation': vehicle.immatriculation,
                    'marque': vehicle.marque,
                    'modele': vehicle.modele,
                    'categorie': vehicle.categorie,
                    'asac_status': asac_status,
                    'export_date': export_date,
                    'error_message': '',
                    'selected': False
                })
            
            self.populate_vehicles_table()
            self.add_log(f"📊 {len(self.vehicles_data)} véhicules chargés", "INFO")
            
        except Exception as e:
            self.add_log(f"❌ Erreur chargement véhicules: {str(e)}", "ERROR")
            self.vehicles_data = []
    
    def load_fleets_from_db(self):
        """Charge les flottes depuis la base de données"""
        try:
            from addons.Automobiles.models.flottes_models import Fleet
            
            fleets = self.controller.session.query(Fleet).all()
            
            self.fleets_data = []
            for fleet in fleets:
                self.fleets_data.append({
                    'id': fleet.id,
                    'nom': fleet.nom_flotte,
                    'nb_vehicules': len(fleet.vehicles) if hasattr(fleet, 'vehicles') else 0,
                    'remise': fleet.remise_flotte,
                    'asac_status': 'pending',
                    'export_date': ''
                })
            
            self.populate_fleets_table()
            self.add_log(f"📊 {len(self.fleets_data)} flottes chargées", "INFO")
            
        except Exception as e:
            self.add_log(f"❌ Erreur chargement flottes: {str(e)}", "ERROR")
            self.fleets_data = []
    
    def load_contacts_from_db(self):
        """Charge les contacts depuis la base de données"""
        try:
            from addons.Automobiles.models.contact_models import Contact
            
            contacts = self.controller.session.query(Contact).all()
            
            self.contacts_data = []
            for contact in contacts:
                self.contacts_data.append({
                    'id': contact.id,
                    'nom': contact.nom,
                    'prenom': contact.prenom,
                    'telephone': contact.telephone,
                    'email': contact.email,
                    'asac_status': 'pending'
                })
            
            self.populate_contacts_table()
            self.add_log(f"📊 {len(self.contacts_data)} contacts chargés", "INFO")
            
        except Exception as e:
            self.add_log(f"❌ Erreur chargement contacts: {str(e)}", "ERROR")
            self.contacts_data = []
    
    def _get_vehicle_asac_status(self, vehicle_id):
        """Récupère le statut ASAC d'un véhicule"""
        try:
            history = self.settings.value(f"asac_history_{vehicle_id}", [])
            if isinstance(history, str):
                try:
                    history = json.loads(history)
                except:
                    history = []
            
            if history:
                last = history[0]
                return last.get('status', 'pending'), last.get('date', '')
            return 'pending', ''
        except:
            return 'pending', ''
    
    def _update_stats(self):
        """Met à jour les statistiques"""
        total = len(self.vehicles_data)
        pending = sum(1 for v in self.vehicles_data if v.get('asac_status') == 'pending')
        success = sum(1 for v in self.vehicles_data if v.get('asac_status') == 'success')
        error = sum(1 for v in self.vehicles_data if v.get('asac_status') == 'error')
        
        self.stats_total.value_label.setText(f"📊 {total}")
        self.stats_pending.value_label.setText(f"⏳ {pending}")
        self.stats_success.value_label.setText(f"✅ {success}")
        self.stats_error.value_label.setText(f"❌ {error}")
    
    def set_status(self, message, level="info"):
        """Met à jour le statut"""
        colors = {
            "success": "#10b981",
            "error": "#ef4444",
            "warning": "#f59e0b",
            "info": "#3b82f6"
        }
        color = colors.get(level, "#64748b")
        self.status_icon.setStyleSheet(f"color: {color}; font-size: 10px;")
        self.status_label.setText(message)
    
    def load_config(self):
        """Charge la configuration ASAC"""
        config = {
            "url": self.settings.value("url", ""),
            "app_key": self.settings.value("app_key", ""),
            "username": self.settings.value("username", ""),
            "password": self.settings.value("password", ""),
            "email": self.settings.value("email", ""),
            "office_code": self.settings.value("office_code", "AG-DLA-001"),
            "org_code": self.settings.value("org_code", "ACTIVA")
        }
        return config
    
    def open_config(self):
        """Ouvre la configuration ASAC"""
        dialog = ConfigDialog(self)
        if dialog.exec():
            self.load_config()
            self.add_log("✅ Configuration mise à jour", "SUCCESS")
    
    def reset_export_status(self):
        """Réinitialise les statuts d'export"""
        reply = QMessageBox.question(
            self, "Réinitialisation",
            "Voulez-vous réinitialiser tous les statuts d'export ASAC ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for v in self.vehicles_data:
                v['asac_status'] = 'pending'
                v['export_date'] = ''
                v['error_message'] = ''
                self.settings.remove(f"asac_history_{v.get('id')}")
            
            self.populate_vehicles_table()
            self.add_log("🔄 Statuts d'export réinitialisés", "INFO")
    
    def view_vehicle_details(self, row):
        """Affiche les détails d'un véhicule"""
        if row < len(self.vehicles_data):
            vehicle = self.vehicles_data[row]
            details = json.dumps(vehicle, indent=2, default=str)
            QMessageBox.information(self, "Détails du véhicule", details)


# ============================================================
# BULK EXPORT WORKER
# ============================================================

class BulkExportWorker(QThread):
    """Thread pour l'export en masse vers ASAC"""
    
    progress_updated = Signal(int, int, str)
    log_updated = Signal(str, str)
    finished = Signal(dict)
    error = Signal(str)
    vehicle_result = Signal(dict, dict)
    
    def __init__(self, vehicles_data: List[Dict], config: Dict, options: Dict = None):
        super().__init__()
        self.vehicles_data = vehicles_data
        self.config = config
        self.options = options or {}
        self._running = True
        self.request_interval = 1.0
    
    def run(self):
        try:
            total = len(self.vehicles_data)
            results = {
                'total': total,
                'success': 0,
                'failed': 0,
                'skipped': 0,
                'errors': [],
                'details': []
            }
            
            for i, vehicle_data in enumerate(self.vehicles_data):
                if not self._running:
                    break
                
                self.progress_updated.emit(i + 1, total, 
                    f"Traitement {i+1}/{total}: {vehicle_data.get('immatriculation', 'N/A')}")
                
                try:
                    result = self._export_vehicle(vehicle_data)
                    self.vehicle_result.emit(vehicle_data, result)
                    
                    if result.get('success'):
                        results['success'] += 1
                        results['details'].append({
                            'vehicle': vehicle_data,
                            'status': 'SUCCESS',
                            'message': result.get('message', 'Exporté'),
                            'reference': result.get('reference', '')
                        })
                        self.log_updated.emit(
                            f"✅ {vehicle_data.get('immatriculation', 'N/A')}: Exporté", "SUCCESS")
                    else:
                        results['failed'] += 1
                        error_msg = result.get('error', 'Erreur inconnue')
                        results['errors'].append(f"{vehicle_data.get('immatriculation', 'N/A')}: {error_msg}")
                        results['details'].append({
                            'vehicle': vehicle_data,
                            'status': 'ERROR',
                            'message': error_msg
                        })
                        self.log_updated.emit(
                            f"❌ {vehicle_data.get('immatriculation', 'N/A')}: {error_msg}", "ERROR")
                    
                    if i < total - 1:
                        time.sleep(self.request_interval)
                    
                except Exception as e:
                    results['failed'] += 1
                    error_msg = str(e)
                    results['errors'].append(f"{vehicle_data.get('immatriculation', 'N/A')}: {error_msg}")
                    results['details'].append({
                        'vehicle': vehicle_data,
                        'status': 'ERROR',
                        'message': error_msg
                    })
                    self.log_updated.emit(
                        f"❌ {vehicle_data.get('immatriculation', 'N/A')}: {error_msg}", "ERROR")
            
            results['completed'] = True
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(str(e))
    
    def _export_vehicle(self, vehicle_data: Dict) -> Dict:
        """Exporte un véhicule vers ASAC"""
        try:
            worker = ExportWorker(vehicle_data, self.config)
            request = worker.build_asac_request()
            
            import requests
            
            auth_url = f"{self.config.get('url', '')}/api/v1/auth/tokens"
            headers = {
                "X-App-Id": self.config.get("app_key", ""),
                "Content-Type": "application/json"
            }
            auth_payload = {
                "username": self.config.get("username", ""),
                "password": self.config.get("password", ""),
                "email": self.config.get("email", "")
            }
            
            auth_response = requests.post(auth_url, headers=headers, json=auth_payload, timeout=10)
            
            if auth_response.status_code != 200:
                return {'success': False, 'error': f"Authentification échouée: {auth_response.text[:100]}"}
            
            auth_data = auth_response.json()
            token = auth_data.get("token", "")
            
            prod_url = f"{self.config['url']}/api/v1/productions"
            prod_headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            prod_response = requests.post(prod_url, json=request, headers=prod_headers, timeout=30)
            
            if prod_response.status_code in [200, 201]:
                response_data = prod_response.json()
                return {
                    'success': True,
                    'message': 'Exporté avec succès',
                    'reference': response_data.get('data', {}).get('reference', 'N/A')
                }
            else:
                return {'success': False, 'error': f"Erreur ASAC: {prod_response.text[:200]}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def stop(self):
        self._running = False