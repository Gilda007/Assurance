# addons/Automobiles/views/settings_view.py
"""
Vue des paramètres et configuration
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QTabWidget, QGroupBox, QFormLayout, QLineEdit,
    QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox,
    QColorDialog, QFontDialog, QFileDialog, QMessageBox,
    QListWidget, QListWidgetItem, QStackedWidget
)
from PySide6.QtCore import Qt, QSettings, Signal
from PySide6.QtGui import QColor, QFont

from addons.Automobiles.views.style import Colors, Fonts, Spacing
from addons.Automobiles.views.widgets.modern_card import ModernCard


class SettingsView(QWidget):
    """Vue des paramètres de l'application"""
    
    settings_changed = Signal()
    
    def __init__(self, controller, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.settings = QSettings("AutoAssure", "AutomobileModule")
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.LG)
        
        # En-tête
        header = QLabel("Paramètres")
        header.setStyleSheet(f"""
            font-size: {Fonts.H2}px;
            font-weight: {Fonts.BOLD};
            padding: {Spacing.MD}px 0;
        """)
        layout.addWidget(header)
        
        # Onglets principaux
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                background-color: {Colors.WHITE};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
            }}
            QTabBar::tab {{
                padding: 10px 20px;
                margin-right: 4px;
            }}
        """)
        
        # Créer les onglets
        self.setup_general_tab()
        self.setup_company_tab()
        self.setup_api_tab()
        self.setup_appearance_tab()
        self.setup_database_tab()
        self.setup_users_tab()
        
        layout.addWidget(self.tabs)
        
        # Boutons d'action
        self.setup_buttons()
        layout.addWidget(self.buttons_card)
    
    def setup_general_tab(self):
        """Onglet paramètres généraux"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(Spacing.LG)
        
        # Informations société
        company_group = QGroupBox("Informations société")
        company_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: {Fonts.SEMIBOLD};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
                margin-top: 12px;
            }}
        """)
        
        form_layout = QFormLayout(company_group)
        form_layout.setSpacing(Spacing.MD)
        
        self.company_name = QLineEdit()
        form_layout.addRow("Nom de la société:", self.company_name)
        
        self.company_registration = QLineEdit()
        form_layout.addRow("Numéro d'enregistrement:", self.company_registration)
        
        self.company_phone = QLineEdit()
        form_layout.addRow("Téléphone:", self.company_phone)
        
        self.company_email = QLineEdit()
        form_layout.addRow("Email:", self.company_email)
        
        self.company_address = QLineEdit()
        form_layout.addRow("Adresse:", self.company_address)
        
        layout.addWidget(company_group)
        
        # Paramètres généraux
        general_group = QGroupBox("Paramètres généraux")
        general_group.setStyleSheet(company_group.styleSheet())
        
        general_layout = QFormLayout(general_group)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Français", "English"])
        general_layout.addRow("Langue:", self.language_combo)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Clair", "Sombre", "Système"])
        general_layout.addRow("Thème:", self.theme_combo)
        
        self.date_format = QComboBox()
        self.date_format.addItems(["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])
        general_layout.addRow("Format date:", self.date_format)
        
        self.currency = QLineEdit("XAF")
        general_layout.addRow("Devise:", self.currency)
        
        layout.addWidget(general_group)
        layout.addStretch()
        
        self.tabs.addTab(tab, "⚙️ Général")
    
    def setup_company_tab(self):
        """Onglet compagnies d'assurance"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Liste des compagnies
        self.company_list = QListWidget()
        self.company_list.setMinimumHeight(200)
        self.company_list.itemClicked.connect(self.on_company_selected)
        layout.addWidget(QLabel("Compagnies partenaires:"))
        layout.addWidget(self.company_list)
        
        # Formulaire d'édition
        form_group = QGroupBox("Informations compagnie")
        form_layout = QFormLayout(form_group)
        
        self.comp_name = QLineEdit()
        form_layout.addRow("Nom:", self.comp_name)
        
        self.comp_code = QLineEdit()
        form_layout.addRow("Code compagnie:", self.comp_code)
        
        self.comp_api_url = QLineEdit()
        form_layout.addRow("URL API:", self.comp_api_url)
        
        self.comp_api_key = QLineEdit()
        self.comp_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Clé API:", self.comp_api_key)
        
        # Boutons
        btn_layout = QHBoxLayout()
        self.add_comp_btn = QPushButton("➕ Ajouter")
        self.update_comp_btn = QPushButton("✏️ Modifier")
        self.delete_comp_btn = QPushButton("🗑️ Supprimer")
        
        btn_layout.addWidget(self.add_comp_btn)
        btn_layout.addWidget(self.update_comp_btn)
        btn_layout.addWidget(self.delete_comp_btn)
        
        layout.addWidget(form_group)
        layout.addLayout(btn_layout)
        
        self.tabs.addTab(tab, "🏢 Compagnies")
        
        # Connexions
        self.add_comp_btn.clicked.connect(self.add_company)
        self.update_comp_btn.clicked.connect(self.update_company)
        self.delete_comp_btn.clicked.connect(self.delete_company)
    
    def setup_api_tab(self):
        """Onglet configuration API ASAC"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(Spacing.LG)
        
        # Configuration API
        api_group = QGroupBox("Configuration API ASAC")
        api_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 12px;
            }
        """)
        
        form_layout = QFormLayout(api_group)
        
        self.api_base_url = QLineEdit()
        self.api_base_url.setPlaceholderText("https://api.asac.cm/v1")
        form_layout.addRow("URL de base:", self.api_base_url)
        
        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Clé API:", self.api_key)
        
        self.api_secret = QLineEdit()
        self.api_secret.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Secret API:", self.api_secret)
        
        self.api_timeout = QSpinBox()
        self.api_timeout.setRange(5, 120)
        self.api_timeout.setValue(30)
        form_layout.addRow("Timeout (secondes):", self.api_timeout)
        
        layout.addWidget(api_group)
        
        # Options de synchronisation
        sync_group = QGroupBox("Synchronisation")
        sync_layout = QFormLayout(sync_group)
        
        self.auto_sync = QCheckBox("Synchronisation automatique")
        sync_layout.addRow(self.auto_sync)
        
        self.sync_interval = QSpinBox()
        self.sync_interval.setRange(1, 24)
        self.sync_interval.setValue(6)
        sync_layout.addRow("Intervalle (heures):", self.sync_interval)
        
        layout.addWidget(sync_group)
        
        # Bouton test
        test_btn = QPushButton("🔌 Tester la connexion API")
        test_btn.clicked.connect(self.test_api_connection)
        layout.addWidget(test_btn)
        
        layout.addStretch()
        
        self.tabs.addTab(tab, "🌐 API ASAC")
    
    def setup_appearance_tab(self):
        """Onglet apparence"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(Spacing.LG)
        
        # Couleurs
        colors_group = QGroupBox("Personnalisation des couleurs")
        colors_layout = QFormLayout(colors_group)
        
        self.primary_color_btn = QPushButton("Couleur principale")
        self.primary_color_btn.clicked.connect(lambda: self.pick_color("primary"))
        colors_layout.addRow("Couleur principale:", self.primary_color_btn)
        
        self.secondary_color_btn = QPushButton("Couleur secondaire")
        self.secondary_color_btn.clicked.connect(lambda: self.pick_color("secondary"))
        colors_layout.addRow("Couleur secondaire:", self.secondary_color_btn)
        
        layout.addWidget(colors_group)
        
        # Police
        font_group = QGroupBox("Police d'écriture")
        font_layout = QFormLayout(font_group)
        
        self.font_btn = QPushButton("Choisir police")
        self.font_btn.clicked.connect(self.pick_font)
        font_layout.addRow("Police:", self.font_btn)
        
        layout.addWidget(font_group)
        
        # Affichage
        display_group = QGroupBox("Affichage")
        display_layout = QFormLayout(display_group)
        
        self.show_tooltips = QCheckBox("Afficher les infobulles")
        self.show_tooltips.setChecked(True)
        display_layout.addRow(self.show_tooltips)
        
        self.animations = QCheckBox("Activer les animations")
        self.animations.setChecked(True)
        display_layout.addRow(self.animations)
        
        self.items_per_page = QSpinBox()
        self.items_per_page.setRange(10, 200)
        self.items_per_page.setValue(50)
        display_layout.addRow("Éléments par page:", self.items_per_page)
        
        layout.addWidget(display_group)
        layout.addStretch()
        
        self.tabs.addTab(tab, "🎨 Apparence")
    
    def setup_database_tab(self):
        """Onglet base de données"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(Spacing.LG)
        
        # Informations DB
        db_group = QGroupBox("Informations base de données")
        db_layout = QFormLayout(db_group)
        
        self.db_host = QLineEdit()
        db_layout.addRow("Hôte:", self.db_host)
        
        self.db_name = QLineEdit()
        db_layout.addRow("Nom DB:", self.db_name)
        
        self.db_user = QLineEdit()
        db_layout.addRow("Utilisateur:", self.db_user)
        
        self.db_port = QLineEdit()
        db_layout.addRow("Port:", self.db_port)
        
        layout.addWidget(db_group)
        
        # Actions
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        backup_btn = QPushButton("💾 Sauvegarder la base de données")
        backup_btn.clicked.connect(self.backup_database)
        actions_layout.addWidget(backup_btn)
        
        restore_btn = QPushButton("🔄 Restaurer la base de données")
        restore_btn.clicked.connect(self.restore_database)
        actions_layout.addWidget(restore_btn)
        
        layout.addWidget(actions_group)
        layout.addStretch()
        
        self.tabs.addTab(tab, "💾 Base de données")
    
    def setup_users_tab(self):
        """Onglet utilisateurs"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Liste des utilisateurs
        self.users_list = QListWidget()
        self.users_list.setMinimumHeight(200)
        self.users_list.itemClicked.connect(self.on_user_selected)
        layout.addWidget(QLabel("Utilisateurs:"))
        layout.addWidget(self.users_list)
        
        # Formulaire d'édition
        form_group = QGroupBox("Informations utilisateur")
        form_layout = QFormLayout(form_group)
        
        self.user_username = QLineEdit()
        form_layout.addRow("Nom d'utilisateur:", self.user_username)
        
        self.user_email = QLineEdit()
        form_layout.addRow("Email:", self.user_email)
        
        self.user_role = QComboBox()
        self.user_role.addItems(["Administrateur", "Gestionnaire", "Consultant"])
        form_layout.addRow("Rôle:", self.user_role)
        
        self.user_password = QLineEdit()
        self.user_password.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Mot de passe:", self.user_password)
        
        # Boutons
        btn_layout = QHBoxLayout()
        self.add_user_btn = QPushButton("➕ Ajouter")
        self.update_user_btn = QPushButton("✏️ Modifier")
        self.delete_user_btn = QPushButton("🗑️ Supprimer")
        
        btn_layout.addWidget(self.add_user_btn)
        btn_layout.addWidget(self.update_user_btn)
        btn_layout.addWidget(self.delete_user_btn)
        
        layout.addWidget(form_group)
        layout.addLayout(btn_layout)
        
        self.tabs.addTab(tab, "👥 Utilisateurs")
        
        # Connexions
        self.add_user_btn.clicked.connect(self.add_user)
        self.update_user_btn.clicked.connect(self.update_user)
        self.delete_user_btn.clicked.connect(self.delete_user)
    
    def setup_buttons(self):
        """Configure les boutons d'action"""
        self.buttons_card = ModernCard()
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.save_btn = QPushButton("💾 Sauvegarder")
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.SUCCESS};
                padding: 10px 30px;
            }}
        """)
        self.save_btn.clicked.connect(self.save_settings)
        
        self.reset_btn = QPushButton("↺ Réinitialiser")
        self.reset_btn.clicked.connect(self.reset_settings)
        
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.clicked.connect(self.cancel_settings)
        
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        self.buttons_card.add_layout(btn_layout)
    
    def load_settings(self):
        """Charge les paramètres sauvegardés"""
        # Général
        self.company_name.setText(self.settings.value("company/name", ""))
        self.company_registration.setText(self.settings.value("company/registration", ""))
        self.company_phone.setText(self.settings.value("company/phone", ""))
        self.company_email.setText(self.settings.value("company/email", ""))
        self.company_address.setText(self.settings.value("company/address", ""))
        
        # API
        self.api_base_url.setText(self.settings.value("api/base_url", "https://api.asac.cm/v1"))
        self.api_key.setText(self.settings.value("api/key", ""))
        self.api_timeout.setValue(int(self.settings.value("api/timeout", 30)))
        
        # Apparence
        self.show_tooltips.setChecked(self.settings.value("appearance/show_tooltips", True, type=bool))
        self.animations.setChecked(self.settings.value("appearance/animations", True, type=bool))
        self.items_per_page.setValue(int(self.settings.value("appearance/items_per_page", 50)))
        
        # Base de données
        self.db_host.setText(self.settings.value("database/host", "localhost"))
        self.db_name.setText(self.settings.value("database/name", "ams_db"))
        self.db_user.setText(self.settings.value("database/user", "ams_admin"))
        self.db_port.setText(self.settings.value("database/port", "5432"))
        
        # Charger les listes
        self.load_companies()
        self.load_users()
    
    def load_companies(self):
        """Charge la liste des compagnies"""
        # TODO: Charger depuis la base
        self.company_list.clear()
        sample_companies = ["AXA Assurance", "Allianz", "SAHAM", "Zenith"]
        for company in sample_companies:
            self.company_list.addItem(company)
    
    def load_users(self):
        """Charge la liste des utilisateurs"""
        # TODO: Charger depuis la base
        self.users_list.clear()
        sample_users = [("admin", "Administrateur"), ("manager", "Gestionnaire"), ("user", "Consultant")]
        for username, role in sample_users:
            item = QListWidgetItem(f"{username} ({role})")
            item.setData(Qt.ItemDataRole.UserRole, {"username": username, "role": role})
            self.users_list.addItem(item)
    
    def save_settings(self):
        """Sauvegarde les paramètres"""
        # Général
        self.settings.setValue("company/name", self.company_name.text())
        self.settings.setValue("company/registration", self.company_registration.text())
        self.settings.setValue("company/phone", self.company_phone.text())
        self.settings.setValue("company/email", self.company_email.text())
        self.settings.setValue("company/address", self.company_address.text())
        
        # API
        self.settings.setValue("api/base_url", self.api_base_url.text())
        self.settings.setValue("api/key", self.api_key.text())
        self.settings.setValue("api/timeout", self.api_timeout.value())
        
        # Apparence
        self.settings.setValue("appearance/show_tooltips", self.show_tooltips.isChecked())
        self.settings.setValue("appearance/animations", self.animations.isChecked())
        self.settings.setValue("appearance/items_per_page", self.items_per_page.value())
        
        # Base de données
        self.settings.setValue("database/host", self.db_host.text())
        self.settings.setValue("database/name", self.db_name.text())
        self.settings.setValue("database/user", self.db_user.text())
        self.settings.setValue("database/port", self.db_port.text())
        
        self.settings.sync()
        
        QMessageBox.information(self, "Succès", "Paramètres sauvegardés avec succès")
        self.settings_changed.emit()
    
    def reset_settings(self):
        """Réinitialise les paramètres"""
        reply = QMessageBox.question(self, "Confirmation", 
                                     "Voulez-vous réinitialiser tous les paramètres ?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings.clear()
            self.load_settings()
            QMessageBox.information(self, "Succès", "Paramètres réinitialisés")
    
    def cancel_settings(self):
        """Annule les modifications"""
        self.load_settings()
        QMessageBox.information(self, "Info", "Modifications annulées")
    
    def pick_color(self, color_type):
        """Ouvre le dialogue de sélection de couleur"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.settings.setValue(f"appearance/{color_type}_color", color.name())
    
    def pick_font(self):
        """Ouvre le dialogue de sélection de police"""
        font, ok = QFontDialog.getFont()
        if ok:
            self.settings.setValue("appearance/font_family", font.family())
            self.settings.setValue("appearance/font_size", font.pointSize())
    
    def test_api_connection(self):
        """Teste la connexion à l'API"""
        QMessageBox.information(self, "Test API", "Fonctionnalité à implémenter")
    
    def backup_database(self):
        """Sauvegarde la base de données"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Sauvegarder la base", "", "SQL Backup (*.sql)")
        if file_path:
            QMessageBox.information(self, "Sauvegarde", f"Base sauvegardée vers {file_path}")
    
    def restore_database(self):
        """Restaure la base de données"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Restaurer la base", "", "SQL Backup (*.sql)")
        if file_path:
            QMessageBox.information(self, "Restauration", f"Base restaurée depuis {file_path}")
    
    def add_company(self):
        """Ajoute une compagnie"""
        name = self.comp_name.text()
        if name:
            self.company_list.addItem(name)
            self.comp_name.clear()
            QMessageBox.information(self, "Succès", f"Compagnie {name} ajoutée")
    
    def update_company(self):
        """Met à jour une compagnie"""
        current = self.company_list.currentItem()
        if current and self.comp_name.text():
            current.setText(self.comp_name.text())
            QMessageBox.information(self, "Succès", "Compagnie modifiée")
    
    def delete_company(self):
        """Supprime une compagnie"""
        current = self.company_list.currentItem()
        if current:
            reply = QMessageBox.question(self, "Confirmation", 
                                        f"Supprimer {current.text()} ?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.company_list.takeItem(self.company_list.row(current))
    
    def on_company_selected(self, item):
        """Sélection d'une compagnie"""
        self.comp_name.setText(item.text())
    
    def on_user_selected(self, item):
        """Sélection d'un utilisateur"""
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            self.user_username.setText(data.get("username", ""))
            self.user_role.setCurrentText(data.get("role", "Consultant"))
    
    def add_user(self):
        """Ajoute un utilisateur"""
        username = self.user_username.text()
        if username:
            role = self.user_role.currentText()
            item = QListWidgetItem(f"{username} ({role})")
            item.setData(Qt.ItemDataRole.UserRole, {"username": username, "role": role})
            self.users_list.addItem(item)
            self.user_username.clear()
            self.user_password.clear()
            QMessageBox.information(self, "Succès", f"Utilisateur {username} ajouté")
    
    def update_user(self):
        """Met à jour un utilisateur"""
        current = self.users_list.currentItem()
        if current and self.user_username.text():
            username = self.user_username.text()
            role = self.user_role.currentText()
            current.setText(f"{username} ({role})")
            current.setData(Qt.ItemDataRole.UserRole, {"username": username, "role": role})
            QMessageBox.information(self, "Succès", "Utilisateur modifié")
    
    def delete_user(self):
        """Supprime un utilisateur"""
        current = self.users_list.currentItem()
        if current:
            reply = QMessageBox.question(self, "Confirmation", 
                                        f"Supprimer {current.text()} ?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.users_list.takeItem(self.users_list.row(current))
    
    def refresh_data(self):
        """Rafraîchit les données"""
        self.load_settings()