from PySide6.QtWidgets import (QDialog, QMessageBox, QVBoxLayout, QFormLayout, QLineEdit, 
                             QComboBox, QPushButton, QHBoxLayout, QLabel, QFrame, QGridLayout, QFileDialog)
from PySide6.QtCore import Qt, QRegularExpression, QTimer
import cv2
from PySide6.QtGui import QImage, QPixmap, QRegularExpressionValidator
import os
import shutil
from pathlib import Path

class ContactForm(QDialog):
    def __init__(self, parent=None, contact_data=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.contact_data = contact_data
        self.setup_ui()
        
        # Si on est en mode édition, on remplit les champs
        if self.contact_data:
            self.fill_data()

        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.image_capturee = None # Stockera la photo finale

    def setup_ui(self):
        self.setMinimumWidth(500)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Main Container
        self.main_container = QFrame()
        self.main_container.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #dcdde1;
                border-radius: 15px;
            }
            QLabel { border: none; color: #2f3640; font-size: 13px; }
            QLineEdit, QComboBox {
                border: 1px solid #dcdde1;
                border-radius: 6px;
                padding: 8px;
                background-color: #f5f6fa;
                selection-background-color: #3498db;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #ffffff;
            }
            QPushButton#btn_save {
                background-color: #2ecc71;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 10px;
            }
            QPushButton#btn_save:hover { background-color: #27ae60; }
            QPushButton#btn_cancel {
                background-color: #f5f6fa;
                color: #7f8c8d;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        
        container_layout = QVBoxLayout(self.main_container)
        container_layout.setSpacing(15)
        container_layout.setContentsMargins(25, 20, 25, 25)

        # --- HEADER ---
        header = QHBoxLayout()
        icon_label = QLabel("👤")
        icon_label.setStyleSheet("font-size: 24px; border: none;")
        
        title_text = "Modifier le Contact" if self.contact_data else "Nouvelle Fiche Contact"
        self.title_label = QLabel(title_text)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 18px; color: #2c3e50;")
        
        self.btn_close_top = QPushButton("✕")
        self.btn_close_top.setFixedSize(30, 30)
        self.btn_close_top.setCursor(Qt.PointingHandCursor)
        self.btn_close_top.setStyleSheet("border: none; font-size: 16px; color: #95a5a6;")
        self.btn_close_top.clicked.connect(self.reject)

        header.addWidget(icon_label)
        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(self.btn_close_top)
        container_layout.addLayout(header)

        photo_layout = QVBoxLayout()
        self.video_label = QLabel()
        self.video_label.setFixedSize(120, 120)
        self.video_label.setStyleSheet("""
            border: 3px solid #3498db;
            border-radius: 60px;
            background-color: #ecf0f1;
        """)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setText("👤")
        
        self.btn_camera = QPushButton("📸 Prendre Photo")
        self.btn_camera.setStyleSheet("""
            QPushButton { background-color: #34495e; color: white; border-radius: 4px; padding: 5px; }
            QPushButton:hover { background-color: #2c3e50; }
        """)
        self.btn_camera.clicked.connect(self.toggle_camera)
        
        photo_layout.addWidget(self.video_label, alignment=Qt.AlignCenter)
        photo_layout.addWidget(self.btn_camera, alignment=Qt.AlignCenter)
        container_layout.addLayout(photo_layout)
        self.btn_import = QPushButton("📂 Joindre un fichier")
        self.btn_import.setStyleSheet("""
            QPushButton { background-color: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; border-radius: 4px; padding: 5px; }
            QPushButton:hover { background-color: #e2e8f0; }
        """)
        self.btn_import.clicked.connect(self.import_document)
        photo_layout.addWidget(self.btn_import, alignment=Qt.AlignCenter)
        self.fichiers_a_importer = []
        # --- CHAMPS (Grille plus élégante) ---
        grid = QGridLayout()
        grid.setSpacing(12)

        # On définit les widgets
        self.type_contact = QComboBox()
        self.type_contact.addItems(["Assuré", "Bénéficiaire", "Prospect"])
        
        self.nature = QComboBox()
        self.nature.addItems(["Physique", "Morale"])

        self.nom = QLineEdit()
        self.prenom = QLineEdit()
        self.telephone = QLineEdit()
        self.email = QLineEdit()
        self.adresse = QLineEdit()
        self.num_id = QLineEdit()
        email_regex = QRegularExpression(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}")
        self.email.setValidator(QRegularExpressionValidator(email_regex, self.email))
        self.nom.setPlaceholderText("Ex: SOCIETE TOUT-RISQUE ou DUPONT")
        self.num_id.setPlaceholderText("N° de CNI, Passeport ou Registre de Commerce")

        # Organisation dans la grille
        grid.addWidget(QLabel("Type de Contact"), 0, 0)
        grid.addWidget(self.type_contact, 1, 0)
        grid.addWidget(QLabel("Nature"), 0, 1)
        grid.addWidget(self.nature, 1, 1)

        grid.addWidget(QLabel("Nom / Raison Sociale"), 2, 0, 1, 2)
        grid.addWidget(self.nom, 3, 0, 1, 2)

        grid.addWidget(QLabel("Prénom"), 4, 0)
        grid.addWidget(self.prenom, 5, 0)
        grid.addWidget(QLabel("Téléphone"), 4, 1)
        grid.addWidget(self.telephone, 5, 1)

        grid.addWidget(QLabel("E-mail"), 6, 0, 1, 2)
        grid.addWidget(self.email, 7, 0, 1, 2)
        
        grid.addWidget(QLabel("N° Identification"), 8, 0, 1, 2)
        grid.addWidget(self.num_id, 9, 0, 1, 2)

        container_layout.addLayout(grid)

        # --- FOOTER ---
        buttons = QHBoxLayout()
        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.setObjectName("btn_cancel")
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Enregistrer la fiche")
        self.btn_save.setObjectName("btn_save")
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.clicked.connect(self.accept)

        buttons.addStretch()
        buttons.addWidget(self.btn_cancel)
        buttons.addWidget(self.btn_save)
        container_layout.addLayout(buttons)

        layout.addWidget(self.main_container)

    def fill_data(self):
        """Remplit les champs si on passe un objet contact existant"""
        self.nom.setText(self.contact_data.nom)
        self.prenom.setText(self.contact_data.prenom or "")
        self.telephone.setText(self.contact_data.telephone or "")
        self.email.setText(self.contact_data.email or "")
        self.num_id.setText(self.contact_data.num_piece_id or "")
        index_type = self.type_contact.findText(self.contact_data.type_contact)
        if index_type >= 0: self.type_contact.setCurrentIndex(index_type)

    def toggle_nature_fields(self, text):
        """Désactive le champ prénom si c'est une personne morale"""
        self.prenom.setEnabled(text == "Physique")
        if text == "Morale":
            self.prenom.clear()

    def get_data(self):
        # 1. Définir le chemin de base vers addons/contact_manager/static/contacts
        # On adapte le chemin pour pointer précisément vers ton dossier static
        base_dir = Path(__file__).parent.parent / "static" / "contacts"
        
        # 2. Préparation du nom unique pour le dossier
        nom_client = self.nom.text().strip().upper()
        prenom_client = self.prenom.text().strip().capitalize()
        identifiant = self.num_id.text().strip() or "SANS_ID"
        
        folder_name = f"{nom_client}_{prenom_client}_{identifiant}"
        contact_dir = base_dir / folder_name
        
        # 3. Création physique du dossier (et des parents si static/contacts n'existe pas)
        contact_dir.mkdir(parents=True, exist_ok=True)
        
        # --- NOUVEAU : Traitement des fichiers joints (CNI, PDF, etc.) ---
        if hasattr(self, 'fichiers_a_importer'):
            for file_path in self.fichiers_a_importer:
                src_path = Path(file_path)
                dest_path = contact_dir / src_path.name
                try:
                    # copy2 préserve les métadonnées (dates, etc.)
                    shutil.copy2(src_path, dest_path)
                except Exception as e:
                    print(f"[ERREUR] Impossible de copier {src_path.name}: {e}")

        # 4. Gestion de la photo (Webcam)
        photo_path = None
        if hasattr(self, 'image_capturee') and self.image_capturee:
            filename = "photo_identite.jpg"
            full_path = contact_dir / filename
            
            if self.image_capturee.save(str(full_path), "JPG"):
                # On stocke le chemin relatif depuis la racine du projet
                # pour que l'affichage fonctionne même si tu déplaces le dossier du projet
                try:
                    # Remonte jusqu'à la racine (ajuste le nombre de .parent selon ta structure)
                    root_dir = Path(__file__).parent.parent.parent.parent
                    photo_path = str(full_path.relative_to(root_dir))
                except ValueError:
                    photo_path = str(full_path)
        
        # Si on modifie et qu'on n'a pas repris de photo, on garde l'ancienne
        elif self.contact_data:
            photo_path = self.contact_data.photo_path

        # 5. Retour des données prêtes pour le contrôleur/SQLAlchemy
        return {
            "type_contact": self.type_contact.currentText(),
            "nature": self.nature.currentText(),
            "nom": nom_client,
            "prenom": prenom_client,
            "telephone": self.telephone.text().strip(),
            "email": self.email.text().strip(),
            "adresse": self.adresse.text().strip(),
            "num_piece_id": self.num_id.text().strip(),
            "photo_path": photo_path,
            # "dossier_client": str(contact_dir) # Important pour l'ouvrir plus tard
        }

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()

    def toggle_camera(self):
        """Démarre la caméra ou prend la photo"""
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.timer.start(30) # 30ms pour un flux fluide
                self.btn_camera.setText("🎯 Capturer")
                self.btn_camera.setStyleSheet("background-color: #e67e22; color: white;")
        else:
            self.stop_camera()
            self.btn_camera.setText("✅ Photo Prise")
            self.btn_camera.setStyleSheet("background-color: #2ecc71; color: white;")

    def update_frame(self):
        """Affiche le flux vidéo dans le label circulaire"""
        ret, frame = self.cap.read()
        if ret:
            # On recadre en carré pour le cercle
            h, w, _ = frame.shape
            min_dim = min(h, w)
            start_x = (w - min_dim) // 2
            frame = frame[:, start_x:start_x+min_dim]
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QImage(frame, min_dim, min_dim, QImage.Format_RGB888)
            self.image_capturee = image # On garde la dernière frame
            self.video_label.setPixmap(QPixmap.fromImage(image).scaled(120, 120, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))

    def stop_camera(self):
        if self.cap:
            self.timer.stop()
            self.cap.release()
            self.cap = None

    def reject(self):
        self.stop_camera() # Sécurité pour libérer la webcam
        super().reject()

    def import_document(self):
        """Ouvre l'explorateur pour choisir des fichiers (PDF, Images, etc.)"""
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "Sélectionner des documents", 
            "", 
            "Documents (*.pdf *.jpg *.png *.jpeg *.docx)"
        )
        if files:
            self.fichiers_a_importer.extend(files)
            # Feedback visuel sur le bouton
            self.btn_import.setText(f"📂 {len(self.fichiers_a_importer)} fichier(s) prêt(s)")
            self.btn_import.setStyleSheet("""
                background-color: #dcfce7; 
                color: #166534; 
                border: 1px solid #bbf7d0;
                border-radius: 4px;
                padding: 5px;
            """)

    def on_add_new_contact(self):
        """Récupère les données, valide les champs obligatoires et appelle le contrôleur."""
        
        # 1. Collecte des données depuis les widgets
        data = {
            "type_contact": self.type_contact.currentText(),
            "nature": self.nature.currentText(),
            "nom": self.nom.text().strip().upper(), # Convention : Nom en majuscules
            "prenom": self.prenom.text().strip().title(), # Convention : Prénom (ex: Jean)
            "telephone": self.telephone.text().strip(),
            "email": self.email.text().strip().lower(),
            "num_piece_id": self.num_id.text().strip(),
            # "dossier_client": self.fichiers_a_importer[0] if self.fichiers_a_importer else None
        }

        # 2. Validation des contraintes 'NOT NULL' de la base de données
        if not data["nom"]:
            QMessageBox.warning(self, "Champ obligatoire", "Le champ 'Nom / Raison Sociale' est requis.")
            self.nom.setFocus()
            return

        # 3. Appel au contrôleur
        # On passe le dictionnaire 'data' au contrôleur que nous avons corrigé
        contact_obj, success, message = self.ContactController.create_contact(data)

        if success:
            QMessageBox.information(self, "Succès", f"Fiche contact de {data['nom']} créée avec succès.")
            self.accept() # Ferme le formulaire uniquement si la DB a validé
        else:
            # Affiche l'erreur réelle (ex: duplication d'email ou erreur IP)
            QMessageBox.critical(self, "Erreur de création", f"Impossible d'enregistrer :\n{message}")