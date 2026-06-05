# addons/Automobiles/views/asac_manager.py
"""
Interface ASAC - Export et suivi des attestations d'assurance
Design moderne et professionnel
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QMessageBox, QProgressBar, QTabWidget, QTextEdit,
    QLineEdit, QComboBox, QGroupBox, QGridLayout,
    QDialog, QScrollArea, QApplication, QSplitter
)
from PySide6.QtCore import Qt, QThread, Signal, QDateTime, QSettings, QTimer, QUrl
from PySide6.QtGui import QColor, QFont, QDesktopServices
from datetime import datetime
import json
import os


# ============================================================================
# STYLE MODERNE
# ============================================================================

MODERN_STYLE = """
    QWidget {
        background-color: #f8fafc;
        font-family: 'Segoe UI', sans-serif;
        color: #1e293b;
    }
    
    QScrollArea {
        border: none;
        background: transparent;
    }
    
    QScrollBar:vertical {
        background: #e2e8f0;
        width: 6px;
        border-radius: 3px;
    }
    
    QScrollBar::handle:vertical {
        background: #94a3b8;
        border-radius: 3px;
    }
    
    QScrollBar::handle:vertical:hover {
        background: #64748b;
    }
    
    .HeaderCard {
        background: white;
        border-radius: 24px;
        padding: 20px 24px;
        border: none;
    }
    
    .InfoCard {
        background: white;
        border-radius: 20px;
        padding: 20px;
        border: none;
    }
    
    .SectionTitle {
        font-size: 16px;
        font-weight: 700;
        color: #0f172a;
        padding-bottom: 12px;
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 16px;
    }
    
    .LabelPrimary {
        color: #64748b;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .LabelValue {
        color: #1e293b;
        font-size: 14px;
        font-weight: 600;
    }
    
    QTableWidget {
        background: white;
        border: none;
        border-radius: 16px;
        gridline-color: #f1f5f9;
    }
    
    QTableWidget::item {
        padding: 12px 10px;
        border: none;
    }
    
    QTableWidget::item:selected {
        background-color: #eef2ff;
    }
    
    QHeaderView::section {
        background-color: #f8fafc;
        border: none;
        border-bottom: 2px solid #e2e8f0;
        padding: 12px 10px;
        font-weight: 600;
        color: #475569;
        font-size: 12px;
    }
    
    QTabWidget::pane {
        border: none;
        background: transparent;
    }
    
    QTabBar::tab {
        background: #f1f5f9;
        border: none;
        border-radius: 12px;
        padding: 10px 24px;
        margin: 0 4px;
        font-weight: 600;
        font-size: 13px;
    }
    
    QTabBar::tab:selected {
        background: #3b82f6;
        color: white;
    }
    
    QTabBar::tab:hover {
        background: #e2e8f0;
    }
    
    QLineEdit, QTextEdit {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 8px 12px;
        font-size: 13px;
    }
    
    QLineEdit:focus, QTextEdit:focus {
        border-color: #3b82f6;
    }
    
    QPushButton {
        background: #f1f5f9;
        border: none;
        border-radius: 10px;
        padding: 8px 16px;
        font-weight: 600;
        font-size: 13px;
    }
    
    QPushButton:hover {
        background: #e2e8f0;
    }
    
    .BtnPrimary {
        background: #3b82f6;
        color: white;
    }
    .BtnPrimary:hover {
        background: #2563eb;
    }
    
    .BtnSuccess {
        background: #10b981;
        color: white;
    }
    .BtnSuccess:hover {
        background: #059669;
    }
    
    .BtnSecondary {
        background: #f1f5f9;
        color: #475569;
        border: 1px solid #e2e8f0;
    }
    .BtnSecondary:hover {
        background: #e2e8f0;
    }
    
    QProgressBar {
        border: none;
        border-radius: 10px;
        background-color: #e2e8f0;
        height: 6px;
    }
    
    QProgressBar::chunk {
        background-color: #3b82f6;
        border-radius: 10px;
    }
    
    .StatusBadge {
        background: #eef2ff;
        color: #3b82f6;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 11px;
        font-weight: 600;
    }
    
    .StatusSuccess {
        background: #d1fae5;
        color: #059669;
    }
    
    .StatusError {
        background: #fee2e2;
        color: #dc2626;
    }
"""


# ============================================================================
# THREADS API
# ============================================================================

class ExportWorker(QThread):
    progress = Signal(int, str)
    finished = Signal(bool, dict, str)
    
    def __init__(self, vehicle_data, config):
        super().__init__()
        self.vehicle_data = vehicle_data
        self.config = config
    
    def run(self):
        try:
            self.progress.emit(10, "📋 Préparation des données...")
            
            # Construction de la requête ASAC
            request = self.build_asac_request()
            
            self.progress.emit(30, "🔐 Authentification ASAC...")
            
            # Appel API
            import requests
            auth_url = f"{self.config['url']}/api/v1/auth/tokens/app-key"
            auth_response = requests.post(
                auth_url,
                params={"app_key": self.config["app_key"], "username": self.config["username"]},
                timeout=10
            )
            
            if auth_response.status_code != 200:
                self.finished.emit(False, {}, f"Authentification échouée: {auth_response.text[:100]}")
                return
            
            token = auth_response.json().get("token")
            
            self.progress.emit(60, "📤 Envoi à ASAC...")
            
            prod_url = f"{self.config['url']}/api/v1/productions"
            headers = {"Authorization": f"Bearer {token}"}
            prod_response = requests.post(prod_url, json=request, headers=headers, timeout=30)
            
            self.progress.emit(90, "📥 Traitement de la réponse...")
            
            if prod_response.status_code in [200, 201]:
                response_data = prod_response.json()
                self.progress.emit(100, "✅ Export terminé !")
                self.finished.emit(True, response_data, "")
            else:
                self.finished.emit(False, {}, f"Erreur ASAC: {prod_response.text[:200]}")
                
        except Exception as e:
            self.finished.emit(False, {}, str(e))
    
    def build_asac_request(self):
        """Construit la requête ASAC à partir des données du véhicule"""
        vehicle = self.vehicle_data
        
        return {
            ""
            "attestation": {
                "numero_police": vehicle.get("numero_police", ""),
                "immatriculation": vehicle.get("immatriculation", ""),
                "chassis": vehicle.get("chassis", ""),
                "marque": vehicle.get("marque", ""),
                "modele": vehicle.get("modele", ""),
                "date_premiere_mise_circulation": vehicle.get("annee", ""),
                "energie": vehicle.get("energie", "Essence"),
                "categorie": vehicle.get("categorie", "VP"),
                "places": vehicle.get("places", 5),
                "valeur_neuf": vehicle.get("valeur_neuf", 0),
                "valeur_venale": vehicle.get("valeur_venale", 0)
            },
            "assure": {
                "nom": vehicle.get("owner", ""),
                "telephone": vehicle.get("phone", ""),
                "email": vehicle.get("email", ""),
                "adresse": vehicle.get("city", "")
            },
            "garanties": {
                "responsabilite_civile": float(vehicle.get("amt_rc", 0)),
                "defense_recours": float(vehicle.get("amt_dr", 0)),
                "vol": float(vehicle.get("amt_vol", 0)),
                "incendie": float(vehicle.get("amt_in", 0)),
                "bris_de_glace": float(vehicle.get("amt_bris", 0))
            },
            "prime": {
                "prime_nette": float(vehicle.get("prime_nette", 0)),
                "prime_brute": float(vehicle.get("prime_brute", 0)),
                "tva": float(vehicle.get("tva", 0)),
                "total_ttc": float(vehicle.get("pttc", vehicle.get("prime_nette", 0)))
            },
            "periode": {
                "date_debut": str(vehicle.get("date_debut", "")),
                "date_fin": str(vehicle.get("date_fin", ""))
            }
        }

class ImportThread(QThread):
    progress = Signal(int, str)
    finished = Signal(bool, dict, str)
    
    def __init__(self, controller, file_path, config):
        super().__init__()
        self.controller = controller
        self.file_path = file_path
        self.config = config
    
    def run(self):
        try:
            self.progress.emit(10, "📖 Lecture du fichier...")
            
            import pandas as pd
            if self.file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(self.file_path)
            else:
                df = pd.read_csv(self.file_path)
            
            total = len(df)
            self.progress.emit(20, f"🚗 Traitement de {total} véhicules...")
            
            imported = []
            errors = []
            
            for idx, row in df.iterrows():
                try:
                    vehicle_data = self._row_to_vehicle_data(row)
                    success, vehicle_id, msg = self.controller.vehicles.create_vehicle(
                        vehicle_data, user_id=1,
                        local_ip="127.0.0.1", public_ip="127.0.0.1"
                    )
                    
                    if success:
                        imported.append(vehicle_data.get('immatriculation'))
                    else:
                        errors.append(f"{vehicle_data.get('immatriculation')}: {msg}")
                    
                    progress = 20 + int((idx + 1) / total * 70)
                    self.progress.emit(progress, f"📦 {idx+1}/{total} - {vehicle_data.get('immatriculation', 'N/A')}")
                    
                except Exception as e:
                    errors.append(f"Ligne {idx+2}: {str(e)}")
            
            result = {
                "total": total,
                "imported": len(imported),
                "errors": len(errors),
                "error_list": errors[:10],
                "imported_list": imported
            }
            
            self.progress.emit(100, "✅ Import terminé !")
            self.finished.emit(len(errors) == 0, result, "")
            
        except Exception as e:
            self.finished.emit(False, {}, str(e))
    
    def _row_to_vehicle_data(self, row):
        return {
            'immatriculation': str(row.get('immatriculation', '')).strip().upper(),
            'marque': str(row.get('marque', '')).strip(),
            'modele': str(row.get('modele', '')).strip(),
            'chassis': str(row.get('chassis', '')).strip() or None,
            'annee': int(row.get('annee', 0)) if row.get('annee') else None,
            'energie': str(row.get('energie', 'Essence')).strip(),
            'categorie': str(row.get('categorie', 'VP')).strip(),
            'usage': str(row.get('usage', 'Particulier')).strip(),
            'places': int(row.get('places', 5)) if row.get('places') else 5,
            'zone': str(row.get('zone', 'A')).strip(),
            'valeur_neuf': float(row.get('valeur_neuf', 0)) if row.get('valeur_neuf') else 0,
            'valeur_venale': float(row.get('valeur_venale', 0)) if row.get('valeur_venale') else 0,
            'prime_nette': float(row.get('prime_nette', 0)) if row.get('prime_nette') else 0,
        }

# ============================================================================
# DIALOGUE DE CONFIGURATION
# ============================================================================

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration ASAC")
        self.setMinimumSize(550, 500)
        self.setModal(True)
        self.setStyleSheet(MODERN_STYLE)
        self.setup_ui()
        self.load_config()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # En-tête
        header = QFrame()
        header.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #1e293b,stop:1 #0f172a); border-radius: 20px;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 20, 24, 20)
        
        icon = QLabel("⚙️")
        icon.setStyleSheet("font-size: 32px;")
        title = QLabel("Configuration du serveur ASAC")
        title.setStyleSheet("font-size: 18px; font-weight: 800; color: white;")
        
        header_layout.addWidget(icon)
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addWidget(header)
        
        # Formulaire
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(16)
        
        # Carte des paramètres
        card = QFrame()
        card.setProperty("class", "InfoCard")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(16)
        
        fields = [
            ("🌐 URL API", "url", "https://ppeatt-api.asac.cm"),
            ("🔑 Clé applicative (App Key)", "app_key", ""),
            ("👤 Nom d'utilisateur", "username", ""),
            ("🏢 Code bureau", "office_code", "AG-DLA-001"),
            ("📋 Organisation", "org_code", "ACTIVA")
        ]
        
        self.inputs = {}
        for label, key, placeholder in fields:
            lbl = QLabel(label)
            lbl.setProperty("class", "LabelPrimary")
            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            if key == "app_key":
                inp.setEchoMode(QLineEdit.Password)
            
            card_layout.addWidget(lbl)
            card_layout.addWidget(inp)
            self.inputs[key] = inp
        
        form_layout.addWidget(card)
        
        # Bouton test
        test_btn = QPushButton("🔌 Tester la connexion")
        test_btn.setProperty("class", "BtnSecondary")
        test_btn.clicked.connect(self.test_connection)
        form_layout.addWidget(test_btn)
        
        scroll.setWidget(form_widget)
        layout.addWidget(scroll)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setProperty("class", "BtnSecondary")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("💾 Sauvegarder")
        save_btn.setProperty("class", "BtnSuccess")
        save_btn.clicked.connect(self.save_config)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
    
    def load_config(self):
        settings = QSettings("LOMETA", "ASAC")
        for key, inp in self.inputs.items():
            inp.setText(settings.value(key, ""))
    
    def save_config(self):
        settings = QSettings("LOMETA", "ASAC")
        for key, inp in self.inputs.items():
            settings.setValue(key, inp.text())
        
        QMessageBox.information(self, "Succès", "Configuration sauvegardée !")
        self.accept()
    
    def test_connection(self):
        import requests
        url = self.inputs["url"].text()
        app_key = self.inputs["app_key"].text()
        username = self.inputs["username"].text()
        
        if not url or not app_key or not username:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir l'URL, l'App Key et le nom d'utilisateur")
            return
        
        try:
            response = requests.post(
                f"{url}/api/v1/auth/tokens/app-key",
                params={"app_key": app_key, "username": username},
                timeout=5
            )
            if response.status_code == 200:
                QMessageBox.information(self, "Succès", "✅ Connexion au serveur ASAC réussie !")
            else:
                QMessageBox.warning(self, "Erreur", f"❌ Erreur HTTP {response.status_code}")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"❌ {str(e)}")
    
    def get_config(self):
        return {key: inp.text() for key, inp in self.inputs.items()}


# ============================================================================
# WIDGET PRINCIPAL
# ============================================================================

class AsacManager(QDialog):
    """Interface d'export ASAC pour un véhicule"""
    
    def __init__(self, controller, vehicle_data, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.vehicle_data = vehicle_data
        self.export_worker = None
        self.import_thread = None
        self.import_file_path = None
        
        self.setWindowTitle(f"ASAC Export - {vehicle_data.get('immatriculation', 'Véhicule')}")
        self.setMinimumSize(1000, 750)
        self.setStyleSheet(MODERN_STYLE)
        
        self.setup_ui()
        self.load_config()
        self.display_vehicle_info()

    def setup_ui(self):
        self.setStyleSheet(MODERN_STYLE)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)
        
        # En-tête
        header = self._create_header()
        layout.addWidget(header)
        
        # TabWidget
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self._create_export_tab(), "📤 Export ASAC")
        self.tab_widget.addTab(self._create_import_tab(), "📥 Import ASAC")
        
        layout.addWidget(self.tab_widget)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Splitter principal
        splitter = QSplitter(Qt.Horizontal)
        
        # Panneau gauche - Informations véhicule
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Panneau droit - Export et historique
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([400, 600])
        layout.addWidget(splitter)
        
        # Barre de statut
        self.status_bar = QFrame()
        self.status_bar.setProperty("class", "InfoCard")
        self.status_bar.setFixedHeight(50)
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(16, 8, 16, 8)
        
        self.status_icon = QLabel("●")
        self.status_icon.setStyleSheet("color: #f59e0b; font-size: 12px;")
        self.status_label = QLabel("Prêt")
        self.status_label.setStyleSheet("color: #64748b; font-size: 12px;")
        
        status_layout.addWidget(self.status_icon)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        # Boutons fermeture
        close_btn = QPushButton("Fermer")
        close_btn.setProperty("class", "BtnSecondary")
        close_btn.clicked.connect(self.close)
        status_layout.addWidget(close_btn)
        
        layout.addWidget(self.status_bar)
    
    def create_left_panel(self):
        """Panneau gauche - Informations du véhicule"""
        panel = QScrollArea()
        panel.setWidgetResizable(True)
        panel.setFrameShape(QFrame.NoFrame)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(16)
        
        # Carte véhicule
        vehicle_card = QFrame()
        vehicle_card.setProperty("class", "InfoCard")
        vehicle_layout = QVBoxLayout(vehicle_card)
        vehicle_layout.setSpacing(12)
        
        # Titre
        title_layout = QHBoxLayout()
        title_icon = QLabel("🚗")
        title_icon.setStyleSheet("font-size: 24px;")
        title = QLabel("Informations véhicule")
        title.setStyleSheet("font-size: 16px; font-weight: 800;")
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title)
        title_layout.addStretch()
        vehicle_layout.addLayout(title_layout)
        
        # Champs info - CORRECTION : utiliser des clés simples sans espaces
        info_fields = [
            ("Immatriculation", "immatriculation"),
            ("Marque / Modèle", "marque_modele"),
            ("Châssis", "chassis"),
            ("Année", "annee"),
            ("Énergie", "energie"),
            ("Catégorie", "categorie"),
            ("Propriétaire", "owner"),
            ("Téléphone", "phone"),
            ("Email", "email"),
            ("Prime nette", "prime_nette")
        ]
        
        self.vehicle_info = {}
        for label, key in info_fields:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setProperty("class", "LabelPrimary")
            lbl.setFixedWidth(120)
            
            value_lbl = QLabel()
            value_lbl.setProperty("class", "LabelValue")
            value_lbl.setWordWrap(True)
            
            row.addWidget(lbl)
            row.addWidget(value_lbl, 1)
            vehicle_layout.addLayout(row)
            
            self.vehicle_info[key] = value_lbl
        
        layout.addWidget(vehicle_card)
        
        # Carte garanties
        garanties_card = QFrame()
        garanties_card.setProperty("class", "InfoCard")
        garanties_layout = QVBoxLayout(garanties_card)
        garanties_layout.setSpacing(10)
        
        garanties_title = QLabel("🛡️ Garanties souscrites")
        garanties_title.setStyleSheet("font-size: 14px; font-weight: 700;")
        garanties_layout.addWidget(garanties_title)
        
        self.garanties_table = QTableWidget(0, 2)
        self.garanties_table.setHorizontalHeaderLabels(["Garantie", "Montant"])
        self.garanties_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.garanties_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.garanties_table.setAlternatingRowColors(True)
        self.garanties_table.setMaximumHeight(200)
        garanties_layout.addWidget(self.garanties_table)
        
        layout.addWidget(garanties_card)
        
        # Carte configuration
        config_card = QFrame()
        config_card.setProperty("class", "InfoCard")
        config_layout = QVBoxLayout(config_card)
        config_layout.setSpacing(10)
        
        config_header = QHBoxLayout()
        config_title = QLabel("⚙️ Serveur ASAC")
        config_title.setStyleSheet("font-size: 14px; font-weight: 700;")
        self.config_status = QLabel("Non configuré")
        self.config_status.setProperty("class", "StatusBadge")
        config_header.addWidget(config_title)
        config_header.addStretch()
        config_header.addWidget(self.config_status)
        config_layout.addLayout(config_header)
        
        self.server_info_label = QLabel("Cliquez sur 'Configurer' pour paramétrer le serveur")
        self.server_info_label.setStyleSheet("color: #64748b; font-size: 12px;")
        config_layout.addWidget(self.server_info_label)
        
        config_btn = QPushButton("🔧 Configurer le serveur")
        config_btn.setProperty("class", "BtnSecondary")
        config_btn.clicked.connect(self.open_config)
        config_layout.addWidget(config_btn)
        
        layout.addWidget(config_card)
        layout.addStretch()
        
        panel.setWidget(container)
        return panel
    
    def create_right_panel(self):
        """Panneau droit - Export et historique"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Carte d'aperçu JSON
        preview_card = QFrame()
        preview_card.setProperty("class", "InfoCard")
        preview_layout = QVBoxLayout(preview_card)
        preview_layout.setSpacing(12)
        
        preview_header = QHBoxLayout()
        preview_title = QLabel("📋 Aperçu de la requête")
        preview_title.setStyleSheet("font-size: 14px; font-weight: 700;")
        preview_header.addWidget(preview_title)
        preview_header.addStretch()
        
        copy_btn = QPushButton("📋 Copier")
        copy_btn.setProperty("class", "BtnSecondary")
        copy_btn.setFixedSize(80, 30)
        copy_btn.clicked.connect(self.copy_json)
        preview_header.addWidget(copy_btn)
        
        preview_layout.addLayout(preview_header)
        
        self.json_preview = QTextEdit()
        self.json_preview.setReadOnly(True)
        self.json_preview.setFont(QFont("Courier New", 10))
        self.json_preview.setMinimumHeight(250)
        self.json_preview.setStyleSheet("""
            QTextEdit {
                background: #1e1e2e;
                color: #cdd6f4;
                border-radius: 12px;
                padding: 16px;
                font-family: monospace;
            }
        """)
        preview_layout.addWidget(self.json_preview)
        
        layout.addWidget(preview_card)
        
        # Zone d'export
        export_card = QFrame()
        export_card.setProperty("class", "InfoCard")
        export_layout = QVBoxLayout(export_card)
        export_layout.setSpacing(12)
        
        export_title = QLabel("🚀 Export vers ASAC")
        export_title.setStyleSheet("font-size: 14px; font-weight: 700;")
        export_layout.addWidget(export_title)
        
        self.export_progress = QProgressBar()
        self.export_progress.setVisible(False)
        export_layout.addWidget(self.export_progress)
        
        # Boutons d'export
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        self.export_btn = QPushButton("📤 Exporter vers ASAC")
        self.export_btn.setProperty("class", "BtnPrimary")
        self.export_btn.setMinimumHeight(45)
        self.export_btn.clicked.connect(self.start_export)
        
        self.view_certificate_btn = QPushButton("📄 Voir l'attestation")
        self.view_certificate_btn.setProperty("class", "BtnSecondary")
        self.view_certificate_btn.setVisible(False)
        self.view_certificate_btn.clicked.connect(self.view_certificate)
        
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.view_certificate_btn)
        export_layout.addLayout(btn_layout)
        
        layout.addWidget(export_card)
        
        # Historique
        history_card = QFrame()
        history_card.setProperty("class", "InfoCard")
        history_layout = QVBoxLayout(history_card)
        history_layout.setSpacing(12)
        
        history_title = QLabel("📜 Historique des exports")
        history_title.setStyleSheet("font-size: 14px; font-weight: 700;")
        history_layout.addWidget(history_title)
        
        self.history_table = QTableWidget(0, 4)
        self.history_table.setHorizontalHeaderLabels(["Date", "Référence", "Statut", "Détails"])
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setMinimumHeight(180)
        
        history_layout.addWidget(self.history_table)
        layout.addWidget(history_card)
        
        return panel
    
    def display_vehicle_info(self):
        """Affiche les informations du véhicule"""
        # Infos générales
        self.vehicle_info["immatriculation"].setText(self.vehicle_data.get("immatriculation", "N/A"))
        
        marque_modele = f"{self.vehicle_data.get('marque', '')} {self.vehicle_data.get('modele', '')}".strip()
        self.vehicle_info["marque_modele"].setText(marque_modele or "N/A")  # ← Clé corrigée
        
        self.vehicle_info["chassis"].setText(self.vehicle_data.get("chassis", "N/A"))
        self.vehicle_info["annee"].setText(str(self.vehicle_data.get("annee", "N/A")))
        self.vehicle_info["energie"].setText(self.vehicle_data.get("energie", "N/A"))
        self.vehicle_info["categorie"].setText(self.vehicle_data.get("categorie", "N/A"))
        self.vehicle_info["owner"].setText(self.vehicle_data.get("owner", "N/A"))
        self.vehicle_info["phone"].setText(self.vehicle_data.get("phone", "N/A"))
        self.vehicle_info["email"].setText(self.vehicle_data.get("email", "N/A"))
        
        prime = self.vehicle_data.get("prime_nette", 0)
        self.vehicle_info["prime_nette"].setText(f"{prime:,.0f} FCFA" if prime else "N/A")
        
        # Garanties
        garanties = [
            ("Responsabilité Civile", "amt_rc"),
            ("Défense et Recours", "amt_dr"),
            ("Vol", "amt_vol"),
            ("Vol à main armée", "amt_vb"),
            ("Incendie", "amt_in"),
            ("Bris de glace", "amt_bris"),
            ("Assistance", "amt_ar"),
            ("Dommages Tous Accidents", "amt_dta"),
            ("Individuelle Chauffeur", "amt_ipt")
        ]
        
        self.garanties_table.setRowCount(0)  # ← Vider avant de remplir
        for name, key in garanties:
            montant = self.vehicle_data.get(key, 0)
            if montant and float(montant) > 0:
                row = self.garanties_table.rowCount()
                self.garanties_table.insertRow(row)
                self.garanties_table.setItem(row, 0, QTableWidgetItem(name))
                self.garanties_table.setItem(row, 1, QTableWidgetItem(f"{float(montant):,.0f} FCFA"))
        
        # Générer l'aperçu JSON
        self.update_json_preview()
    
    def update_json_preview(self):
        """Met à jour l'aperçu JSON de la requête"""
        settings = QSettings("LOMETA", "ASAC")
        config = {
            "url": settings.value("url", ""),
            "app_key": settings.value("app_key", ""),
            "username": settings.value("username", ""),
            "office_code": settings.value("office_code", "AG-DLA-001"),
            "org_code": settings.value("org_code", "ACTIVA")
        }
        
        request = {
            "attestation": {
                "numero_police": self.vehicle_data.get("numero_police", ""),
                "immatriculation": self.vehicle_data.get("immatriculation", ""),
                "chassis": self.vehicle_data.get("chassis", ""),
                "marque": self.vehicle_data.get("marque", ""),
                "modele": self.vehicle_data.get("modele", ""),
                "energie": self.vehicle_data.get("energie", "Essence"),
                "categorie": self.vehicle_data.get("categorie", "VP"),
                "places": self.vehicle_data.get("places", 5)
            },
            "assure": {
                "nom": self.vehicle_data.get("owner", ""),
                "telephone": self.vehicle_data.get("phone", ""),
                "email": self.vehicle_data.get("email", "")
            },
            "garanties": {
                "responsabilite_civile": float(self.vehicle_data.get("amt_rc", 0)),
                "defense_recours": float(self.vehicle_data.get("amt_dr", 0)),
                "vol": float(self.vehicle_data.get("amt_vol", 0)),
                "incendie": float(self.vehicle_data.get("amt_in", 0))
            },
            "prime": {
                "prime_nette": float(self.vehicle_data.get("prime_nette", 0)),
                "prime_brute": float(self.vehicle_data.get("prime_brute", 0))
            },
            "period": {
                "date_debut": str(self.vehicle_data.get("date_debut", "")),
                "date_fin": str(self.vehicle_data.get("date_fin", ""))
            },
            "meta": {
                "office_code": config.get("office_code", "AG-DLA-001"),
                "organization_code": config.get("org_code", "ACTIVA")
            }
        }
        
        self.json_preview.setText(json.dumps(request, indent=2, default=str, ensure_ascii=False))
    
    def copy_json(self):
        """Copie le JSON dans le presse-papier"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.json_preview.toPlainText())
        
        self.status_label.setText("✅ JSON copié dans le presse-papier")
        self.status_icon.setStyleSheet("color: #10b981; font-size: 12px;")
        QTimer.singleShot(3000, self.reset_status)
    
    def reset_status(self):
        self.status_label.setText("Prêt")
        self.status_icon.setStyleSheet("color: #f59e0b; font-size: 12px;")
    
    def load_config(self):
        """Charge la configuration et met à jour l'affichage"""
        settings = QSettings("LOMETA", "ASAC")
        url = settings.value("url", "")
        app_key = settings.value("app_key", "")
        
        if url and app_key:
            self.config_status.setText("Connecté")
            self.config_status.setProperty("class", "StatusBadge StatusSuccess")
            self.server_info_label.setText(f"Serveur: {url}")
        else:
            self.config_status.setText("Non configuré")
            self.config_status.setProperty("class", "StatusBadge StatusError")
            self.server_info_label.setText("Configuration requise avant export")
        
        self.config_status.style().unpolish(self.config_status)
        self.config_status.style().polish(self.config_status)

    def open_config(self):
        """Ouvre la fenêtre de configuration"""
        dialog = ConfigDialog(self)
        if dialog.exec():
            self.load_config()
            self.update_json_preview()
    
    def start_export(self):
        """Démarre l'export vers ASAC"""
        settings = QSettings("LOMETA", "ASAC")
        config = {
            "url": settings.value("url", ""),
            "app_key": settings.value("app_key", ""),
            "username": settings.value("username", ""),
            "office_code": settings.value("office_code", "AG-DLA-001"),
            "org_code": settings.value("org_code", "ACTIVA")
        }
        
        if not config["url"] or not config["app_key"] or not config["username"]:
            QMessageBox.warning(self, "Configuration manquante", 
                "Veuillez configurer le serveur ASAC avant d'exporter.\n\n"
                "Cliquez sur 'Configurer le serveur' pour définir:\n"
                "• URL de l'API\n"
                "• Clé applicative (App Key)\n"
                "• Nom d'utilisateur")
            self.open_config()
            return
        
        self.export_btn.setEnabled(False)
        self.export_btn.setText("⏳ Export en cours...")
        self.export_progress.setVisible(True)
        self.export_progress.setValue(0)
        
        self.status_label.setText("Export en cours...")
        self.status_icon.setStyleSheet("color: #3b82f6; font-size: 12px;")
        
        self.export_worker = ExportWorker(self.vehicle_data, config)
        self.export_worker.progress.connect(self.on_export_progress)
        self.export_worker.finished.connect(self.on_export_finished)
        self.export_worker.start()
    
    def on_export_progress(self, value, message):
        self.export_progress.setValue(value)
        self.status_label.setText(message)
    
    def on_export_finished(self, success, response, error):
        self.export_btn.setEnabled(True)
        self.export_btn.setText("📤 Exporter vers ASAC")
        self.export_progress.setVisible(False)
        
        if success:
            reference = response.get("data", {}).get("reference", response.get("reference", "N/A"))
            
            # Sauvegarder dans l'historique
            self.save_to_history(reference, response)
            
            self.status_label.setText("✅ Export réussi !")
            self.status_icon.setStyleSheet("color: #10b981; font-size: 12px;")
            
            # Afficher le certificat
            self.last_certificate_url = response.get("data", {}).get("download_link", 
                                    response.get("download_link", ""))
            self.view_certificate_btn.setVisible(True)
            
            QMessageBox.information(self, "Export réussi", 
                f"✅ Le véhicule {self.vehicle_data.get('immatriculation', '')} a été exporté avec succès !\n\n"
                f"📄 Référence: {reference}\n\n"
                f"L'attestation a été générée sur le serveur ASAC.")
        else:
            self.status_label.setText(f"❌ Erreur: {error[:80]}")
            self.status_icon.setStyleSheet("color: #ef4444; font-size: 12px;")
            
            QMessageBox.critical(self, "Erreur d'export", 
                f"❌ L'export a échoué.\n\n{error}")
        
        QTimer.singleShot(5000, self.reset_status)
        self.refresh_history()
    
    def save_to_history(self, reference, response):
        """Sauvegarde l'export dans l'historique"""
        settings = QSettings("LOMETA", "ASAC")
        history = settings.value(f"history_{self.vehicle_data.get('immatriculation', 'unknown')}", [])
        if isinstance(history, str):
            try:
                history = json.loads(history)
            except:
                history = []
        
        record = {
            "date": QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm:ss"),
            "reference": reference,
            "status": "success",
            "response": response,
            "timestamp": QDateTime.currentDateTime().toSecsSinceEpoch()
        }
        
        history.insert(0, record)
        history = history[:20]
        settings.setValue(f"history_{self.vehicle_data.get('immatriculation', 'unknown')}", 
                         json.dumps(history, default=str))
    
    def refresh_history(self):
        """Rafraîchit l'historique des exports"""
        settings = QSettings("LOMETA", "ASAC")
        history = settings.value(f"history_{self.vehicle_data.get('immatriculation', 'unknown')}", [])
        if isinstance(history, str):
            try:
                history = json.loads(history)
            except:
                history = []
        
        self.history_table.setRowCount(len(history))
        for i, record in enumerate(history):
            self.history_table.setItem(i, 0, QTableWidgetItem(record.get("date", "")))
            self.history_table.setItem(i, 1, QTableWidgetItem(record.get("reference", "N/A")))
            
            status_item = QTableWidgetItem("✅ Succès")
            status_item.setForeground(QColor("#10b981"))
            self.history_table.setItem(i, 2, status_item)
            
            # Bouton détails
            btn = QPushButton("👁️ Détails")
            btn.setProperty("class", "BtnSecondary")
            btn.setFixedSize(80, 28)
            btn.clicked.connect(lambda checked, r=record: self.show_details(r))
            self.history_table.setCellWidget(i, 3, btn)
    
    def show_details(self, record):
        """Affiche les détails d'un export"""
        content = json.dumps(record, indent=2, default=str, ensure_ascii=False)
        dialog = QDialog(self)
        dialog.setWindowTitle("Détails de l'export")
        dialog.setMinimumSize(600, 500)
        dialog.setStyleSheet(MODERN_STYLE)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        
        text = QTextEdit()
        text.setPlainText(content)
        text.setFont(QFont("Courier New", 10))
        text.setStyleSheet("background: #1e1e2e; color: #cdd6f4; border-radius: 12px; padding: 16px;")
        
        layout.addWidget(text)
        
        btn = QPushButton("Fermer")
        btn.setProperty("class", "BtnPrimary")
        btn.clicked.connect(dialog.accept)
        layout.addWidget(btn, alignment=Qt.AlignRight)
        
        dialog.exec()
    
    def view_certificate(self):
        """Ouvre l'attestation dans le navigateur"""
        if hasattr(self, 'last_certificate_url') and self.last_certificate_url:
            QDesktopServices.openUrl(QUrl(self.last_certificate_url))
        else:
            QMessageBox.information(self, "Information", "Aucune attestation disponible pour cet export")