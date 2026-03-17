from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLabel, QPushButton, QFrame, QMessageBox, QDialog)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QIcon, QFont
from addons.Paramètres.views.dialog_form import UserDialog
from addons.Paramètres.views.user_from import CustomUserForm
from addons.user_manager.reports.audit_exporter import AuditReporter


class UserListView(QWidget):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        print(f"DEBUG: Contrôleur reçu par la vue : {self.controller}")
        self.setObjectName("UserListView")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # --- EN-TÊTE DE PAGE ---
        self.header_container = QWidget()
        header_layout = QHBoxLayout(self.header_container)
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        self.title_label = QLabel("Gestion des Utilisateurs")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        
        self.btn_add = QPushButton(" + Ajouter un utilisateur")
        self.btn_add.setFixedSize(200, 40)
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #27ae60; }
        """)

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_add)
        self.btn_add.clicked.connect(self.on_add_clicked)
        self.main_layout.addWidget(self.header_container)

        # --- TABLEAU STYLISÉ ---
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "UTILISATEUR", "RÔLE", "ACTIONS"])
        
        # Comportement du header
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # ID petit
        header.setSectionResizeMode(3, QHeaderView.Fixed) # Actions taille fixe
        self.table.setColumnWidth(3, 150)
        
        # Design général du tableau
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setFocusPolicy(Qt.NoFocus) # Enlever le contour pointillé au clic
        
        self.apply_styles()
        self.main_layout.addWidget(self.table)

        self.btn_audit = QPushButton("📜 Journal d'Audit")
        self.btn_audit.setStyleSheet("""
            QPushButton {
                background-color: #636e72;
                color: white;
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2d3436; }
        """)
        header_layout.addWidget(self.btn_audit)
        self.btn_audit.clicked.connect(self.on_view_audit_logs)
        # Vérification explicite
        role = self.controller.current_user_role
        print(f"DEBUG: Rôle détecté pour l'UI : {role}") # Pour vérifier dans ta console
        if role != "admin":
            self.btn_audit.setEnabled(False)
            self.btn_audit.setVisible(False) # C'est encore plus sûr de le cacher carrément
            self.btn_audit.setToolTip("Accès réservé aux administrateurs")
        
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
        self.table.setRowCount(0)
        for user in users:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 60) # Des lignes plus hautes pour respirer

            # ID (Centré)
            item_id = QTableWidgetItem(str(getattr(user, 'id', '')))
            item_id.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, item_id)

            # Nom d'utilisateur (En gras)
            item_name = QTableWidgetItem(getattr(user, 'username', ''))
            item_name.setFont("font-weight: bold;")
            self.table.setItem(row, 1, item_name)

            font = QFont()
            font.setBold(True)
            item_name.setFont(font)
            self.table.setItem(row, 1, item_name)
            # Badge pour le Rôle
            role_value = getattr(user, 'role', 'agent')
            self.set_role_badge(row, role_value)

            # Actions
            self.set_action_buttons(row, user)

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

    def display_page(self, row):
        key = self.sidebar.item(row).data(Qt.UserRole)
        
        if key not in self.pages_cache:
            if key == "users":
                from .user_list_view import UserListPage
                self.pages_cache[key] = UserListPage(self.controllers.get('user'), self.user)
            elif key == "modules":
                self.pages_cache[key] = ParametreModuleWidget(self.controllers.get('module'), self.user)
            
            self.container.addWidget(self.pages_cache[key])
            
        self.container.setCurrentWidget(self.pages_cache[key])