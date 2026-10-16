
"""
Vue de connexion - Style moderne "LOMETA"
Design : Image de fond urbaine + carte centrale en verre dépoli
Accent : Vert néon (#84cc16)
"""
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFrame, QGraphicsDropShadowEffect, QSizePolicy, QGridLayout,
    QCheckBox, QGraphicsBlurEffect, QGraphicsOpacityEffect
)
from PySide6.QtCore import (
    Qt, Signal, QPoint, QPropertyAnimation, QSize, QSettings,
    QEasingCurve, QTimer
)
from PySide6.QtGui import (
    QColor, QPixmap, QFont, QPainter, QLinearGradient, QBrush,
    QPen, QFontDatabase
)

import qtawesome as qta
import random
import glob

# ═══════════════════════════════════════════════════════════════════
# PALETTE & STYLES
# ═══════════════════════════════════════════════════════════════════

ACCENT = "#a3e635"        # Vert néon (lime)
ACCENT_HOVER = "#84cc16"
ACCENT_DARK = "#65a30d"
BG_DARK = "rgba(15, 23, 42, 0.85)"    # Carte sombre translucide
TEXT_LIGHT = "#ffffff"
TEXT_MUTED = "rgba(255, 255, 255, 0.65)"
FIELD_BG = "rgba(0, 0, 0, 0.4)"
FIELD_BORDER = "#4ade80"              # Bordure verte des champs


# ═══════════════════════════════════════════════════════════════════
# VUE PRINCIPALE
# ═══════════════════════════════════════════════════════════════════

class LoginView(QWidget):
    """Vue de connexion style LOMETA — carte en verre dépoli sur fond urbain."""
    
    login_requested = Signal(str, str, bool)
    
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        
        # ─── Configuration fenêtre (plein écran + frameless) ───
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setMinimumSize(1280, 720)
        self.old_pos = None
        
        # ═══════════════════════════════════════════════════════════
        # ROTATION D'IMAGES DE FOND
        # ═══════════════════════════════════════════════════════════
        self.background_images = self._discover_background_images()
        self.current_bg_index = 0
        self.current_pixmap = None       # Image actuellement affichée
        self.next_pixmap = None          # Image en cours de fondu
        self.fade_progress = 0.0         # 0.0 → 1.0 pendant la transition
        self._fade_progress_value = 0.0
        
        # Charger la première image tout de suite
        if self.background_images:
            self.current_pixmap = self._load_pixmap(self.background_images[0])
        
        # ─── Settings ───
        self.settings = QSettings("LOMETA", "Login")
        
        self.setup_ui()
        self.load_saved_session()
        
        # ✅ Démarrer la rotation toutes les 1 minute
        if len(self.background_images) > 1:
            self._bg_timer = QTimer(self)
            self._bg_timer.timeout.connect(self._rotate_background)
            self._bg_timer.start(60_000)   # 60 000 ms = 1 minute
        
        # ✅ Animation de fondu (créée une seule fois, réutilisée)
        self._fade_anim = QPropertyAnimation(self, b"fade_progress_prop")
        self._fade_anim.finished.connect(self._on_fade_finished)
        # ⚠️ On utilise une propriété Qt personnalisée ci-dessous

    # def _find_existing_image(self):
    #     for path in self.image_candidates:
    #         if os.path.exists(path):
    #             return path
    #     return None

    def _discover_background_images(self):
        """
        Découvre toutes les images de fond disponibles.
        Cherche dans plusieurs dossiers avec plusieurs extensions.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Dossiers à scanner
        search_dirs = [
            base_dir,
            os.path.join(base_dir, "backgrounds"),
            os.path.join(base_dir, "images", "backgrounds"),
            os.path.join(base_dir, "..", "..", "..", "assets", "backgrounds"),
        ]
        
        # Extensions supportées
        extensions = ["*.jpg", "*.jpeg", "*.png", "*.webp"]
        
        found = []
        for directory in search_dirs:
            if not os.path.isdir(directory):
                continue
            for ext in extensions:
                pattern = os.path.join(directory, f"login_bg*{ext[1:]}")
                found.extend(glob.glob(pattern))
                # Aussi : bg1.jpg, bg2.jpg, background_1.png...
                pattern = os.path.join(directory, f"background*{ext[1:]}")
                found.extend(glob.glob(pattern))
        
        # Dédupliquer (même chemin absolu)
        unique = list(dict.fromkeys(os.path.abspath(p) for p in found))
        
        if not unique:
            # Fallback : nom standard dans le dossier du fichier
            fallback = os.path.join(base_dir, "login_bg.jpg")
            if os.path.exists(fallback):
                unique.append(fallback)
        
        return unique


    def _load_pixmap(self, path):
        """Charge une image sans la scaler (le scaling se fait dans paintEvent)."""
        pix = QPixmap(path)
        if pix.isNull():
            return None
        return pix
    

    def _get_fade_progress(self):
        return self._fade_progress_value

    def _set_fade_progress(self, value):
        self._fade_progress_value = value
        self.update()  # redessine avec le fondu

    # Déclaration de la propriété Qt
    from PySide6.QtCore import Property as QtProperty

    fade_progress_prop = QtProperty(
        float,
        _get_fade_progress,
        _set_fade_progress,
    )

    # def _rotate_background(self):
    #     """Change l'image de fond avec un fondu de 1,5 seconde."""
    #     if len(self.background_images) <= 1:
    #         return
        
    #     # Ne pas rotation si une animation est déjà en cours
    #     if self._fade_anim.state() == QPropertyAnimation.Running:
    #         return
        
    #     # ─── Choisir une image différente ───
    #     old_index = self.current_bg_index
    #     new_index = old_index
    #     while new_index == old_index:
    #         new_index = random.randint(0, len(self.background_images) - 1)
    #     self.current_bg_index = new_index
        
    #     # ─── Préparer le fondu ───
    #     self.next_pixmap = self._load_pixmap(self.background_images[new_index])
    #     if self.next_pixmap is None:
    #         return
        
    #     # ─── Lancer l'animation ───
    #     self._fade_anim.stop()
    #     self._fade_anim.setDuration(3000)  # 1,5 s de transition
    #     self._fade_anim.setStartValue(0.0)
    #     self._fade_anim.setEndValue(1.0)
    #     self._fade_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
    #     # À la fin, l'image suivante devient l'image courante
    #     def on_finished():
    #         self.current_pixmap = self.next_pixmap
    #         self.next_pixmap = None
    #         self._fade_progress_value = 0.0
    #         self.update()
        
    #     try:
    #         self._fade_anim.finished.disconnect()
    #     except Exception:
    #         pass
    #     self._fade_anim.finished.connect(on_finished)
        
    #     self._fade_anim.start()

    def _rotate_background(self):
        """Change l'image de fond avec un fondu."""
        if len(self.background_images) <= 1:
            return
        
        if self._fade_anim.state() == QPropertyAnimation.Running:
            return
        
        # Choisir une image différente
        old_index = self.current_bg_index
        new_index = old_index
        while new_index == old_index:
            new_index = random.randint(0, len(self.background_images) - 1)
        self.current_bg_index = new_index
        
        # Préparer le fondu
        self.next_pixmap = self._load_pixmap(self.background_images[new_index])
        if self.next_pixmap is None:
            return
        
        # ✅ Plus besoin de disconnect : on connecte UNE SEULE FOIS dans __init__
        self._fade_anim.stop()
        self._fade_anim.setDuration(1500)
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._fade_anim.start()

    def _on_fade_finished(self):
        """Appelée à la fin du fondu — l'image suivante devient l'image courante."""
        self.current_pixmap = self.next_pixmap
        self.next_pixmap = None
        self._fade_progress_value = 0.0
        self.update()

    # ═══════════════════════════════════════════════════════════════
    # FOND : IMAGE URBAINE
    # ═══════════════════════════════════════════════════════════════
    
    # def paintEvent(self, event):
    #     """Peint l'image de fond (étirée sur toute la fenêtre)."""
    #     painter = QPainter(self)
    #     painter.setRenderHint(QPainter.Antialiasing)
    #     painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
    #     if self.image_path:
    #         pixmap = QPixmap(self.image_path)
    #         if not pixmap.isNull():
    #             scaled = pixmap.scaled(
    #                 self.size(),
    #                 Qt.AspectRatioMode.KeepAspectRatioByExpanding,
    #                 Qt.TransformationMode.SmoothTransformation,
    #             )
    #             # Centrer l'image
    #             x = (self.width() - scaled.width()) // 2
    #             y = (self.height() - scaled.height()) // 2
    #             painter.drawPixmap(x, y, scaled)
    #         else:
    #             # Fallback : dégradé sombre
    #             gradient = QLinearGradient(0, 0, 0, self.height())
    #             gradient.setColorAt(0, QColor("#0f172a"))
    #             gradient.setColorAt(1, QColor("#1e293b"))
    #             painter.fillRect(self.rect(), QBrush(gradient))
    #     else:
    #         # Pas d'image : dégradé sombre
    #         gradient = QLinearGradient(0, 0, 0, self.height())
    #         gradient.setColorAt(0, QColor("#0f172a"))
    #         gradient.setColorAt(1, QColor("#1e293b"))
    #         painter.fillRect(self.rect(), QBrush(gradient))
        
    #     # Overlay sombre pour faire ressortir la carte
    #     painter.fillRect(self.rect(), QColor(0, 0, 0, 80))
        
    #     super().paintEvent(event)
    
    def paintEvent(self, event):
        """Peint l'image de fond avec fondu entre deux images."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # ─── Image de fond (avec ou sans fondu) ───
        if self.current_pixmap:
            self._draw_pixmap_scaled(painter, self.current_pixmap, opacity=1.0)
        
        if self.next_pixmap:
            # Fondu progressif : opacity = valeur de la propriété (0 → 1)
            self._draw_pixmap_scaled(
                painter, self.next_pixmap,
                opacity=self._fade_progress_value,
            )
        
        # ─── Fallback si aucune image ───
        if not self.current_pixmap and not self.next_pixmap:
            gradient = QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0, QColor("#0f172a"))
            gradient.setColorAt(1, QColor("#1e293b"))
            painter.fillRect(self.rect(), QBrush(gradient))
        
        # ─── Overlay sombre pour faire ressortir la carte ───
        painter.fillRect(self.rect(), QColor(0, 0, 0, 80))
        
        super().paintEvent(event)


    def _draw_pixmap_scaled(self, painter, pixmap, opacity=1.0):
        """Dessine une pixmap scalée et centrée avec une opacité donnée."""
        if pixmap is None or pixmap.isNull():
            return
        
        scaled = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        
        x = (self.width() - scaled.width()) // 2
        y = (self.height() - scaled.height()) // 2
        
        if opacity < 1.0:
            painter.save()
            painter.setOpacity(opacity)
            painter.drawPixmap(x, y, scaled)
            painter.restore()
        else:
            painter.drawPixmap(x, y, scaled)

    # ═══════════════════════════════════════════════════════════════
    # UI PRINCIPALE
    # ═══════════════════════════════════════════════════════════════
    
    def setup_ui(self):
        # Layout principal : la carte est centrée
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Stretch haut
        self.main_layout.addStretch(1)
        
        # Ligne horizontale : stretch + carte + stretch
        h_row = QHBoxLayout()
        h_row.addStretch(1)
        
        self.card = self._build_card()
        h_row.addWidget(self.card)
        
        h_row.addStretch(1)
        self.main_layout.addLayout(h_row)
        
        # Stretch bas
        self.main_layout.addStretch(1)
        
        # ─── Bouton fermer en haut à droite (absolu) ───
        self.btn_close = QPushButton("✕", self)
        self.btn_close.setFixedSize(36, 36)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.1);
                border: none;
                color: rgba(255,255,255,0.7);
                font-size: 16px;
                border-radius: 18px;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.8);
                color: white;
            }
        """)
        self.btn_close.clicked.connect(self.close)
    
    def resizeEvent(self, event):
        """Repositionne le bouton fermer en haut à droite."""
        super().resizeEvent(event)
        if hasattr(self, 'btn_close'):
            self.btn_close.move(self.width() - 56, 20)
    
    # ═══════════════════════════════════════════════════════════════
    # CARTE CENTRALE (verre dépoli)
    # ═══════════════════════════════════════════════════════════════
    
    def _build_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("LoginCard")
        card.setFixedSize(480, 620)
        card.setStyleSheet(f"""
            QFrame#LoginCard {{
                background: {BG_DARK};
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 24px;
            }}
        """)
        
        # Ombre portée
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(60)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 20)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(0)
        
        # ─── 1. Titre "LOG IN TO LOMETA" ───
        title = QLabel("LOG IN TO LOMETA")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            color: {TEXT_LIGHT};
            font-size: 24px;
            font-weight: 900;
            letter-spacing: 4px;
            background: transparent;
        """)
        layout.addWidget(title)
        
        layout.addSpacing(24)
        
        # ─── 2. Logo LOMETA (icône + texte) ───
        # logo_row = QHBoxLayout()
        # logo_row.setSpacing(10)
        # logo_row.addStretch()
        
        # # Icône voiture (FontAwesome)
        # logo_icon = QLabel()
        # try:
        #     icon = qta.icon('fa5s.car-side', color=ACCENT)
        #     logo_icon.setPixmap(icon.pixmap(QSize(48, 48)))
        # except Exception:
        #     logo_icon.setText("🚗")
        #     logo_icon.setStyleSheet(f"color: {ACCENT}; font-size: 40px;")
        # logo_row.addWidget(logo_icon)
        
        # # Texte LOMETA
        # logo_text = QLabel("LOMETA")
        # logo_text.setStyleSheet(f"""
        #     color: {TEXT_LIGHT};
        #     font-size: 32px;
        #     font-weight: 900;
        #     letter-spacing: 4px;
        #     background: transparent;
        # """)
        # logo_row.addWidget(logo_text)
        # logo_row.addStretch()
        
        # layout.addLayout(logo_row)
        
        layout.addSpacing(32)
        
        # ─── 3. Champ "Username or Email" ───
        self.edit_user = self._create_field(
            placeholder="Username or Email",
            icon_name="fa5s.user",
            is_password=False,
        )
        layout.addWidget(self.edit_user)
        
        layout.addSpacing(14)
        
        # ─── 4. Champ "Password" ───
        self.edit_pass = self._create_field(
            placeholder="Password",
            icon_name="fa5s.lock",
            is_password=True,
        )
        layout.addWidget(self.edit_pass)
        
        # ─── 5. Lien "Forgot Password?" ───
        layout.addSpacing(10)
        forgot_row = QHBoxLayout()
        forgot_row.addStretch()
        
        btn_forgot = QPushButton("Forgot Password?")
        btn_forgot.setCursor(Qt.PointingHandCursor)
        btn_forgot.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {ACCENT};
                font-size: 13px;
                font-weight: 500;
                padding: 0;
            }}
            QPushButton:hover {{
                color: {ACCENT_HOVER};
                text-decoration: underline;
            }}
        """)
        forgot_row.addWidget(btn_forgot)
        layout.addLayout(forgot_row)
        
        layout.addSpacing(24)
        
        # ─── 6. Bouton "LOG IN" ───
        self.btn_submit = QPushButton("LOG IN")
        self.btn_submit.setFixedHeight(56)
        self.btn_submit.setCursor(Qt.PointingHandCursor)
        self.btn_submit.clicked.connect(self.handle_login_submission)
        self.btn_submit.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT};
                color: #0f172a;
                border: none;
                border-radius: 28px;
                font-size: 15px;
                font-weight: 900;
                letter-spacing: 2px;
            }}
            QPushButton:hover {{
                background: {ACCENT_HOVER};
            }}
            QPushButton:pressed {{
                background: {ACCENT_DARK};
            }}
        """)
        layout.addWidget(self.btn_submit)
        
        layout.addSpacing(24)

        remember_row = QHBoxLayout()
        remember_row.setSpacing(0)
        
        self.remember_checkbox = QCheckBox("  Remember me")
        self.remember_checkbox.setCursor(Qt.PointingHandCursor)
        self.remember_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {TEXT_MUTED};
                font-size: 13px;
                font-weight: 500;
                spacing: 10px;
                background: transparent;
                padding: 4px 0;
            }}
            QCheckBox:hover {{
                color: {TEXT_LIGHT};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 5px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                background: rgba(0, 0, 0, 0.3);
            }}
            QCheckBox::indicator:hover {{
                border-color: {ACCENT};
                background: rgba(163, 230, 53, 0.1);
            }}
            QCheckBox::indicator:checked {{
                background: {ACCENT};
                border-color: {ACCENT};
                image: none;
            }}
        """)
        remember_row.addWidget(self.remember_checkbox)
        remember_row.addStretch()
        layout.addSpacing(20)

        layout.addLayout(remember_row)
        
        # ─── 7. Séparateur "Or continue with:" ───
        sep_row = QHBoxLayout()
        sep_row.setSpacing(12)
        
        line_left = QFrame()
        line_left.setFixedHeight(1)
        line_left.setStyleSheet("background: rgba(255,255,255,0.15);")
        sep_row.addWidget(line_left, 1)
        
        sep_text = QLabel("Or continue with:")
        sep_text.setStyleSheet(f"""
            color: {TEXT_MUTED};
            font-size: 12px;
            background: transparent;
        """)
        sep_row.addWidget(sep_text)
        
        line_right = QFrame()
        line_right.setFixedHeight(1)
        line_right.setStyleSheet("background: rgba(255,255,255,0.15);")
        sep_row.addWidget(line_right, 1)
        
        layout.addLayout(sep_row)
        
        layout.addSpacing(20)
        
        # ─── 8. Boutons SSO (Google, Apple, Microsoft) ───
        sso_row = QHBoxLayout()
        sso_row.setSpacing(20)
        sso_row.addStretch()
        
        sso_buttons = [
            ('fa5b.google', '#ffffff'),
            ('fa5b.apple', '#ffffff'),
            ('fa5b.microsoft', '#ffffff'),
        ]
        
        for icon_name, color in sso_buttons:
            btn = QPushButton()
            btn.setFixedSize(48, 48)
            btn.setCursor(Qt.PointingHandCursor)
            try:
                icon = qta.icon(icon_name, color=color)
                btn.setIcon(icon)
                btn.setIconSize(QSize(24, 24))
            except Exception:
                btn.setText("?")
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,0.08);
                    border: 1px solid rgba(255,255,255,0.12);
                    border-radius: 24px;
                }
                QPushButton:hover {
                    background: rgba(255,255,255,0.15);
                    border-color: rgba(255,255,255,0.25);
                }
            """)
            sso_row.addWidget(btn)
        
        sso_row.addStretch()
        layout.addLayout(sso_row)
        
        layout.addStretch(1)
        
        # ─── 9. Lien "Don't have an account? SIGN UP" ───
        signup_row = QHBoxLayout()
        signup_row.setSpacing(6)
        signup_row.addStretch()
        
        signup_text = QLabel("Don't have an account?")
        signup_text.setStyleSheet(f"""
            color: {TEXT_MUTED};
            font-size: 13px;
            background: transparent;
        """)
        signup_row.addWidget(signup_text)
        
        btn_signup = QPushButton("SIGN UP")
        btn_signup.setCursor(Qt.PointingHandCursor)
        btn_signup.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {ACCENT};
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 1px;
                padding: 0;
            }}
            QPushButton:hover {{
                color: {ACCENT_HOVER};
                text-decoration: underline;
            }}
        """)
        signup_row.addWidget(btn_signup)
        signup_row.addStretch()
        
        layout.addLayout(signup_row)
        
        return card
    
    # ═══════════════════════════════════════════════════════════════
    # CHLOMETA DE SAISIE (style LOMETA)
    # ═══════════════════════════════════════════════════════════════
    
    def _create_field(self, placeholder: str, icon_name: str, is_password: bool = False) -> QFrame:
        """
        Crée un champ arrondi avec bordure verte, icône à gauche,
        et (si password) un bouton œil à droite.
        """
        frame = QFrame()
        frame.setFixedHeight(52)
        frame.setStyleSheet(f"""
            QFrame {{
                background: {FIELD_BG};
                border: 1.5px solid {FIELD_BORDER};
                border-radius: 26px;
            }}
            QFrame:focus-within {{
                border: 2px solid {ACCENT};
                background: rgba(0, 0, 0, 0.55);
            }}
        """)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 0, 16, 0)
        layout.setSpacing(12)
        
        # ─── Icône gauche (FontAwesome) ───
        icon_lbl = QLabel()
        try:
            icon = qta.icon(icon_name, color=ACCENT)
            icon_lbl.setPixmap(icon.pixmap(QSize(18, 18)))
        except Exception:
            icon_lbl.setText("●")
            icon_lbl.setStyleSheet(f"color: {ACCENT}; font-size: 14px;")
        icon_lbl.setFixedSize(20, 20)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(icon_lbl)
        
        # ─── Champ de saisie ───
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        if is_password:
            edit.setEchoMode(QLineEdit.EchoMode.Password)
        edit.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                background: transparent;
                font-size: 14px;
                color: {TEXT_LIGHT};
                padding: 0;
                selection-background-color: {ACCENT};
                selection-color: #0f172a;
            }}
            QLineEdit::placeholder {{
                color: {TEXT_MUTED};
            }}
        """)
        layout.addWidget(edit, 1)
        
        # ─── Bouton œil (password uniquement) ───
        if is_password:
            btn_eye = QPushButton()
            btn_eye.setFixedSize(24, 24)
            btn_eye.setCursor(Qt.PointingHandCursor)
            btn_eye.setCheckable(True)
            btn_eye.setIcon(qta.icon('fa5s.eye', color=TEXT_MUTED))
            btn_eye.setIconSize(QSize(14, 14))
            btn_eye.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                }
                QPushButton:hover {
                    background: rgba(255,255,255,0.1);
                    border-radius: 12px;
                }
                QPushButton:checked {
                    background: rgba(163, 230, 53, 0.15);
                    border-radius: 12px;
                }
            """)
            
            def toggle_echo(checked):
                edit.setEchoMode(
                    QLineEdit.EchoMode.Normal if checked
                    else QLineEdit.EchoMode.Password
                )
                btn_eye.setIcon(
                    qta.icon(
                        'fa5s.eye-slash' if checked else 'fa5s.eye',
                        color=ACCENT if checked else TEXT_MUTED,
                    )
                )
            
            btn_eye.toggled.connect(toggle_echo)
            layout.addWidget(btn_eye)
        
        # ─── API de compatibilité ───
        frame.text = lambda: edit.text()
        frame.field = edit
        frame.clear = lambda: edit.clear()
        
        return frame
    
    # ═══════════════════════════════════════════════════════════════
    # LOGIQUE MÉTIER
    # ═══════════════════════════════════════════════════════════════
    
    def shake_window(self):
        """Animation de secousse en cas d'erreur."""
        anim = QPropertyAnimation(self, b"pos")
        anim.setDuration(50)
        anim.setLoopCount(5)
        curr = self.pos()
        anim.setKeyValueAt(0, curr)
        anim.setKeyValueAt(0.25, curr + QPoint(10, 0))
        anim.setKeyValueAt(0.5, curr + QPoint(-10, 0))
        anim.setKeyValueAt(0.75, curr + QPoint(10, 0))
        anim.setKeyValueAt(1, curr)
        anim.setEasingCurve(QEasingCurve.Type.Linear)
        anim.start()
        self._shake_anim = anim
    
    # ─── Déplacement de la fenêtre par la souris ───
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
    
    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
    
    def mouseReleaseEvent(self, event):
        self.old_pos = None
    
    # ─── Session sauvegardée ───
    def load_saved_session(self):
        username = self.settings.value("username", "")
        remember = self.settings.value("remember", False, type=bool)
        
        if remember and username:
            self.edit_user.field.setText(username)
            self.edit_pass.field.setFocus()
    
    def save_session(self, username, remember):
        if remember:
            self.settings.setValue("username", username)
            self.settings.setValue("remember", True)
        else:
            self.settings.remove("username")
            self.settings.setValue("remember", False)
    
    def handle_login_submission(self):
        """Soumet le formulaire de connexion."""
        user = self.edit_user.text().strip()
        pwd = self.edit_pass.text().strip()
        remember = self.remember_checkbox.isChecked()  # Pas de checkbox visible dans la maquette
        
        if user and pwd:
            self.save_session(user, remember)
            self.login_requested.emit(user, pwd, remember)
        else:
            self.shake_window()
    
    def show_error(self, message: str):
        """Affiche une erreur (secousse + tooltip)."""
        self.shake_window()
