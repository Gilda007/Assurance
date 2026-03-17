# addons/Automobile/main_ui.py
from core.base_module import BaseModule
from PySide6.QtWidgets import QPushButton, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from core.alerts import AlertManager


# Importez vos futures vues et contrôleurs ici
# from addons.Automobile.views.vehicle_view import VehicleMainView
# from addons.Automobile.controllers.vehicle_controller import VehicleController

class AutomobileModule(BaseModule):
    def setup(self):
        """Initialisation du bouton dans la barre latérale principale"""
        # 1. Récupération des ressources partagées
        self.db_session = getattr(self.main_window, 'db_session', None)
        self.current_user = getattr(self.main_window, 'current_user', None)

        # 2. Création du bouton d'accès au module
        self.btn = QPushButton("🚗 Automobile")
        self.btn.setFixedHeight(45)
        self.btn.setCursor(Qt.PointingHandCursor)
        
        # Style moderne cohérent avec le reste de l'UI
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

        # 3. Connexion au clic
        self.btn.clicked.connect(self.activate_module)
        
        # 4. Ajout au layout de la sidebar principale
        if hasattr(self.main_window, 'sidebar_layout'):
            self.main_window.sidebar_layout.addWidget(self.btn)

    def activate_module(self):
        current_user = getattr(self.main_window, 'current_user', None)
        
        # UTILISATION DU BON NOM : content_area
        stack = getattr(self.main_window, 'content_area', None)

        if not stack:
            print("ERREUR : 'content_area' est introuvable dans MainWindow")
            return

        if not hasattr(self, 'view'):
            self.view = self.create_module_view() 
            stack.addWidget(self.view)

        stack.setCurrentWidget(self.view)

    def create_module_view(self):
        """Crée l'interface et injecte les dépendances"""
        # On crée le contrôleur
        self.controller = VehicleController(self.db_session)
        
        # On passe le contrôleur et l'utilisateur à la vue principale
        # La vue principale se chargera de les passer aux 10 autres fichiers
        return VehicleMainView(self.controller, getattr(self.main_window, 'current_user', None))
    # VehicleMainView(controller=main_controller, user=self.current_user)