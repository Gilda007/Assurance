from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QFrame, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QColor

class LoginView(QWidget):
    login_requested = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connexion - AMS Project")
        self.setFixedSize(400, 600)
        
        # 1. Fenêtre sans bordures et arrière-plan transparent
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint) 

        # Pour permettre le déplacement de la fenêtre
        self.old_pos = None

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        self.container = QFrame()
        self.container.setObjectName("LoginContainer")
        self.container.setStyleSheet("""
            #LoginContainer {
                background-color: #ffffff;
                border-radius: 15px;
                border: 1px solid #dcdde1;
            }
            #BtnClose {
                background-color: transparent;
                color: #7f8c8d;
                font-size: 18px;
                font-weight: bold;
                border: none;
            }
            #BtnClose:hover {
                color: #e74c3c;
            }
            QLineEdit {
                padding: 12px;
                border: 2px solid #f5f6fa;
                border-radius: 8px;
                background-color: #f5f6fa;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #ffffff;
            }
            QPushButton#MainBtn {
                background-color: #3498db;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
            }
        """)

        # Ombre
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.container)
        
        # --- BARRE DE TITRE PERSONNALISÉE (Bouton Fermer) ---
        title_bar = QHBoxLayout()
        title_bar.addStretch()
        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("BtnClose")
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.clicked.connect(self.close) # Ferme la fenêtre
        title_bar.addWidget(self.btn_close)
        layout.addLayout(title_bar)
        # ----------------------------------------------------

        inner_layout = QVBoxLayout()
        inner_layout.setContentsMargins(30, 0, 30, 30)
        inner_layout.setSpacing(15)

        title = QLabel("AMS-AUTO")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #3498db;")
        title.setAlignment(Qt.AlignCenter)
        
        self.username = QLineEdit()
        self.username.setPlaceholderText("Nom d'utilisateur")
        
        self.password = QLineEdit()
        self.password.setPlaceholderText("Mot de passe")
        self.password.setEchoMode(QLineEdit.Password)

        self.btn_login = QPushButton("Se connecter")
        self.btn_login.setObjectName("MainBtn")
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.clicked.connect(self.emit_login)

        inner_layout.addWidget(title)
        inner_layout.addSpacing(20)
        inner_layout.addWidget(self.username)
        inner_layout.addWidget(self.password)
        inner_layout.addSpacing(10)
        inner_layout.addWidget(self.btn_login)
        inner_layout.addStretch()

        layout.addLayout(inner_layout)
        main_layout.addWidget(self.container)

    # --- LOGIQUE POUR DÉPLACER LA FENÊTRE SANS BORDURES ---
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
    # -----------------------------------------------------

    def emit_login(self):
        self.login_requested.emit(self.username.text(), self.password.text())