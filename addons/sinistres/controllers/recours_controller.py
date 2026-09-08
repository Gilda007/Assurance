"""
Contrôleur des recours - Interface entre l'UI et RecoursService
"""
from PySide6.QtCore import Signal
from typing import Optional, List, Dict, Any

from addons.sinistres.controllers.controleur_base import BaseController
from addons.sinistres.services.recours_service import RecoursService


class RecoursController(BaseController):
    """Contrôleur pour la gestion des recours"""
    
    # Signaux spécifiques
    recours_created = Signal(dict)
    recours_updated = Signal(dict)
    recours_status_changed = Signal(int, str)
    recours_list_updated = Signal(list)
    encaissement_added = Signal(dict)
    reversement_added = Signal(dict)
    relance_added = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.service = RecoursService()
    
    # ============================================================
    # GESTION DES RECOURS
    # ============================================================
    
    def creer_recours(self, data: Dict[str, Any]) -> Optional[dict]:
        """Crée un nouveau recours"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return None
            
            data['created_by'] = self.get_current_user_id()
            recours = self.service.creer_recours(data)
            result = self._serialize_recours(recours)
            
            self.recours_created.emit(result)
            self.handle_success(f"Recours {recours.numero_recours} créé avec succès")
            return result
            
        except Exception as e:
            self.handle_error(e)
            return None
    
    def get_recours(self, recours_id: int) -> Optional[dict]:
        """Récupère un recours par son ID"""
        try:
            recours = self.service.get_recours(recours_id)
            if recours:
                return self._serialize_recours(recours)
            return None
        except Exception as e:
            self.handle_error(e)
            return None
    
    def get_recours_by_sinistre(self, sinistre_id: int) -> List[dict]:
        """Récupère tous les recours d'un sinistre"""
        try:
            recours = self.service.get_recours_by_sinistre(sinistre_id)
            result = [self._serialize_recours(r) for r in recours]
            self.recours_list_updated.emit(result)
            return result
        except Exception as e:
            self.handle_error(e)
            return []
    
    def update_recours(self, recours_id: int, data: Dict[str, Any]) -> bool:
        """Met à jour un recours"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            data['updated_by'] = self.get_current_user_id()
            recours = self.service.update_recours(recours_id, data)
            
            if recours:
                self.recours_updated.emit(self._serialize_recours(recours))
                self.handle_success("Recours mis à jour")
                return True
            
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    def changer_statut_recours(self, recours_id: int, nouveau_statut: str, motif: str = None) -> bool:
        """Change le statut d'un recours"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            recours = self.service.changer_statut_recours(
                recours_id=recours_id,
                nouveau_statut=nouveau_statut,
                utilisateur_id=self.get_current_user_id(),
                motif=motif
            )
            
            if recours:
                self.recours_status_changed.emit(recours_id, nouveau_statut)
                self.handle_success(f"Statut changé en {nouveau_statut}")
                return True
            
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    # ============================================================
    # GESTION DES ENCAISSEMENTS
    # ============================================================
    
    def enregistrer_encaissement(self, recours_id: int, data: Dict[str, Any]) -> bool:
        """Enregistre un encaissement"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            encaissement = self.service.enregistrer_encaissement(
                recours_id=recours_id,
                data=data,
                utilisateur_id=self.get_current_user_id()
            )
            
            if encaissement:
                self.encaissement_added.emit({
                    'id': encaissement.id,
                    'montant': encaissement.montant,
                    'mode_encaissement': encaissement.mode_encaissement,
                    'date_encaissement': encaissement.date_encaissement.isoformat() if encaissement.date_encaissement else None,
                    'solde_apres_encaissement': encaissement.solde_apres_encaissement
                })
                self.handle_success(f"Encaissement de {encaissement.montant} enregistré")
                return True
            
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    def get_encaissements(self, recours_id: int) -> List[dict]:
        """Récupère tous les encaissements d'un recours"""
        try:
            encaissements = self.service.get_encaissements(recours_id)
            return [
                {
                    'id': e.id,
                    'montant': e.montant,
                    'mode_encaissement': e.mode_encaissement,
                    'reference_bancaire': e.reference_bancaire,
                    'date_encaissement': e.date_encaissement.isoformat() if e.date_encaissement else None,
                    'est_partiel': e.est_partiel,
                    'solde_apres_encaissement': e.solde_apres_encaissement,
                    'est_comptabilise': e.est_comptabilise
                }
                for e in encaissements
            ]
        except Exception as e:
            self.handle_error(e)
            return []
    
    # ============================================================
    # GESTION DES REVERSEMENTS
    # ============================================================
    
    def creer_reversement(self, recours_id: int, data: Dict[str, Any]) -> bool:
        """Crée un reversement pour un recours"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            reversement = self.service.creer_reversement(
                recours_id=recours_id,
                data=data,
                utilisateur_id=self.get_current_user_id()
            )
            
            if reversement:
                self.reversement_added.emit({
                    'id': reversement.id,
                    'beneficiaire_id': reversement.beneficiaire_id,
                    'beneficiaire_nom': reversement.beneficiaire_nom,
                    'montant': reversement.montant,
                    'quote_part': reversement.quote_part,
                    'type_reversement': reversement.type_reversement,
                    'mode_paiement': reversement.mode_paiement,
                    'date_reversement': reversement.date_reversement.isoformat() if reversement.date_reversement else None,
                    'est_paye': reversement.est_paye
                })
                self.handle_success(f"Reversement de {reversement.montant} créé")
                return True
            
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    def marquer_reversement_paye(self, reversement_id: int) -> bool:
        """Marque un reversement comme payé"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            result = self.service.marquer_reversement_paye(
                reversement_id=reversement_id,
                utilisateur_id=self.get_current_user_id()
            )
            
            if result:
                self.handle_success("Reversement marqué comme payé")
                return True
            
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    # ============================================================
    # GESTION DES RELANCES
    # ============================================================
    
    def ajouter_relance(self, recours_id: int, data: Dict[str, Any]) -> bool:
        """Ajoute une relance à un recours"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            relance = self.service.ajouter_relance(
                recours_id=recours_id,
                data=data,
                utilisateur_id=self.get_current_user_id()
            )
            
            if relance:
                self.relance_added.emit({
                    'id': relance.id,
                    'date_relance': relance.date_relance.isoformat() if relance.date_relance else None,
                    'type_relance': relance.type_relance,
                    'contenu': relance.contenu,
                    'statut': relance.statut
                })
                self.handle_success("Relance ajoutée")
                return True
            
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    def get_relances(self, recours_id: int) -> List[dict]:
        """Récupère toutes les relances d'un recours"""
        try:
            relances = self.service.get_relances(recours_id)
            return [
                {
                    'id': r.id,
                    'date_relance': r.date_relance.isoformat() if r.date_relance else None,
                    'type_relance': r.type_relance,
                    'contenu': r.contenu,
                    'reponse_recue': r.reponse_recue,
                    'date_reponse': r.date_reponse.isoformat() if r.date_reponse else None,
                    'contenu_reponse': r.contenu_reponse,
                    'prochaine_relance': r.prochaine_relance.isoformat() if r.prochaine_relance else None,
                    'statut': r.statut
                }
                for r in relances
            ]
        except Exception as e:
            self.handle_error(e)
            return []
    
    def get_statistiques(self, sinistre_id: int = None) -> Dict[str, Any]:
        """Récupère les statistiques des recours"""
        try:
            return self.service.get_statistiques(sinistre_id)
        except Exception as e:
            self.handle_error(e)
            return {}
    
    # ============================================================
    # MÉTHODE PRIVÉE
    # ============================================================
    
    def _serialize_recours(self, recours) -> dict:
        """Sérialise un recours en dictionnaire"""
        return {
            'id': recours.id,
            'numero_recours': recours.numero_recours,
            'sinistre_id': recours.sinistre_id,
            'type_recours': recours.type_recours,
            'debiteur_id': recours.debiteur_id,
            'debiteur_nom': recours.debiteur_nom,
            'montant_reclame': recours.montant_reclame,
            'montant_accepte': recours.montant_accepte,
            'montant_encaisse': recours.montant_encaisse,
            'solde': recours.solde,
            'date_ouverture': recours.date_ouverture.isoformat() if recours.date_ouverture else None,
            'date_accord': recours.date_accord.isoformat() if recours.date_accord else None,
            'date_derniere_relance': recours.date_derniere_relance.isoformat() if recours.date_derniere_relance else None,
            'date_prochaine_relance': recours.date_prochaine_relance.isoformat() if recours.date_prochaine_relance else None,
            'date_cloture': recours.date_cloture.isoformat() if recours.date_cloture else None,
            'statut': recours.statut,
            'responsable_id': recours.responsable_id,
            'nombre_relances': recours.nombre_relances,
            'observations': recours.observations,
            'created_at': recours.created_at.isoformat() if recours.created_at else None,
            'created_by': recours.created_by,
            'is_active': recours.is_active
        }

    # Ajouter ces méthodes à la fin de la classe RecoursController

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

    def get_recours_by_numero(self, numero: str) -> Optional[dict]:
        """Récupère un recours par son numéro"""
        try:
            recours = self.service.get_recours_by_numero(numero)
            if recours:
                return self._serialize_recours(recours)
            return None
        except Exception as e:
            self.handle_error(e)
            return None

    def get_encaissements_by_recours(self, recours_id: int) -> List[dict]:
        """Récupère tous les encaissements d'un recours"""
        try:
            return self.get_encaissements(recours_id)
        except Exception as e:
            self.handle_error(e)
            return []

    def get_reversements_by_recours(self, recours_id: int) -> List[dict]:
        """Récupère tous les reversements d'un recours"""
        try:
            reversements = self.service.get_reversements(recours_id)
            return [
                {
                    'id': r.id,
                    'beneficiaire_id': r.beneficiaire_id,
                    'beneficiaire_nom': r.beneficiaire_nom,
                    'montant': r.montant,
                    'quote_part': r.quote_part,
                    'type_reversement': r.type_reversement,
                    'mode_paiement': r.mode_paiement,
                    'date_reversement': r.date_reversement.isoformat() if r.date_reversement else None,
                    'est_paye': r.est_paye,
                    'est_comptabilise': r.est_comptabilise
                }
                for r in reversements
            ]
        except Exception as e:
            self.handle_error(e)
            return []

    def get_relances_by_recours(self, recours_id: int) -> List[dict]:
        """Récupère toutes les relances d'un recours"""
        try:
            return self.get_relances(recours_id)
        except Exception as e:
            self.handle_error(e)
            return []

    def get_statistiques_recours_global(self) -> Dict[str, Any]:
        """Récupère les statistiques globales des recours"""
        try:
            return self.service.get_statistiques()
        except Exception as e:
            self.handle_error(e)
            return {}

    def get_recours_a_relancer(self) -> List[dict]:
        """Récupère les recours nécessitant une relance"""
        try:
            recours = self.service.get_recours_a_relancer()
            return [self._serialize_recours(r) for r in recours]
        except Exception as e:
            self.handle_error(e)
            return []

    def get_relances_en_attente(self, recours_id: int) -> List[dict]:
        """Récupère les relances en attente de réponse"""
        try:
            relances = self.service.get_relances_en_attente(recours_id)
            return [
                {
                    'id': r.id,
                    'date_relance': r.date_relance.isoformat() if r.date_relance else None,
                    'type_relance': r.type_relance,
                    'contenu': r.contenu,
                    'statut': r.statut
                }
                for r in relances
            ]
        except Exception as e:
            self.handle_error(e)
            return []

    def marquer_reponse_relance(self, relance_id: int, contenu_reponse: str) -> bool:
        """Marque une relance comme ayant reçu une réponse"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            result = self.service.marquer_reponse_relance(
                relance_id=relance_id,
                contenu_reponse=contenu_reponse,
                utilisateur_id=self.get_current_user_id()
            )
            if result:
                self.handle_success("Réponse enregistrée")
                return True
            return False
        except Exception as e:
            self.handle_error(e)
            return False

    def planifier_relances_auto(self) -> Dict[str, int]:
        """Planifie automatiquement les relances"""
        try:
            return self.service.planifier_relances_auto()
        except Exception as e:
            self.handle_error(e)
            return {'planifiees': 0, 'erreurs': 0}