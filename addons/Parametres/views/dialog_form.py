from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QFormLayout, QFrame)
from PySide6.QtCore import Qt, QPoint

class UserDialog(QDialog):
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        
        # 1. ENLEVER LES BORDURES
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground) # Permet des coins arrondis
        
        self.setFixedWidth(400)
        self.user_data = user_data
        self.old_pos = None # Pour le déplacement de la fenêtre

        self.setup_ui()

    def setup_ui(self):
        # Frame principal pour simuler la fenêtre (avec bordures arrondies et ombre)
        self.main_frame = QFrame(self)
        self.main_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #dcdde1;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.main_frame)
        
        content_layout = QVBoxLayout(self.main_frame)
        content_layout.setContentsMargins(20, 10, 20, 20)

        # --- BARRE DE TITRE PERSONNALISÉE ---
        title_bar = QHBoxLayout()
        
        title_label = QLabel("👤 GESTION UTILISATEUR")
        title_label.setStyleSheet("font-weight: bold; color: #2f3640; border: none;")
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.clicked.connect(self.reject) # Fermer la boîte
        self.btn_close.setStyleSheet("""
            QPushButton {
                border: none;
                font-size: 18px;
                color: #7f8c8d;
                background: transparent;
            }
            QPushButton:hover { color: #e74c3c; }
        """)
        
        title_bar.addWidget(title_label)
        title_bar.addStretch()
        title_bar.addWidget(self.btn_close)
        content_layout.addLayout(title_bar)

        # Séparateur
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #f5f6fa; border: none;")
        content_layout.addWidget(line)

        # --- FORMULAIRE ---
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(0, 20, 0, 20)

        input_style = """
            QLineEdit, QComboBox {
                border: 1px solid #dcdde1;
                border-radius: 5px;
                padding: 8px;
                background: #fdfdfd;
            }
            QLineEdit:focus { border: 1px solid #3498db; }
        """

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nom d'utilisateur")
        self.username_input.setStyleSheet(input_style)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(input_style)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(["agent", "superviseur", "admin"])
        self.role_combo.setStyleSheet(input_style)

        if self.user_data:
            self.username_input.setText(getattr(self.user_data, 'username', ''))
            self.role_combo.setCurrentText(getattr(self.user_data, 'role', 'agent'))

        form_layout.addRow("Utilisateur :", self.username_input)
        form_layout.addRow("Mot de passe :", self.password_input)
        form_layout.addRow("Rôle :", self.role_combo)
        content_layout.addLayout(form_layout)

        # --- BOUTONS D'ACTION ---
        btn_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("Enregistrer les modifications" if self.user_data else "Créer l'utilisateur")
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setFixedHeight(40)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        self.btn_save.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.btn_save)
        content_layout.addLayout(btn_layout)

    # --- LOGIQUE POUR DÉPLACER LA FENÊTRE ---
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
            "password": self.password_input.text(),
            "role": self.role_combo.currentText()
        }
    
    # Dans UserDialog (dialogs.py)
    def accept(self):
        """Surchargé pour valider avant de fermer"""
        if not self.username_input.text().strip():
            self.username_input.setStyleSheet("border: 1px solid red; padding: 8px;")
            self.username_input.setPlaceholderText("CE CHAMP EST REQUIS")
            return
        
        # Si tout est OK, on appelle la méthode originale de QDialog
        super().accept()