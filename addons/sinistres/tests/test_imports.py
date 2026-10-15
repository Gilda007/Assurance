"""
Tests d'import — vérifie que tous les modules se chargent
"""
import pytest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestImportsModels:
    """Vérifie l'import des modèles"""
    
    def test_import_models_package(self):
        """Le package models est importable"""
        import addons.sinistres.models as m
        assert m is not None
    
    def test_import_all_models(self):
        """Tous les modèles listés dans __all__ sont importables"""
        from addons.sinistres import models
        
        attendus = [
            'LometaSinistre', 'LometaDommage', 'LometaTiers',
            'LometaExpertise', 'LometaEvaluation', 'LometaProvision',
            'LometaReglement', 'LometaRecours', 'LometaBanque',
            'LometaDocument', 'LometaTache', 'LometaNotification',
            'LometaWorkflow', 'LometaAvocat',
        ]
        
        for nom in attendus:
            assert hasattr(models, nom), f"Modèle {nom} non trouvé dans models"


class TestImportsServices:
    """Vérifie l'import des services"""
    
    def test_import_services_package(self):
        import addons.sinistres.services as s
        assert s is not None
    
    def test_import_all_services(self):
        from addons.sinistres.services.sinistre_service import SinistreService
        from addons.sinistres.services.expertise_service import ExpertiseService
        from addons.sinistres.services.evaluation_service import EvaluationService
        from addons.sinistres.services.reglement_service import ReglementService
        from addons.sinistres.services.recours_service import RecoursService
        from addons.sinistres.services.referentiel_service import ReferentielService
        
        assert SinistreService is not None
        assert ExpertiseService is not None
        assert EvaluationService is not None
        assert ReglementService is not None
        assert RecoursService is not None
        assert ReferentielService is not None


class TestImportsControllers:
    """Vérifie l'import des contrôleurs"""
    
    def test_import_all_controllers(self):
        from addons.sinistres.controllers.sinistre_controller import SinistreController
        from addons.sinistres.controllers.expertise_controller import ExpertiseController
        from addons.sinistres.controllers.evaluation_controller import EvaluationController
        from addons.sinistres.controllers.reglement_controller import ReglementController
        from addons.sinistres.controllers.recours_controller import RecoursController
        
        assert SinistreController is not None