from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class AccountSettingsView(QWidget):
    def __init__(self, controller=None, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.setStyleSheet("background-color: #f8fafc;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(60, 60, 60, 60)
        main_layout.setSpacing(30)

        # --- TITRE DE SECTION ---
        title_v = QVBoxLayout()
        title = QLabel("Paramètres du profil")
        title.setStyleSheet("font-size: 28px; font-weight: 800; color: #0f172a;")
        subtitle = QLabel("Gérez vos informations personnelles et la sécurité de votre compte.")
        subtitle.setStyleSheet("color: #64748b; font-size: 14px;")
        title_v.addWidget(title)
        title_v.addWidget(subtitle)
        main_layout.addLayout(title_v)

        # --- GRILLE DE CONTENU ---
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)

        # 1. Carte Informations (Gauche)
        info_card = QFrame()
        info_card.setFixedWidth(350)
        info_card.setStyleSheet("background-color: white; border-radius: 15px; border: 1px solid #e2e8f0;")
        self._add_shadow(info_card)
        
        info_lay = QVBoxLayout(info_card)
        info_lay.setContentsMargins(25, 25, 25, 25)
        
        user_name = getattr(self.user, 'name', "Utilisateur")
        user_role = getattr(self.user, 'role', "Agent")

        avatar = QLabel(user_name[0].upper())
        avatar.setFixedSize(60, 60)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("""
            background-color: #3b82f6; color: white; 
            font-size: 24px; font-weight: bold; border-radius: 30px;
        """)
        
        u_label = QLabel(user_name)
        u_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #1e293b; margin-top: 10px;")
        r_label = QLabel(user_role.upper())
        r_label.setStyleSheet("color: #3b82f6; font-size: 11px; font-weight: 800; letter-spacing: 1px;")
        
        info_lay.addWidget(avatar, alignment=Qt.AlignCenter)
        info_lay.addWidget(u_label, alignment=Qt.AlignCenter)
        info_lay.addWidget(r_label, alignment=Qt.AlignCenter)
        info_lay.addSpacing(20)
        info_lay.addWidget(QLabel("Dernière connexion : Aujourd'hui"), alignment=Qt.AlignCenter)
        info_lay.addStretch()

        # 2. Carte Formulaire (Droite)
        form_card = QFrame()
        form_card.setStyleSheet("background-color: white; border-radius: 15px; border: 1px solid #e2e8f0;")
        self._add_shadow(form_card)
        
        form_lay = QVBoxLayout(form_card)
        form_lay.setContentsMargins(35, 35, 35, 35)
        form_lay.setSpacing(15)

        form_lay.addWidget(self._create_section_title("🔒 Sécurité du compte"))
        
        self.old_pass = self._create_input("Ancien mot de passe", True)
        self.new_pass = self._create_input("Nouveau mot de passe", True)
        self.conf_pass = self._create_input("Confirmer le mot de passe", True)
        
        form_lay.addWidget(self.old_pass)
        form_lay.addWidget(self.new_pass)
        form_lay.addWidget(self.conf_pass)
        
        form_lay.addSpacing(20)
        
        self.btn_save = QPushButton("Enregistrer les modifications")
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setFixedHeight(45)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #0f172a; color: white; font-weight: bold; 
                border-radius: 8px; font-size: 14px;
            }
            QPushButton:hover { background-color: #1e293b; }
        """)
        
        form_lay.addWidget(self.btn_save)
        form_lay.addStretch()

        content_layout.addWidget(info_card)
        content_layout.addWidget(form_card, 1)
        main_layout.addLayout(content_layout)

    def _create_input(self, placeholder, is_password=False):
        line = QLineEdit()
        line.setPlaceholderText(placeholder)
        if is_password: line.setEchoMode(QLineEdit.Password)
        line.setFixedHeight(45)
        line.setStyleSheet("""
            QLineEdit {
                background-color: #f8fafc; border: 1px solid #e2e8f0; 
                border-radius: 8px; padding: 0 15px; color: #1e293b;
            }
            QLineEdit:focus { border: 2px solid #3b82f6; background-color: white; }
        """)
        return line

    def _create_section_title(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #1e293b; margin-bottom: 5px;")
        return lbl

    def _add_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 4)
        widget.setGraphicsEffect(shadow)