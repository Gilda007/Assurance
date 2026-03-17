from PySide6.QtWidgets import (QLineEdit, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLabel, QPushButton, QListWidgetItem, QStackedWidget, QListWidget, QFrame, QMessageBox, QDialog)
from PySide6.QtCore import Qt

class AccountSettingsView(QWidget):
    def __init__(self, controller=None, user=None): # Ajout du controller ici
        super().__init__()
        self.controller = controller
        self.user = user  # On stocke l'utilisateur
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Sécurité : on récupère le nom
        username = getattr(self.user, 'username', getattr(self.user, 'name', "Utilisateur Inconnu"))
        role = getattr(self.user, 'role', "Non défini")
        
        username = getattr(self.user, 'name', "Utilisateur Inconnu")
        self.info_user = QLabel(f"Utilisateur : <b>{username}</b>")
        title = QLabel("Mon Compte")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        self.info_user = QLabel(f"Utilisateur : <b>{username}</b>")
        self.info_role = QLabel(f"Rôle : <span style='color: blue;'>{role}</span>")

        # Formulaire
        form_frame = QFrame()
        form_frame.setStyleSheet("background: white; border-radius: 10px; padding: 20px;")
        form_layout = QVBoxLayout(form_frame)

        self.info_user = QLabel(f"Utilisateur : <b>{user}</b>")
        self.info_role = QLabel(f"Rôle : <span style='color: blue;'>{user.role}</span>")
        
        self.old_password = QLineEdit()
        self.old_password.setPlaceholderText("Ancien mot de passe")
        self.old_password.setEchoMode(QLineEdit.Password)
        
        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("Nouveau mot de passe")
        self.new_password.setEchoMode(QLineEdit.Password)

        self.btn_save = QPushButton("Mettre à jour le profil")
        self.btn_save.setStyleSheet("background-color: #10b981; color: white; height: 40px;")

        form_layout.addWidget(self.info_user)
        form_layout.addWidget(self.info_role)
        form_layout.addSpacing(20)
        form_layout.addWidget(QLabel("Changer le mot de passe :"))
        form_layout.addWidget(self.old_password)
        form_layout.addWidget(self.new_password)
        form_layout.addWidget(self.btn_save)
        
        layout.addWidget(form_frame)
        layout.addStretch()