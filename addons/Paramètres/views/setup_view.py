# from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
#                              QPushButton, QLabel, QFrame, QGraphicsDropShadowEffect)
# from PySide6.QtCore import Qt
# from PySide6.QtGui import QColor, QFont

# class SetupView(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Configuration Initiale - AMS Project")
#         self.setFixedSize(450, 650)
#         self.setAttribute(Qt.WA_TranslucentBackground) # Pour les coins arrondis fluides
#         self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint) # Optionnel: sans bordures

#         self.init_ui()

#     def init_ui(self):
#         # Layout principal pour centrer le cadre
#         main_layout = QVBoxLayout(self)
        
#         # Cadre principal (Le "Card" design)
#         self.container = QFrame()
#         self.container.setObjectName("MainContainer")
#         self.container.setStyleSheet("""
#             #MainContainer {
#                 background-color: #ffffff;
#                 border-radius: 15px;
#                 border: 1px solid #dcdde1;
#             }
#             QLabel {
#                 color: #2f3640;
#                 font-family: 'Segoe UI', sans-serif;
#             }
#             QLineEdit {
#                 padding: 12px;
#                 border: 2px solid #f5f6fa;
#                 border-radius: 8px;
#                 background-color: #f5f6fa;
#                 font-size: 14px;
#                 color: #2f3640;
#             }
#             QLineEdit:focus {
#                 border: 2px solid #3498db;
#                 background-color: #ffffff;
#             }
#             QPushButton {
#                 background-color: #2ecc71;
#                 color: white;
#                 padding: 12px;
#                 border-radius: 8px;
#                 font-weight: bold;
#                 font-size: 15px;
#             }
#             QPushButton:hover {
#                 background-color: #27ae60;
#             }
#             QPushButton:pressed {
#                 background-color: #1e8449;
#             }
#         """)

#         # Ombre portée
#         shadow = QGraphicsDropShadowEffect(self)
#         shadow.setBlurRadius(20)
#         shadow.setXOffset(0)
#         shadow.setYOffset(5)
#         shadow.setColor(QColor(0, 0, 0, 80))
#         self.container.setGraphicsEffect(shadow)

#         # Layout interne du conteneur
#         layout = QVBoxLayout(self.container)
#         layout.setContentsMargins(40, 40, 40, 40)
#         layout.setSpacing(15)

#         # Titre et Sous-titre
#         title_bar = QHBoxLayout()
#         title_bar.addStretch()
#         self.btn_close = QPushButton("✕")
#         self.btn_close.setObjectName("BtnClose")
#         self.btn_close.setFixedSize(30, 30)
#         self.btn_close.setCursor(Qt.PointingHandCursor)
#         self.btn_close.clicked.connect(self.close) # Ferme la fenêtre
#         title = QLabel("Initialisation")
#         title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2ecc71;")
#         title.setAlignment(Qt.AlignCenter)
#         title_bar.addWidget(self.btn_close)
#         layout.addLayout(title_bar)
        
#         subtitle = QLabel("Créez le compte administrateur principal")
#         subtitle.setStyleSheet("font-size: 13px; color: #7f8c8d; margin-bottom: 10px;")
#         subtitle.setAlignment(Qt.AlignCenter)

#         # Champs de saisie
#         self.username = QLineEdit()
#         self.username.setPlaceholderText("Nom d'utilisateur (admin)")
        
#         self.full_name = QLineEdit()
#         self.full_name.setPlaceholderText("Nom complet (ex: Jean Dupont)")

#         self.email = QLineEdit()
#         self.email.setPlaceholderText("Adresse Email")

#         self.password = QLineEdit()
#         self.password.setPlaceholderText("Mot de passe sécurisé")
#         self.password.setEchoMode(QLineEdit.Password)

#         # Bouton d'action
#         self.btn_create = QPushButton("Lancer l'installation")
#         self.btn_create.setCursor(Qt.PointingHandCursor)

#         # Ajout des widgets au layout
#         layout.addWidget(title)
#         layout.addWidget(subtitle)
#         layout.addSpacing(10)
#         layout.addWidget(QLabel("<b>Identifiants</b>"))
#         layout.addWidget(self.username)
#         layout.addWidget(self.full_name)
#         layout.addWidget(self.email)
#         layout.addWidget(QLabel("<b>Sécurité</b>"))
#         layout.addWidget(self.password)
#         layout.addSpacing(20)
#         layout.addWidget(self.btn_create)
#         layout.addStretch()

#         main_layout.addWidget(self.container)


import sys
import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QFrame, QGraphicsDropShadowEffect,
                             QSizePolicy, QGridLayout, QApplication)
from PySide6.QtCore import Qt, Signal, QPoint, QPropertyAnimation, QSize
from PySide6.QtGui import QColor, QPixmap

class SetupView(QWidget):
    # Signal pour notifier le contrôleur que la configuration est prête
    setup_submitted = Signal(str, str, str, str)
    
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        
        # --- CONFIGURATION FENÊTRE ---
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(1000, 700)
        self.old_pos = None
        
        # L'image doit être dans le même dossier que ce fichier .py
        self.image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "car_orange.png")
        
        self.setup_ui()

    def setup_ui(self):
        # CORRECTION : Ajout de self. devant main_layout pour qu'il soit accessible partout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)

        # --- LE CONTENEUR PRINCIPAL ---
        self.body = QFrame()
        self.body.setObjectName("MainBody")
        self.body.setStyleSheet("#MainBody { background-color: white; border-radius: 10px; }")
        
        shadow = QGraphicsDropShadowEffect(blurRadius=60, xOffset=0, yOffset=20, color=QColor(0, 0, 0, 45))
        self.body.setGraphicsEffect(shadow)

        layout_h = QHBoxLayout(self.body)
        layout_h.setContentsMargins(0, 0, 0, 0)
        layout_h.setSpacing(0)

        # --- PANNEAU GAUCHE : LE FORMULAIRE ---
        self.left_panel = QWidget()
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(70, 60, 70, 60)

        config_label = QLabel("Configuration")
        config_label.setStyleSheet("color: #6b7280; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 2px;")
        
        title_label = QLabel("Compte Administrateur")
        title_label.setStyleSheet("color: #111827; font-size: 32px; font-weight: 800;")

        self.username = self._create_input("Nom d'utilisateur", "👤")
        self.full_name = self._create_input("Nom complet", "💳")
        self.email = self._create_input("Adresse Email", "✉")
        self.password = self._create_input("Mot de passe", "🔒", is_password=True)

        # Champs de saisie
        # self.username = QLineEdit()
        # self.username.setPlaceholderText("Nom d'utilisateur (admin)")
        
        # self.full_name = QLineEdit()
        # self.full_name.setPlaceholderText("Nom complet (ex: Jean Dupont)")

        # self.email = QLineEdit()
        # self.email.setPlaceholderText("Adresse Email")

        # self.password = QLineEdit()
        # self.password.setPlaceholderText("Mot de passe sécurisé")
        # self.password.setEchoMode(QLineEdit.Password)

        self.btn_create = QPushButton("LANCER L'INSTALLATION")
        self.btn_create.setFixedHeight(60)
        self.btn_create.setCursor(Qt.PointingHandCursor)
        self.btn_create.clicked.connect(self.handle_setup_submission)
        self.btn_create.setStyleSheet("""
            QPushButton {
                background-color: #064e3b; color: white; border-radius: 18px;
                font-weight: 800; font-size: 13px; letter-spacing: 2px;
            }
            QPushButton:hover { background-color: #059669; }
        """)

        left_layout.addWidget(config_label)
        left_layout.addWidget(title_label)
        left_layout.addSpacing(40)
        left_layout.addWidget(self.username)
        left_layout.addSpacing(15)
        left_layout.addWidget(self.full_name)
        left_layout.addSpacing(15)
        left_layout.addWidget(self.email)
        left_layout.addSpacing(15)
        left_layout.addWidget(self.password)
        left_layout.addSpacing(40)
        left_layout.addWidget(self.btn_create)
        left_layout.addStretch()

        # --- PANNEAU DROIT : IMAGE + OVERLAY NOIR ---
        self.right_panel = QFrame()
        self.right_panel.setFixedWidth(450)
        self.right_panel.setStyleSheet("border-top-right-radius: 10px; border-bottom-right-radius: 10px;")
        
        right_grid = QGridLayout(self.right_panel)
        right_grid.setContentsMargins(0, 0, 0, 0)

        # 1. Image
        self.img_label = QLabel()
        self.img_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.img_label.setScaledContents(True)
        
        if os.path.exists(self.image_path):
            self.img_label.setPixmap(QPixmap(self.image_path))
        else:
            self.img_label.setStyleSheet("background-color: #111827; border-top-right-radius: 10px; border-bottom-right-radius: 10px;")

        # 2. Overlay Noir Légèrement transparent
        overlay = QFrame()
        overlay.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 0.7); 
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)
        
        overlay_layout = QVBoxLayout(overlay)
        overlay_layout.setContentsMargins(60, 80, 60, 80)

        # Bouton Fermer
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.clicked.connect(self.close)
        self.btn_close.setStyleSheet("QPushButton { border: none; color: white; font-size: 18px; background: none; }")
        
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        top_bar.addWidget(self.btn_close)
        
        main_title = QLabel("AMS\nPROJECT.")
        main_title.setStyleSheet("color: white; font-size: 50px; font-weight: 900; line-height: 1; background: transparent;")

        overlay_layout.addLayout(top_bar)
        overlay_layout.addSpacing(20)
        overlay_layout.addWidget(main_title)
        overlay_layout.addStretch()
        
        right_grid.addWidget(self.img_label, 0, 0)
        right_grid.addWidget(overlay, 0, 0)

        # Assemblage
        layout_h.addWidget(self.left_panel)
        layout_h.addWidget(self.right_panel)
        
        # Cette ligne ne posera plus d'erreur
        self.main_layout.addWidget(self.body)

    def _create_input(self, placeholder, icon, is_password=False):
        frame = QFrame()
        frame.setFixedHeight(55)
        frame.setStyleSheet("""
            QFrame { background: #f9fafb; border: 1px solid #f3f4f6; border-radius: 15px; } 
            QFrame:focus-within { border-color: #10b981; background: white; }
        """)
        
        l = QHBoxLayout(frame)
        l.setContentsMargins(15, 0, 15, 0)
        
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 16px; background: none;")
        
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        if is_password: 
            edit.setEchoMode(QLineEdit.EchoMode.Password)
        edit.setStyleSheet("border: none; background: transparent; color: #1f2937;")
        
        l.addWidget(icon_lbl)
        l.addWidget(edit)
        
        # --- L'ASTUCE POUR NE PAS TOUCHER AU CONTROLEUR ---
        # On ajoute une méthode .text() dynamiquement au Frame
        frame.text = lambda: edit.text()
        
        # Optionnel : si votre contrôleur utilise aussi .setText()
        frame.setText = lambda val: edit.setText(val)
        
        # On garde quand même la référence au champ si besoin
        frame.field = edit 
        
        return frame

    def handle_setup_submission(self):
        user = self.username.field.text().strip()
        name = self.full_name.field.text().strip()
        mail = self.email.field.text().strip()
        pwd = self.password.field.text().strip()
        
        if user and pwd:
            self.setup_submitted.emit(user, name, mail, pwd)
        else:
            self.shake_window()

    def shake_window(self):
        animation = QPropertyAnimation(self, b"pos")
        animation.setDuration(50); animation.setLoopCount(5)
        curr = self.pos()
        animation.setKeyValueAt(0, curr); animation.setKeyValueAt(0.5, curr + QPoint(8, 0)); animation.setKeyValueAt(1, curr)
        animation.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event): self.old_pos = None