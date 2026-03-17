from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLabel, QPushButton, QListWidgetItem, QStackedWidget, QListWidget, QFrame, QMessageBox, QDialog)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QIcon, QFont
from addons.Paramètres.controllers import controller
from addons.Paramètres.views.dialog_form import UserDialog
from addons.Paramètres.views.user_from import CustomUserForm
from addons.Paramètres.reports.audit_exporter import AuditReporter
from addons.Paramètres.views.parametre_module_view import ParametreModuleWidget
from addons.Paramètres.views.accout_setting_view import AccountSettingsView
from addons.Paramètres.views.about_us_view import AboutUsView
from addons.Paramètres.views.user_list_view import UserListPage

class ParametreMainView(QWidget):
    def __init__(self, controller=None, user=None):
        super().__init__()
        self.controller = controller
        print(self.controller)
        self.user = user
        self.pages_cache = {} # Stocke les pages déjà créées

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # --- Sidebar de navigation ---
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setObjectName("ParamNav")
        # ... (votre style CSS ici) ...

        # --- Stack d'affichage ---
        self.container = QStackedWidget()

        # Définition des menus
        self.menu_items = [
            ("👥 Utilisateurs", "users"),
            ("📦 Modules", "modules"),
            ("👤 Mon Compte", "account"),
            ("ℹ️ À propos", "about")
        ]

        for text, key in self.menu_items:
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, key) # On stocke la clé technique
            self.sidebar.addItem(item)

        self.sidebar.currentRowChanged.connect(self.display_page)
        
        self.layout.addWidget(self.sidebar)
        self.layout.addWidget(self.container)

        # Charger la première page
        self.sidebar.setCurrentRow(0)
    
    def display_page(self, row):
        item = self.sidebar.item(row)
        if not item: return
        key = item.data(Qt.UserRole)
        
        if key not in self.pages_cache:
            # Sécurité : on vérifie si self.controller est un dictionnaire ou un objet unique
            is_dict = isinstance(self.controller, dict)
            
            if key == "users":
                ctrl = self.controller.get('user') if is_dict else self.controller
                page = UserListPage(ctrl, self.user)
                
            # Dans views.py, à l'intérieur de display_page
            elif key == "modules":
                # On importe notre nouveau contrôleur
                try:
                    from addons.Paramètres.controllers.module_controller import ModuleController
                    # On l'instancie
                    module_ctrl = ModuleController(getattr(self.controller, 'session', None))
                    
                    # On crée la vue avec le bon contrôleur
                    page = ParametreModuleWidget(module_ctrl, self.user)
                except ImportError:
                    # Si vous avez tout mis dans controller.py
                    from addons.Paramètres.controllers.controller import ModuleController
                    module_ctrl = ModuleController(getattr(self.controller, 'session', None))
                    page = ParametreModuleWidget(module_ctrl, self.user)
                
            elif key == "account":
    # Vérifie si self.user existe avant de créer la page
    if self.user:
        # On passe le contrôleur et l'utilisateur (vérifie l'ordre des arguments)
        page = AccountSettingsView(self.controller, self.user)
    else:
        # Page de secours ou message d'erreur si pas d'utilisateur connecté
        page = QLabel("Erreur : Aucun utilisateur connecté")
                
            else:
                # Pour 'A propos' ou autre page sans contrôleur spécifique
                page = AboutUsView()
            
            # On enregistre la page et on l'ajoute à l'affichage
            page.setObjectName(key)
            self.pages_cache[key] = page
            self.container.addWidget(page)
            
        # On affiche la page correspondante
        self.container.setCurrentWidget(self.pages_cache[key])
    # --- GÉNÉRATEURS DE PAGES ---
    def get_user_page(self):
        return UserListPage(self.controller, self.user)

    def get_module_page(self):
        return ParametreModuleWidget(self.controller, self.user)

    def get_account_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("<h2>Gestion du Compte</h2><p>Modifier votre mot de passe ici.</p>"))
        return page

    def get_about_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("<h2>AMS AUTO v1.1</h2><p>Système de gestion d'assurance.<br>2026 Tous droits réservés.</p>"))
        return page

    def setup_stats_cards(self):
        stats_layout = QHBoxLayout()
        stats = [
            ("Modules Actifs", "12", "#dcfce7", "#166534"),
            ("Espace Utilisé", "45 MB", "#dbeafe", "#1e40af"),
            ("Alertes Audit", "2", "#fee2e2", "#991b1b")
        ]
        for title, val, bg, fg in stats:
            card = QFrame()
            card.setStyleSheet(f"background-color: {bg}; border-radius: 15px; min-height: 80px;")
            l = QVBoxLayout(card)
            t = QLabel(title); t.setStyleSheet(f"color: {fg}; font-weight: bold; font-size: 12px;")
            v = QLabel(val); v.setStyleSheet(f"color: {fg}; font-size: 20px; font-weight: 800;")
            l.addWidget(t); l.addWidget(v)
            stats_layout.addWidget(card)
        self.main_layout.addLayout(stats_layout)

    def setup_table(self):
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["MODULE", "VERSION", "STATUT", "ACTIONS"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white; border-radius: 15px; border: 1px solid #e2e8f0;
                alternate-background-color: #f8fafc; gridline-color: transparent;
            }
            QHeaderView::section {
                background-color: transparent; padding: 15px; border: none;
                font-weight: bold; color: #64748b; font-size: 12px;
            }
        """)
        self.main_layout.addWidget(self.table) 

    def apply_styles(self):
        self.setStyleSheet("""
            #UserListView { background-color: #f8f9fa; }
            
            QTableWidget {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                gridline-color: transparent;
                alternate-background-color: #fdfdfd;
                font-size: 13px;
            }
            
            QHeaderView::section {
                background-color: #f1f3f5;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #dee2e6;
                font-weight: bold;
                color: #495057;
                text-transform: uppercase;
                font-size: 11px;
            }
            
            QTableWidget::item {
                border-bottom: 1px solid #eee;
                padding: 10px;
                color: #333;
            }
            
            QTableWidget::item:selected {
                background-color: #e7f1ff;
                color: #007bff;
            }
        """)

    def display_users(self, users):
        """Route les données vers la page UserListPage"""
        # 1. On s'assure que la page est dans le cache
        if "users" not in self.pages_cache:
            from addons.Paramètres.views.user_list_view import UserListPage
            # Récupération sécurisée du contrôleur
            ctrl = self.controller.get('user') if isinstance(self.controller, dict) else self.controller
            
            self.pages_cache["users"] = UserListPage(ctrl, self.user)
            self.container.addWidget(self.pages_cache["users"])

        # 2. On récupère l'instance de la page
        user_page = self.pages_cache["users"]
        
        # 3. On lui donne les utilisateurs pour qu'elle remplisse SON tableau
        if hasattr(user_page, 'display_users'):
            user_page.display_users(users)
        else:
            print("Erreur: La méthode display_users est manquante dans UserListPage")

    def set_role_badge(self, row, role):
        # 1. Création d'un conteneur pour centrer le badge
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0) # Supprime les marges du conteneur
        layout.setAlignment(Qt.AlignCenter)   # Centre le badge dans la cellule

        # 2. Création du badge (Label)
        label = QLabel(role.upper())
        
        # Couleurs selon le rôle
        color = "#e67e22" if role.lower() == "admin" else "#3498db"
        
        label.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                border-radius: 12px;
                padding: 5px 15px;
                font-size: 11px;
                font-weight: bold;
                min-width: 80px;
            }}
        """)
        label.setAlignment(Qt.AlignCenter)

        # 3. Assemblage
        layout.addWidget(label)
        self.table.setCellWidget(row, 2, container)

    def set_action_buttons(self, row, user):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Création des boutons avec des couleurs distinctes
        btns = {
            "view": ("👁️", "#3498db"),
            "edit": ("✏️", "#f1c40f"),
            "delete": ("🗑️", "#e74c3c")
        }

        for key, (icon, color) in btns.items():
            btn = QPushButton(icon)
            btn.setFixedSize(32, 32)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: white;
                    border: 1px solid {color};
                    border-radius: 16px;
                    color: {color};
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {color};
                    color: white;
                }}
            """)
            layout.addWidget(btn)
            
            # Connexion (exemple pour delete)
            if key == "delete":
                btn.clicked.connect(lambda chk=False, u=user: self.on_delete(u))
            elif key == "edit":
                btn.clicked.connect(lambda chk=False, u=user: self.on_edit(u))

        container.setLayout(layout)
        self.table.setCellWidget(row, 3, container)

    def on_view(self, user):
        print(f"Visualisation de : {user.username}")

    def on_add_clicked(self):
        # 1. Utilisation du nouveau formulaire spécifique (CustomUserForm)
        # Assure-toi de l'importer en haut : from .dialog_form import CustomUserForm
        dialog = CustomUserForm(self)
        
        if dialog.exec() == QDialog.Accepted:
            # 2. Récupérer les données saisies (incluant l'email désormais)
            new_user_data = dialog.get_data()
            
            # 3. Validation côté client (Check Email pour éviter l'erreur NOT NULL)
            if not new_user_data['username'] or not new_user_data['email'] or not new_user_data['password']:
                QMessageBox.warning(
                    self, 
                    "Champs manquants", 
                    "Le nom d'utilisateur, l'email et le mot de passe sont obligatoires."
                )
                # On ré-ouvre le dialogue si on veut forcer la saisie sans perdre ce qui est écrit
                # Sinon on s'arrête là.
                return

            # 4. Envoyer au contrôleur pour l'insertion en DB
            # Le contrôleur recevra maintenant data['email']
            success, message = self.controller.create_user(new_user_data)
            
            if success:
                # 5. Succès : Rafraîchir la liste et notifier l'utilisateur
                users = self.controller.get_all_users()
                self.display_users(users)
                
                # Optionnel : Une petite notification de succès
                QMessageBox.information(self, "Succès", "L'utilisateur a été créé avec succès.")
            else:
                # 6. Échec : Afficher l'erreur retournée par Postgres/SQLAlchemy
                QMessageBox.critical(self, "Erreur lors de la création", message)
                
    def on_edit(self, user):
        # 1. Ouvrir le dialogue avec les données actuelles
        # On peut réutiliser CustomUserForm en lui passant les infos
        dialog = CustomUserForm(self)
        
        # Pré-remplir le formulaire avec les infos de 'user'
        dialog.username_input.setText(user.username)
        dialog.email_input.setText(user.email)
        dialog.role_combo.setCurrentText(user.role)
        dialog.btn_save.setText("METTRE À JOUR") # Changer le texte du bouton

        if dialog.exec() == QDialog.Accepted:
            new_data = dialog.get_data()
            
            # 2. Appeler le contrôleur avec l'ID de l'utilisateur
            success, message = self.controller.update_user(user.id, new_data)
            
            if success:
                # 3. TRÈS IMPORTANT : Rafraîchir le tableau
                self.display_users(self.controller.get_all_users())
                QMessageBox.information(self, "Succès", message)
            else:
                QMessageBox.critical(self, "Erreur", message)

    def on_delete(self, user):
        # 1. Demander confirmation (Sécurité)
        confirm = QMessageBox.question(
            self, 
            "Confirmation de suppression",
            f"Êtes-vous sûr de vouloir supprimer l'utilisateur {user.username} ?\nCette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            # 2. Appeler le contrôleur avec l'ID
            success, message = self.controller.delete_user(user.id)
            
            if success:
                # 3. RAFRAÎCHIR le tableau immédiatement
                users = self.controller.get_all_users()
                self.display_users(users)
                QMessageBox.information(self, "Supprimé", message)
            else:
                QMessageBox.critical(self, "Erreur", message)

    def on_view_audit_logs(self):
        # 1. Récupérer les logs depuis le contrôleur
        logs = self.controller.get_audit_logs()
        
        # 2. Création de la fenêtre de log
        dialog = QDialog(self)
        dialog.setWindowTitle("Traçabilité du Système - Audit Sécurité")
        dialog.setMinimumSize(850, 500)
        layout = QVBoxLayout(dialog)

        # AJOUT DU BOUTON EXPORT
        btn_layout = QHBoxLayout()
        btn_export = QPushButton("📤 Exporter en CSV")
        btn_export.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")

        def handle_export():
            success, path = AuditReporter.export_to_csv(logs)
            if success:
                QMessageBox.information(dialog, "Export Réussi", f"Le journal a été enregistré ici :\n{path}")
            else:
                QMessageBox.critical(dialog, "Erreur", f"Échec de l'exportation : {path}")

        btn_export.clicked.connect(handle_export)
        
        # 3. Configuration du tableau
        log_table = QTableWidget()
        log_table.setColumnCount(5)
        log_table.setHorizontalHeaderLabels([
            "Date & Heure", 
            "Utilisateur ID", 
            "Action", 
            "Détails de l'opération", 
            "Adresse IP" 
        ])
        
        # Design du tableau
        log_table.setAlternatingRowColors(True)
        log_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch) # Détails prend la place
        
        log_table.setRowCount(len(logs))
        for i, log in enumerate(logs):
            # Formatage de la date (ex: 19/02/2026 14:30)
            date_str = log.created_at.strftime("%d/%m/%Y %H:%M:%S")
            
            log_table.setItem(i, 0, QTableWidgetItem(date_str))
            log_table.setItem(i, 1, QTableWidgetItem(str(log.user_id)))
            
            # Action en couleur pour lisibilité
            action_item = QTableWidgetItem(log.action)
            if "SUPPRESSION" in log.action:
                action_item.setForeground(QColor("#d63031"))
            log_table.setItem(i, 2, action_item)
            
            log_table.setItem(i, 3, QTableWidgetItem(log.details))
            
            # Adresse IP
            ip_item = QTableWidgetItem(log.ip_address if log.ip_address else "127.0.0.1")
            ip_item.setTextAlignment(Qt.AlignCenter)
            log_table.setItem(i, 4, ip_item)
        
        layout.addWidget(log_table)
        
        # Bouton de fermeture
        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close)
        btn_layout.addWidget(btn_export)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)
        
        dialog.exec()

    def switch_page(self, index):
        """Crée la page dynamiquement si elle n'existe pas encore"""
        text = self.sidebar.item(index).text()
        page_func = self.menu_map[text]

        # On vérifie si on a déjà créé cette page pour ne pas la recréer
        existing_page = None
        for i in range(self.container.count()):
            if self.container.widget(i).objectName() == text:
                existing_page = self.container.widget(i)
                break

        if not existing_page:
            new_page = page_func()
            new_page.setObjectName(text)
            self.container.addWidget(new_page)
            self.container.setCurrentWidget(new_page)
        else:
            self.container.setCurrentWidget(existing_page)