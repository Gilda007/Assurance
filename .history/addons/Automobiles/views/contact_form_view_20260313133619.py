import cv2
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QComboBox, QPushButton, QLabel, QFrame, QGridLayout, 
                             QScrollArea, QDateEdit, QMessageBox, QWidget)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QImage, QPixmap, QColor, QIcon

class ContactForm(QDialog):
    def __init__(self, controller, parent=None, contact_data=None):
        super().__init__(parent)
        # Fenêtre sans bordure avec coins arrondis gérés par le style
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.controller = controller
        self.contact_data = contact_data
        
        # Logique Caméra
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.captured_image = None

        self.setup_ui()

    # def setup_ui(self):
    #     self.setMinimumSize(1200, 850)
    #     main_layout = QVBoxLayout(self)
    #     main_layout.setContentsMargins(10, 10, 10, 10)

    #     # --- CONTENEUR GLOBAL ---
    #     self.container = QFrame()
    #     self.container.setObjectName("MainContainer")
    #     self.container.setStyleSheet("""
    #         #MainContainer {
    #             background-color: #ffffff;
    #             border-radius: 20px;
    #             border: 1px solid #e2e8f0;
    #         }
    #         .Card {
    #             background-color: #f8fafc;
    #             border: 1px solid #f1f5f9;
    #             border-radius: 15px;
    #         }
    #         .SectionTitle {
    #             color: #1e293b;
    #             font-weight: 800;
    #             font-size: 14px;
    #             padding-bottom: 5px;
    #             border-bottom: 2px solid #3b82f6;
    #         }
    #         QLabel { color: #64748b; font-weight: 700; font-size: 11px; text-transform: uppercase; }
            
    #         QLineEdit, QComboBox, QDateEdit {
    #             background-color: #ffffff;
    #             border: 1px solid #cbd5e1;
    #             border-radius: 8px;
    #             padding: 10px;
    #             color: #1e293b;
    #             font-size: 13px;
    #         }
    #         QLineEdit:focus { border: 2px solid #3b82f6; }
    #     """)
        
    #     container_layout = QVBoxLayout(self.container)
    #     container_layout.setContentsMargins(30, 30, 30, 30)

    #     # --- BARRE DE TITRE ---
    #     header = QHBoxLayout()
    #     title_icon = QLabel("👤")
    #     title_icon.setStyleSheet("font-size: 24px; border: none;")
    #     header.addWidget(title_icon)
        
    #     v_title = QVBoxLayout()
    #     lbl_main = QLabel("Nouveau Dossier Client")
    #     lbl_main.setStyleSheet("font-size: 20px; color: #1e293b; font-weight: 900; border: none; text-transform: none;")
    #     lbl_sub = QLabel("Complétez les informations pour la base de données")
    #     lbl_sub.setStyleSheet("font-size: 12px; color: #94a3b8; font-weight: normal; border: none; text-transform: none;")
    #     v_title.addWidget(lbl_main)
    #     v_title.addWidget(lbl_sub)
    #     header.addLayout(v_title)
    #     header.addStretch()
        
    #     btn_exit = QPushButton("✕")
    #     btn_exit.setFixedSize(35, 35)
    #     btn_exit.setStyleSheet("background: #f1f5f9; border-radius: 17px; color: #64748b; font-weight: bold;")
    #     btn_exit.clicked.connect(self.reject)
    #     header.addWidget(btn_exit)
    #     container_layout.addLayout(header)

    #     # --- CORPS PRINCIPAL ---
    #     body = QHBoxLayout()
    #     body.setSpacing(30)

    #     # A. COLONNE GAUCHE : FORMULAIRE
    #     scroll = QScrollArea()
    #     scroll.setWidgetResizable(True)
    #     scroll.setFrameShape(QFrame.NoFrame)
        
    #     form_wrapper = QWidget()
    #     self.grid = QGridLayout(form_wrapper)
    #     self.grid.setSpacing(20)

    #     # Bloc 1 : Statut
    #     self._add_section_header("I. Statut du Dossier", 0)
    #     self.type_client = QComboBox(); self.type_client.addItems(["Standard", "VIP", "Premium"])
    #     self.nature = QComboBox(); self.nature.addItems(["Client", "Prospect", "Entreprise"])
    #     self.charge = QLineEdit(); self.charge.setPlaceholderText("Nom du gestionnaire")
        
    #     self._add_smart_field("Catégorie Client", self.type_client, 1, 0)
    #     self._add_smart_field("Nature Relation", self.nature, 1, 1)
    #     self._add_smart_field("Chargé de Clientèle", self.charge, 1, 2)

    #     # Bloc 2 : Identité
    #     self._add_section_header("II. Informations Identitaires", 2)
    #     self.civilite = QComboBox(); self.civilite.addItems(["M.", "Mme", "Mlle"])
    #     self.nom = QLineEdit(); self.prenom = QLineEdit()
    #     self.date_naiss = QDateEdit(); self.date_naiss.setCalendarPopup(True)
        
    #     self._add_smart_field("Civilité", self.civilite, 3, 0)
    #     self._add_smart_field("Nom / Raison Sociale", self.nom, 3, 1, colspan=2)
    #     self._add_smart_field("Prénoms", self.prenom, 4, 0, colspan=2)
    #     self._add_smart_field("Date de Naissance", self.date_naiss, 4, 2)

    #     # Bloc 3 : Contact & Localisation
    #     self._add_section_header("III. Contact & Localisation", 5)
    #     self.tel = QLineEdit(); self.email = QLineEdit(); self.adresse = QLineEdit()
    #     self.ville = QLineEdit(); self.pays = QLineEdit()
        
    #     self._add_smart_field("Mobile / WhatsApp", self.tel, 6, 0)
    #     self._add_smart_field("Email Personnel", self.email, 6, 1, colspan=2)
    #     self._add_smart_field("Adresse Complète", self.adresse, 7, 0, colspan=3)
    #     self._add_smart_field("Quartier / Ville", self.ville, 8, 0, colspan=2)
    #     self._add_smart_field("Nationalité", self.pays, 8, 2)

    #     scroll.setWidget(form_wrapper)
    #     body.addWidget(scroll, 7)

    #     # B. COLONNE DROITE : BIOMÉTRIE
    #     cam_card = QFrame()
    #     cam_card.setProperty("class", "Card")
    #     cam_vbox = QVBoxLayout(cam_card)
    #     cam_vbox.setContentsMargins(20, 20, 20, 20)

    #     self.lbl_cam = QLabel("APPAREIL PHOTO")
    #     self.lbl_cam.setFixedSize(340, 255)
    #     self.lbl_cam.setStyleSheet("background: #0f172a; border-radius: 12px; color: #475569;")
    #     self.lbl_cam.setAlignment(Qt.AlignCenter)
        
    #     cam_vbox.addWidget(QLabel("📸 Capture Biométrique"), alignment=Qt.AlignCenter)
    #     cam_vbox.addWidget(self.lbl_cam)
        
    #     self.btn_power = QPushButton("Allumer la Caméra")
    #     self.btn_power.setStyleSheet("background: #1e293b; color: white; padding: 12px; border-radius: 8px; font-weight: bold;")
        
    #     self.btn_snap = QPushButton("Capturer")
    #     self.btn_snap.setEnabled(False)
    #     self.btn_snap.setStyleSheet("background: #10b981; color: white; padding: 12px; border-radius: 8px; font-weight: bold;")

    #     cam_vbox.addWidget(self.btn_power)
    #     cam_vbox.addWidget(self.btn_snap)
    #     cam_vbox.addStretch()

    #     body.addWidget(cam_card, 3)
    #     container_layout.addLayout(body)

    #     # --- PIED DE PAGE ---
    #     footer = QHBoxLayout()
    #     btn_cancel = QPushButton("Annuler")
    #     btn_cancel.setStyleSheet("color: #64748b; font-weight: bold; border: none;")
        
    #     self.btn_save = QPushButton("Enregistrer la Fiche")
    #     self.btn_save.setFixedSize(220, 45)
    #     self.btn_save.setStyleSheet("""
    #         QPushButton {
    #             background: #2563eb; color: white; border-radius: 10px; font-weight: 800; font-size: 13px;
    #         }
    #         QPushButton:hover { background: #1d4ed8; }
    #     """)

    #     footer.addStretch()
    #     footer.addWidget(btn_cancel)
    #     footer.addWidget(self.btn_save)
    #     container_layout.addLayout(footer)

    #     main_layout.addWidget(self.container)

    #     # Connexions
    #     self.btn_power.clicked.connect(self.toggle_cam)
    #     self.btn_snap.clicked.connect(self.capture_photo)

    def setup_ui(self):
        self.setMinimumSize(1250, 850)
        main_layout = QVBoxLayout(self)
        
        # --- CONTENEUR PRINCIPAL ---
        self.container = QFrame()
        self.container.setObjectName("MainContainer")
        self.container.setStyleSheet("""
            #MainContainer { background-color: #ffffff; border-radius: 20px; border: 1px solid #e2e8f0; }
            .SectionCard { background-color: #f8fafc; border-radius: 12px; border: 1px solid #f1f5f9; padding: 10px; }
            .SectionTitle { color: #2563eb; font-weight: 800; font-size: 13px; text-transform: uppercase; margin-bottom: 10px; }
            QLabel { color: #64748b; font-weight: 700; font-size: 11px; }
            QLineEdit, QComboBox, QDateEdit { background-color: white; border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px; }
            QLineEdit:focus { border: 2px solid #3b82f6; }
        """)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(30, 30, 30, 30)

        # --- TITRE ---
        header = QLabel("📋 CRÉATION DE DOSSIER CLIENT")
        header.setStyleSheet("font-size: 22px; color: #1e293b; font-weight: 900; margin-bottom: 10px;")
        container_layout.addWidget(header)

        # --- CORPS (Formulaire | Camera) ---
        body = QHBoxLayout()
        body.setSpacing(30)

        # GAUCHE : FORMULAIRE DÉFILANT
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        # Le wrapper qui contiendra tous les blocs
        form_wrapper = QWidget()
        self.grid = QGridLayout(form_wrapper)
        self.grid.setSpacing(25)
        self.grid.setContentsMargins(0, 0, 15, 0)

        # --- RÉPARTITION DES 17 CHAMPS ---

        # Bloc 1 : Statut (4 champs)
        self._add_section_header("I. Administration & Statut", 0)
        self.type_client = QComboBox(); self.type_client.addItems(["Standard", "VIP"])
        self.nature = QComboBox(); self.nature.addItems(["Client", "Prospect"])
        self.charge_client = QLineEdit()
        self.redacteur = QLineEdit()
        
        self._add_smart_field("Type Client", self.type_client, 1, 0)
        self._add_smart_field("Nature", self.nature, 1, 1)
        self._add_smart_field("Chargé Clientèle", self.charge_client, 2, 0)
        self._add_smart_field("Rédacteur Production", self.redacteur, 2, 1)

        # Bloc 2 : État Civil (6 champs)
        self._add_section_header("II. État Civil & Identité", 3)
        self.civilite = QComboBox(); self.civilite.addItems(["M.", "Mme", "Mlle"])
        self.nom = QLineEdit(); self.prenom = QLineEdit()
        self.date_naiss = QDateEdit(); self.date_naiss.setCalendarPopup(True)
        self.nationalite = QLineEdit()
        self.num_contribuable = QLineEdit()

        self._add_smart_field("Civilité", self.civilite, 4, 0)
        self._add_smart_field("Nom / Raison Sociale", self.nom, 4, 1, colspan=2)
        self._add_smart_field("Prénoms", self.prenom, 5, 0, colspan=2)
        self._add_smart_field("Date Naissance", self.date_naiss, 5, 2)
        self._add_smart_field("Nationalité", self.nationalite, 6, 0)
        self._add_smart_field("N° Contribuable", self.num_contribuable, 6, 1, colspan=2)

        # Bloc 3 : Contact & Localisation (4 champs)
        self._add_section_header("III. Coordonnées & Contact", 7)
        self.tel = QLineEdit(); self.fax = QLineEdit(); self.email = QLineEdit()
        self.adresse = QLineEdit()

        self._add_smart_field("Téléphone", self.tel, 8, 0)
        self._add_smart_field("Fax", self.fax, 8, 1)
        self._add_smart_field("Email", self.email, 8, 2)
        self._add_smart_field("Adresse Complète", self.adresse, 9, 0, colspan=3)

        # Bloc 4 : Permis (3 champs)
        self._add_section_header("IV. Permis de Conduire", 10)
        self.cat_permis = QComboBox(); self.cat_permis.addItems(["A", "B", "C", "D"])
        self.date_permis = QDateEdit(); self.date_permis.setCalendarPopup(True)
        self.num_permis = QLineEdit()

        self._add_smart_field("Catégorie", self.cat_permis, 11, 0)
        self._add_smart_field("N° de Permis", self.num_permis, 11, 1)
        self._add_smart_field("Date Obtention", self.date_permis, 11, 2)

        scroll.setWidget(form_wrapper)
        body.addWidget(scroll, 7) # 70% de largeur

        # --- DROITE : CAMERA (30% de largeur) ---
         cam_card = QFrame()
    #     cam_card.setProperty("class", "Card")
    #     cam_vbox = QVBoxLayout(cam_card)
    #     cam_vbox.setContentsMargins(20, 20, 20, 20)

    #     self.lbl_cam = QLabel("APPAREIL PHOTO")
    #     self.lbl_cam.setFixedSize(340, 255)
    #     self.lbl_cam.setStyleSheet("background: #0f172a; border-radius: 12px; color: #475569;")
    #     self.lbl_cam.setAlignment(Qt.AlignCenter)
        
    #     cam_vbox.addWidget(QLabel("📸 Capture Biométrique"), alignment=Qt.AlignCenter)
    #     cam_vbox.addWidget(self.lbl_cam)
        
    #     self.btn_power = QPushButton("Allumer la Caméra")
    #     self.btn_power.setStyleSheet("background: #1e293b; color: white; padding: 12px; border-radius: 8px; font-weight: bold;")
        
    #     self.btn_snap = QPushButton("Capturer")
    #     self.btn_snap.setEnabled(False)
    #     self.btn_snap.setStyleSheet("background: #10b981; color: white; padding: 12px; border-radius: 8px; font-weight: bold;")

    #     cam_vbox.addWidget(self.btn_power)
    #     cam_vbox.addWidget(self.btn_snap)
    #     cam_vbox.addStretch()

    #     body.addWidget(cam_card, 3)
    #     container_layout.addLayout(body)

    #     # --- PIED DE PAGE ---
    #     footer = QHBoxLayout()
    #     btn_cancel = QPushButton("Annuler")
    #     btn_cancel.setStyleSheet("color: #64748b; font-weight: bold; border: none;")
        
    #     self.btn_save = QPushButton("Enregistrer la Fiche")
    #     self.btn_save.setFixedSize(220, 45)
    #     self.btn_save.setStyleSheet("""
    #         QPushButton {
    #             background: #2563eb; color: white; border-radius: 10px; font-weight: 800; font-size: 13px;
    #         }
    #         QPushButton:hover { background: #1d4ed8; }
    #     """)

    #     footer.addStretch()
    #     footer.addWidget(btn_cancel)
    #     footer.addWidget(self.btn_save)
    #     container_layout.addLayout(footer)

    #     main_layout.addWidget(self.container)

    #     # Connexions
    #     self.btn_power.clicked.connect(self.toggle_cam)
    #     self.btn_snap.clicked.connect(self.capture_photo)

        container_layout.addLayout(body)

        # --- FOOTER ---
        footer = QHBoxLayout()
        self.btn_save = QPushButton("💾 Enregistrer la Fiche")
        self.btn_save.setFixedSize(250, 45)
        self.btn_save.setStyleSheet("background: #2563eb; color: white; border-radius: 10px; font-weight: 800;")
        footer.addStretch()
        footer.addWidget(self.btn_save)
        container_layout.addLayout(footer)

        main_layout.addWidget(self.container)

    def _add_section_header(self, title, row):
        lbl = QLabel(title)
        lbl.setProperty("class", "SectionTitle")
        self.grid.addWidget(lbl, row, 0, 1, 3)

    def _add_smart_field(self, label, widget, row, col, colspan=1):
        v = QVBoxLayout()
        v.setSpacing(5)
        l = QLabel(label)
        v.addWidget(l)
        v.addWidget(widget)
        self.grid.addLayout(v, row, col, 1, colspan)

    # --- LOGIQUE CAMERA ---
    def toggle_cam(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            self.timer.start(30)
            self.btn_power.setText("Couper l'alimentation")
            self.btn_snap.setEnabled(True)
        else:
            self.timer.stop()
            self.cap.release()
            self.cap = None
            self.lbl_cam.clear()
            self.btn_power.setText("Allumer la Caméra")
            self.btn_snap.setEnabled(False)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            img = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
            self.lbl_cam.setPixmap(QPixmap.fromImage(img).scaled(340, 255, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))

    def capture_photo(self):
        ret, frame = self.cap.read()
        if ret:
            self.captured_image = frame
            self.lbl_cam.setStyleSheet("border: 4px solid #10b981; border-radius: 12px;")
            QMessageBox.information(self, "Capture", "Photo enregistrée temporairement.")