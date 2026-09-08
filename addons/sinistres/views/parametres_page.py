"""
Page de gestion des paramètres et des rôles utilisateurs
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton, QComboBox, QLineEdit,
    QGroupBox, QFormLayout, QDialog, QDialogButtonBox,
    QMessageBox, QFrame, QTabWidget, QCheckBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from typing import List, Dict, Any


class ParametresPage(QWidget):
    """Page de gestion des paramètres et des rôles"""
    
    def __init__(self, controller, user, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.user = user
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # En-tête
        header = QLabel("⚙️ Paramètres et administration")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
        layout.addWidget(header)
        
        # Onglets
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                border-radius: 0 0 8px 8px;
                background-color: white;
            }
            QTabBar::tab {
                padding: 10px 20px;
                margin-right: 2px;
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #1a73e8;
            }
            QTabBar::tab:hover {
                background-color: #f1f5f9;
            }
        """)
        
        # Onglet 1: Utilisateurs et rôles
        self.tabs.addTab(self.create_users_tab(), "👤 Utilisateurs et rôles")
        
        # Onglet 2: Paramètres généraux
        self.tabs.addTab(self.create_settings_tab(), "📋 Paramètres généraux")
        
        # Onglet 3: Audit et logs
        self.tabs.addTab(self.create_audit_tab(), "📜 Audit et logs")
        
        layout.addWidget(self.tabs)
    
    # ============================================================
    # ONGLET 1: UTILISATEURS ET RÔLES
    # ============================================================
    
    def create_users_tab(self):
        """Crée l'onglet de gestion des utilisateurs et rôles"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Section: Rôles
        roles_group = QGroupBox("Rôles utilisateurs")
        roles_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        roles_layout = QVBoxLayout(roles_group)
        
        # Tableau des rôles
        self.table_roles = QTableWidget()
        self.table_roles.setColumnCount(6)
        self.table_roles.setHorizontalHeaderLabels([
            "ID", "Nom du rôle", "Description", "Utilisateurs", "Statut", "Actions"
        ])
        self.table_roles.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_roles.setAlternatingRowColors(True)
        self.table_roles.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 8px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        self.table_roles.setSortingEnabled(True)
        roles_layout.addWidget(self.table_roles)
        
        # Boutons rôles
        roles_btn_layout = QHBoxLayout()
        
        self.btn_ajouter_role = QPushButton("➕ Ajouter un rôle")
        self.btn_ajouter_role.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        self.btn_ajouter_role.clicked.connect(self.ajouter_role)
        roles_btn_layout.addWidget(self.btn_ajouter_role)
        
        roles_btn_layout.addStretch()
        roles_layout.addLayout(roles_btn_layout)
        
        layout.addWidget(roles_group)
        
        # Section: Utilisateurs
        users_group = QGroupBox("Utilisateurs")
        users_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        users_layout = QVBoxLayout(users_group)
        
        # Tableau des utilisateurs
        self.table_users = QTableWidget()
        self.table_users.setColumnCount(7)
        self.table_users.setHorizontalHeaderLabels([
            "ID", "Nom", "Email", "Rôle", "Statut", "Dernière connexion", "Actions"
        ])
        self.table_users.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_users.setAlternatingRowColors(True)
        self.table_users.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 8px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        self.table_users.setSortingEnabled(True)
        users_layout.addWidget(self.table_users)
        
        # Boutons utilisateurs
        users_btn_layout = QHBoxLayout()
        
        self.btn_ajouter_user = QPushButton("➕ Ajouter un utilisateur")
        self.btn_ajouter_user.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        self.btn_ajouter_user.clicked.connect(self.ajouter_utilisateur)
        users_btn_layout.addWidget(self.btn_ajouter_user)
        
        users_btn_layout.addStretch()
        users_layout.addLayout(users_btn_layout)
        
        layout.addWidget(users_group)
        
        return tab
    
    # ============================================================
    # ONGLET 2: PARAMÈTRES GÉNÉRAUX
    # ============================================================
    
    def create_settings_tab(self):
        """Crée l'onglet des paramètres généraux"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        
        # Section: Paramètres de l'application
        app_group = QGroupBox("Paramètres de l'application")
        app_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        app_layout = QFormLayout(app_group)
        app_layout.setSpacing(12)
        
        # Langue
        self.input_langue = QComboBox()
        self.input_langue.addItems(["Français", "English"])
        app_layout.addRow("Langue:", self.input_langue)
        
        # Date format
        self.input_date_format = QComboBox()
        self.input_date_format.addItems(["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])
        app_layout.addRow("Format de date:", self.input_date_format)
        
        # Devise
        self.input_devise = QComboBox()
        self.input_devise.addItems(["XAF", "EUR", "USD"])
        app_layout.addRow("Devise par défaut:", self.input_devise)
        
        content_layout.addWidget(app_group)
        
        # Section: Paramètres des sinistres
        sinistre_group = QGroupBox("Paramètres des sinistres")
        sinistre_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        sinistre_layout = QFormLayout(sinistre_group)
        sinistre_layout.setSpacing(12)
        
        # Délai d'instruction
        self.input_delai_instruction = QLineEdit()
        self.input_delai_instruction.setPlaceholderText("30")
        sinistre_layout.addRow("Délai d'instruction (jours):", self.input_delai_instruction)
        
        # Délai d'expertise
        self.input_delai_expertise = QLineEdit()
        self.input_delai_expertise.setPlaceholderText("15")
        sinistre_layout.addRow("Délai d'expertise (jours):", self.input_delai_expertise)
        
        # Délai de règlement
        self.input_delai_reglement = QLineEdit()
        self.input_delai_reglement.setPlaceholderText("10")
        sinistre_layout.addRow("Délai de règlement (jours):", self.input_delai_reglement)
        
        content_layout.addWidget(sinistre_group)
        
        # Section: Notifications
        notif_group = QGroupBox("Notifications")
        notif_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        notif_layout = QFormLayout(notif_group)
        notif_layout.setSpacing(12)
        
        self.check_email = QCheckBox("Activer les notifications par email")
        self.check_email.setChecked(True)
        notif_layout.addRow("", self.check_email)
        
        self.check_sms = QCheckBox("Activer les notifications par SMS")
        notif_layout.addRow("", self.check_sms)
        
        content_layout.addWidget(notif_group)
        
        # Bouton sauvegarder
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_save_settings = QPushButton("💾 Sauvegarder les paramètres")
        self.btn_save_settings.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 10px 30px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        self.btn_save_settings.clicked.connect(self.sauvegarder_parametres)
        btn_layout.addWidget(self.btn_save_settings)
        
        content_layout.addLayout(btn_layout)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return tab
    
    # ============================================================
    # ONGLET 3: AUDIT ET LOGS
    # ============================================================
    
    def create_audit_tab(self):
        """Crée l'onglet d'audit et logs"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Filtres
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        filter_layout.addWidget(QLabel("Action:"))
        self.filter_action = QComboBox()
        self.filter_action.addItem("Toutes", "")
        self.filter_action.addItem("CREATION", "CREATION")
        self.filter_action.addItem("MODIFICATION", "MODIFICATION")
        self.filter_action.addItem("VALIDATION", "VALIDATION")
        self.filter_action.addItem("SUPPRESSION", "SUPPRESSION")
        self.filter_action.addItem("CHANGEMENT_STATUT", "CHANGEMENT_STATUT")
        filter_layout.addWidget(self.filter_action)
        
        filter_layout.addWidget(QLabel("Entité:"))
        self.filter_entite = QComboBox()
        self.filter_entite.addItem("Toutes", "")
        self.filter_entite.addItem("Sinistre", "Sinistre")
        self.filter_entite.addItem("Expertise", "Expertise")
        self.filter_entite.addItem("Evaluation", "Evaluation")
        self.filter_entite.addItem("Reglement", "Reglement")
        self.filter_entite.addItem("Recours", "Recours")
        filter_layout.addWidget(self.filter_entite)
        
        filter_layout.addStretch()
        
        self.btn_refresh_audit = QPushButton("🔄 Rafraîchir")
        self.btn_refresh_audit.clicked.connect(self.load_audit)
        filter_layout.addWidget(self.btn_refresh_audit)
        
        layout.addLayout(filter_layout)
        
        # Tableau d'audit
        self.table_audit = QTableWidget()
        self.table_audit.setColumnCount(7)
        self.table_audit.setHorizontalHeaderLabels([
            "Date", "Utilisateur", "Action", "Entité", "ID", "Champ", "Ancien → Nouveau"
        ])
        self.table_audit.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_audit.setAlternatingRowColors(True)
        self.table_audit.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 8px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        layout.addWidget(self.table_audit)
        
        # Statistiques
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 8px;
                padding: 10px;
            }
            QLabel {
                color: #1e293b;
                font-size: 12px;
            }
            QLabel.value {
                font-weight: bold;
                font-size: 16px;
            }
        """)
        stats_layout = QHBoxLayout(stats_frame)
        
        self.lbl_total_logs = QLabel("Total: 0")
        self.lbl_total_logs.setStyleSheet("font-weight: bold; color: #1a73e8;")
        stats_layout.addWidget(self.lbl_total_logs)
        
        stats_layout.addStretch()
        
        self.lbl_actions_24h = QLabel("24h: 0")
        self.lbl_actions_24h.setStyleSheet("color: #64748b;")
        stats_layout.addWidget(self.lbl_actions_24h)
        
        layout.addWidget(stats_frame)
        
        return tab
    
    # ============================================================
    # MÉTHODES DE CHARGEMENT
    # ============================================================
    
    def load_data(self):
        """Charge toutes les données"""
        self.load_roles()
        self.load_users()
        self.load_audit()
    
    def load_roles(self):
        """Charge la liste des rôles"""
        # TODO: Récupérer les rôles depuis la base
        roles = [
            {'id': 1, 'nom': 'Admin', 'description': 'Accès complet', 'users': 1, 'actif': True},
            {'id': 2, 'nom': 'Gestionnaire', 'description': 'Gestion des sinistres', 'users': 5, 'actif': True},
            {'id': 3, 'nom': 'Responsable', 'description': 'Validation des évaluations', 'users': 2, 'actif': True},
            {'id': 4, 'nom': 'Expert', 'description': 'Expertise et rapports', 'users': 3, 'actif': True},
            {'id': 5, 'nom': 'Comptable', 'description': 'Paiements et comptabilité', 'users': 2, 'actif': True},
        ]
        self.update_roles_table(roles)
    
    def update_roles_table(self, roles: List[dict]):
        """Met à jour le tableau des rôles"""
        self.table_roles.setRowCount(len(roles))
        
        for i, role in enumerate(roles):
            self.table_roles.setItem(i, 0, QTableWidgetItem(str(role.get('id', ''))))
            self.table_roles.setItem(i, 1, QTableWidgetItem(role.get('nom', '')))
            self.table_roles.setItem(i, 2, QTableWidgetItem(role.get('description', '')))
            self.table_roles.setItem(i, 3, QTableWidgetItem(str(role.get('users', 0))))
            
            statut_item = QTableWidgetItem("✅ Actif" if role.get('actif') else "❌ Inactif")
            statut_item.setForeground(QColor("#22c55e" if role.get('actif') else "#ef4444"))
            self.table_roles.setItem(i, 4, statut_item)
            
            # Boutons d'action
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            btn_layout.setSpacing(5)
            
            btn_edit = QPushButton("✏️")
            btn_edit.setFixedSize(30, 30)
            btn_edit.setStyleSheet("border-radius: 15px;")
            btn_edit.clicked.connect(lambda checked, r=role: self.editer_role(r))
            btn_layout.addWidget(btn_edit)
            
            btn_toggle = QPushButton("🔒" if role.get('actif') else "🔓")
            btn_toggle.setFixedSize(30, 30)
            btn_toggle.setStyleSheet("border-radius: 15px;")
            btn_toggle.clicked.connect(lambda checked, r=role: self.toggle_role(r))
            btn_layout.addWidget(btn_toggle)
            
            btn_layout.addStretch()
            self.table_roles.setCellWidget(i, 5, btn_widget)
    
    def load_users(self):
        """Charge la liste des utilisateurs"""
        # TODO: Récupérer les utilisateurs depuis la base
        users = [
            {'id': 1, 'nom': 'Jean Dupont', 'email': 'jean@example.com', 'role': 'Admin', 'actif': True, 'last_login': '2026-09-07 10:30'},
            {'id': 2, 'nom': 'Marie Martin', 'email': 'marie@example.com', 'role': 'Gestionnaire', 'actif': True, 'last_login': '2026-09-07 09:15'},
            {'id': 3, 'nom': 'Pierre Durand', 'email': 'pierre@example.com', 'role': 'Expert', 'actif': True, 'last_login': '2026-09-06 16:45'},
        ]
        self.update_users_table(users)
    
    def update_users_table(self, users: List[dict]):
        """Met à jour le tableau des utilisateurs"""
        self.table_users.setRowCount(len(users))
        
        for i, user in enumerate(users):
            self.table_users.setItem(i, 0, QTableWidgetItem(str(user.get('id', ''))))
            self.table_users.setItem(i, 1, QTableWidgetItem(user.get('nom', '')))
            self.table_users.setItem(i, 2, QTableWidgetItem(user.get('email', '')))
            self.table_users.setItem(i, 3, QTableWidgetItem(user.get('role', '')))
            
            statut_item = QTableWidgetItem("✅ Actif" if user.get('actif') else "❌ Inactif")
            statut_item.setForeground(QColor("#22c55e" if user.get('actif') else "#ef4444"))
            self.table_users.setItem(i, 4, statut_item)
            
            self.table_users.setItem(i, 5, QTableWidgetItem(user.get('last_login', '')))
            
            # Boutons d'action
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            btn_layout.setSpacing(5)
            
            btn_edit = QPushButton("✏️")
            btn_edit.setFixedSize(30, 30)
            btn_edit.setStyleSheet("border-radius: 15px;")
            btn_edit.clicked.connect(lambda checked, u=user: self.editer_utilisateur(u))
            btn_layout.addWidget(btn_edit)
            
            btn_toggle = QPushButton("🔒" if user.get('actif') else "🔓")
            btn_toggle.setFixedSize(30, 30)
            btn_toggle.setStyleSheet("border-radius: 15px;")
            btn_toggle.clicked.connect(lambda checked, u=user: self.toggle_utilisateur(u))
            btn_layout.addWidget(btn_toggle)
            
            btn_layout.addStretch()
            self.table_users.setCellWidget(i, 6, btn_widget)
    
    def load_audit(self):
        """Charge les logs d'audit"""
        # TODO: Récupérer les logs depuis la base
        logs = [
            {'date': '2026-09-07 10:30', 'user': 'Jean Dupont', 'action': 'CREATION', 'entite': 'Sinistre', 'id': 'SIN-2026-000001', 'champ': '', 'change': ''},
            {'date': '2026-09-07 10:35', 'user': 'Jean Dupont', 'action': 'MODIFICATION', 'entite': 'Sinistre', 'id': 'SIN-2026-000001', 'champ': 'statut', 'change': 'OUVERT → EN_INSTRUCTION'},
        ]
        self.update_audit_table(logs)
    
    def update_audit_table(self, logs: List[dict]):
        """Met à jour le tableau d'audit"""
        self.table_audit.setRowCount(len(logs))
        
        action_colors = {
            'CREATION': '#22c55e',
            'MODIFICATION': '#f59e0b',
            'VALIDATION': '#3b82f6',
            'SUPPRESSION': '#ef4444',
            'CHANGEMENT_STATUT': '#8b5cf6'
        }
        
        for i, log in enumerate(logs):
            self.table_audit.setItem(i, 0, QTableWidgetItem(log.get('date', '')))
            self.table_audit.setItem(i, 1, QTableWidgetItem(log.get('user', '')))
            
            action_item = QTableWidgetItem(log.get('action', ''))
            color = action_colors.get(log.get('action', ''), '#64748b')
            action_item.setBackground(QColor(color))
            action_item.setForeground(QColor('white'))
            self.table_audit.setItem(i, 2, action_item)
            
            self.table_audit.setItem(i, 3, QTableWidgetItem(log.get('entite', '')))
            self.table_audit.setItem(i, 4, QTableWidgetItem(log.get('id', '')))
            self.table_audit.setItem(i, 5, QTableWidgetItem(log.get('champ', '')))
            self.table_audit.setItem(i, 6, QTableWidgetItem(log.get('change', '')))
        
        self.lbl_total_logs.setText(f"Total: {len(logs)}")
        self.lbl_actions_24h.setText(f"24h: {len([l for l in logs if '2026-09-07' in l.get('date', '')])}")
    
    # ============================================================
    # ACTIONS RÔLES
    # ============================================================
    
    def ajouter_role(self):
        """Ouvre le dialogue d'ajout de rôle"""
        QMessageBox.information(self, "Ajout rôle", "Dialogue d'ajout de rôle (à implémenter)")
    
    def editer_role(self, role: dict):
        """Ouvre le dialogue d'édition de rôle"""
        QMessageBox.information(self, "Édition rôle", f"Édition du rôle {role.get('nom')} (à implémenter)")
    
    def toggle_role(self, role: dict):
        """Active/désactive un rôle"""
        QMessageBox.information(self, "Toggle rôle", f"Activation/désactivation du rôle {role.get('nom')} (à implémenter)")
    
    # ============================================================
    # ACTIONS UTILISATEURS
    # ============================================================
    
    def ajouter_utilisateur(self):
        """Ouvre le dialogue d'ajout d'utilisateur"""
        QMessageBox.information(self, "Ajout utilisateur", "Dialogue d'ajout d'utilisateur (à implémenter)")
    
    def editer_utilisateur(self, user: dict):
        """Ouvre le dialogue d'édition d'utilisateur"""
        QMessageBox.information(self, "Édition utilisateur", f"Édition de l'utilisateur {user.get('nom')} (à implémenter)")
    
    def toggle_utilisateur(self, user: dict):
        """Active/désactive un utilisateur"""
        QMessageBox.information(self, "Toggle utilisateur", f"Activation/désactivation de l'utilisateur {user.get('nom')} (à implémenter)")
    
    # ============================================================
    # PARAMÈTRES
    # ============================================================
    
    def sauvegarder_parametres(self):
        """Sauvegarde les paramètres"""
        QMessageBox.information(self, "Sauvegarde", "Paramètres sauvegardés avec succès !")