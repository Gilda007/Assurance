"""
Contrôleur des évaluations - Interface entre l'UI et EvaluationService
"""
from PySide6.QtCore import Signal
from typing import Optional, List, Dict, Any

from addons.sinistres.controllers.controleur_base import BaseController
from addons.sinistres.services.evaluation_service import EvaluationService


class EvaluationController(BaseController):
    """Contrôleur pour la gestion des évaluations"""
    
    # Signaux spécifiques
    evaluation_created = Signal(dict)
    evaluation_updated = Signal(dict)
    evaluation_validated = Signal(int)
    evaluation_revised = Signal(dict)
    evaluation_list_updated = Signal(list)
    
    def __init__(self):
        super().__init__()
        self.service = EvaluationService()
    
    # ============================================================
    # GESTION DES ÉVALUATIONS
    # ============================================================
    
    def creer_evaluation(self, data: Dict[str, Any]) -> Optional[dict]:
        """Crée une nouvelle évaluation"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return None
            
            data['created_by'] = self.get_current_user_id()
            evaluation = self.service.creer_evaluation(data)
            result = self._serialize_evaluation(evaluation)
            
            self.evaluation_created.emit(result)
            self.handle_success(f"Évaluation {evaluation.numero_evaluation} créée avec succès")
            return result
            
        except Exception as e:
            self.handle_error(e)
            return None
    
    def get_evaluation(self, evaluation_id: int) -> Optional[dict]:
        """Récupère une évaluation par son ID"""
        try:
            evaluation = self.service.get_evaluation(evaluation_id)
            if evaluation:
                return self._serialize_evaluation(evaluation)
            return None
        except Exception as e:
            self.handle_error(e)
            return None
    
    def get_evaluations_by_sinistre(self, sinistre_id: int) -> List[dict]:
        """Récupère toutes les évaluations d'un sinistre"""
        try:
            evaluations = self.service.get_evaluations_by_sinistre(sinistre_id)
            result = [self._serialize_evaluation(e) for e in evaluations]
            self.evaluation_list_updated.emit(result)
            return result
        except Exception as e:
            self.handle_error(e)
            return []
    
    def update_evaluation(self, evaluation_id: int, data: Dict[str, Any]) -> bool:
        """Met à jour une évaluation"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            data['updated_by'] = self.get_current_user_id()
            evaluation = self.service.update_evaluation(evaluation_id, data)
            
            if evaluation:
                self.evaluation_updated.emit(self._serialize_evaluation(evaluation))
                self.handle_success("Évaluation mise à jour")
                return True
            
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    def reviser_evaluation(self, evaluation_id: int, data: Dict[str, Any]) -> bool:
        """Révisé une évaluation avec historisation"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            # Ajouter le motif si non fourni
            if not data.get('motif'):
                data['motif'] = "Révision demandée"
            
            evaluation = self.service.reviser_evaluation(
                evaluation_id=evaluation_id,
                data=data,
                utilisateur_id=self.get_current_user_id()
            )
            
            if evaluation:
                self.evaluation_revised.emit(self._serialize_evaluation(evaluation))
                self.handle_success("Évaluation révisée avec succès")
                return True
            
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    def valider_evaluation(self, evaluation_id: int) -> bool:
        """Valide une évaluation"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            evaluation = self.service.valider_evaluation(
                evaluation_id=evaluation_id,
                utilisateur_id=self.get_current_user_id()
            )
            
            if evaluation:
                self.evaluation_validated.emit(evaluation_id)
                self.handle_success("Évaluation validée")
                return True
            
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    def get_revisions(self, evaluation_id: int) -> List[dict]:
        """Récupère toutes les révisions d'une évaluation"""
        try:
            revisions = self.service.get_revisions(evaluation_id)
            return [
                {
                    'id': r.id,
                    'ancien_montant_brut': r.ancien_montant_brut,
                    'ancien_montant_net': r.ancien_montant_net,
                    'nouveau_montant_brut': r.nouveau_montant_brut,
                    'nouveau_montant_net': r.nouveau_montant_net,
                    'motif': r.motif,
                    'date_revision': r.date_revision.isoformat() if r.date_revision else None,
                    'revise_par': r.revise_par
                }
                for r in revisions
            ]
        except Exception as e:
            self.handle_error(e)
            return []
    
    def calculer_montant_net(self, montant_brut: float, franchise: float, taux_responsabilite: float) -> float:
        """Calcule le montant net selon la formule standard"""
        return (montant_brut - franchise) * taux_responsabilite
    
    def get_statistiques(self, sinistre_id: int = None) -> Dict[str, Any]:
        """Récupère les statistiques des évaluations"""
        try:
            return self.service.get_statistiques(sinistre_id)
        except Exception as e:
            self.handle_error(e)
            return {}
    
    # ============================================================
    # MÉTHODE PRIVÉE
    # ============================================================
    
    def _serialize_evaluation(self, evaluation) -> dict:
        """Sérialise une évaluation en dictionnaire"""
        return {
            'id': evaluation.id,
            'numero_evaluation': evaluation.numero_evaluation,
            'sinistre_id': evaluation.sinistre_id,
            'type_evaluation': evaluation.type_evaluation,
            'categorie': evaluation.categorie,
            'montant_brut': evaluation.montant_brut,
            'franchise': evaluation.franchise,
            'taux_responsabilite': evaluation.taux_responsabilite,
            'montant_net': evaluation.montant_net,
            'details': evaluation.details,
            'est_validee': evaluation.est_validee,
            'validee_par': evaluation.validee_par,
            'date_validation': evaluation.date_validation.isoformat() if evaluation.date_validation else None,
            'date_evaluation': evaluation.date_evaluation.isoformat() if evaluation.date_evaluation else None,
            'created_at': evaluation.created_at.isoformat() if evaluation.created_at else None,
            'created_by': evaluation.created_by,
            'is_active': evaluation.is_active
        }

    # Ajouter ces méthodes à la fin de la classe EvaluationController

    def get_sinistres_recents(self, limit: int = 50) -> List[dict]:
        """Récupère les sinistres récents (délégation)"""
        try:
            from addons.sinistres.controllers.sinistre_controller import SinistreController
            sc = SinistreController()
            sc.set_current_user(self.get_current_user())
            return sc.get_sinistres_recents(limit)
        except Exception as e:
            self.handle_error(e)
            return []

    def get_provisions_by_sinistre(self, sinistre_id: int) -> List[dict]:
        """Récupère toutes les provisions d'un sinistre"""
        try:
            provisions = self.service.get_provisions_by_sinistre(sinistre_id)
            return [
                {
                    'id': p.id,
                    'numero_provision': p.numero_provision,
                    'type_provision': p.type_provision,
                    'categorie': p.categorie,
                    'montant': p.montant,
                    'est_active': p.est_active,
                    'est_comptabilisee': p.est_comptabilisee,
                    'date_creation': p.date_creation.isoformat() if p.date_creation else None,
                    'motif': p.motif
                }
                for p in provisions
            ]
        except Exception as e:
            self.handle_error(e)
            return []

    def get_evaluation_by_numero(self, numero: str) -> Optional[dict]:
        """Récupère une évaluation par son numéro"""
        try:
            evaluation = self.service.get_evaluation_by_numero(numero)
            if evaluation:
                return self._serialize_evaluation(evaluation)
            return None
        except Exception as e:
            self.handle_error(e)
            return None

    def get_revisions_by_evaluation(self, evaluation_id: int) -> List[dict]:
        """Récupère toutes les révisions d'une évaluation"""
        try:
            return self.get_revisions(evaluation_id)
        except Exception as e:
            self.handle_error(e)
            return []

    def get_sinistre_info(self, sinistre_id: int) -> dict:
        """Récupère les informations d'un sinistre"""
        try:
            from addons.sinistres.controllers.sinistre_controller import SinistreController
            sc = SinistreController()
            sc.set_current_user(self.get_current_user())
            return sc.get_sinistre(sinistre_id)
        except Exception as e:
            self.handle_error(e)
            return {}