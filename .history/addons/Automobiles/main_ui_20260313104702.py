# addons/Automobile/main_ui.py
from core.base_module import BaseModule
from PySide6.QtWidgets import QPushButton, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from core.alerts import AlertManager


# Importez vos futures vues et contrôleurs ici
# from addons.Automobile.views.vehicle_view import VehicleMainView
# from addons.Automobile.controllers.vehicle_controller import VehicleController

    # addons/Automobile/main_ui.py
from core.base_module import BaseModule
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt
from core.alerts import AlertManager

# Imports centralisés depuis les répertoires du module
# from addons.Automobiles.views import VehicleMainView
# from addons.Automobiles.controllers import VehicleController

from addons.Automobiles.controllers import AutomobileMainController

class AutomobileModule(BaseModule):
    def setup(self):
        """Initialisation du bouton dans la barre latérale principale"""
        # Récupération des ressources partagées depuis la fenêtre principale
        self.db_session = getattr(self.main_window, 'db_session', None)
        
        # Création du bouton d'accès au module
        self.btn = QPushButton("🚗 Automobile")
        self.btn.setFixedHeight(45)
        self.btn.setCursor(Qt.PointingHandCursor)
        
        self.btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #f8fafc;
                text-align: left;
                padding-left: 20px;
                border: none;
                border-radius: 8px;
                margin: 2px 10px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #334155;
            }
        """)

        self.btn.clicked.connect(self.activate_module)
        
        if hasattr(self.main_window, 'sidebar_layout'):
            self.main_window.sidebar_layout.addWidget(self.btn)

    def activate_module(self):
        """Logique d'affichage de l'interface dans la zone de contenu"""
        current_user = getattr(self.main_window, 'current_user', None)
        
        if not current_user:
            AlertManager.show_error(self.main_window, "Accès Refusé", 
                                "Veuillez vous connecter pour accéder au parc automobile.")
            return

        # Utilisation de 'content_area' comme identifié précédemment
        stack = getattr(self.main_window, 'content_area', None)

        if stack is None:
            print("ERREUR : 'content_area' est introuvable dans MainWindow")
            return

        if not hasattr(self, 'view'):
            # Création de la vue avec injection des dépendances
            self.view = self.create_module_view() 
            stack.addWidget(self.view)

        stack.setCurrentWidget(self.view)

    def create_module_view(self):
        """Initialise le contrôleur et la vue principale"""
        # On initialise le contrôleur avec la session de base de données
        self.controller = VehicleController(self.db_session)
        
        # On récupère l'utilisateur actuel
        current_user = getattr(self.main_window, 'current_user', None)
        
        # On injecte le contrôleur et l'utilisateur dans la vue principale.
        # Cette vue se chargera ensuite de les passer aux 10 sous-fichiers.
        return VehicleMainView(self.controller, current_user)