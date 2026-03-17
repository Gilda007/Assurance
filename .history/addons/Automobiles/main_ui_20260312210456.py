# addons/Automobile/main_ui.py
from core.base_module import BaseModule
from PySide6.QtWidgets import QPushButton, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from core.alerts import AlertManager
from addons.Automobiles.views import *
from addons.Automobiles.controllers import *
from addons.Automobiles

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
        """Logique exécutée lors du clic sur le bouton Automobile"""
        print(f"DEBUG: Activation du module Automobile par {getattr(self.current_user, 'username', 'Inconnu')}")

        # Sécurité : Vérifier si l'utilisateur est connecté
        if not self.current_user:
            AlertManager.show_error(self.main_window, "Accès Refusé", "Veuillez vous connecter pour accéder au parc automobile.")
            return

        # Initialisation de la vue (si elle n'existe pas encore)
        if not hasattr(self, 'view'):
            self.view = self.create_module_view()
            # On ajoute la vue au QStackedWidget principal de la MainWindow
            self.main_window.container.addWidget(self.view)

        # Affichage de la vue
        self.main_window.container.setCurrentWidget(self.view)

    def create_module_view(self):
        """Crée l'interface principale du module Automobile"""
        # Pour l'instant, on crée une page temporaire
        # Plus tard, vous remplacerez ceci par : return VehicleMainView(self.controller, self.current_user)
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("Gestion du Parc Automobile")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #1e293b;")
        title.setAlignment(Qt.AlignCenter)
        
        desc = QLabel("Ici s'affichera la liste de vos véhicules, expertises et sinistres.")
        desc.setStyleSheet("color: #64748b; font-size: 16px;")
        desc.setAlignment(Qt.AlignCenter)
        
        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addStretch()
        
        return page