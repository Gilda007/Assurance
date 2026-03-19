
import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QFrame, QGraphicsDropShadowEffect,
                             QSizePolicy, QGridLayout)
from PySide6.QtCore import Qt, Signal, QPoint, QPropertyAnimation, QSize
from PySide6.QtGui import QColor, QPixmap, QRegion, QPainterPath

class LoginView(QWidget):
    # Signal attendu par le contrôleur (ajustez le nom si nécessaire, ex: login_requested)
    login_requested = Signal(str, str)
    
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        
        # --- CONFIGURATION FENÊTRE ---
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(1000, 700)
        self.old_pos = None
        
        # Chemin vers l'image logo.png
        self.image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.webp")
        
        self.setup_ui()

    def setup_ui(self):
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

        # --- PANNEAU GAUCHE : VISUEL (MCLAREN + OVERLAY) ---
        self.left_panel = QFrame()
        self.left_panel.setFixedWidth(480)
        self.left_panel.setStyleSheet("border-top-left-radius: 10px; border-bottom-left-radius: 10px; border-bottom-left-radius: 10px;")
        
        left_grid = QGridLayout(self.left_panel)
        left_grid.setContentsMargins(0, 0, 0, 0)

        # 1. Image de fond
        self.img_label = QLabel()
        self.img_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.img_label.setScaledContents(True)
        
        if os.path.exists(self.image_path):
            pixmap = QPixmap(self.image_path)
            # On simule l'effet "Cover"
            scaled_pixmap = pixmap.scaled(QSize(480, 700), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            self.img_label.setPixmap(scaled_pixmap)
        
        # Application du masque arrondi (Coins gauches)
        self.img_label.adjustSize()
        path = QPainterPath()
        path.addRoundedRect(self.img_label.rect(), 10, 10) 
        self.img_label.setMask(QRegion(path.toFillPolygon().toPolygon()))

        # 2. Overlay Noir
        overlay = QFrame()
        overlay.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(0, 0, 0, 0.5),   /* Noir intense en haut */
                    stop: 0.5 rgba(0, 0, 0, 0.4),  /* Milieu semi-transparent */
                    stop: 1 rgba(0, 0, 0, 1)     /* Presque transparent en bas */
                );
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
            }
        """)
        
        overlay_layout = QVBoxLayout(overlay)
        overlay_layout.setContentsMargins(60, 80, 60, 80)
        
        title_ams = QLabel("AMS\nPROJECT.")
        title_ams.setStyleSheet("color: white; font-size: 50px; font-weight: 900; line-height: 1; background: transparent;")
        
        desc = QLabel("L'intelligence au service de votre parc automobile.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #a7f3d0; font-size: 16px; font-weight: 300; background: transparent; margin-top: 20px;")

        overlay_layout.addWidget(title_ams)
        overlay_layout.addWidget(desc)
        overlay_layout.addStretch()

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

        # En-tête formulaire
        login_title = QLabel("Connexion")
        login_title.setStyleSheet("color: #111827; font-size: 32px; font-weight: 800;")
        
        login_sub = QLabel("Veuillez entrer vos identifiants pour continuer.")
        login_sub.setStyleSheet("color: #6b7280; font-size: 14px; margin-bottom: 30px;")

        # Champs (Compatibles avec .text())
        self.edit_user = self._create_input("Identifiant", "👤")
        self.edit_pass = self._create_input("Mot de passe", "🔒", True)

        self.btn_submit = QPushButton("SE CONNECTER")
        self.btn_submit.setFixedHeight(55)
        self.btn_submit.setCursor(Qt.PointingHandCursor)
        self.btn_submit.clicked.connect(self.handle_login_submission)
        self.btn_submit.setStyleSheet("""
            QPushButton {
                background-color: #064e3b; color: white; border-radius: 15px;
                font-weight: 800; font-size: 13px; letter-spacing: 2px;
            }
            QPushButton:hover { background-color: #059669; }
        """)

        right_layout.addLayout(h_close)
        right_layout.addSpacing(20)
        right_layout.addWidget(login_title)
        right_layout.addWidget(login_sub)
        right_layout.addWidget(self.edit_user)
        right_layout.addSpacing(15)
        right_layout.addWidget(self.edit_pass)
        right_layout.addSpacing(30)
        right_layout.addWidget(self.btn_submit)
        right_layout.addStretch()

        layout_h.addWidget(self.left_panel)
        layout_h.addWidget(self.right_panel)
        self.main_layout.addWidget(self.body)

    def _create_input(self, placeholder, icon, is_password=False):
        frame = QFrame()
        frame.setFixedHeight(55)
        frame.setStyleSheet("""
            QFrame { background: #f9fafb; border-radius: 10px; } 
            QFrame:focus-within { border-color: #059669; background: white; }
        """)
        l = QHBoxLayout(frame)
        l.setContentsMargins(15, 0, 15, 0)
        
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 16px; background: none;")
        
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        if is_password: edit.setEchoMode(QLineEdit.EchoMode.Password)
        edit.setStyleSheet("border: none; background: transparent; font-size: 14px; color: #1f2937;")
        
        l.addWidget(icon_lbl)
        l.addWidget(edit)
        
        # Compatibilité contrôleur
        frame.text = lambda: edit.text()
        frame.field = edit
        return frame

    def handle_login_submission(self):
        user = self.edit_user.text().strip()
        pwd = self.edit_pass.text().strip()
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