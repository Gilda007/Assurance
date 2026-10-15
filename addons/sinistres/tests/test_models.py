"""
Tests des modèles SQLAlchemy
"""
import pytest
from datetime import datetime


class TestModelFields:
    """Vérifie les champs des modèles"""
    
    def test_sinistre_has_fields(self):
        from addons.sinistres.models import LometaSinistre
        
        champs = ['id', 'numero_sinistre', 'date_survenance', 'date_declaration',
                  'branche', 'categorie', 'statut', 'compagnie_id']
        for c in champs:
            assert hasattr(LometaSinistre, c), f"Champ {c} manquant"
    
    def test_evaluation_has_new_fields(self):
        """Évaluation doit avoir dommage_id et statut (après migration)"""
        from addons.sinistres.models import LometaEvaluation
        
        assert hasattr(LometaEvaluation, 'dommage_id'), "dommage_id manquant"
        assert hasattr(LometaEvaluation, 'statut'), "statut manquant"
    
    def test_recours_has_fk(self):
        """Recours doit avoir les nouvelles FK"""
        from addons.sinistres.models import LometaRecours
        
        champs = ['reglement_id', 'evaluation_id', 'debiteur_type',
                  'debiteur_tiers_id', 'debiteur_compagnie_id']
        for c in champs:
            assert hasattr(LometaRecours, c), f"Champ {c} manquant"
    
    def test_reglement_has_evaluation_id(self):
        """Règlement doit avoir evaluation_id"""
        from addons.sinistres.models import LometaReglement
        
        assert hasattr(LometaReglement, 'evaluation_id')
        assert hasattr(LometaReglement, 'lot_paiement_id')
        assert hasattr(LometaReglement, 'note_credit_id')


class TestModelRelations:
    """Vérifie les relations entre modèles"""
    
    def test_sinistre_relations(self):
        from addons.sinistres.models import LometaSinistre
        
        assert hasattr(LometaSinistre, 'dommages')
        assert hasattr(LometaSinistre, 'tiers')
        assert hasattr(LometaSinistre, 'expertises')
        assert hasattr(LometaSinistre, 'evaluations')
        assert hasattr(LometaSinistre, 'reglements')
        assert hasattr(LometaSinistre, 'recours')
    
    def test_recours_has_debiteur_property(self):
        """Recours a la propriété debiteur_id"""
        from addons.sinistres.models import LometaRecours
        
        assert isinstance(LometaRecours.debiteur_id, property)