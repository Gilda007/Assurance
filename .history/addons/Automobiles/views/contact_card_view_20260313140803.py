from math import perm
import os
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGraphicsDropShadowEffect)
from PySide6.QtGui import QColor, QPixmap, QPainter, QBrush, QPainterPath
from PySide6.QtCore import Qt, QPropertyAnimation, QRect

from addons.Automobiles.security.access_control import Permissions, SecurityManager

class ContactCard(QFrame):
    def __init__(self, contact, on_edit, on_delete, on_open_folder, user_role):
        super().__init__()
        self.contact = contact
        self.setFixedSize(160, 210)
        
        # 1. Chargement de l'image
        self.bg_pixmap = None
        if contact.photo_path and os.path.exists(contact.photo_path):
            self.bg_pixmap = QPixmap(contact.photo_path)

        # 2. Ombre portée (Animation de profondeur)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(4)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(self.shadow)

        self.anim_shadow = QPropertyAnimation(self.shadow, b"blurRadius")
        self.anim_shadow.setDuration(200)

        # 3. Layout et Overlay
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.overlay = QFrame()
        self.has_photo = self.bg_pixmap is not None
        
        # Couleurs adaptatives
        self.bg_normal = "rgba(0, 0, 0, 0.5)" if self.has_photo else "rgba(255, 255, 255, 0.9)"
        self.bg_hovecler = "rgba(0, 0, 0, 0.4)" if self.has_photo else "rgba(255, 255, 255, 1.0)"
        self.text_color = "white" if self.has_photo else "#1e293b"
        self.sub_text = "#e2e8f0" if self.has_photo else "#64748b"

        self.apply_overlay_style(self.bg_normal)

        # Contenu de l'overlay
        overlay_layout = QVBoxLayout(self.overlay)
        overlay_layout.setContentsMargins(20, 20, 20, 20)
        
        # Badge
        type_val = str(contact.type_contact or "Prospect")
        badge_bg = "#10b981" if "ASSURÉ" in type_val.upper() else "#f59e0b"
        badge = QLabel(type_val.upper())
        badge.setStyleSheet(f"background: {badge_bg}; color: white; font-size: 9px; font-weight: bold; padding: 4px 8px; border-radius: 6px;")
        overlay_layout.addWidget(badge, alignment=Qt.AlignRight)

        overlay_layout.addStretch()

        # Infos
        name = QLabel(f"{contact.nom}\n{contact.prenom or ''}")
        name.setStyleSheet(f"font-weight: 800; font-size: 18px; color: {self.text_color}; background: transparent; border: none;")
        overlay_layout.addWidget(name)

        tel = QLabel(f"📞 {contact.telephone or '---'}")
        tel.setStyleSheet(f"color: {self.sub_text}; font-size: 12px; background: transparent; border: none;")
        overlay_layout.addWidget(tel)

        # Barre d'actions
        # Barre d'actions corrigée
        # --- Barre d'actions ---
        actions_container = QFrame()
        actions_container.setStyleSheet("background: rgba(255,255,255,0.2); border-radius: 10px;")
        actions_layout = QHBoxLayout(actions_container)

        # Définition des actions : (Icône, Couleur Hover, Fonction, Permission)
        actions = [
            ("📂", "rgba(59, 130, 246, 0.5)", on_open_folder, None),
            ("✏️", "rgba(16, 185, 129, 0.5)", on_edit, Permissions.CONTACT_EDIT),
            ("🗑️", "rgba(239, 68, 68, 0.5)", on_delete, Permissions.CONTACT_DELETE)
        ]

        print(f"DEBUG CARD: user_role = {user_role}")
        print(f"DEBUG CARD: type de user_role = {type(user_role)}")
        for icon, h_bg, func, perm in actions:
            # On vérifie la permission
            # Si perm est None, c'est autorisé pour tous. Sinon on demande au SecurityManager
            role_str = str(user_role.role) if hasattr(user_role, 'role') else str(user_role)
            is_allowed = (perm is None) or SecurityManager.has_permission(role_str, perm)
            
            # DEBUG : Décommente la ligne suivante pour voir pourquoi ça bloque en console
            # print(f"DEBUG: Role={user_role} | Perm={perm} | Allowed={is_allowed}")

            if is_allowed:
                btn = QPushButton(icon)
                btn.setFixedSize(35, 35)
                btn.setCursor(Qt.PointingHandCursor)
                btn.setStyleSheet(f"""
                    QPushButton {{ 
                        background: transparent; 
                        border: none; 
                        font-size: 16px; 
                        color: {self.text_color}; 
                    }}
                    QPushButton:hover {{ 
                        background: {h_bg}; 
                        border-radius: 6px; 
                    }}
                """)
                
                # Correction du lambda pour éviter le crash 'bool' object is not callable
                btn.clicked.connect(lambda checked, f=func: f(self.contact))
                actions_layout.addWidget(btn)

        overlay_layout.addWidget(actions_container)
        self.main_layout.addWidget(self.overlay)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing) # Pour des bords lisses
        
        # 1. Créer le chemin arrondi (Rayon de 16px pour correspondre à l'overlay)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 16, 16)
        
        # 2. "Clit" le peintre sur ce chemin
        # Tout ce qui sera dessiné après sera limité à l'intérieur de ce chemin arrondi
        painter.setClipPath(path)
        
        if self.bg_pixmap:
            # Redimensionnement intelligent
            scaled = self.bg_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            
            # Centrage
            x = (scaled.width() - self.width()) // 2
            y = (scaled.height() - self.height()) // 2
            
            painter.drawPixmap(0, 0, scaled.copy(x, y, self.width(), self.height()))
        else:
            # Fond par défaut si pas de photo
            painter.setBrush(QColor("#f1f5f9"))
            painter.setPen(Qt.NoPen)
            painter.drawPath(path)

    def apply_overlay_style(self, bg_color, border="none"):
        self.overlay.setStyleSheet(f"QFrame {{ background-color: {bg_color}; border-radius: 16px; border: {border}; }}")

    def enterEvent(self, event):
        self.apply_overlay_style(self.bg_hovecler, "2px solid #3b82f6")
        self.anim_shadow.setEndValue(30)
        self.anim_shadow.start()

    def leaveEvent(self, event):
        self.apply_overlay_style(self.bg_normal)
        self.anim_shadow.setEndValue(15)
        self.anim_shadow.start()