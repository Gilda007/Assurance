from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QFrame, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont

class SetupView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuration Initiale - AMS Project")
        self.setFixedSize(450, 650)
        self.setAttribute(Qt.WA_TranslucentBackground) # Pour les coins arrondis fluides
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint) # Optionnel: sans bordures

        self.init_ui()

    def init_ui(self):
        # Layout principal pour centrer le cadre
        main_layout = QVBoxLayout(self)
        
        # Cadre principal (Le "Card" design)
        self.container = QFrame()
        self.container.setObjectName("MainContainer")
        self.container.setStyleSheet("""
            #MainContainer {
                background-color: #ffffff;
                border-radius: 15px;
                border: 1px solid #dcdde1;
            }
            QLabel {
                color: #2f3640;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit {
                padding: 12px;
                border: 2px solid #f5f6fa;
                border-radius: 8px;
                background-color: #f5f6fa;
                font-size: 14px;
                color: #2f3640;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)

        # Ombre portée
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.container.setGraphicsEffect(shadow)

        # Layout interne du conteneur
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)

        # Titre et Sous-titre
        title_bar = QHBoxLayout()
        title_bar.addStretch()
        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("BtnClose")
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.clicked.connect(self.close) # Ferme la fenêtre
        title = QLabel("Initialisation")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2ecc71;")
        title.setAlignment(Qt.AlignCenter)
        title_bar.addWidget(self.btn_close)
        layout.addLayout(title_bar)
        
        subtitle = QLabel("Créez le compte administrateur principal")
        subtitle.setStyleSheet("font-size: 13px; color: #7f8c8d; margin-bottom: 10px;")
        subtitle.setAlignment(Qt.AlignCenter)

        # Champs de saisie
        self.username = QLineEdit()
        self.username.setPlaceholderText("Nom d'utilisateur (admin)")
        
        self.full_name = QLineEdit()
        self.full_name.setPlaceholderText("Nom complet (ex: Jean Dupont)")

        self.email = QLineEdit()
        self.email.setPlaceholderText("Adresse Email")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Mot de passe sécurisé")
        self.password.setEchoMode(QLineEdit.Password)

        # Bouton d'action
        self.btn_create = QPushButton("Lancer l'installation")
        self.btn_create.setCursor(Qt.PointingHandCursor)

        # Ajout des widgets au layout
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(10)
        layout.addWidget(QLabel("<b>Identifiants</b>"))
        layout.addWidget(self.username)
        layout.addWidget(self.full_name)
        layout.addWidget(self.email)
        layout.addWidget(QLabel("<b>Sécurité</b>"))
        layout.addWidget(self.password)
        layout.addSpacing(20)
        layout.addWidget(self.btn_create)
        layout.addStretch()

        main_layout.addWidget(self.container)