from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QGraphicsDropShadowEffect, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class FormulaireCreationCompagnie(QDialog):
    def __init__(self, parent=None, controller=None, current_user=None):
        super().__init__(parent)
        self.controller = controller
        self.user = current_user
        
        # --- CONFIGURATION DU DIALOGUE (LOOK MODERNE SANS CADRE) ---
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setup_ui()

    def _add_glow_effect(self, widget):
        """Ajoute une ombre très diffuse pour remplacer les bordures"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 10)
        widget.setGraphicsEffect(shadow)

    def setup_ui(self):
        # Layout principal de la fenêtre (ajoute de la marge pour l'ombre)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)

        # --- CONTENEUR PRINCIPAL (CARTE BLANCHE) ---
        self.container = QFrame()
        self.container.setStyleSheet("background-color: white; border-radius: solid v10px; border: none;")
        self._add_glow_effect(self.container)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(40, 30, 40, 45)
        layout.setSpacing(20)

        # --- HEADER : TITRE ET BOUTON FERMER ---
        top_bar = QHBoxLayout()
        title = QLabel("Nouveau Partenaire")
        title.setStyleSheet("font-size: 24px; font-weight: 900; color: #0f172a; border: none;")
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setFixedSize(35, 35)
        self.btn_close.clicked.connect(self.reject) # Ferme sans valider
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #f8fafc; color: #64748b; 
                border-radius: 17px; font-size: 14px; font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #fee2e2; color: #ef4444; }
        """)
        
        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_close)
        layout.addLayout(top_bar)

        layout.addSpacing(10)

        # --- CHAMPS : INFORMATIONS GÉNÉRALES ---
        self.nom = self._create_modern_field("Nom de la compagnie", "ex: Allianz Bénin")
        self.code = self._create_modern_field("Code Identifiant", "ex: ALZ-001")
        self.email = self._create_modern_field("Email de contact", "contact@allianz.bj")
        
        layout.addWidget(self.nom)
        layout.addWidget(self.code)
        layout.addWidget(self.email)

        # --- SECTION : GESTION DE LA FLOTTE (HORIZONTAL) ---
        flotte_section = QVBoxLayout()
        flotte_section.setSpacing(10)
        
        flotte_title = QLabel("NUMÉROTATION DE LA FLOTTE")
        flotte_title.setStyleSheet("color: #3b82f6; font-size: 10px; font-weight: 900; letter-spacing: 1.5px;")
        flotte_section.addWidget(flotte_title)

        flotte_layout = QHBoxLayout()
        flotte_layout.setSpacing(15)
        
        self.num_debut = self._create_minimal_input("N° Début", "001")
        self.num_fin = self._create_minimal_input("N° Fin", "999")
        
        flotte_layout.addWidget(self.num_debut)
        flotte_layout.addWidget(self.num_fin)
        flotte_section.addLayout(flotte_layout)
        
        layout.addLayout(flotte_section)

        layout.addSpacing(15)

        # --- BOUTON DE VALIDATION ---
        self.btn_save = QPushButton("CRÉER LE PARTENAIRE")
        self.btn_save.setFixedHeight(55)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #0f172a; color: white; font-weight: 800;
                border-radius: 15px; font-size: 14px; border: none;
            }
            QPushButton:hover { background-color: #1e293b; }
        """)
        # Important: Le signal .clicked.connect(self.accept) sera géré dans on_add_click
        layout.addWidget(self.btn_save)

        self.main_layout.addWidget(self.container)

    def _create_modern_field(self, label, placeholder):
        """Crée un champ complet avec label discret"""
        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)

        lbl = QLabel(label)
        lbl.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: 800; text-transform: uppercase; border: none;")
        
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setFixedHeight(45)
        edit.setStyleSheet(self._get_input_style())
        
        lay.addWidget(lbl)
        lay.addWidget(edit)
        return container

    def _create_minimal_input(self, label, placeholder):
        """Crée un champ compact pour la ligne de flotte"""
        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)

        lbl = QLabel(label)
        lbl.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600; border: none;")
        
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setFixedHeight(42)
        edit.setStyleSheet(self._get_input_style())
        
        lay.addWidget(lbl)
        lay.addWidget(edit)
        return container

    def _get_input_style(self):
        """Style commun pour tous les champs : zéro bordure sauf en bas au focus"""
        return """
            QLineEdit {
                background-color: #f8fafc; 
                border: none;
                border-bottom: 2px solid #f1f5f9; 
                border-radius: 8px; 
                padding-left: 15px; 
                color: #1e293b; 
                font-size: 14px;
            }
            QLineEdit:focus { 
                border-bottom: 2px solid #3b82f6; 
                background-color: white; 
            }
        """

    def get_data(self):
        """Récupère toutes les données du formulaire pour le dictionnaire de sortie"""
        return {
            "nom": self.nom.findChild(QLineEdit).text(),
            "code": self.code.findChild(QLineEdit).text(),
            "email": self.email.findChild(QLineEdit).text(),
            "flotte_debut": self.num_debut.findChild(QLineEdit).text(),
            "flotte_fin": self.num_fin.findChild(QLineEdit).text()
        }