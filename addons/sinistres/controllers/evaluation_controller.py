"""
Contrôleur des évaluations - Interface entre l'UI et EvaluationService
"""
import datetime

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
        return montant_brut - franchise
    
    def get_statistiques(self, sinistre_id: int = None) -> Dict[str, Any]:
        """Récupère les statistiques des évaluations"""
        try:
            return self.service.get_statistiques(sinistre_id)
        except Exception as e:
            self.handle_error(e)
            return {}

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

    def get_missions_validees(self, sinistre_id: int) -> List[dict]:
        """
        Missions d'expertise VALIDÉES (type EXPERTISE ou CONTRE_EXPERTISE)
        rattachées au sinistre, pour servir de base à une évaluation.
        """
        try:
            from addons.sinistres.services.expertise_service import ExpertiseService
            svc = ExpertiseService()
            missions = svc.get_missions_by_sinistre(sinistre_id)

            result = []
            for m in missions:
                if m.statut != "VALIDE":
                    continue
                if m.type_mission_code not in ("EXPERTISE", "CONTRE_EXPERTISE", "GARAGISTE"):
                    continue
                # On ne prend que les missions qui portent un montant
                if not m.montant_estime:
                    continue
                result.append(self._serialize_mission_basic(m))
            return result
        except Exception as e:
            self.handle_error(e)
            return []

    def _serialize_mission_basic(self, m) -> dict:
        """Sérialisation légère d'une mission pour le dialog d'évaluation."""
        parent_num = None
        if m.mission_parente_id:
            from addons.sinistres.services.expertise_service import ExpertiseService
            p = ExpertiseService().get_mission(m.mission_parente_id)
            if p:
                parent_num = p.numero_mission

        return {
            'id': m.id,
            'numero_mission': m.numero_mission,
            'type_mission_code': m.type_mission_code,
            'type_mission_libelle': (
                'Contre-expertise' if m.type_mission_code == 'CONTRE_EXPERTISE'
                else 'Garagiste' if m.type_mission_code == 'GARAGISTE'
                else 'Expertise'
            ),
            'type_expertise': m.type_expertise,
            'expert_nom': m.expert_nom,
            'montant_estime': float(m.montant_estime) if m.montant_estime else 0,
            'date_validation': (
                m.date_validation.isoformat() if m.date_validation else None
            ),
            'mission_parente_numero': parent_num,
        }

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

    def get_all_evaluations(self) -> List[dict]:
        """Récupère toutes les évaluations (tous sinistres)"""
        try:
            evaluations = self.service.get_all_evaluations()
            return [self._serialize_evaluation(e) for e in evaluations]
        except Exception as e:
            self.handle_error(e)
            return []

    def get_all_provisions(self) -> List[dict]:
        """Récupère toutes les provisions (tous sinistres)"""
        try:
            provisions = self.service.get_all_provisions()
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

    def get_evaluation_by_dommage(self, dommage_id: int) -> Optional[dict]:
        """Récupère l'évaluation associée à un dommage (SIN-041 : 1-1)"""
        try:
            evaluation = self.service.get_evaluation_by_dommage(dommage_id)
            if evaluation:
                return self._serialize_evaluation(evaluation)
            return None
        except Exception as e:
            self.handle_error(e)
            return None

    def get_provisions_by_evaluation(self, evaluation_id: int) -> List[dict]:
        """Récupère les provisions générées par une évaluation"""
        try:
            provisions = self.service.get_provisions_by_evaluation(evaluation_id)
            return [
                {
                    'id': p.id,
                    'numero_provision': p.numero_provision,
                    'type_provision': p.type_provision,
                    'montant': p.montant,
                    'est_active': p.est_active,
                    'date_creation': p.date_creation.isoformat() if p.date_creation else None,
                }
                for p in provisions
            ]
        except Exception as e:
            self.handle_error(e)
            return []

    def _serialize_evaluation(self, evaluation) -> dict:
        """Sérialise une évaluation en dictionnaire"""
        return {
            'id': evaluation.id,
            'numero_evaluation': evaluation.numero_evaluation,
            'sinistre_id': evaluation.sinistre_id,
            'dommage_id': getattr(evaluation, 'dommage_id', None),  # ✅ NOUVEAU
            'type_evaluation': evaluation.type_evaluation,
            'categorie': evaluation.categorie,
            'montant_brut': evaluation.montant_brut,
            'montant_expert': float(evaluation.montant_expert) if evaluation.montant_expert else None,
            'franchise': evaluation.franchise,
            'taux_responsabilite': evaluation.taux_responsabilite,
            'montant_net': evaluation.montant_net,
            'details': evaluation.details,
            'statut': getattr(evaluation, 'statut', 'BROUILLON'),  # ✅ NOUVEAU
            'est_validee': evaluation.est_validee,
            'validee_par': evaluation.validee_par,
            'date_validation': evaluation.date_validation.isoformat() if evaluation.date_validation else None,
            'date_evaluation': evaluation.date_evaluation.isoformat() if evaluation.date_evaluation else None,
            'created_at': evaluation.created_at.isoformat() if evaluation.created_at else None,
            'created_by': evaluation.created_by,
            'is_active': evaluation.is_active
        }

    def get_taches_by_entite(self, entite_type: str, entite_id: int) -> List[dict]:
        """Récupère les tâches liées à une entité (SINISTRE, EVALUATION, etc.)"""
        try:
            taches = self.service.get_taches_by_entite(entite_type, entite_id)
            return [
                {
                    'id': t.id,
                    'titre': t.titre,
                    'description': t.description,
                    'type_tache': t.type_tache,
                    'priorite': t.priorite,
                    'statut': t.statut,
                    'assignee_a': t.assignee_a,
                    'date_echeance': t.date_echeance.isoformat() if t.date_echeance else None,
                }
                for t in taches
            ]
        except Exception as e:
            self.handle_error(e)
            return []

    def get_provisions_by_dommage(self, dommage_id: int) -> List[dict]:
        """Récupère les provisions liées au dommage (via son évaluation)"""
        try:
            evaluation = self.get_evaluation_by_dommage(dommage_id)
            if not evaluation:
                return []
            return self.get_provisions_by_evaluation(evaluation['id'])
        except Exception as e:
            self.handle_error(e)
            return []

    def get_taches_by_sinistre(self, sinistre_id: int) -> List[dict]:
        """Récupère les tâches d'un sinistre"""
        try:
            taches = self.service.get_taches_by_sinistre(sinistre_id)
            return [
                {
                    'id': t.id,
                    'titre': t.titre,
                    'description': t.description,
                    'type_tache': t.type_tache,
                    'priorite': t.priorite,
                    'statut': t.statut,
                    'assignee_a': t.assignee_a,
                    'date_echeance': t.date_echeance.isoformat() if t.date_echeance else None,
                }
                for t in taches
            ]
        except Exception as e:
            self.handle_error(e)
            return []

    def toggle_provision_active(self, provision_id: int, active: bool) -> bool:
        """
        ✅ DÉLÉGATION AU SERVICE
        Le contrôleur ne fait AUCUN SQL — il appelle le service et émet un signal.
        """
        try:
            # ✅ 1. Vérification utilisateur (responsabilité contrôleur)
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            # ✅ 2. Appel au service (responsabilité métier)
            provision = self.service.toggle_provision_active(  # ✅ Service
                provision_id=provision_id,
                active=active
            )
            
            # ✅ 3. Feedback UI (responsabilité contrôleur)
            if provision:
                self.success_occurred.emit(
                    f"✅ Provision {'activée' if active else 'désactivée'} : "
                    f"{provision.numero_provision}"
                )
                return True
            
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    def comptabiliser_provision(self, provision_id: int) -> bool:
        """
        ✅ DÉLÉGATION AU SERVICE
        Le service fait le SQL, le contrôleur orchestre.
        """
        try:
            # ✅ 1. Vérification utilisateur
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            # ✅ 2. Appel au service
            provision = self.service.comptabiliser_provision(  # ✅ Service
                provision_id=provision_id,
                utilisateur_id=self.get_current_user_id()
            )
            
            # ✅ 3. Tentative de création d'écriture comptable (optionnel)
            if provision:
                try:
                    self._creer_ecriture_comptable_provision(provision)
                except Exception as e:
                    print(f"⚠️ Écriture comptable non créée : {e}")
                
                self.success_occurred.emit(
                    f"✅ Provision comptabilisée : {provision.numero_provision}"
                )
                return True
            
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    def get_provision(self, provision_id: int) -> Optional[dict]:
        """Récupère une provision par son ID"""
        try:
            provision = self.service.get_provision(provision_id)  # ✅ Service
            if provision:
                return self._serialize_provision(provision)
            return None
        except Exception as e:
            self.handle_error(e)
            return None
    
    def _creer_ecriture_comptable_provision(self, provision):
        """
        Méthode privée : orchestre la création d'écriture comptable.
        Le contrôleur appelle un AUTRE contrôleur/service, pas du SQL direct.
        """
        try:
            from addons.sinistres.controllers.comptabilite_controller import (
                ComptabiliteController
            )
            compta = ComptabiliteController()
            compta.set_current_user(self.get_current_user())
            
            if hasattr(compta, 'creer_ecriture_provision'):
                compta.creer_ecriture_provision(
                    provision_id=provision.id,
                    montant=provision.montant,
                    libelle=f"Comptabilisation provision {provision.numero_provision}",
                    date_ecriture=datetime.now()
                )
        except ImportError:
            print("⚠️ ComptabiliteController non disponible")

    def _serialize_provision(self, provision) -> dict:
        """Sérialise une provision en dictionnaire"""
        return {
            'id': provision.id,
            'numero_provision': provision.numero_provision,
            'sinistre_id': getattr(provision, 'sinistre_id', None),
            'evaluation_id': getattr(provision, 'evaluation_id', None),
            'type_provision': getattr(provision, 'type_provision', ''),
            'categorie': getattr(provision, 'categorie', ''),
            'montant': float(getattr(provision, 'montant', 0) or 0),
            'est_active': bool(getattr(provision, 'est_active', True)),
            'est_comptabilisee': bool(getattr(provision, 'est_comptabilisee', False)),
            'date_creation': provision.date_creation.isoformat() if getattr(provision, 'date_creation', None) else None,
            'date_comptabilisation': provision.date_comptabilisation.isoformat() if getattr(provision, 'date_comptabilisation', None) else None,
            'comptabilise_par': getattr(provision, 'comptabilise_par', None),
            'motif': getattr(provision, 'motif', ''),
        }

    
