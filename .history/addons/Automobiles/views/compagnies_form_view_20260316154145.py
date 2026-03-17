from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QGraphicsDropShadowEffect, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class FormulaireCreationCompagnie(QDialog):
    def __init__(self, parent=None, controller=None, current_user=None):
        super().__init__(parent)
        self.controller = controller
        self.user = current_user
        
        # --- CONFIGURATION DU DIALOGUE ---
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(550)
        
        self.setup_ui()

    def _add_glow_effect(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 10)
        widget.setGraphicsEffect(shadow)

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)

        self.container = QFrame()
        self.container.setStyleSheet("background-color: white; border-radius: 20px; border: none;")
        self._add_glow_effect(self.container)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(40, 30, 40, 45)
        layout.setSpacing(12)

        # --- HEADER ---
        top_bar = QHBoxLayout()
        title = QLabel("Nouveau Partenaire")
        title.setStyleSheet("font-size: 22px; font-weight: 900; color: #0f172a; border: none;")
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setFixedSize(35, 35)
        self.btn_close.clicked.connect(self.reject)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #f8fafc; color: #64748b; border-radius: 17px; 
                font-size: 14px; font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #fee2e2; color: #ef4444; }
        """)
        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_close)
        layout.addLayout(top_bar)

        layout.addSpacing(10)

        # --- CHAMPS D'IDENTIFICATION ---
        layout.addWidget(self._create_field("code", "Code Compagnie", "ex: 1111", True))
        layout.addWidget(self._create_field("nom", "Nom de la compagnie", "ex: AREA YAOUNDE", True))
        
        # --- CHAMPS DE CONTACT ---
        layout.addWidget(self._create_field("email", "Email de contact", "contact@assurance.cm"))
        layout.addWidget(self._create_field("telephone", "Téléphone", "+237 6xx xxx xxx"))
        layout.addWidget(self._create_field("adresse", "Adresse physique", "Rue de l'indépendance"))

        # --- SECTION FLOTTE (AJOUTÉE) ---
        flotte_label = QLabel("PLAGE DE NUMÉROTATION FLOTTE")
        flotte_label.setStyleSheet("color: #3b82f6; font-size: 10px; font-weight: 900; margin-top: 10px;")
        layout.addWidget(flotte_label)

        flotte_layout = QHBoxLayout()
        self.num_debut = self._create_field("num_debut", "Num Début", "0001")
        self.num_fin = self._create_field("num_fin", "Num Fin", "9999")
        flotte_layout.addWidget(self.num_debut)
        flotte_layout.addWidget(self.num_fin)
        layout.addLayout(flotte_layout)

        layout.addSpacing(20)

        # --- BOUTON DE VALIDATION ---
        self.btn_save = QPushButton("ENREGISTRER LA COMPAGNIE")
        self.btn_save.setFixedHeight(55)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.clicked.connect(self.accept)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #0f172a; color: white; font-weight: 800;
                border-radius: 15px; font-size: 13px; border: none;
            }
            QPushButton:hover { background-color: #2563eb; }
        """)
        layout.addWidget(self.btn_save)

        self.main_layout.addWidget(self.container)

    def _create_field(self, attr_name, label, placeholder, required=False):
        """Méthode helper pour créer un champ et l'enregistrer comme attribut"""
        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)

        lbl = QLabel(f"{label} *" if required else label)
        lbl.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: 800; text-transform: uppercase;")
        
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setFixedHeight(40)
        edit.setStyleSheet("""
            QLineEdit {
                background-color: #f8fafc; border: none; border-bottom: 2px solid #f1f5f9; 
                border-radius: 6px; padding-left: 12px; color: #1e293b; font-size: 13px;
            }
            QLineEdit:focus { border-bottom: 2px solid #3b82f6; background-color: white; }
        """)
        
        lay.addWidget(lbl)
        lay.addWidget(edit)
        
        # On attache le QLineEdit à l'instance pour y accéder via get_data
        setattr(self, f"input_{attr_name}", edit)
        return container

    def get_data(self):
        """Retourne les clés EXACTES du modèle SQL"""
        return {
            "nom": self.edit_nom.text().strip(),
            "code": self.edit_code.text().strip(),
            "email": self.edit_email.text().strip(),
            "telephone": self.edit_phone.text().strip(),
            "adresse": self.edit_adresse.text().strip(),
            "num_debut": self.input_debut.text().strip(),
            "num_fin": self.input_fin.text().strip()
        }
    def accept(self):
        """Surcharge de la méthode accept pour ajouter un feedback visuel"""
        from PySide6.QtGui import QCursor
        from PySide6.QtCore import Qt
        
        # Changer le curseur pour indiquer un travail en cours
        self.setCursor(QCursor(Qt.WaitCursor))
        self.btn_save.setEnabled(False)
        self.btn_save.setText("COMMUNICATION AVEC LE SERVEUR...")
        
        # Appeler la méthode parente qui fermera le dialogue avec QDialog.Accepted
        super().accept()