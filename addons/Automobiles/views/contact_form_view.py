# contact_form_view.py
import cv2
import os
import uuid 
from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QComboBox, QPushButton, QLabel, QFrame, QGridLayout, 
    QScrollArea, QDateEdit, QMessageBox, QWidget,
    QSplitter, QSizePolicy, QStackedWidget, QGroupBox,
    QFormLayout, QListWidget
)
from PySide6.QtCore import Qt, QTimer, QSize, QDate, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QImage, QPixmap, QColor, QFont, QIcon, QPalette
from addons.Automobiles.utils.countries import COUNTRIES
from addons.Automobiles.utils.cities import CITIES_BY_COUNTRY



class ContactForm(QDialog):
    """Formulaire professionnel de gestion des contacts"""
    
    contact_saved = Signal(object)
    
    # Styles prédéfinis
    STYLE = """
        QDialog {
            background: transparent;
        }
        QLabel {
            color: #1e293b;
            font-weight: 500;
            font-size: 12px;
        }
        QLabel#required {
            color: #ef4444;
        }
        QLabel#section_title {
            color: #2563eb;
            font-weight: 700;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 6px;
            margin-top: 4px;
        }
        QLineEdit, QComboBox, QDateEdit {
            background: #ffffff;
            border: 1.5px solid #e2e8f0;
            border-radius: 8px;
            padding: 9px 14px;
            color: #0f172a;
            font-size: 13px;
            min-height: 22px;
        }
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
            border-color: #2563eb;
            background: #f8faff;
        }
        QLineEdit:disabled, QComboBox:disabled {
            background: #f1f5f9;
            color: #94a3b8;
        }
        QLineEdit#readonly {
            background: #f1f5f9;
            color: #475569;
        }
        QGroupBox {
            border: 1.5px solid #e2e8f0;
            border-radius: 12px;
            margin-top: 12px;
            padding-top: 16px;
            background: #ffffff;
        }
        QGroupBox::title {
            left: 16px;
            padding: 0 10px;
            color: #1e293b;
            font-weight: 700;
            font-size: 13px;
        }
        QScrollArea {
            border: none;
            background: transparent;
        }
        QScrollArea > QWidget > QWidget {
            background: transparent;
        }
        QScrollBar:vertical {
            background: #f1f5f9;
            width: 6px;
            border-radius: 3px;
        }
        QScrollBar::handle:vertical {
            background: #cbd5e1;
            border-radius: 3px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover {
            background: #94a3b8;
        }
        QScrollBar:horizontal {
            background: #f1f5f9;
            height: 6px;
            border-radius: 3px;
        }
        QScrollBar::handle:horizontal {
            background: #cbd5e1;
            border-radius: 3px;
            min-width: 30px;
        }
        QScrollBar::handle:horizontal:hover {
            background: #94a3b8;
        }
         /* ✅ STYLE POUR LES LISTES DÉROULANTES DES COMBOBOX */
        QComboBox QAbstractItemView {
            background: #ffffff;
            border: 1.5px solid #e2e8f0;
            border-radius: 8px;
            padding: 4px;
            selection-background-color: #2563eb;
            selection-color: #ffffff;
            color: #0f172a;
            font-size: 13px;
            outline: none;
        }
        QComboBox QAbstractItemView::item {
            padding: 8px 12px;
            border-radius: 4px;
            min-height: 20px;
        }
        QComboBox QAbstractItemView::item:hover {
            background: #f1f5f9;
            color: #0f172a;
        }
        QComboBox QAbstractItemView::item:selected {
            background: #2563eb;
            color: #ffffff;
        }
        
        /* ✅ STYLE POUR L'ICÔNE DE LA FLÈCHE */
        QComboBox::drop-down {
            border: none;
            width: 30px;
        }
        QComboBox::down-arrow {
            image: none;
            border: none;
            width: 10px;
            height: 10px;
            background: transparent;
        }
        QComboBox::down-arrow:on {
            /* Optionnel: style quand la liste est ouverte */
        }
        
        QGroupBox {
            border: 1.5px solid #e2e8f0;
            border-radius: 12px;
            margin-top: 12px;
            padding-top: 16px;
            background: #ffffff;
        }
        QGroupBox::title {
            left: 16px;
            padding: 0 10px;
            color: #1e293b;
            font-weight: 700;
            font-size: 13px;
        }
        QScrollArea {
            border: none;
            background: transparent;
        }
        QScrollArea > QWidget > QWidget {
            background: transparent;
        }
        QScrollBar:vertical {
            background: #f1f5f9;
            width: 6px;
            border-radius: 3px;
        }
        QScrollBar::handle:vertical {
            background: #cbd5e1;
            border-radius: 3px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover {
            background: #94a3b8;
        }
        QScrollBar:horizontal {
            background: #f1f5f9;
            height: 6px;
            border-radius: 3px;
        }
        QScrollBar::handle:horizontal {
            background: #cbd5e1;
            border-radius: 3px;
            min-width: 30px;
        }
        QScrollBar::handle:horizontal:hover {
            background: #94a3b8;
        }
    """

    combo_popup_style = """
        QComboBox {
            background: #ffffff;
            border: 1.5px solid #e2e8f0;
            border-radius: 8px;
            padding: 9px 14px;
            color: #0f172a;
            font-size: 13px;
            min-height: 22px;
        }
        QComboBox:focus {
            border-color: #2563eb;
            background: #f8faff;
        }
        QComboBox::drop-down {
            border: none;
            width: 30px;
            background: transparent;
        }
        QComboBox::down-arrow {
            image: none;
            border: none;
            width: 10px;
            height: 10px;
            background: transparent;
        }
        QComboBox QAbstractItemView {
            background: #ffffff;
            border: 1.5px solid #e2e8f0;
            border-radius: 8px;
            padding: 4px;
            selection-background-color: #2563eb;
            selection-color: #ffffff;
            color: #0f172a;
            font-size: 13px;
            outline: none;
        }
        QComboBox QAbstractItemView::item {
            padding: 8px 12px;
            border-radius: 4px;
            min-height: 20px;
        }
        QComboBox QAbstractItemView::item:hover {
            background: #f1f5f9;
            color: #0f172a;
        }
        QComboBox QAbstractItemView::item:selected {
            background: #2563eb;
            color: #ffffff;
        }
    """

    def __init__(self, controller, contact_data=None, parent=None, mode="add"):
        super().__init__(parent)
        
        # Configuration de la fenêtre
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Données
        self.controller = controller
        self.contact_data = contact_data
        self.mode = mode
        self.is_editing = contact_data is not None
        
        # État de la caméra
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)
        self.captured_image = None
        self.is_camera_on = False
        
        # Configuration de l'UI
        self._setup_ui()
        self._setup_connections()
        
        # Chargement des données
        if self.contact_data:
            self._load_data()

        self._on_type_changed(self.type_client.currentIndex())
        
        # État initial
        self._update_visibility()
        # self._load_subscribers()
        # self._load_subscribers_for_driver()

    # ============================================================
    # CONFIGURATION DE L'UI
    # ============================================================
    
    def _setup_ui(self):
        """Configure l'interface principale"""
        self.setMinimumSize(1300, 880)
        self.resize(1350, 900)
        self.setStyleSheet(self.STYLE)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Conteneur principal avec ombre
        self.container = QFrame()
        self.container.setObjectName("MainContainer")
        self.container.setStyleSheet("""
            QFrame#MainContainer {
                background: #ffffff;
                border-radius: 24px;
                border: 1px solid rgba(30, 41, 59, 0.08);
                margin: 12px;
            }
        """)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # --- HEADER ---
        self._setup_header(container_layout)
        
        # --- SEPARATEUR ---
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background: #e2e8f0; margin: 0 30px;")
        container_layout.addWidget(separator)
        
        # --- CORPS ---
        body_widget = QWidget()
        body_widget.setStyleSheet("background: transparent;")
        body_layout = QHBoxLayout(body_widget)
        body_layout.setContentsMargins(30, 20, 30, 20)
        body_layout.setSpacing(25)
        
        # Formulaire
        form_widget = self._setup_form()
        body_layout.addWidget(form_widget, 7)
        
        # Panneau caméra
        camera_panel = self._setup_camera_panel()
        body_layout.addWidget(camera_panel, 3)
        
        container_layout.addWidget(body_widget)
        
        # --- FOOTER ---
        self._setup_footer(container_layout)
        
        main_layout.addWidget(self.container)

    def _setup_header(self, parent_layout):
        """Configure l'en-tête"""
        header = QFrame()
        header.setFixedHeight(72)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f8fafc, stop:1 #ffffff);
                border-top-left-radius: 24px;
                border-top-right-radius: 24px;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 0, 20, 0)
        header_layout.setSpacing(15)
        
        # Titre
        mode_text = "MODIFICATION" if self.mode == "edit" else "NOUVEAU"
        title = QLabel(f"📋 FICHE CONTACT — {mode_text}")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: 700;
            color: #0f172a;
            letter-spacing: -0.3px;
        """)
        
        subtitle = QLabel("Renseignez les informations du client")
        subtitle.setStyleSheet("""
            font-size: 13px;
            color: #64748b;
            font-weight: 400;
        """)
        
        title_container = QVBoxLayout()
        title_container.setSpacing(0)
        title_container.addWidget(title)
        title_container.addWidget(subtitle)
        
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        
        # Boutons de contrôle
        btn_style = """
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                padding: 6px 10px;
                color: #64748b;
            }
            QPushButton:hover {
                background: #f1f5f9;
            }
            QPushButton#closeBtn:hover {
                background: #fee2e2;
                color: #ef4444;
            }
        """
        
        self.btn_minimize = QPushButton("─")
        self.btn_minimize.setFixedSize(34, 34)
        self.btn_minimize.setStyleSheet(btn_style)
        self.btn_minimize.clicked.connect(self.showMinimized)
        
        self.btn_maximize = QPushButton("□")
        self.btn_maximize.setFixedSize(34, 34)
        self.btn_maximize.setStyleSheet(btn_style)
        self.btn_maximize.clicked.connect(self.toggle_maximize)
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("closeBtn")
        self.btn_close.setFixedSize(34, 34)
        self.btn_close.setStyleSheet(btn_style)
        self.btn_close.clicked.connect(self.reject)

        header_layout.addWidget(self.btn_minimize)
        header_layout.addWidget(self.btn_maximize)
        header_layout.addWidget(self.btn_close)
        
        parent_layout.addWidget(header)


    def _setup_form(self):
        """Configure le formulaire"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        self.form_layout = QGridLayout(content)
        self.form_layout.setSpacing(16)
        self.form_layout.setContentsMargins(0, 0, 10, 0)
        self.form_layout.setColumnStretch(0, 1)
        self.form_layout.setColumnStretch(1, 1)
        self.form_layout.setColumnStretch(2, 1)
        
        row = 0
        
        # === SECTION 1: TYPE DE CLIENT ===
        self._add_section_title("I. Type de Client", row)
        row += 1
        
        # Conteneur pour le type de client
        type_container = QWidget()
        type_container.setStyleSheet("background: transparent;")
        type_layout = QHBoxLayout(type_container)
        type_layout.setSpacing(15)
        type_layout.setContentsMargins(0, 0, 0, 0)
        
        type_label = QLabel("Type de Client *")
        type_label.setStyleSheet("""
            color: #1e293b;
            font-weight: 600;
            font-size: 13px;
            min-width: 120px;
        """)
        type_layout.addWidget(type_label)
        
        self.type_client = QComboBox()
        self.type_client.addItems(["Souscripteur", "Chauffeur"])
        self.type_client.setStyleSheet(self.combo_popup_style)
        type_layout.addWidget(self.type_client)
        type_layout.addStretch()
        
        self.form_layout.addWidget(type_container, row, 0, 1, 3)
        row += 1
        
        # === SECTION 2: ADMINISTRATION ===
        self._add_section_title("II. Administration", row)
        row += 1
        
        self.statut = QComboBox()
        self.statut.addItems(["Actif", "Inactif", "En attente"])
        self.statut.setStyleSheet(self.combo_popup_style)
        self._add_field("Statut", self.statut, row, 0)
        
        self.nature = QComboBox()
        self.nature.addItems(["Particulier", "Société"])
        self.nature.currentIndexChanged.connect(self._update_visibility)
        self.nature.setStyleSheet(self.combo_popup_style)
        self._add_field("Nature", self.nature, row, 1)
        
        self.charge_client = QLineEdit()
        self.charge_client.setPlaceholderText("Chargé de clientèle")
        self._add_field("Chargé de clientèle", self.charge_client, row, 2)
        row += 1
        
        # === SECTION 3: IDENTITÉ ===
        self._add_section_title("III. Identité", row)
        row += 1
        
        self.civilite = QComboBox()
        self.civilite.addItems(["M.", "Mme", "Mlle", "Dr", "Pr"])
        self.civilite.setStyleSheet(self.combo_popup_style)
        self._add_field("Civilité", self.civilite, row, 0)
        
        self.nom = QLineEdit()
        self.nom.setPlaceholderText("Nom / Raison sociale")
        self._add_field("Nom *", self.nom, row, 1, 2)
        row += 1
        
        self.prenom = QLineEdit()
        self.prenom.setPlaceholderText("Prénom(s)")
        self._add_field("Prénoms", self.prenom, row, 0, 2)
        
        self.date_naiss = QDateEdit()
        self.date_naiss.setCalendarPopup(True)
        self.date_naiss.setDate(QDate.currentDate().addYears(-30))
        self.date_naiss.setDisplayFormat("dd/MM/yyyy")
        self._add_field("Date de naissance", self.date_naiss, row, 2)
        row += 1
        
        self.nationalite = QComboBox()
        self.nationalite.setEditable(True)
        self.nationalite.setPlaceholderText("Sélectionner ou saisir une nationalité")
        self.nationalite.setStyleSheet(self.combo_popup_style)
        self.nationalite.addItem("")  # Option vide
        self.nationalite.addItem("CAMEROUN")  # Cameroun en premier
        self.nationalite.insertSeparator(2)
        for country in COUNTRIES:
            if country != "CAMEROUN":
                self.nationalite.addItem(country)
        self.nationalite.currentTextChanged.connect(self._update_cities)
        self._add_field("Nationalité", self.nationalite, row, 0)
        
        self.num_contribuable = QLineEdit()
        self.num_contribuable.setPlaceholderText("N° IFU / Contribuable")
        self._add_field("N° Contribuable", self.num_contribuable, row, 1, 2)
        row += 1
        
        self.specific_stack = QStackedWidget()
        self.specific_stack.setMinimumHeight(140)
        
        # Souscripteur
        subscriber_widget = self._create_subscriber_fields()
        self.specific_stack.addWidget(subscriber_widget)
        
        # Chauffeur
        driver_widget = self._create_driver_fields()
        self.specific_stack.addWidget(driver_widget)
        
        self._add_field("", self.specific_stack, row, 0, 3)
        row += 1
        
        # === SECTION 5: COORDONNÉES ===
        self._add_section_title("V. Coordonnées", row)
        row += 1
        
        self.tel = QLineEdit()
        self.tel.setPlaceholderText("Téléphone")
        self._add_field("Téléphone", self.tel, row, 0)
        
        self.fax = QLineEdit()
        self.fax.setPlaceholderText("Portable / Fax")
        self._add_field("Portable", self.fax, row, 1)
        
        self.email = QLineEdit()
        self.email.setPlaceholderText("email@exemple.com")
        self._add_field("Email", self.email, row, 2)
        row += 1
        
        self.adresse = QLineEdit()
        self.adresse.setPlaceholderText("Adresse complète")
        self._add_field("Adresse", self.adresse, row, 1, 1)
        
        self.ville = QComboBox()
        self.ville.setEditable(True)
        self.ville.setPlaceholderText("Sélectionner ou saisir une ville")
        self.ville.setStyleSheet(self.combo_popup_style)
        self._add_field("Nationalité", self.nationalite, row, 0)
        self._add_field("Ville", self.ville, row, 2)
        row += 1
        
        # === SECTION 6: PERMIS DE CONDUIRE (UNIQUEMENT POUR CHAUFFEUR) ===
        # ✅ Créer un conteneur pour la section permis
        self.permis_container = QWidget()
        self.permis_container.setStyleSheet("background: transparent;")
        permis_layout = QVBoxLayout(self.permis_container)
        permis_layout.setSpacing(16)
        permis_layout.setContentsMargins(0, 0, 0, 0)
        
        # Titre de la section
        permis_title = QLabel("VI. Permis de conduire")
        permis_title.setObjectName("section_title")
        permis_title.setStyleSheet("""
            color: #2563eb;
            font-weight: 700;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 6px;
            margin-top: 4px;
        """)
        permis_layout.addWidget(permis_title)
        
        # Champs permis
        permis_fields = QWidget()
        permis_fields_layout = QGridLayout(permis_fields)
        permis_fields_layout.setSpacing(16)
        permis_fields_layout.setContentsMargins(0, 8, 0, 0)
        permis_fields_layout.setColumnStretch(0, 1)
        permis_fields_layout.setColumnStretch(1, 1)
        permis_fields_layout.setColumnStretch(2, 1)
        
        # Catégorie permis
        self.cat_permis = QComboBox()
        self.cat_permis.addItems(["A", "B", "C", "D", "E", "F", "G"])
        
        # Numéro de permis
        self.num_permis = QLineEdit()
        self.num_permis.setPlaceholderText("N° de permis")
        
        # Date d'obtention
        self.date_permis = QDateEdit()
        self.date_permis.setCalendarPopup(True)
        self.date_permis.setDate(QDate.currentDate().addYears(-5))
        self.date_permis.setDisplayFormat("dd/MM/yyyy")
        
        # Ajouter les champs avec un label personnalisé
        self._add_field_to_layout(permis_fields_layout, "Catégorie", self.cat_permis, 0, 0)
        self._add_field_to_layout(permis_fields_layout, "N° de permis", self.num_permis, 0, 1)
        self._add_field_to_layout(permis_fields_layout, "Date d'obtention", self.date_permis, 0, 2)
        
        permis_layout.addWidget(permis_fields)
        self.form_layout.addWidget(self.permis_container, row, 0, 1, 3)
        row += 1
        
        # === SECTION 7: NOTES ===
        self._add_section_title("VII. Notes", row)
        row += 1
        
        self.notes = QLineEdit()
        self.notes.setPlaceholderText("Informations complémentaires...")
        self._add_field("Notes", self.notes, row, 0, 3)
        row += 1
        
        # Espace
        self.form_layout.setRowStretch(row, 1)
        
        scroll.setWidget(content)
        return scroll

    def _update_cities(self, country_name):
        """Met à jour la liste des villes en fonction du pays sélectionné"""
        # Bloquer les signaux pour éviter les boucles
        self.ville.blockSignals(True)
        
        # Vider la combo
        self.ville.clear()
        
        if country_name and country_name in CITIES_BY_COUNTRY:
            # Ajouter les villes du pays sélectionné
            cities = CITIES_BY_COUNTRY[country_name]
            self.ville.addItem("")  # Option vide
            for city in cities:
                self.ville.addItem(city)
            self.ville.setEnabled(True)
            self.ville.setPlaceholderText("Sélectionner ou saisir une ville")
        else:
            # Aucun pays sélectionné ou pays non reconnu
            self.ville.addItem("")
            self.ville.setEnabled(False)
            self.ville.setPlaceholderText("Sélectionnez d'abord un pays")
        
        self.ville.blockSignals(False)

    def _create_subscriber_fields(self):
        """Champs spécifiques souscripteur"""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        
        self.subscriber_code = QLineEdit()
        self.subscriber_code.setPlaceholderText("Généré automatiquement")
        self.subscriber_code.setObjectName("readonly")
        self.subscriber_code.setReadOnly(True)
        layout.addWidget(QLabel("Code client"), 0, 0)
        layout.addWidget(self.subscriber_code, 1, 0)
        
        self.profession = QComboBox()
        self.profession.addItems([
            "Agent commercial", "Agent de recouvrement", "Agriculteur",
            "Artisan", "Conjoint", "Employeur", "Religieux",
            "Retraité", "Salarié", "Sans emploi",
            "VRP", "Autre profession"
        ])
        self.profession.setEditable(True)
        layout.addWidget(QLabel("Profession"), 0, 1)
        self.profession.setStyleSheet(self.combo_popup_style)
        layout.addWidget(self.profession, 1, 1)
        
        self.cat_socio_prof = QComboBox()
        self.cat_socio_prof.addItems([
            "Cadre supérieur", "Profession libérale", "Employé",
            "Ouvrier", "Commerçant", "Industriel", "Sans profession"
        ])
        self.cat_socio_prof.setEditable(True)
        self.cat_socio_prof.setStyleSheet(self.combo_popup_style)
        layout.addWidget(QLabel("Catégorie socio-professionnelle"), 0, 2)
        layout.addWidget(self.cat_socio_prof, 1, 2)
        
        layout.setRowStretch(2, 1)
        
        return widget

    def _create_driver_fields(self):
        """Champs spécifiques chauffeur"""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        
        self.driver_code = QLineEdit()
        self.driver_code.setPlaceholderText("Généré automatiquement")
        self.driver_code.setObjectName("readonly")
        self.driver_code.setReadOnly(True)
        layout.addWidget(QLabel("Code chauffeur"), 0, 0)
        layout.addWidget(self.driver_code, 1, 0)
        
        self.driver_specialite = QComboBox()
        self.driver_specialite.addItems([
            "Transport de personnes", "Transport de marchandises",
            "Matières dangereuses", "Transport scolaire",
            "Transport sanitaire", "Poids lourds",
            "Véhicules de tourisme", "Autre"
        ])
        self.driver_specialite.setEditable(True)
        self.driver_specialite.setStyleSheet(self.combo_popup_style)
        layout.addWidget(QLabel("Spécialité"), 0, 1)
        layout.addWidget(self.driver_specialite, 1, 1)
        
        self.driver_experience = QComboBox()
        self.driver_experience.addItems([str(i) for i in range(0, 51)])
        self.driver_experience.setCurrentIndex(2)
        self.driver_experience.setStyleSheet(self.combo_popup_style)
        layout.addWidget(QLabel("Années d'expérience"), 0, 2)
        layout.addWidget(self.driver_experience, 1, 2)
        
        # Souscripteur lié
        lbl = QLabel("Souscripteur associé *")
        lbl.setStyleSheet("color: #dc2626; font-weight: 600;")
        layout.addWidget(lbl, 2, 0, 1, 3)
        
        self.driver_subscriber_link = QComboBox()
        self.driver_subscriber_link.setPlaceholderText("Sélectionner un souscripteur...")
        self.driver_subscriber_link.setStyleSheet(self.combo_popup_style)
        layout.addWidget(self.driver_subscriber_link, 3, 0, 1, 3)
        
        layout.setRowStretch(4, 1)
        
        return widget

    def _setup_camera_panel(self):
        """Configure le panneau caméra"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-radius: 16px;
                border: 1.5px solid #e2e8f0;
            }
        """)
        panel.setMinimumHeight(420)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # Titre
        title = QLabel("📸 CAPTURE BIOMÉTRIQUE")
        title.setStyleSheet("""
            font-size: 14px;
            font-weight: 700;
            color: #0f172a;
            text-align: center;
            padding-bottom: 8px;
            border-bottom: 2px solid #e2e8f0;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Vue caméra
        self.camera_view = QLabel("APPAREIL PHOTO")
        self.camera_view.setMinimumHeight(200)
        self.camera_view.setStyleSheet("""
            background: #0f172a;
            border-radius: 12px;
            color: #64748b;
            font-size: 14px;
            border: 3px dashed #475569;
        """)
        self.camera_view.setAlignment(Qt.AlignCenter)
        self.camera_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.camera_view)

        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self.btn_power = QPushButton("📷 Allumer")
        self.btn_power.setCursor(Qt.PointingHandCursor)
        self.btn_power.setStyleSheet("""
            QPushButton {
                background: #1e293b;
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 12px;
                border: none;
                min-height: 38px;
            }
            QPushButton:hover {
                background: #0f172a;
            }
        """)
        
        self.btn_snap = QPushButton("🎯 Capturer")
        self.btn_snap.setEnabled(False)
        self.btn_snap.setCursor(Qt.PointingHandCursor)
        self.btn_snap.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 12px;
                border: none;
                min-height: 38px;
            }
            QPushButton:hover {
                background: #059669;
            }
            QPushButton:disabled {
                opacity: 0.5;
            }
        """)
        
        self.btn_clear = QPushButton("🗑️ Effacer")
        self.btn_clear.setEnabled(False)
        self.btn_clear.setCursor(Qt.PointingHandCursor)
        self.btn_clear.setStyleSheet("""
            QPushButton {
                background: #fee2e2;
                color: #dc2626;
                padding: 10px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 12px;
                border: none;
                min-height: 38px;
            }
            QPushButton:hover {
                background: #fecaca;
            }
            QPushButton:disabled {
                opacity: 0.5;
            }
        """)
        self.btn_clear.clicked.connect(self.clear_photo)

        btn_layout.addWidget(self.btn_power)
        btn_layout.addWidget(self.btn_snap)
        btn_layout.addWidget(self.btn_clear)
        layout.addLayout(btn_layout)

        # Statut
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background: #f1f5f9;
                border-radius: 6px;
                padding: 6px 12px;
            }
        """)
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(6, 4, 6, 4)
        
        self.status_dot = QLabel()
        self.status_dot.setFixedSize(8, 8)
        self.status_dot.setStyleSheet("background: #94a3b8; border-radius: 4px;")
        
        self.status_label = QLabel("Caméra éteinte")
        self.status_label.setStyleSheet("color: #64748b; font-size: 11px;")
        
        status_layout.addWidget(self.status_dot)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        layout.addWidget(status_frame)

        # Info
        info = QLabel("💡 Allumez la caméra pour capturer une photo")
        info.setStyleSheet("color: #94a3b8; font-size: 10px; font-style: italic; text-align: center;")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

        return panel

    def _setup_footer(self, parent_layout):
        """Configure le pied de page"""
        footer = QFrame()
        footer.setFixedHeight(80)
        footer.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-bottom-left-radius: 24px;
                border-bottom-right-radius: 24px;
                border-top: 1px solid #e2e8f0;
            }
        """)
        
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(30, 0, 30, 0)
        footer_layout.setSpacing(15)

        # Progress bar
        self.progress_bar = QFrame()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setStyleSheet("""
            QFrame {
                background: #e2e8f0;
                border-radius: 2px;
            }
        """)
        self.progress_bar.setVisible(False)
        
        # Boutons
        btn_style = """
            QPushButton {
                padding: 12px 32px;
                border-radius: 10px;
                font-weight: 700;
                font-size: 14px;
                border: none;
                min-height: 44px;
                min-width: 140px;
            }
        """
        
        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.setStyleSheet(btn_style + """
            QPushButton {
                background: #f1f5f9;
                color: #475569;
            }
            QPushButton:hover {
                background: #e2e8f0;
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_save = QPushButton("💾 Enregistrer")
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet(btn_style + """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb, stop:1 #1d4ed8);
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1d4ed8, stop:1 #1e40af);
            }
        """)
        self.btn_save.clicked.connect(self.validate_and_save)

        footer_layout.addWidget(self.progress_bar)
        footer_layout.addStretch()
        footer_layout.addWidget(self.btn_cancel)
        footer_layout.addWidget(self.btn_save)
        
        parent_layout.addWidget(footer)

    # ============================================================
    # MÉTHODES UTILITAIRES
    # ============================================================
    
    def _add_section_title(self, title, row):
        """Ajoute un titre de section"""
        label = QLabel(title)
        label.setObjectName("section_title")
        self.form_layout.addWidget(label, row, 0, 1, 3)

    def _add_field(self, label_text, widget, row, col, colspan=1):
        """Ajoute un champ avec son label"""
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        
        # ✅ Un seul layout pour le container
        layout = QVBoxLayout(container)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel(label_text)
        
        if "*" in label_text:
            label.setStyleSheet("color: #1e293b; font-weight: 600;")
            required = QLabel("*")
            required.setObjectName("required")
            
            # Layout horizontal pour le label + *
            label_layout = QHBoxLayout()
            label_layout.setSpacing(2)
            label_layout.setContentsMargins(0, 0, 0, 0)
            label_layout.addWidget(label)
            label_layout.addWidget(required)
            label_layout.addStretch()
            
            layout.addLayout(label_layout)
        else:
            layout.addWidget(label)
        
        layout.addWidget(widget)
        
        self.form_layout.addWidget(container, row, col, 1, colspan)

    def _setup_connections(self):
        """Configure les connexions"""
        self.type_client.currentIndexChanged.connect(self._on_type_changed)
        self.btn_power.clicked.connect(self.toggle_camera)
        self.btn_snap.clicked.connect(self.capture_photo)

    # ============================================================
    # LOGIQUE D'AFFICHAGE
    # ============================================================
    
    def _update_visibility(self):
        """Met à jour la visibilité des champs"""
        is_driver = self.type_client.currentIndex() == 1
        is_societe = self.nature.currentIndex() == 1

        self.permis_container.setVisible(is_driver)
        # Champs à cacher pour les sociétés
        self.prenom.setVisible(not is_societe)
        self.date_naiss.setVisible(not is_societe)
        self.nationalite.setVisible(not is_societe)
        
        # Champs souscripteur (cachés pour les sociétés)
        if self.type_client.currentIndex() == 0:
            self.profession.setVisible(not is_societe)
            self.cat_socio_prof.setVisible(not is_societe)
        
        # Permis (caché pour les souscripteurs sociétés)
        if not is_driver and is_societe:
            self.cat_permis.setVisible(False)
            self.num_permis.setVisible(False)
            self.date_permis.setVisible(False)
        else:
            self.cat_permis.setVisible(True)
            self.num_permis.setVisible(True)
            self.date_permis.setVisible(True)
        self.nom.setVisible(True)

    def _add_field_to_layout(self, layout, label_text, widget, row, col, colspan=1):
        """Ajoute un champ avec label dans un layout existant"""
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        vbox = QVBoxLayout(container)
        vbox.setSpacing(4)
        vbox.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel(label_text)
        label.setStyleSheet("color: #1e293b; font-weight: 500; font-size: 12px;")
        vbox.addWidget(label)
        vbox.addWidget(widget)
        
        layout.addWidget(container, row, col, 1, colspan)
    # ============================================================
    # CHARGEMENT DES DONNÉES
    # ============================================================

    def _load_subscribers(self):
        """Charge les souscripteurs existants pour la liste déroulante"""
        try:
            # ✅ Vérifier que le widget existe
            if not hasattr(self, 'driver_subscriber_link'):
                print("⚠️ driver_subscriber_link n'existe pas encore")
                return
            
            # ✅ Récupérer uniquement les contacts de type "Souscripteur"
            subscribers = []
            
            # Essayer différentes méthodes pour récupérer les souscripteurs
            if hasattr(self.controller, 'contacts'):
                if hasattr(self.controller.contacts, 'get_all_contacts'):
                    subscribers = self.controller.contacts.get_all_contacts("Souscripteur")
            
            # ✅ Remplir la combo box
            self.driver_subscriber_link.clear()
            self.driver_subscriber_link.addItem("Sélectionner un souscripteur...", None)
            
            for sub in subscribers:
                nom = getattr(sub, 'nom', '')
                prenom = getattr(sub, 'prenom', '')
                display = f"{nom} {prenom}".strip()
                if not display:
                    display = getattr(sub, 'code_client', f"ID: {getattr(sub, 'id', '')}")
                self.driver_subscriber_link.addItem(display, getattr(sub, 'id', None))
            
            if len(subscribers) == 0:
                self.driver_subscriber_link.addItem("Aucun souscripteur trouvé", None)
            
            print(f"✅ {len(subscribers)} souscripteurs chargés")
                    
        except Exception as e:
            print(f"❌ Erreur chargement souscripteurs: {e}")
            import traceback
            traceback.print_exc()
            if hasattr(self, 'driver_subscriber_link'):
                self.driver_subscriber_link.clear()
                self.driver_subscriber_link.addItem("Erreur de chargement", None)


    def _load_subscribers_for_driver(self):
        """Alias pour _load_subscribers"""
        self._load_subscribers()

    def _load_data(self):
        """Charge les données existantes"""
        if not self.contact_data:
            return
        
        # ✅ Déterminer si c'est un chauffeur ou un souscripteur
        is_driver = hasattr(self.contact_data, 'type_client') and self.contact_data.type_client == "Chauffeur"

        data_obj = self.contact_data.data if is_driver else self.contact_data
        
        # --- SECTION 1: TYPE DE CLIENT ---
        if hasattr(self.contact_data, 'type_client'):
            idx = self.type_client.findText(self.contact_data.type_client)
            if idx >= 0:
                self.type_client.setCurrentIndex(idx)
        
        self._on_type_changed(self.type_client.currentIndex())
        
        # --- SECTION 2: ADMINISTRATION ---
        if hasattr(self.contact_data, 'nature'):
            idx = self.nature.findText(self.contact_data.nature)
            if idx >= 0:
                self.nature.setCurrentIndex(idx)
        
        # ✅ Gestion du statut (pour Contact et Driver)
        if hasattr(self.contact_data, 'statut'):
            idx = self.statut.findText(self.contact_data.statut)
            if idx >= 0:
                self.statut.setCurrentIndex(idx)
        
        if hasattr(self.contact_data, 'charge_clientele'):
            self.charge_client.setText(self.contact_data.charge_clientele or '')
        
        self._update_visibility()
        
        # --- SECTION 3: IDENTITÉ ---
        self.nom.setText(getattr(self.contact_data, 'nom', ''))
        self.prenom.setText(getattr(self.contact_data, 'prenom', ''))
        
        if hasattr(self.contact_data, 'civilite'):
            idx = self.civilite.findText(self.contact_data.civilite)
            if idx >= 0:
                self.civilite.setCurrentIndex(idx)
        
        if hasattr(self.contact_data, 'date_naissance') and self.contact_data.date_naissance:
            self.date_naiss.setDate(self._to_qdate(self.contact_data.date_naissance))
        
        if hasattr(self.contact_data, 'nationalite') and self.contact_data.nationalite:
            # Trouver l'index du pays dans la combo
            index = self.nationalite.findText(self.contact_data.nationalite)
            if index >= 0:
                self.nationalite.setCurrentIndex(index)
            else:
                # Si le pays n'existe pas dans la liste, l'ajouter
                self.nationalite.addItem(self.contact_data.nationalite)
                self.nationalite.setCurrentText(self.contact_data.nationalite)

        self.num_contribuable.setText(getattr(self.contact_data, 'num_contribuable', ''))
        
        # --- SECTION 5: COORDONNÉES ---
        self.tel.setText(getattr(self.contact_data, 'telephone', ''))
        self.fax.setText(getattr(self.contact_data, 'fax', ''))
        self.email.setText(getattr(self.contact_data, 'email', ''))
        self.adresse.setText(getattr(self.contact_data, 'adresse', ''))
        if hasattr(self.contact_data, 'ville') and self.contact_data.ville:
            # Forcer la mise à jour des villes
            self._update_cities(self.nationalite.currentText())
            
            # Sélectionner la ville
            index = self.ville.findText(self.contact_data.ville)
            if index >= 0:
                self.ville.setCurrentIndex(index)
            else:
                self.ville.addItem(self.contact_data.ville)
                self.ville.setCurrentText(self.contact_data.ville)
        
        # --- SECTION 6: PERMIS ---
        self.num_permis.setText(getattr(self.contact_data, 'num_permis', ''))
        if hasattr(self.contact_data, 'cat_permis'):
            idx = self.cat_permis.findText(self.contact_data.cat_permis or 'B')
            if idx >= 0:
                self.cat_permis.setCurrentIndex(idx)
        if hasattr(self.contact_data, 'date_permis') and self.contact_data.date_permis:
            self.date_permis.setDate(self._to_qdate(self.contact_data.date_permis))
        
        # --- SECTION 7: NOTES ---
        self.notes.setText(getattr(self.contact_data, 'notes', ''))
        
        # --- SECTION 4: INFORMATIONS SPÉCIFIQUES ---
        if not is_driver:
            # ✅ Souscripteur
            if hasattr(self, 'subscriber_code'):
                self.subscriber_code.setText(getattr(self.contact_data, 'code_client', ''))
            
            if hasattr(self, 'profession'):
                profession = getattr(self.contact_data, 'profession', '')
                idx = self.profession.findText(profession)
                if idx >= 0:
                    self.profession.setCurrentIndex(idx)
                elif profession:
                    self.profession.setCurrentText(profession)
            
            if hasattr(self, 'cat_socio_prof'):
                cat_socio = getattr(self.contact_data, 'cat_socio_prof', '')
                idx = self.cat_socio_prof.findText(cat_socio)
                if idx >= 0:
                    self.cat_socio_prof.setCurrentIndex(idx)
                elif cat_socio:
                    self.cat_socio_prof.setCurrentText(cat_socio)
        else:
            # ✅ Chauffeur
            if is_driver:
                # ✅ Chauffeur
                if hasattr(self, 'driver_code'):
                    code = getattr(self.contact_data, 'code_chauffeur', '')
                    if code:
                        self.driver_code.setText(code)
                    else:
                        # Si pas de code, afficher un placeholder
                        self.driver_code.setText("Généré automatiquement")
            
            if hasattr(self, 'driver_specialite'):
                specialite = getattr(self.contact_data, 'specialite', '')
                idx = self.driver_specialite.findText(specialite)
                if idx >= 0:
                    self.driver_specialite.setCurrentIndex(idx)
                elif specialite:
                    self.driver_specialite.setCurrentText(specialite)
            
            if hasattr(self, 'driver_experience'):
                experience = str(getattr(self.contact_data, 'annees_experience', 0))
                idx = self.driver_experience.findText(experience)
                if idx >= 0:
                    self.driver_experience.setCurrentIndex(idx)
                else:
                    self.driver_experience.setCurrentText(experience)
            
            # Charger le souscripteur associé
            if hasattr(self, 'driver_subscriber_link'):
                subscriber_id = getattr(self.contact_data, 'subscriber_id', None)
                if subscriber_id:
                    for i in range(self.driver_subscriber_link.count()):
                        if self.driver_subscriber_link.itemData(i) == subscriber_id:
                            self.driver_subscriber_link.setCurrentIndex(i)
                            break
    # ============================================================
    # CAMÉRA
    # ============================================================
    
    def toggle_camera(self):
        """Active/désactive la caméra"""
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.timer.start(30)
                self.btn_power.setText("🔴 Éteindre")
                self.btn_power.setStyleSheet("""
                    QPushButton {
                        background: #ef4444;
                        color: white;
                        padding: 10px;
                        border-radius: 8px;
                        font-weight: 600;
                        font-size: 12px;
                        border: none;
                        min-height: 38px;
                    }
                    QPushButton:hover {
                        background: #dc2626;
                    }
                """)
                self.btn_snap.setEnabled(True)
                self.camera_view.setStyleSheet("""
                    background: #0f172a;
                    border-radius: 12px;
                    border: 3px solid #10b981;
                """)
                self.status_dot.setStyleSheet("background: #10b981; border-radius: 4px;")
                self.status_label.setText("Caméra active")
                self.status_label.setStyleSheet("color: #10b981; font-size: 11px; font-weight: 600;")
            else:
                QMessageBox.critical(self, "Erreur", "Impossible d'accéder à la webcam.")
                self.cap = None
        else:
            self.stop_camera()

    def stop_camera(self):
        """Arrête la caméra"""
        self.timer.stop()
        if self.cap:
            self.cap.release()
        self.cap = None
        
        self.camera_view.clear()
        self.camera_view.setText("APPAREIL PHOTO")
        self.camera_view.setStyleSheet("""
            background: #0f172a;
            border-radius: 12px;
            color: #64748b;
            font-size: 14px;
            border: 3px dashed #475569;
        """)
        self.btn_power.setText("📷 Allumer")
        self.btn_power.setStyleSheet("""
            QPushButton {
                background: #1e293b;
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 12px;
                border: none;
                min-height: 38px;
            }
            QPushButton:hover {
                background: #0f172a;
            }
        """)
        self.btn_snap.setEnabled(False)
        self.status_dot.setStyleSheet("background: #94a3b8; border-radius: 4px;")
        self.status_label.setText("Caméra éteinte")
        self.status_label.setStyleSheet("color: #64748b; font-size: 11px;")

    def _update_frame(self):
        """Met à jour le flux vidéo"""
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            img = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
            self.camera_view.setPixmap(QPixmap.fromImage(img).scaled(
                self.camera_view.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            ))

    def capture_photo(self):
        """Capture une photo"""
        ret, frame = self.cap.read()
        if ret:
            self.captured_image = frame
            self.stop_camera()
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            img = QImage(frame_rgb.data, w, h, ch * w, QImage.Format_RGB888)
            self.camera_view.setPixmap(QPixmap.fromImage(img).scaled(
                self.camera_view.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            ))
            self.camera_view.setStyleSheet("""
                border: 4px solid #10b981;
                border-radius: 12px;
                background: #0f172a;
            """)
            self.btn_clear.setEnabled(True)
            self.status_dot.setStyleSheet("background: #2563eb; border-radius: 4px;")
            self.status_label.setText("Photo capturée ✅")
            self.status_label.setStyleSheet("color: #2563eb; font-size: 11px; font-weight: 600;")
            QMessageBox.information(self, "Succès", "📸 Photo capturée avec succès !")

    def clear_photo(self):
        """Efface la photo"""
        self.captured_image = None
        self.camera_view.clear()
        self.camera_view.setText("APPAREIL PHOTO")
        self.camera_view.setStyleSheet("""
            background: #0f172a;
            border-radius: 12px;
            color: #64748b;
            font-size: 14px;
            border: 3px dashed #475569;
        """)
        self.btn_clear.setEnabled(False)
        self.status_dot.setStyleSheet("background: #94a3b8; border-radius: 4px;")
        self.status_label.setText("Photo effacée")
        self.status_label.setStyleSheet("color: #64748b; font-size: 11px;")

    def _on_type_changed(self, index):
        """Gère le changement de type de client"""
        self.specific_stack.setCurrentIndex(index)
        self._update_visibility()
        
        # ✅ Recharger les souscripteurs quand on passe en mode Chauffeur
        if index == 1:  # Chauffeur
            self._load_subscribers()
        
        # Mettre à jour le placeholder
        if index == 0:  # Souscripteur
            self.nom.setPlaceholderText("Nom / Raison sociale")
            self.nom.setVisible(True)
        else:  # Chauffeur
            self.nom.setPlaceholderText("Nom complet du chauffeur")
            self.nom.setVisible(True)
            
    # ============================================================
    # GESTION DE LA FENÊTRE
    # ============================================================
    
    def toggle_maximize(self):
        """Bascule plein écran"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.isMaximized():
            child = self.childAt(event.pos())
            if not isinstance(child, (QPushButton, QLineEdit, QComboBox, QDateEdit, QListWidget)):
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_position') and not self.isMaximized():
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if hasattr(self, 'drag_position'):
            delattr(self, 'drag_position')

    # ============================================================
    # VALIDATION ET SAUVEGARDE
    # ============================================================

    def validate_and_save(self):
        """Valide et sauvegarde"""
        errors = self._validate()
        
        if errors:
            QMessageBox.warning(self, "⚠️ Champs obligatoires",
                f"Veuillez corriger les erreurs suivantes :\n\n" + "\n".join(errors))
            return
        
        try:
            data = self._get_data()
            
            # ✅ Déterminer la table de destination en fonction du type
            if self.type_client.currentText() == "Chauffeur":
                # ✅ Sauvegarder dans Driver
                if self.mode == "edit" and self.contact_data:
                    # Pour l'édition d'un chauffeur
                    if hasattr(self.controller, 'drivers'):
                        result = self.controller.drivers.update_driver(self.contact_data.id, data)
                    else:
                        result = self.controller.contacts.update_driver(self.contact_data.id, data)
                else:
                    # Création d'un nouveau chauffeur
                    if hasattr(self.controller, 'drivers'):
                        result = self.controller.drivers.create_driver(data)
                    else:
                        result = self.controller.contacts.create_driver(data)
            else:
                # ✅ Sauvegarder dans Contact (Souscripteur)
                if self.mode == "edit" and self.contact_data:
                    result = self.controller.contacts.update_contact(self.contact_data.id, data)
                else:
                    result = self.controller.contacts.create_contact(data)
            
            # ✅ Vérifier le résultat (objet, success, message)
            if result and result[1]:  # (objet, success, message)
                self.contact_saved.emit(result[0])
                QMessageBox.information(self, "✅ Succès", result[2])
                self.accept()
            else:
                QMessageBox.critical(self, "❌ Erreur", result[2] if result else "Erreur inconnue")
                    
        except Exception as e:
            QMessageBox.critical(self, "❌ Erreur", f"Erreur : {str(e)}")
            import traceback
            traceback.print_exc()

    def _validate(self):
        """Valide le formulaire"""
        errors = []
        
        if not self.nom.text().strip():
            errors.append("❌ Nom / Raison sociale obligatoire")
        
        if self.type_client.currentText() == "Chauffeur":
            if not self.driver_subscriber_link.currentData():
                errors.append("❌ Un chauffeur doit être lié à un souscripteur")
            if not self.num_permis.text().strip():
                errors.append("❌ N° de permis obligatoire pour un chauffeur")
        
        return errors

    # def _get_data(self):
    #     """Récupère les données du formulaire"""
    #     is_driver = self.type_client.currentText() == "Chauffeur"
        
    #     # ✅ Données communes à tous les types
    #     data = {
    #         # --- SECTION 1: TYPE DE CLIENT ---
    #         "type_client": self.type_client.currentText(),
            
    #         # --- SECTION 2: ADMINISTRATION ---
    #         "statut": self.statut.currentText(),
    #         "nature": self.nature.currentText(),
    #         "charge_clientele": self.charge_client.text().strip(),
            
    #         # --- SECTION 3: IDENTITÉ ---
    #         "civilite": self.civilite.currentText(),
    #         "nom": self.nom.text().strip().upper(),
    #         "prenom": self.prenom.text().strip().title() if self.prenom.isVisible() else "",
    #         "date_naissance": self.date_naiss.date().toPython() if self.date_naiss.isVisible() else None,
    #         "nationalite": self.nationalite.currentText().strip(),
    #         "num_contribuable": self.num_contribuable.text().strip(),
            
    #         # --- SECTION 5: COORDONNÉES ---
    #         "telephone": self.tel.text().strip(),
    #         "fax": self.fax.text().strip(),
    #         "email": self.email.text().strip().lower(),
    #         "adresse": self.adresse.text().strip(),
    #         "ville": self.ville.currentText().strip(),
            
    #         # --- SECTION 6: PERMIS (commun) ---
    #         "cat_permis": self.cat_permis.currentText() if self.cat_permis.isVisible() else "",
    #         "num_permis": self.num_permis.text().strip() if self.num_permis.isVisible() else "",
    #         "date_permis": self.date_permis.date().toPython() if self.date_permis.isVisible() else None,
            
    #         # --- SECTION 7: NOTES ---
    #         "notes": self.notes.text().strip(),
    #     }
        
    #     # ✅ SECTION 4: INFORMATIONS SPÉCIFIQUES
    #     if not is_driver:
    #         # Souscripteur
    #         data.update({
    #             "code_client": self.subscriber_code.text().strip() if hasattr(self, 'subscriber_code') else "",
    #             "profession": self.profession.currentText() if hasattr(self, 'profession') and self.profession.isVisible() else "",
    #             "cat_socio_prof": self.cat_socio_prof.currentText() if hasattr(self, 'cat_socio_prof') and self.cat_socio_prof.isVisible() else "",
    #         })
    #     else:
    #         # Chauffeur
    #         data.update({
    #             "code_chauffeur": self.driver_code.text().strip() if hasattr(self, 'driver_code') else "",
    #             "specialite": self.driver_specialite.currentText() if hasattr(self, 'driver_specialite') else "",
    #             "annees_experience": int(self.driver_experience.currentText()) if hasattr(self, 'driver_experience') and self.driver_experience.currentText().isdigit() else 0,
    #             "subscriber_id": self.driver_subscriber_link.currentData() if hasattr(self, 'driver_subscriber_link') else None
    #         })
        
    #     return data

    def _get_data(self):
        """Récupère les données du formulaire"""
        is_driver = self.type_client.currentText() == "Chauffeur"
        
        # ✅ Données communes à tous les types
        data = {
            # --- SECTION 1: TYPE DE CLIENT ---
            "type_client": self.type_client.currentText(),
            
            # --- SECTION 2: ADMINISTRATION ---
            "statut": self.statut.currentText(),
            "nature": self.nature.currentText(),
            "charge_clientele": self.charge_client.text().strip(),
            
            # --- SECTION 3: IDENTITÉ ---
            "civilite": self.civilite.currentText(),
            "nom": self.nom.text().strip().upper(),
            "prenom": self.prenom.text().strip().title() if self.prenom.isVisible() else "",
            "date_naissance": self.date_naiss.date().toPython() if self.date_naiss.isVisible() else None,
            "nationalite": self.nationalite.currentText().strip(),
            "num_contribuable": self.num_contribuable.text().strip(),
            
            # --- SECTION 5: COORDONNÉES ---
            "telephone": self.tel.text().strip(),
            "fax": self.fax.text().strip(),
            "email": self.email.text().strip().lower(),
            "adresse": self.adresse.text().strip(),
            "ville": self.ville.currentText().strip(),
            
            # --- SECTION 6: PERMIS (commun) ---
            "cat_permis": self.cat_permis.currentText() if self.cat_permis.isVisible() else "",
            "num_permis": self.num_permis.text().strip() if self.num_permis.isVisible() else "",
            "date_permis": self.date_permis.date().toPython() if self.date_permis.isVisible() else None,
            
            # --- SECTION 7: NOTES ---
            "notes": self.notes.text().strip(),
        }
        
        # ✅ SECTION 4: INFORMATIONS SPÉCIFIQUES
        if not is_driver:
            # Souscripteur
            data.update({
                "code_client": self.subscriber_code.text().strip() if hasattr(self, 'subscriber_code') else "",
                "profession": self.profession.currentText() if hasattr(self, 'profession') and self.profession.isVisible() else "",
                "cat_socio_prof": self.cat_socio_prof.currentText() if hasattr(self, 'cat_socio_prof') and self.cat_socio_prof.isVisible() else "",
            })
        else:
            # ✅ Chauffeur - Générer un code unique avec UUID
            code_chauffeur = self.driver_code.text().strip() if hasattr(self, 'driver_code') else ""
            
            # Si le code est vide ou "Généré automatiquement", créer un UUID
            if not code_chauffeur or code_chauffeur == "Généré automatiquement":
                # Récupérer les 3 premières lettres du nom pour plus de lisibilité
                nom_prefix = self.nom.text().strip().upper()[:3] if self.nom.text().strip() else "DRV"
                code_chauffeur = f"{nom_prefix}-{uuid.uuid4().hex[:8].upper()}"
            
            data.update({
                "code_chauffeur": code_chauffeur,
                "specialite": self.driver_specialite.currentText() if hasattr(self, 'driver_specialite') else "",
                "annees_experience": int(self.driver_experience.currentText()) if hasattr(self, 'driver_experience') and self.driver_experience.currentText().isdigit() else 0,
                "subscriber_id": self.driver_subscriber_link.currentData() if hasattr(self, 'driver_subscriber_link') else None
            })
        
        return data

    def _to_qdate(self, dt):
        """Convertit datetime en QDate"""
        if dt is None:
            return QDate.currentDate()
        if isinstance(dt, datetime):
            return QDate(dt.year, dt.month, dt.day)
        if hasattr(dt, 'year'):
            return QDate(dt.year, dt.month, dt.day)
        return QDate.currentDate()

    def closeEvent(self, event):
        """Gère la fermeture de la fenêtre"""
        # ✅ Arrêter la caméra si elle est active
        if hasattr(self, 'cap') and self.cap is not None:
            self.stop_camera()
        
        # ✅ Arrêter le timer
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        
        event.accept()