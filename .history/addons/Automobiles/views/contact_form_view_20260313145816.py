import cv2
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QComboBox, QPushButton, QLabel, QFrame, QGridLayout, 
                             QScrollArea, QDateEdit, QMessageBox, QWidget)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QImage, QPixmap, QColor

class ContactForm(QDialog):
    def __init__(self, controller, contact_data=None, parent=None):
        super().__init__(parent)
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
        
        if self.contact_data:
            self.fill_form()

    def setup_ui(self):
        self.setMinimumSize(1250, 850)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- CONTENEUR PRINCIPAL ---
        self.container = QFrame()
        self.container.setObjectName("MainContainer")
        self.container.setStyleSheet("""
            #MainContainer { background-color: #ffffff; border-radius: 10px; border: 2px solid #1e293b; }
            .SectionTitle { color: #2563eb; font-weight: 800; font-size: 13px; text-transform: uppercase; margin-bottom: 5px; border-bottom: 2px solid #f1f5f9; }
            QLabel { color: #64748b; font-weight: 700; font-size: 11px; }
            QLineEdit, QComboBox, QDateEdit { background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px; color: #1e293b; }
            QLineEdit:focus { border: 2px solid #3b82f6; background-color: white; }
        """)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setSpacing(20)

        # --- HEADER ---
        header_layout = QHBoxLayout()
        header_title = QLabel("📋 FICHE INFORMATION CLIENT")
        header_title.setStyleSheet("font-size: 22px; color: #1e293b; font-weight: 900; border: none;")
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(35, 35)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setStyleSheet("background-color: #fee2e2; color: #ef4444; border-radius: 17px; font-weight: bold; border: none;")
        self.btn_close.clicked.connect(self.reject)

        header_layout.addWidget(header_title)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_close)
        container_layout.addLayout(header_layout)

        # --- CORPS (Splitter : Formulaire | Caméra) ---
        body_layout = QHBoxLayout()
        body_layout.setSpacing(30)

        # GAUCHE : FORMULAIRE DÉFILANT
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        form_wrapper = QWidget()
        self.grid = QGridLayout(form_wrapper)
        self.grid.setSpacing(20)

        # Bloc 1 : Statut
        self._add_section_header("I. Administration & Statut", 0)
        self.type_client = QComboBox(); self.type_client.addItems(["Nouveau Client", "Ancien Client", "VIP"])
        self.nature = QComboBox(); self.nature.addItems(["Particulier", "Société"])
        self.charge_client = QLineEdit()
        self.redacteur = QLineEdit()
        
        self._add_smart_field("Type de Client", self.type_client, 1, 0)
        self._add_smart_field("Nature Entité", self.nature, 1, 1)
        self._add_smart_field("Chargé de Clientèle", self.charge_client, 2, 0)
        self._add_smart_field("Rédacteur Production", self.redacteur, 2, 1)

        # Bloc 2 : Identité
        self._add_section_header("II. État Civil & Identité", 3)
        self.civilite = QComboBox(); self.civilite.addItems(["M.", "Mme", "Mlle", "Dr", "Pr"])
        self.nom = QLineEdit(); self.prenom = QLineEdit()
        self.date_naiss = QDateEdit(); self.date_naiss.setCalendarPopup(True)
        self.nationalite = QLineEdit()
        self.num_contribuable = QLineEdit()

        self._add_smart_field("Intitulé / Civilité", self.civilite, 4, 0)
        self._add_smart_field("Nom Client / Raison Sociale", self.nom, 4, 1, colspan=2)
        self._add_smart_field("Prénoms", self.prenom, 5, 0, colspan=2)
        self._add_smart_field("Date de Naissance", self.date_naiss, 5, 2)
        self._add_smart_field("Nationalité", self.nationalite, 6, 0)
        self._add_smart_field("N° Contribuable (IFU)", self.num_contribuable, 6, 1, colspan=2)

        # Bloc 3 : Contact
        self._add_section_header("III. Coordonnées & Contact", 7)
        self.tel = QLineEdit(); self.fax = QLineEdit(); self.email = QLineEdit()
        self.adresse = QLineEdit(); self.ville = QLineEdit()

        self._add_smart_field("Téléphone Bureau", self.tel, 8, 0)
        self._add_smart_field("Téléphone Portable / Fax", self.fax, 8, 1)
        self._add_smart_field("Adresse E-mail", self.email, 8, 2)
        self._add_smart_field("Adresse Résidentielle", self.adresse, 9, 0, colspan=2)
        self._add_smart_field("Ville", self.ville, 9, 2)

        # Bloc 4 : Permis
        self._add_section_header("IV. Permis de Conduire", 10)
        self.cat_permis = QComboBox(); self.cat_permis.addItems(["A", "B", "C", "D", "E", "F", "G"])
        self.date_permis = QDateEdit(); self.date_permis.setCalendarPopup(True)
        self.num_permis = QLineEdit()

        self._add_smart_field("Catégorie Permis", self.cat_permis, 11, 0)
        self._add_smart_field("N° de Permis", self.num_permis, 11, 1)
        self._add_smart_field("Date d'Obtention", self.date_permis, 11, 2)

        scroll.setWidget(form_wrapper)
        body_layout.addWidget(scroll, 7)

        # DROITE : BIOMÉTRIE
        cam_card = QFrame()
        cam_card.setStyleSheet("background-color: #f8fafc; border-radius: 15px; border: 1px solid #e2e8f0;")
        cam_vbox = QVBoxLayout(cam_card)
        cam_vbox.setContentsMargins(20, 20, 20, 20)

        self.lbl_cam = QLabel("APPAREIL PHOTO")
        self.lbl_cam.setFixedSize(340, 255)
        self.lbl_cam.setStyleSheet("background: #0f172a; border-radius: 12px; color: #475569;")
        self.lbl_cam.setAlignment(Qt.AlignCenter)
        
        cam_vbox.addWidget(QLabel("📸 CAPTURE BIOMÉTRIQUE"), alignment=Qt.AlignCenter)
        cam_vbox.addWidget(self.lbl_cam)
        
        self.btn_power = QPushButton("Allumer la Caméra")
        self.btn_power.setCursor(Qt.PointingHandCursor)
        self.btn_power.setStyleSheet("background: #1e293b; color: white; padding: 12px; border-radius: 8px; font-weight: bold;")
        
        self.btn_snap = QPushButton("🎯 Prendre la Photo")
        self.btn_snap.setEnabled(False)
        self.btn_snap.setStyleSheet("background: #10b981; color: white; padding: 12px; border-radius: 8px; font-weight: bold;")

        cam_vbox.addWidget(self.btn_power)
        cam_vbox.addWidget(self.btn_snap)
        cam_vbox.addStretch()

        body_layout.addWidget(cam_card, 3)
        container_layout.addLayout(body_layout)

        # --- FOOTER ---
        footer_layout = QHBoxLayout()
        self.btn_save = QPushButton("💾 ENREGISTRER LA FICHE")
        self.btn_save.setFixedSize(280, 50)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton { background: #2563eb; color: white; border-radius: 12px; font-weight: 800; font-size: 14px; }
            QPushButton:hover { background: #1d4ed8; }
        """)
        self.btn_save.clicked.connect(self.accept)
        
        footer_layout.addStretch()
        footer_layout.addWidget(self.btn_save)
        container_layout.addLayout(footer_layout)

        main_layout.addWidget(self.container)

        # Connexions Caméra
        self.btn_power.clicked.connect(self.toggle_camera)
        self.btn_snap.clicked.connect(self.capture_photo)

    def _add_section_header(self, title, row):
        lbl = QLabel(title)
        lbl.setProperty("class", "SectionTitle")
        lbl.setStyleSheet("color: #2563eb; font-weight: 800; font-size: 13px; margin-top: 10px;")
        self.grid.addWidget(lbl, row, 0, 1, 3)

    def _add_smart_field(self, label, widget, row, col, colspan=1):
        v = QVBoxLayout()
        v.setSpacing(5)
        l = QLabel(label)
        v.addWidget(l)
        v.addWidget(widget)
        self.grid.addLayout(v, row, col, 1, colspan)

    # --- LOGIQUE CAMERA CORRIGÉE ---
    def toggle_camera(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.timer.start(30)
                self.btn_power.setText("Couper la Caméra")
                self.btn_power.setStyleSheet("background: #ef4444; color: white; padding: 12px; border-radius: 8px;")
                self.btn_snap.setEnabled(True)
            else:
                QMessageBox.critical(self, "Erreur", "Impossible d'accéder à la webcam.")
        else:
            self.stop_camera()

    def stop_camera(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
        self.cap = None
        self.lbl_cam.clear()
        self.lbl_cam.setText("APPAREIL PHOTO")
        self.btn_power.setText("Allumer la Caméra")
        self.btn_power.setStyleSheet("background: #1e293b; color: white; padding: 12px; border-radius: 8px;")
        self.btn_snap.setEnabled(False)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1) # Effet miroir
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            img = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
            self.lbl_cam.setPixmap(QPixmap.fromImage(img).scaled(self.lbl_cam.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))

    def capture_photo(self):
        ret, frame = self.cap.read()
        if ret:
            # On peut sauvegarder temporairement ou garder l'image en mémoire
            self.captured_image = frame
            self.stop_camera()
            # Afficher l'image fixe capturée
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            img = QImage(frame_rgb.data, w, h, ch * w, QImage.Format_RGB888)
            self.lbl_cam.setPixmap(QPixmap.fromImage(img).scaled(self.lbl_cam.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            self.lbl_cam.setStyleSheet("border: 4px solid #10b981; border-radius: 12px;")

    def get_data(self):
        """
        Récupère les 17+ champs pour le contrôleur.
        Inclut la référence à l'image capturée.
        """
        return {
            # I. Administration & Statut
            "type_client": self.type_client.currentText(),
            "nature": self.nature.currentText(),
            "charge_clientele": self.charge_client.text().strip(),
            "redacteur_production": self.redacteur.text().strip(),
            
            # II. État Civil & Identité
            "civilite": self.civilite.currentText(),
            "nom": self.nom.text().strip().upper(), # Nom en majuscules (Standard)
            "prenom": self.prenom.text().strip().title(), # Prénoms (Standard)
            "date_naissance": self.date_naiss.date().toPython(),
            "nationalite": self.nationalite.text().strip(),
            "num_contribuable": self.num_contribuable.text().strip(),
            
            # III. Coordonnées & Contact
            "telephone": self.tel.text().strip(),
            "fax": self.fax.text().strip(),
            "email": self.email.text().strip().lower(),
            "adresse": self.adresse.text().strip(),
            "ville": self.ville.text().strip(),
            
            # IV. Permis de Conduire
            "cat_permis": self.cat_permis.currentText(),
            "num_permis": self.num_permis.text().strip(),
            "date_permis": self.date_permis.date().toPython(),

            # --- GESTION DE LA PHOTO ---
            # On passe l'image brute au contrôleur. 
            # C'est le contrôleur qui décidera de la sauvegarder sur disque et 
            # d'enregistrer le 'photo_path' final dans le modèle.
            "image_brute": self.captured_image 
        }

    def fill_form(self):
        """Remplit le formulaire en mode édition"""
        if not self.contact_data: return
        self.nom.setText(getattr(self.contact_data, 'nom', ''))
        self.prenom.setText(getattr(self.contact_data, 'prenom', ''))
        # ... Remplir les autres champs selon vos modèles ...