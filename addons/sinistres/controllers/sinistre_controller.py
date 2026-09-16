
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
        """Récupère un sinistre par son ID (retourne un dict sérialisé)"""
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
            from addons.sinistres.services.workflow_service import WorkflowService
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
            
            if not dommage:
                return None
            
            return {
                'id': dommage.id,
                'sinistre_id': dommage.sinistre_id,
                'type_dommage': dommage.type_dommage,
                'description': dommage.description,
                'montant_estime': dommage.montant_estime,
                'montant_accepte': dommage.montant_accepte,
                'photos': getattr(dommage, 'photos', None) or [],
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
                    'montant_accepte': d.montant_accepte,
                    'evaluation_id': d.evaluation_id,
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
            
            if not tiers:
                return None
            
            return self._serialize_tiers(tiers)
        except Exception as e:
            self.handle_error(e)
            return None
    
    def get_tiers(self, sinistre_id: int) -> List[dict]:
        """Récupère tous les tiers d'un sinistre"""
        try:
            tiers_list = self.service.get_tiers(sinistre_id)
            return [self._serialize_tiers(t) for t in tiers_list]
        except Exception as e:
            self.handle_error(e)
            return []
    
    def update_tiers(self, tiers_id: int, data: Dict[str, Any]) -> Optional[dict]:
        """Met à jour un tiers"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return None
            
            data['updated_by'] = self.get_current_user_id()
            tiers = self.service.update_tiers(tiers_id, data)
            
            if tiers:
                result = self._serialize_tiers(tiers)
                self.handle_success("Tiers mis à jour")
                return result
            return None
        except Exception as e:
            self.handle_error(e)
            return None
    
    def supprimer_tiers(self, tiers_id: int) -> bool:
        """Supprime (soft delete) un tiers"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            result = self.service.supprimer_tiers(
                tiers_id,
                utilisateur_id=self.get_current_user_id()
            )
            if result:
                self.handle_success("Tiers supprimé")
            return result
        except Exception as e:
            self.handle_error(e)
            return False
    
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
    # MISSIONS D'EXPERTISE
    # ============================================================
    
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
            return self.service.get_historique_sinistre(sinistre_id)
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
            result['commentaires'] = self.get_commentaires(sinistre_id)
            result['historique'] = self.get_historique_sinistre(sinistre_id)
            
            return result
        except Exception as e:
            self.handle_error(e)
            return None
    
    # ============================================================
    # MÉTHODES PRIVÉES - SÉRIALISATION
    # ============================================================
    
    def _serialize_sinistre(self, sinistre: LometaSinistre) -> dict:
        """Sérialise un sinistre complet avec toutes ses relations"""
        
        # --- Responsable ---
        responsable_nom = None
        if sinistre.responsable_id:
            try:
                user = self.service.get_user(sinistre.responsable_id)
                if user:
                    responsable_nom = getattr(user, 'full_name', None) or getattr(user, 'username', None)
            except Exception:
                pass
        
        # --- Tiers ---
        tiers_list = []
        for t in (sinistre.tiers or []):
            if getattr(t, 'is_active', True):
                tiers_list.append(self._serialize_tiers(t))
        
        # --- Dommages ---
        dommages_list = [
            {
                'id': d.id,
                'sinistre_id': d.sinistre_id,
                'type_dommage': d.type_dommage,
                'code_dommage': getattr(d, 'code_dommage', None),
                'description': d.description,
                'montant_estime': d.montant_estime,
                'montant_accepte': d.montant_accepte,
                'evaluation_id': d.evaluation_id,
                'photos': getattr(d, 'photos', None) or [], 
            }
            for d in (sinistre.dommages or [])
        ]
        
        # --- Expertises ---
        expertises_list = []
        for e in (sinistre.expertises or []):
            expertises_list.append({
                'id': e.id,
                'numero_mission': getattr(e, 'numero_mission', None),
                'sinistre_id': e.sinistre_id,
                'type_expertise': getattr(e, 'type_expertise', None),
                'domaine': getattr(e, 'domaine', None),
                'expert_nom': getattr(e, 'expert_nom', None),
                'expert_id': getattr(e, 'expert_id', None),
                'date_mission': e.date_mission.isoformat() if getattr(e, 'date_mission', None) else None,
                'date_echeance': e.date_echeance.isoformat() if getattr(e, 'date_echeance', None) else None,
                'montant_estime': getattr(e, 'montant_estime', None),
                'statut': getattr(e, 'statut', None),
                'observations': getattr(e, 'observations', None),
            })
        
        # --- Évaluations ---
        evaluations_list = []
        for ev in (sinistre.evaluations or []):
            evaluations_list.append({
                'id': ev.id,
                'numero_evaluation': getattr(ev, 'numero_evaluation', None),
                'sinistre_id': ev.sinistre_id,
                'type_evaluation': getattr(ev, 'type_evaluation', None),
                'montant_brut': getattr(ev, 'montant_brut', 0),
                'franchise': getattr(ev, 'franchise', 0),
                'taux_responsabilite': getattr(ev, 'taux_responsabilite', 0),
                'montant_net': getattr(ev, 'montant_net', 0),
                'est_validee': getattr(ev, 'est_validee', False),
                'details': getattr(ev, 'details', None),
                'created_at': ev.created_at.isoformat() if getattr(ev, 'created_at', None) else None,
            })
        
        # --- Règlements ---
        reglements_list = []
        for r in (sinistre.reglements or []):
            reglements_list.append({
                'id': r.id,
                'numero_reglement': getattr(r, 'numero_reglement', None),
                'sinistre_id': r.sinistre_id,
                'beneficiaire_nom': getattr(r, 'beneficiaire_nom', None),
                'beneficiaire_id': getattr(r, 'beneficiaire_id', None),
                'montant': getattr(r, 'montant', 0),
                'type_paiement': getattr(r, 'type_paiement', None),
                'statut': getattr(r, 'statut', None),
                'date_demande': r.date_demande.isoformat() if getattr(r, 'date_demande', None) else None,
                'date_paiement': r.date_paiement.isoformat() if getattr(r, 'date_paiement', None) else None,
            })
        
        # --- Recours ---
        recours_list = []
        for rec in (sinistre.recours or []):
            recours_list.append({
                'id': rec.id,
                'numero_recours': getattr(rec, 'numero_recours', None),
                'sinistre_id': rec.sinistre_id,
                'debiteur_nom': getattr(rec, 'debiteur_nom', None),
                'type_recours': getattr(rec, 'type_recours', None),
                'montant_reclame': getattr(rec, 'montant_reclame', 0),
                'montant_accepte': getattr(rec, 'montant_accepte', None),
                'montant_encaisse': getattr(rec, 'montant_encaisse', 0),
                'solde': getattr(rec, 'solde', 0),
                'statut': getattr(rec, 'statut', None),
                'date_ouverture': rec.date_ouverture.isoformat() if getattr(rec, 'date_ouverture', None) else None,
            })
        
        # --- Construction du dict final ---
        return {
            'id': sinistre.id,
            'numero_sinistre': sinistre.numero_sinistre,
            'numero_reference': sinistre.numero_reference,
            'date_survenance': sinistre.date_survenance.isoformat() if sinistre.date_survenance else None,
            'date_declaration': sinistre.date_declaration.isoformat() if sinistre.date_declaration else None,
            'date_ouverture': sinistre.date_ouverture.isoformat() if sinistre.date_ouverture else None,
            'date_cloture': sinistre.date_cloture.isoformat() if sinistre.date_cloture else None,
            'date_reexamen': sinistre.date_reexamen.isoformat() if sinistre.date_reexamen else None,
            'date_derniere_modification': sinistre.date_derniere_modification.isoformat() if sinistre.date_derniere_modification else None,
            'contrat_id': sinistre.contrat_id,
            'client_id': sinistre.client_id,
            'compagnie_id': sinistre.compagnie_id,
            'agence_id': sinistre.agence_id,
            'branche': sinistre.branche,
            'categorie': sinistre.categorie,
            'sous_categorie': sinistre.sous_categorie,
            'statut': sinistre.statut,
            'taux_responsabilite': sinistre.taux_responsabilite,
            'circonstance_principale': sinistre.circonstance_principale,
            'circonstance_secondaire': sinistre.circonstance_secondaire,
            'description': sinistre.description,
            'est_flotte': sinistre.est_flotte,
            'vehicule_sinistre_id': sinistre.vehicule_sinistre_id,
            'flotte_id': sinistre.flotte_id,
            'responsable_id': sinistre.responsable_id,
            'responsable_nom': responsable_nom,
            'created_at': sinistre.created_at.isoformat() if sinistre.created_at else None,
            'created_by': sinistre.created_by,
            'updated_at': sinistre.updated_at.isoformat() if sinistre.updated_at else None,
            'updated_by': sinistre.updated_by,
            'is_active': sinistre.is_active,
            # Relations complètes
            'tiers': tiers_list,
            'dommages': dommages_list,
            'expertises': expertises_list,
            'evaluations': evaluations_list,
            'reglements': reglements_list,
            'recours': recours_list,
            # Compteurs
            'nb_tiers': len(tiers_list),
            'nb_dommages': len(dommages_list),
            'nb_expertises': len(expertises_list),
            'nb_evaluations': len(evaluations_list),
            'nb_reglements': len(reglements_list),
            'nb_recours': len(recours_list),
        }
    
    def _serialize_tiers(self, tiers: LometaTiers) -> dict:
        """Sérialise un tiers complet"""
        return {
            'id': tiers.id,
            'sinistre_id': tiers.sinistre_id,
            'type_tiers': tiers.type_tiers,
            'code_tiers': tiers.code_tiers,
            'civilite': tiers.civilite,
            'nom': tiers.nom,
            'prenom': tiers.prenom,
            'adresse': tiers.adresse,
            'code_postal': tiers.code_postal,
            'ville': tiers.ville,
            'pays': tiers.pays,
            'telephone': tiers.telephone,
            'email': tiers.email,
            'assurance': tiers.assurance,
            'police_assurance': tiers.police_assurance,
            'compagnie_assurance_id': getattr(tiers, 'compagnie_assurance_id', None),
            'date_naissance': tiers.date_naissance.isoformat() if tiers.date_naissance else None,
            'profession': tiers.profession,
            'observations': tiers.observations,
            'created_at': tiers.created_at.isoformat() if tiers.created_at else None,
            'updated_at': tiers.updated_at.isoformat() if tiers.updated_at else None,
            'is_active': getattr(tiers, 'is_active', True),
        }
    
    def _serialize_mission(self, mission) -> dict:
        """Sérialise une mission d'expertise"""
        return {
            'id': mission.id,
            'numero_mission': getattr(mission, 'numero_mission', None),
            'sinistre_id': mission.sinistre_id,
            'type_expertise': getattr(mission, 'type_expertise', None),
            'domaine': getattr(mission, 'domaine', None),
            'expert_id': getattr(mission, 'expert_id', None),
            'expert_nom': getattr(mission, 'expert_nom', None),
            'date_mission': mission.date_mission.isoformat() if getattr(mission, 'date_mission', None) else None,
            'date_echeance': mission.date_echeance.isoformat() if getattr(mission, 'date_echeance', None) else None,
            'montant_estime': getattr(mission, 'montant_estime', None),
            'statut': getattr(mission, 'statut', None),
            'observations': getattr(mission, 'observations', None),
        }