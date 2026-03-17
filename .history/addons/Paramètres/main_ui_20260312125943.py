
# addons/user_manager/main_ui.py
from core.base_module import BaseModule
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt
from addons.Paramètres.views.views import UserListView
from addons.Pa.controllers.controller import UserController
import traceback
from core.alerts import AlertManager

# addons/user_manager/main_ui.py

class UserModule(BaseModule):
    def setup(self):
        db_session = getattr(self.main_window, 'db_session', None)
        self.controller = UserController(db_session)
        # On ne crée pas la vue tout de suite pour économiser de la RAM
        self.btn = QPushButton("👥 Gestion Utilisateurs")
        self.btn.setFixedHeight(45)
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.clicked.connect(lambda: self.activate_module())
        self.main_window.sidebar_layout.addWidget(self.btn)
        
        # On initialise le contrôleur ici si besoin
        current_user = getattr(self.main_window, 'current_user', None)
        user_id = current_user.id if current_user else 2 

        # 3. INITIALISATION CORRECTE
        # On passe la session et l'ID au contrôleur
        self.controller = UserController(db_session, current_user_id=user_id)
# addons/user_manager/main_ui.py

    def activate_user_manager(self):
        # On récupère l'utilisateur stocké lors du login
        user = getattr(self.main_window, 'current_user', None)
        
        if user:
            # On crée le contrôleur avec le VRAI ID
            self.controller = UserController(self.db_session, current_user_id=user.id)
            self.view = UserListView(controller=self.controller)
        else:
            AlertManager.show_error(self, "Erreur", "Aucune session active détectée.")

    def activate_module(self):
        print("DEBUG: Clic sur Gestion Utilisateurs")
        
        # 1. Récupération de la session et de l'utilisateur de la MainWindow
        db_conn = getattr(self.main_window, 'db_session', None)
        current_user = getattr(self.main_window, 'current_user', None)

        # 2. Vérification stricte de la session
        if current_user is None:
            print("ERREUR SÉCURITÉ : Aucun utilisateur connecté.")
            return # On arrête tout ici pour la sécurité

        user_id = current_user.id
        print(f"DEBUG : Module activé par {current_user.username} (ID: {user_id})")

        # 3. Initialisation du contrôleur avec le VRAI ID
        self.controller = UserController(db_conn, current_user_id=user_id)

        # 4. Création de la vue avec le contrôleur injecté
        self.view = UserListView(controller=self.controller)
        
        # 5. Chargement des données et affichage
        users = self.controller.get_all_users()
        self.view.display_users(users)
        self.main_window.set_content_widget(self.view)