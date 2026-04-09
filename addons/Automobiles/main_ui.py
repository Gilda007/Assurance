# addons/Automobile/main_ui.py
"""
Module Automobile - Point d'entrée de l'extension
Gère l'intégration dans la barre latérale et l'activation de l'interface
"""

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt

from core.base_module import BaseModule
from core.alerts import AlertManager

from addons.Automobiles.views.view import VehicleMainView
from addons.Automobiles.controllers import AutomobileMainController


class AutomobileModule(BaseModule):
    """
    Module principal de gestion automobile
    S'intègre dans l'application principale via la barre latérale
    """
    
    # Constantes pour le style
    BUTTON_HEIGHT = 45
    BUTTON_STYLE = """
        QPushButton {
            background-color: transparent;
            color: #f8fafc;
            text-align: left;
            padding-left: 20px;
            border: none;
            border-radius: 8px;
            margin: 2px 10px;
            font-size: 13px;
            font-weight: 500;
        }
        QPushButton:hover {
            background-color: #334155;
        }
        QPushButton:pressed {
            background-color: #1e293b;
        }
    """
    
    def __init__(self, main_window):
        """Initialise le module avec la fenêtre principale"""
        super().__init__(main_window)
        self._view = None
        self._controller = None
        self._button = None
    
    def setup(self):
        """Configure le module dans l'interface principale"""
        self._create_navigation_button()
        self._add_to_sidebar()
    
    def _create_navigation_button(self):
        """Crée et configure le bouton de navigation du module"""
        self._button = QPushButton("🚗  Automobile")
        self._button.setFixedHeight(self.BUTTON_HEIGHT)
        self._button.setCursor(Qt.PointingHandCursor)
        self._button.setStyleSheet(self.BUTTON_STYLE)
        self._button.clicked.connect(self.activate_module)
    
    def _add_to_sidebar(self):
        """Ajoute le bouton à la barre latérale si elle existe"""
        if hasattr(self.main_window, 'sidebar_layout'):
            self.main_window.sidebar_layout.addWidget(self._button)
        else:
            sidebar = getattr(self.main_window, 'sidebar', None)
            if sidebar and hasattr(sidebar, 'layout'):
                sidebar.layout().addWidget(self._button)
    
    def activate_module(self):
        """Active l'interface du module dans la zone de contenu principale"""
        # 1. Vérification de l'authentification
        current_user = self._get_current_user()
        if not current_user:
            AlertManager.show_error(
                self.main_window,
                "Accès Refusé",
                "Veuillez vous connecter pour accéder au parc automobile."
            )
            return
        
        # 2. Récupération de la zone de contenu
        content_stack = self._get_content_area()
        if not content_stack:
            self._log_error("Zone de contenu introuvable dans MainWindow")
            return
        
        # 3. Initialisation des composants si nécessaire
        if not self._view:
            self._initialize_module_components(current_user)
            content_stack.addWidget(self._view)
        
        # 4. Affichage de la vue
        content_stack.setCurrentWidget(self._view)
    
    def _get_current_user(self):
        """Récupère l'utilisateur courant depuis la fenêtre principale"""
        return getattr(self.main_window, 'current_user', None)
    
    def _get_content_area(self):
        """Récupère la zone de contenu (stacked widget) depuis la fenêtre principale"""
        content_area = getattr(self.main_window, 'content_area', None)
        if content_area:
            return content_area
        
        alternatives = ['stacked_widget', 'main_stack', 'content_stack']
        for attr in alternatives:
            if hasattr(self.main_window, attr):
                return getattr(self.main_window, attr)
        
        return None
    
    def _initialize_module_components(self, current_user):
        """
        Initialise le contrôleur et la vue du module
        
        Args:
            current_user: L'utilisateur courant (objet ou ID)
        """
        # Récupération de l'ID utilisateur
        user_id = self._extract_user_id(current_user)
        
        # === CORRECTION DÉFINITIVE ===
        # Le constructeur attend: session et current_user_id
        self._controller = AutomobileMainController(
            session=self.db_session,
            current_user_id=user_id
        )
        # ==============================
        
        # Création de la vue (interface utilisateur)
        self._view = VehicleMainView(
            controller=self._controller,
            user=current_user
        )
    
    def _extract_user_id(self, user):
        """Extrait l'ID d'un utilisateur (objet ou valeur directe)"""
        if hasattr(user, 'id'):
            return user.id
        return user
    
    def _log_error(self, message):
        """Log une erreur de manière élégante"""
        print(f"[AutomobileModule] {message}")
    
    @property
    def view(self):
        """Retourne la vue du module"""
        return self._view
    
    @property
    def controller(self):
        """Retourne le contrôleur du module"""
        return self._controller
    
    @property
    def db_session(self):
        """Retourne la session de base de données depuis la fenêtre principale"""
        return getattr(self.main_window, 'db_session', None)
    
    def cleanup(self):
        """Nettoie les ressources du module"""
        if self._controller and hasattr(self._controller, 'cleanup'):
            self._controller.cleanup()
        
        if self._view:
            self._view.deleteLater()
            self._view = None
        
        self._controller = None