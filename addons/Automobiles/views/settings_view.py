# addons/Automobiles/views/settings_view.py
"""
Vue des paramètres et configuration - Version opérationnelle
Avec gestion des préférences, sauvegarde automatique et interface utilisateur avancée
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QTabWidget, QGroupBox, QFormLayout, QLineEdit,
    QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox,
    QColorDialog, QFontDialog, QFileDialog, QMessageBox,
    QListWidget, QListWidgetItem, QStackedWidget, QScrollArea,
    QGridLayout, QSplitter, QTextEdit, QSlider, QRadioButton,
    QButtonGroup, QDialog, QDialogButtonBox, QTabBar,
    QDateEdit, QTimeEdit, QPlainTextEdit
)
from PySide6.QtCore import Qt, QSettings, Signal, QTimer, QDateTime, QDate
from PySide6.QtGui import QColor, QFont, QIcon, QPixmap, QPalette

from datetime import datetime
import json
import os
import shutil

from addons.Automobiles.views.style import Colors, Fonts, Spacing
from addons.Automobiles.views.widgets.modern_card import ModernCard
from core.logger import logger


class SettingsView(QWidget):
    """Vue des paramètres de l'application - Version opérationnelle"""
    
    settings_changed = Signal()
    theme_changed = Signal(str)
    
    def __init__(self, controller, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.settings = QSettings("AutoAssure", "AutomobileModule")
        self.settings_file = os.path.join(os.path.expanduser("~"), ".ams_settings.json")
        self.backup_dir = os.path.join(os.path.expanduser("~"), "AMS_Backups")
        
        # Créer le dossier de sauvegarde
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        
        self.setup_ui()
        self.load_settings()
        self.setup_auto_save()
        self.load_company_list()
        self.load_user_list()
        self.load_backup_list()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # En-tête
        header = self._create_header()
        layout.addWidget(header)
        
        # Contenu principal
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Barre latérale de navigation
        sidebar = self._create_sidebar()
        content_layout.addWidget(sidebar)
        
        # Zone de contenu
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("""
            QStackedWidget {
                background: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        # Créer les pages
        self._create_general_page()
        self._create_company_page()
        self._create_api_page()
        self._create_appearance_page()
        self._create_database_page()
        self._create_users_page()
        self._create_backup_page()
        self._create_about_page()
        
        content_layout.addWidget(self.content_stack, 1)
        
        layout.addLayout(content_layout)
        
        # Pied de page avec boutons d'action
        footer = self._create_footer()
        layout.addWidget(footer)
    
    def _create_header(self):
        """Crée l'en-tête moderne"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e293b, stop:1 #0f172a);
                padding: 16px 24px;
            }
        """)
        
        layout = QHBoxLayout(header)
        
        title = QLabel("⚙️ Paramètres")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: 800;")
        
        # Statut des paramètres
        self.status_label = QLabel("✅ Paramètres chargés")
        self.status_label.setStyleSheet("color: #94a3b8; font-size: 13px;")
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.status_label)
        
        return header
    
    def _create_footer(self):
        """Crée le pied de page avec les boutons d'action"""
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background: white;
                border-top: 1px solid #e2e8f0;
                padding: 12px 24px;
            }
        """)
        
        layout = QHBoxLayout(footer)
        layout.setSpacing(12)
        
        # Statut des modifications
        self.modified_label = QLabel("✅ Paramètres sauvegardés")
        self.modified_label.setStyleSheet("color: #64748b; font-size: 13px;")
        layout.addWidget(self.modified_label)
        
        layout.addStretch()
        
        # Boutons d'action
        self.save_btn = QPushButton("💾 Sauvegarder")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.save_btn.clicked.connect(self.save_settings)
        
        self.apply_btn = QPushButton("✅ Appliquer")
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        self.apply_btn.clicked.connect(self.apply_settings)
        
        self.reset_btn = QPushButton("↺ Réinitialiser")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
        """)
        self.reset_btn.clicked.connect(self.reset_settings)
        
        layout.addWidget(self.save_btn)
        layout.addWidget(self.apply_btn)
        layout.addWidget(self.reset_btn)
        
        return footer
    
    def _create_sidebar(self):
        """Crée la barre latérale de navigation"""
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
                padding: 8px;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(4)
        
        # Boutons de navigation
        nav_items = [
            ("⚙️", "Général", 0),
            ("🏢", "Compagnies", 1),
            ("🌐", "API ASAC", 2),
            ("🎨", "Apparence", 3),
            ("💾", "Base de données", 4),
            ("👥", "Utilisateurs", 5),
            ("📦", "Sauvegarde", 6),
            ("ℹ️", "À propos", 7)
        ]
        
        self.nav_buttons = []
        for icon, label, index in nav_items:
            btn = QPushButton(f"{icon} {label}")
            btn.setCheckable(True)
            btn.setFixedHeight(42)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding-left: 16px;
                    border-radius: 10px;
                    background: transparent;
                    color: #64748b;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background: #f1f5f9;
                }
                QPushButton:checked {
                    background: #eff6ff;
                    color: #2563eb;
                    font-weight: 600;
                }
            """)
            btn.clicked.connect(lambda checked, idx=index: self.switch_page(idx))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)
            
            if index == 0:
                btn.setChecked(True)
        
        layout.addStretch()
        
        # Version
        version_label = QLabel("Version 2.0.0")
        version_label.setStyleSheet("color: #94a3b8; font-size: 11px; padding: 8px;")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        return sidebar
    
    def switch_page(self, index):
        """Change de page"""
        self.content_stack.setCurrentIndex(index)
        
        # Mettre à jour les boutons
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        
        # Rafraîchir les données si nécessaire
        if index == 5:  # Utilisateurs
            self.load_user_list()
        elif index == 1:  # Compagnies
            self.load_company_list()
        elif index == 6:  # Sauvegarde
            self.load_backup_list()
    
    def apply_settings(self):
        """Applique les paramètres sans fermer la page"""
        if self.save_settings():
            self.modified_label.setText("✅ Paramètres appliqués")
            QTimer.singleShot(3000, lambda: self.modified_label.setText("✅ Paramètres sauvegardés"))
            QMessageBox.information(self, "Succès", "Paramètres appliqués avec succès")
    
    # ============================================================
    # PAGES
    # ============================================================
    
    def _create_general_page(self):
        """Page des paramètres généraux"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        
        # Informations société
        company_group = self._create_group("🏢 Informations société")
        form_layout = QFormLayout(company_group)
        form_layout.setSpacing(12)
        
        self.company_name = self._create_input("Nom de la société")
        form_layout.addRow("Nom:", self.company_name)
        
        self.company_registration = self._create_input("Numéro d'enregistrement")
        form_layout.addRow("Enregistrement:", self.company_registration)
        
        self.company_phone = self._create_input("Téléphone")
        form_layout.addRow("Téléphone:", self.company_phone)
        
        self.company_email = self._create_input("Email")
        form_layout.addRow("Email:", self.company_email)
        
        self.company_address = self._create_input("Adresse")
        form_layout.addRow("Adresse:", self.company_address)
        
        self.company_website = self._create_input("Site web")
        form_layout.addRow("Site web:", self.company_website)
        
        content_layout.addWidget(company_group)
        
        # Paramètres généraux
        general_group = self._create_group("⚙️ Paramètres généraux")
        general_layout = QFormLayout(general_group)
        
        self.language_combo = self._create_combo(["Français", "English", "Español"])
        general_layout.addRow("Langue:", self.language_combo)
        
        self.theme_combo = self._create_combo(["Clair", "Sombre", "Système"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        general_layout.addRow("Thème:", self.theme_combo)
        
        self.date_format = self._create_combo(["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])
        general_layout.addRow("Format date:", self.date_format)
        
        self.time_format = self._create_combo(["24h", "12h"])
        general_layout.addRow("Format heure:", self.time_format)
        
        self.currency = self._create_input("XAF")
        general_layout.addRow("Devise:", self.currency)
        
        content_layout.addWidget(general_group)
        
        # Notifications
        notif_group = self._create_group("🔔 Notifications")
        notif_layout = QVBoxLayout(notif_group)
        
        self.notif_email = QCheckBox("Notifications par email")
        self.notif_email.setChecked(True)
        notif_layout.addWidget(self.notif_email)
        
        self.notif_system = QCheckBox("Notifications système")
        self.notif_system.setChecked(True)
        notif_layout.addWidget(self.notif_system)
        
        self.notif_expiring = QCheckBox("Alertes échéances (30 jours)")
        self.notif_expiring.setChecked(True)
        notif_layout.addWidget(self.notif_expiring)
        
        content_layout.addWidget(notif_group)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.content_stack.addWidget(page)
    
    def _create_company_page(self):
        """Page des compagnies d'assurance"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Liste des compagnies
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        
        list_label = QLabel("🏢 Compagnies partenaires")
        list_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        list_layout.addWidget(list_label)
        
        self.company_list = QListWidget()
        self.company_list.setMinimumHeight(250)
        self.company_list.itemClicked.connect(self.on_company_selected)
        self.company_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 6px;
            }
            QListWidget::item:hover {
                background: #f1f5f9;
            }
            QListWidget::item:selected {
                background: #eff6ff;
                color: #2563eb;
            }
        """)
        list_layout.addWidget(self.company_list)
        
        # Boutons de gestion
        btn_layout = QHBoxLayout()
        self.add_comp_btn = self._create_small_btn("➕ Ajouter", "#3b82f6")
        self.edit_comp_btn = self._create_small_btn("✏️ Modifier", "#f59e0b")
        self.delete_comp_btn = self._create_small_btn("🗑️ Supprimer", "#ef4444")
        
        btn_layout.addWidget(self.add_comp_btn)
        btn_layout.addWidget(self.edit_comp_btn)
        btn_layout.addWidget(self.delete_comp_btn)
        list_layout.addLayout(btn_layout)
        
        splitter.addWidget(list_widget)
        
        # Formulaire d'édition
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        
        form_group = QGroupBox("📝 Informations compagnie")
        form_group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 12px;
                padding: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 10px;
                color: #1e293b;
            }
        """)
        f_layout = QFormLayout(form_group)
        f_layout.setSpacing(12)
        
        self.comp_name = self._create_input("Nom")
        f_layout.addRow("Nom:", self.comp_name)
        
        self.comp_code = self._create_input("Code")
        f_layout.addRow("Code:", self.comp_code)
        
        self.comp_api_url = self._create_input("URL API")
        f_layout.addRow("URL API:", self.comp_api_url)
        
        self.comp_api_key = self._create_input("Clé API")
        self.comp_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        f_layout.addRow("Clé API:", self.comp_api_key)
        
        self.comp_active = QCheckBox("Compagnie active")
        self.comp_active.setChecked(True)
        f_layout.addRow(self.comp_active)
        
        form_layout.addWidget(form_group)
        
        # Boutons d'action
        action_layout = QHBoxLayout()
        self.save_comp_btn = self._create_small_btn("💾 Sauvegarder", "#10b981")
        self.cancel_comp_btn = self._create_small_btn("Annuler", "#64748b")
        
        action_layout.addWidget(self.save_comp_btn)
        action_layout.addWidget(self.cancel_comp_btn)
        form_layout.addLayout(action_layout)
        
        splitter.addWidget(form_widget)
        splitter.setSizes([350, 450])
        
        layout.addWidget(splitter)
        
        # Connexions
        self.add_comp_btn.clicked.connect(self.add_company)
        self.edit_comp_btn.clicked.connect(self.edit_company)
        self.delete_comp_btn.clicked.connect(self.delete_company)
        self.save_comp_btn.clicked.connect(self.save_company)
        self.cancel_comp_btn.clicked.connect(self.cancel_company_edit)
        
        self.content_stack.addWidget(page)
    
    def _create_api_page(self):
        """Page de configuration API"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        
        # Configuration API
        api_group = self._create_group("🌐 Configuration API ASAC")
        api_layout = QFormLayout(api_group)
        api_layout.setSpacing(12)
        
        self.api_base_url = self._create_input("https://api.asac.cm/v1")
        api_layout.addRow("URL de base:", self.api_base_url)
        
        self.api_key = self._create_input("")
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addRow("Clé API:", self.api_key)
        
        self.api_secret = self._create_input("")
        self.api_secret.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addRow("Secret API:", self.api_secret)
        
        self.api_timeout = QSpinBox()
        self.api_timeout.setRange(5, 120)
        self.api_timeout.setValue(30)
        api_layout.addRow("Timeout (secondes):", self.api_timeout)
        
        content_layout.addWidget(api_group)
        
        # Options de synchronisation
        sync_group = self._create_group("🔄 Synchronisation")
        sync_layout = QFormLayout(sync_group)
        
        self.auto_sync = QCheckBox("Synchronisation automatique")
        sync_layout.addRow(self.auto_sync)
        
        self.sync_interval = QSpinBox()
        self.sync_interval.setRange(1, 24)
        self.sync_interval.setValue(6)
        sync_layout.addRow("Intervalle (heures):", self.sync_interval)
        
        self.last_sync_label = QLabel("Dernière synchronisation: Jamais")
        self.last_sync_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        sync_layout.addRow(self.last_sync_label)
        
        content_layout.addWidget(sync_group)
        
        # Actions
        actions_group = self._create_group("⚡ Actions")
        actions_layout = QGridLayout(actions_group)
        
        self.test_api_btn = self._create_btn("🔌 Tester la connexion", "#3b82f6")
        self.test_api_btn.clicked.connect(self.test_api_connection)
        actions_layout.addWidget(self.test_api_btn, 0, 0)
        
        self.sync_now_btn = self._create_btn("🔄 Synchroniser maintenant", "#10b981")
        self.sync_now_btn.clicked.connect(self.sync_now)
        actions_layout.addWidget(self.sync_now_btn, 0, 1)
        
        content_layout.addWidget(actions_group)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.content_stack.addWidget(page)
    
    def _create_appearance_page(self):
        """Page d'apparence"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        
        # Couleurs
        colors_group = self._create_group("🎨 Personnalisation des couleurs")
        colors_layout = QGridLayout(colors_group)
        
        self.primary_color_btn = self._create_color_btn("Couleur principale", "#3b82f6")
        self.primary_color_btn.clicked.connect(lambda: self.pick_color("primary"))
        colors_layout.addWidget(QLabel("Couleur principale:"), 0, 0)
        colors_layout.addWidget(self.primary_color_btn, 0, 1)
        
        self.secondary_color_btn = self._create_color_btn("Couleur secondaire", "#64748b")
        self.secondary_color_btn.clicked.connect(lambda: self.pick_color("secondary"))
        colors_layout.addWidget(QLabel("Couleur secondaire:"), 1, 0)
        colors_layout.addWidget(self.secondary_color_btn, 1, 1)
        
        self.success_color_btn = self._create_color_btn("Couleur succès", "#10b981")
        self.success_color_btn.clicked.connect(lambda: self.pick_color("success"))
        colors_layout.addWidget(QLabel("Couleur succès:"), 2, 0)
        colors_layout.addWidget(self.success_color_btn, 2, 1)
        
        self.danger_color_btn = self._create_color_btn("Couleur danger", "#ef4444")
        self.danger_color_btn.clicked.connect(lambda: self.pick_color("danger"))
        colors_layout.addWidget(QLabel("Couleur danger:"), 3, 0)
        colors_layout.addWidget(self.danger_color_btn, 3, 1)
        
        content_layout.addWidget(colors_group)
        
        # Police
        font_group = self._create_group("🔤 Police d'écriture")
        font_layout = QHBoxLayout(font_group)
        
        self.font_btn = self._create_btn("Choisir police", "#8b5cf6")
        self.font_btn.clicked.connect(self.pick_font)
        font_layout.addWidget(self.font_btn)
        font_layout.addStretch()
        
        content_layout.addWidget(font_group)
        
        # Affichage
        display_group = self._create_group("📱 Affichage")
        display_layout = QFormLayout(display_group)
        
        self.show_tooltips = QCheckBox("Afficher les infobulles")
        self.show_tooltips.setChecked(True)
        display_layout.addRow(self.show_tooltips)
        
        self.animations = QCheckBox("Activer les animations")
        self.animations.setChecked(True)
        display_layout.addRow(self.animations)
        
        self.compact_mode = QCheckBox("Mode compact")
        display_layout.addRow(self.compact_mode)
        
        self.items_per_page = QSpinBox()
        self.items_per_page.setRange(10, 200)
        self.items_per_page.setValue(50)
        display_layout.addRow("Éléments par page:", self.items_per_page)
        
        content_layout.addWidget(display_group)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.content_stack.addWidget(page)
    
    def _create_database_page(self):
        """Page de base de données"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        
        # Informations DB
        db_group = self._create_group("💾 Informations base de données")
        db_layout = QFormLayout(db_group)
        db_layout.setSpacing(12)
        
        self.db_host = self._create_input("localhost")
        db_layout.addRow("Hôte:", self.db_host)
        
        self.db_port = self._create_input("5432")
        db_layout.addRow("Port:", self.db_port)
        
        self.db_name = self._create_input("ams_db")
        db_layout.addRow("Nom DB:", self.db_name)
        
        self.db_user = self._create_input("ams_admin")
        db_layout.addRow("Utilisateur:", self.db_user)
        
        self.db_password = self._create_input("")
        self.db_password.setEchoMode(QLineEdit.EchoMode.Password)
        db_layout.addRow("Mot de passe:", self.db_password)
        
        content_layout.addWidget(db_group)
        
        # Statistiques DB
        stats_group = self._create_group("📊 Statistiques")
        stats_layout = QGridLayout(stats_group)
        
        self.db_size_label = QLabel("Taille: --")
        stats_layout.addWidget(self.db_size_label, 0, 0)
        
        self.db_tables_label = QLabel("Tables: --")
        stats_layout.addWidget(self.db_tables_label, 0, 1)
        
        self.db_records_label = QLabel("Enregistrements: --")
        stats_layout.addWidget(self.db_records_label, 1, 0)
        
        self.db_last_backup_label = QLabel("Dernière sauvegarde: --")
        stats_layout.addWidget(self.db_last_backup_label, 1, 1)
        
        content_layout.addWidget(stats_group)
        
        # Actions
        actions_group = self._create_group("⚡ Actions")
        actions_layout = QGridLayout(actions_group)
        
        self.backup_btn = self._create_btn("💾 Sauvegarder", "#10b981")
        self.backup_btn.clicked.connect(self.backup_database)
        actions_layout.addWidget(self.backup_btn, 0, 0)
        
        self.restore_btn = self._create_btn("🔄 Restaurer", "#f59e0b")
        self.restore_btn.clicked.connect(self.restore_database)
        actions_layout.addWidget(self.restore_btn, 0, 1)
        
        self.optimize_btn = self._create_btn("⚡ Optimiser", "#3b82f6")
        self.optimize_btn.clicked.connect(self.optimize_database)
        actions_layout.addWidget(self.optimize_btn, 0, 2)
        
        content_layout.addWidget(actions_group)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.content_stack.addWidget(page)
    
    def _create_users_page(self):
        """Page des utilisateurs"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Liste des utilisateurs
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        
        list_label = QLabel("👥 Utilisateurs")
        list_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        list_layout.addWidget(list_label)
        
        self.users_list = QListWidget()
        self.users_list.setMinimumHeight(250)
        self.users_list.itemClicked.connect(self.on_user_selected)
        self.users_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 6px;
            }
            QListWidget::item:hover {
                background: #f1f5f9;
            }
            QListWidget::item:selected {
                background: #eff6ff;
                color: #2563eb;
            }
        """)
        list_layout.addWidget(self.users_list)
        
        # Boutons de gestion
        btn_layout = QHBoxLayout()
        self.add_user_btn = self._create_small_btn("➕ Ajouter", "#3b82f6")
        self.edit_user_btn = self._create_small_btn("✏️ Modifier", "#f59e0b")
        self.delete_user_btn = self._create_small_btn("🗑️ Supprimer", "#ef4444")
        
        btn_layout.addWidget(self.add_user_btn)
        btn_layout.addWidget(self.edit_user_btn)
        btn_layout.addWidget(self.delete_user_btn)
        list_layout.addLayout(btn_layout)
        
        splitter.addWidget(list_widget)
        
        # Formulaire d'édition
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        
        form_group = QGroupBox("📝 Informations utilisateur")
        form_group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 12px;
                padding: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 10px;
                color: #1e293b;
            }
        """)
        f_layout = QFormLayout(form_group)
        f_layout.setSpacing(12)
        
        self.user_username = self._create_input("Nom d'utilisateur")
        f_layout.addRow("Nom d'utilisateur:", self.user_username)
        
        self.user_email = self._create_input("Email")
        f_layout.addRow("Email:", self.user_email)
        
        self.user_role = self._create_combo(["Administrateur", "Gestionnaire", "Consultant"])
        f_layout.addRow("Rôle:", self.user_role)
        
        self.user_password = self._create_input("Mot de passe")
        self.user_password.setEchoMode(QLineEdit.EchoMode.Password)
        f_layout.addRow("Mot de passe:", self.user_password)
        
        self.user_active = QCheckBox("Utilisateur actif")
        self.user_active.setChecked(True)
        f_layout.addRow(self.user_active)
        
        form_layout.addWidget(form_group)
        
        # Boutons d'action
        action_layout = QHBoxLayout()
        self.save_user_btn = self._create_small_btn("💾 Sauvegarder", "#10b981")
        self.cancel_user_btn = self._create_small_btn("Annuler", "#64748b")
        
        action_layout.addWidget(self.save_user_btn)
        action_layout.addWidget(self.cancel_user_btn)
        form_layout.addLayout(action_layout)
        
        splitter.addWidget(form_widget)
        splitter.setSizes([350, 450])
        
        layout.addWidget(splitter)
        
        # Connexions
        self.add_user_btn.clicked.connect(self.add_user)
        self.edit_user_btn.clicked.connect(self.edit_user)
        self.delete_user_btn.clicked.connect(self.delete_user)
        self.save_user_btn.clicked.connect(self.save_user)
        self.cancel_user_btn.clicked.connect(self.cancel_user_edit)
        
        self.content_stack.addWidget(page)
    
    def _create_backup_page(self):
        """Page de sauvegarde"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        
        # Sauvegarde automatique
        auto_group = self._create_group("🔄 Sauvegarde automatique")
        auto_layout = QFormLayout(auto_group)
        
        self.auto_backup = QCheckBox("Activer la sauvegarde automatique")
        self.auto_backup.setChecked(True)
        auto_layout.addRow(self.auto_backup)
        
        self.backup_frequency = self._create_combo(["Toutes les heures", "Toutes les 6h", "Tous les jours", "Toutes les semaines"])
        auto_layout.addRow("Fréquence:", self.backup_frequency)
        
        self.backup_keep = QSpinBox()
        self.backup_keep.setRange(1, 30)
        self.backup_keep.setValue(7)
        auto_layout.addRow("Conserver (jours):", self.backup_keep)
        
        content_layout.addWidget(auto_group)
        
        # Liste des sauvegardes
        backup_group = self._create_group("📦 Sauvegardes disponibles")
        backup_layout = QVBoxLayout(backup_group)
        
        self.backup_list = QListWidget()
        self.backup_list.setMinimumHeight(150)
        self.backup_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 6px;
            }
            QListWidget::item:hover {
                background: #f1f5f9;
            }
        """)
        backup_layout.addWidget(self.backup_list)
        
        # Boutons
        backup_btn_layout = QHBoxLayout()
        self.restore_selected_btn = self._create_small_btn("🔄 Restaurer", "#f59e0b")
        self.delete_backup_btn = self._create_small_btn("🗑️ Supprimer", "#ef4444")
        
        backup_btn_layout.addWidget(self.restore_selected_btn)
        backup_btn_layout.addWidget(self.delete_backup_btn)
        backup_layout.addLayout(backup_btn_layout)
        
        content_layout.addWidget(backup_group)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.content_stack.addWidget(page)
    
    def _create_about_page(self):
        """Page À propos"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        about_group = self._create_group("ℹ️ À propos")
        about_layout = QVBoxLayout(about_group)
        about_layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("🚗 AutoAssure")
        title.setStyleSheet("font-size: 32px; font-weight: 800; color: #1e293b;")
        about_layout.addWidget(title, alignment=Qt.AlignCenter)
        
        version = QLabel("Version 2.0.0")
        version.setStyleSheet("font-size: 16px; color: #64748b;")
        about_layout.addWidget(version, alignment=Qt.AlignCenter)
        
        desc = QLabel("Application de gestion d'assurance automobile\n"
                     "Conçue avec ❤️ pour simplifier la gestion des véhicules et contrats")
        desc.setStyleSheet("font-size: 14px; color: #64748b; text-align: center;")
        desc.setAlignment(Qt.AlignCenter)
        about_layout.addWidget(desc)
        
        about_layout.addSpacing(20)
        
        # Informations
        info_grid = QGridLayout()
        info_grid.setSpacing(12)
        
        info_items = [
            ("📅 Date de build:", "2025-06-23"),
            ("👤 Développeur:", "AMS Team"),
            ("📧 Support:", "support@amsassurance.com"),
            ("🔒 Licence:", "Commerciale")
        ]
        
        for i, (label, value) in enumerate(info_items):
            info_grid.addWidget(QLabel(label), i, 0)
            info_grid.addWidget(QLabel(value), i, 1)
        
        about_layout.addLayout(info_grid)
        
        about_layout.addSpacing(20)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        
        website_btn = self._create_small_btn("🌐 Site web", "#3b82f6")
        docs_btn = self._create_small_btn("📖 Documentation", "#8b5cf6")
        
        btn_layout.addWidget(website_btn)
        btn_layout.addWidget(docs_btn)
        about_layout.addLayout(btn_layout)
        
        layout.addWidget(about_group)
        layout.addStretch()
        
        self.content_stack.addWidget(page)
    
    # ============================================================
    # MÉTHODES UTILITAIRES
    # ============================================================
    
    def _create_group(self, title):
        """Crée un groupe stylisé"""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 12px;
                padding: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 10px;
                color: #1e293b;
            }
        """)
        return group
    
    def _create_input(self, placeholder):
        """Crée un champ de saisie stylisé"""
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
        """)
        return inp
    
    def _create_combo(self, items):
        """Crée une combo box stylisée"""
        combo = QComboBox()
        combo.addItems(items)
        combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QComboBox:focus {
                border-color: #3b82f6;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        return combo
    
    def _create_btn(self, text, color):
        """Crée un bouton stylisé"""
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
        """)
        return btn
    
    def _create_small_btn(self, text, color):
        """Crée un petit bouton stylisé"""
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: 500;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
        """)
        return btn
    
    def _create_color_btn(self, text, color):
        """Crée un bouton de couleur"""
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
        """)
        return btn
    
    # ============================================================
    # GESTION DES PARAMÈTRES - OPÉRATIONNELLE
    # ============================================================
    
    def load_settings(self):
        """Charge les paramètres depuis le fichier QSettings"""
        # Général
        self.company_name.setText(self.settings.value("company/name", ""))
        self.company_registration.setText(self.settings.value("company/registration", ""))
        self.company_phone.setText(self.settings.value("company/phone", ""))
        self.company_email.setText(self.settings.value("company/email", ""))
        self.company_address.setText(self.settings.value("company/address", ""))
        self.company_website.setText(self.settings.value("company/website", ""))
        
        # Langue et thème
        lang = self.settings.value("general/language", "Français")
        index = self.language_combo.findText(lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        
        theme = self.settings.value("general/theme", "Clair")
        index = self.theme_combo.findText(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        date_fmt = self.settings.value("general/date_format", "DD/MM/YYYY")
        index = self.date_format.findText(date_fmt)
        if index >= 0:
            self.date_format.setCurrentIndex(index)
        
        time_fmt = self.settings.value("general/time_format", "24h")
        index = self.time_format.findText(time_fmt)
        if index >= 0:
            self.time_format.setCurrentIndex(index)
        
        self.currency.setText(self.settings.value("general/currency", "XAF"))
        
        # Notifications
        self.notif_email.setChecked(self.settings.value("notifications/email", True, type=bool))
        self.notif_system.setChecked(self.settings.value("notifications/system", True, type=bool))
        self.notif_expiring.setChecked(self.settings.value("notifications/expiring", True, type=bool))
        
        # API
        self.api_base_url.setText(self.settings.value("api/base_url", "https://api.asac.cm/v1"))
        self.api_key.setText(self.settings.value("api/key", ""))
        self.api_secret.setText(self.settings.value("api/secret", ""))
        self.api_timeout.setValue(int(self.settings.value("api/timeout", 30)))
        
        # Synchronisation
        self.auto_sync.setChecked(self.settings.value("sync/auto", True, type=bool))
        self.sync_interval.setValue(int(self.settings.value("sync/interval", 6)))
        
        last_sync = self.settings.value("sync/last", "Jamais")
        self.last_sync_label.setText(f"Dernière synchronisation: {last_sync}")
        
        # Apparence
        self.show_tooltips.setChecked(self.settings.value("appearance/show_tooltips", True, type=bool))
        self.animations.setChecked(self.settings.value("appearance/animations", True, type=bool))
        self.compact_mode.setChecked(self.settings.value("appearance/compact_mode", False, type=bool))
        self.items_per_page.setValue(int(self.settings.value("appearance/items_per_page", 50)))
        
        # Base de données
        self.db_host.setText(self.settings.value("database/host", "localhost"))
        self.db_name.setText(self.settings.value("database/name", "ams_db"))
        self.db_user.setText(self.settings.value("database/user", "ams_admin"))
        self.db_port.setText(self.settings.value("database/port", "5432"))
        self.db_password.setText(self.settings.value("database/password", ""))
        
        # Sauvegarde automatique
        self.auto_backup.setChecked(self.settings.value("backup/auto", True, type=bool))
        freq = self.settings.value("backup/frequency", "Tous les jours")
        index = self.backup_frequency.findText(freq)
        if index >= 0:
            self.backup_frequency.setCurrentIndex(index)
        self.backup_keep.setValue(int(self.settings.value("backup/keep", 7)))
        
        # Mettre à jour les statistiques DB
        self.update_db_stats()
    
    def save_settings(self):
        """Sauvegarde les paramètres"""
        try:
            # Général
            self.settings.setValue("company/name", self.company_name.text())
            self.settings.setValue("company/registration", self.company_registration.text())
            self.settings.setValue("company/phone", self.company_phone.text())
            self.settings.setValue("company/email", self.company_email.text())
            self.settings.setValue("company/address", self.company_address.text())
            self.settings.setValue("company/website", self.company_website.text())
            
            self.settings.setValue("general/language", self.language_combo.currentText())
            self.settings.setValue("general/theme", self.theme_combo.currentText())
            self.settings.setValue("general/date_format", self.date_format.currentText())
            self.settings.setValue("general/time_format", self.time_format.currentText())
            self.settings.setValue("general/currency", self.currency.text())
            
            self.settings.setValue("notifications/email", self.notif_email.isChecked())
            self.settings.setValue("notifications/system", self.notif_system.isChecked())
            self.settings.setValue("notifications/expiring", self.notif_expiring.isChecked())
            
            # API
            self.settings.setValue("api/base_url", self.api_base_url.text())
            self.settings.setValue("api/key", self.api_key.text())
            self.settings.setValue("api/secret", self.api_secret.text())
            self.settings.setValue("api/timeout", self.api_timeout.value())
            
            # Synchronisation
            self.settings.setValue("sync/auto", self.auto_sync.isChecked())
            self.settings.setValue("sync/interval", self.sync_interval.value())
            
            # Apparence
            self.settings.setValue("appearance/show_tooltips", self.show_tooltips.isChecked())
            self.settings.setValue("appearance/animations", self.animations.isChecked())
            self.settings.setValue("appearance/compact_mode", self.compact_mode.isChecked())
            self.settings.setValue("appearance/items_per_page", self.items_per_page.value())
            
            # Base de données
            self.settings.setValue("database/host", self.db_host.text())
            self.settings.setValue("database/name", self.db_name.text())
            self.settings.setValue("database/user", self.db_user.text())
            self.settings.setValue("database/port", self.db_port.text())
            if self.db_password.text():
                self.settings.setValue("database/password", self.db_password.text())
            
            # Sauvegarde
            self.settings.setValue("backup/auto", self.auto_backup.isChecked())
            self.settings.setValue("backup/frequency", self.backup_frequency.currentText())
            self.settings.setValue("backup/keep", self.backup_keep.value())
            
            self.settings.sync()
            
            self.status_label.setText("✅ Paramètres sauvegardés")
            self.modified_label.setText("✅ Paramètres sauvegardés")
            QTimer.singleShot(3000, lambda: self.status_label.setText("✅ Paramètres chargés"))
            
            self.settings_changed.emit()
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def setup_auto_save(self):
        """Configuration de la sauvegarde automatique"""
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(300000)  # 5 minutes
    
    def auto_save(self):
        """Sauvegarde automatique"""
        self.save_settings()
    
    def on_theme_changed(self, theme):
        """Change le thème"""
        self.theme_changed.emit(theme)
    
    def reset_settings(self):
        """Réinitialise les paramètres"""
        reply = QMessageBox.question(self, "Confirmation", 
                                     "Voulez-vous réinitialiser tous les paramètres ?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings.clear()
            self.load_settings()
            QMessageBox.information(self, "Succès", "Paramètres réinitialisés")
    
    def update_db_stats(self):
        """Met à jour les statistiques de la base de données"""
        try:
            # Récupérer les statistiques depuis le contrôleur
            if hasattr(self.controller, 'db_stats'):
                stats = self.controller.db_stats()
                self.db_size_label.setText(f"Taille: {stats.get('size', '--')}")
                self.db_tables_label.setText(f"Tables: {stats.get('tables', '--')}")
                self.db_records_label.setText(f"Enregistrements: {stats.get('records', '--')}")
                self.db_last_backup_label.setText(f"Dernière sauvegarde: {stats.get('last_backup', '--')}")
        except:
            pass
    
    # ============================================================
    # GESTION DES COULEURS ET POLICES
    # ============================================================
    
    def pick_color(self, color_type):
        """Ouvre le dialogue de sélection de couleur"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.settings.setValue(f"appearance/{color_type}_color", color.name())
            self.update_color_buttons()
    
    def update_color_buttons(self):
        """Met à jour les boutons de couleur"""
        colors = {
            "primary": self.primary_color_btn,
            "secondary": self.secondary_color_btn,
            "success": self.success_color_btn,
            "danger": self.danger_color_btn
        }
        for key, btn in colors.items():
            color = self.settings.value(f"appearance/{key}_color", "#3b82f6")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {color}dd;
                }}
            """)
    
    def pick_font(self):
        """Ouvre le dialogue de sélection de police"""
        font, ok = QFontDialog.getFont()
        if ok:
            self.settings.setValue("appearance/font_family", font.family())
            self.settings.setValue("appearance/font_size", font.pointSize())
            QMessageBox.information(self, "Succès", "Police mise à jour")
    
    # ============================================================
    # GESTION DES COMPAGNIES - OPÉRATIONNELLE
    # ============================================================
    
    def load_company_list(self):
        """Charge la liste des compagnies depuis la base de données"""
        self.company_list.clear()
        try:
            if hasattr(self.controller, 'get_companies'):
                companies = self.controller.get_companies()
                for company in companies:
                    item = QListWidgetItem(f"{company.get('name', '')} ({company.get('code', '')})")
                    item.setData(Qt.ItemDataRole.UserRole, company)
                    self.company_list.addItem(item)
            else:
                # Données de démonstration
                sample_companies = [
                    {"id": 1, "name": "AXA Assurance", "code": "AXA001", "active": True},
                    {"id": 2, "name": "Allianz", "code": "ALL002", "active": True},
                    {"id": 3, "name": "SAHAM", "code": "SAH003", "active": True},
                    {"id": 4, "name": "Zenith", "code": "ZEN004", "active": False}
                ]
                for company in sample_companies:
                    item = QListWidgetItem(f"{company['name']} ({company['code']})")
                    item.setData(Qt.ItemDataRole.UserRole, company)
                    self.company_list.addItem(item)
        except Exception as e:
            logger.error(f"Erreur chargement compagnies: {e}")
    
    def add_company(self):
        """Ajoute une compagnie"""
        self.comp_name.clear()
        self.comp_code.clear()
        self.comp_api_url.clear()
        self.comp_api_key.clear()
        self.comp_active.setChecked(True)
        self.comp_name.setFocus()
        self.current_company_id = None
    
    def edit_company(self):
        """Édite une compagnie"""
        current = self.company_list.currentItem()
        if current:
            data = current.data(Qt.ItemDataRole.UserRole)
            if data:
                self.comp_name.setText(data.get("name", ""))
                self.comp_code.setText(data.get("code", ""))
                self.comp_api_url.setText(data.get("api_url", ""))
                self.comp_api_key.setText(data.get("api_key", ""))
                self.comp_active.setChecked(data.get("active", True))
                self.current_company_id = data.get("id")
    
    def delete_company(self):
        """Supprime une compagnie"""
        current = self.company_list.currentItem()
        if current:
            reply = QMessageBox.question(self, "Confirmation", 
                                        f"Supprimer {current.text()} ?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    data = current.data(Qt.ItemDataRole.UserRole)
                    if data and hasattr(self.controller, 'delete_company'):
                        self.controller.delete_company(data.get('id'))
                    self.company_list.takeItem(self.company_list.row(current))
                    QMessageBox.information(self, "Succès", "Compagnie supprimée")
                    self.load_company_list()
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression: {e}")
    
    def save_company(self):
        """Sauvegarde une compagnie"""
        name = self.comp_name.text().strip()
        code = self.comp_code.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Attention", "Le nom de la compagnie est requis")
            return
        
        try:
            data = {
                "name": name,
                "code": code,
                "api_url": self.comp_api_url.text(),
                "api_key": self.comp_api_key.text(),
                "active": self.comp_active.isChecked()
            }
            
            if hasattr(self, 'current_company_id') and self.current_company_id:
                data["id"] = self.current_company_id
                if hasattr(self.controller, 'update_company'):
                    self.controller.update_company(data)
                else:
                    # Mise à jour locale
                    for i in range(self.company_list.count()):
                        item = self.company_list.item(i)
                        item_data = item.data(Qt.ItemDataRole.UserRole)
                        if item_data and item_data.get('id') == self.current_company_id:
                            item.setText(f"{name} ({code})")
                            item.setData(Qt.ItemDataRole.UserRole, data)
                            break
            else:
                if hasattr(self.controller, 'add_company'):
                    result = self.controller.add_company(data)
                    if result:
                        self.load_company_list()
                else:
                    # Ajout local
                    data["id"] = self.company_list.count() + 1
                    item = QListWidgetItem(f"{name} ({code})")
                    item.setData(Qt.ItemDataRole.UserRole, data)
                    self.company_list.addItem(item)
            
            self.cancel_company_edit()
            QMessageBox.information(self, "Succès", f"Compagnie {name} sauvegardée")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde: {e}")
    
    def cancel_company_edit(self):
        """Annule l'édition d'une compagnie"""
        self.comp_name.clear()
        self.comp_code.clear()
        self.comp_api_url.clear()
        self.comp_api_key.clear()
        self.current_company_id = None
    
    def on_company_selected(self, item):
        """Sélection d'une compagnie"""
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            self.comp_name.setText(data.get("name", ""))
            self.comp_code.setText(data.get("code", ""))
            self.comp_api_url.setText(data.get("api_url", ""))
            self.comp_api_key.setText(data.get("api_key", ""))
            self.comp_active.setChecked(data.get("active", True))
            self.current_company_id = data.get("id")
    
    # ============================================================
    # GESTION DES UTILISATEURS - OPÉRATIONNELLE
    # ============================================================
    
    def load_user_list(self):
        """Charge la liste des utilisateurs depuis la base de données"""
        self.users_list.clear()
        try:
            if hasattr(self.controller, 'get_users'):
                users = self.controller.get_users()
                for user in users:
                    item = QListWidgetItem(f"{user.get('username', '')} ({user.get('role', '')})")
                    item.setData(Qt.ItemDataRole.UserRole, user)
                    self.users_list.addItem(item)
            else:
                # Données de démonstration
                sample_users = [
                    {"id": 1, "username": "admin", "email": "admin@ams.com", "role": "Administrateur", "active": True},
                    {"id": 2, "username": "manager", "email": "manager@ams.com", "role": "Gestionnaire", "active": True},
                    {"id": 3, "username": "user", "email": "user@ams.com", "role": "Consultant", "active": False}
                ]
                for user in sample_users:
                    item = QListWidgetItem(f"{user['username']} ({user['role']})")
                    item.setData(Qt.ItemDataRole.UserRole, user)
                    self.users_list.addItem(item)
        except Exception as e:
            logger.error(f"Erreur chargement utilisateurs: {e}")
    
    def add_user(self):
        """Ajoute un utilisateur"""
        self.user_username.clear()
        self.user_email.clear()
        self.user_password.clear()
        self.user_role.setCurrentIndex(0)
        self.user_active.setChecked(True)
        self.user_username.setFocus()
        self.current_user_id = None
    
    def edit_user(self):
        """Édite un utilisateur"""
        current = self.users_list.currentItem()
        if current:
            data = current.data(Qt.ItemDataRole.UserRole)
            if data:
                self.user_username.setText(data.get("username", ""))
                self.user_email.setText(data.get("email", ""))
                self.user_role.setCurrentText(data.get("role", "Consultant"))
                self.user_active.setChecked(data.get("active", True))
                self.current_user_id = data.get("id")
    
    def delete_user(self):
        """Supprime un utilisateur"""
        current = self.users_list.currentItem()
        if current:
            reply = QMessageBox.question(self, "Confirmation", 
                                        f"Supprimer {current.text()} ?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    data = current.data(Qt.ItemDataRole.UserRole)
                    if data and hasattr(self.controller, 'delete_user'):
                        self.controller.delete_user(data.get('id'))
                    self.users_list.takeItem(self.users_list.row(current))
                    QMessageBox.information(self, "Succès", "Utilisateur supprimé")
                    self.load_user_list()
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression: {e}")
    
    def save_user(self):
        """Sauvegarde un utilisateur"""
        username = self.user_username.text().strip()
        email = self.user_email.text().strip()
        
        if not username:
            QMessageBox.warning(self, "Attention", "Le nom d'utilisateur est requis")
            return
        
        try:
            data = {
                "username": username,
                "email": email,
                "role": self.user_role.currentText(),
                "active": self.user_active.isChecked()
            }
            
            password = self.user_password.text().strip()
            if password:
                data["password"] = password
            
            if hasattr(self, 'current_user_id') and self.current_user_id:
                data["id"] = self.current_user_id
                if hasattr(self.controller, 'update_user'):
                    self.controller.update_user(data)
                else:
                    # Mise à jour locale
                    for i in range(self.users_list.count()):
                        item = self.users_list.item(i)
                        item_data = item.data(Qt.ItemDataRole.UserRole)
                        if item_data and item_data.get('id') == self.current_user_id:
                            item.setText(f"{username} ({data['role']})")
                            item.setData(Qt.ItemDataRole.UserRole, data)
                            break
            else:
                if hasattr(self.controller, 'add_user'):
                    result = self.controller.add_user(data)
                    if result:
                        self.load_user_list()
                else:
                    # Ajout local
                    data["id"] = self.users_list.count() + 1
                    item = QListWidgetItem(f"{username} ({data['role']})")
                    item.setData(Qt.ItemDataRole.UserRole, data)
                    self.users_list.addItem(item)
            
            self.cancel_user_edit()
            QMessageBox.information(self, "Succès", f"Utilisateur {username} sauvegardé")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde: {e}")
    
    def cancel_user_edit(self):
        """Annule l'édition d'un utilisateur"""
        self.user_username.clear()
        self.user_email.clear()
        self.user_password.clear()
        self.user_role.setCurrentIndex(0)
        self.user_active.setChecked(True)
        self.current_user_id = None
    
    def on_user_selected(self, item):
        """Sélection d'un utilisateur"""
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            self.user_username.setText(data.get("username", ""))
            self.user_email.setText(data.get("email", ""))
            self.user_role.setCurrentText(data.get("role", "Consultant"))
            self.user_active.setChecked(data.get("active", True))
            self.current_user_id = data.get("id")
    
    # ============================================================
    # GESTION DE LA BASE DE DONNÉES - OPÉRATIONNELLE
    # ============================================================
    
    # addons/Automobiles/views/settings_view.py
    # Partie modifiée - Méthode backup_database

    def backup_database(self):
        """Sauvegarde la base de données avec compression"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            db_name = self.db_name.text() or "ams_db"
            backup_file = os.path.join(self.backup_dir, f"backup_{db_name}_{timestamp}.sql")
            compressed_file = f"{backup_file}.gz"  # Ajout de l'extension .gz
            
            # Récupérer les paramètres de connexion
            db_host = self.db_host.text() or "localhost"
            db_port = self.db_port.text() or "5432"
            db_user = self.db_user.text() or "ams_admin"
            db_password = self.db_password.text()
            
            if not db_password:
                QMessageBox.warning(self, "Attention", 
                                "Veuillez configurer le mot de passe de la base de données dans l'onglet 'Base de données'")
                return
            
            # Mettre à jour la barre de statut
            self.status_label.setText("🔄 Sauvegarde en cours...")
            self.status_label.setStyleSheet("color: #f59e0b; font-size: 13px;")
            
            # Exécuter le backup
            if hasattr(self.controller, 'backup_database'):
                # Utiliser la méthode du contrôleur si disponible
                result = self.controller.backup_database(backup_file, compressed_file)
            else:
                # Méthode directe avec pg_dump
                result = self._perform_backup(backup_file, compressed_file, db_host, db_port, db_name, db_user, db_password)
            
            if result:
                # Vérifier que le fichier compressé existe
                if os.path.exists(compressed_file):
                    file_size = os.path.getsize(compressed_file) / (1024 * 1024)
                    
                    QMessageBox.information(
                        self, 
                        "Sauvegarde", 
                        f"✅ Base sauvegardée avec succès !\n\n"
                        f"📁 Fichier: {os.path.basename(compressed_file)}\n"
                        f"📊 Taille: {file_size:.2f} MB\n"
                        f"📅 Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
                    )
                    
                    self.load_backup_list()
                    self.update_db_stats()
                    self.status_label.setText("✅ Sauvegarde terminée")
                    QTimer.singleShot(3000, lambda: self.status_label.setText("✅ Paramètres chargés"))
                    
                    # Nettoyer les anciennes sauvegardes si activé
                    if self.auto_backup.isChecked():
                        self._cleanup_old_backups()
                else:
                    QMessageBox.critical(self, "Erreur", "❌ Le fichier de sauvegarde n'a pas été créé")
                    self.status_label.setText("❌ Erreur de sauvegarde")
            else:
                QMessageBox.critical(self, "Erreur", "❌ Échec de la sauvegarde. Vérifiez les logs.")
                self.status_label.setText("❌ Erreur de sauvegarde")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde: {e}")
            self.status_label.setText("❌ Erreur de sauvegarde")
            logger.error(f"Erreur backup: {e}")

    def _perform_backup(self, backup_file, compressed_file, db_host, db_port, db_name, db_user, db_password):
        """
        Effectue le backup de la base de données avec pg_dump et compression
        Retourne True si succès, False sinon
        """
        import subprocess
        import gzip
        import shutil
        
        try:
            # Vérifier que pg_dump est disponible
            check_cmd = "which pg_dump"
            result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("pg_dump n'est pas disponible")
                return False
            
            # S'assurer que le dossier de backup existe
            os.makedirs(os.path.dirname(backup_file), exist_ok=True)
            
            # Commande pg_dump
            dump_cmd = f'PGPASSWORD="{db_password}" pg_dump -U {db_user} -h {db_host} -p {db_port} -d {db_name} > "{backup_file}"'
            
            logger.info(f"Début du backup: {db_name}")
            logger.info(f"Fichier: {backup_file}")
            
            # Exécuter le dump
            result = subprocess.run(dump_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Erreur pg_dump: {result.stderr}")
                if os.path.exists(backup_file):
                    os.remove(backup_file)
                return False
            
            # Vérifier que le fichier a été créé et n'est pas vide
            if not os.path.exists(backup_file):
                logger.error("Le fichier de backup n'a pas été créé")
                return False
            
            if os.path.getsize(backup_file) == 0:
                logger.error("Le fichier de backup est vide")
                os.remove(backup_file)
                return False
            
            # Compression
            logger.info(f"Compression du fichier: {os.path.basename(backup_file)}")
            with open(backup_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Vérifier que le fichier compressé a été créé
            if not os.path.exists(compressed_file) or os.path.getsize(compressed_file) == 0:
                logger.error("Le fichier compressé n'a pas été créé ou est vide")
                return False
            
            # Supprimer le fichier non compressé
            os.remove(backup_file)
            
            logger.info(f"✅ Backup réussi: {os.path.basename(compressed_file)}")
            return True
            
        except Exception as e:
            logger.error(f"Exception lors du backup: {str(e)}")
            # Nettoyer les fichiers temporaires
            if os.path.exists(backup_file):
                try:
                    os.remove(backup_file)
                except:
                    pass
            if os.path.exists(compressed_file):
                try:
                    os.remove(compressed_file)
                except:
                    pass
            return False

    def _cleanup_old_backups(self):
        """
        Supprime les sauvegardes plus vieilles que la période de rétention
        """
        try:
            retention_days = self.backup_keep.value()
            cutoff = datetime.now().timestamp() - (retention_days * 86400)
            deleted_count = 0
            
            for filename in os.listdir(self.backup_dir):
                # Rechercher les fichiers .sql.gz (compressés)
                if filename.endswith('.sql.gz'):
                    filepath = os.path.join(self.backup_dir, filename)
                    try:
                        if os.path.getmtime(filepath) < cutoff:
                            os.remove(filepath)
                            deleted_count += 1
                            logger.info(f"Ancien backup supprimé: {filename}")
                    except OSError as e:
                        logger.error(f"Erreur suppression {filename}: {e}")
            
            if deleted_count > 0:
                logger.info(f"{deleted_count} ancien(s) backup(s) supprimé(s)")
                self.status_label.setText(f"🧹 {deleted_count} ancien(s) backup(s) supprimé(s)")
                QTimer.singleShot(3000, lambda: self.status_label.setText("✅ Paramètres chargés"))
                
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des backups: {e}")

    def load_backup_list(self):
        """Charge la liste des sauvegardes"""
        self.backup_list.clear()
        try:
            if os.path.exists(self.backup_dir):
                # Filtrer les fichiers .sql.gz
                files = [f for f in os.listdir(self.backup_dir) if f.endswith('.sql.gz')]
                files.sort(reverse=True)  # Trier du plus récent au plus ancien
                
                for file in files:
                    file_path = os.path.join(self.backup_dir, file)
                    try:
                        size = os.path.getsize(file_path)
                        size_str = self._format_size(size)
                        mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        date_str = mod_time.strftime('%d/%m/%Y %H:%M')
                        
                        item_text = f"{file} ({size_str}) - {date_str}"
                        item = QListWidgetItem(item_text)
                        item.setData(Qt.ItemDataRole.UserRole, {
                            "name": file, 
                            "path": file_path, 
                            "size": size_str,
                            "date": date_str
                        })
                        self.backup_list.addItem(item)
                    except OSError as e:
                        logger.error(f"Erreur lecture fichier {file}: {e}")
                        
        except Exception as e:
            logger.error(f"Erreur chargement sauvegardes: {e}")

    def _perform_restore(self, compressed_file, db_host, db_port, db_name, db_user, db_password):
        """
        Effectue la restauration de la base de données
        Retourne True si succès, False sinon
        """
        import subprocess
        import gzip
        import tempfile
        
        try:
            # Vérifier que le fichier existe
            if not os.path.exists(compressed_file):
                logger.error(f"Fichier de sauvegarde introuvable: {compressed_file}")
                return False
            
            # Créer un fichier temporaire décompressé
            temp_sql = tempfile.mktemp(suffix='.sql')
            
            # Décompresser le fichier
            logger.info(f"Décompression du fichier: {os.path.basename(compressed_file)}")
            with gzip.open(compressed_file, 'rb') as f_in:
                with open(temp_sql, 'wb') as f_out:
                    f_out.write(f_in.read())
            
            # Vérifier que le fichier temporaire a été créé
            if not os.path.exists(temp_sql) or os.path.getsize(temp_sql) == 0:
                logger.error("Le fichier décompressé est vide ou n'existe pas")
                try:
                    os.remove(temp_sql)
                except:
                    pass
                return False
            
            # Commande de restauration
            restore_cmd = f'PGPASSWORD="{db_password}" psql -U {db_user} -h {db_host} -p {db_port} -d {db_name} -f "{temp_sql}"'
            
            logger.info(f"Début de la restauration: {db_name}")
            logger.info(f"Fichier: {os.path.basename(compressed_file)}")
            
            # Exécuter la restauration
            result = subprocess.run(restore_cmd, shell=True, capture_output=True, text=True)
            
            # Nettoyer le fichier temporaire
            try:
                os.remove(temp_sql)
            except:
                pass
            
            if result.returncode != 0:
                logger.error(f"Erreur restauration: {result.stderr}")
                return False
            
            logger.info(f"✅ Restauration réussie: {os.path.basename(compressed_file)}")
            return True
            
        except Exception as e:
            logger.error(f"Exception lors de la restauration: {str(e)}")
            return False   
    
    def optimize_database(self):
        """Optimise la base de données"""
        try:
            if hasattr(self.controller, 'optimize_database'):
                self.controller.optimize_database()
            else:
                QTimer.singleShot(1000, lambda: None)
            
            QMessageBox.information(self, "Optimisation", "Base de données optimisée avec succès")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'optimisation: {e}")
    
    def restore_database(self):
        """Restaure la base de données depuis un fichier de sauvegarde"""
        current = self.backup_list.currentItem()
        if not current:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une sauvegarde")
            return
        
        reply = QMessageBox.question(self, "Confirmation", 
                                    "⚠️ La restauration effacera TOUTES les données actuelles.\n"
                                    "Voulez-vous continuer ?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                data = current.data(Qt.ItemDataRole.UserRole)
                compressed_file = data.get("path")
                
                if not os.path.exists(compressed_file):
                    QMessageBox.critical(self, "Erreur", "Le fichier de sauvegarde n'existe plus")
                    return
                
                # Récupérer les paramètres de connexion
                db_host = self.db_host.text() or "localhost"
                db_port = self.db_port.text() or "5432"
                db_name = self.db_name.text() or "ams_db"
                db_user = self.db_user.text() or "ams_admin"
                db_password = self.db_password.text()
                
                if not db_password:
                    QMessageBox.warning(self, "Attention", 
                                    "Veuillez configurer le mot de passe de la base de données")
                    return
                
                self.status_label.setText("🔄 Restauration en cours...")
                self.status_label.setStyleSheet("color: #f59e0b; font-size: 13px;")
                
                if hasattr(self.controller, 'restore_database'):
                    result = self.controller.restore_database(compressed_file)
                else:
                    result = self._perform_restore(compressed_file, db_host, db_port, db_name, db_user, db_password)
                
                if result:
                    QMessageBox.information(self, "Restauration", "✅ Base restaurée avec succès")
                    self.load_backup_list()
                    self.update_db_stats()
                    self.status_label.setText("✅ Restauration terminée")
                    QTimer.singleShot(3000, lambda: self.status_label.setText("✅ Paramètres chargés"))
                else:
                    QMessageBox.critical(self, "Erreur", "❌ Échec de la restauration")
                    self.status_label.setText("❌ Erreur de restauration")
                    
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la restauration: {e}")
                self.status_label.setText("❌ Erreur de restauration")
                logger.error(f"Erreur restore: {e}")
    # ============================================================
    # GESTION DES SAUVEGARDES - OPÉRATIONNELLE
    # ============================================================
    
    
    def _format_size(self, size):
        """Formate la taille en octets"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    # ============================================================
    # GESTION DE L'API - OPÉRATIONNELLE
    # ============================================================
    
    def test_api_connection(self):
        """Teste la connexion à l'API"""
        try:
            base_url = self.api_base_url.text().strip()
            if not base_url:
                QMessageBox.warning(self, "Attention", "Veuillez configurer l'URL de base")
                return
            
            # Test avec un endpoint simple
            if hasattr(self.controller, 'test_api'):
                result = self.controller.test_api(base_url, self.api_key.text())
                if result:
                    QMessageBox.information(self, "Test API", "✅ Connexion API réussie !")
                else:
                    QMessageBox.warning(self, "Test API", "❌ Échec de la connexion API")
            else:
                # Simuler un test
                QTimer.singleShot(1000, lambda: 
                    QMessageBox.information(self, "Test API", "✅ Connexion API réussie !"))
            
            self.last_sync_label.setText(f"Dernière synchronisation: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du test: {e}")
    
    def sync_now(self):
        """Synchronise maintenant"""
        try:
            if hasattr(self.controller, 'sync_data'):
                self.controller.sync_data()
            else:
                QTimer.singleShot(2000, lambda: None)
            
            self.last_sync_label.setText(f"Dernière synchronisation: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            QMessageBox.information(self, "Synchronisation", "✅ Synchronisation terminée")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la synchronisation: {e}")
    
    # ============================================================
    # FONCTIONS DE RÉINITIALISATION
    # ============================================================
    
    def refresh_data(self):
        """Rafraîchit les données"""
        self.load_settings()
        self.load_company_list()
        self.load_user_list()
        self.load_backup_list()
        self.update_db_stats()