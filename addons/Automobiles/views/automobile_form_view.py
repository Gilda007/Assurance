import os
from PySide6.QtWidgets import (QCheckBox, QDialog, QListWidget, QListWidgetItem, QVBoxLayout, QHBoxLayout, QGridLayout, QProgressBar,
                             QLabel, QLineEdit, QComboBox, QPushButton, QFrame, 
                             QGraphicsDropShadowEffect, QWidget, QScrollArea, QTextEdit, QDateEdit, QMessageBox, QApplication,
                             QGroupBox, QSplitter, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QPoint, QDate, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPixmap, QFont, QLinearGradient, QBrush
import socket
import platform
import requests

class VehicleForm(QDialog):
    def __init__(self, controller, contacts_list=None, current_user=None, data=None, mode="add", vehicle_to_edit=None):
        super().__init__()
      
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.controller = controller
        self.contacts = contacts_list or []
        self.current_user = current_user
        self.mode = mode
        self.initial_data = data
        self.vehicle_to_edit = vehicle_to_edit
        self.vehicle_id = vehicle_to_edit.id if hasattr(vehicle_to_edit, 'id') else None
        self.selected_cie_id = None
        self.old_pos = None
        self.is_maximized = False
        self.normal_geometry = None
        
        self.setup_ui()

        if vehicle_to_edit:
            self.load_existing_data(vehicle_to_edit)

        if self.initial_data:
            self.fill_form(self.initial_data)
        
        if self.mode == "view":
            self.freeze_ui()

    def setup_ui(self):
        self.resize(950, 850)
        self.setMinimumSize(900, 750)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)

        # Carte principale
        self.card = QFrame()
        self.card.setObjectName("MainCard")
        self.card.setStyleSheet("""
            QFrame#MainCard {
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

        # --- HEADER GRADIENT ---
        header_widget = QFrame()
        header_widget.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2c3e50);
                border-top-left-radius: 24px;
                border-top-right-radius: 24px;
            }
        """)
        header_widget.setFixedHeight(80)
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(30, 0, 20, 0)
        
        # Titre avec icône
        title_text = QLabel("🚗 FICHE COMPLÈTE DU VÉHICULE")
        title_text.setStyleSheet("""
            font-size: 20px;
            font-weight: 800;
            color: white;
            font-family: 'Segoe UI', 'Arial';
            letter-spacing: 0.5px;
        """)
        
        # Boutons de contrôle
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
                background: #e74c3c;
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

        # --- SCROLL AREA ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
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
                background: #3498db;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        form_layout = QVBoxLayout(content)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(25)

        # Style commun pour les groupes
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
                color: #2c3e50;
            }
        """
        
        # Style des champs
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
                border-color: #3498db;
                background-color: #f0f9ff;
            }
            QLabel {
                color: #4a5568;
                font-weight: 600;
                font-size: 12px;
                margin-bottom: 4px;
            }
        """
        
        # === SECTION 1: PROPRIÉTAIRE ===
        group_owner = QGroupBox("👤 PROPRIÉTAIRE DU VÉHICULE")
        group_owner.setStyleSheet(group_style)
        owner_layout = QVBoxLayout(group_owner)
        owner_layout.setSpacing(15)
        owner_layout.setContentsMargins(25, 25, 25, 25)
        
        # Barre de recherche
        self.owner_search = QLineEdit()
        self.owner_search.setPlaceholderText("🔍 Rechercher un client (Nom, téléphone, ou n° de pièce)...")
        self.owner_search.setStyleSheet(field_style)
        self.owner_search.textChanged.connect(self.filter_clients)
        owner_layout.addWidget(self.owner_search)
        
        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background: #e2e8f0; width: 2px; margin: 10px 0; }")
        
        # Liste des clients
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
            QListWidget::item:hover {
                background: #f7fafc;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2c3e50);
                color: white;
            }
        """)
        self.client_list_widget.currentRowChanged.connect(self.display_client_details)
        splitter.addWidget(self.client_list_widget)
        
        # Carte client
        self.client_card = QFrame()
        self.client_card.setObjectName("ClientCard")
        self.client_card.setStyleSheet("""
            QFrame#ClientCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fef9e7, stop:1 #f0f9ff);
                border-radius: 16px;
                border: 2px solid #e2e8f0;
            }
        """)
        card_layout_client = QHBoxLayout(self.client_card)
        card_layout_client.setContentsMargins(20, 20, 20, 20)
        card_layout_client.setSpacing(15)
        
        # Photo
        self.client_photo = QLabel()
        self.client_photo.setObjectName("PhotoLabel")
        self.client_photo.setFixedSize(90, 90)
        self.client_photo.setStyleSheet("""
            QLabel {
                background: white;
                border-radius: 45px;
                border: 3px solid #e2e8f0;
            }
        """)
        self.client_photo.setAlignment(Qt.AlignCenter)
        card_layout_client.addWidget(self.client_photo)
        
        # Détails
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setSpacing(8)
        
        self.lbl_card_name = QLabel("SÉLECTIONNEZ UN CLIENT")
        self.lbl_card_name.setStyleSheet("font-size: 16px; font-weight: 800; color: #2c3e50;")
        
        self.lbl_card_info = QLabel("Détails : ---\nTel : ---\nAdresse : ---")
        self.lbl_card_info.setStyleSheet("font-size: 12px; color: #718096; line-height: 1.5;")
        self.lbl_card_info.setWordWrap(True)
        
        details_layout.addWidget(self.lbl_card_name)
        details_layout.addWidget(self.lbl_card_info)
        details_layout.addStretch()
        
        card_layout_client.addWidget(details_widget, 1)
        splitter.addWidget(self.client_card)
        splitter.setSizes([350, 450])
        
        owner_layout.addWidget(splitter)
        form_layout.addWidget(group_owner)
        
        # === SECTION 2: IDENTIFICATION & TECHNIQUE ===
        group_id = QGroupBox("🔍 IDENTIFICATION & CARACTÉRISTIQUES")
        group_id.setStyleSheet(group_style)
        id_layout = QGridLayout(group_id)
        id_layout.setSpacing(20)
        id_layout.setContentsMargins(25, 25, 25, 25)
        
        # Ligne 1: Immatriculation et Châssis
        id_layout.addWidget(self.create_label_with_icon("🔢", "Immatriculation"), 0, 0)
        id_layout.addWidget(self.create_label_with_icon("🔧", "N° Châssis"), 0, 1)
        
        self.immat_input = QLineEdit()
        self.immat_input.setStyleSheet(field_style)
        id_layout.addWidget(self.immat_input, 1, 0)
        
        self.chassis_input = QLineEdit()
        self.chassis_input.setStyleSheet(field_style)
        id_layout.addWidget(self.chassis_input, 1, 1)
        
        # Ligne 2: Marque, Modèle, Année
        id_layout.addWidget(self.create_label_with_icon("🏭", "Marque"), 2, 0)
        id_layout.addWidget(self.create_label_with_icon("📱", "Modèle"), 2, 1)
        id_layout.addWidget(self.create_label_with_icon("📅", "Année"), 2, 2)
        
        self.marque_input = QLineEdit()
        self.marque_input.setStyleSheet(field_style)
        id_layout.addWidget(self.marque_input, 3, 0)
        
        self.modele_input = QLineEdit()
        self.modele_input.setStyleSheet(field_style)
        id_layout.addWidget(self.modele_input, 3, 1)
        
        self.annee_input = QLineEdit()
        self.annee_input.setStyleSheet(field_style)
        self.annee_input.setPlaceholderText("2024")
        id_layout.addWidget(self.annee_input, 3, 2)
        
        # Ligne 3: Énergie, Puissance, Places
        id_layout.addWidget(self.create_label_with_icon("⛽", "Énergie"), 4, 0)
        id_layout.addWidget(self.create_label_with_icon("⚡", "Puissance (CV)"), 4, 1)
        id_layout.addWidget(self.create_label_with_icon("👥", "Places"), 4, 2)
        
        self.energie_combo = QComboBox()
        self.energie_combo.addItems(["Essence", "Diesel", "Hybride", "Electrique"])
        self.energie_combo.setStyleSheet(field_style)
        id_layout.addWidget(self.energie_combo, 5, 0)
        
        self.usage_input = QLineEdit()
        self.usage_input.setStyleSheet(field_style)
        self.usage_input.setPlaceholderText("Ex: 7 CV")
        id_layout.addWidget(self.usage_input, 5, 1)
        
        self.places_input = QLineEdit()
        self.places_input.setStyleSheet(field_style)
        self.places_input.setPlaceholderText("5")
        id_layout.addWidget(self.places_input, 5, 2)
        
        # Ligne 4: Zone, Catégorie, Remorque
        id_layout.addWidget(self.create_label_with_icon("🗺️", "Zone"), 6, 0)
        id_layout.addWidget(self.create_label_with_icon("📊", "Catégorie"), 6, 1)
        
        self.combo_zone = QComboBox()
        self.combo_zone.addItems(["A", "B", "C"])
        self.combo_zone.setStyleSheet(field_style)
        id_layout.addWidget(self.combo_zone, 7, 0)
        
        self.combo_cat = QLineEdit()
        self.combo_fleet = QLineEdit()
        self.combo_cat.setStyleSheet(field_style)
        self.combo_cat.setPlaceholderText("01, 02, ...")
        id_layout.addWidget(self.combo_cat, 7, 1)
        
        self.check_remorque = QCheckBox("🚛 Véhicule avec Remorque")
        self.check_remorque.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                font-weight: 600;
                color: #4a5568;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #cbd5e0;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
            }
        """)
        id_layout.addWidget(self.check_remorque, 7, 2)
        id_layout.addWidget(self.create_label_with_icon("🏷️", "Libellé du tarif"), 8, 0, 1, 2)

        self.combo_fleet = QLineEdit()
        self.combo_fleet.setStyleSheet(field_style)
        self.combo_fleet.setPlaceholderText("Ex: Tarif Standard, Tarif Premium, ...")
        id_layout.addWidget(self.combo_fleet, 9, 0, 1, 2)

        
        form_layout.addWidget(group_id)
        
        # === SECTION 3: VALEURS & PÉRIODE ===
        group_values = QGroupBox("💰 VALEURS & PÉRIODE")
        group_values.setStyleSheet(group_style)
        values_layout = QGridLayout(group_values)
        values_layout.setSpacing(20)
        values_layout.setContentsMargins(25, 25, 25, 25)
        
        # Valeurs
        values_layout.addWidget(self.create_label_with_icon("💎", "Valeur à Neuf (FCFA)"), 0, 0)
        values_layout.addWidget(self.create_label_with_icon("📉", "Valeur Vénale (FCFA)"), 0, 1)
        values_layout.addWidget(self.create_label_with_icon("📊", "Statut"), 0, 2)
        
        self.val_neuf = QLineEdit()
        self.val_neuf.setStyleSheet(field_style)
        self.val_neuf.setPlaceholderText("0")
        self.val_neuf.textChanged.connect(self.refresh_all_garanties)
        values_layout.addWidget(self.val_neuf, 1, 0)
        
        self.val_venale = QLineEdit()
        self.val_venale.setStyleSheet(field_style)
        self.val_venale.setPlaceholderText("0")
        self.val_venale.textChanged.connect(self.refresh_all_garanties)
        values_layout.addWidget(self.val_venale, 1, 1)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["En Circulation", "En Panne", "Vendu", "Saisi"])
        self.status_combo.setStyleSheet(field_style)
        values_layout.addWidget(self.status_combo, 1, 2)
        
        # Dates
        values_layout.addWidget(self.create_label_with_icon("📅", "Date Début"), 2, 0)
        values_layout.addWidget(self.create_label_with_icon("📅", "Date Fin"), 2, 1)
        
        self.date_debut = QDateEdit()
        self.date_debut.setDisplayFormat("dd/MM/yyyy")
        self.date_debut.setCalendarPopup(True)
        self.date_debut.setDate(QDate.currentDate())
        self.date_debut.setStyleSheet(field_style)
        self.date_debut.dateChanged.connect(self.refresh_all_garanties)
        values_layout.addWidget(self.date_debut, 3, 0)
        
        self.date_fin = QDateEdit()
        self.date_fin.setDisplayFormat("dd/MM/yyyy")
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDate(QDate.currentDate().addYears(1))
        self.date_fin.setStyleSheet(field_style)
        self.date_fin.dateChanged.connect(self.refresh_all_garanties)
        values_layout.addWidget(self.date_fin, 3, 1)
        
        form_layout.addWidget(group_values)
        
        # === SECTION 4: GARANTIES ===
        group_garanties = QGroupBox("🛡️ GARANTIES & COTISATIONS")
        group_garanties.setStyleSheet(group_style)
        garanties_layout = QGridLayout(group_garanties)
        garanties_layout.setSpacing(15)
        garanties_layout.setContentsMargins(25, 25, 25, 25)
        
        # Dictionnaire pour stocker les labels de résultat
        self.result_labels = {}
        
        # Liste des garanties
        garanties = [
            ("rc", "RC (Resp. Civile)", "💰 RC"),
            ("dr", "Défense Recours", "⚖️ DR"),
            ("vol", "Vol / Vol partie", "🚗 VOL"),
            ("vb", "Vol / Braquage", "🔫 VB"),
            ("in", "Incendie", "🔥 INC"),
            ("bris", "Bris de Glace", "🪟 BG"),
            ("ar", "Assistance Réparation", "🔧 AR"),
            ("dta", "Dommages Tous Accidents", "💥 DTA"),
            ("ipt", "Indiv. Personnes Transportées", "👥 IPT")
        ]
        
        for i, (key, label, short_label) in enumerate(garanties):
            # Checkbox
            checkbox = QCheckBox(label)
            checkbox.setStyleSheet("""
                QCheckBox {
                    font-size: 12px;
                    font-weight: 600;
                    color: #4a5568;
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border-radius: 4px;
                    border: 2px solid #cbd5e0;
                }
                QCheckBox::indicator:checked {
                    background-color: #3498db;
                    border-color: #3498db;
                }
            """)
            setattr(self, f"check_{key}", checkbox)
            
            # Label de résultat
            res_lbl = QLabel("0 FCFA")
            res_lbl.setStyleSheet("""
                font-weight: bold;
                color: #27ae60;
                font-size: 13px;
                background: #e8f5e9;
                padding: 6px 12px;
                border-radius: 8px;
            """)
            res_lbl.setVisible(False)
            self.result_labels[key] = res_lbl
            
            # Ajout au grid
            garanties_layout.addWidget(checkbox, i, 0)
            garanties_layout.addWidget(QLabel(short_label), i, 1)
            garanties_layout.addWidget(res_lbl, i, 2)
            
            checkbox.stateChanged.connect(lambda state, k=key: self.update_garantie_price(k, state))
        
        form_layout.addWidget(group_garanties)
        
        # === SECTION 5: RÉCAPITULATIF FINANCIER ===
        group_recap = QGroupBox("🧮 RÉCAPITULATIF FINANCIER")
        group_recap.setStyleSheet(group_style)
        recap_layout = QGridLayout(group_recap)
        recap_layout.setSpacing(20)
        recap_layout.setContentsMargins(25, 25, 25, 25)
        
        # Style pour les champs calculés
        style_auto = """
            background-color: #f8f9fa;
            color: #2c3e50;
            font-weight: bold;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 12px;
            font-size: 14px;
        """
        
        style_nette = """
            background-color: #e3f2fd;
            color: #1976d2;
            font-weight: bold;
            border: 2px solid #bbdef5;
            border-radius: 12px;
            padding: 12px;
            font-size: 16px;
        """
        
        recap_layout.addWidget(QLabel("💰 Prime Brute"), 0, 0)
        recap_layout.addWidget(QLabel("🎁 Réduction"), 0, 1)
        recap_layout.addWidget(QLabel("✨ Prime Nette"), 0, 2)
        
        self.prime_brute = QLineEdit("0")
        self.prime_brute.setReadOnly(True)
        self.prime_brute.setStyleSheet(style_auto)
        recap_layout.addWidget(self.prime_brute, 1, 0)
        
        self.reduction = QLineEdit("0")
        self.reduction.setReadOnly(True)
        self.reduction.setStyleSheet(style_auto)
        recap_layout.addWidget(self.reduction, 1, 1)
        
        self.prime_nette = QLineEdit("0")
        self.prime_nette.setReadOnly(True)
        self.prime_nette.setStyleSheet(style_nette)
        recap_layout.addWidget(self.prime_nette, 1, 2)
        
        self.prime_emise = QLineEdit()
        self.prime_emise.setReadOnly(True)
        self.prime_emise.setVisible(False)  # Champ caché pour la BD
        checkbox.stateChanged.connect(lambda state, k=key: self.handle_garantie_click(k, state))
        checkbox.stateChanged.connect(lambda state, k=key: self.update_garantie_price(k, state))
        
        form_layout.addWidget(group_recap)
        
        # --- PROGRESS BAR ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                text-align: center;
                background-color: #F8F9FA;
                height: 30px;
                font-weight: bold;
                color: #333;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #2ECC71, stop:1 #27AE60);
                border-radius: 8px;
            }
        """)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        
        # --- FOOTER ---
        footer = QHBoxLayout()
        footer.setContentsMargins(30, 20, 30, 30)
        
        self.btn_save = QPushButton("💾 ENREGISTRER LE VÉHICULE")
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2c3e50);
                color: white;
                font-size: 15px;
                font-weight: bold;
                border-radius: 16px;
                padding: 14px 32px;
                font-family: 'Segoe UI';
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2980b9, stop:1 #1e2a3a);
            }
            QPushButton:pressed {
                padding-top: 15px;
                padding-bottom: 13px;
            }
        """)
        self.btn_save.clicked.connect(self.validate_and_save)
        
        footer.addStretch()
        footer.addWidget(self.btn_save)
        footer.addStretch()
        footer.addWidget(self.progress_bar)
        
        scroll.setWidget(content)
        card_layout.addWidget(scroll)
        card_layout.addLayout(footer)
        
        main_layout.addWidget(self.card)

    def create_label_with_icon(self, icon, text):
        """Crée un label avec icône et texte"""
        label = QLabel(f"{icon} {text}")
        label.setStyleSheet("""
            font-size: 12px;
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 4px;
        """)
        return label

    def toggle_maximize(self):
        """Bascule entre mode normal et plein écran"""
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
        """Gère le déplacement de la fenêtre"""
        if event.button() == Qt.LeftButton and not self.is_maximized:
            child = self.childAt(event.pos())
            if not isinstance(child, (QPushButton, QLineEdit, QComboBox, QTextEdit, QListWidget, QCheckBox)):
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        """Déplace la fenêtre"""
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_position') and not self.is_maximized:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Libère le déplacement"""
        if hasattr(self, 'drag_position'):
            delattr(self, 'drag_position')

    # ... (toutes les autres méthodes existantes restent identiques)
    def filter_clients(self, text):
        """Filtre les clients selon la recherche"""
        self.client_list_widget.clear()
        if len(text) < 2:
            return
        
        clients = self.controller.compagnies.get_contacts_for_combo(text)
        
        for client in clients:
            if isinstance(client, tuple):
                name_display = f"{client[0]} {client[1] if len(client) > 1 else ''}"
            else:
                name_display = f"{client.nom} {client.code or ''}"
                
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
        
        self.selected_cie_id = client.id
        
        name_html = (
            f"<div style='color: #2c3e50; font-size: 16px; font-weight: bold;'>"
            f"{client.nom.upper()}</div>"
            f"<div style='color: #7f8c8d; font-size: 11px;'>ID: {client.code or 'N/A'}</div>"
        )
        self.lbl_card_name.setText(name_html)
        
        info_text = f"""
            <table width="100%" style="margin-top: 10px;">
                <tr>
                    <td style="color: #95a5a6; font-size: 11px;">📌 NATURE</td>
                    <td style="color: #34495e; font-weight: 500;">{getattr(client, 'nature', 'Compagnie')}</td>
                </tr>
                <tr>
                    <td style="color: #95a5a6; font-size: 11px; padding-top: 5px;">📞 TÉLÉPHONE</td>
                    <td style="color: #34495e; font-weight: 500; padding-top: 5px;">{client.telephone or 'N/A'}</td>
                </tr>
                <tr>
                    <td style="color: #95a5a6; font-size: 11px; padding-top: 5px;">📧 EMAIL</td>
                    <td style="color: #34495e; font-weight: 500; padding-top: 5px;">{client.email or 'N/A'}</td>
                </tr>
                <tr>
                    <td style="color: #95a5a6; font-size: 11px; padding-top: 5px;">📍 ADRESSE</td>
                    <td style="color: #34495e; font-weight: 500; padding-top: 5px;">{client.adresse or 'N/A'}</td>
                </tr>
            </table>
        """
        self.lbl_card_info.setText(info_text)
        
        if hasattr(client, 'photo_path') and client.photo_path and os.path.exists(client.photo_path):
            pixmap = QPixmap(client.photo_path)
            self.client_photo.setPixmap(pixmap.scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.client_photo.setAlignment(Qt.AlignCenter)
            self.client_photo.setStyleSheet("""
                background-color: #ecf0f1; 
                border-radius: 45px; 
                color: #bdc3c7; 
                font-size: 45px;
                border: 3px solid #e2e8f0;
            """)
            self.client_photo.setText("👤")

    def load_existing_data(self, v):
        """Charge les données d'un véhicule existant"""
        try:
            # Textes
            text_fields = [
                ('immatriculation', self.immat_input),
                ('chassis', self.chassis_input),
                ('marque', self.marque_input),
                ('modele', self.modele_input),
                ('usage', self.usage_input),
            ]
            for attr, widget in text_fields:
                widget.setText(str(getattr(v, attr, "")) if getattr(v, attr, None) else "")
            
            # Nombres
            if hasattr(v, 'annee') and v.annee:
                self.annee_input.setText(str(v.annee))
            
            if hasattr(v, 'places') and v.places:
                self.places_input.setText(str(v.places))
            
            self.val_neuf.setText(str(getattr(v, 'valeur_neuf', 0) or 0))
            self.val_venale.setText(str(getattr(v, 'valeur_venale', 0) or 0))
            
            # Combobox
            if hasattr(v, 'energie') and v.energie:
                index = self.energie_combo.findText(v.energie, Qt.MatchFlag.MatchExactly)
                if index >= 0:
                    self.energie_combo.setCurrentIndex(index)
            
            if hasattr(v, 'statut') and v.statut:
                index = self.status_combo.findText(v.statut, Qt.MatchFlag.MatchExactly)
                if index >= 0:
                    self.status_combo.setCurrentIndex(index)
            
            # Dates
            if hasattr(v, 'date_debut') and v.date_debut:
                d = v.date_debut
                q_date = QDate(d.year, d.month, d.day)
                self.date_debut.setDate(q_date)
            
            if hasattr(v, 'date_fin') and v.date_fin:
                d = v.date_fin
                q_date = QDate(d.year, d.month, d.day)
                self.date_fin.setDate(q_date)
            
            # Checkboxes garanties
            garanties_keys = ["rc", "dr", "vol", "vb", "in", "bris", "ar", "dta", "ipt"]
            for key in garanties_keys:
                checkbox = getattr(self, f"check_{key}", None)
                if checkbox:
                    valeur_bd = getattr(v, f"check_{key}", False)
                    checkbox.setChecked(bool(valeur_bd))
                    if self.result_labels.get(key):
                        self.result_labels[key].setVisible(bool(valeur_bd))
            
            # Propriétaire
            if hasattr(v, 'owner_id') and v.owner_id:
                for i in range(self.client_list_widget.count()):
                    item = self.client_list_widget.item(i)
                    if item and item.data(Qt.UserRole) and item.data(Qt.UserRole).id == v.owner_id:
                        self.client_list_widget.setCurrentItem(item)
                        break
            
            # Rafraîchir les calculs
            self.refresh_all_garanties()
            
        except Exception as e:
            print(f"Erreur lors du chargement : {str(e)}")

    def get_form_data(self):
        """Récupère les données du formulaire"""
        def clean_amt(key):
            label = self.result_labels.get(key)
            if label and label.isVisible():
                txt = label.text().replace(" FCFA", "").replace(" ", "").replace(",", ".")
                return float(txt) if txt else 0.0
            return 0.0
        
        def clean_input(widget):
            txt = widget.text().replace(" ", "").replace(",", ".")
            return float(txt) if txt else 0.0
        
        data = {
            # --- IDENTIFICATION & PROPRIÉTAIRE ---
            "immatriculation": self.immat_input.text().strip().upper(),
            "chassis": self.chassis_input.text().strip().upper(),
            "zone": self.combo_zone.currentText(),
            "libele_tarif": self.combo_fleet.text().strip().upper(),
            "categorie": self.combo_cat.text(),
            "compagny_id": self.client_list_widget.currentItem().data(Qt.UserRole).id if self.client_list_widget.currentItem() else None,
            "marque": self.marque_input.text().strip(),
            "modele": self.modele_input.text().strip(),
            "annee": int(self.annee_input.text()) if self.annee_input.text().isdigit() else None,
            "energie": self.energie_combo.currentText(),
            "usage": self.usage_input.text().strip(),
            "places": int(self.places_input.text()) if self.places_input.text().isdigit() else 5,
            "has_remorque": self.check_remorque.isChecked(),
            "statut": self.status_combo.currentText(),

            # --- DATES (Conversion QDate -> Python Date) ---
            "date_debut": self.date_debut.date().toPython(),
            "date_fin": self.date_fin.date().toPython(),

            # --- RÉCAPITULATIF FINANCIER ---
            "valeur_neuf": clean_input(self.val_neuf),
            "valeur_venale": clean_input(self.val_venale),
            "prime_brute": clean_input(self.prime_brute),
            "reduction": clean_input(self.reduction),
            "prime_nette": clean_input(self.prime_nette),
            "prime_emise": clean_input(self.prime_nette), # prime_emise = prime_nette

            # --- ÉTAT DES GARANTIES (Booleans) ---
            "check_rc": self.check_rc.isChecked(),
            "check_dr": self.check_dr.isChecked(),
            "check_vol": self.check_vol.isChecked(),
            "check_vb": self.check_vb.isChecked(),
            "check_in": self.check_in.isChecked(),
            "check_bris": self.check_bris.isChecked(),
            "check_ar": self.check_ar.isChecked(),
            "check_dta": self.check_dta.isChecked(),
            "check_ipt": self.check_ipt.isChecked(),

            # --- MONTANTS DES GARANTIES (Valeurs calculées) ---
            "amt_rc": clean_amt("rc"),
            "amt_dr": clean_amt("dr"),
            "amt_vol": clean_amt("vol"),
            "amt_vb": clean_amt("vb"),
            "amt_in": clean_amt("in"),
            "amt_bris": clean_amt("bris"),
            "amt_ar": clean_amt("ar"),
            "amt_dta": clean_amt("dta"),
            "amt_ipt": clean_amt("ipt")
        }
        return data

    def validate_and_save(self):
        """Valide et sauvegarde le véhicule"""
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.btn_save.setEnabled(False)
        self.btn_save.setText("⏳ Traitement en cours...")
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)
        QApplication.processEvents()
        
        try:
            data = self.get_form_data()
            ip_local = socket.gethostbyname(socket.gethostname())
            ip_public = None
            try:
                ip_public = requests.get('https://api.ipify.org', timeout=1).text
            except:
                ip_public = "Non disponible"
            
            self.progress_bar.setValue(30)
            current_user_id = getattr(self, "current_user_id", 1)
            
            if hasattr(self, 'vehicle_to_edit') and self.vehicle_to_edit and hasattr(self.vehicle_to_edit, 'id'):
                self.progress_bar.setValue(50)
                success, message = self.controller.vehicles.update_vehicle(
                    vehicle_id=self.vehicle_to_edit.id, 
                    new_data=data, 
                    user_id=current_user_id,
                    local_ip=ip_local,
                    public_ip=ip_public
                )
            else:
                self.progress_bar.setValue(50)
                success, message = self.controller.vehicles.create_vehicle(
                    data=data, 
                    user_id=current_user_id,
                    local_ip=ip_local,
                    public_ip=ip_public
                )
            
            self.progress_bar.setValue(90)
            QApplication.processEvents()
            
            if success:
                self.progress_bar.setValue(100)
                QApplication.restoreOverrideCursor()
                import time
                time.sleep(0.3)
                self.accept()
            else:
                raise Exception(message)
                
        except Exception as e:
            QApplication.restoreOverrideCursor()
            self.btn_save.setEnabled(True)
            self.btn_save.setText("💾 ENREGISTRER LE VÉHICULE")
            self.progress_bar.setVisible(False)
            QMessageBox.critical(self, "Erreur de sauvegarde", f"Détails : {str(e)}")

    def get_data(self):
        data = {
            "libele_tarif": self.combo_fleet.text().strip().upper(),
            "immatriculation": self.immat_input.text().strip().upper(),
            "chassis": self.chassis_input.text().strip(),
            "zone": self.combo_zone.currentText(),
            "categorie": self.combo_cat.text(),
            "marque": self.marque_input.text().strip(),
            "modele": self.modele_input.text().strip(),
            "annee": self.annee_input.text().strip(),
            "places": int(self.places_input.text() or 0),
            "energie": self.energie_combo.currentText(),
            "remorque": self.check_remorque.isChecked(),
            "val_neuf": float(self.val_neuf.text() or 0),
            "val_venale": float(self.val_venale.text() or 0),
            "usage": self.usage_input.text().strip(),
            "prime_emise": float(self.prime_emise.text() or 0),
            "statut": self.status_combo.currentText(),
            # Garanties (Booléens)
            "garantie_rc": self.check_rc.isChecked(),
            "garantie_tc": self.check_tc.isChecked(),
            "garantie_vol": self.check_vol.isChecked(),
            "garantie_bris": self.check_bris.isChecked(),
            "garantie_dom": self.check_dom.isChecked(),
            "garantie_dr": self.check_dr.isChecked(),
            "proprietaire_nom": self.owner_name.text().strip(),
            "proprietaire_type": self.owner_type.currentText(),
            "proprietaire_tel": self.owner_phone.text().strip(),
            "proprietaire_adresse": self.owner_address.text().strip(),
        }
        return data
    
    def get_system_info(self):
        """Récupère l'IP locale et le nom de la machine."""
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            os_info = f"{platform.system()} {platform.release()}"
            print(os_info)
            return {
                "ip_address": ip_address,
                "hostname": hostname,
                "os_info": os_info
            }
        except Exception:
            return {"ip_address": "127.0.0.1", "hostname": "unknown", "os_info": "N/A"}
   
    def freeze_ui(self):
        """Désactive tous les champs pour la consultation"""
        for widget in self.findChildren((QLineEdit, QComboBox, QTextEdit, QCheckBox, QDateEdit)):
            widget.setEnabled(False)
        self.btn_save.setEnabled(False)
        self.setWindowTitle("Consultation du véhicule")


    # GESTION DES GARANTIES POUR AFFICHAGE SUR INTERFACE ET ENREGISTREMENT
    def update_rc_calculation(self):
        """Récupère les données du formulaire et interroge le contrôleur pour la RC."""
        try:
            # 1. Récupération des informations du formulaire
            # Note: Assurez-vous que ces noms d'attributs correspondent à vos widgets
            cie_id = self.selected_cie_id 
            zone = self.combo_zone.currentText()
            categorie = self.combo_cat.text() # ex: '01'
            energie = self.energie_combo.currentText() # 'Essence' ou 'Diesel'
            
            cv_text = self.usage_input.text().strip()
            cv = int(cv_text) if cv_text else 0
            
            # Vérification si la checkbox remorque globale est cochée
            avec_remorque = self.check_remorque.isChecked() 

            # 2. Appel de la méthode de matrice via le contrôleur
            if self.controller:
                montant_rc = self.controller.vehicles.get_rc_premium_from_matrix(
                    cie_id=cie_id,
                    zone=zone,
                    categorie=categorie,
                    energie=energie,
                    cv_saisi=cv,
                    avec_remorque=avec_remorque
                )

                # 3. Mise à jour du label de résultat
                if montant_rc > 0:
                    self.result_labels["rc"].setText(f"{montant_rc:,.0f} FCFA")
                else:
                    self.result_labels["rc"].setText("Tarif introuvable")

        except Exception as e:
            print(f"Erreur lors du calcul RC : {e}")
            self.result_labels["rc"].setText("Erreur calcul")
  
    def calculate_total_premium(self):
        """Calcule le total des primes"""
        try:
            def get_amt(key):
                label = self.result_labels.get(key)
                if label and label.isVisible():
                    txt = label.text().replace(" FCFA", "").replace(" ", "").replace(",", ".")
                    return float(txt) if txt else 0.0
                return label
            
            amt_rc = get_amt("rc")
            amt_dr = get_amt("dr")
            amt_vol = get_amt("vol")
            amt_vb = get_amt("vb")
            amt_in = get_amt("in")
            amt_bris = get_amt("bris")
            amt_dta = get_amt("dta")
            amt_ar = get_amt("ar")
            amt_ipt = get_amt("ipt")
            
            total_brut = amt_rc + amt_dr + amt_vol + amt_vb + amt_in + amt_bris + amt_dta + amt_ar + amt_ipt
            
            partie_A = (amt_rc + amt_dr) * 0.10
            partie_B = (amt_vol + amt_vb + amt_in + amt_bris + amt_dta) * 0.50
            
            total_reduction = partie_A + partie_B
            total_net = total_brut - total_reduction
            
            self.prime_brute.setText(f"{total_brut:,.0f}".replace(",", " "))
            self.reduction.setText(f"{total_reduction:,.0f}".replace(",", " "))
            self.prime_nette.setText(f"{total_net:,.0f}".replace(",", " "))
            self.prime_emise.setText(f"{total_net:.0f}")
            
        except Exception as e:
            print(f"Erreur dans le récapitulatif financier : {e}")

    def refresh_all_garanties(self):
        """Rafraîchit toutes les garanties"""
        for key in self.result_labels.keys():
            checkbox = getattr(self, f"check_{key}")
            if checkbox.isChecked():
                self.update_garantie_price(key, 2)

    def update_garantie_price(self, key, state):
        """Met à jour le prix d'une garantie avec audit et matrice de tarifs"""
        label = self.result_labels.get(key)
        if not label: return

        if state:
            try:
                # 1. Calcul du prorata (Période)
                d_debut = self.date_debut.date().toPython()
                d_fin = self.date_fin.date().toPython()
                nbr_jr = max(0, (d_fin - d_debut).days)
                prorata = nbr_jr / 365.0 if nbr_jr > 0 else 0
                
                # 2. Récupération des valeurs numériques
                def get_val(line_edit):
                    txt = line_edit.text().replace(" ", "").replace(",", ".")
                    return float(txt) if txt and txt != "." else 0.0
                
                v_venale = get_val(self.val_venale)
                v_neuf = get_val(self.val_neuf)
                
                try:
                    places = int(self.places_input.text()) if self.places_input.text() else 1
                except: places = 1
                
                montant = 0.0

                # 3. LOGIQUE DE CALCUL PAR GARANTIE
                if key == "rc":
                    # UTILISATION DE LA MATRICE (TABLE AUTOMOBILE_TARIFS)
                    if self.selected_cie_id:
                        zone = self.combo_zone.currentText()
                        cat = self.combo_cat.text() # On prend les 2 premiers chiffres
                        energie = self.energie_combo.currentText()
                        cv = int(self.usage_input.text()) if self.usage_input.text().isdigit() else 0
                        remorque = self.check_remorque.isChecked()

                        # Appel au contrôleur pour le tarif annuel
                        base_rc = self.controller.vehicles.get_rc_premium_from_matrix(
                            self.selected_cie_id, zone, cat, energie, cv, remorque
                        )
                        montant = base_rc * prorata
                    else:
                        montant = 0.0

                elif key == "vol":
                    montant = v_venale * 0.02 * prorata # 2% de la valeur vénale
                elif key == "vb":
                    montant = v_venale * 0.02 * prorata
                elif key == "in":
                    montant = v_venale * 0.0025 * prorata # 0.25%
                elif key == "bris":
                    montant = v_neuf * 0.005 * prorata    # 0.5% de la valeur à neuf
                elif key == "ar":
                    montant = v_venale * 0.03 * prorata
                elif key == "dta":
                    montant = v_neuf * 0.05 * prorata
                elif key == "ipt":
                    # Exemple de calcul fixe par place
                    montant = (5000 * places) * prorata
                
                # 4. Affichage formaté
                label.setText(f"{round(montant):,.0f} FCFA".replace(",", " "))
                label.setVisible(True)
                label.setStyleSheet("color: #27ae60; font-weight: bold;") # Vert si actif
                
            except Exception as e:
                print(f"❌ Erreur calcul {key}: {e}")
                label.setText("0 FCFA")
        else:
            label.setText("0 FCFA")
            label.setVisible(False)
            label.setStyleSheet("color: #95a5a6;") # Gris si inactif
        
        # Recalcul du total général
        self.calculate_total_premium()

    def handle_garantie_click(self, key, state):
        """Gère l'affichage et le calcul lors du clic sur une garantie."""
        is_checked = (state == Qt.Checked or state == 2)
        res_label = self.result_labels.get(key)

        if is_checked:
            res_label.setVisible(True)
            if key == "rc":
                # Déclenche le calcul immédiat de la RC
                self.update_rc_calculation()
        else:
            res_label.setVisible(False)
            res_label.setText("0 FCFA")