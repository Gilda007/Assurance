# # addons/user_manager/main_ui.py
# from core.base_module import BaseModule
# from PySide6.QtWidgets import QPushButton
# from PySide6.QtCore import Qt
# from addons.Paramètres.views.views import ParametreMainView
# from addons.Paramètres.controllers.controller import UserController
# import traceback
# from core.alerts import AlertManager

# # addons/user_manager/main_ui.py

# class UserModule(BaseModule):
#     def setup(self):
#         db_session = getattr(self.main_window, 'db_session', None)
#         self.controller = UserController(db_session)
#         # On ne crée pas la vue tout de suite pour économiser de la RAM
#         self.btn = QPushButton("👥 Paramètres")
#         self.btn.setFixedHeight(45)
#         self.btn.setCursor(Qt.PointingHandCursor)
#         self.btn.clicked.connect(lambda: self.activate_module())
#         self.main_window.sidebar_layout.addWidget(self.btn)
        
#         # On initialise le contrôleur ici si besoin
#         current_user = getattr(self.main_window, 'current_user', None)
#         user_id = current_user.id if current_user else 2 

#         # 3. INITIALISATION CORRECTE
#         # On passe la session et l'ID au contrôleur
#         self.controller = UserController(db_session, current_user_id=user_id)
#     # addons/user_manager/main_ui.py

#     def activate_user_manager(self):
#         # On récupère l'utilisateur stocké lors du login
#         user = getattr(self.main_window, 'current_user', None)
        
#         if user:
#             # On crée le contrôleur avec le VRAI ID
#             self.controller = UserController(self.db_session, current_user_id=user.id)
#             self.view = ParametreMainView(controller=self.controller)
#         else:
#             AlertManager.show_error(self, "Erreur", "Aucune session active détectée.")

#     def activate_module(self):
#         print("DEBUG: Clic sur Gestion Utilisateurs")
        
#         # 1. Récupération de la session et de l'utilisateur de la MainWindow
#         db_conn = getattr(self.main_window, 'db_session', None)
#         current_user = getattr(self.main_window, 'current_user', None)

#         # 2. Vérification stricte de la session
#         if current_user is None:
#             print("ERREUR SÉCURITÉ : Aucun utilisateur connecté.")
#             return # On arrête tout ici pour la sécurité

#         user_id = current_user.id

#         # 3. Initialisation du contrôleur avec le VRAI ID
#         self.controller = UserController(db_conn, current_user_id=user_id)

#         # 4. Création de la vue avec le contrôleur injecté
#         self.view = ParametreMainView(controller=self.controller, user=current_user)
        
#         # 5. Chargement des données et affichage
#         users = self.controller.get_all_users()
#         self.view.display_users(users)
#         self.main_window.set_content_widget(self.view)

from core.base_module import BaseModule
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from addons.Paramètres.views.views import ParametreMainView
from addons.Paramètres.controllers.controller import UserController
from core.alerts import AlertManager


# Style moderne pour le bouton de la barre latérale
MODERN_BTN_STYLE = """
QPushButton {
    background-color: transparent;
    color: #546e7a;
    border: none;
    border-radius: 8px;
    text-align: left;
    padding-left: 15px;
    font-size: 14px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #f1f3f4;
    color: #1a73e8;
}
QPushButton:checked {
    background-color: #e8f0fe;
    color: #1a73e8;
    border-right: 3px solid #1a73e8;
}
"""


class UserModule(BaseModule):
    def setup(self):
        """Initialisation silencieuse du module"""
        # 1. Récupération sécurisée de la session
        self.db_session = getattr(self.main_window, 'db_session', None)
        self.current_user = getattr(self.main_window, 'current_user', None)
        
        # 2. Création du bouton avec un style Premium
        self.btn = QPushButton("  Gestion Utilisateurs")
        self.btn.setCheckable(True) # Pour l'état "actif"
        self.btn.setFixedHeight(50)
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.setStyleSheet(MODERN_BTN_STYLE)
        
        # Optionnel: Ajoute une icône SVG pour le professionnalisme
        # self.btn.setIcon(QIcon("assets/icons/users.svg"))
        # self.btn.setIconSize(QSize(20, 20))

        # 3. Connexion de l'événement
        self.btn.clicked.connect(self.activate_module)
        
        # 4. Ajout au menu latéral
        if hasattr(self.main_window, 'sidebar_layout'):
            self.main_window.sidebar_layout.addWidget(self.btn)

    def activate_module(self):
        """Logique d'activation avec récupération dynamique de l'utilisateur"""
        try:
            # RECHERCHE DYNAMIQUE : On va chercher l'info fraîche dans la fenêtre principale
            user = getattr(self.main_window, 'current_user', None)
            db_session = getattr(self.main_window, 'db_session', None)

            if not user:
                # Si vraiment pas d'utilisateur, on affiche l'erreur
                AlertManager.show_error(self.main_window, "Sécurité", "Aucun utilisateur connecté détecté.")
                return

            # Mise à jour de la référence locale
            self.current_user = user
            self.db_session = db_session

            # Suite du code de chargement...
            self.btn.setChecked(True)
            self.controller = UserController(self.db_session, current_user_id=self.current_user.id)
            self.view = ParametreMainView(controller=self.controller, user=self.current_user)
            
            users = self.controller.get_all_users()
            self.view.display_users(users)
            self.main_window.set_content_widget(self.view)

        except Exception as e:
            AlertManager.show_error(self.main_window, "Erreur", str(e))