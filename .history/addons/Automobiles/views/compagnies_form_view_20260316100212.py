from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QGraphicsDropShadowEffect, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class FormulaireCreationCompagnie(QDialog):
    def __init__(self, parent=None, controller=None, current_user=None):
        super().__init__(parent)
        self.controller = controller
        self.user = current_user
        
        # Configuration pour le look "Air" sans bordures système
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
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

        # --- CARTE PRINCIPALE ---
        self.container = QFrame()
        self.container.setStyleSheet("background-color: white; border-radius: 30px; border: none;")
        self._add_glow_effect(self.container)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(40, 30, 40, 45)
        layout.setSpacing(20)

        # --- BARRE DE TITRE & FERMETURE ---
        top_bar = QHBoxLayout()
        title = QLabel("Nouveau Partenaire")
        title.setStyleSheet("font-size: 24px; font-weight: 900; color: #0f172a; border: none;")
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setFixedSize(35, 35)
        self.btn_close.clicked.connect(self.reject)
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

        # --- CHAMPS : IDENTITÉ ---
        self.nom = self._create_field("Nom de la compagnie", "ex: AXA Assurance")
        self.code = self._create_field("Code Identifiant", "ex: AXA-001")
        layout.addWidget(self.nom)
        layout.addWidget(self.code)

        # --- CHAMPS : GESTION FLOTTE (HORIZONTAL) ---
        flotte_label = QLabel("NUMÉROTATION DE FLOTTE")
        flotte_label.setStyleSheet("color: #3b82f6; font-size: 10px; font-weight: 900; letter-spacing: 1.5px; margin-top: 10px;")
        layout.addWidget(flotte_label)

        flotte_layout = QHBoxLayout()
        flotte_layout.setSpacing(15)
        
        self.num_debut = self._create_field_minimal("Début", "001")
        self.num_fin = self._create_field_minimal("Fin", "999")
        
        flotte_layout.addWidget(self.num_debut)
        flotte_layout.addWidget(self.num_fin)
        layout.addLayout(flotte_layout)

        layout.addSpacing(15)

        # --- BOUTON DE VALIDATION ---
        self.btn_save = QPushButton("Enregistrer le Partenaire")
        self.btn_save.setFixedHeight(55)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #0f172a; color: white; font-weight: 800;
                border-radius: 15px; font-size: 14px; border: none;
            }
            QPushButton:hover { background-color: #1e293b; }
        """)
        layout.addWidget(self.btn_save)

        self.main_layout.addWidget(self.container)

    def _create_field(self, label, placeholder):
        """Champ standard avec label au-dessus"""
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(5)
        
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: 800; text-transform: uppercase;")
        
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setFixedHeight(45)
        edit.setStyleSheet(self._input_style())
        
        l.addWidget(lbl)
        l.addWidget(edit)
        return w

    def _create_field_minimal(self, label, placeholder):
        """Champ plus compact pour la ligne de flotte"""
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(5)
        
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600;")
        
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setFixedHeight(42)
        edit.setStyleSheet(self._input_style())
        
        l.addWidget(lbl)
        l.addWidget(edit)
        return w

    def _input_style(self):
        return """
            QLineEdit {
                background-color: #f8fafc; border: none;
                border-bottom: 2px solid #f1f5f9; 
                border-radius: 8px; padding-left: 15px; 
                color: #1e293b; font-size: 14px;
            }
            QLineEdit:focus { 
                border-bottom: 2px solid #3b82f6; 
                background-color: white; 
            }
        """

    def get_data(self):
        """Extrait les données pour le contrôleur"""
        return {
            "nom": self.nom.findChild(QLineEdit).text(),
            "code": self.code.findChild(QLineEdit).text(),
            "flotte_debut": self.num_debut.findChild(QLineEdit).text(),
            "flotte_fin": self.num_fin.findChild(QLineEdit).text()
        }