from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class FormulaireCreationCompagnie(QDialog):
    def __init__(self, parent=None, controller=None, current_user=None):
        super().__init__(parent)
        self.controller = controller
        self.user = current_user
        
        # --- CONFIGURATION DU DIALOGUE (SANS BORDURES SYSTÈME) ---
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setup_ui()

    def _add_ultra_soft_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setColor(QColor(0, 0, 0, 15)) # Ombre très légère
        shadow.setOffset(0, 10)
        widget.setGraphicsEffect(shadow)

    def setup_ui(self):
        # Layout principal du Dialogue
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20) # Espace pour l'ombre

        # --- LE CONTENEUR (LA CARTE) ---
        self.container = QFrame()
        # AUCUNE BORDURE ICI : border: none
        self.container.setStyleSheet("background-color: white; border-radius: 25px; border: none;")
        self._add_ultra_soft_shadow(self.container)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(40, 30, 40, 40)
        layout.setSpacing(20)

        # --- BARRE SUPÉRIEURE (TITRE + FERMER) ---
        top_bar = QHBoxLayout()
        title = QLabel("Nouveau Partenaire")
        title.setStyleSheet("font-size: 22px; font-weight: 900; color: #0f172a; border: none;")
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setFixedSize(32, 32)
        self.btn_close.clicked.connect(self.reject) # Ferme sans enregistrer
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9; color: #64748b; 
                border-radius: 16px; font-size: 14px; font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #fee2e2; color: #ef4444; }
        """)
        
        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_close)
        layout.addLayout(top_bar)

        layout.addSpacing(10)

        # --- CHAMPS DE SAISIE (STYLE UNDERLINE / SANS CADRE) ---
        self.nom = self._create_field("Nom de la compagnie", "ex: Allianz")
        self.code = self._create_field("Code interne", "ex: ALZ-01")
        self.email = self._create_field("Email de contact", "contact@exemple.com")
        self.tel = self._create_field("Téléphone", "+229 ...")

        layout.addWidget(self.nom)
        layout.addWidget(self.code)
        layout.addWidget(self.email)
        layout.addWidget(self.tel)

        layout.addSpacing(20)

        # --- BOUTON DE SAUVEGARDE ---
        self.btn_save = QPushButton("Enregistrer la compagnie")
        self.btn_save.setFixedHeight(50)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; color: white; font-weight: 800;
                border-radius: 12px; font-size: 14px; border: none;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        layout.addWidget(self.btn_save)

        self.main_layout.addWidget(self.container)

    def _create_field(self, label, placeholder):
        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)

        lbl = QLabel(label)
        lbl.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: 800; text-transform: uppercase; border: none;")
        
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setFixedHeight(40)
        # Bordure uniquement en bas pour un look minimaliste "Zero Border"
        edit.setStyleSheet("""
            QLineEdit {
                background: #f8fafc; border: none;
                border-bottom: 2px solid #f1f5f9; 
                padding-left: 10px; color: #1e293b; font-size: 14px;
            }
            QLineEdit:focus { 
                border-bottom: 2px solid #3b82f6; 
                background: white; 
            }
        """)
        
        lay.addWidget(lbl)
        lay.addWidget(edit)
        return container

    def get_data(self):
        """Récupère les informations saisies"""
        return {
            "nom": self.nom.findChild(QLineEdit).text(),
            "code": self.code.findChild(QLineEdit).text(),
            "email": self.email.findChild(QLineEdit).text(),
            "telephone": self.tel.findChild(QLineEdit).text()
        }