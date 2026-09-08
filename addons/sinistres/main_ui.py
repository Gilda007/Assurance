"""
Module LOMETA Sinistres - Point d'entrée principal
Adapté pour utiliser les contrôleurs LOMETA
"""
from core.base_module import BaseModule
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QMessageBox
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from core.alerts import AlertManager

from addons.sinistres.views.view import LometaSinistresMainView
from addons.sinistres.controllers.sinistre_controller import SinistreController
from addons.sinistres.controllers.referentiel_controller import ReferentielController
from addons.sinistres.controllers.expertise_controller import ExpertiseController
from addons.sinistres.controllers.evaluation_controller import EvaluationController
from addons.sinistres.controllers.reglement_controller import ReglementController
from addons.sinistres.controllers.recours_controller import RecoursController


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


class LometaSinistresModule(BaseModule):
    """
    Module LOMETA de gestion des sinistres
    Couvre les Tomes 2 à 7 du CDC LOMETA
    """
    
    def __init__(self, main_window=None, controller=None):
        """Initialisation du module"""
        super().__init__(main_window)
        
        # ✅ Tous les contrôleurs
        self.sinistre_controller = SinistreController()
        self.referentiel_controller = ReferentielController()
        self.expertise_controller = ExpertiseController()
        self.evaluation_controller = EvaluationController()
        self.reglement_controller = ReglementController()
        self.recours_controller = RecoursController()
        
        # Références
        self.db_session = None
        self.current_user = None
        self.view = None
        self.btn = None
        
    def setup(self):
        """Initialisation silencieuse du module"""
        # 1. Récupération sécurisée de la session et de l'utilisateur
        self.db_session = getattr(self.main_window, 'db_session', None)
        self.current_user = getattr(self.main_window, 'current_user', None)
        
        # 2. Création du bouton avec un style Premium
        self.btn = QPushButton("  🏛️ LOMETA Sinistres")
        self.btn.setCheckable(True)
        self.btn.setFixedHeight(50)
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.setStyleSheet(MODERN_BTN_STYLE)
        
        # 3. Connexion de l'événement
        self.btn.clicked.connect(self.activate_module)
        
        # 4. Ajout au menu latéral
        if hasattr(self.main_window, 'sidebar_layout'):
            self.main_window.sidebar_layout.addWidget(self.btn)
        
        # 5. Initialiser les référentiels si nécessaire (en arrière-plan)
        self._init_referentiels()
    
    def _init_referentiels(self):
        """
        Vérifie et initialise les référentiels si nécessaire
        Cette méthode s'exécute silencieusement au démarrage
        """
        try:
            # Récupérer l'utilisateur
            user = getattr(self.main_window, 'current_user', None)
            if not user:
                return
            
            # Configurer le contrôleur
            self.referentiel_controller.set_current_user(user)
            
            # Vérifier si des référentiels existent déjà
            referentiels = self.referentiel_controller.get_referentiels_by_famille("sinistres_types")
            
            # Si aucun référentiel n'existe, initialiser les données
            if not referentiels:
                result = self.referentiel_controller.init_donnees_initiales()
                
                if result.get('crees', 0) > 0 or result.get('mis_a_jour', 0) > 0:
                    print(f"✅ LOMETA: Référentiels initialisés - {result['crees']} créés, {result['mis_a_jour']} mis à jour")
                
                if result.get('erreurs'):
                    print(f"⚠️ LOMETA: Erreurs lors de l'initialisation des référentiels: {result['erreurs']}")
                    
        except Exception as e:
            # Ne pas bloquer le chargement du module en cas d'erreur
            print(f"⚠️ LOMETA: Erreur lors de l'initialisation des référentiels: {e}")

    def activate_module(self):
        """
        Logique d'activation avec récupération dynamique de l'utilisateur
        """
        try:
            # RECHERCHE DYNAMIQUE : On va chercher l'info fraîche dans la fenêtre principale
            user = getattr(self.main_window, 'current_user', None)
            db_session = getattr(self.main_window, 'db_session', None)

            if not user:
                AlertManager.show_error(self.main_window, "Sécurité", "Aucun utilisateur connecté détecté.")
                return

            # Mise à jour des références locales
            self.current_user = user
            self.db_session = db_session
            
            # ✅ Configurer TOUS les contrôleurs avec l'utilisateur courant
            self.sinistre_controller.set_current_user(user)
            self.referentiel_controller.set_current_user(user)
            self.expertise_controller.set_current_user(user)
            self.evaluation_controller.set_current_user(user)
            self.reglement_controller.set_current_user(user)
            self.recours_controller.set_current_user(user)

            # ✅ Création de la vue avec TOUS les contrôleurs
            self.view = LometaSinistresMainView(
                sinistre_controller=self.sinistre_controller,
                referentiel_controller=self.referentiel_controller,
                expertise_controller=self.expertise_controller,
                evaluation_controller=self.evaluation_controller,
                reglement_controller=self.reglement_controller,
                recours_controller=self.recours_controller,
                user=self.current_user
            )
            
            # Affichage dans la fenêtre principale
            self.main_window.set_content_widget(self.view)
            
            # Mettre à jour l'état du bouton
            self.btn.setChecked(True)

        except Exception as e:
            AlertManager.show_error(self.main_window, "Erreur", f"Erreur lors de l'activation du module LOMETA: {str(e)}")