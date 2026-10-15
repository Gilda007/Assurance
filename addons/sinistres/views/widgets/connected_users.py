"""
Widget Utilisateurs connectés pour le dashboard LOMETA

Affiche la liste des utilisateurs ayant une session active :
- Avatar avec initiale colorée par rôle
- Nom complet + badge de rôle
- Statut (en ligne / inactif / hors ligne)
- Dernière activité en temps relatif
- Rafraîchissement automatique toutes les 30 secondes
"""
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QSizePolicy, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor, QFont

from datetime import datetime
from typing import List, Dict, Optional


# ============================================================
# CONSTANTES
# ============================================================

# Statuts de session
STATUS_ONLINE = "online"      # Actif < 5 min
STATUS_IDLE = "idle"          # Actif < 30 min
STATUS_OFFLINE = "offline"    # Actif > 30 min

STATUS_COLORS = {
    STATUS_ONLINE: "#22c55e",
    STATUS_IDLE: "#f59e0b",
    STATUS_OFFLINE: "#94a3b8",
}

STATUS_LABELS = {
    STATUS_ONLINE: "En ligne",
    STATUS_IDLE: "Inactif",
    STATUS_OFFLINE: "Hors ligne",
}

# Couleurs par rôle
ROLE_COLORS = {
    'Administrateur': '#1e3a8a',
    'Admin': '#1e3a8a',
    'Gestionnaire': '#3b82f6',
    'Responsable': '#8b5cf6',
    'Comptable': '#f59e0b',
    'Expert': '#06b6d4',
    'Utilisateur': '#64748b',
}


# ============================================================
# LIGNE UTILISATEUR
# ============================================================

class UserRow(QFrame):
    """Ligne d'un utilisateur connecté"""
    disconnect_requested = Signal(dict)
    show_sessions_requested = Signal(dict)
    block_user_requested = Signal(dict)
    
    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self.user = user
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border-bottom: 1px solid #f1f5f9;
            }
            QFrame:hover {
                background-color: #f8fafc;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)
        
        # ============================================================
        # Avatar (initiale dans un cercle coloré)
        # ============================================================
        nom = user.get('nom') or user.get('full_name') or user.get('username') or 'Utilisateur'
        initiale = nom[0].upper() if nom else '?'
        
        role = user.get('role') or 'Utilisateur'
        role_color = ROLE_COLORS.get(role, '#64748b')
        
        avatar = QLabel(initiale)
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(f"""
            QLabel {{
                background-color: {role_color}20;
                color: {role_color};
                border-radius: 18px;
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(avatar)
        
        # ============================================================
        # Informations (nom + rôle + activité)
        # ============================================================
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        # Ligne 1 : pastille statut + nom + badge rôle
        name_row = QHBoxLayout()
        name_row.setSpacing(6)
        
        # Pastille statut
        status = user.get('status', STATUS_OFFLINE)
        status_color = STATUS_COLORS.get(status, '#94a3b8')
        
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {status_color}; font-size: 10px;")
        dot.setFixedWidth(10)
        dot.setToolTip(STATUS_LABELS.get(status, "Inconnu"))
        name_row.addWidget(dot)
        
        # Nom
        name_lbl = QLabel(nom)
        name_lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #1e293b;")
        name_lbl.setToolTip(nom)
        name_row.addWidget(name_lbl)
        
        # Badge rôle
        role_lbl = QLabel(role)
        role_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {role_color}20;
                color: {role_color};
                padding: 1px 6px;
                border-radius: 6px;
                font-size: 9px;
                font-weight: bold;
            }}
        """)
        name_row.addWidget(role_lbl)
        
        name_row.addStretch()
        info_layout.addLayout(name_row)
        
        # Ligne 2 : dernière activité
        last_activity = user.get('last_activity')
        time_label = self._format_relative_time(last_activity)
        
        # Ajouter l'IP si présente
        ip = user.get('ip_address')
        ip_suffix = f"  •  {ip}" if ip else ""
        
        last_lbl = QLabel(f"Dernière activité : {time_label}{ip_suffix}")
        last_lbl.setStyleSheet("font-size: 10px; color: #94a3b8;")
        info_layout.addWidget(last_lbl)
        
        layout.addLayout(info_layout, 1)


    def _show_context_menu(self, position):
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QAction
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 13px;
                color: #1e293b;
            }
            QMenu::item:selected {
                background-color: #f1f5f9;
                color: #1a73e8;
            }
            QMenu::separator {
                height: 1px;
                background-color: #e2e8f0;
                margin: 4px 8px;
            }
        """)
        
        # Voir les sessions
        action_sessions = QAction("👁️  Voir les sessions", self)
        action_sessions.triggered.connect(lambda: self.show_sessions_requested.emit(self.user))
        menu.addAction(action_sessions)
        
        menu.addSeparator()
        
        # Déconnecter
        action_disconnect = QAction("🔌  Déconnecter", self)
        action_disconnect.triggered.connect(lambda: self.disconnect_requested.emit(self.user))
        menu.addAction(action_disconnect)
        
        # Bloquer
        action_block = QAction("🚫  Bloquer le compte", self)
        action_block.triggered.connect(lambda: self.block_user_requested.emit(self.user))
        menu.addAction(action_block)
        
        menu.exec(self.mapToGlobal(position))

    
    # ============================================================
    # HELPER
    # ============================================================
    
    def _format_relative_time(self, date_str) -> str:
        """Formate une date en temps relatif ('à l'instant', 'il y a 5 min')"""
        if not date_str:
            return "—"
        try:
            if isinstance(date_str, str):
                d = datetime.fromisoformat(str(date_str)[:19])
            elif isinstance(date_str, datetime):
                d = date_str
            else:
                return "—"
            
            delta = datetime.now() - d
            seconds = int(delta.total_seconds())
            
            if seconds < 0:
                return "à l'instant"
            elif seconds < 60:
                return "à l'instant"
            elif seconds < 3600:
                return f"il y a {seconds // 60} min"
            elif seconds < 86400:
                return f"il y a {seconds // 3600}h"
            else:
                return f"il y a {seconds // 86400}j"
        except Exception:
            return "—"


# ============================================================
# CARTE PRINCIPALE
# ============================================================

class ConnectedUsersCard(QFrame):
    """
    Carte affichant les utilisateurs connectés
    
    Utilisation :
        card = ConnectedUsersCard()
        card.refresh_requested.connect(mon_handler)
        card.set_users([...])
    """
    refresh_requested = Signal()
    disconnect_requested = Signal(dict)
    show_sessions_requested = Signal(dict)
    block_user_requested = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Style de la carte
        self.setStyleSheet("""
            QFrame#ConnectedUsersCard {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        self.setObjectName("ConnectedUsersCard")
        self.setMinimumHeight(280)
        self.setMaximumHeight(400)

        # ============================================================
        # ✅ Effet d'ombrage subtil
        # ============================================================
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(15, 23, 42, 30))
        self.setGraphicsEffect(shadow)
        
        # ============================================================
        # Layout principal
        # ============================================================
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 15, 18, 15)
        main_layout.setSpacing(10)
        
        # ============================================================
        # En-tête
        # ============================================================
        header = QHBoxLayout()
        header.setSpacing(8)
        
        # Icône
        icon = QLabel("👥")
        icon.setStyleSheet("font-size: 16px;")
        header.addWidget(icon)
        
        # Titre
        title = QLabel("Utilisateurs connectés")
        title.setStyleSheet("font-size: 13px; font-weight: bold; color: #1e293b;")
        header.addWidget(title)
        
        # Compteur
        self.count_badge = QLabel("0")
        self.count_badge.setStyleSheet("""
            QLabel {
                background-color: #e8f0fe;
                color: #1a73e8;
                padding: 2px 8px;
                border-radius: 8px;
                font-size: 10px;
                font-weight: bold;
            }
        """)
        self.count_badge.setAlignment(Qt.AlignCenter)
        self.count_badge.setMinimumWidth(24)
        header.addWidget(self.count_badge)
        
        header.addStretch()
        
        # Bouton rafraîchir
        self.btn_refresh = QPushButton("🔄")
        self.btn_refresh.setFixedSize(24, 24)
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setToolTip("Rafraîchir la liste")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                font-size: 12px;
                color: #64748b;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                color: #1a73e8;
            }
        """)
        self.btn_refresh.clicked.connect(self._on_refresh_clicked)
        header.addWidget(self.btn_refresh)
        
        main_layout.addLayout(header)
        
        # ============================================================
        # Séparateur
        # ============================================================
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #f1f5f9; max-height: 1px; border: none;")
        main_layout.addWidget(sep)
        
        # ============================================================
        # Zone scrollable pour la liste
        # ============================================================
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #cbd5e1;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #94a3b8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        self.users_container = QWidget()
        self.users_container.setStyleSheet("background-color: transparent;")
        self.users_layout = QVBoxLayout(self.users_container)
        self.users_layout.setContentsMargins(0, 0, 0, 0)
        self.users_layout.setSpacing(0)
        
        scroll.setWidget(self.users_container)
        main_layout.addWidget(scroll, 1)
        
        # ============================================================
        # Message vide (caché par défaut)
        # ============================================================
        self.lbl_empty = QLabel("Aucun utilisateur connecté")
        self.lbl_empty.setStyleSheet("""
            QLabel {
                color: #94a3b8;
                font-size: 11px;
                font-style: italic;
                padding: 20px;
            }
        """)
        self.lbl_empty.setAlignment(Qt.AlignCenter)
        self.lbl_empty.hide()
        main_layout.addWidget(self.lbl_empty)
        
        # ============================================================
        # Timer auto-refresh (30 secondes)
        # ============================================================
        self._auto_refresh = QTimer(self)
        self._auto_refresh.timeout.connect(self._on_refresh_clicked)
        self._auto_refresh.start(30000)
    
    # ============================================================
    # MISE À JOUR
    # ============================================================
    
    def set_users(self, users: List[Dict]):
        """
        Met à jour la liste des utilisateurs
        
        Args:
            users: liste de dicts avec :
                - id (int)
                - nom / full_name (str)
                - username (str)
                - role (str)
                - last_activity (str ISO ou datetime)
                - ip_address (str, optionnel)
                - status ('online' | 'idle' | 'offline')
        """
        # Vider la liste
        while self.users_layout.count():
            item = self.users_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Filtrer les utilisateurs actifs (online + idle uniquement)
        active_users = [
            u for u in (users or [])
            if u.get('status') in (STATUS_ONLINE, STATUS_IDLE)
        ]
        
        # Mettre à jour le compteur
        self.count_badge.setText(str(len(active_users)))
        
        # Si aucun utilisateur
        if not active_users:
            self.lbl_empty.show()
            return
        
        self.lbl_empty.hide()
        
        # Trier : online d'abord, puis idle, puis par activité récente
        def sort_key(u):
            status = u.get('status', STATUS_OFFLINE)
            priority = {
                STATUS_ONLINE: 0,
                STATUS_IDLE: 1,
                STATUS_OFFLINE: 2,
            }.get(status, 3)
            # Inverser le tri sur last_activity pour avoir le plus récent en premier
            last = u.get('last_activity') or ''
            return (priority, -1 if last else 0)
        
        active_users.sort(key=sort_key)
        
        # Ajouter chaque utilisateur
        for user in active_users:
            row = UserRow(user)
            row.disconnect_requested.connect(self.disconnect_requested.emit)
            row.show_sessions_requested.connect(self.show_sessions_requested.emit)
            row.block_user_requested.connect(self.block_user_requested.emit)
            self.users_layout.addWidget(row)
        
        # Stretch final pour aligner vers le haut
        self.users_layout.addStretch()
    
    # ============================================================
    # SIGNAL
    # ============================================================
    
    def _on_refresh_clicked(self):
        """Émet un signal pour demander le rafraîchissement"""
        self.refresh_requested.emit()
    
    # ============================================================
    # NETTOYAGE
    # ============================================================
    
    def stop_auto_refresh(self):
        """Arrête le timer d'auto-refresh"""
        if self._auto_refresh:
            self._auto_refresh.stop()
    
    def start_auto_refresh(self, interval_ms: int = 30000):
        """Démarre le timer d'auto-refresh"""
        if self._auto_refresh:
            self._auto_refresh.start(interval_ms)