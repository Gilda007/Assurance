# fleet_import_dialog.py - Version avec prévisualisation complète
"""
Dialogue d'importation de flotte depuis un fichier Excel/CSV
Avec prévisualisation complète du document
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QTableWidget, QTableWidgetItem, QProgressBar,
    QMessageBox, QFrame, QComboBox, QGroupBox, QRadioButton,
    QButtonGroup, QScrollArea, QSplitter, QTabWidget, QTextEdit,
    QCheckBox, QHeaderView, QWidget, QApplication
)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QFont, QColor, QTextCursor, QPalette
import pandas as pd
import os
import traceback


class FleetImportThread(QThread):
    """Thread pour l'importation des flottes"""
    progress_update = Signal(int, str)
    log_update = Signal(str)
    finished = Signal(bool, str, dict)
    
    def __init__(self, controller, file_path, fleet_name, import_mode, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.file_path = file_path
        self.fleet_name = fleet_name
        self.import_mode = import_mode  # 'new' ou 'existing'
        self.existing_fleet_id = None
        self.is_cancelled = False
        
    def cancel(self):
        self.is_cancelled = True
        
    def run(self):
        try:
            # Lire le fichier complet
            if self.file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(self.file_path)
            else:
                # Essayer différents encodages pour CSV
                encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
                df = None
                for encoding in encodings:
                    try:
                        df = pd.read_csv(self.file_path, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                if df is None:
                    raise Exception("Impossible de lire le fichier CSV avec les encodages standards")
            
            total_rows = len(df)
            self.progress_update.emit(0, f"Chargement du fichier... ({total_rows} véhicules)")
            
            # Vérifier les colonnes requises
            required_columns = ['immatriculation', 'marque', 'modele']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                self.finished.emit(False, f"Colonnes manquantes: {', '.join(missing_columns)}", {})
                return
            
            # Nettoyer les données
            df = df.where(pd.notnull(df), None)
            
            # Créer ou récupérer la flotte
            fleet_id = None
            
            if self.import_mode == 'new':
                # Créer une nouvelle flotte
                fleet_data = {
                    'nom_flotte': self.fleet_name,
                    'owner_id': self.controller.current_contact_id if hasattr(self.controller, 'current_contact_id') else None,
                    'statut': 'Actif'
                }
                
                success, result = self.controller.fleets.create_fleet(fleet_data)
                if not success:
                    self.finished.emit(False, f"Erreur création flotte: {result}", {})
                    return
                fleet_id = result.id if hasattr(result, 'id') else result
                self.log_update.emit(f"✅ Flotte créée: {self.fleet_name}")
                
            else:
                fleet_id = self.existing_fleet_id
                self.log_update.emit(f"📦 Importation dans la flotte existante ID: {fleet_id}")
            
            # Importer les véhicules
            created_vehicles = []
            failed_vehicles = []
            
            for idx, row in df.iterrows():
                if self.is_cancelled:
                    self.finished.emit(False, "Importation annulée par l'utilisateur", {})
                    return
                
                # Progression
                progress = int((idx + 1) / total_rows * 100)
                immat = str(row.get('immatriculation', 'N/A')) if row.get('immatriculation') else 'N/A'
                self.progress_update.emit(progress, f"Importation véhicule {idx+1}/{total_rows}: {immat}")
                
                # Préparer les données du véhicule
                vehicle_data = {
                    'immatriculation': str(row.get('immatriculation', '')).strip().upper(),
                    'marque': str(row.get('marque', '')).strip(),
                    'modele': str(row.get('modele', '')).strip(),
                    'annee': int(row.get('annee', 0)) if row.get('annee') and pd.notna(row.get('annee')) else None,
                    'energie': str(row.get('energie', 'Essence')).strip() if row.get('energie') and pd.notna(row.get('energie')) else 'Essence',
                    'chassis': str(row.get('chassis', '')).strip() if row.get('chassis') and pd.notna(row.get('chassis')) else None,
                    'categorie': str(row.get('categorie', 'VP')).strip() if row.get('categorie') and pd.notna(row.get('categorie')) else 'VP',
                    'usage': str(row.get('usage', 'Particulier')).strip() if row.get('usage') and pd.notna(row.get('usage')) else 'Particulier',
                    'places': int(row.get('places', 5)) if row.get('places') and pd.notna(row.get('places')) else 5,
                    'valeur_neuf': float(row.get('valeur_neuf', 0)) if row.get('valeur_neuf') and pd.notna(row.get('valeur_neuf')) else 0,
                    'valeur_venale': float(row.get('valeur_venale', 0)) if row.get('valeur_venale') and pd.notna(row.get('valeur_venale')) else 0,
                    'owner_id': self.controller.current_contact_id if hasattr(self.controller, 'current_contact_id') else None,
                    'fleet_id': fleet_id,
                    'carte_rose': str(row.get('carte_rose', '')).strip() if row.get('carte_rose') and pd.notna(row.get('carte_rose')) else None,
                    'code_tarif': str(row.get('code_tarif', '')).strip() if row.get('code_tarif') and pd.notna(row.get('code_tarif')) else None,
                    'zone': str(row.get('zone', '')).strip() if row.get('zone') and pd.notna(row.get('zone')) else None
                }
                
                # Vérifier que l'immatriculation est valide
                if not vehicle_data['immatriculation'] or vehicle_data['immatriculation'] == 'N/A':
                    failed_vehicles.append({
                        'immatriculation': f"Ligne {idx+2}",
                        'error': "Immatriculation manquante"
                    })
                    self.log_update.emit(f"  ✗ Ligne {idx+2} - Immatriculation manquante")
                    continue
                
                # Créer le véhicule
                success, result = self.controller.vehicles.create_vehicle(vehicle_data)
                
                if success:
                    created_vehicles.append({
                        'immatriculation': vehicle_data['immatriculation'],
                        'id': result.id if hasattr(result, 'id') else result
                    })
                    self.log_update.emit(f"  ✓ {vehicle_data['immatriculation']} importé")
                else:
                    failed_vehicles.append({
                        'immatriculation': vehicle_data['immatriculation'],
                        'error': str(result)
                    })
                    self.log_update.emit(f"  ✗ {vehicle_data['immatriculation']} - Erreur: {result}")
            
            # Résumé
            summary = {
                'fleet_id': fleet_id,
                'fleet_name': self.fleet_name if self.import_mode == 'new' else "Flotte existante",
                'total': total_rows,
                'created': len(created_vehicles),
                'failed': len(failed_vehicles),
                'failed_list': failed_vehicles,
                'df_head': df.head(20).to_dict() if len(df) > 0 else {}
            }
            
            if len(created_vehicles) > 0:
                self.finished.emit(True, f"Importation terminée: {len(created_vehicles)}/{total_rows} véhicules importés", summary)
            else:
                self.finished.emit(False, "Aucun véhicule n'a pu être importé", summary)
                
        except Exception as e:
            traceback.print_exc()
            self.finished.emit(False, f"Erreur lors de l'importation: {str(e)}", {})


class PreviewTableWidget(QTableWidget):
    """Tableau de prévisualisation amélioré"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background: white;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background: #f8fafc;
                padding: 10px;
                font-weight: 600;
                color: #1e293b;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
            QTableWidget::item:selected {
                background: #dbeafe;
            }
        """)
        
    def display_dataframe(self, df, max_rows=None):
        """Affiche un dataframe dans le tableau"""
        if df is None or len(df) == 0:
            self.setRowCount(0)
            self.setColumnCount(0)
            return
        
        # Limiter le nombre de lignes si nécessaire
        display_df = df if max_rows is None else df.head(max_rows)
        
        self.setColumnCount(len(display_df.columns))
        self.setHorizontalHeaderLabels(display_df.columns)
        self.setRowCount(len(display_df))
        
        # Remplir les données
        for i in range(len(display_df)):
            for j, col in enumerate(display_df.columns):
                value = display_df.iloc[i][col]
                if pd.isna(value):
                    text = ""
                else:
                    text = str(value)
                item = QTableWidgetItem(text)
                item.setToolTip(text)  # Tooltip pour voir le contenu complet
                self.setItem(i, j, item)
        
        # Ajuster les colonnes
        self.resizeColumnsToContents()
        
        # Limiter la largeur maximale des colonnes
        for j in range(self.columnCount()):
            if self.columnWidth(j) > 300:
                self.setColumnWidth(j, 300)


class FleetImportDialog(QDialog):
    """Dialogue d'importation de flotte avec prévisualisation complète"""
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.file_path = None
        self.import_thread = None
        self.df_full = None  # Stocker le dataframe complet
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Importation de flotte")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        self.setModal(True)
        
        # Style global
        self.setStyleSheet("""
            QDialog {
                background: #f8fafc;
            }
            QGroupBox {
                font-weight: 600;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 12px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                color: #1e293b;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Splitter principal
        main_splitter = QSplitter(Qt.Vertical)
        
        # ==================== PARTIE HAUTE ====================
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setSpacing(16)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Section fichier
        file_group = QGroupBox("1. Sélection du fichier")
        file_layout = QVBoxLayout(file_group)
        
        # Sélection fichier
        file_select_layout = QHBoxLayout()
        
        self.file_label = QLabel("Aucun fichier sélectionné")
        self.file_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                padding: 12px;
                background: #f8fafc;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
                font-family: monospace;
            }
        """)
        
        self.btn_select_file = QPushButton("📂 Parcourir")
        self.btn_select_file.clicked.connect(self.select_file)
        self.btn_select_file.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        
        file_select_layout.addWidget(self.file_label, stretch=1)
        file_select_layout.addWidget(self.btn_select_file)
        file_layout.addLayout(file_select_layout)
        
        # Info format
        format_info = QHBoxLayout()
        format_label = QLabel("📄 Formats acceptés: .xlsx, .xls, .csv")
        format_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
        
        self.file_info_label = QLabel("")
        self.file_info_label.setStyleSheet("color: #10b981; font-size: 11px;")
        
        format_info.addWidget(format_label)
        format_info.addStretch()
        format_info.addWidget(self.file_info_label)
        file_layout.addLayout(format_info)
        
        top_layout.addWidget(file_group)
        
        # Section configuration flotte
        fleet_group = QGroupBox("2. Configuration de la flotte")
        fleet_layout = QVBoxLayout(fleet_group)
        
        # Mode d'import
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode d'importation:"))
        
        self.mode_new = QRadioButton("✨ Créer une nouvelle flotte")
        self.mode_existing = QRadioButton("📦 Ajouter à une flotte existante")
        self.mode_new.setChecked(True)
        
        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.mode_new)
        self.mode_group.addButton(self.mode_existing)
        
        mode_layout.addWidget(self.mode_new)
        mode_layout.addWidget(self.mode_existing)
        mode_layout.addStretch()
        fleet_layout.addLayout(mode_layout)
        
        # Nouvelle flotte
        self.new_fleet_widget = QWidget()
        new_fleet_layout = QHBoxLayout(self.new_fleet_widget)
        new_fleet_layout.addWidget(QLabel("Nom de la flotte:"))
        self.fleet_name_input = QComboBox()
        self.fleet_name_input.setEditable(True)
        self.fleet_name_input.setPlaceholderText("Entrez le nom de la flotte...")
        self.fleet_name_input.setMinimumWidth(300)
        self.fleet_name_input.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background: white;
            }
        """)
        new_fleet_layout.addWidget(self.fleet_name_input, stretch=1)
        fleet_layout.addWidget(self.new_fleet_widget)
        
        # Flotte existante
        self.existing_fleet_widget = QWidget()
        self.existing_fleet_widget.setVisible(False)
        existing_fleet_layout = QHBoxLayout(self.existing_fleet_widget)
        existing_fleet_layout.addWidget(QLabel("Sélectionner la flotte:"))
        self.existing_fleet_combo = QComboBox()
        self.existing_fleet_combo.setMinimumWidth(300)
        self.existing_fleet_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background: white;
            }
        """)
        self.load_existing_fleets()
        existing_fleet_layout.addWidget(self.existing_fleet_combo, stretch=1)
        
        # Bouton rafraîchir
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(32, 32)
        refresh_btn.setToolTip("Rafraîchir la liste des flottes")
        refresh_btn.clicked.connect(self.load_existing_fleets)
        refresh_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                background: white;
            }
            QPushButton:hover {
                background: #f1f5f9;
            }
        """)
        existing_fleet_layout.addWidget(refresh_btn)
        
        fleet_layout.addWidget(self.existing_fleet_widget)
        
        # Connecter les radios
        self.mode_new.toggled.connect(self.on_mode_changed)
        
        top_layout.addWidget(fleet_group)
        
        # ==================== PARTIE BASSE (Prévisualisation) ====================
        preview_group = QGroupBox("3. Prévisualisation des données")
        preview_layout = QVBoxLayout(preview_group)
        
        # Barre d'outils de prévisualisation
        preview_toolbar = QHBoxLayout()
        
        self.total_rows_label = QLabel("0 lignes")
        self.total_rows_label.setStyleSheet("color: #64748b; font-weight: 500;")
        
        self.show_all_checkbox = QCheckBox("Afficher tout le document")
        self.show_all_checkbox.setEnabled(False)
        self.show_all_checkbox.toggled.connect(self.toggle_preview_mode)
        self.show_all_checkbox.setStyleSheet("""
            QCheckBox {
                color: #475569;
            }
        """)
        
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(['utf-8', 'latin1', 'iso-8859-1', 'cp1252'])
        self.encoding_combo.setVisible(False)  # Caché par défaut, visible pour CSV
        self.encoding_combo.currentTextChanged.connect(self.reload_file)
        
        preview_toolbar.addWidget(self.total_rows_label)
        preview_toolbar.addStretch()
        preview_toolbar.addWidget(self.show_all_checkbox)
        preview_toolbar.addWidget(QLabel("Encodage:"))
        preview_toolbar.addWidget(self.encoding_combo)
        
        preview_layout.addLayout(preview_toolbar)
        
        # Onglets de prévisualisation
        self.preview_tabs = QTabWidget()
        self.preview_tabs.setStyleSheet("""
            QTabWidget::pane {
                background: white;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
            }
            QTabBar::tab {
                padding: 8px 16px;
                background: #f1f5f9;
            }
            QTabBar::tab:selected {
                background: white;
            }
        """)
        
        # Onglet Tableau
        self.table_preview = PreviewTableWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.table_preview)
        scroll_area.setWidgetResizable(True)
        self.preview_tabs.addTab(scroll_area, "📊 Vue tableau")
        
        # Onglet Texte brut
        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(True)
        self.text_preview.setFont(QFont("Courier New", 10))
        self.text_preview.setStyleSheet("""
            QTextEdit {
                border: none;
                background: #1e1e2e;
                color: #cdd6f4;
            }
        """)
        self.preview_tabs.addTab(self.text_preview, "📝 Vue texte brut")
        
        # Onglet Statistiques
        self.stats_preview = QTextEdit()
        self.stats_preview.setReadOnly(True)
        self.stats_preview.setStyleSheet("""
            QTextEdit {
                border: none;
                background: #f8fafc;
                font-family: monospace;
            }
        """)
        self.preview_tabs.addTab(self.stats_preview, "📈 Statistiques")
        
        preview_layout.addWidget(self.preview_tabs, stretch=1)
        
        top_layout.addWidget(preview_group)
        
        # Ajouter au splitter
        main_splitter.addWidget(top_widget)
        
        # ==================== PARTIE PROGRESSION ====================
        progress_widget = QWidget()
        progress_layout = QVBoxLayout(progress_widget)
        progress_layout.setSpacing(10)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                text-align: center;
                height: 30px;
                background: white;
            }
            QProgressBar::chunk {
                background: #3b82f6;
                border-radius: 7px;
            }
        """)
        
        self.log_text = QTextEdit()
        self.log_text.setVisible(False)
        self.log_text.setMaximumHeight(200)
        self.log_text.setFont(QFont("Courier New", 9))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background: #1e1e2e;
                color: #cdd6f4;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.log_text)
        
        main_splitter.addWidget(progress_widget)
        
        # Définir les tailles initiales du splitter
        main_splitter.setSizes([600, 200])
        
        main_layout.addWidget(main_splitter, stretch=1)
        
        # ==================== BOUTONS ====================
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.btn_import = QPushButton("🚀 Importer")
        self.btn_import.setEnabled(False)
        self.btn_import.clicked.connect(self.start_import)
        self.btn_import.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 28px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #059669;
            }
            QPushButton:disabled {
                background: #cbd5e1;
            }
        """)
        
        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.clicked.connect(self.cancel_import)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                color: #475569;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 12px 24px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #e2e8f0;
            }
        """)
        
        button_layout.addWidget(self.btn_cancel)
        button_layout.addWidget(self.btn_import)
        main_layout.addLayout(button_layout)
        
    def load_existing_fleets(self):
        """Charge les flottes existantes pour le contact"""
        try:
            contact_id = getattr(self.controller, 'current_contact_id', None)
            if not contact_id and hasattr(self.parent(), 'contact'):
                contact_id = self.parent().contact.id
            
            if contact_id:
                fleets = self.controller.fleets.get_fleets_by_owner(contact_id)
                self.existing_fleet_combo.clear()
                
                if fleets:
                    for fleet in fleets:
                        fleet_name = getattr(fleet, 'nom_flotte', getattr(fleet, 'nom', 'Sans nom'))
                        self.existing_fleet_combo.addItem(f"🚛 {fleet_name}", fleet.id)
                else:
                    self.existing_fleet_combo.addItem("Aucune flotte disponible", None)
        except Exception as e:
            print(f"Erreur chargement flottes: {e}")
    
    def on_mode_changed(self):
        """Change le mode d'importation"""
        is_new = self.mode_new.isChecked()
        self.new_fleet_widget.setVisible(is_new)
        self.existing_fleet_widget.setVisible(not is_new)
        
    def select_file(self):
        """Sélectionne le fichier à importer"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un fichier",
            "",
            "Fichiers Excel (*.xlsx *.xls);;Fichiers CSV (*.csv);;Tous les fichiers (*.*)"
        )
        
        if file_path:
            self.file_path = file_path
            self.file_label.setText(f"📄 {os.path.basename(file_path)}")
            
            # Afficher l'encodage pour les CSV
            is_csv = file_path.endswith('.csv')
            self.encoding_combo.setVisible(is_csv)
            
            # Charger et prévisualiser
            self.load_and_preview()
            
    def load_and_preview(self):
        """Charge le fichier et met à jour la prévisualisation"""
        try:
            if not self.file_path:
                return
            
            encoding = self.encoding_combo.currentText() if self.encoding_combo.isVisible() else None
            
            # Charger le fichier complet
            if self.file_path.endswith(('.xlsx', '.xls')):
                self.df_full = pd.read_excel(self.file_path)
                self.file_info_label.setText(f"✅ {len(self.df_full)} lignes chargées")
            else:
                # Essayer l'encodage sélectionné
                self.df_full = pd.read_csv(self.file_path, encoding=encoding)
                self.file_info_label.setText(f"✅ {len(self.df_full)} lignes chargées (encodage: {encoding})")
            
            # Mettre à jour l'UI
            self.total_rows_label.setText(f"📊 {len(self.df_full)} lignes, {len(self.df_full.columns)} colonnes")
            self.show_all_checkbox.setEnabled(True)
            self.btn_import.setEnabled(True)
            
            # Afficher la prévisualisation (mode tableau par défaut)
            self.update_preview()
            
            # Générer les statistiques
            self.generate_statistics()
            
            # Afficher le texte brut
            self.show_raw_text()
            
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger le fichier: {str(e)}")
            self.df_full = None
            self.show_all_checkbox.setEnabled(False)
            self.btn_import.setEnabled(False)
            self.total_rows_label.setText("0 lignes")
    
    def reload_file(self):
        """Recharge le fichier avec un nouvel encodage"""
        if self.file_path:
            self.load_and_preview()
    
    def update_preview(self):
        """Met à jour la prévisualisation selon le mode"""
        if self.df_full is None:
            return
        
        if self.show_all_checkbox.isChecked():
            # Afficher tout le document
            self.table_preview.display_dataframe(self.df_full)
        else:
            # Afficher seulement les 50 premières lignes
            self.table_preview.display_dataframe(self.df_full, max_rows=50)
    
    def toggle_preview_mode(self, checked):
        """Change le mode de prévisualisation"""
        self.update_preview()
        if checked:
            self.total_rows_label.setText(f"📊 {len(self.df_full)} lignes, {len(self.df_full.columns)} colonnes (affichage complet)")
        else:
            self.total_rows_label.setText(f"📊 {len(self.df_full)} lignes, {len(self.df_full.columns)} colonnes (50 premières lignes)")
    
    def generate_statistics(self):
        """Génère des statistiques sur le fichier"""
        if self.df_full is None:
            return
        
        stats_text = []
        stats_text.append("=" * 60)
        stats_text.append("STATISTIQUES DU FICHIER")
        stats_text.append("=" * 60)
        stats_text.append(f"\n📊 Dimensions: {len(self.df_full)} lignes × {len(self.df_full.columns)} colonnes")
        
        # Colonnes requises
        required_cols = ['immatriculation', 'marque', 'modele']
        stats_text.append(f"\n📋 Colonnes requises:")
        for col in required_cols:
            exists = col in self.df_full.columns
            stats_text.append(f"   {'✅' if exists else '❌'} {col}")
        
        # Colonnes optionnelles trouvées
        optional_cols = ['annee', 'energie', 'chassis', 'categorie', 'usage', 'places', 'valeur_neuf', 'valeur_venale']
        found_optional = [col for col in optional_cols if col in self.df_full.columns]
        if found_optional:
            stats_text.append(f"\n📁 Colonnes optionnelles trouvées: {', '.join(found_optional)}")
        
        # Valeurs manquantes
        stats_text.append(f"\n⚠️ Valeurs manquantes:")
        for col in self.df_full.columns:
            missing = self.df_full[col].isna().sum()
            if missing > 0:
                stats_text.append(f"   {col}: {missing} valeur(s) manquante(s)")
        
        # Aperçu des marques
        if 'marque' in self.df_full.columns:
            stats_text.append(f"\n🏭 Top 5 des marques:")
            top_marques = self.df_full['marque'].value_counts().head(5)
            for marque, count in top_marques.items():
                stats_text.append(f"   {marque}: {count} véhicule(s)")
        
        # Aperçu des années
        if 'annee' in self.df_full.columns:
            stats_text.append(f"\n📅 Années:")
            annee_min = self.df_full['annee'].min() if not self.df_full['annee'].isna().all() else "N/A"
            annee_max = self.df_full['annee'].max() if not self.df_full['annee'].isna().all() else "N/A"
            stats_text.append(f"   Minimum: {annee_min}")
            stats_text.append(f"   Maximum: {annee_max}")
        
        self.stats_preview.setText("\n".join(stats_text))
    
    def show_raw_text(self):
        """Affiche le contenu brut du fichier"""
        if self.df_full is None:
            return
        
        try:
            # Pour les petits fichiers, afficher tout
            if len(self.df_full) <= 200:
                text_content = self.df_full.to_string()
            else:
                # Pour les gros fichiers, afficher les 200 premières lignes
                text_content = self.df_full.head(200).to_string()
                text_content += f"\n\n... et {len(self.df_full) - 200} lignes supplémentaires"
            
            self.text_preview.setText(text_content)
        except Exception as e:
            self.text_preview.setText(f"Erreur d'affichage: {str(e)}")
    
    def start_import(self):
        """Démarre l'importation"""
        if not self.file_path or self.df_full is None:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un fichier valide")
            return
        
        # Désactiver les contrôles
        self.btn_import.setEnabled(False)
        self.btn_select_file.setEnabled(False)
        self.btn_cancel.setText("⏹️ Annuler l'import")
        
        # Afficher la progression
        self.progress_bar.setVisible(True)
        self.log_text.setVisible(True)
        self.log_text.clear()
        self.add_log_message("🚀 Démarrage de l'importation...")
        
        # Récupérer le nom de la flotte
        if self.mode_new.isChecked():
            fleet_name = self.fleet_name_input.currentText().strip()
            if not fleet_name:
                QMessageBox.warning(self, "Erreur", "Veuillez entrer un nom pour la flotte")
                self.reset_ui()
                return
            import_mode = 'new'
            existing_fleet_id = None
        else:
            import_mode = 'existing'
            existing_fleet_id = self.existing_fleet_combo.currentData()
            if not existing_fleet_id:
                QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une flotte")
                self.reset_ui()
                return
        
        # Stocker l'ID du contact courant
        if hasattr(self.parent(), 'contact'):
            self.controller.current_contact_id = self.parent().contact.id
        
        # Créer et démarrer le thread
        self.import_thread = FleetImportThread(
            self.controller,
            self.file_path,
            fleet_name if import_mode == 'new' else "",
            import_mode,
            self
        )
        self.import_thread.existing_fleet_id = existing_fleet_id
        self.import_thread.progress_update.connect(self.on_progress_update)
        self.import_thread.log_update.connect(self.on_log_update)
        self.import_thread.finished.connect(self.on_import_finished)
        self.import_thread.start()
    
    def add_log_message(self, message):
        """Ajoute un message au log"""
        self.log_text.append(message)
        # Scroll en bas
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)
        QApplication.processEvents()
    
    def on_progress_update(self, value, message):
        """Met à jour la progression"""
        self.progress_bar.setValue(value)
        self.add_log_message(message)
        
    def on_log_update(self, message):
        """Ajoute un message au log"""
        self.add_log_message(message)
        
    def on_import_finished(self, success, message, summary):
        """Finalise l'importation"""
        self.progress_bar.setValue(100)
        
        if success:
            if summary.get('failed', 0) > 0:
                failed_msg = f"\n\n⚠️ Échecs: {len(summary['failed_list'])} véhicule(s)\n"
                for failed in summary['failed_list'][:10]:  # Afficher max 10 erreurs
                    failed_msg += f"\n   • {failed['immatriculation']}: {failed['error']}"
                if len(summary['failed_list']) > 10:
                    failed_msg += f"\n   ... et {len(summary['failed_list']) - 10} autres"
                
                QMessageBox.warning(self, "Importation partielle", message + failed_msg)
            else:
                QMessageBox.information(self, "✅ Succès", message)
            
            # Fermer le dialogue et rafraîchir la vue parente
            self.accept()
        else:
            QMessageBox.critical(self, "❌ Erreur", message)
            self.reset_ui()
    
    def cancel_import(self):
        """Annule l'importation en cours"""
        if self.import_thread and self.import_thread.isRunning():
            self.import_thread.cancel()
            self.add_log_message("⏸️ Annulation en cours...")
            self.btn_cancel.setEnabled(False)
        else:
            self.reject()
    
    def reset_ui(self):
        """Réinitialise l'interface"""
        self.btn_import.setEnabled(True)
        self.btn_select_file.setEnabled(True)
        self.btn_cancel.setText("Annuler")
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.log_text.setVisible(False)
        
    def closeEvent(self, event):
        """Gère la fermeture de la fenêtre"""
        if self.import_thread and self.import_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "Importation en cours",
                "L'importation est en cours.\nVoulez-vous vraiment annuler et fermer ?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.import_thread.cancel()
                self.import_thread.wait(2000)
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()