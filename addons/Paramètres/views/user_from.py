from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QFrame, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor

class CustomUserForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 1. Fenêtre sans bordures et transparente
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.old_pos = None # Pour le déplacement
        self.setup_ui()

    def setup_ui(self):
        self.setFixedSize(450, 550)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # 2. Le "Conteneur" principal (La Card)
        self.container = QFrame()
        self.container.setObjectName("MainContainer")
        self.container.setStyleSheet("""
            #MainContainer {
                background-color: white;
                border-radius: 20px;
                border: 1px solid #dfe6e9;
            }
        """)
        
        # Ajout d'une ombre portée
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.container.setGraphicsEffect(shadow)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(30, 20, 30, 30)
        container_layout.setSpacing(15)

        # --- BARRE DE TITRE & FERMETURE ---
        title_bar = QHBoxLayout()
        title_label = QLabel("NOUVEL UTILISATEUR")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2d3436; border: none;")
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.clicked.connect(self.reject)
        self.btn_close.setStyleSheet("QPushButton { border: none; font-size: 16px; color: #b2bec3; } QPushButton:hover { color: #d63031; }")
        
        title_bar.addWidget(title_label)
        title_bar.addStretch()
        title_bar.addWidget(self.btn_close)
        container_layout.addLayout(title_bar)

        # --- CHAMPS DE SAISIE ---
        style_input = """
            QLineEdit, QComboBox {
                background-color: #f5f6fa;
                border: 2px solid #f5f6fa;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                color: #2d3436;
            }
            QLineEdit:focus { border: 2px solid #3498db; background-color: white; }
        """

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nom d'utilisateur")
        self.username_input.setStyleSheet(style_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Adresse Email (Requis)")
        self.email_input.setStyleSheet(style_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(style_input)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["agent", "admin"])
        self.role_combo.setStyleSheet(style_input)

        # Ajout au layout
        container_layout.addWidget(QLabel("Nom complet"))
        container_layout.addWidget(self.username_input)
        container_layout.addWidget(QLabel("Email professionnel"))
        container_layout.addWidget(self.email_input)
        container_layout.addWidget(QLabel("Sécurité"))
        container_layout.addWidget(self.password_input)
        container_layout.addWidget(QLabel("Rôle système"))
        container_layout.addWidget(self.role_combo)

        container_layout.addStretch()

        # --- BOUTON ENREGISTRER ---
        self.btn_save = QPushButton("CRÉER LE COMPTE")
        self.btn_save.setFixedHeight(50)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #0984e3;
                color: white;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #74b9ff; }
            QPushButton:pressed { background-color: #0984e3; }
        """)
        self.btn_save.clicked.connect(self.accept)
        container_layout.addWidget(self.btn_save)

        layout.addWidget(self.container)

    # --- MÉTHODES POUR DÉPLACER LA FENÊTRE ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def get_data(self):
        return {
            "username": self.username_input.text(),
            "email": self.email_input.text(),
            "password": self.password_input.text(),
            "role": self.role_combo.currentText()
        }