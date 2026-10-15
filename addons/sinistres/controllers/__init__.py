"""Contrôleurs du module Sinistres."""

from addons.sinistres.controllers.sinistre_controller import SinistreController
from addons.sinistres.controllers.referentiel_controller import ReferentielController
from addons.sinistres.controllers.expertise_controller import ExpertiseController
from addons.sinistres.controllers.evaluation_controller import EvaluationController
from addons.sinistres.controllers.reglement_controller import ReglementController
from addons.sinistres.controllers.recours_controller import RecoursController
from addons.sinistres.controllers.automobile_controller import AutomobileController

__all__ = [
    "SinistreController",
    "ReferentielController",
    "ExpertiseController",
    "EvaluationController",
    "ReglementController",
    "RecoursController",
    "AutomobileController"
]


class SinistresMainController:
    """Point d'entrée centralisé pour les sous-contrôleurs du module sinistres."""

    def __init__(self, session=None, current_user_id=None):
        self.session = session
        self.user_id = current_user_id

        self.sinistre = SinistreController()
        self.referentiel = ReferentielController()
        self.expertise = ExpertiseController()
        self.evaluation = EvaluationController()
        self.reglement = ReglementController()
        self.recours = RecoursController()
        self.automobile = AutomobileController()

    def is_available(self):
        """Vérifie simplement que le contrôleur principal est initialisé."""
        return True