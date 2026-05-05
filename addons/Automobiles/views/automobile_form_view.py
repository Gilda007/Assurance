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

# from main import AppColors

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

        self.preselected_owner_id = data.get('owner_id') if data else None
        
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
        
                # === SECTION 1: COMPAGNIE D'ASSURANCE ===
        group_compagny = QGroupBox("🏢 Compagnie d'assurance")
        group_compagny.setStyleSheet(group_style)
        compagny_layout = QVBoxLayout(group_compagny)
        compagny_layout.setSpacing(15)
        compagny_layout.setContentsMargins(25, 25, 25, 25)

        # Barre de recherche compagnie
        self.search_compagny = QLineEdit()
        self.search_compagny.setPlaceholderText("🔍 Rechercher une compagnie d'assurance...")
        self.search_compagny.setStyleSheet(field_style)
        self.search_compagny.textChanged.connect(self.filter_compagnies)
        compagny_layout.addWidget(self.search_compagny)

        # Splitter pour compagnie
        compagny_splitter = QSplitter(Qt.Horizontal)
        compagny_splitter.setStyleSheet("QSplitter::handle { background: #e2e8f0; width: 2px; margin: 10px 0; }")

        # Liste des compagnies
        self.compagny_list = QListWidget()
        self.compagny_list.setStyleSheet("""
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
        self.compagny_list.currentRowChanged.connect(self.display_compagny_details)
        compagny_splitter.addWidget(self.compagny_list)

        # Carte de la compagnie sélectionnée
        self.compagny_card = QFrame()
        self.compagny_card.setObjectName("CompagnyCard")
        self.compagny_card.setStyleSheet("""
            QFrame#CompagnyCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fef9e7, stop:1 #f0f9ff);
                border-radius: 16px;
                border: 2px solid #e2e8f0;
            }
        """)
        compagny_card_layout = QHBoxLayout(self.compagny_card)
        compagny_card_layout.setContentsMargins(20, 20, 20, 20)
        compagny_card_layout.setSpacing(15)

        # Logo/Photo compagnie
        self.compagny_photo = QLabel()
        self.compagny_photo.setObjectName("CompagnyPhoto")
        self.compagny_photo.setFixedSize(80, 80)
        self.compagny_photo.setStyleSheet("""
            QLabel {
                background: white;
                border-radius: 40px;
                border: 3px solid #e2e8f0;
            }
        """)
        self.compagny_photo.setAlignment(Qt.AlignCenter)
        self.compagny_photo.setText("🏢")
        self.compagny_photo.setStyleSheet("font-size: 32px;")
        compagny_card_layout.addWidget(self.compagny_photo)

        # Détails compagnie
        compagny_details = QWidget()
        compagny_details_layout = QVBoxLayout(compagny_details)
        compagny_details_layout.setSpacing(8)

        self.lbl_compagny_name = QLabel("Aucune compagnie sélectionnée")
        self.lbl_compagny_name.setStyleSheet("font-size: 16px; font-weight: 800; color: #2c3e50;")

        self.lbl_compagny_info = QLabel("Sélectionnez une compagnie d'assurance dans la liste")
        self.lbl_compagny_info.setStyleSheet("font-size: 12px; color: #718096; line-height: 1.5;")
        self.lbl_compagny_info.setWordWrap(True)

        compagny_details_layout.addWidget(self.lbl_compagny_name)
        compagny_details_layout.addWidget(self.lbl_compagny_info)
        compagny_details_layout.addStretch()

        compagny_card_layout.addWidget(compagny_details, 1)
        compagny_splitter.addWidget(self.compagny_card)
        compagny_splitter.setSizes([350, 450])

        compagny_layout.addWidget(compagny_splitter)
        form_layout.addWidget(group_compagny)

        # === SECTION 2: PROPRIÉTAIRE DU VÉHICULE ===
        group_owner = QGroupBox("👤 Propriétaire du véhicule")
        group_owner.setStyleSheet(group_style)
        owner_layout = QVBoxLayout(group_owner)
        owner_layout.setSpacing(15)
        owner_layout.setContentsMargins(25, 25, 25, 25)

        # Barre de recherche propriétaire
        self.search_owner = QLineEdit()
        self.search_owner.setPlaceholderText("🔍 Rechercher un propriétaire (nom, téléphone, CNI)...")
        self.search_owner.setStyleSheet(field_style)
        self.search_owner.textChanged.connect(self.filter_owners)
        owner_layout.addWidget(self.search_owner)

        # Splitter pour propriétaire
        owner_splitter = QSplitter(Qt.Horizontal)
        owner_splitter.setStyleSheet("QSplitter::handle { background: #e2e8f0; width: 2px; margin: 10px 0; }")

        # Liste des propriétaires
        self.owner_list = QListWidget()
        self.owner_list.setStyleSheet("""
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
        self.owner_list.currentRowChanged.connect(self.display_owner_details)
        owner_splitter.addWidget(self.owner_list)

        # Carte du propriétaire sélectionné
        self.owner_card = QFrame()
        self.owner_card.setObjectName("OwnerCard")
        self.owner_card.setStyleSheet("""
            QFrame#OwnerCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fef9e7, stop:1 #f0f9ff);
                border-radius: 16px;
                border: 2px solid #e2e8f0;
            }
        """)
        owner_card_layout = QHBoxLayout(self.owner_card)
        owner_card_layout.setContentsMargins(20, 20, 20, 20)
        owner_card_layout.setSpacing(15)

        # Photo/avatar propriétaire
        self.owner_photo = QLabel()
        self.owner_photo.setObjectName("OwnerPhoto")
        self.owner_photo.setFixedSize(80, 80)
        self.owner_photo.setStyleSheet("""
            QLabel {
                background: white;
                border-radius: 40px;
                border: 3px solid #e2e8f0;
            }
        """)
        self.owner_photo.setAlignment(Qt.AlignCenter)
        self.owner_photo.setText("👤")
        self.owner_photo.setStyleSheet("font-size: 32px;")
        owner_card_layout.addWidget(self.owner_photo)

        # Détails propriétaire
        owner_details_widget = QWidget()
        owner_details_layout = QVBoxLayout(owner_details_widget)
        owner_details_layout.setSpacing(8)

        self.lbl_owner_name = QLabel("Aucun propriétaire sélectionné")
        self.lbl_owner_name.setStyleSheet("font-size: 16px; font-weight: 800; color: #2c3e50;")

        self.lbl_owner_info = QLabel("Sélectionnez le propriétaire du véhicule dans la liste")
        self.lbl_owner_info.setStyleSheet("font-size: 12px; color: #718096; line-height: 1.5;")
        self.lbl_owner_info.setWordWrap(True)

        owner_details_layout.addWidget(self.lbl_owner_name)
        owner_details_layout.addWidget(self.lbl_owner_info)
        owner_details_layout.addStretch()

        owner_card_layout.addWidget(owner_details_widget, 1)
        owner_splitter.addWidget(self.owner_card)
        owner_splitter.setSizes([350, 450])

        owner_layout.addWidget(owner_splitter)
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
        id_layout.addWidget(self.create_label_with_icon("🏷️", "Code du Tarif"), 6, 1)
        
        self.combo_zone = QComboBox()
        self.combo_zone.addItems(["A", "B", "C"])
        self.combo_zone.setStyleSheet(field_style)
        id_layout.addWidget(self.combo_zone, 7, 0)
        
        self.code_tarif = QComboBox()
        self.code_tarif.setStyleSheet(field_style)
        self.code_tarif.setPlaceholderText("Code ministériel du tarif...")
        self.code_tarif.setEditable(False)
        self.code_tarif.currentTextChanged.connect(self.on_code_tarif_changed)
        id_layout.addWidget(self.code_tarif, 7, 1)
        
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
        id_layout.addWidget(self.create_label_with_icon("📊", "Catégorie"), 8, 2, 1, 2)

        self.combo_fleet = QComboBox()
        self.combo_fleet.setStyleSheet(field_style)
        self.combo_fleet.setEditable(True)
        self.combo_fleet.setPlaceholderText("Ex: Tarif Standard, Tarif Premium, ...")
        id_layout.addWidget(self.combo_fleet, 9, 0, 1, 2)

        self.combo_cat = QComboBox()
        self.combo_cat.setStyleSheet(field_style)
        self.combo_cat.setPlaceholderText("Ex: remplissage automatique...")
        id_layout.addWidget(self.combo_cat, 9, 2, 1, 2)

        
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
        values_layout.addWidget(self.create_label_with_icon("📅", "Nombre de Jours"), 2, 2)
        
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

        self.nbr_jour = QLineEdit()
        self.nbr_jour.setStyleSheet(field_style)
        self.nbr_jour.setPlaceholderText("0")
        self.nbr_jour.textChanged.connect(self.refresh_all_garanties)
        values_layout.addWidget(self.nbr_jour, 3, 2)
        
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
            ("dta", "Dommages", "💥 DT Risque"),
            ("ipt", "Indiv. Personnes Transportées", "👥 IPT")
        ]

        for i, (key, label_text, short_label) in enumerate(garanties):
            # Checkbox
            checkbox = QCheckBox(label_text)
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
            
            # Label du montant brut
            montant_brut_label = QLabel("0 FCFA")
            montant_brut_label.setStyleSheet("""
                font-weight: bold;
                color: #27ae60;
                font-size: 13px;
                background: #e8f5e9;
                padding: 6px 12px;
                border-radius: 8px;
            """)
            montant_brut_label.setVisible(False)
            
            # Champ taux de réduction
            taux_input = QLineEdit()
            taux_input.setPlaceholderText("Taux %")
            taux_input.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 6px 10px;
                    font-size: 12px;
                    max-width: 80px;
                }
                QLineEdit:focus {
                    border-color: #3498db;
                }
            """)
            taux_input.setVisible(False)

            montant_taux = QLabel("0 FCFA")
            montant_taux.setStyleSheet(style_nette)
            montant_taux.setVisible(False)
            
            # Label du montant net (après réduction)
            montant_net_label = QLabel("0 FCFA")
            montant_net_label.setStyleSheet("""
                font-weight: bold;
                color: #e67e22;
                font-size: 13px;
                background: #fff3e0;
                padding: 6px 12px;
                border-radius: 8px;
            """)
            montant_net_label.setVisible(False)
            
            # Stocker dans le dictionnaire
            self.result_labels[key] = {
                'montant_brut': montant_brut_label,
                'taux': taux_input,
                'montant_taux': montant_taux,
                'montant_net': montant_net_label
            }
            
            # Ajout au grid - CORRECTION ICI !
            garanties_layout.addWidget(checkbox, i, 0)
            garanties_layout.addWidget(QLabel(short_label), i, 1)
            garanties_layout.addWidget(montant_brut_label, i, 2)  # Utilisez la variable
            garanties_layout.addWidget(taux_input, i, 3)          # Utilisez la variable
            garanties_layout.addWidget(montant_taux, i, 4)  
            garanties_layout.addWidget(montant_net_label, i, 5)   # Utilisez la variable, PAS QLabel()
            
            # Connexion des signaux
            checkbox.stateChanged.connect(lambda state, k=key: self.update_garantie_price(k, state))

        form_layout.addWidget(group_garanties)
        
        # === SECTION 5: RÉCAPITULATIF FINANCIER ===
        group_recap = QGroupBox("🧮 RÉCAPITULATIF FINANCIER")
        group_recap.setStyleSheet(group_style)
        recap_layout = QGridLayout(group_recap)
        recap_layout.setSpacing(15)
        recap_layout.setContentsMargins(25, 25, 25, 25)

        # Styles
        style_primary = """
            QLineEdit {
                background-color: #eff6ff;
                color: #1e40af;
                font-weight: bold;
                border: 2px solid #bfdbfe;
                border-radius: 12px;
                padding: 12px;
                font-size: 14px;
            }
        """

        style_success = """
            QLineEdit {
                background-color: #f0fdf4;
                color: #166534;
                font-weight: bold;
                border: 2px solid #bbf7d0;
                border-radius: 12px;
                padding: 12px;
                font-size: 16px;
            }
        """

        style_warning = """
            QLineEdit {
                background-color: #fffbeb;
                color: #b45309;
                font-weight: bold;
                border: 2px solid #fde68a;
                border-radius: 12px;
                padding: 12px;
                font-size: 14px;
            }
        """

        style_info = """
            QLineEdit {
                background-color: #f8fafc;
                color: #334155;
                font-weight: 500;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 12px;
                font-size: 13px;
            }
        """

        # Titre de section
        title_lbl = QLabel("💰 DÉTAIL DES MONTANTS")
        title_lbl.setStyleSheet("""
            font-size: 14px;
            font-weight: 700;
            color: #1e293b;
            padding: 5px 10px;
            background: #f1f5f9;
            border-radius: 8px;
        """)
        recap_layout.addWidget(title_lbl, 0, 0, 1, 3)

        # Ligne 1 - Montants principaux
        self.prime_brute = QLineEdit("0")
        self.prime_brute.setReadOnly(True)
        self.prime_brute.setStyleSheet(style_info)
        self.prime_brute.setAlignment(Qt.AlignRight)
        recap_layout.addWidget(self.create_labeled_field("Montant Brut", self.prime_brute), 1, 0)

        self.prime_nette = QLineEdit("0")
        self.prime_nette.setReadOnly(True)
        self.prime_nette.setStyleSheet(style_success)
        self.prime_nette.setAlignment(Qt.AlignRight)
        recap_layout.addWidget(self.create_labeled_field("Prime Nette", self.prime_nette), 1, 2)

        self.reduction = QLineEdit("0")
        self.reduction.setReadOnly(True)
        self.reduction.setStyleSheet(style_warning)
        self.reduction.setAlignment(Qt.AlignRight)
        recap_layout.addWidget(self.create_labeled_field("Réduction", self.reduction), 1, 1)

        # Ligne 2 - Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: #e2e8f0; margin: 10px 0;")
        recap_layout.addWidget(sep, 2, 0, 1, 3)

        # Ligne 3 - Taxes et frais
        self.carte_rose = QLineEdit("0")
        self.carte_rose.setStyleSheet(style_info)
        self.carte_rose.setAlignment(Qt.AlignRight)
        self.carte_rose.textChanged.connect(self.calculate_pttc)
        recap_layout.addWidget(self.create_labeled_field("Carte Rose", self.carte_rose),  5, 1)

        self.accessoire = QLineEdit("0")
        self.accessoire.setReadOnly(False)
        self.accessoire.setStyleSheet(style_info)
        self.accessoire.setAlignment(Qt.AlignRight)
        self.accessoire.textChanged.connect(self.calculate_tva)
        self.accessoire.textChanged.connect(self.calculate_pttc)
        recap_layout.addWidget(self.create_labeled_field("Accessoires", self.accessoire), 3, 1)

        self.tva = QLineEdit("0")
        self.tva.setReadOnly(True)
        self.tva.setStyleSheet(style_info)
        self.tva.setAlignment(Qt.AlignRight)
        recap_layout.addWidget(self.create_labeled_field("TVA (19.25%)", self.tva), 3, 2)

        # Ligne 4 - Séparateur
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("background: #e2e8f0; margin: 10px 0;")
        recap_layout.addWidget(sep2, 4, 0, 1, 3)

        # Ligne 5 - Autres frais
        self.asac = QLineEdit("0")
        self.asac.setReadOnly(False)
        self.asac.setStyleSheet(style_info)
        self.asac.setAlignment(Qt.AlignRight)
        self.asac.textChanged.connect(self.calculate_tva)
        self.asac.textChanged.connect(self.calculate_pttc)
        recap_layout.addWidget(self.create_labeled_field("Fichier ASAC", self.asac), 3, 0)

        self.vignette = QLineEdit("0")
        self.vignette.setStyleSheet(style_info)
        self.vignette.setAlignment(Qt.AlignRight)
        self.vignette.textChanged.connect(self.calculate_pttc)
        recap_layout.addWidget(self.create_labeled_field("Vignette", self.vignette), 5, 0)

        self.pttc = QLineEdit("0")
        self.pttc.setReadOnly(True)
        self.pttc.setStyleSheet(style_primary)
        self.pttc.setAlignment(Qt.AlignRight)
        recap_layout.addWidget(self.create_labeled_field("PTTC", self.pttc), 5, 2)

        # Champ caché
        self.prime_emise = QLineEdit()
        self.prime_emise.setReadOnly(True)
        self.prime_emise.setVisible(False)

        form_layout.addWidget(group_recap)
        
        # --- PROGRESS BAR ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 6px;
                background-color: #f1f5f9;
                height: 8px;
                text-align: center;
                font-size: 10px;
                font-weight: 500;
                color: #1e293b;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #2563eb);
                border-radius: 6px;
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

    def create_labeled_field(self, label_text, field_widget):
        """Crée un widget contenant un label et un champ"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        label = QLabel(label_text)
        label.setStyleSheet("""
            font-size: 11px;
            font-weight: 600;
            color: #64748b;
            letter-spacing: 0.3px;
        """)
        
        layout.addWidget(label)
        layout.addWidget(field_widget)
        
        return container

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

    def fill_form(self, data):
        """Pré-remplit le formulaire avec les données fournies"""
        if not data:
            return
        
        # Pré-remplir le propriétaire si les données sont fournies
        owner_id = data.get('owner_id')
        print(f"Pré-remplissage du formulaire avec owner_id: {owner_id}")
        if owner_id:
            self.preselected_owner_id = owner_id
            # Récupérer et afficher les informations du propriétaire
            self.load_owner_details_by_id(owner_id)

    def load_owner_details_by_id(self, owner_id):
        """Charge et affiche les détails du propriétaire par son ID"""
        try:
            # Récupérer le contact depuis le contrôleur
            contact = self.controller.contacts.get_contact_by_id(owner_id)
            
            if not contact:
                print(f"⚠️ Propriétaire avec ID {owner_id} non trouvé")
                return
            
            # Stocker l'ID sélectionné
            self.selected_owner_id = owner_id
            
            # Mettre à jour l'affichage des détails
            owner_name = f"{contact.nom} {contact.prenom or ''}".upper()
            self.lbl_owner_name.setText(owner_name)
            
            info_text = f"""
                📌 Type: {contact.nature or 'Particulier'}
                📞 Tél: {contact.telephone or 'N/A'}
                📧 Email: {contact.email or 'N/A'}
                🆔 Code client: {contact.id or 'N/A'}
                📍 Charge Clientèle: {contact.charge_clientele or 'N/A'}
            """
            self.lbl_owner_info.setText(info_text)
            
            # Mettre à jour l'avatar/photo
            if hasattr(contact, 'photo') and contact.photo:
                pixmap = QPixmap()
                pixmap.loadFromData(contact.photo)
                self.owner_photo.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                initials = f"{contact.nom[0]}{contact.prenom[0] if contact.prenom else ''}".upper()
                self.owner_photo.setText(initials)
                self.owner_photo.setStyleSheet("""
                    QLabel {
                        background: #3498db;
                        color: white;
                        font-size: 28px;
                        font-weight: bold;
                        border-radius: 40px;
                        border: 3px solid #e2e8f0;
                    }
                """)
            
            # Ajouter le contact à la liste s'il n'y est pas déjà
            self._add_contact_to_list(contact)
            
        except Exception as e:
            print(f"Erreur lors du chargement du propriétaire: {e}")

    def _add_contact_to_list(self, contact):
        """Ajoute un contact à la liste et le sélectionne"""
        # Vérifier si le contact est déjà dans la liste
        for i in range(self.owner_list.count()):
            item = self.owner_list.item(i)
            if item and item.data(Qt.UserRole) and item.data(Qt.UserRole).id == contact.id:
                # Déjà présent, le sélectionner
                self.owner_list.setCurrentItem(item)
                self.display_owner_details(i)
                return
        
        # Ajouter le contact à la liste
        name_display = f"{contact.nom} {contact.prenom or ''} - {contact.telephone or ''}"
        self.owner_list.addItem(name_display)
        item = self.owner_list.item(self.owner_list.count() - 1)
        item.setData(Qt.UserRole, contact)
        self.owner_list.setCurrentItem(item)
        self.display_owner_details(self.owner_list.count() - 1)

    # ... (toutes les autres méthodes existantes restent identiques)
    def filter_clients(self, text):
        """Filtre les clients selon la recherche"""
        self.owner_list.clear()
        if len(text) < 2:
            return
        
        clients = self.controller.contacts.get_contacts_for_combo(text)
        
        for client in clients:
            if isinstance(client, tuple):
                name_display = f"{client[0]} {client[1] if len(client) > 1 else ''}"
            else:
                name_display = f"{client.nom} {client.code or ''}"
                
            item = QListWidgetItem(name_display)
            item.setData(Qt.UserRole, client)
            self.owner_list.addItem(item)

    def filter_compagnies(self, text):
        """Filtre les compagnies selon la recherche"""
        self.compagny_list.clear()
        if len(text) < 2:
            return
        
        compagnies = self.controller.compagnies.get_contacts_for_combo(text)
        
        for compagny in compagnies:
            name_display = f"{compagny.nom} - {compagny.code or ''}"
            item = QListWidgetItem(name_display)
            item.setData(Qt.UserRole, compagny)
            self.compagny_list.addItem(item)

    def display_compagny_details(self, row):
        """Affiche les détails de la compagnie sélectionnée"""
        if row < 0:
            return
        
        item = self.compagny_list.currentItem()
        if not item:
            return
        
        compagny = item.data(Qt.UserRole)
        self.selected_cie_id = compagny.id
        
        # Mettre à jour l'affichage
        self.lbl_compagny_name.setText(compagny.nom.upper())
        
        info_text = f"""
            📌 Code: {compagny.code or 'N/A'}
            📞 Tél: {compagny.telephone or 'N/A'}
            📧 Email: {compagny.email or 'N/A'}
            📍 Adresse: {compagny.adresse or 'N/A'}
        """
        self.lbl_compagny_info.setText(info_text)
        
        # Charger les logos si disponibles
        if hasattr(compagny, 'logo') and compagny.logo:
            pixmap = QPixmap()
            pixmap.loadFromData(compagny.logo)
            self.compagny_photo.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.compagny_photo.setText("🏢")
            self.compagny_photo.setStyleSheet("font-size: 32px;")
        
        self.load_tarif_codes()

    def filter_owners(self, text):
        """Filtre les propriétaires selon la recherche"""
        self.owner_list.clear()
        if len(text) < 2:
            return
        
        owners = self.controller.contacts.search_contacts(text)
        
        for owner in owners:
            name_display = f"{owner.nom} {owner.prenom or ''} - {owner.telephone or ''}"
            item = QListWidgetItem(name_display)
            item.setData(Qt.UserRole, owner)
            self.owner_list.addItem(item)

    def display_owner_details(self, row):
        """Affiche les détails du propriétaire sélectionné"""
        if row < 0:
            return
        
        item = self.owner_list.currentItem()
        if not item:
            return
        
        owner = item.data(Qt.UserRole)
        self.selected_owner_id = owner.id
        
        # Mettre à jour l'affichage
        owner_name = f"{owner.nom} {owner.prenom or ''}".upper()
        self.lbl_owner_name.setText(owner_name)
        
        info_text = f"""
            📌 Type: {owner.nature or 'Particulier'}
            📞 Tél: {owner.telephone or 'N/A'}
            📧 Email: {owner.email or 'N/A'}
            🆔 Code client: {owner.id or 'N/A'}
            📍 Charge Clientèle: {owner.charge_clientele or 'N/A'}
        """
        self.lbl_owner_info.setText(info_text)
        
        # Photo/avatar
        if hasattr(owner, 'photo') and owner.photo:
            pixmap = QPixmap()
            pixmap.loadFromData(owner.photo)
            self.owner_photo.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # Initiales
            initials = f"{owner.nom[0]}{owner.prenom[0] if owner.prenom else ''}".upper()
            self.owner_photo.setText(initials)
            self.owner_photo.setStyleSheet("""
                QLabel {
                    background: #3498db;
                    color: white;
                    font-size: 28px;
                    font-weight: bold;
                    border-radius: 40px;
                    border: 3px solid #e2e8f0;
                }
            """)

    def display_client(self, row):
        """Affiche les détails du client sélectionné"""
        if row < 0:
            return
        
        item = self.owner_list.currentItem()
        if not item:
            return
        client = item.data(Qt.UserRole)
        
        self.selected_cie_id = client.id
        
        name_html = (
            f"<div style='color: #2c3e50; font-size: 16px; font-weight: bold;'>"
            f"{client.nom.upper()}</div>"
            f"<div style='color: #7f8c8d; font-size: 11px;'>ID: {client.id or 'N/A'}</div>"
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
        self.load_tarif_codes()

    def load_existing_data(self, v):
        """Charge les données d'un véhicule existant"""
        try:
            # --- TEXTE DE BASE ---
            text_fields = [
                ('immatriculation', self.immat_input),
                ('chassis', self.chassis_input),
                ('marque', self.marque_input),
                ('modele', self.modele_input),
                ('usage', self.usage_input),
            ]
            for attr, widget in text_fields:
                val = getattr(v, attr, "")
                widget.setText(str(val) if val else "")

            # --- CHAMPS NUMÉRIQUES ---
            if hasattr(v, 'annee') and v.annee:
                self.annee_input.setText(str(v.annee))
            
            if hasattr(v, 'places') and v.places:
                self.places_input.setText(str(v.places))
            
            # --- VALEURS FINANCIÈRES ---
            self.val_neuf.setText(str(getattr(v, 'valeur_neuf', 0) or 0))
            self.val_venale.setText(str(getattr(v, 'valeur_venale', 0) or 0))
            
            # --- COMBOBOX (Énergie, Statut, Zone) ---
            if hasattr(v, 'energie') and v.energie:
                index = self.energie_combo.findText(v.energie, Qt.MatchFlag.MatchExactly)
                if index >= 0:
                    self.energie_combo.setCurrentIndex(index)
            
            if hasattr(v, 'statut') and v.statut:
                index = self.status_combo.findText(v.statut, Qt.MatchFlag.MatchExactly)
                if index >= 0:
                    self.status_combo.setCurrentIndex(index)
            
            if hasattr(v, 'zone') and v.zone:
                index = self.combo_zone.findText(v.zone, Qt.MatchFlag.MatchExactly)
                if index >= 0:
                    self.combo_zone.setCurrentIndex(index)
            
            # --- DATES ---
            if hasattr(v, 'date_debut') and v.date_debut:
                d = v.date_debut
                q_date = QDate(d.year, d.month, d.day)
                self.date_debut.setDate(q_date)
            
            if hasattr(v, 'date_fin') and v.date_fin:
                d = v.date_fin
                q_date = QDate(d.year, d.month, d.day)
                self.date_fin.setDate(q_date)
            
            # --- CHECKBOXES DES GARANTIES ---
            garanties_keys = ["rc", "dr", "vol", "vb", "in", "bris", "ar", "dta", "ipt"]
            # --- AFFICHAGE DES MONTANTS DES GARANTIES DEPUIS LA BASE ---
            for key in garanties_keys:
                amt_field = f"amt_{key}"
                garantie_data = self.result_labels.get(key)  # C'est maintenant un dictionnaire
                
                if garantie_data and hasattr(v, amt_field) and getattr(v, amt_field):
                    montant = float(getattr(v, amt_field))
                    montant_brut_label = garantie_data['montant_brut']  # Récupérer le label brut
                    montant_brut_label.setText(f"{montant:,.0f} FCFA".replace(",", " "))
                    montant_brut_label.setVisible(True)
                    
                    # Appliquer le style adapté
                    if montant > 0:
                        montant_brut_label.setStyleSheet("""
                            color: #27ae60;
                            font-weight: bold;
                            background-color: #e8f5e9;
                            padding: 4px 8px;
                            border-radius: 6px;
                        """)
                    else:
                        montant_brut_label.setStyleSheet("""
                            color: #95a5a6;
                            font-weight: normal;
                            background-color: #f8f9fa;
                            padding: 4px 8px;
                            border-radius: 6px;
                        """)
                elif garantie_data:
                    # Si la garantie n'est pas cochée, on cache le label
                    checkbox = getattr(self, f"check_{key}", None)
                    if checkbox and not checkbox.isChecked():
                        montant_brut_label = garantie_data['montant_brut']
                        montant_brut_label.setVisible(False)
                        montant_brut_label.setText("0 FCFA")
            
            # --- CHECKBOX REMORQUE ---
            if hasattr(v, 'has_remorque'):
                self.check_remorque.setChecked(bool(v.has_remorque))
            
            # --- CHAMPS CATÉGORIE ET LIBELLÉ TARIF ---
            if hasattr(v, 'categorie') and v.categorie:
                self.combo_cat.setCurrentText(str(v.categorie))
            
            # --- GESTION DU PROPRIÉTAIRE (COMPAGNIE) ---
            if hasattr(v, 'owner_id') and v.owner_id:
                # Sauvegarder l'ID de la compagnie sélectionnée
                self.selected_cie_id = v.owner_id
                
                # Parcourir la liste des clients pour sélectionner le bon
                for i in range(self.compagny_list.count()):
                    item = self.compagny_list.item(i)
                    if item and item.data(Qt.UserRole) and item.data(Qt.UserRole).id == v.owner_id:
                        self.compagny_list.setCurrentItem(item)
                        self.display_compagny_details(i)
                        break
                
                # CHARGER LES CODES TARIF APRÈS AVOIR SÉLECTIONNÉ LA COMPAGNIE
                self.load_tarif_codes()
                
                # --- CODE TARIF (ComboBox) ---
                if hasattr(v, 'code_tarif') and v.code_tarif:
                    code_to_find = str(v.code_tarif).strip()
                    index = self.code_tarif.findText(code_to_find)
                    if index >= 0:
                        self.code_tarif.setCurrentIndex(index)
                    else:
                        # Si le code n'existe pas dans la liste, on l'ajoute temporairement
                        self.code_tarif.addItem(code_to_find, {"code": code_to_find, "libelle": ""})
                        index = self.code_tarif.findText(code_to_find)
                        if index >= 0:
                            self.code_tarif.setCurrentIndex(index)
                
                # --- LIBELLÉ TARIF (ComboBox) ---
                if hasattr(v, 'libele_tarif') and v.libele_tarif:
                    libelle_to_find = str(v.libele_tarif).strip()
                    index = self.combo_fleet.findText(libelle_to_find)
                    if index >= 0:
                        self.combo_fleet.setCurrentIndex(index)
                    else:
                        # Si le libellé n'existe pas dans la liste, on l'ajoute temporairement
                        self.combo_fleet.addItem(libelle_to_find, {"code": "", "libelle": libelle_to_find})
                        index = self.combo_fleet.findText(libelle_to_find)
                        if index >= 0:
                            self.combo_fleet.setCurrentIndex(index)
            
            # --- AFFICHAGE DES MONTANTS DES GARANTIES DEPUIS LA BASE ---
            for key in garanties_keys:
                amt_field = f"amt_{key}"
                label = self.result_labels.get(key)
                
                if label and hasattr(v, amt_field) and getattr(v, amt_field):
                    montant = float(getattr(v, amt_field))
                    label.setText(f"{montant:,.0f} FCFA".replace(",", " "))
                    label.setVisible(True)
                    
                    # Appliquer le style adapté
                    if montant > 0:
                        label.setStyleSheet("""
                            color: #27ae60;
                            font-weight: bold;
                            background-color: #e8f5e9;
                            padding: 4px 8px;
                            border-radius: 6px;
                        """)
                    else:
                        label.setStyleSheet("""
                            color: #95a5a6;
                            font-weight: normal;
                            background-color: #f8f9fa;
                            padding: 4px 8px;
                            border-radius: 6px;
                        """)
                elif label:
                    # Si la garantie n'est pas cochée, on cache le label
                    checkbox = getattr(self, f"check_{key}", None)
                    if checkbox and not checkbox.isChecked():
                        label.setVisible(False)
                        label.setText("0 FCFA")
            
            # --- AFFICHAGE DES PRIMES DEPUIS LA BASE ---
            try:
                # Prime brute
                if hasattr(v, 'prime_brute') and v.prime_brute:
                    self.prime_brute.setText(f"{float(v.prime_brute):,.0f}".replace(",", " "))
                
                # Réduction
                if hasattr(v, 'reduction') and v.reduction:
                    self.reduction.setText(f"{float(v.reduction):,.0f}".replace(",", " "))
                
                # Prime nette
                if hasattr(v, 'prime_nette') and v.prime_nette:
                    self.prime_nette.setText(f"{float(v.prime_nette):,.0f}".replace(",", " "))
                    self.reduction.setText(f"{float(v.prime_nette):.0f}")
                    
            except Exception as e:
                print(f"Erreur lors du chargement des primes : {e}")
            
            # --- MISE À JOUR DES LABELS VISIBLES ---
            # S'assurer que seules les garanties cochées sont visibles
            for key in garanties_keys:
                checkbox = getattr(self, f"check_{key}", None)
                garantie_data = self.result_labels.get(key)
                if checkbox and garantie_data:
                    is_checked = checkbox.isChecked()
                    garantie_data['montant_brut'].setVisible(is_checked)
                    garantie_data['taux'].setVisible(is_checked)
                    garantie_data['montant_taux'].setVisible(is_checked)
                    garantie_data['montant_net'].setVisible(is_checked)
            
            # --- NE PAS RECALCULER AUTOMATIQUEMENT ---
            # On affiche simplement les données existantes sans déclencher de recalcul
            
        except Exception as e:
            print(f"Erreur lors du chargement des données du véhicule : {str(e)}")
            import traceback
            traceback.print_exc()
    
    def get_form_data(self):
        """Récupère les données du formulaire"""
        def clean_amt(key):
            garantie_data = self.result_labels.get(key)
            if garantie_data:
                montant_net_label = garantie_data['montant_net']
                if montant_net_label and montant_net_label.isVisible():
                    txt = montant_net_label.text().replace(" FCFA", "").replace(" ", "").replace(",", ".")
                    return float(txt) if txt else 0.0
            return 0.0
        
        def get_brut_amt(key):
            garantie_data = self.result_labels.get(key)
            if garantie_data:
                montant_brut_label = garantie_data['montant_brut']
                if montant_brut_label and montant_brut_label.isVisible():
                    txt = montant_brut_label.text().replace(" FCFA", "").replace(" ", "").replace(",", ".")
                    return float(txt) if txt else 0.0
            return 0.0
        
        def get_fleet_amt(key):
            garantie_data = self.result_labels.get(key)
            if garantie_data:
                montant_brut_label = garantie_data['montant_net']
                if montant_brut_label and montant_brut_label.isVisible():
                    txt = montant_brut_label.text().replace(" FCFA", "").replace(" ", "").replace(",", ".")
                    return float(txt) if txt else 0.0
            return 0.0
        
        def get_red_amt(key):
            garantie_data = self.result_labels.get(key)
            if garantie_data:
                montant_taux_label = garantie_data.get('montant_taux')
                if montant_taux_label and montant_taux_label.isVisible():
                    txt = montant_taux_label.text().replace(" FCFA", "").replace(" ", "").replace(",", ".")
                    return float(txt) if txt else 0.0
            return 0.0
        
        def get_taux(key):
            garantie_data = self.result_labels.get(key)
            if garantie_data:
                taux_widget = garantie_data.get('taux')
                if taux_widget and taux_widget.isVisible():
                    txt = taux_widget.text().strip()
                    if txt.endswith('%'):
                        txt = txt[:-1]
                    try:
                        return float(txt) if txt else 0.0
                    except ValueError:
                        return 0.0
            return 0.0
        
        def clean_input(widget):
            txt = widget.text().replace(" ", "").replace(",", ".")
            return float(txt) if txt else 0.0
    
        # Récupérer les montants bruts
        amt_rc = get_fleet_amt("rc")
        amt_dr = get_fleet_amt("dr")
        amt_vol = get_fleet_amt("vol")
        amt_vb = get_fleet_amt("vb")
        amt_in = get_fleet_amt("in")
        amt_bris = get_fleet_amt("bris")
        amt_ar = get_fleet_amt("ar")
        amt_dta = get_fleet_amt("dta")
        amt_ipt = get_fleet_amt("ipt")

        
        data = {
            # --- IDENTIFICATION & PROPRIÉTAIRE ---
            "immatriculation": self.immat_input.text().strip().upper(),
            "chassis": self.chassis_input.text().strip().upper(),
            "zone": self.combo_zone.currentText(),
            "libele_tarif": self.combo_fleet.currentText().strip().upper(),
            "categorie": self.combo_cat.currentText().strip().upper(),
            "compagny_id": self.compagny_list.currentItem().data(Qt.UserRole).id if self.compagny_list.currentItem() else None,
            "owner_id": self.owner_list.currentItem().data(Qt.UserRole).id if self.owner_list.currentItem() else None,
            "marque": self.marque_input.text().strip(),
            "modele": self.modele_input.text().strip(),
            "annee": int(self.annee_input.text()) if self.annee_input.text().isdigit() else None,
            "energie": self.energie_combo.currentText(),
            "usage": self.usage_input.text().strip(),
            "places": int(self.places_input.text()) if self.places_input.text().isdigit() else 5,
            "has_remorque": self.check_remorque.isChecked(),
            "statut": self.status_combo.currentText(),
            "code_tarif": self.code_tarif.currentText().strip(),

            # --- DATES ---
            "date_debut": self.date_debut.date().toPython(),
            "date_fin": self.date_fin.date().toPython(),
            "nbr_jour": int(self.nbr_jour.text()) if self.nbr_jour.text().isdigit() else 0,

            # --- VALEURS ---
            "valeur_neuf": clean_input(self.val_neuf),
            "valeur_venale": clean_input(self.val_venale),

            # --- RÉCAPITULATIF FINANCIER ---
            "prime_brute": clean_input(self.prime_brute),
            "reduction": clean_input(self.reduction),
            "prime_nette": clean_input(self.prime_nette),
            "prime_emise": clean_input(self.prime_nette),

            # --- FRAIS SUPPLÉMENTAIRES ---
            "carte_rose": clean_input(self.carte_rose),
            "accessoires": clean_input(self.accessoire),
            "tva": clean_input(self.tva),
            "fichier_asac": clean_input(self.asac),
            "vignette": clean_input(self.vignette),
            "pttc": clean_input(self.pttc),

            # --- ÉTAT DES GARANTIES ---
            "check_rc": self.check_rc.isChecked(),
            "check_dr": self.check_dr.isChecked(),
            "check_vol": self.check_vol.isChecked(),
            "check_vb": self.check_vb.isChecked(),
            "check_in": self.check_in.isChecked(),
            "check_bris": self.check_bris.isChecked(),
            "check_ar": self.check_ar.isChecked(),
            "check_dta": self.check_dta.isChecked(),
            "check_ipt": self.check_ipt.isChecked(),

            # --- MONTANTS BRUTS ---
            "amt_rc": get_brut_amt("rc"),
            "amt_dr": get_brut_amt("dr"),
            "amt_vol": get_brut_amt("vol"),
            "amt_vb": get_brut_amt("vb"),
            "amt_in": get_brut_amt("in"),
            "amt_bris": get_brut_amt("bris"),
            "amt_ar": get_brut_amt("ar"),
            "amt_dta": get_brut_amt("dta"),
            "amt_ipt": get_brut_amt("ipt"),

            # --- MONTANTS NETS ---
            "amt_red_rc": clean_amt("rc"),
            "amt_red_dr": clean_amt("dr"),
            "amt_red_vol": clean_amt("vol"),
            "amt_red_vb": clean_amt("vb"),
            "amt_red_in": clean_amt("in"),
            "amt_red_bris": clean_amt("bris"),
            "amt_red_ar": clean_amt("ar"),
            "amt_red_dta": clean_amt("dta"),
            "amt_red_ipt": clean_amt("ipt"),

            # --- VALEURS DES RÉDUCTIONS ---
            "amt_val_red_rc": get_red_amt("rc"),
            "amt_val_red_dr": get_red_amt("dr"),
            "amt_val_red_vol": get_red_amt("vol"),
            "amt_val_red_vb": get_red_amt("vb"),
            "amt_val_red_in": get_red_amt("in"),
            "amt_val_red_bris": get_red_amt("bris"),
            "amt_val_red_ar": get_red_amt("ar"),
            "amt_val_red_dta": get_red_amt("dta"),
            "amt_val_red_ipt": get_red_amt("ipt"),

            # --- TAUX DE RÉDUCTION ---
            "red_rc": get_taux("rc"),
            "red_dr": get_taux("dr"),
            "red_vol": get_taux("vol"),
            "red_vb": get_taux("vb"),
            "red_in": get_taux("in"),
            "red_bris": get_taux("bris"),
            "red_ar": get_taux("ar"),
            "red_dta": get_taux("dta"),
            "red_ipt": get_taux("ipt"),

            "amt_fleet_rc_val": amt_rc,
            "amt_fleet_dr_val": amt_dr,
            "amt_fleet_vol_val": amt_vol,
            "amt_fleet_vb_val": amt_vb,
            "amt_fleet_in_val": amt_in,
            "amt_fleet_bris_val": amt_bris,
            "amt_fleet_ar_val": amt_ar,
            "amt_fleet_dta_val": amt_dta,
            "amt_fleet_ipt_val": amt_ipt,
        }
        
        # DEBUG: Afficher les données avant sauvegarde
        print("=== DONNÉES SAUVEGARDÉES ===")
        for key, value in data.items():
            if key.startswith(('owner_id', 'amt', 'prime', 'reduction', 'carte', 'accessoires', 'tva', 'asac', 'vignette', 'pttc')):
                print(f"{key}: {value}")
        print("============================")

        print("=== INITIALISATION DES CHAMPS DE FLOTTE ===")
        for key in ['amt_fleet_rc_val', 'amt_fleet_dr_val', 'amt_fleet_vol_val', 
                'amt_fleet_vb_val', 'amt_fleet_in_val', 'amt_fleet_bris_val',
                'amt_fleet_ar_val', 'amt_fleet_dta_val', 'amt_fleet_ipt_val']:
            print(f"   {key}: {data.get(key, 0)}")
        
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
                success, vehicle_id, message = self.controller.vehicles.create_vehicle(
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
        """Récupère les données du formulaire pour la sauvegarde"""
        def clean_amt(key):
            garantie_data = self.result_labels.get(key)
            if garantie_data:
                montant_net_label = garantie_data['montant_net']
                if montant_net_label and montant_net_label.isVisible():
                    txt = montant_net_label.text().replace(" FCFA", "").replace(" ", "").replace(",", ".")
                    print(f"clean_amt({key}) = {txt}")  # ← DEBUG
                    return float(txt) if txt else 0.0
            return 0.0
        
        def get_brut_amt(key):
            garantie_data = self.result_labels.get(key)
            if garantie_data:
                montant_brut_label = garantie_data['montant_brut']
                if montant_brut_label and montant_brut_label.isVisible():
                    txt = montant_brut_label.text().replace(" FCFA", "").replace(" ", "").replace(",", ".")
                    print(f"get_brut_amt({key}) = {txt}")  # ← DEBUG
                    return float(txt) if txt else 0.0
            return 0.0
        
        def get_red_amt(key):
            garantie_data = self.result_labels.get(key)
            if garantie_data:
                montant_taux_label = garantie_data.get('montant_taux')
                if montant_taux_label and montant_taux_label.isVisible():
                    txt = montant_taux_label.text().replace(" FCFA", "").replace(" ", "").replace(",", ".")
                    return float(txt) if txt else 0.0
            return 0.0
        
        def get_taux(key):
            garantie_data = self.result_labels.get(key)
            if garantie_data:
                taux_widget = garantie_data.get('taux')
                if taux_widget and taux_widget.isVisible():
                    txt = taux_widget.text().strip()
                    if txt.endswith('%'):
                        txt = txt[:-1]
                    try:
                        return float(txt) if txt else 0.0
                    except ValueError:
                        return 0.0
            return 0.0
        
        data = {
            # --- IDENTIFICATION & PROPRIÉTAIRE ---
            "immatriculation": self.immat_input.text().strip().upper(),
            "chassis": self.chassis_input.text().strip(),
            "zone": self.combo_zone.currentText(),
            "libele_tarif": self.combo_fleet.currentText(),
            "categorie": self.combo_cat.currentText(),
            "marque": self.marque_input.text().strip(),
            "modele": self.modele_input.text().strip(),
            "annee": int(self.annee_input.text()) if self.annee_input.text().isdigit() else None,
            "energie": self.energie_combo.currentText(),
            "usage": self.usage_input.text().strip(),
            "places": int(self.places_input.text()) if self.places_input.text().isdigit() else 5,
            "has_remorque": self.check_remorque.isChecked(),
            "statut": self.status_combo.currentText(),
            "code_tarif": self.code_tarif.currentText(),
            
            # --- PROPRIÉTAIRES ---
            "compagny_id": self.compagny_list.currentItem().data(Qt.UserRole).id if self.compagny_list.currentItem() else None,
            "owner_id": self.owner_list.currentItem().data(Qt.UserRole).id if self.owner_list.currentItem() else None,
            
            # --- DATES ---
            "date_debut": self.date_debut.date().toPython(),
            "date_fin": self.date_fin.date().toPython(),
            "nbr_jour": int(self.nbr_jour.text()) if self.nbr_jour.text().isdigit() else 0,
            
            # --- VALEURS FINANCIÈRES ---
            "valeur_neuf": float(self.val_neuf.text().replace(" ", "").replace(",", ".") or 0),
            "valeur_venale": float(self.val_venale.text().replace(" ", "").replace(",", ".") or 0),
            
            # --- RÉCAPITULATIF FINANCIER ---
            "prime_brute": float(self.prime_brute.text().replace(" ", "").replace(",", ".") or 0),
            "reduction": float(self.reduction.text().replace(" ", "").replace(",", ".") or 0),
            "prime_nette": float(self.prime_nette.text().replace(" ", "").replace(",", ".") or 0),
            "prime_emise": float(self.prime_nette.text().replace(" ", "").replace(",", ".") or 0),
            
            # --- FRAIS SUPPLÉMENTAIRES ---
            "carte_rose": float(self.carte_rose.text().replace(" ", "").replace(",", ".") or 0),
            "accessoires": float(self.accessoire.text().replace(" ", "").replace(",", ".") or 0),
            "tva": float(self.tva.text().replace(" ", "").replace(",", ".") or 0),
            "fichier_asac": float(self.asac.text().replace(" ", "").replace(",", ".") or 0),
            "vignette": float(self.vignette.text().replace(" ", "").replace(",", ".") or 0),
            "pttc": float(self.pttc.text().replace(" ", "").replace(",", ".") or 0),
            
            # --- ÉTAT DES GARANTIES (Booléens) ---
            "check_rc": self.check_rc.isChecked(),
            "check_dr": self.check_dr.isChecked(),
            "check_vol": self.check_vol.isChecked(),
            "check_vb": self.check_vb.isChecked(),
            "check_in": self.check_in.isChecked(),
            "check_bris": self.check_bris.isChecked(),
            "check_ar": self.check_ar.isChecked(),
            "check_dta": self.check_dta.isChecked(),
            "check_ipt": self.check_ipt.isChecked(),
            
            # --- MONTANTS BRUTS DES GARANTIES ---
            "amt_rc": get_brut_amt("rc"),
            "amt_dr": get_brut_amt("dr"),
            "amt_vol": get_brut_amt("vol"),
            "amt_vb": get_brut_amt("vb"),
            "amt_in": get_brut_amt("in"),
            "amt_bris": get_brut_amt("bris"),
            "amt_ar": get_brut_amt("ar"),
            "amt_dta": get_brut_amt("dta"),
            "amt_ipt": get_brut_amt("ipt"),
            
            # --- MONTANTS NETS APRÈS RÉDUCTION ---
            "amt_red_rc": clean_amt("rc"),
            "amt_red_dr": clean_amt("dr"),
            "amt_red_vol": clean_amt("vol"),
            "amt_red_vb": clean_amt("vb"),
            "amt_red_in": clean_amt("in"),
            "amt_red_bris": clean_amt("bris"),
            "amt_red_ar": clean_amt("ar"),
            "amt_red_dta": clean_amt("dta"),
            "amt_red_ipt": clean_amt("ipt"),
            
            # --- VALEURS DES RÉDUCTIONS (en FCFA) ---
            "amt_val_red_rc": get_red_amt("rc"),
            "amt_val_red_dr": get_red_amt("dr"),
            "amt_val_red_vol": get_red_amt("vol"),
            "amt_val_red_vb": get_red_amt("vb"),
            "amt_val_red_in": get_red_amt("in"),
            "amt_val_red_bris": get_red_amt("bris"),
            "amt_val_red_ar": get_red_amt("ar"),
            "amt_val_red_dta": get_red_amt("dta"),
            "amt_val_red_ipt": get_red_amt("ipt"),
            
            # --- TAUX DE RÉDUCTION ---
            "red_rc": get_taux("rc"),
            "red_dr": get_taux("dr"),
            "red_vol": get_taux("vol"),
            "red_vb": get_taux("vb"),
            "red_in": get_taux("in"),
            "red_bris": get_taux("bris"),
            "red_ar": get_taux("ar"),
            "red_dta": get_taux("dta"),
            "red_ipt": get_taux("ipt"),
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
            # Récupération des informations du formulaire
            cie_id = self.selected_cie_id 
            zone = self.combo_zone.currentText()
            categorie = self.combo_cat.currentText()
            energie = self.energie_combo.currentText()
            
            cv_text = self.usage_input.text().strip()
            cv = int(cv_text) if cv_text else 0
            
            avec_remorque = self.check_remorque.isChecked() 

            if self.controller:
                res_rc = self.controller.vehicles.get_rc_premium_from_matrix(
                    cie_id=cie_id,
                    zone=zone,
                    categorie=categorie,
                    energie=energie,
                    cv_saisi=cv,
                    avec_remorque=avec_remorque,
                    code_tarif=self.code_tarif.currentText().strip() if self.code_tarif.currentText() else None
                )

                montant_rc = res_rc.get('rc', 0.0) if isinstance(res_rc, dict) else res_rc
                libelle = res_rc.get('libelle', '') if isinstance(res_rc, dict) else ''
                categorie_retournee = res_rc.get('categorie', '') if isinstance(res_rc, dict) else ''

                if categorie_retournee and self.combo_cat.currentText() != categorie_retournee:
                    if self.combo_cat.findText(categorie_retournee) == -1:
                        self.combo_cat.addItem(categorie_retournee)
                    self.combo_cat.setCurrentText(categorie_retournee)

                if libelle and self.combo_fleet.currentText() != libelle:
                    self.combo_fleet.setCurrentText(libelle)

                # Mise à jour du label de résultat
                garantie_data = self.result_labels.get("rc")
                if garantie_data and montant_rc > 0:
                    garantie_data['montant_brut'].setText(f"{montant_rc:,.0f} FCFA")
                    garantie_data['montant_net'].setText(f"{montant_rc:,.0f} FCFA")
                elif garantie_data:
                    garantie_data['montant_brut'].setText("Tarif introuvable")
                    garantie_data['montant_net'].setText("Tarif introuvable")

        except Exception as e:
            print(f"Erreur lors du calcul RC : {e}")
            garantie_data = self.result_labels.get("rc")
            if garantie_data:
                garantie_data['montant_brut'].setText("Erreur calcul")
                garantie_data['montant_net'].setText("Erreur calcul")
  
    def calculate_total_premium(self):
        """Calcule le total des primes avec gestion sécurisée des types"""
        try:
            def get_amt(key):
                garantie_data = self.result_labels.get(key)
                if garantie_data:
                    montant_brut_label = garantie_data['montant_brut']
                    if montant_brut_label and montant_brut_label.isVisible():
                        txt = montant_brut_label.text().replace(" FCFA", "").replace(" ", "").replace(",", ".")
                        try:
                            return float(txt) if txt and "Erreur" not in txt else 0.0
                        except ValueError:
                            return 0.0
                return 0.0

            def get_red_amt(key):
                garantie_data = self.result_labels.get(key)
                if garantie_data:
                    montant_net_label = garantie_data['montant_net']
                    if montant_net_label and montant_net_label.isVisible():
                        txt = montant_net_label.text().replace(" FCFA", "").replace(" ", "").replace(",", ".")
                        try:
                            return float(txt) if txt and "Erreur" not in txt else 0.0
                        except ValueError:
                            return 0.0
                return 0.0
            
            def get_reduction_amt(key):
                """Récupère le montant de la réduction (amt_val_red_xx)"""
                garantie_data = self.result_labels.get(key)
                if garantie_data:
                    montant_taux_label = garantie_data.get('montant_taux')
                    if montant_taux_label and montant_taux_label.isVisible():
                        txt = montant_taux_label.text().replace(" FCFA", "").replace(" ", "").replace(",", ".")
                        try:
                            return float(txt) if txt and "Erreur" not in txt else 0.0
                        except ValueError:
                            return 0.0
                return 0.0
            
            # Récupération sécurisée (tous seront des floats)
            amt_rc = get_amt("rc")
            amt_dr = get_amt("dr")
            amt_vol = get_amt("vol")
            amt_vb = get_amt("vb")
            amt_in = get_amt("in")
            amt_bris = get_amt("bris")
            amt_dta = get_amt("dta")
            amt_ar = get_amt("ar")
            amt_ipt = get_amt("ipt")

            amt_red_rc = get_red_amt("rc")
            amt_red_dr = get_red_amt("dr")
            amt_red_vol = get_red_amt("vol")
            amt_red_vb = get_red_amt("vb")
            amt_red_in = get_red_amt("in")
            amt_red_bris = get_red_amt("bris")
            amt_red_dta = get_red_amt("dta")
            amt_red_ar = get_red_amt("ar")
            amt_red_ipt = get_red_amt("ipt")

            amt_val_red_rc = get_reduction_amt("rc")
            amt_val_red_dr = get_reduction_amt("dr")
            amt_val_red_vol = get_reduction_amt("vol")
            amt_val_red_vb = get_reduction_amt("vb")
            amt_val_red_in = get_reduction_amt("in")
            amt_val_red_bris = get_reduction_amt("bris")
            amt_val_red_dta = get_reduction_amt("dta")
            amt_val_red_ar = get_reduction_amt("ar")
            amt_val_red_ipt = get_reduction_amt("ipt")
            
            # 1. Total Brut
            total_brut = amt_rc + amt_dr + amt_vol + amt_vb +  amt_in + amt_bris + amt_dta + amt_ar + amt_ipt
            total_net = amt_red_rc + amt_red_dr + amt_red_vol + amt_red_vb + amt_red_in + amt_red_bris + amt_red_dta + amt_red_ar + amt_red_ipt
            reduction = amt_val_red_rc + amt_val_red_dr + amt_val_red_vol + amt_val_red_vb + amt_val_red_in + amt_val_red_bris + amt_val_red_dta + amt_val_red_ar + amt_val_red_ipt
            
            print(reduction)
            # 3. Mise à jour de l'affichage
            self.prime_brute.setText(f"{total_brut:,.0f}".replace(",", " "))
            self.prime_nette.setText(f"{total_net:,.0f}".replace(",", " "))
            self.reduction.setText(f"{reduction:,.0f}".replace(",", " "))

            # Calcul de la TVA
            self.calculate_tva()
            
            # Calcul du PTTC (Prime Toute Taxe Comprise)
            self.calculate_pttc()
            
            # # Pour la base de données (sans espaces)
            # self.prime_emise.setText(f"{reduction:.0f}")
            
        except Exception as e:
            print(f"Erreur dans le récapitulatif financier : {e}")

    def calculate_pttc(self):
        """Calcule le PTTC (Prime Toute Taxe Comprise)"""
        try:
            prime_nette = self.get_float_value(self.prime_nette)
            accessoires = self.get_float_value(self.accessoire)
            asac = self.get_float_value(self.asac)
            tva = self.get_float_value(self.tva)
            vignette = self.get_float_value(self.vignette)
            carte_rose = self.get_float_value(self.carte_rose)
            
            pttc = prime_nette + accessoires + asac + tva + vignette + carte_rose
            print(pttc)
            
            self.pttc.setText(f"{pttc:,.0f}".replace(",", " "))
            
            return pttc
        except Exception as e:
            print(f"Erreur calcul PTTC: {e}")
            return 0

    def refresh_all_garanties(self):
        """Rafraîchit toutes les garanties"""
        for key in self.result_labels.keys():
            checkbox = getattr(self, f"check_{key}")
            if checkbox.isChecked():
                self.update_garantie_price(key, 2)

    def on_code_tarif_changed(self, code):
        """Lorsque le code tarif change, met à jour le libellé et la catégorie correspondants"""
        if code and self.selected_cie_id:
            # Chercher le libellé correspondant dans les données chargées
            for item in [self.code_tarif.itemData(i) for i in range(self.code_tarif.count())]:
                if item and item.get('code') == code:
                    libelle = item.get('libelle', '')
                    if libelle:
                        self.combo_fleet.setCurrentText(libelle)
                    break

            # Si un code tarif est sélectionné, recalculer la RC pour récupérer la catégorie
            self.update_rc_calculation()

    def load_tarif_codes(self):
        """Charge la liste des codes tarif pour la compagnie sélectionnée"""
        if not self.selected_cie_id or not self.controller:
            return
        
        try:
            codes = self.controller.vehicles.get_tarif_codes_by_compagnie(self.selected_cie_id)
            
            # Vider et remplir la combo box
            self.code_tarif.clear()
            self.code_tarif.addItem("", "")  # Option vide
            
            for code, libelle in codes:
                self.code_tarif.addItem(code, {"code": code, "libelle": libelle})
                # Stocker le libellé comme user data
            
            # Mettre à jour aussi la combo_fleet
            self.combo_fleet.clear()
            self.combo_fleet.addItem("", "")
            for code, libelle in codes:
                self.combo_fleet.addItem(libelle, {"code": code, "libelle": libelle})

            # Mettre à jour la combo_cat avec les catégories disponibles
            self.combo_cat.clear()
            self.combo_cat.addItem("", "")
            categories = []
            if self.controller:
                categories = self.controller.vehicles.get_tarif_categories_by_compagnie(self.selected_cie_id)
            for categorie in categories:
                self.combo_cat.addItem(str(categorie))
                
        except Exception as e:
            print(f"Erreur lors du chargement des codes tarif : {e}")

    def update_garantie_price(self, key, state):
        """
        Met à jour le prix d'une garantie
        """
        garantie_data = self.result_labels.get(key)
        if not garantie_data:
            return
        
        montant_brut_label = garantie_data['montant_brut']
        taux_widget = garantie_data['taux']
        montant_taux_label = garantie_data['montant_taux']
        montant_net_label = garantie_data['montant_net']

        try:
            if state:  # Garantie activée
                # Calcul du prorata
                d_debut = self.date_debut.date().toPython()
                d_fin = self.date_fin.date().toPython()
                nbr_jr = max(0, (d_fin - d_debut).days)
                self.nbr_jour.setText(str(nbr_jr))
                prorata = nbr_jr / 365.0 if nbr_jr > 0 else 1
                
                # Calcul du montant brut selon le type de garantie
                montant_brut = self.calculate_garantie_amount(key, prorata)
                
                # Afficher le montant brut
                if montant_brut > 0:
                    montant_brut_label.setText(f"{montant_brut:,.0f} FCFA".replace(",", " "))
                    montant_brut_label.setStyleSheet("""
                        color: #27ae60;
                        font-weight: bold;
                        background-color: #e8f5e9;
                        padding: 4px 8px;
                        border-radius: 6px;
                    """)

                    # Afficher le montant du taux (même valeur que brut initialement)
                    montant_taux_label.setText(f"{montant_brut:,.0f} FCFA".replace(",", " "))
                    montant_taux_label.setStyleSheet("""
                        color: #27ae60;
                        font-weight: bold;
                        background-color: #e8f5e9;
                        padding: 4px 8px;
                        border-radius: 6px;
                    """)
                else:
                    montant_brut_label.setText("0 FCFA")
                    montant_taux_label.setText("0 FCFA")
                
                # Afficher les widgets (AJOUTER montant_taux_label ici)
                montant_brut_label.setVisible(True)
                taux_widget.setVisible(True)
                montant_taux_label.setVisible(True)  # ← AJOUTER CETTE LIGNE
                montant_net_label.setVisible(True)
                
                # Connecter le signal du taux si ce n'est pas déjà fait
                try:
                    taux_widget.textChanged.disconnect()
                except:
                    pass
                taux_widget.textChanged.connect(lambda: self.update_net_amount(key))
                
                # Calculer le montant net initial
                self.update_net_amount(key)
                
            else:  # Garantie désactivée
                # Cacher tous les widgets
                montant_brut_label.setVisible(False)
                taux_widget.setVisible(False)
                montant_taux_label.setVisible(False)  # ← AJOUTER CETTE LIGNE
                montant_net_label.setVisible(False)
                
                # Réinitialiser
                montant_brut_label.setText("0 FCFA")
                montant_net_label.setText("0 FCFA")
                montant_taux_label.setText("0 FCFA")
                taux_widget.setText("")
            
            self.calculate_total_premium()
            
        except Exception as e:
            print(f"❌ Erreur pour la garantie '{key}': {str(e)}")
            import traceback
            traceback.print_exc()
            
    def get_rc_base_amount(self):
        """
        Récupère le montant de base de la RC (utile pour les garanties dépendantes)
        
        Returns:
            float: Montant de la RC (0 si non calculée)
        """
        try:
            garantie_data = self.result_labels.get("rc")
            if garantie_data:
                montant_brut_label = garantie_data['montant_brut']
                if montant_brut_label and montant_brut_label.isVisible():
                    txt = montant_brut_label.text().replace(" FCFA", "").replace(" ", "").replace(",", ".")
                    return float(txt) if txt else 0.0
            return 0.0
        except (ValueError, AttributeError):
            return 0.0
        
    def handle_garantie_click(self, key, state):
        """Gère l'affichage et le calcul lors du clic sur une garantie"""
        is_checked = (state == Qt.Checked or state == 2)
        garantie_data = self.result_labels.get(key)
        
        if garantie_data:
            if is_checked:
                garantie_data['montant_brut'].setVisible(True)
                garantie_data['taux'].setVisible(True)
                garantie_data['montant_taux'].setVisible(True)
                garantie_data['montant_net'].setVisible(True)
                if key == "rc":
                    self.update_rc_calculation()
            else:
                garantie_data['montant_brut'].setVisible(False)
                garantie_data['taux'].setVisible(False)
                garantie_data['montant_taux'].setVisible(False)
                garantie_data['montant_net'].setVisible(False)
                garantie_data['montant_brut'].setText("0 FCFA")
                garantie_data['montant_net'].setText("0 FCFA")
                garantie_data['montant_taux'].setText("0 FCFA")

    def calculate_tva(self):
        """Calcule la TVA selon la formule: TVA = (Prime_net + Accessoires + Fichier ASAC) * 19.25%"""
        try:
            # Récupérer les valeurs
            prime_nette = self.get_float_value(self.prime_nette)
            accessoires = self.get_float_value(self.accessoire)
            asac = self.get_float_value(self.asac)
            
            # Calcul de la TVA
            base_tva = prime_nette + accessoires + asac
            tva = base_tva * 0.1925  # 19.25%
            
            # Mettre à jour le champ TVA
            self.tva.setText(f"{tva:,.0f}".replace(",", " "))
            
            return tva
        except Exception as e:
            print(f"Erreur calcul TVA: {e}")
            return 0
        
    def calculate_garantie_amount(self, key, prorata):
        """Calcule le montant brut de la garantie"""
        # Récupérer les valeurs nécessaires
        v_venale = self.get_float_value(self.val_venale)
        v_neuf = self.get_float_value(self.val_neuf)
        
        if key == "rc":
            return self.calculate_rc_brut() * prorata
        elif key == "dr":
            return self.get_rc_base_amount() * 0.03
        elif key == "vol":
            return v_venale * 0.02 * prorata
        elif key == "vb":
            return v_venale * 0.02 * prorata
        elif key == "in":
            return v_venale * 0.025 * prorata
        elif key == "bris":
            return v_neuf * 0.005 * prorata
        elif key == "ar":
            return v_venale * 0.75 * 0.03 * prorata
        elif key == "dta":
            # cv = self.get_int_value(self.usage_input)
            # if cv < 2:
            #     return 0
            # elif 2 <= cv <= 7:
            #     return 30000 * prorata
            # elif 8 <= cv <= 13:
            #     return 50000 * prorata
            # elif 14 <= cv <= 20:
            #     return 75000 * prorata
            # else:
            #     return 200000 * prorata
            return self.val_neuf * 0.05 * prorata
        elif key == "ipt":
            if int(self.places_input.text()) == 5:
                return 7500
            elif int(self.places_input.text()) == 7:
                return ((7500 * 7) / 5) * prorata
        return 0

    def update_net_amount(self, key):
        """Met à jour le montant net après application du taux"""
        garantie_data = self.result_labels.get(key)
        if not garantie_data:
            return
        
        try:
            # Récupérer le montant brut
            brut_text = garantie_data['montant_brut'].text()
            brut_text = brut_text.replace(" FCFA", "").replace(" ", "").replace(",", ".")
            
            try:
                montant_brut = float(brut_text) if brut_text else 0
            except ValueError:
                montant_brut = 0
            
            # Récupérer le taux
            taux_text = garantie_data['taux'].text().strip()
            if taux_text.endswith('%'):
                taux_text = taux_text[:-1]
            
            try:
                taux = float(taux_text) if taux_text else 0
            except ValueError:
                taux = 0
            
            # Calculer le montant net et la réduction
            if taux > 0:
                reduction = montant_brut * (taux / 100)
                montant_net = montant_brut - reduction
            else:
                reduction = 0
                montant_net = montant_brut
            
            # Afficher le montant net
            montant_net_label = garantie_data['montant_net']
            montant_net_label.setText(f"{montant_net:,.0f} FCFA".replace(",", " "))
            
            # Afficher le montant de la réduction si le widget existe
            montant_taux = garantie_data.get('montant_taux')
            if montant_taux:
                montant_taux.setText(f"{reduction:,.0f} FCFA".replace(",", " "))
            
            # Appliquer un style différent selon le taux
            if taux > 0:
                montant_net_label.setStyleSheet("""
                    color: #e67e22;
                    font-weight: bold;
                    background-color: #fff3e0;
                    padding: 4px 8px;
                    border-radius: 6px;
                    border-left: 2px solid #e67e22;
                """)
            else:
                montant_net_label.setStyleSheet("""
                    color: #27ae60;
                    font-weight: bold;
                    background-color: #e8f5e9;
                    padding: 4px 8px;
                    border-radius: 6px;
                """)
            
            # Mettre à jour le total
            self.calculate_total_premium()
            
        except Exception as e:
            print(f"Erreur lors du calcul du montant net pour {key}: {e}")
            import traceback
            traceback.print_exc()

    def get_float_value(self, widget):
        """Récupère une valeur float d'un widget"""
        try:
            if not widget or not widget.text():
                return 0.0
            txt = widget.text().strip().replace(" ", "").replace(",", ".")
            return float(txt) if txt else 0.0
        except:
            return 0.0

    def get_int_value(self, widget):
        """Récupère une valeur int d'un widget"""
        try:
            if not widget or not widget.text():
                return 0
            return int(widget.text())
        except:
            return 0

    def calculate_rc_brut(self):
        """Calcule le montant brut de la RC"""
        try:
            if not self.selected_cie_id:
                return 0
                
            # Récupérer les paramètres
            code_tarif = self.code_tarif.currentText().strip() if hasattr(self.code_tarif, 'currentText') else ""
            categorie = self.combo_cat.currentText().strip()
            avec_remorque = self.check_remorque.isChecked()
            zone = self.combo_zone.currentText()
            energie = self.energie_combo.currentText()
            cv = self.get_int_value(self.usage_input)
            
            # Appeler la méthode du contrôleur
            res_rc = self.controller.vehicles.get_rc_premium_from_matrix(
                cie_id=self.selected_cie_id,
                zone_saisie=zone,
                categorie=categorie,
                energie=energie,
                cv_saisi=cv,
                avec_remorque=avec_remorque,
                code_tarif=code_tarif if code_tarif else None
            )
            
            # Récupérer le montant
            montant_rc = res_rc.get('rc', 0.0)
            
            # Mettre à jour le libellé et la catégorie si nécessaire
            libelle = res_rc.get('libelle', '')
            categorie_retournee = res_rc.get('categorie', '')
            
            if libelle and self.combo_fleet.currentText() != libelle:
                self.combo_fleet.setCurrentText(libelle)
            
            if categorie_retournee and self.combo_cat.currentText() != categorie_retournee:
                self.combo_cat.setCurrentText(categorie_retournee)
            
            return montant_rc
            
        except Exception as e:
            print(f"Erreur lors du calcul RC : {e}")
            return 0

    # Dans votre vue de création de véhicule (automobile_view.py par exemple)

    def create_vehicle_with_contract(self, vehicle_data):
        """Crée un véhicule et son contrat proformat"""
        
        with self.controller.vehicles as vehicle_ctrl:
            success, vehicle, message = vehicle_ctrl.create_vehicle(
                data=vehicle_data,
                user_id=self.get_current_user_id()
            )
            
            if success:
                QMessageBox.information(self, "Succès", 
                    f"Véhicule créé avec succès!\n"
                    f"Immatriculation: {vehicle.immatriculation}\n"
                    f"Un proformat a été généré automatiquement.")
                
                # Ouvrir la vue de détail du véhicule avec son proformat
                self.show_vehicle_detail(vehicle.id)
            else:
                QMessageBox.warning(self, "Erreur", f"Erreur: {message}")
