# from PySide6.QtWidgets import (QDialog, QMessageBox, QVBoxLayout, QFormLayout, QLineEdit, 
#                              QComboBox, QPushButton, QHBoxLayout, QLabel, QFrame, QGridLayout, QFileDialog)
# from PySide6.QtCore import Qt, QRegularExpression, QTimer
# import cv2
# from PySide6.QtGui import QImage, QPixmap, QRegularExpressionValidator
# import os
# import shutil
# from pathlib import Path

# class ContactForm(QDialog):
#     def __init__(self, parent=None, contact_data=None):
#         super().__init__(parent)
#         self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
#         self.setAttribute(Qt.WA_TranslucentBackground)
#         self.contact_data = contact_data
#         self.setup_ui()
        
#         # Si on est en mode édition, on remplit les champs
#         if self.contact_data:
#             self.fill_data()

#         self.cap = None
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.update_frame)
#         self.image_capturee = None # Stockera la photo finale

#     def setup_ui(self):
#         self.setMinimumWidth(650)
#         self.main_layout = QVBoxLayout(self)
        
#         # --- CONTENEUR PRINCIPAL ---
#         self.container = QFrame()
#         self.container.setObjectName("MainContainer")
#         self.container.setStyleSheet("""
#             #MainContainer {
#                 background-color: #ffffff;
#                 border-radius: 20px;
#                 border: 1px solid #e2e8f0;
#             }
#             QLabel { color: #475569; font-weight: bold; font-size: 13px; }
#             QLineEdit, QComboBox {
#                 background-color: #f8fafc;
#                 border: 1px solid #cbd5e1;
#                 border-radius: 8px;
#                 padding: 10px;
#                 color: #1e293b;
#                 font-size: 14px;
#             }
#             QLineEdit:focus { border: 2px solid #3b82f6; background-color: #ffffff; }
#             QPushButton#BtnSave {
#                 background-color: #2563eb; color: white; border-radius: 8px; 
#                 font-weight: bold; font-size: 14px; padding: 12px;
#             }
#             QPushButton#BtnCancel {
#                 background-color: #f1f5f9; color: #475569; border-radius: 8px; 
#                 font-weight: bold; padding: 12px;
#             }
#         """)
        
#         layout = QVBoxLayout(self.container)
#         layout.setContentsMargins(30, 30, 30, 30)
#         layout.setSpacing(20)

#         # --- EN-TÊTE ---
#         header = QHBoxLayout()
#         title = QLabel("📝 Fiche Informations Contact")
#         title.setStyleSheet("font-size: 20px; color: #1e293b; font-weight: 900;")
#         header.addWidget(title)
#         header.addStretch()
#         layout.addLayout(header)

#         # --- GRILLE DE FORMULAIRE (Inspirée de la photo) ---
#         form_grid = QGridLayout()
#         form_grid.setSpacing(15)

#         # Ligne 1 : Type et Nature
#         self.type_contact = QComboBox()
#         self.type_contact.addItems(["Physique", "Morale"])
#         self.nature = QComboBox()
#         self.nature.addItems(["Client", "Prospect", "Partenaire"])
        
#         form_grid.addWidget(QLabel("Type de Contact"), 0, 0)
#         form_grid.addWidget(self.type_contact, 1, 0)
#         form_grid.addWidget(QLabel("Nature"), 0, 1)
#         form_grid.addWidget(self.nature, 1, 1)

#         # Ligne 2 : Nom et Prénom
#         self.nom = QLineEdit(); self.nom.setPlaceholderText("ex: DIALLO")
#         self.prenom = QLineEdit(); self.prenom.setPlaceholderText("ex: Saliou")
        
#         form_grid.addWidget(QLabel("Nom / Raison Sociale"), 2, 0)
#         form_grid.addWidget(self.nom, 3, 0)
#         form_grid.addWidget(QLabel("Prénom"), 2, 1)
#         form_grid.addWidget(self.prenom, 3, 1)

#         # Ligne 3 : Téléphone et Email
#         self.telephone = QLineEdit(); self.telephone.setPlaceholderText("+221 ...")
#         self.email = QLineEdit(); self.email.setPlaceholderText("email@exemple.com")
        
#         form_grid.addWidget(QLabel("Téléphone"), 4, 0)
#         form_grid.addWidget(self.telephone, 5, 0)
#         form_grid.addWidget(QLabel("Email"), 4, 1)
#         form_grid.addWidget(self.email, 5, 1)

#         # Ligne 4 : Pièce ID et Adresse
#         self.num_id = QLineEdit(); self.num_id.setPlaceholderText("N° CNI ou Passeport")
#         self.adresse = QLineEdit(); self.adresse.setPlaceholderText("Dakar, Plateau...")
        
#         form_grid.addWidget(QLabel("N° Identification"), 6, 0)
#         form_grid.addWidget(self.num_id, 7, 0)
#         form_grid.addWidget(QLabel("Adresse Résidentielle"), 6, 1)
#         form_grid.addWidget(self.adresse, 7, 1)

#         layout.addLayout(form_grid)

#         # --- BOUTONS D'ACTION ---
#         btn_layout = QHBoxLayout()
#         self.btn_cancel = QPushButton("Annuler")
#         self.btn_cancel.setObjectName("BtnCancel")
#         self.btn_save = QPushButton("Enregistrer le Contact")
#         self.btn_save.setObjectName("BtnSave")
        
#         btn_layout.addStretch()
#         btn_layout.addWidget(self.btn_cancel)
#         btn_layout.addWidget(self.btn_save)
#         layout.addLayout(btn_layout)

#         self.main_layout.addWidget(self.container)

#         # Connexions
#         self.btn_cancel.clicked.connect(self.reject)
#         self.btn_save.clicked.connect(self.get_data)

        
#     def fill_data(self):
#         """Remplit les champs si on passe un objet contact existant"""
#         self.nom.setText(self.contact_data.nom)
#         self.prenom.setText(self.contact_data.prenom or "")
#         self.telephone.setText(self.contact_data.telephone or "")
#         self.email.setText(self.contact_data.email or "")
#         self.num_id.setText(self.contact_data.num_piece_id or "")
#         index_type = self.type_contact.findText(self.contact_data.type_contact)
#         if index_type >= 0: self.type_contact.setCurrentIndex(index_type)

#     def toggle_nature_fields(self, text):
#         """Désactive le champ prénom si c'est une personne morale"""
#         self.prenom.setEnabled(text == "Physique")
#         if text == "Morale":
#             self.prenom.clear()

#     def get_data(self):
#         # 1. Définir le chemin de base vers addons/contact_manager/static/contacts
#         # On adapte le chemin pour pointer précisément vers ton dossier static
#         base_dir = Path(__file__).parent.parent / "static" / "contacts"
        
#         # 2. Préparation du nom unique pour le dossier
#         nom_client = self.nom.text().strip().upper()
#         prenom_client = self.prenom.text().strip().capitalize()
#         identifiant = self.num_id.text().strip() or "SANS_ID"
        
#         folder_name = f"{nom_client}_{prenom_client}_{identifiant}"
#         contact_dir = base_dir / folder_name
        
#         # 3. Création physique du dossier (et des parents si static/contacts n'existe pas)
#         contact_dir.mkdir(parents=True, exist_ok=True)
        
#         # --- NOUVEAU : Traitement des fichiers joints (CNI, PDF, etc.) ---
#         if hasattr(self, 'fichiers_a_importer'):
#             for file_path in self.fichiers_a_importer:
#                 src_path = Path(file_path)
#                 dest_path = contact_dir / src_path.name
#                 try:
#                     # copy2 préserve les métadonnées (dates, etc.)
#                     shutil.copy2(src_path, dest_path)
#                 except Exception as e:
#                     print(f"[ERREUR] Impossible de copier {src_path.name}: {e}")

#         # 4. Gestion de la photo (Webcam)
#         photo_path = None
#         if hasattr(self, 'image_capturee') and self.image_capturee:
#             filename = "photo_identite.jpg"
#             full_path = contact_dir / filename
            
#             if self.image_capturee.save(str(full_path), "JPG"):
#                 # On stocke le chemin relatif depuis la racine du projet
#                 # pour que l'affichage fonctionne même si tu déplaces le dossier du projet
#                 try:
#                     # Remonte jusqu'à la racine (ajuste le nombre de .parent selon ta structure)
#                     root_dir = Path(__file__).parent.parent.parent.parent
#                     photo_path = str(full_path.relative_to(root_dir))
#                 except ValueError:
#                     photo_path = str(full_path)
        
#         # Si on modifie et qu'on n'a pas repris de photo, on garde l'ancienne
#         elif self.contact_data:
#             photo_path = self.contact_data.photo_path

#         # 5. Retour des données prêtes pour le contrôleur/SQLAlchemy
#         return {
#             "type_contact": self.type_contact.currentText(),
#             "nature": self.nature.currentText(),
#             "nom": nom_client,
#             "prenom": prenom_client,
#             "telephone": self.telephone.text().strip(),
#             "email": self.email.text().strip(),
#             "adresse": self.adresse.text().strip(),
#             "num_piece_id": self.num_id.text().strip(),
#             "photo_path": photo_path,
#             # "dossier_client": str(contact_dir) # Important pour l'ouvrir plus tard
#         }

#     def mousePressEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             self.drag_pos = event.globalPosition().toPoint()

#     def mouseMoveEvent(self, event):
#         if event.buttons() == Qt.LeftButton:
#             self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
#             self.drag_pos = event.globalPosition().toPoint()
#             event.accept()

#     def toggle_camera(self):
#         """Démarre la caméra ou prend la photo"""
#         if self.cap is None:
#             self.cap = cv2.VideoCapture(0)
#             if self.cap.isOpened():
#                 self.timer.start(30) # 30ms pour un flux fluide
#                 self.btn_camera.setText("🎯 Capturer")
#                 self.btn_camera.setStyleSheet("background-color: #e67e22; color: white;")
#         else:
#             self.stop_camera()
#             self.btn_camera.setText("✅ Photo Prise")
#             self.btn_camera.setStyleSheet("background-color: #2ecc71; color: white;")

#     def update_frame(self):
#         """Affiche le flux vidéo dans le label circulaire"""
#         ret, frame = self.cap.read()
#         if ret:
#             # On recadre en carré pour le cercle
#             h, w, _ = frame.shape
#             min_dim = min(h, w)
#             start_x = (w - min_dim) // 2
#             frame = frame[:, start_x:start_x+min_dim]
            
#             frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             image = QImage(frame, min_dim, min_dim, QImage.Format_RGB888)
#             self.image_capturee = image # On garde la dernière frame
#             self.video_label.setPixmap(QPixmap.fromImage(image).scaled(120, 120, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))

#     def stop_camera(self):
#         if self.cap:
#             self.timer.stop()
#             self.cap.release()
#             self.cap = None

#     def reject(self):
#         self.stop_camera() # Sécurité pour libérer la webcam
#         super().reject()

#     def import_document(self):
#         """Ouvre l'explorateur pour choisir des fichiers (PDF, Images, etc.)"""
#         files, _ = QFileDialog.getOpenFileNames(
#             self, 
#             "Sélectionner des documents", 
#             "", 
#             "Documents (*.pdf *.jpg *.png *.jpeg *.docx)"
#         )
#         if files:
#             self.fichiers_a_importer.extend(files)
#             # Feedback visuel sur le bouton
#             self.btn_import.setText(f"📂 {len(self.fichiers_a_importer)} fichier(s) prêt(s)")
#             self.btn_import.setStyleSheet("""
#                 background-color: #dcfce7; 
#                 color: #166534; 
#                 border: 1px solid #bbf7d0;
#                 border-radius: 4px;
#                 padding: 5px;
#             """)

#     def on_add_new_contact(self):
#         """Récupère les données, valide les champs obligatoires et appelle le contrôleur."""
        
#         # 1. Collecte des données depuis les widgets
#         data = {
#             "type_contact": self.type_contact.currentText(),
#             "nature": self.nature.currentText(),
#             "nom": self.nom.text().strip().upper(), # Convention : Nom en majuscules
#             "prenom": self.prenom.text().strip().title(), # Convention : Prénom (ex: Jean)
#             "telephone": self.telephone.text().strip(),
#             "email": self.email.text().strip().lower(),
#             "num_piece_id": self.num_id.text().strip(),
#             # "dossier_client": self.fichiers_a_importer[0] if self.fichiers_a_importer else None
#         }

#         # 2. Validation des contraintes 'NOT NULL' de la base de données
#         if not data["nom"]:
#             QMessageBox.warning(self, "Champ obligatoire", "Le champ 'Nom / Raison Sociale' est requis.")
#             self.nom.setFocus()
#             return

#         # 3. Appel au contrôleur
#         # On passe le dictionnaire 'data' au contrôleur que nous avons corrigé
#         contact_obj, success, message = self.ContactController.create_contact(data)

#         if success:
#             QMessageBox.information(self, "Succès", f"Fiche contact de {data['nom']} créée avec succès.")
#             self.accept() # Ferme le formulaire uniquement si la DB a validé
#         else:
#             # Affiche l'erreur réelle (ex: duplication d'email ou erreur IP)
#             QMessageBox.critical(self, "Erreur de création", f"Impossible d'enregistrer :\n{message}")

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QComboBox, QPushButton, QLabel, QFrame, QGridLayout, 
                             QScrollArea, QDateEdit, QWidget)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QColor

class ContactForm(QDialog):
    def __init__(self, controller, parent=None, contact_data=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.controller = controller
        self.contact_data = contact_data

        # Variables pour la photo
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.captured_image = None # Contiendra l'image finale

        self.setup_ui()
        
        if self.contact_data:
            self.fill_data()

    def setup_ui(self):
        self.setMinimumWidth(1050)
        self.setMinimumHeight(750)
        main_layout = QVBoxLayout(self)
        
        # --- CONTENEUR PRINCIPAL ---
        self.container = QFrame()
        self.container.setObjectName("MainContainer")
        self.container.setStyleSheet("""
            #MainContainer {
                background-color: #ffffff;
                border-radius: 20px;
                border: 1px solid #e2e8f0;
            }
            .SectionTitle {
                color: #2563eb;
                font-weight: 800;
                font-size: 14px;
                margin-top: 10px;
                border-bottom: 1px solid #eff6ff;
            }
            QLabel { color: #475569; font-weight: 600; font-size: 12px; }
            QLineEdit, QComboBox, QDateEdit {
                background-color: #f8fafc;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 8px;
                color: #1e293b;
            }
            QLineEdit:focus { border: 2px solid #3b82f6; background-color: #ffffff; }
        """)
        
        container_layout = QVBoxLayout(self.container)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("📄 FICHE D'IDENTIFICATION CLIENT")
        title.setStyleSheet("font-size: 18px; color: #1e293b; font-weight: 900;")
        header.addWidget(title)
        header.addStretch()
        container_layout.addLayout(header)

        # --- LAYOUT HORIZONTAL PRINCIPAL (Formulaire | Photo) ---
        body_layout = QHBoxLayout()

        # Zone Scrollable pour le formulaire
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        form_widget = QWidget()
        self.grid = QGridLayout(form_widget)
        self.grid.setSpacing(15)

        # --- SECTION 1 : PROFIL & STATUT ---
        self._add_section_title("1. Statut et Identité", 0)
        
        self.type_client = self._create_combo(["Standard", "VIP"])
        self.type_contact = self._create_combo(["Physique", "Morale"])
        self.nature = self._create_combo(["Client", "Prospect", "Partenaire"])
        
        self._add_field("Type Client", self.type_client, 1, 0)
        self._add_field("Type Contact", self.type_contact, 1, 1)
        self._add_field("Nature", self.nature, 1, 2)

        self.nom = QLineEdit(); self.nom.setPlaceholderText("Nom ou Raison Sociale")
        self.prenom = QLineEdit(); self.prenom.setPlaceholderText("Prénom")
        self.civilite = self._create_combo(["M.", "Mme", "Mlle"])

        self._add_field("Civilité", self.civilite, 2, 0)
        self._add_field("Nom / Raison Sociale", self.nom, 2, 1)
        self._add_field("Prénom", self.prenom, 2, 2)

        # --- SECTION 2 : INFORMATIONS FISCALES & PERSO ---
        self._add_section_title("2. Informations Fiscales & Personnelles", 3)
        
        self.num_contribuable = QLineEdit(); self.num_contribuable.setPlaceholderText("N° IFU / Contribuable")
        self.date_naissance = QDateEdit(); self.date_naissance.setCalendarPopup(True)
        self.nationalite = QLineEdit(); self.nationalite.setPlaceholderText("ex: Sénégalaise")

        self._add_field("N° Contribuable", self.num_contribuable, 4, 0)
        self._add_field("Date de Naissance", self.date_naissance, 4, 1)
        self._add_field("Nationalité", self.nationalite, 4, 2)

        # --- SECTION 3 : CONTACT & LOCALISATION ---
        self._add_section_title("3. Coordonnées de Contact", 5)
        
        self.telephone = QLineEdit(); self.telephone.setPlaceholderText("Téléphone Principal")
        self.fax = QLineEdit(); self.fax.setPlaceholderText("Numéro de Fax")
        self.email = QLineEdit(); self.email.setPlaceholderText("email@domaine.com")
        self.adresse = QLineEdit(); self.adresse.setPlaceholderText("Adresse complète")

        self._add_field("Téléphone", self.telephone, 6, 0)
        self._add_field("Fax", self.fax, 6, 1)
        self._add_field("E-mail", self.email, 6, 2)
        self._add_field("Adresse Résidentielle", self.adresse, 7, 0, colspan=3)

        # --- SECTION 4 : PERMIS & GESTION ---
        self._add_section_title("4. Permis de Conduire & Suivi Dossier", 8)
        
        self.cat_permis = self._create_combo(["A", "B", "C", "D", "E"])
        self.date_permis = QDateEdit(); self.date_permis.setCalendarPopup(True)
        self.charge_clientele = QLineEdit(); self.charge_clientele.setPlaceholderText("Nom du gestionnaire")
        self.redacteur_prod = QLineEdit(); self.redacteur_prod.setPlaceholderText("Rédacteur production")

        self._add_field("Catégorie Permis", self.cat_permis, 9, 0)
        self._add_field("Date d'obtention", self.date_permis, 9, 1)
        self._add_field("Chargé de Clientèle", self.charge_clientele, 10, 0)
        self._add_field("Rédacteur Production", self.redacteur_prod, 10, 1)

        scroll.setWidget(form_widget)
        container_layout.addWidget(scroll)

        # Boutons
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setStyleSheet("background: #f1f5f9; color: #475569; padding: 10px 20px; border-radius: 8px; font-weight: bold;")
        btn_save = QPushButton("Enregistrer la Fiche")
        btn_save.setStyleSheet("background: #2563eb; color: white; padding: 10px 25px; border-radius: 8px; font-weight: bold;")
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        container_layout.addLayout(btn_layout)

        main_layout.addWidget(self.container)

        # Events
        btn_cancel.clicked.connect(self.reject)
        btn_save.clicked.connect(self.accept)

    # --- HELPERS ---
    def _add_section_title(self, text, row):
        lbl = QLabel(text)
        lbl.setProperty("class", "SectionTitle")
        self.grid.addWidget(lbl, row, 0, 1, 3)

    def _add_field(self, label_text, widget, row, col, colspan=1):
        vbox = QVBoxLayout()
        vbox.setSpacing(4)
        lbl = QLabel(label_text)
        vbox.addWidget(lbl)
        vbox.addWidget(widget)
        self.grid.addLayout(vbox, row, col, 1, colspan)

    def _create_combo(self, items):
        cb = QComboBox()
        cb.addItems(items)
        return cb