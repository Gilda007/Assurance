import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QFrame, QGraphicsDropShadowEffect,
                             QSizePolicy, QGridLayout)
from PySide6.QtCore import Qt, Signal, QPoint, QPropertyAnimation
from PySide6.QtGui import QColor, QPixmap

class LoginView(QWidget):
    login_requested = Signal(str, str)
    
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        
        # --- CONFIGURATION FENÊTRE ---
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(1000, 700)
        self.old_pos = None
        
        # Chemin direct puisque l'image est dans le même répertoire
        # On utilise abspath pour être sûr que Python la trouve quel que soit le terminal
        self.image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.webp")
        
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Conteneur principal blanc avec coins arrondis
        self.body = QFrame()
        self.body.setStyleSheet("background-color: white; border-radius: 40px;")
        
        shadow = QGraphicsDropShadowEffect(blurRadius=60, xOffset=0, yOffset=20, color=QColor(0, 0, 0, 45))
        self.body.setGraphicsEffect(shadow)

        layout_horizontal = QHBoxLayout(self.body)
        layout_horizontal.setContentsMargins(0, 0, 0, 0)
        layout_horizontal.setSpacing(0)

        # --- PANNEAU GAUCHE : VISUEL ---
        self.left_panel = QFrame()
        self.left_panel.setFixedWidth(480)
        # Grid pour superposer l'image et le filtre
        left_grid = QGridLayout(self.left_panel)
        left_grid.setContentsMargins(0, 0, 0, 0)

        # 1. L'image (Correction de l'erreur AttributeError)
        self.img_label = QLabel()
        self.img_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.img_label.setScaledContents(True) # Pour que l'image remplisse le label
        
        if os.path.exists(self.image_path):
            pixmap = QPixmap(self.image_path)
            self.img_label.setPixmap(pixmap)
        else:
            self.img_label.setText("Image introuvable")
            self.img_label.setStyleSheet("color: white; background-color: #022c22; border-top-left-radius: 40px;")

        # 2. Le filtre sombre (Overlay)
        overlay = QFrame()
        overlay.setStyleSheet("""
            QFrame {
                /* Noir avec 70% d'opacité (0,0,0 = Noir) */
                background-color: rgba(0, 0, 0, 0.7); 
            }
        """)
        
        # Texte sur l'overlay
        overlay_layout = QVBoxLayout(overlay)
        overlay_layout.setContentsMargins(60, 80, 60, 80)
        
        title = QLabel("AMS\nPROJECT.")
        title.setStyleSheet("color: white; font-size: 50px; font-weight: 900; background: transparent;")
        desc = QLabel("L'intelligence au service de votre parc automobile.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #a7f3d0; font-size: 16px; font-weight: 300; background: transparent;")

        overlay_layout.addWidget(title)
        overlay_layout.addWidget(desc)
        overlay_layout.addStretch()

        # Empilement dans la grille
        left_grid.addWidget(self.img_label, 0, 0)
        left_grid.addWidget(overlay, 0, 0)

        # --- PANNEAU DROIT : FORMULAIRE ---
        self.right_panel = QWidget()
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(80, 60, 80, 60)

        # Bouton fermer
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(30, 30)
        btn_close.clicked.connect(self.close)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setStyleSheet("QPushButton { border: none; color: #d1d5db; font-size: 18px; } QPushButton:hover { color: #ef4444; }")
        
        h_close = QHBoxLayout()
        h_close.addStretch()
        h_close.addWidget(btn_close)

        # Champs
        self.edit_user = self._create_input("Identifiant", "👤")
        self.edit_pass = self._create_input("Mot de passe", "🔒", True)

        self.btn_submit = QPushButton("SE CONNECTER")
        self.btn_submit.setFixedHeight(55)
        self.btn_submit.clicked.connect(self.handle_login)
        self.btn_submit.setStyleSheet("""
            QPushButton {
                background-color: #064e3b; color: white; border-radius: 15px;
                font-weight: 800; font-size: 13px; letter-spacing: 2px;
            }
            QPushButton:hover { background-color: #059669; }
        """)

        right_layout.addLayout(h_close)
        right_layout.addSpacing(30)
        right_layout.addWidget(QLabel("Connexion", styleSheet="color: #111827; font-size: 32px; font-weight: 800;"))
        right_layout.addSpacing(40)
        right_layout.addWidget(self.edit_user)
        right_layout.addSpacing(15)
        right_layout.addWidget(self.edit_pass)
        right_layout.addSpacing(30)
        right_layout.addWidget(self.btn_submit)
        right_layout.addStretch()

        layout_horizontal.addWidget(self.left_panel)
        layout_horizontal.addWidget(self.right_panel)
        main_layout.addWidget(self.body)

    def _create_input(self, placeholder, icon, is_password=False):
        frame = QFrame()
        frame.setStyleSheet("background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 12px;")
        frame.setFixedHeight(55)
        l = QHBoxLayout(frame)
        l.addWidget(QLabel(icon))
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        if is_password: edit.setEchoMode(QLineEdit.Password)
        edit.setStyleSheet("border: none; background: transparent; font-size: 14px; color: #1f2937;")
        l.addWidget(edit)
        frame.field = edit
        return frame

    def handle_login(self):
        user = self.edit_user.field.text().strip()
        pwd = self.edit_pass.field.text().strip()
        if user and pwd:
            self.login_requested.emit(user, pwd)
        else:
            self.shake_window()

    def shake_window(self):
        anim = QPropertyAnimation(self, b"pos")
        anim.setDuration(50)
        anim.setLoopCount(5)
        curr = self.pos()
        anim.setKeyValueAt(0, curr)
        anim.setKeyValueAt(0.5, curr + QPoint(8, 0))
        anim.setKeyValueAt(1, curr)
        anim.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event): self.old_pos = None

    def emit_login(self):
        self.login_requested.emit(self.username.text(), self.password.text())

