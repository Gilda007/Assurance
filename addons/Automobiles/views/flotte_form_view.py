from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QLineEdit, QComboBox, QPushButton, QFrame, 
                             QGraphicsDropShadowEffect, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QScrollArea, QListWidget, QListWidgetItem, QWidget, QMessageBox, QDateEdit,
                             QSplitter, QGroupBox, QCheckBox)
from PySide6.QtCore import QDate, Qt, QPoint, QTimer
from PySide6.QtGui import QColor, QIcon, QPixmap, QFont
import os


class GarantieSelectionDialog(QDialog):
    """Dialogue personnalisé pour sélectionner les garanties d'un véhicule dans la flotte"""
    
    def __init__(self, vehicle_data, parent=None):
        super().__init__(parent)
        self.vehicle_data = vehicle_data
        self.selected_garanties = {}
        self.garantie_widgets = {}
        self.total_amount = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle(f"Sélection des garanties - {self.vehicle_data.get('immatriculation', 'Véhicule')}")
        self.setMinimumSize(500, 600)
        self.setStyleSheet("""
            QDialog {
                background: white;
                border-radius: 16px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
            }
            QCheckBox {
                spacing: 8px;
                font-size: 13px;
                padding: 5px;
            }
            QLineEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # En-tête
        header = QLabel(f"🚗 {self.vehicle_data.get('immatriculation', 'Véhicule')} - {self.vehicle_data.get('marque', '')} {self.vehicle_data.get('modele', '')}")
        header.setStyleSheet("font-size: 16px; font-weight: 800; color: #2c3e50; padding: 10px; background: #f0f9ff; border-radius: 10px;")
        layout.addWidget(header)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("border: none;")
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(10)
        
        # Groupe Garanties de base
        base_group = QGroupBox("🛡️ Garanties de base")
        base_layout = QGridLayout(base_group)
        base_layout.setSpacing(10)
        
        garanties = [
            ("rc", "Responsabilité Civile", "amt_rc"),
            ("dr", "Défense et Recours", "amt_dr"),
            ("vol", "Vol du véhicule", "amt_vol"),
            ("vb", "Vol à main armée", "amt_vb"),
        ]
        
        for i, (key, label, amt_key) in enumerate(garanties):
            checkbox = QCheckBox(label)
            checkbox.setObjectName(key)
            checkbox.stateChanged.connect(lambda state, k=key: self.on_garantie_toggle(k, state))
            
            amount_input = QLineEdit()
            amount_input.setPlaceholderText("Montant (FCFA)")
            amount_input.setEnabled(False)
            amount_input.setObjectName(f"amount_{key}")
            amount_input.textChanged.connect(self.calculate_total)
            
            base_layout.addWidget(checkbox, i, 0)
            base_layout.addWidget(amount_input, i, 1)
            
            self.garantie_widgets[key] = {
                'checkbox': checkbox,
                'amount': amount_input,
                'amt_key': amt_key,
                'default_value': float(self.vehicle_data.get(amt_key, 0) or 0)
            }
            
            if self.garantie_widgets[key]['default_value'] > 0:
                amount_input.setText(f"{self.garantie_widgets[key]['default_value']:,.0f}".replace(",", " "))
                checkbox.setChecked(True)
                amount_input.setEnabled(True)
        
        container_layout.addWidget(base_group)
        
        # Groupe Garanties supplémentaires
        extra_group = QGroupBox("🔥 Garanties supplémentaires")
        extra_layout = QGridLayout(extra_group)
        extra_layout.setSpacing(10)
        
        extra_garanties = [
            ("in", "Incendie", "amt_in"),
            ("bris", "Bris de glace", "amt_bris"),
            ("ar", "Assistance réparation", "amt_ar"),
            ("dta", "Dommages tous accidents", "amt_dta"),
            ("ipt", "Individuelle chauffeur", "amt_ipt"),
        ]
        
        for i, (key, label, amt_key) in enumerate(extra_garanties):
            checkbox = QCheckBox(label)
            checkbox.setObjectName(key)
            checkbox.stateChanged.connect(lambda state, k=key: self.on_garantie_toggle(k, state))
            
            amount_input = QLineEdit()
            amount_input.setPlaceholderText("Montant (FCFA)")
            amount_input.setEnabled(False)
            amount_input.setObjectName(f"amount_{key}")
            amount_input.textChanged.connect(self.calculate_total)
            
            extra_layout.addWidget(checkbox, i, 0)
            extra_layout.addWidget(amount_input, i, 1)
            
            self.garantie_widgets[key] = {
                'checkbox': checkbox,
                'amount': amount_input,
                'amt_key': amt_key,
                'default_value': float(self.vehicle_data.get(amt_key, 0) or 0)
            }
            
            if self.garantie_widgets[key]['default_value'] > 0:
                amount_input.setText(f"{self.garantie_widgets[key]['default_value']:,.0f}".replace(",", " "))
                checkbox.setChecked(True)
                amount_input.setEnabled(True)
        
        container_layout.addWidget(extra_group)

        for key, widget in self.garantie_widgets.items():
            print(f"Garantie {key}: default_value = {widget['default_value']}")
            if widget['default_value'] > 0:
                widget['amount'].setText(f"{widget['default_value']:,.0f}".replace(",", " "))
                widget['checkbox'].setChecked(True)
                widget['amount'].setEnabled(True)
            else:
                print(f"  -> Pas de valeur par défaut pour {key}")

        # Total
        total_frame = QFrame()
        total_frame.setStyleSheet("""
            QFrame {
                background: #f0fdf4;
                border-radius: 12px;
                margin-top: 10px;
            }
        """)
        total_layout = QHBoxLayout(total_frame)
        total_layout.setContentsMargins(15, 10, 15, 10)
        
        total_label = QLabel("💰 TOTAL DES GARANTIES:")
        total_label.setStyleSheet("font-weight: bold; color: #166534;")
        
        self.total_amount = QLabel("0 FCFA")
        self.total_amount.setStyleSheet("font-size: 18px; font-weight: 800; color: #166534;")
        
        total_layout.addWidget(total_label)
        total_layout.addStretch()
        total_layout.addWidget(self.total_amount)
        
        container_layout.addWidget(total_frame)
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_ok = QPushButton("✓ Valider")
        btn_ok.setCursor(Qt.PointingHandCursor)
        btn_ok.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #059669;
            }
        """)
        btn_ok.clicked.connect(self.accept)
        
        btn_cancel = QPushButton("✗ Annuler")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: #ef4444;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #dc2626;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)
        
        self.calculate_total()
    
    def on_garantie_toggle(self, key, state):
        """Gère l'activation/désactivation d'une garantie"""
        widget = self.garantie_widgets.get(key)
        if widget:
            is_checked = state == Qt.Checked
            widget['amount'].setEnabled(is_checked)
            if not is_checked:
                widget['amount'].clear()
            self.calculate_total()
    
    def calculate_total(self):
        """Calcule le total des garanties sélectionnées"""
        total = 0
        for key, widget in self.garantie_widgets.items():
            if widget['checkbox'].isChecked():
                text = widget['amount'].text()
                clean_text = text.replace(" ", "").replace(",", "")
                try:
                    amount = float(clean_text) if clean_text else 0
                    total += amount
                except ValueError:
                    pass
        if self.total_amount:
            self.total_amount.setText(f"{total:,.0f}".replace(",", " ") + " FCFA")
    
    def get_selected_garanties(self):
        """Retourne les garanties sélectionnées avec leurs montants"""
        result = {}
        for key, widget in self.garantie_widgets.items():
            if widget['checkbox'].isChecked():
                text = widget['amount'].text()
                clean_text = text.replace(" ", "").replace(",", "")
                try:
                    amount = float(clean_text) if clean_text else 0
                    result[key] = amount
                except ValueError:
                    result[key] = 0
        return result


class FleetForm(QDialog):
    def __init__(self, controller, current_fleet=None, parent=None, contacts_list=None, compagnies_list=None, mode="add", preselected_client_id=None):
        super().__init__(parent)
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.controller = controller 
        self.current_fleet = current_fleet
        self.contacts_list = contacts_list or []
        self.compagnies_list = compagnies_list or []
        self.mode = "update" if current_fleet else mode
        self.preselected_client_id = preselected_client_id
        self.selected_client_id = None
        self.vehicle_garanties = {}
        self.drag_pos = QPoint()
        self.is_maximized = False
        self.normal_geometry = None
        
        self.setup_ui()
        
        # Charger tous les clients au démarrage
        self.load_all_clients()
        
        if self.current_fleet:
            self.load_data(self.current_fleet)
            self.setWindowTitle(f"Modifier la Flotte : {self.current_fleet.nom_flotte}")
            self.btn_save.setText("💾 METTRE À JOUR LA FLOTTE")

        if self.mode == "view":
            self.freeze_ui()

    def setup_ui(self):
        self.resize(1000, 850)
        self.setMinimumSize(900, 700)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)

        # Carte principale
        self.card = QFrame()
        self.card.setObjectName("FleetCard")
        self.card.setStyleSheet("""
            QFrame#FleetCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border-radius: 24px;
                border: 1px solid rgba(0,0,0,0.08);
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 10)
        self.card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # HEADER
        header_widget = QFrame()
        header_widget.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-top-left-radius: 24px;
                border-top-right-radius: 24px;
            }
        """)
        header_widget.setFixedHeight(80)
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(30, 0, 20, 0)
        
        title_text = QLabel("🏢 Configuration de la Flotte")
        title_text.setStyleSheet("""
            font-size: 20px;
            font-weight: 800;
            color: white;
            font-family: 'Segoe UI', 'Arial';
            letter-spacing: 0.5px;
        """)
        
        btn_style = """
            QPushButton {
                background: rgba(255,255,255,0.2);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 16px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.3);
            }
            QPushButton#closeBtn:hover {
                background: #ff4757;
            }
        """
        
        self.btn_minimize = QPushButton("─")
        self.btn_minimize.setFixedSize(32, 32)
        self.btn_minimize.setStyleSheet(btn_style)
        self.btn_minimize.clicked.connect(self.showMinimized)
        
        self.btn_maximize = QPushButton("□")
        self.btn_maximize.setFixedSize(32, 32)
        self.btn_maximize.setStyleSheet(btn_style)
        self.btn_maximize.clicked.connect(self.toggle_maximize)
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("closeBtn")
        self.btn_close.setFixedSize(32, 32)
        self.btn_close.setStyleSheet(btn_style)
        self.btn_close.clicked.connect(self.reject)
        
        header_layout.addWidget(title_text)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_minimize)
        header_layout.addWidget(self.btn_maximize)
        header_layout.addWidget(self.btn_close)
        
        card_layout.addWidget(header_widget)

        # CONTENU SCROLLABLE
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f2f6;
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0aec0;
            }
        """)
        
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        form_layout = QVBoxLayout(content_widget)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(25)

        group_style = """
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #e2e8f0;
                border-radius: 16px;
                margin-top: 12px;
                padding-top: 12px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 12px 0 12px;
                color: #4a5568;
            }
        """
        
        field_style = """
            QLineEdit, QComboBox, QDateEdit, QTextEdit {
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 10px 14px;
                background-color: white;
                font-size: 13px;
                color: #2d3748;
                font-family: 'Segoe UI';
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
                border-color: #667eea;
                background-color: #faf5ff;
            }
            QLabel {
                color: #4a5568;
                font-weight: 600;
                font-size: 13px;
                margin-bottom: 5px;
            }
        """
        
        # SECTION 1: INFORMATIONS GÉNÉRALES
        group_info = QGroupBox("📋 Informations Générales")
        group_info.setStyleSheet(group_style)
        info_layout = QGridLayout(group_info)
        info_layout.setSpacing(20)
        info_layout.setContentsMargins(25, 25, 25, 25)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex: SABC Logistique")
        self.name_input.setStyleSheet(field_style)
        
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Ex: FL-SABC-2024")
        self.code_input.setStyleSheet(field_style)
        
        info_layout.addWidget(self.create_label_with_icon("🏷️", "Nom de la Flotte"), 0, 0)
        info_layout.addWidget(self.create_label_with_icon("🔢", "Code / Référence"), 0, 1)
        info_layout.addWidget(self.name_input, 1, 0)
        info_layout.addWidget(self.code_input, 1, 1)
        
        form_layout.addWidget(group_info)
        
        # SECTION 2: CLIENT
        group_client = QGroupBox("👤 Client")
        group_client.setStyleSheet(group_style)
        client_layout = QVBoxLayout(group_client)
        client_layout.setSpacing(15)
        client_layout.setContentsMargins(25, 25, 25, 25)
        
        self.owner_search = QLineEdit()
        self.owner_search.setPlaceholderText("🔍 Rechercher un client...")
        self.owner_search.setStyleSheet(field_style + "background: #f7fafc; font-size: 13px;")
        self.owner_search.textChanged.connect(self.filter_contacts)
        client_layout.addWidget(self.owner_search)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background: #e2e8f0; width: 2px; margin: 10px 0; }")
        
        self.client_list_widget = QListWidget()
        self.client_list_widget.setStyleSheet("""
            QListWidget {
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                background: white;
                outline: none;
                padding: 5px;
            }
            QListWidget::item {
                padding: 12px;
                border-radius: 8px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
            }
        """)
        self.client_list_widget.currentRowChanged.connect(self.display_client_details)
        splitter.addWidget(self.client_list_widget)
        
        self.client_card = QFrame()
        self.client_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fef9e7, stop:1 #faf5ff);
                border-radius: 16px;
                border: 2px solid #e2e8f0;
            }
        """)
        card_layout_client = QHBoxLayout(self.client_card)
        card_layout_client.setContentsMargins(20, 20, 20, 20)
        card_layout_client.setSpacing(15)
        
        self.client_photo = QLabel()
        self.client_photo.setFixedSize(100, 100)
        self.client_photo.setAlignment(Qt.AlignCenter)
        self.client_photo.setText("👤")
        self.client_photo.setStyleSheet("""
            background-color: #ecf0f1; 
            border-radius: 50px; 
            color: #bdc3c7; 
            font-size: 50px;
            border: 3px solid #e2e8f0;
        """)
        card_layout_client.addWidget(self.client_photo)
        
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setSpacing(8)
        
        self.lbl_card_name = QLabel("SÉLECTIONNEZ UN CLIENT")
        self.lbl_card_name.setStyleSheet("font-size: 16px; font-weight: 800; color: #2d3748;")
        
        self.lbl_card_info = QLabel("Détails : ---\nTel : ---\nAdresse : ---")
        self.lbl_card_info.setStyleSheet("font-size: 12px; color: #718096; line-height: 1.5;")
        self.lbl_card_info.setWordWrap(True)
        
        details_layout.addWidget(self.lbl_card_name)
        details_layout.addWidget(self.lbl_card_info)
        details_layout.addStretch()
        
        card_layout_client.addWidget(details_widget, 1)
        splitter.addWidget(self.client_card)
        splitter.setSizes([350, 450])
        client_layout.addWidget(splitter)
        form_layout.addWidget(group_client)
        
        # SECTION 3: ASSURANCE ET CONTRAT
        group_contract = QGroupBox("📄 Contrat & Assurance")
        group_contract.setStyleSheet(group_style)
        contract_layout = QGridLayout(group_contract)
        contract_layout.setSpacing(20)
        contract_layout.setContentsMargins(25, 25, 25, 25)
        
        contract_layout.addWidget(self.create_label_with_icon("🏦", "Assureur Principal"), 0, 0)
        self.assureur_input = QComboBox()
        self.assureur_input.setStyleSheet(field_style)
        for cie in self.compagnies_list:
            self.assureur_input.addItem(cie.nom, cie.id)
        contract_layout.addWidget(self.assureur_input, 1, 0)
        
        contract_layout.addWidget(self.create_label_with_icon("💰", "Mode de Facturation"), 0, 1)
        self.combo_mgmt = QComboBox()
        self.combo_mgmt.setStyleSheet(field_style)
        self.combo_mgmt.addItem("🚗 Individuelle (Par véhicule)", "PAR_VEHICULE")
        self.combo_mgmt.addItem("🌍 Globale (Prime de flotte)", "GLOBAL")
        contract_layout.addWidget(self.combo_mgmt, 1, 1)
        
        contract_layout.addWidget(self.create_label_with_icon("📅", "Début Contrat"), 2, 0)
        contract_layout.addWidget(self.create_label_with_icon("📅", "Fin Contrat"), 2, 1)
        
        self.date_debut = QDateEdit()
        self.date_debut.setCalendarPopup(True)
        self.date_debut.setDate(QDate.currentDate())
        self.date_debut.setStyleSheet(field_style)
        contract_layout.addWidget(self.date_debut, 3, 0)
        
        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDate(QDate.currentDate().addYears(1))
        self.date_fin.setStyleSheet(field_style)
        contract_layout.addWidget(self.date_fin, 3, 1)
        
        contract_layout.addWidget(self.create_label_with_icon("📊", "Statut de la Flotte"), 4, 0)
        contract_layout.addWidget(self.create_label_with_icon("🎁", "Remise Commerciale (%)"), 4, 1)
        
        self.status_combo = QComboBox()
        self.status_combo.setStyleSheet(field_style)
        self.status_combo.addItems(["Actif", "En attente", "Résilié", "Bloqué"])
        contract_layout.addWidget(self.status_combo, 5, 0)
        
        self.remise_input = QLineEdit()
        self.remise_input.setPlaceholderText("0.00")
        self.remise_input.setStyleSheet(field_style)
        contract_layout.addWidget(self.remise_input, 5, 1)
        
        form_layout.addWidget(group_contract)
        
        # SECTION 4: VÉHICULES
        group_vehicles = QGroupBox("🚗 Véhicules")
        group_vehicles.setStyleSheet(group_style)
        vehicles_layout = QVBoxLayout(group_vehicles)
        vehicles_layout.setSpacing(15)
        vehicles_layout.setContentsMargins(25, 25, 25, 25)
        
        header_vehicles = QHBoxLayout()
        header_vehicles.addWidget(QLabel("Sélectionnez les véhicules de la flotte"))
        header_vehicles.addStretch()
        
        self.total_prime_lbl = QLabel("Total Primes : 0 FCFA")
        self.total_prime_lbl.setStyleSheet("""
            font-size: 16px;
            font-weight: 800;
            color: #48bb78;
            background: #f0fff4;
            padding: 8px 16px;
            border-radius: 12px;
        """)
        header_vehicles.addWidget(self.total_prime_lbl)
        vehicles_layout.addLayout(header_vehicles)
        
        self.vehicle_search = QLineEdit()
        self.vehicle_search.setPlaceholderText("🔍 Rechercher un véhicule...")
        self.vehicle_search.setStyleSheet(field_style)
        self.vehicle_search.textChanged.connect(self.filter_vehicles)
        vehicles_layout.addWidget(self.vehicle_search)
        
        self.vehicle_table = QTableWidget()
        self.vehicle_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                background: white;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item {
                padding: 12px;
            }
            QHeaderView::section {
                background: #f8fafc;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: bold;
                color: #4a5568;
            }
        """)
        self.vehicle_table.setColumnCount(13)
        self.vehicle_table.setHorizontalHeaderLabels([
            "Sélection", "Immatriculation", "Marque", "RC", "DR", "Vol", 
            "VB", "Incendie", "Bris", "AR", "DTA", "IPT", "Actions"
        ])
        self.vehicle_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.vehicle_table.setAlternatingRowColors(True)
        self.vehicle_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.vehicle_table.setMinimumHeight(300)
        
        vehicles_layout.addWidget(self.vehicle_table)
        self.vehicle_table.itemChanged.connect(self.on_item_changed)
        form_layout.addWidget(group_vehicles)
        
        # SECTION 5: OBSERVATIONS
        group_obs = QGroupBox("📝 Observations")
        group_obs.setStyleSheet(group_style)
        obs_layout = QVBoxLayout(group_obs)
        obs_layout.setContentsMargins(25, 25, 25, 25)
        
        self.obs_input = QTextEdit()
        self.obs_input.setPlaceholderText("Notes de couverture, remarques particulières...")
        self.obs_input.setStyleSheet(field_style + "min-height: 80px;")
        obs_layout.addWidget(self.obs_input)
        form_layout.addWidget(group_obs)
        
        # BOUTON D'ACTION
        self.btn_save = QPushButton("💾 ENREGISTRER LA FLOTTE")
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                font-size: 15px;
                font-weight: bold;
                border-radius: 16px;
                padding: 16px;
                margin-top: 10px;
                font-family: 'Segoe UI';
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a67d8, stop:1 #6b46c1);
            }
        """)
        self.btn_save.clicked.connect(self.validate_and_save)
        form_layout.addWidget(self.btn_save)
        
        scroll.setWidget(content_widget)
        card_layout.addWidget(scroll)
        main_layout.addWidget(self.card)

    def create_label_with_icon(self, icon, text):
        label = QLabel(f"{icon} {text}")
        label.setStyleSheet("font-size: 13px; font-weight: 600; color: #4a5568; margin-bottom: 4px;")
        return label

    def load_all_clients(self):
        """Charge tous les clients dans la liste"""
        self.client_list_widget.clear()
        
        try:
            clients = self.controller.contacts.get_all_contacts()
            print(f"📋 Chargement de {len(clients)} clients")
            
            for client in clients:
                name_display = f"{client.nom} {client.prenom or ''} - {client.telephone or ''}"
                item = QListWidgetItem(name_display)
                item.setData(Qt.UserRole, client)
                self.client_list_widget.addItem(item)
            
            if self.preselected_client_id:
                self.select_preselected_client()
                
        except Exception as e:
            print(f"Erreur chargement clients: {e}")

    def on_item_changed(self, item):
        """Gère tous les changements dans le tableau"""
        if not item or self.vehicle_table.signalsBlocked():
            return
        
        # Si le changement concerne une checkbox
        if item.column() == 0:
            self.update_fleet_totals()
        # Si le changement concerne une cellule de montant
        elif 3 <= item.column() <= 11:
            row = item.row()
            self.update_row_total_fast(row)
            self.update_fleet_totals()

    def update_row_total_fast(self, row):
        """Met à jour le total d'une ligne rapidement"""
        try:
            self.vehicle_table.blockSignals(True)
            
            row_sum = 0
            for col in range(3, 12):
                cell = self.vehicle_table.item(row, col)
                if cell:
                    val = cell.data(Qt.UserRole)
                    if val is None:
                        text = cell.text().replace(" ", "")
                        try:
                            val = float(text) if text else 0
                        except ValueError:
                            val = 0
                    row_sum += float(val)
            
            # Mettre à jour la cellule total
            total_formatted = f"{row_sum:,.0f}".replace(",", " ")
            total_item = QTableWidgetItem(total_formatted)
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            total_item.setData(Qt.UserRole, float(row_sum))
            total_item.setFont(QFont("Arial", 9, QFont.Bold))
            self.vehicle_table.setItem(row, 11, total_item)
            
            self.vehicle_table.blockSignals(False)
            
        except Exception as e:
            print(f"Erreur update_row_total_fast: {e}")
            self.vehicle_table.blockSignals(False)
               
    def select_preselected_client(self):
        """Sélectionne automatiquement le client pré-sélectionné"""
        if not self.preselected_client_id:
            return
        
        for i in range(self.client_list_widget.count()):
            item = self.client_list_widget.item(i)
            if item:
                client = item.data(Qt.UserRole)
                if hasattr(client, 'id') and str(client.id) == str(self.preselected_client_id):
                    self.client_list_widget.setCurrentRow(i)
                    self.display_client_details(i)
                    self.selected_client_id = self.preselected_client_id
                    break

    def filter_contacts(self, text):
        """Filtre les contacts selon la recherche"""
        self.client_list_widget.clear()
        
        if len(text) < 2:
            self.load_all_clients()
            return
        
        clients = self.controller.contacts.get_contacts_for_combo(text)
        
        for client in clients:
            if isinstance(client, tuple):
                name_display = f"{client[1]} {client[2] if len(client) > 2 else ''}"
            else:
                name_display = f"{client.nom} {client.prenom or ''} - {client.telephone or ''}"
                
            item = QListWidgetItem(name_display)
            item.setData(Qt.UserRole, client)
            self.client_list_widget.addItem(item)

    def display_client_details(self, row):
        """Affiche les détails du client sélectionné"""
        if row < 0:
            return
        
        item = self.client_list_widget.currentItem()
        if not item:
            return
        client = item.data(Qt.UserRole)
        
        self.selected_client_id = client.id if hasattr(client, 'id') else client[0]
        
        if hasattr(client, 'nom'):
            client_name = client.nom.upper()
            phone = client.telephone or 'N/A'
            email = client.email or 'N/A'
            adresse = client.adresse or 'N/A'
            nature = getattr(client, 'nature', 'Client')
        else:
            client_name = str(client[1]).upper()
            phone = client[2] if len(client) > 2 else 'N/A'
            email = client[3] if len(client) > 3 else 'N/A'
            adresse = client[4] if len(client) > 4 else 'N/A'
            nature = 'Client'
        
        self.lbl_card_name.setText(f"<b>{client_name}</b><br><small>ID: {self.selected_client_id}</small>")
        
        info_text = f"""📌 NATURE: {nature}
📞 TÉLÉPHONE: {phone}
📧 EMAIL: {email}
📍 ADRESSE: {adresse}"""
        self.lbl_card_info.setText(info_text)
        
        self.filter_vehicles_by_client(self.selected_client_id)

    def filter_vehicles_by_client(self, client_id):
        """Filtre les véhicules pour n'afficher que ceux du client sélectionné"""
        try:
            vehicles = self.controller.vehicles.get_vehicles_by_owner_id(client_id)
            self.update_vehicle_table_with_client_vehicles(vehicles)
        except Exception as e:
            print(f"Erreur filtre véhicules: {e}")

    def update_vehicle_table_with_client_vehicles(self, vehicles):
        """Met à jour le tableau avec les véhicules du client"""
        try:
            self.vehicle_table.blockSignals(True)
            self.vehicle_table.setRowCount(0)
            
            num_v = len(vehicles)
            self.vehicle_table.setRowCount(num_v + 1)
            
            col_totals = {i: 0.0 for i in range(3, 12)}

            for row, v in enumerate(vehicles):
                saved_garanties = self.vehicle_garanties.get(v.id, {})
                
                # Checkbox
                check_item = QTableWidgetItem()
                check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                state = Qt.Checked if (self.current_fleet and v.fleet_id == self.current_fleet.id) else Qt.Unchecked
                check_item.setCheckState(state)
                check_item.setData(Qt.UserRole, v.id)
                self.vehicle_table.setItem(row, 0, check_item)
                
                # Infos
                self.vehicle_table.setItem(row, 1, QTableWidgetItem(str(v.immatriculation)))
                self.vehicle_table.setItem(row, 2, QTableWidgetItem(str(v.marque or "N/A")))
                
                # Garanties
                guarantees = {
                    3: ('rc', v.amt_rc), 4: ('dr', v.amt_dr), 5: ('vol', v.amt_vol),
                    6: ('vb', v.amt_vb), 7: ('in', v.amt_in), 8: ('bris', v.amt_bris),
                    9: ('ar', v.amt_ar), 10: ('dta', v.amt_dta), 11: ('ipt', v.amt_ipt)
                }
                
                row_sum = 0.0
                for col_idx, (gar_key, default_val) in guarantees.items():
                    amt = saved_garanties.get(gar_key, float(default_val or 0))
                    self.vehicle_table.setItem(row, col_idx, self.create_num_item(amt))
                    row_sum += amt
                    if state == Qt.Checked:
                        col_totals[col_idx] += amt
                
                # Total ligne
                total_item = self.create_num_item(row_sum)
                total_item.setFont(QFont("Arial", 9, QFont.Bold))
                self.vehicle_table.setItem(row, 11, total_item)
                if state == Qt.Checked:
                    col_totals[11] += row_sum
                
                # Bouton personnalisation
                btn_custom = QPushButton("✏️")
                btn_custom.setFixedSize(30, 30)
                btn_custom.setCursor(Qt.PointingHandCursor)
                btn_custom.clicked.connect(lambda checked, vid=v.id, row_idx=row: self.customize_vehicle_garanties(vid, row_idx))
                self.vehicle_table.setCellWidget(row, 12, btn_custom)
            
            # Footer
            if num_v > 0:
                last_row = num_v
                self.vehicle_table.setSpan(last_row, 0, 1, 2)
                
                empty_item = QTableWidgetItem("")
                empty_item.setBackground(QColor("#f8fafc"))
                empty_item.setFlags(Qt.NoItemFlags)
                self.vehicle_table.setItem(last_row, 0, empty_item)
                
                lbl_footer = QTableWidgetItem("TOTAL SÉLECTION")
                lbl_footer.setFont(QFont("Arial", 10, QFont.Bold))
                lbl_footer.setTextAlignment(Qt.AlignCenter)
                self.vehicle_table.setItem(last_row, 2, lbl_footer)
                
                for col_idx, total_val in col_totals.items():
                    footer_item = self.create_num_item(total_val)
                    footer_item.setBackground(QColor("#e2e8f0"))
                    footer_item.setFont(QFont("Arial", 10, QFont.Bold))
                    self.vehicle_table.setItem(last_row, col_idx, footer_item)
            
            self.vehicle_table.blockSignals(False)
            self.calculate_totals_on_change(None)
            
        except Exception as e:
            print(f"Erreur update_vehicle_table: {e}")
            if hasattr(self, 'vehicle_table'):
                self.vehicle_table.blockSignals(False)

    def customize_vehicle_garanties(self, vehicle_id, row):
        """Ouvre le dialogue de personnalisation des garanties pour un véhicule"""
        try:
            vehicle = self.controller.vehicles.get_vehicles_by_id(vehicle_id)
            if not vehicle:
                QMessageBox.warning(self, "Erreur", "Véhicule non trouvé")
                return
            
            vehicle_data = {
                'id': vehicle.id,
                'immatriculation': vehicle.immatriculation,
                'marque': vehicle.marque,
                'modele': vehicle.modele,
                'amt_rc': float(vehicle.amt_rc or 0),
                'amt_dr': float(vehicle.amt_dr or 0),
                'amt_vol': float(vehicle.amt_vol or 0),
                'amt_vb': float(vehicle.amt_vb or 0),
                'amt_in': float(vehicle.amt_in or 0),
                'amt_bris': float(vehicle.amt_bris or 0),
                'amt_ar': float(vehicle.amt_ar or 0),
                'amt_dta': float(vehicle.amt_dta or 0),
                'amt_ipt': float(vehicle.amt_ipt or 0)
            }
            
            saved_garanties = self.vehicle_garanties.get(vehicle_id, {})
            dialog = GarantieSelectionDialog(vehicle_data, self)
            
            for key, value in saved_garanties.items():
                if key in dialog.garantie_widgets:
                    dialog.garantie_widgets[key]['checkbox'].setChecked(True)
                    dialog.garantie_widgets[key]['amount'].setText(f"{value:,.0f}".replace(",", " "))
                    dialog.garantie_widgets[key]['amount'].setEnabled(True)
            
            if dialog.exec():
                selected = dialog.get_selected_garanties()
                self.vehicle_garanties[vehicle_id] = selected
                self.update_vehicle_row_garanties(row, selected)
                self.update_fleet_totals()
                
        except Exception as e:
            print(f"Erreur customisation: {e}")
            QMessageBox.warning(self, "Erreur", f"Impossible de personnaliser: {str(e)}")

    def update_vehicle_row_garanties(self, row, garanties):
        """Met à jour les montants des garanties dans le tableau"""
        try:
            # Bloquer tous les signaux
            self.vehicle_table.blockSignals(True)
            
            # Mapping colonne -> clé garantie
            col_mapping = {
                3: 'rc', 4: 'dr', 5: 'vol', 6: 'vb',
                7: 'in', 8: 'bris', 9: 'ar', 10: 'dta', 11: 'ipt'
            }
            
            row_sum = 0
            
            for col, gar_key in col_mapping.items():
                amount = garanties.get(gar_key, 0)
                
                # Créer un NOUVEL item
                formatted_val = f"{amount:,.0f}".replace(",", " ")
                new_item = QTableWidgetItem(formatted_val)
                new_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                new_item.setData(Qt.UserRole, float(amount))
                
                # Remplacer l'item existant
                self.vehicle_table.setItem(row, col, new_item)
                row_sum += amount
            
            # Mettre à jour le total de la ligne
            total_formatted = f"{row_sum:,.0f}".replace(",", " ")
            total_item = QTableWidgetItem(total_formatted)
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            total_item.setData(Qt.UserRole, float(row_sum))
            total_item.setFont(QFont("Arial", 9, QFont.Bold))
            self.vehicle_table.setItem(row, 11, total_item)
            
            # Débloquer les signaux
            self.vehicle_table.blockSignals(False)
            
            # Mettre à jour les totaux de la flotte
            self.update_fleet_totals()
            
        except Exception as e:
            print(f"Erreur mise à jour ligne: {e}")
            self.vehicle_table.blockSignals(False)
            import traceback
            traceback.print_exc()
            
    def update_fleet_totals(self):
        """Met à jour les totaux de la flotte sans utiliser de signaux"""
        try:
            num_rows = self.vehicle_table.rowCount()
            if num_rows <= 1:
                return
            
            last_row = num_rows - 1
            new_totals = {i: 0.0 for i in range(3, 12)}
            selected_count = 0

            for row in range(last_row):
                check_item = self.vehicle_table.item(row, 0)
                if check_item and check_item.checkState() == Qt.Checked:
                    selected_count += 1
                    for col in range(3, 12):
                        cell = self.vehicle_table.item(row, col)
                        if cell:
                            val = cell.data(Qt.UserRole)
                            if val is not None:
                                new_totals[col] += float(val)

            # Mettre à jour le footer sans déclencher de signaux
            self.vehicle_table.blockSignals(True)
            
            for col, total_val in new_totals.items():
                footer_item = self.vehicle_table.item(last_row, col)
                if footer_item:
                    formatted_val = f"{total_val:,.0f}".replace(",", " ")
                    footer_item.setText(formatted_val)
                    footer_item.setData(Qt.UserRole, total_val)
            
            # Mettre à jour le label
            total_global = new_totals[11]
            self.total_prime_lbl.setText(f"Total Primes ({selected_count} véhicules) : {total_global:,.0f} FCFA".replace(",", " "))
            
            self.vehicle_table.blockSignals(False)
            
        except Exception as e:
            print(f"Erreur update_fleet_totals: {e}")
            self.vehicle_table.blockSignals(False)

    def create_num_item(self, val):
        formatted_val = f"{val:,.0f}".replace(",", " ")
        item = QTableWidgetItem(formatted_val)
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        item.setData(Qt.UserRole, float(val or 0))
        return item

    # def calculate_totals_on_change(self, item):
    #     """Calcule les totaux de la flotte"""
    #     try:
    #         self.vehicle_table.blockSignals(True)
            
    #         num_rows = self.vehicle_table.rowCount()
    #         if num_rows <= 1:
    #             self.vehicle_table.blockSignals(False)
    #             return
            
    #         last_row = num_rows - 1
    #         new_totals = {i: 0.0 for i in range(3, 12)}
    #         selected_count = 0

    #         # Parcourir toutes les lignes de véhicules
    #         for row in range(last_row):
    #             check_item = self.vehicle_table.item(row, 0)
    #             is_checked = check_item and check_item.checkState() == Qt.Checked
                
    #             if is_checked:
    #                 selected_count += 1
    #                 # Sommer les valeurs de chaque colonne de montant
    #                 for col in range(3, 12):
    #                     cell = self.vehicle_table.item(row, col)
    #                     if cell:
    #                         # Récupérer la valeur brute stockée dans UserRole
    #                         val = cell.data(Qt.UserRole)
    #                         if val is None:
    #                             # Si UserRole n'existe pas, extraire du texte
    #                             text = cell.text().replace(" ", "")
    #                             try:
    #                                 val = float(text) if text else 0
    #                             except ValueError:
    #                                 val = 0
    #                         new_totals[col] += float(val)

    #         # Mettre à jour la ligne de footer
    #         for col, total_val in new_totals.items():
    #             footer_item = self.vehicle_table.item(last_row, col)
    #             if footer_item:
    #                 footer_item.setText(f"{total_val:,.0f}".replace(",", " "))
    #                 footer_item.setData(Qt.UserRole, total_val)

    #         # Mettre à jour le label global
    #         total_global = new_totals[11]
    #         self.total_prime_lbl.setText(f"Total Primes ({selected_count} véhicules) : {total_global:,.0f} FCFA".replace(",", " "))

    #         self.vehicle_table.blockSignals(False)
            
    #     except Exception as e:
    #         print(f"Erreur calcul totaux: {e}")
    #         self.vehicle_table.blockSignals(False)

    def calculate_totals_on_change(self, item):
        """Calcule les totaux de la flotte (appelé par signal)"""
        if item is not None and item.column() != 0:
            return
        self.update_fleet_totals()    

    def filter_vehicles(self, text):
        for row in range(self.vehicle_table.rowCount()):
            immat = self.vehicle_table.item(row, 1).text().lower()
            marque = self.vehicle_table.item(row, 2).text().lower()
            self.vehicle_table.setRowHidden(row, not (text.lower() in immat or text.lower() in marque))

    def get_selected_vehicles_with_garanties(self):
        selected = []
        for row in range(self.vehicle_table.rowCount() - 1):
            check_item = self.vehicle_table.item(row, 0)
            if check_item and check_item.checkState() == Qt.Checked:
                vehicle_id = check_item.data(Qt.UserRole)
                
                # Récupérer les montants directement du tableau
                amounts = {
                    'rc': self._get_cell_value(row, 3),
                    'dr': self._get_cell_value(row, 4),
                    'vol': self._get_cell_value(row, 5),
                    'vb': self._get_cell_value(row, 6),
                    'in': self._get_cell_value(row, 7),
                    'bris': self._get_cell_value(row, 8),
                    'ar': self._get_cell_value(row, 9),
                    'dta': self._get_cell_value(row, 10),
                    'ipt': self._get_cell_value(row, 11)
                }
                
                selected.append({
                    'vehicle_id': vehicle_id,
                    'garanties': amounts
                })
        
        return selected

    def _get_cell_value(self, row, col):
        item = self.vehicle_table.item(row, col)
        if item:
            text = item.text().replace(" ", "")
            try:
                return float(text) if text else 0
            except ValueError:
                return 0
        return 0

    def load_data(self, fleet):
        self.name_input.setText(fleet.nom_flotte)
        self.code_input.setText(getattr(fleet, 'code', ""))
        self.obs_input.setPlainText(getattr(fleet, 'observations', ""))

    def get_form_data(self):
        remise_text = self.remise_input.text().strip()
        try:
            remise_val = float(remise_text) if remise_text else 0.0
        except ValueError:
            remise_val = 0.0

        last_row = self.vehicle_table.rowCount() - 1

        def get_total_col(col_idx):
            if last_row < 0:
                return 0.0
            item = self.vehicle_table.item(last_row, col_idx)
            return item.data(Qt.UserRole) if item else 0.0
        
        return {
            "nom_flotte": self.name_input.text().strip(),
            "code_flotte": self.code_input.text().strip(),
            "owner_id": self.selected_client_id,
            "assureur": self.assureur_input.currentText(),
            "type_gestion": self.combo_mgmt.currentText(),
            "remise_flotte": remise_val,
            "statut": self.status_combo.currentText(),
            "is_active": self.status_combo.currentText() == "Actif",
            "date_debut": self.date_debut.date().toPython(),
            "date_fin": self.date_fin.date().toPython(),
            "observations": self.obs_input.toPlainText().strip(),
            "total_rc": get_total_col(3), "total_dr": get_total_col(4),
            "total_vol": get_total_col(5), "total_vb": get_total_col(6),
            "total_in": get_total_col(7), "total_bris": get_total_col(8),
            "total_ar": get_total_col(9), "total_dta": get_total_col(10),
            "total_prime_nette": get_total_col(11)
        }

    def validate_and_save(self):
        try:
            data = self.get_form_data()

            if not data["nom_flotte"]:
                QMessageBox.warning(self, "Attention", "Le nom de la flotte est requis.")
                return

            if not data["code_flotte"]:
                QMessageBox.warning(self, "Attention", "Le code de la flotte est requis.")
                return
            
            selected_vehicles = self.get_selected_vehicles_with_garanties()
            vehicle_ids = [v['vehicle_id'] for v in selected_vehicles]
            user_id = getattr(self.parent(), 'current_user_id', 1)

            if self.mode == "update":
                success, msg = self.controller.fleets.update_fleet_data(self.current_fleet.id, data, user_id)
                if success:
                    self.controller.fleets.update_fleet_vehicles(self.current_fleet.id, vehicle_ids, user_id)
            else:
                success, fleet_id = self.controller.fleets.create_fleet(data, user_id)
                if success and isinstance(fleet_id, int):
                    self.controller.fleets.update_fleet_vehicles(fleet_id, vehicle_ids, user_id)

            if success:
                self.accept()
            else:
                QMessageBox.critical(self, "Erreur", f"Erreur: {msg}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur Critique", str(e))

    def toggle_maximize(self):
        if self.is_maximized:
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            self.btn_maximize.setText("□")
        else:
            self.normal_geometry = self.geometry()
            screen_geometry = self.screen().availableGeometry()
            self.setGeometry(screen_geometry)
            self.btn_maximize.setText("❐")
        self.is_maximized = not self.is_maximized

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.is_maximized:
            child = self.childAt(event.pos())
            if not isinstance(child, (QPushButton, QLineEdit, QComboBox, QTextEdit, QTableWidget, QListWidget)):
                self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_pos') and not self.is_maximized:
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.pos() + delta)
            self.drag_pos = event.globalPosition().toPoint()

    def freeze_ui(self):
        for widget in self.findChildren((QLineEdit, QComboBox, QTextEdit, QDateEdit, QTableWidget)):
            widget.setEnabled(False)
        self.btn_save.setEnabled(False)