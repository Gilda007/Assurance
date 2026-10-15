"""
Dialogue de confirmation pour la déconnexion d'un utilisateur
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import Qt


class DisconnectUserDialog(QDialog):
    """
    Dialogue pour confirmer la déconnexion d'un utilisateur.
    
    Usage :
        dialog = DisconnectUserDialog(user, sessions_count, parent=self)
        if dialog.exec() == QDialog.Accepted:
            reason = dialog.get_reason()
    """
    
    def __init__(self, user: dict, sessions_count: int = 1, parent=None):
        super().__init__(parent)
        
        self.user = user or {}
        self.sessions_count = max(1, sessions_count)
        self.reason = ""
        
        self.setWindowTitle("Déconnecter l'utilisateur")
        self.setModal(True)
        self.setMinimumWidth(450)
        self.setStyleSheet("QDialog { background-color: #f8fafc; }")
        
        self.setup_ui()
    
    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(15)
        
        # ============================================================
        # 1. BANDEAU D'AVERTISSEMENT
        # ============================================================
        warning = QFrame()
        warning.setStyleSheet("""
            QFrame {
                background-color: #fef3c7;
                border-left: 4px solid #f59e0b;
                border-radius: 6px;
            }
        """)
        warning_layout = QHBoxLayout(warning)
        warning_layout.setContentsMargins(12, 10, 12, 10)
        warning_layout.setSpacing(10)
        
        icon = QLabel("⚠️")
        icon.setStyleSheet("font-size: 22px;")
        warning_layout.addWidget(icon)
        
        # Nom de l'utilisateur (avec fallback)
        nom = (
            self.user.get('nom')
            or self.user.get('full_name')
            or self.user.get('username')
            or 'Utilisateur'
        )
        role = self.user.get('role') or 'Utilisateur'
        
        msg = QLabel(
            f"Vous êtes sur le point de <b>déconnecter</b> :<br>"
            f"<b style='font-size: 13px;'>{nom}</b> "
            f"<span style='color: #92400e;'>({role})</span><br><br>"
            f"<b>{self.sessions_count}</b> session(s) active(s) "
            f"seront fermées immédiatement."
        )
        msg.setStyleSheet("font-size: 12px; color: #92400e;")
        msg.setWordWrap(True)
        warning_layout.addWidget(msg, 1)
        
        root.addWidget(warning)
        
        # ============================================================
        # 2. CHAMP MOTIF
        # ============================================================
        motif_lbl = QLabel("Motif de la déconnexion :")
        motif_lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #1e293b;")
        root.addWidget(motif_lbl)
        
        self.txt_reason = QTextEdit()
        self.txt_reason.setPlaceholderText(
            "Ex: Activité suspecte, demande de l'utilisateur, "
            "maintenance, sécurité..."
        )
        self.txt_reason.setMaximumHeight(80)
        self.txt_reason.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                color: #1e293b;
            }
            QTextEdit:focus {
                border: 2px solid #1a73e8;
            }
        """)
        root.addWidget(self.txt_reason)
        
        # ============================================================
        # 3. INFO SUPPLÉMENTAIRE
        # ============================================================
        info = QLabel(
            "ℹ️ L'utilisateur sera immédiatement déconnecté. "
            "Il pourra se reconnecter s'il le souhaite."
        )
        info.setStyleSheet("""
            font-size: 11px;
            color: #64748b;
            font-style: italic;
        """)
        info.setWordWrap(True)
        root.addWidget(info)
        
        # ============================================================
        # 4. BOUTONS
        # ============================================================
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        # Bouton Annuler
        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #64748b;
                padding: 10px 24px;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #f8fafc;
                border-color: #cbd5e1;
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        
        # Bouton Confirmer
        self.btn_confirm = QPushButton("🔌  Déconnecter")
        self.btn_confirm.setCursor(Qt.PointingHandCursor)
        self.btn_confirm.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                padding: 10px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        self.btn_confirm.clicked.connect(self._on_confirm)
        btn_layout.addWidget(self.btn_confirm)
        
        root.addLayout(btn_layout)
    
    # ============================================================
    # ACTIONS
    # ============================================================
    
    def _on_confirm(self):
        """Valide la déconnexion avec le motif saisi"""
        self.reason = self.txt_reason.toPlainText().strip()
        
        if not self.reason:
            # Motif par défaut si l'utilisateur n'a rien saisi
            self.reason = "Déconnexion administrative"
        
        self.accept()
    
    # ============================================================
    # API PUBLIQUE
    # ============================================================
    
    def get_reason(self) -> str:
        """Retourne le motif saisi par l'administrateur"""
        return self.reason or "Déconnexion administrative"
    
    def get_user_id(self) -> int:
        """Retourne l'ID de l'utilisateur à déconnecter"""
        return self.user.get('id')
    
    def get_user_nom(self) -> str:
        """Retourne le nom de l'utilisateur"""
        return (
            self.user.get('nom')
            or self.user.get('full_name')
            or self.user.get('username')
            or 'Utilisateur'
        )