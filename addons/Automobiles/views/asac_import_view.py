# addons/Automobiles/views/asac_import_view.py
"""
Vue d'importation de véhicules et flottes depuis le serveur ASAC
Import en masse avec aperçu, validation et suivi de progression
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QFileDialog, QMessageBox, QGroupBox,
    QGridLayout, QCheckBox, QComboBox, QLineEdit,
    QTextEdit, QSplitter, QTabWidget, QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QDateTime
from PySide6.QtGui import QColor, QFont, QTextCursor

from datetime import datetime
from typing import List, Dict, Any, Optional
import json

from addons.Automobiles.views.style import Colors, Fonts, Spacing
from addons.Automobiles.views.widgets.modern_card import ModernCard


class ASACImportWorker(QThread):
    """Thread pour l'importation des données ASAC"""
    
    progress_updated = Signal(int, int, str)  # current, total, status
    log_updated = Signal(str, str)  # message, level (INFO, SUCCESS, ERROR, WARNING)
    finished = Signal(dict)  # résultats
    error = Signal(str)
    
    def __init__(self, import_type: str, data: List[Dict], controller, options: Dict = None):
        super().__init__()
        self.import_type = import_type  # 'vehicles' ou 'fleets'
        self.data = data
        self.controller = controller
        self.options = options or {}
        self._running = True
    
    def run(self):
        try:
            results = {
                'total': len(self.data),
                'imported': 0,
                'failed': 0,
                'skipped': 0,
                'errors': [],
                'details': []
            }
            
            for i, item in enumerate(self.data):
                if not self._running:
                    break
                
                self.progress_updated.emit(i + 1, len(self.data), f"Traitement {i+1}/{len(self.data)}")
                
                try:
                    if self.import_type == 'vehicles':
                        result = self._import_vehicle(item)
                    else:
                        result = self._import_fleet(item)
                    
                    if result.get('success'):
                        results['imported'] += 1
                        results['details'].append({
                            'item': item,
                            'status': 'SUCCESS',
                            'message': result.get('message', 'Importé avec succès')
                        })
                        self.log_updated.emit(f"✅ {result.get('message', 'Importé avec succès')}", "SUCCESS")
                    elif result.get('skipped'):
                        results['skipped'] += 1
                        results['details'].append({
                            'item': item,
                            'status': 'SKIPPED',
                            'message': result.get('message', 'Ignoré')
                        })
                        self.log_updated.emit(f"⏭️ {result.get('message', 'Ignoré')}", "WARNING")
                    else:
                        results['failed'] += 1
                        error_msg = result.get('error', 'Erreur inconnue')
                        results['errors'].append(error_msg)
                        results['details'].append({
                            'item': item,
                            'status': 'ERROR',
                            'message': error_msg
                        })
                        self.log_updated.emit(f"❌ {error_msg}", "ERROR")
                
                except Exception as e:
                    results['failed'] += 1
                    error_msg = str(e)
                    results['errors'].append(error_msg)
                    results['details'].append({
                        'item': item,
                        'status': 'ERROR',
                        'message': error_msg
                    })
                    self.log_updated.emit(f"❌ {error_msg}", "ERROR")
            
            results['completed'] = True
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(str(e))
    
    def _import_vehicle(self, data: Dict) -> Dict:
        """Importe un véhicule depuis les données ASAC"""
        try:
            # Vérifier si le véhicule existe déjà
            licence_plate = data.get('licence_plate', data.get('immatriculation'))
            if not licence_plate:
                return {'success': False, 'error': 'Immatriculation manquante'}
            
            # Vérifier les doublons
            if not self.options.get('allow_duplicates', False):
                existing = self.controller.get_vehicle_by_plate(licence_plate)
                if existing:
                    return {'success': False, 'skipped': True, 'message': f'Véhicule {licence_plate} déjà existant'}
            
            # Construire les données du véhicule
            vehicle_data = {
                'licence_plate': licence_plate,
                'vehicle_chassis': data.get('vehicle_chassis', data.get('chassis', '')),
                'vehicle_brand': data.get('vehicle_brand', data.get('marque', '')),
                'vehicle_model': data.get('vehicle_model', data.get('modele', '')),
                'vehicle_first_registration_date': self._parse_date(data.get('vehicle_first_registration_date', data.get('date_premiere_mise_circulation'))),
                'vehicle_category': data.get('vehicle_category', data.get('categorie')),
                'vehicle_genre': data.get('vehicle_genre', data.get('genre')),
                'vehicle_type': data.get('vehicle_type', data.get('type')),
                'vehicle_usage': data.get('vehicle_usage', data.get('usage')),
                'vehicle_energy': data.get('vehicle_energy', data.get('energie')),
                'circulation_zone': data.get('circulation_zone', data.get('zone_circulation')),
                'nb_of_seats': int(data.get('nb_of_seats', data.get('nombre_places', 5))),
                'fiscal_power': int(data.get('fiscal_power', data.get('puissance_fiscale', 5))),
                'vehicle_displacement': int(data.get('vehicle_displacement', data.get('cylindree', 0))),
                'vehicle_gross_weight': int(data.get('vehicle_gross_weight', data.get('ptac', 0))),
                'payload_capacity': int(data.get('payload_capacity', data.get('charge_utile', 0))),
                'vehicle_has_trailer': bool(data.get('vehicle_has_trailer', data.get('remorque', False))),
                'trailer_flammable': bool(data.get('trailer_flammable', data.get('remorque_inflammable', False))),
                'trailer_licence_plate': data.get('trailer_licence_plate', data.get('immatriculation_remorque', '')),
                'vehicle_dual_control': bool(data.get('vehicle_dual_control', data.get('double_commande', False))),
                'vehicle_engine_type': bool(data.get('vehicle_engine_type', data.get('engin_portuaire', False))),
                'civil_liability': bool(data.get('civil_liability', data.get('rc_eleves', False)))
            }
            
            # Créer le véhicule
            vehicle = self.controller.create_vehicle(vehicle_data)
            return {
                'success': True,
                'message': f'Véhicule {licence_plate} importé (ID: {vehicle.id})'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _import_fleet(self, data: Dict) -> Dict:
        """Importe une flotte depuis les données ASAC"""
        try:
            fleet_name = data.get('fleet_name', data.get('nom_flotte'))
            if not fleet_name:
                return {'success': False, 'error': 'Nom de flotte manquant'}
            
            # Récupérer les véhicules de la flotte
            vehicle_ids = []
            vehicles = data.get('vehicles', [])
            
            for v in vehicles:
                plate = v.get('licence_plate', v.get('immatriculation'))
                if plate:
                    # Chercher ou créer le véhicule
                    vehicle = self.controller.get_vehicle_by_plate(plate)
                    if not vehicle:
                        # Importer le véhicule
                        vehicle_result = self._import_vehicle(v)
                        if vehicle_result.get('success'):
                            vehicle = self.controller.get_vehicle_by_plate(plate)
                    
                    if vehicle:
                        vehicle_ids.append(vehicle.id)
            
            if not vehicle_ids:
                return {'success': False, 'error': 'Aucun véhicule valide dans la flotte'}
            
            # Créer la flotte avec ses véhicules
            fleet = self.controller.create_fleet_contract(
                name=fleet_name,
                owner_id=data.get('owner_id', 1),  # À adapter
                company_id=data.get('company_id', 1),  # À adapter
                vehicle_ids=vehicle_ids,
                discount=data.get('fleet_discount', 0)
            )
            
            return {
                'success': True,
                'message': f'Flotte {fleet_name} importée avec {len(vehicle_ids)} véhicules'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _parse_date(self, date_str):
        """Parse une date au format ISO ou variantes"""
        if not date_str:
            return None
        try:
            # Essayer différents formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y%m%d']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            return None
        except Exception:
            return None
    
    def stop(self):
        self._running = False


class ASACImportView(QWidget):
    """Vue d'importation des données ASAC"""
    
    def __init__(self, controller, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.import_worker = None
        self.data_preview = []
        self.import_results = []
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.LG)
        
        # En-tête
        self.setup_header()
        layout.addWidget(self.header_card)
        
        # Zone principale avec onglets
        self.setup_tabs()
        layout.addWidget(self.main_tabs)
        
        # Barre de progression
        self.setup_progress()
        layout.addWidget(self.progress_card)
    
    def setup_header(self):
        """Configure l'en-tête de la page"""
        self.header_card = ModernCard(title="Importation ASAC", icon="📥")
        
        header_layout = QHBoxLayout()
        header_layout.setSpacing(Spacing.XL)
        
        # Description
        desc_layout = QVBoxLayout()
        desc_label = QLabel("Importez en masse des véhicules et des flottes depuis le serveur ASAC")
        desc_label.setStyleSheet(f"font-size: {Fonts.BODY}px; color: {Colors.TEXT_SECONDARY};")
        desc_layout.addWidget(desc_label)
        
        # Métriques
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(Spacing.XL)
        
        self.vehicles_count = QLabel("🚗 0 véhicules")
        self.vehicles_count.setStyleSheet(f"font-size: {Fonts.SMALL}px; font-weight: {Fonts.MEDIUM};")
        stats_layout.addWidget(self.vehicles_count)
        
        self.fleets_count = QLabel("🏢 0 flottes")
        self.fleets_count.setStyleSheet(f"font-size: {Fonts.SMALL}px; font-weight: {Fonts.MEDIUM};")
        stats_layout.addWidget(self.fleets_count)
        
        desc_layout.addLayout(stats_layout)
        header_layout.addLayout(desc_layout)
        header_layout.addStretch()
        
        # Boutons rapides
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(Spacing.MD)
        
        self.sync_btn = QPushButton("🔄 Synchroniser avec ASAC")
        self.sync_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.PRIMARY};
                padding: 10px 20px;
            }}
        """)
        self.sync_btn.clicked.connect(self.sync_with_asac)
        
        self.import_btn = QPushButton("📥 Importer sélection")
        self.import_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.SUCCESS};
                padding: 10px 20px;
            }}
        """)
        self.import_btn.clicked.connect(self.import_selected)
        
        btn_layout.addWidget(self.sync_btn)
        btn_layout.addWidget(self.import_btn)
        header_layout.addLayout(btn_layout)
        
        self.header_card.add_layout(header_layout)
    
    def setup_tabs(self):
        """Configure les onglets principaux"""
        self.main_tabs = QTabWidget()
        self.main_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                background-color: {Colors.WHITE};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
            }}
            QTabBar::tab {{
                padding: 10px 20px;
                margin-right: 4px;
            }}
        """)
        
        # Onglet Véhicules
        vehicles_tab = self.create_vehicles_tab()
        self.main_tabs.addTab(vehicles_tab, "🚗 Véhicules")
        
        # Onglet Flottes
        fleets_tab = self.create_fleets_tab()
        self.main_tabs.addTab(fleets_tab, "🏢 Flottes")
        
        # Onglet Logs
        logs_tab = self.create_logs_tab()
        self.main_tabs.addTab(logs_tab, "📋 Logs")
    
    def create_vehicles_tab(self):
        """Crée l'onglet des véhicules"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(Spacing.MD)
        
        # Filtres
        filters_widget = QWidget()
        filters_layout = QHBoxLayout(filters_widget)
        filters_layout.setSpacing(Spacing.MD)
        
        self.search_vehicles = QLineEdit()
        self.search_vehicles.setPlaceholderText("🔍 Rechercher...")
        self.search_vehicles.textChanged.connect(self.filter_vehicles)
        filters_layout.addWidget(self.search_vehicles)
        
        self.vehicles_status_filter = QComboBox()
        self.vehicles_status_filter.addItems(["Tous", "À importer", "Déjà importé", "Erreur"])
        self.vehicles_status_filter.currentTextChanged.connect(self.filter_vehicles)
        filters_layout.addWidget(self.vehicles_status_filter)
        
        # Sélecteur de source
        self.source_combo = QComboBox()
        self.source_combo.addItems(["ASAC API", "Fichier JSON", "Fichier CSV"])
        self.source_combo.currentTextChanged.connect(self.change_source)
        filters_layout.addWidget(self.source_combo)
        
        filters_layout.addStretch()
        
        # Bouton charger
        load_btn = QPushButton("📂 Charger les données")
        load_btn.clicked.connect(self.load_data_from_source)
        filters_layout.addWidget(load_btn)
        
        layout.addWidget(filters_widget)
        
        # Tableau des véhicules
        self.vehicles_table = QTableWidget()
        self.vehicles_table.setColumnCount(8)
        self.vehicles_table.setHorizontalHeaderLabels([
            "✓", "Immatriculation", "Marque", "Modèle", "Catégorie",
            "Énergie", "Statut", "Actions"
        ])
        self.vehicles_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.vehicles_table.setAlternatingRowColors(True)
        self.vehicles_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Sélectionner toutes les lignes
        self.vehicles_table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        
        layout.addWidget(self.vehicles_table)
        
        # Barre d'actions
        action_bar = QHBoxLayout()
        
        self.select_all_vehicles = QCheckBox("Tout sélectionner")
        self.select_all_vehicles.stateChanged.connect(self.toggle_select_all_vehicles)
        action_bar.addWidget(self.select_all_vehicles)
        
        action_bar.addStretch()
        
        selected_label = QLabel("Sélectionnés: 0")
        selected_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        action_bar.addWidget(selected_label)
        
        self.vehicles_selected_count = selected_label
        
        layout.addLayout(action_bar)
        
        return tab
    
    def create_fleets_tab(self):
        """Crée l'onglet des flottes"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(Spacing.MD)
        
        # Filtres
        filters_widget = QWidget()
        filters_layout = QHBoxLayout(filters_widget)
        filters_layout.setSpacing(Spacing.MD)
        
        self.search_fleets = QLineEdit()
        self.search_fleets.setPlaceholderText("🔍 Rechercher...")
        self.search_fleets.textChanged.connect(self.filter_fleets)
        filters_layout.addWidget(self.search_fleets)
        
        self.fleets_status_filter = QComboBox()
        self.fleets_status_filter.addItems(["Toutes", "À importer", "Déjà importé", "Erreur"])
        self.fleets_status_filter.currentTextChanged.connect(self.filter_fleets)
        filters_layout.addWidget(self.fleets_status_filter)
        
        filters_layout.addStretch()
        
        layout.addWidget(filters_widget)
        
        # Tableau des flottes
        self.fleets_table = QTableWidget()
        self.fleets_table.setColumnCount(6)
        self.fleets_table.setHorizontalHeaderLabels([
            "✓", "Nom", "Véhicules", "Réduction", "Statut", "Actions"
        ])
        self.fleets_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.fleets_table.setAlternatingRowColors(True)
        self.fleets_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.fleets_table)
        
        # Barre d'actions
        action_bar = QHBoxLayout()
        
        self.select_all_fleets = QCheckBox("Tout sélectionner")
        self.select_all_fleets.stateChanged.connect(self.toggle_select_all_fleets)
        action_bar.addWidget(self.select_all_fleets)
        
        action_bar.addStretch()
        
        self.fleets_selected_count = QLabel("Sélectionnées: 0")
        self.fleets_selected_count.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        action_bar.addWidget(self.fleets_selected_count)
        
        layout.addLayout(action_bar)
        
        return tab
    
    def create_logs_tab(self):
        """Crée l'onglet des logs"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Filtres logs
        log_filters = QHBoxLayout()
        
        self.log_level_filter = QComboBox()
        self.log_level_filter.addItems(["Tous", "INFO", "SUCCESS", "WARNING", "ERROR"])
        self.log_level_filter.currentTextChanged.connect(self.filter_logs)
        log_filters.addWidget(QLabel("Niveau:"))
        log_filters.addWidget(self.log_level_filter)
        
        log_filters.addStretch()
        
        clear_logs_btn = QPushButton("🗑️ Effacer les logs")
        clear_logs_btn.clicked.connect(self.clear_logs)
        log_filters.addWidget(clear_logs_btn)
        
        layout.addLayout(log_filters)
        
        # Zone de logs
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setStyleSheet(f"""
            QTextEdit {{
                font-family: 'Courier New', monospace;
                font-size: 11px;
                background-color: #1e293b;
                color: #e2e8f0;
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        layout.addWidget(self.logs_text)
        
        return tab
    
    def setup_progress(self):
        """Configure la barre de progression"""
        self.progress_card = ModernCard(title="Progression", icon="⏳")
        
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(Spacing.SM)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(12)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 6px;
                background-color: {Colors.GRAY_100};
            }}
            QProgressBar::chunk {{
                background-color: {Colors.PRIMARY};
                border-radius: 6px;
            }}
        """)
        progress_layout.addWidget(self.progress_bar)
        
        # Statut de progression
        status_layout = QHBoxLayout()
        self.progress_status = QLabel("Prêt")
        self.progress_status.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Fonts.SMALL}px;")
        status_layout.addWidget(self.progress_status)
        
        self.progress_count = QLabel("0 / 0")
        self.progress_count.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Fonts.SMALL}px;")
        status_layout.addStretch()
        status_layout.addWidget(self.progress_count)
        
        progress_layout.addLayout(status_layout)
        self.progress_card.add_layout(progress_layout)
        
        # Masquer par défaut
        self.progress_card.setVisible(False)
    
    def load_data_from_source(self):
        """Charge les données depuis la source sélectionnée"""
        source = self.source_combo.currentText()
        
        if source == "ASAC API":
            self.load_from_api()
        elif source == "Fichier JSON":
            self.load_from_json()
        elif source == "Fichier CSV":
            self.load_from_csv()
    
    def load_from_api(self):
        """Charge les données depuis l'API ASAC"""
        self.add_log("🔄 Connexion à l'API ASAC...", "INFO")
        self.set_progress_visible(True)
        self.progress_bar.setRange(0, 0)
        self.progress_status.setText("Connexion en cours...")
        
        # Simuler un appel API
        QTimer.singleShot(2000, self._simulate_api_response)
    
    def _simulate_api_response(self):
        """Simule une réponse de l'API ASAC (à remplacer par un vrai appel)"""
        self.add_log("✅ Connexion à l'API ASAC réussie", "SUCCESS")
        
        # Données simulées
        self.data_preview = [
            {
                'licence_plate': 'LS-123-AB',
                'vehicle_brand': 'Toyota',
                'vehicle_model': 'Corolla',
                'vehicle_category': 'VP10',
                'vehicle_energy': 'SEE',
                'nb_of_seats': 5,
                'fiscal_power': 5
            },
            {
                'licence_plate': 'LT-456-CD',
                'vehicle_brand': 'Renault',
                'vehicle_model': 'Clio',
                'vehicle_category': 'VP10',
                'vehicle_energy': 'SED',
                'nb_of_seats': 5,
                'fiscal_power': 4
            },
            {
                'licence_plate': 'LE-789-EF',
                'vehicle_brand': 'Mercedes',
                'vehicle_model': 'C220',
                'vehicle_category': 'VP10',
                'vehicle_energy': 'SED',
                'nb_of_seats': 5,
                'fiscal_power': 8
            },
        ]
        
        self.populate_vehicles_table()
        self.add_log(f"📊 {len(self.data_preview)} véhicules chargés", "INFO")
        
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.progress_status.setText("Chargement terminé")
        self.progress_count.setText(f"{len(self.data_preview)} / {len(self.data_preview)}")
        
        QTimer.singleShot(1000, lambda: self.set_progress_visible(False))
    
    def load_from_json(self):
        """Charge les données depuis un fichier JSON"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner un fichier JSON", "", "JSON Files (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                self.data_preview = data
            elif isinstance(data, dict) and 'vehicles' in data:
                self.data_preview = data['vehicles']
            else:
                self.data_preview = [data]
            
            self.populate_vehicles_table()
            self.add_log(f"✅ {len(self.data_preview)} véhicules chargés depuis {file_path}", "SUCCESS")
            
        except Exception as e:
            self.add_log(f"❌ Erreur de chargement: {str(e)}", "ERROR")
            QMessageBox.critical(self, "Erreur", f"Erreur de chargement: {str(e)}")
    
    def load_from_csv(self):
        """Charge les données depuis un fichier CSV"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner un fichier CSV", "", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            import csv
            self.data_preview = []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.data_preview.append(row)
            
            self.populate_vehicles_table()
            self.add_log(f"✅ {len(self.data_preview)} véhicules chargés depuis {file_path}", "SUCCESS")
            
        except Exception as e:
            self.add_log(f"❌ Erreur de chargement: {str(e)}", "ERROR")
            QMessageBox.critical(self, "Erreur", f"Erreur de chargement: {str(e)}")
    
    def populate_vehicles_table(self):
        """Remplit le tableau des véhicules"""
        self.vehicles_table.setRowCount(len(self.data_preview))
        
        for row, vehicle in enumerate(self.data_preview):
            # Case à cocher
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(lambda state, r=row: self.update_selected_count())
            self.vehicles_table.setCellWidget(row, 0, checkbox)
            
            # Données
            self.vehicles_table.setItem(row, 1, QTableWidgetItem(
                vehicle.get('licence_plate', vehicle.get('immatriculation', '-')))
            )
            self.vehicles_table.setItem(row, 2, QTableWidgetItem(
                vehicle.get('vehicle_brand', vehicle.get('marque', '-')))
            )
            self.vehicles_table.setItem(row, 3, QTableWidgetItem(
                vehicle.get('vehicle_model', vehicle.get('modele', '-')))
            )
            self.vehicles_table.setItem(row, 4, QTableWidgetItem(
                vehicle.get('vehicle_category', vehicle.get('categorie', '-')))
            )
            self.vehicles_table.setItem(row, 5, QTableWidgetItem(
                vehicle.get('vehicle_energy', vehicle.get('energie', '-')))
            )
            
            # Statut (simulé)
            status_item = QTableWidgetItem("À importer")
            status_item.setForeground(QColor(Colors.WARNING))
            self.vehicles_table.setItem(row, 6, status_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            view_btn = QPushButton("👁️")
            view_btn.setFixedSize(24, 24)
            view_btn.setToolTip("Voir détails")
            view_btn.clicked.connect(lambda checked, r=row: self.view_vehicle_details(r))
            actions_layout.addWidget(view_btn)
            
            self.vehicles_table.setCellWidget(row, 7, actions_widget)
        
        self.vehicles_table.resizeColumnsToContents()
        self.update_selected_count()
    
    def populate_fleets_table(self):
        """Remplit le tableau des flottes"""
        # Simuler des flottes
        fleets = [
            {'name': 'Flotte Entreprise A', 'vehicles': 12, 'discount': 10},
            {'name': 'Flotte Société B', 'vehicles': 8, 'discount': 15},
            {'name': 'Flotte Groupe C', 'vehicles': 25, 'discount': 20},
        ]
        
        self.fleets_table.setRowCount(len(fleets))
        
        for row, fleet in enumerate(fleets):
            checkbox = QCheckBox()
            self.fleets_table.setCellWidget(row, 0, checkbox)
            
            self.fleets_table.setItem(row, 1, QTableWidgetItem(fleet['name']))
            self.fleets_table.setItem(row, 2, QTableWidgetItem(str(fleet['vehicles'])))
            self.fleets_table.setItem(row, 3, QTableWidgetItem(f"{fleet['discount']}%"))
            
            status_item = QTableWidgetItem("À importer")
            status_item.setForeground(QColor(Colors.WARNING))
            self.fleets_table.setItem(row, 4, status_item)
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            view_btn = QPushButton("👁️")
            view_btn.setFixedSize(24, 24)
            actions_layout.addWidget(view_btn)
            
            self.fleets_table.setCellWidget(row, 5, actions_widget)
        
        self.fleets_table.resizeColumnsToContents()
    
    def import_selected(self):
        """Importe les éléments sélectionnés"""
        selected = self.get_selected_vehicles()
        
        if not selected:
            QMessageBox.warning(self, "Aucune sélection", 
                               "Veuillez sélectionner au moins un véhicule à importer.")
            return
        
        # Confirmation
        reply = QMessageBox.question(
            self, "Confirmation d'import",
            f"Voulez-vous importer {len(selected)} véhicules ?\n\n"
            "Cette action va créer les véhicules dans la base de données.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Démarrer l'import
        self.start_import('vehicles', selected)
    
    def start_import(self, import_type, data):
        """Démarre l'importation dans un thread séparé"""
        self.set_progress_visible(True)
        self.progress_bar.setValue(0)
        self.progress_status.setText("Importation en cours...")
        self.progress_count.setText(f"0 / {len(data)}")
        
        options = {
            'allow_duplicates': False,
            'validate_only': False
        }
        
        self.import_worker = ASACImportWorker(import_type, data, self.controller, options)
        self.import_worker.progress_updated.connect(self.update_progress)
        self.import_worker.log_updated.connect(self.add_log)
        self.import_worker.finished.connect(self.on_import_finished)
        self.import_worker.error.connect(self.on_import_error)
        self.import_worker.start()
        
        self.import_btn.setEnabled(False)
        self.sync_btn.setEnabled(False)
        self.add_log("🚀 Démarrage de l'importation...", "INFO")
    
    def update_progress(self, current, total, status):
        """Met à jour la barre de progression"""
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
        self.progress_status.setText(status)
        self.progress_count.setText(f"{current} / {total}")
    
    def on_import_finished(self, results):
        """Appelé à la fin de l'importation"""
        self.import_btn.setEnabled(True)
        self.sync_btn.setEnabled(True)
        self.set_progress_visible(False)
        
        # Afficher le résumé
        summary = (
            f"📊 Résumé de l'importation:\n"
            f"✅ Importés: {results['imported']}\n"
            f"⏭️ Ignorés: {results['skipped']}\n"
            f"❌ Échecs: {results['failed']}\n"
            f"📦 Total: {results['total']}"
        )
        
        self.add_log(summary, "SUCCESS")
        
        # Mettre à jour le statut des éléments importés
        self.update_import_status(results)
        
        # Afficher le résultat
        msg = f"Importation terminée!\n\n{summary}"
        if results['failed'] > 0:
            msg += f"\n\nErreurs:\n" + "\n".join(results['errors'][:5])
            if len(results['errors']) > 5:
                msg += f"\n... et {len(results['errors']) - 5} autres erreurs"
            QMessageBox.warning(self, "Importation terminée avec erreurs", msg)
        else:
            QMessageBox.information(self, "Importation réussie", msg)
        
        self.import_results = results['details']
    
    def on_import_error(self, error_msg):
        """Appelé en cas d'erreur d'import"""
        self.import_btn.setEnabled(True)
        self.sync_btn.setEnabled(True)
        self.set_progress_visible(False)
        self.add_log(f"❌ Erreur d'importation: {error_msg}", "ERROR")
        QMessageBox.critical(self, "Erreur", f"Erreur d'importation: {error_msg}")
    
    def update_import_status(self, results):
        """Met à jour le statut des éléments dans le tableau"""
        for i, detail in enumerate(results.get('details', [])):
            if i < self.vehicles_table.rowCount():
                status = detail.get('status', 'UNKNOWN')
                status_text = {
                    'SUCCESS': '✅ Importé',
                    'SKIPPED': '⏭️ Ignoré',
                    'ERROR': '❌ Erreur'
                }.get(status, status)
                
                status_item = QTableWidgetItem(status_text)
                color = {
                    'SUCCESS': Colors.SUCCESS,
                    'SKIPPED': Colors.WARNING,
                    'ERROR': Colors.DANGER
                }.get(status, Colors.TEXT_SECONDARY)
                status_item.setForeground(QColor(color))
                self.vehicles_table.setItem(i, 6, status_item)
    
    def get_selected_vehicles(self):
        """Récupère les véhicules sélectionnés"""
        selected = []
        for row in range(self.vehicles_table.rowCount()):
            checkbox = self.vehicles_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                if row < len(self.data_preview):
                    selected.append(self.data_preview[row])
        return selected
    
    def update_selected_count(self):
        """Met à jour le compteur de sélection"""
        count = len(self.get_selected_vehicles())
        self.vehicles_selected_count.setText(f"Sélectionnés: {count}")
    
    def toggle_select_all_vehicles(self, state):
        """Sélectionne/désélectionne tous les véhicules"""
        for row in range(self.vehicles_table.rowCount()):
            checkbox = self.vehicles_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(state == Qt.CheckState.Checked)
    
    def toggle_select_all_fleets(self, state):
        """Sélectionne/désélectionne toutes les flottes"""
        for row in range(self.fleets_table.rowCount()):
            checkbox = self.fleets_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(state == Qt.CheckState.Checked)
    
    def filter_vehicles(self):
        """Filtre la liste des véhicules"""
        search = self.search_vehicles.text().lower()
        status_filter = self.vehicles_status_filter.currentText()
        
        for row in range(self.vehicles_table.rowCount()):
            visible = True
            if search:
                plate = self.vehicles_table.item(row, 1)
                brand = self.vehicles_table.item(row, 2)
                model = self.vehicles_table.item(row, 3)
                
                visible = (
                    (plate and search in plate.text().lower()) or
                    (brand and search in brand.text().lower()) or
                    (model and search in model.text().lower())
                )
            
            if visible and status_filter != "Tous":
                status_item = self.vehicles_table.item(row, 6)
                if status_item:
                    status_map = {
                        "À importer": "À importer",
                        "Déjà importé": "Déjà importé",
                        "Erreur": "Erreur"
                    }
                    visible = status_filter in status_item.text()
            
            self.vehicles_table.setRowHidden(row, not visible)
    
    def filter_fleets(self):
        """Filtre la liste des flottes"""
        search = self.search_fleets.text().lower()
        status_filter = self.fleets_status_filter.currentText()
        
        for row in range(self.fleets_table.rowCount()):
            visible = True
            if search:
                name = self.fleets_table.item(row, 1)
                if name:
                    visible = search in name.text().lower()
            
            if visible and status_filter != "Toutes":
                status_item = self.fleets_table.item(row, 4)
                if status_item:
                    visible = status_filter in status_item.text()
            
            self.fleets_table.setRowHidden(row, not visible)
    
    def filter_logs(self):
        """Filtre les logs par niveau"""
        level = self.log_level_filter.currentText()
        if level == "Tous":
            return
        
        cursor = self.logs_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        
        # Mettre en évidence les logs du niveau sélectionné
        # (implémentation simplifiée)
    
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
        formatted = f'<span style="color: #64748b;">[{timestamp}]</span> <span style="color: {color};">{message}</span><br>'
        
        self.logs_text.append(formatted)
        
        # Scroll en bas
        cursor = self.logs_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.logs_text.setTextCursor(cursor)
    
    def clear_logs(self):
        """Efface les logs"""
        self.logs_text.clear()
        self.add_log("🗑️ Logs effacés", "INFO")
    
    def set_progress_visible(self, visible):
        """Affiche ou masque la barre de progression"""
        self.progress_card.setVisible(visible)
    
    def change_source(self, source):
        """Change la source de données"""
        self.add_log(f"🔀 Changement de source: {source}", "INFO")
        self.data_preview = []
        self.vehicles_table.setRowCount(0)
        self.vehicles_selected_count.setText("Sélectionnés: 0")
    
    def view_vehicle_details(self, row):
        """Affiche les détails d'un véhicule"""
        if row < len(self.data_preview):
            vehicle = self.data_preview[row]
            details = json.dumps(vehicle, indent=2, default=str)
            QMessageBox.information(self, "Détails du véhicule", details)
    
    def sync_with_asac(self):
        """Synchronise les données avec ASAC"""
        self.add_log("🔄 Synchronisation avec ASAC...", "INFO")
        self.load_from_api()
    
    def refresh_data(self):
        """Rafraîchit les données"""
        self.load_from_api()

    # addons/Automobiles/views/asac_import_view.py - Méthodes supplémentaires à ajouter

    def on_header_clicked(self, index):
        """Gère le clic sur l'en-tête du tableau"""
        if index == 0:  # Colonne de sélection
            all_checked = True
            for row in range(self.vehicles_table.rowCount()):
                checkbox = self.vehicles_table.cellWidget(row, 0)
                if checkbox and not checkbox.isChecked():
                    all_checked = False
                    break
            
            new_state = not all_checked
            for row in range(self.vehicles_table.rowCount()):
                checkbox = self.vehicles_table.cellWidget(row, 0)
                if checkbox:
                    checkbox.setChecked(new_state)
            
            if hasattr(self, 'select_all_vehicles'):
                self.select_all_vehicles.setChecked(new_state)
            
            self.update_selected_count()

    def on_fleets_header_clicked(self, index):
        """Gère le clic sur l'en-tête du tableau des flottes"""
        if index == 0:
            all_checked = True
            for row in range(self.fleets_table.rowCount()):
                checkbox = self.fleets_table.cellWidget(row, 0)
                if checkbox and not checkbox.isChecked():
                    all_checked = False
                    break
            
            new_state = not all_checked
            for row in range(self.fleets_table.rowCount()):
                checkbox = self.fleets_table.cellWidget(row, 0)
                if checkbox:
                    checkbox.setChecked(new_state)
            
            if hasattr(self, 'select_all_fleets'):
                self.select_all_fleets.setChecked(new_state)
            
            self.update_fleets_selected_count()

    def update_fleets_selected_count(self):
        """Met à jour le compteur de sélection des flottes"""
        count = 0
        for row in range(self.fleets_table.rowCount()):
            checkbox = self.fleets_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                count += 1
        self.fleets_selected_count.setText(f"Sélectionnées: {count}")

    def get_selected_fleets(self):
        """Récupère les flottes sélectionnées"""
        selected = []
        # Les données des flottes ne sont pas stockées dans data_preview
        # On utilise le tableau directement
        for row in range(self.fleets_table.rowCount()):
            checkbox = self.fleets_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                name_item = self.fleets_table.item(row, 1)
                if name_item:
                    selected.append({
                        'name': name_item.text(),
                        'vehicles': int(self.fleets_table.item(row, 2).text()) if self.fleets_table.item(row, 2) else 0,
                        'discount': int(self.fleets_table.item(row, 3).text().replace('%', '')) if self.fleets_table.item(row, 3) else 0
                    })
        return selected

    def import_selected_fleets(self):
        """Importe les flottes sélectionnées"""
        selected = self.get_selected_fleets()
        
        if not selected:
            QMessageBox.warning(self, "Aucune sélection", 
                            "Veuillez sélectionner au moins une flotte à importer.")
            return
        
        reply = QMessageBox.question(
            self, "Confirmation d'import",
            f"Voulez-vous importer {len(selected)} flottes ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        self.start_import('fleets', selected)