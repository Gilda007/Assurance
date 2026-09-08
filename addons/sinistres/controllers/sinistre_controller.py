"""
Contrôleur des sinistres - Interface entre l'UI et SinistreService
"""
from PySide6.QtCore import Signal
from typing import Optional, List, Dict, Any
from datetime import datetime

from addons.sinistres.controllers.controleur_base import BaseController
from addons.sinistres.services.sinistre_service import SinistreService
from addons.sinistres.services.referentiel_service import ReferentielService
from addons.sinistres.models.sinistre import (
    LometaSinistre, LometaDommage, LometaTiers, 
    LometaCommentaireSinistre, LometaHistoriqueSinistre
)


class SinistreController(BaseController):
    """Contrôleur pour la gestion des sinistres"""
    
    # Signaux spécifiques
    sinistre_created = Signal(dict)
    sinistre_updated = Signal(dict)
    sinistre_deleted = Signal(int)
    sinistre_status_changed = Signal(int, str)
    sinistre_list_updated = Signal(list)
    
    def __init__(self):
        super().__init__()
        self.service = SinistreService()
        self.referentiel_service = ReferentielService()
    
    # ============================================================
    # CRUD PRINCIPAL
    # ============================================================
    
    def creer_sinistre(self, data: Dict[str, Any]) -> Optional[dict]:
        """Crée un nouveau sinistre"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return None
            
            data['created_by'] = self.get_current_user_id()
            
            sinistre = self.service.creer_sinistre(data)
            result = self._serialize_sinistre(sinistre)
            
            self.sinistre_created.emit(result)
            self.handle_success(f"Sinistre {sinistre.numero_sinistre} créé avec succès")
            return result
            
        except Exception as e:
            self.handle_error(e)
            return None
    
    def get_sinistre(self, sinistre_id: int) -> Optional[dict]:
        """Récupère un sinistre par son ID"""
        try:
            sinistre = self.service.get_sinistre(sinistre_id)
            if sinistre:
                return self._serialize_sinistre(sinistre)
            self.error_occurred.emit("Sinistre non trouvé")
            return None
        except Exception as e:
            self.handle_error(e)
            return None
    
    def get_sinistre_by_numero(self, numero: str) -> Optional[dict]:
        """Récupère un sinistre par son numéro"""
        try:
            sinistre = self.service.get_sinistre_by_numero(numero)
            if sinistre:
                return self._serialize_sinistre(sinistre)
            return None
        except Exception as e:
            self.handle_error(e)
            return None
    
    def update_sinistre(self, sinistre_id: int, data: Dict[str, Any]) -> bool:
        """Met à jour un sinistre"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            data['updated_by'] = self.get_current_user_id()
            sinistre = self.service.update_sinistre(sinistre_id, data)
            
            if sinistre:
                self.sinistre_updated.emit(self._serialize_sinistre(sinistre))
                self.handle_success("Sinistre mis à jour avec succès")
                return True
            
            self.error_occurred.emit("Sinistre non trouvé")
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    def rechercher_sinistres(self, criteres: Dict[str, Any]) -> List[dict]:
        """Recherche des sinistres"""
        try:
            sinistres = self.service.rechercher_sinistres(criteres)
            result = [self._serialize_sinistre(s) for s in sinistres]
            self.sinistre_list_updated.emit(result)
            return result
        except Exception as e:
            self.handle_error(e)
            return []
    
    def get_statistiques(self, branche: str = None) -> Dict[str, Any]:
        """Récupère les statistiques des sinistres"""
        try:
            return self.service.get_statistiques(branche)
        except Exception as e:
            self.handle_error(e)
            return {}

    def get_sinistres_recents(self, limit: int = 50) -> List[dict]:
        """Récupère les sinistres récents pour les combos"""
        try:
            sinistres = self.service.rechercher_sinistres({'limit': limit})
            return [self._serialize_sinistre(s) for s in sinistres]
        except Exception as e:
            self.handle_error(e)
            return []
    # ============================================================
    # GESTION DU CYCLE DE VIE
    # ============================================================
    
    def changer_statut(self, sinistre_id: int, nouveau_statut: str, motif: str = None) -> bool:
        """Change le statut d'un sinistre"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            sinistre = self.service.changer_statut(
                sinistre_id=sinistre_id,
                nouveau_statut=nouveau_statut,
                utilisateur_id=self.get_current_user_id(),
                motif=motif
            )
            
            if sinistre:
                self.sinistre_status_changed.emit(sinistre_id, nouveau_statut)
                self.handle_success(f"Statut changé en {nouveau_statut}")
                return True
            
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    def cloturer_sinistre(self, sinistre_id: int, motif: str) -> bool:
        """Clôture un sinistre"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            sinistre = self.service.cloturer_sinistre(
                sinistre_id=sinistre_id,
                utilisateur_id=self.get_current_user_id(),
                motif=motif
            )
            
            if sinistre:
                self.sinistre_status_changed.emit(sinistre_id, "CLOTURE")
                self.handle_success("Sinistre clôturé avec succès")
                return True
            
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    def reouvrir_sinistre(self, sinistre_id: int, motif: str) -> bool:
        """Réouvre un sinistre clôturé"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            sinistre = self.service.reouvrir_sinistre(
                sinistre_id=sinistre_id,
                utilisateur_id=self.get_current_user_id(),
                motif=motif
            )
            
            if sinistre:
                self.sinistre_status_changed.emit(sinistre_id, "REOUVERT")
                self.handle_success("Sinistre réouvert avec succès")
                return True
            
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    def get_transitions(self, statut_actuel: str) -> List[str]:
        """Récupère les transitions autorisées pour un statut"""
        try:
            from services.workflow_service import WorkflowService
            workflow_service = WorkflowService()
            return workflow_service.get_transitions(statut_actuel)
        except Exception as e:
            self.handle_error(e)
            return []
    
    # ============================================================
    # GESTION DES DOMMAGES
    # ============================================================
    
    def ajouter_dommage(self, sinistre_id: int, data: Dict[str, Any]) -> Optional[dict]:
        """Ajoute un dommage à un sinistre"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return None
            
            data['created_by'] = self.get_current_user_id()
            dommage = self.service.ajouter_dommage(sinistre_id, data)
            
            return {
                'id': dommage.id,
                'type_dommage': dommage.type_dommage,
                'description': dommage.description,
                'montant_estime': dommage.montant_estime
            }
        except Exception as e:
            self.handle_error(e)
            return None
    
    def get_dommages(self, sinistre_id: int) -> List[dict]:
        """Récupère tous les dommages d'un sinistre"""
        try:
            dommages = self.service.get_dommages(sinistre_id)
            return [
                {
                    'id': d.id,
                    'type_dommage': d.type_dommage,
                    'description': d.description,
                    'montant_estime': d.montant_estime,
                    'montant_accepte': d.montant_accepte
                }
                for d in dommages
            ]
        except Exception as e:
            self.handle_error(e)
            return []
    
    # ============================================================
    # GESTION DES TIERS
    # ============================================================
    
    def ajouter_tiers(self, sinistre_id: int, data: Dict[str, Any]) -> Optional[dict]:
        """Ajoute un tiers à un sinistre"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return None
            
            data['created_by'] = self.get_current_user_id()
            tiers = self.service.ajouter_tiers(sinistre_id, data)
            
            return {
                'id': tiers.id,
                'type_tiers': tiers.type_tiers,
                'nom': tiers.nom,
                'prenom': tiers.prenom
            }
        except Exception as e:
            self.handle_error(e)
            return None
    
    def get_tiers(self, sinistre_id: int) -> List[dict]:
        """Récupère tous les tiers d'un sinistre"""
        try:
            tiers = self.service.get_tiers(sinistre_id)
            return [
                {
                    'id': t.id,
                    'type_tiers': t.type_tiers,
                    'nom': t.nom,
                    'prenom': t.prenom,
                    'assurance': t.assurance
                }
                for t in tiers
            ]
        except Exception as e:
            self.handle_error(e)
            return []
    
    # ============================================================
    # GESTION DES COMMENTAIRES
    # ============================================================
    
    def ajouter_commentaire(self, sinistre_id: int, contenu: str, type_commentaire: str) -> bool:
        """Ajoute un commentaire au sinistre"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            self.service.ajouter_commentaire(
                sinistre_id=sinistre_id,
                utilisateur_id=self.get_current_user_id(),
                contenu=contenu,
                type_commentaire=type_commentaire
            )
            
            self.handle_success("Commentaire ajouté")
            return True
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    def get_commentaires(self, sinistre_id: int) -> List[dict]:
        """Récupère tous les commentaires d'un sinistre"""
        try:
            commentaires = self.service.get_commentaires(sinistre_id)
            return [
                {
                    'id': c.id,
                    'contenu': c.contenu,
                    'type_commentaire': c.type_commentaire,
                    'version': c.version,
                    'created_at': c.created_at.isoformat() if c.created_at else None,
                    'utilisateur': c.created_by
                }
                for c in commentaires
            ]
        except Exception as e:
            self.handle_error(e)
            return []
    
    # ============================================================
    # MÉTHODES PRIVÉES
    # ============================================================
    
    def _serialize_sinistre(self, sinistre: LometaSinistre) -> dict:
        """Sérialise un sinistre en dictionnaire"""
        # Récupérer le nom du responsable
        responsable_nom = None
        if sinistre.responsable_id:
            user = self.service.get_user(sinistre.responsable_id)
            if user:
                responsable_nom = user.full_name or user.username
        
        return {
            'id': sinistre.id,
            'numero_sinistre': sinistre.numero_sinistre,
            'numero_reference': sinistre.numero_reference,
            'date_survenance': sinistre.date_survenance.isoformat() if sinistre.date_survenance else None,
            'date_declaration': sinistre.date_declaration.isoformat() if sinistre.date_declaration else None,
            'date_ouverture': sinistre.date_ouverture.isoformat() if sinistre.date_ouverture else None,
            'contrat_id': sinistre.contrat_id,
            'client_id': sinistre.client_id,
            'branche': sinistre.branche,
            'categorie': sinistre.categorie,
            'sous_categorie': sinistre.sous_categorie,
            'statut': sinistre.statut,
            'taux_responsabilite': sinistre.taux_responsabilite,
            'circonstance_principale': sinistre.circonstance_principale,
            'circonstance_secondaire': sinistre.circonstance_secondaire,
            'description': sinistre.description,
            'date_cloture': sinistre.date_cloture.isoformat() if sinistre.date_cloture else None,
            'responsable_id': sinistre.responsable_id,
            'responsable_nom': responsable_nom,
            'created_at': sinistre.created_at.isoformat() if sinistre.created_at else None,
            'created_by': sinistre.created_by,
            'updated_at': sinistre.updated_at.isoformat() if sinistre.updated_at else None,
            'is_active': sinistre.is_active,
            # Statistiques calculées
            'nb_dommages': len(sinistre.dommages) if sinistre.dommages else 0,
            'nb_tiers': len(sinistre.tiers) if sinistre.tiers else 0,
            'nb_expertises': len(sinistre.expertises) if sinistre.expertises else 0,
            'nb_reglements': len(sinistre.reglements) if sinistre.reglements else 0,
        }

    def get_sinistres_recents(self, limit: int = 50) -> List[dict]:
        """Récupère les sinistres récents pour les combos"""
        try:
            sinistres = self.service.rechercher_sinistres({'limit': limit})
            return [self._serialize_sinistre(s) for s in sinistres]
        except Exception as e:
            self.handle_error(e)
            return []

    def get_sinistres_by_branche(self, branche: str = None) -> List[dict]:
        """Récupère les sinistres par branche"""
        try:
            criteres = {}
            if branche:
                criteres['branche'] = branche
            sinistres = self.service.rechercher_sinistres(criteres)
            return [self._serialize_sinistre(s) for s in sinistres]
        except Exception as e:
            self.handle_error(e)
            return []

    def get_sinistres_by_statut(self, statut: str) -> List[dict]:
        """Récupère les sinistres par statut"""
        try:
            sinistres = self.service.rechercher_sinistres({'statut': statut})
            return [self._serialize_sinistre(s) for s in sinistres]
        except Exception as e:
            self.handle_error(e)
            return []

    # Ajouter cette méthode à la fin de la classe SinistreController

    def get_all_missions(self) -> List[dict]:
        """Récupère toutes les missions d'expertise (tous sinistres)"""
        try:
            missions = self.service.get_all_missions()
            return [self._serialize_mission(m) for m in missions]
        except Exception as e:
            self.handle_error(e)
            return []

    def get_historique_sinistre(self, sinistre_id: int) -> List[dict]:
        """Récupère l'historique complet d'un sinistre"""
        try:
            historique = self.service.get_historique(sinistre_id)
            return [
                {
                    'id': h.id,
                    'utilisateur_id': h.utilisateur_id,
                    'utilisateur_nom': h.utilisateur_nom,
                    'date_action': h.date_action.isoformat() if h.date_action else None,
                    'action': h.action,
                    'entite': h.entite,
                    'entite_id': h.entite_id,
                    'champ_modifie': h.champ_modifie,
                    'ancienne_valeur': h.ancienne_valeur,
                    'nouvelle_valeur': h.nouvelle_valeur,
                    'commentaire': h.commentaire
                }
                for h in historique
            ]
        except Exception as e:
            self.handle_error(e)
            return []

    def get_sinistre_complet(self, sinistre_id: int) -> Optional[dict]:
        """Récupère un sinistre complet avec toutes ses relations"""
        try:
            sinistre = self.service.get_sinistre(sinistre_id)
            if not sinistre:
                return None
            
            result = self._serialize_sinistre(sinistre)
            
            # Ajouter les relations
            result['dommages'] = self.get_dommages(sinistre_id)
            result['tiers'] = self.get_tiers(sinistre_id)
            result['commentaires'] = self.get_commentaires(sinistre_id)
            result['historique'] = self.get_historique_sinistre(sinistre_id)
            
            return result
        except Exception as e:
            self.handle_error(e)
            return None