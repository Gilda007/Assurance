"""
Contrôleur des expertises - Interface entre l'UI et ExpertiseService
"""
from PySide6.QtCore import Signal
from typing import Optional, List, Dict, Any

from addons.sinistres.controllers.controleur_base import BaseController
from addons.sinistres.models.sinistre import LometaSinistre
from addons.sinistres.services.expertise_service import ExpertiseService


class ExpertiseController(BaseController):
    """Contrôleur pour la gestion des expertises"""
    
    # Signaux spécifiques
    mission_created = Signal(dict)
    mission_updated = Signal(dict)
    mission_status_changed = Signal(int, str)
    mission_list_updated = Signal(list)
    
    def __init__(self):
        super().__init__()
        self.service = ExpertiseService()
    
    # ============================================================
    # GESTION DES MISSIONS
    # ============================================================
    
    def creer_mission(self, data: Dict[str, Any]) -> Optional[dict]:
        """Crée une nouvelle mission d'expertise"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return None
            
            data['created_by'] = self.get_current_user_id()
            mission = self.service.creer_mission(data)
            result = self._serialize_mission(mission)
            
            self.mission_created.emit(result)
            self.handle_success(f"Mission {mission.numero_mission} créée avec succès")
            return result
            
        except Exception as e:
            self.handle_error(e)
            return None
    
    def get_mission(self, mission_id: int) -> Optional[dict]:
        """Récupère une mission par son ID"""
        try:
            mission = self.service.get_mission(mission_id)
            if mission:
                return self._serialize_mission(mission)
            return None
        except Exception as e:
            self.handle_error(e)
            return None

    def get_all_missions(self) -> List[dict]:
        """Récupère toutes les missions d'expertise (tous sinistres)"""
        try:
            missions = self.service.get_all_missions()
            return [self._serialize_mission(m) for m in missions]
        except Exception as e:
            self.handle_error(e)
            return []
    
    def get_missions_by_sinistre(self, sinistre_id: int) -> List[dict]:
        """Récupère toutes les missions d'un sinistre"""
        try:
            missions = self.service.get_missions_by_sinistre(sinistre_id)
            result = [self._serialize_mission(m) for m in missions]
            self.mission_list_updated.emit(result)
            return result
        except Exception as e:
            self.handle_error(e)
            return []
    
    def get_missions_by_expert(self, expert_id: int) -> List[dict]:
        """Récupère toutes les missions d'un expert"""
        try:
            missions = self.service.get_missions_by_expert(expert_id)
            return [self._serialize_mission(m) for m in missions]
        except Exception as e:
            self.handle_error(e)
            return []
    
    def affecter_expert(self, mission_id: int, expert_id: int) -> bool:
        """Affecte un expert à une mission"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            mission = self.service.affecter_expert(
                mission_id=mission_id,
                expert_id=expert_id,
                utilisateur_id=self.get_current_user_id()
            )
            
            if mission:
                self.mission_updated.emit(self._serialize_mission(mission))
                self.handle_success("Expert affecté avec succès")
                return True
            
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    def demarrer_mission(self, mission_id: int) -> bool:
        """Démarre une mission"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            mission = self.service.demarrer_mission(
                mission_id=mission_id,
                utilisateur_id=self.get_current_user_id()
            )
            
            if mission:
                self.mission_status_changed.emit(mission_id, "EN_COURS")
                self.handle_success("Mission démarrée")
                return True
            
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    def deposer_rapport(self, mission_id: int, data: Dict[str, Any]) -> bool:
        """Dépose un rapport d'expertise"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            mission = self.service.deposer_rapport(
                mission_id=mission_id,
                data=data,
                utilisateur_id=self.get_current_user_id()
            )
            
            if mission:
                self.mission_updated.emit(self._serialize_mission(mission))
                self.handle_success("Rapport déposé avec succès")
                return True
            
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    def valider_mission(self, mission_id: int) -> bool:
        """Valide une mission d'expertise"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            mission = self.service.valider_mission(
                mission_id=mission_id,
                utilisateur_id=self.get_current_user_id()
            )
            
            if mission:
                self.mission_status_changed.emit(mission_id, "VALIDE")
                self.handle_success("Mission validée")
                return True
            
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    def get_statistiques(self, expert_id: int = None) -> Dict[str, Any]:
        """Récupère les statistiques des expertises"""
        try:
            return self.service.get_statistiques(expert_id)
        except Exception as e:
            self.handle_error(e)
            return {}

    # ============================================================
    # GESTION DES EXPERTS (référentiel)
    # ============================================================

    def get_experts(self) -> List[dict]:
        """Récupère tous les experts du référentiel"""
        try:
            experts = self.service.get_experts()
            return [self._serialize_expert(e) for e in experts]
        except Exception as e:
            self.handle_error(e)
            return []


    def get_expert(self, expert_id: int) -> Optional[dict]:
        """Récupère un expert par son ID"""
        try:
            expert = self.service.get_expert(expert_id)
            if expert:
                return self._serialize_expert(expert)
            return None
        except Exception as e:
            self.handle_error(e)
            return None


    def creer_expert(self, data: Dict[str, Any]) -> Optional[dict]:
        """Crée un nouvel expert"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return None
            
            data['created_by'] = self.get_current_user_id()
            expert = self.service.creer_expert(data)
            
            if expert:
                result = self._serialize_expert(expert)
                self.handle_success(f"Expert {expert.nom} créé avec succès")
                return result
            return None
        except Exception as e:
            self.handle_error(e)
            return None


    def update_expert(self, expert_id: int, data: Dict[str, Any]) -> Optional[dict]:
        """Met à jour un expert"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return None
            
            data['updated_by'] = self.get_current_user_id()
            expert = self.service.update_expert(expert_id, data)
            
            if expert:
                result = self._serialize_expert(expert)
                self.handle_success("Expert mis à jour")
                return result
            return None
        except Exception as e:
            self.handle_error(e)
            return None


    def toggle_expert(self, expert_id: int, actif: bool) -> bool:
        """Active/désactive un expert"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            result = self.service.toggle_expert(
                expert_id=expert_id,
                actif=actif,
                utilisateur_id=self.get_current_user_id(),
            )
            if result:
                self.handle_success("Expert activé" if actif else "Expert désactivé")
            return result
        except Exception as e:
            self.handle_error(e)
            return False


    def get_experts_by_domaine(self, domaine: str) -> List[dict]:
        """Récupère les experts d'un domaine donné"""
        try:
            experts = self.service.get_experts_by_domaine(domaine)
            return [self._serialize_expert(e) for e in experts]
        except Exception as e:
            self.handle_error(e)
            return []


    def get_experts_actifs(self) -> List[dict]:
        """Récupère tous les experts actifs"""
        try:
            experts = self.service.get_experts_actifs()
            return [self._serialize_expert(e) for e in experts]
        except Exception as e:
            self.handle_error(e)
            return []


    def _serialize_expert(self, expert) -> dict:
        """Sérialise un expert"""
        return {
            'id': expert.id,
            'code': getattr(expert, 'code', None),
            'civilite': getattr(expert, 'civilite', None),
            'nom': expert.nom,
            'prenom': getattr(expert, 'prenom', None),
            'nom_complet': f"{expert.nom} {getattr(expert, 'prenom', '') or ''}".strip(),
            'agrement': getattr(expert, 'agrement', None),
            'date_agrement': expert.date_agrement.isoformat() if getattr(expert, 'date_agrement', None) else None,
            'est_actif': getattr(expert, 'est_actif', True),
            'telephone': getattr(expert, 'telephone', None),
            'portable': getattr(expert, 'portable', None),
            'email': getattr(expert, 'email', None),
            'adresse': getattr(expert, 'adresse', None),
            'code_postal': getattr(expert, 'code_postal', None),
            'ville': getattr(expert, 'ville', None),
            'pays': getattr(expert, 'pays', None),
            'domaines': getattr(expert, 'domaines', []) or [],
            'zones': getattr(expert, 'zones', []) or [],
            'tarif_horaire': getattr(expert, 'tarif_horaire', 0),
            'frais_deplacement': getattr(expert, 'frais_deplacement', 0),
            'observations': getattr(expert, 'observations', None),
            'created_at': expert.created_at.isoformat() if getattr(expert, 'created_at', None) else None,
            'is_active': getattr(expert, 'is_active', True),
        }
    
    # ============================================================
    # MÉTHODE PRIVÉE
    # ============================================================
    
    def _serialize_mission(self, mission) -> dict:
        """Sérialise une mission en dictionnaire"""

        # ✅ Récupérer le numéro du sinistre
        sinistre_numero = None
        if mission.sinistre_id:
            sinistre = self.service.get_sinistre(mission.sinistre_id)
            if sinistre:
                sinistre_numero = sinistre.numero_sinistre

        # Récupérer le nom de l'expert
        expert_nom = None
        if mission.expert_id:
            expert = self.service.get_expert(mission.expert_id)
            if expert:
                nom = expert.nom or ''
                prenom = getattr(expert, 'prenom', '') or ''
                expert_nom = f"{nom} {prenom}".strip() or expert.code
        
        
        return {
            'id': mission.id,
            'numero_mission': mission.numero_mission,
            'sinistre_id': mission.sinistre_id,
            'sinistre_numero': sinistre_numero,
            'expert_id': mission.expert_id,
            'expert_nom': expert_nom,
            'type_expertise': mission.type_expertise,
            'domaine': mission.domaine,
            'date_mission': mission.date_mission.isoformat() if mission.date_mission else None,
            'date_echeance': mission.date_echeance.isoformat() if mission.date_echeance else None,
            'date_reception_rapport': mission.date_reception_rapport.isoformat() if mission.date_reception_rapport else None,
            'date_validation': mission.date_validation.isoformat() if mission.date_validation else None,
            'statut': mission.statut,
            'montant_estime': mission.montant_estime,
            'observations': mission.observations,
            'rapport_path': mission.rapport_path,
            'created_at': mission.created_at.isoformat() if mission.created_at else None,
            'created_by': mission.created_by,
            'is_active': mission.is_active
        }


    def get_sinistres_recents(self, limit: int = 50) -> List[dict]:
        """Récupère les sinistres récents (délégation vers SinistreController)"""
        try:
            from addons.sinistres.controllers.sinistre_controller import SinistreController
            sc = SinistreController()
            sc.set_current_user(self.get_current_user())
            return sc.get_sinistres_recents(limit)
        except Exception as e:
            self.handle_error(e)
            return []

    def get_mission_by_numero(self, numero: str) -> Optional[dict]:
        """Récupère une mission par son numéro"""
        try:
            mission = self.service.get_mission_by_numero(numero)
            if mission:
                return self._serialize_mission(mission)
            return None
        except Exception as e:
            self.handle_error(e)
            return None

    def get_statistiques_expert(self, expert_id: int) -> Dict[str, Any]:
        """Récupère les statistiques d'un expert"""
        try:
            return self.service.get_statistiques(expert_id)
        except Exception as e:
            self.handle_error(e)
            return {}

    def get_sinistre(self, sinistre_id: int) -> Optional[LometaSinistre]:
        """Récupère un sinistre par son ID"""
        try:
            from addons.sinistres.models.sinistre import LometaSinistre
            return self.session.query(LometaSinistre).filter(
                LometaSinistre.id == sinistre_id,
                LometaSinistre.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_avocats(self, actifs_only: bool = True) -> List[dict]:
        """Récupère la liste des avocats"""
        try:
            return self.service.get_avocats(actifs_only=actifs_only)
        except Exception as e:
            self.handle_error(e)
            return []

    def get_avocat(self, avocat_id: int) -> Optional[dict]:
        """Récupère un avocat par ID"""
        try:
            return self.service.get_avocat(avocat_id)
        except Exception as e:
            self.handle_error(e)
            return None

    def get_documents_by_expertise(self, expertise_id: int) -> List[dict]:
        """Récupère tous les documents GED liés à une expertise"""
        try:
            return self.service.get_documents_by_expertise(expertise_id)
        except Exception as e:
            self.handle_error(e)
            return []

    def ajouter_document_expertise(self, expertise_id: int, document_id: int, type_lien: str) -> bool:
        """Lie un document GED à une expertise"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            result = self.service.ajouter_document_expertise(
                expertise_id=expertise_id,
                document_id=document_id,
                type_lien=type_lien,
                utilisateur_id=self.get_current_user_id()
            )
            if result:
                self.handle_success("Document lié à l'expertise")
            return result
        except Exception as e:
            self.handle_error(e)
            return False

    def supprimer_document_expertise(self, document_expertise_id: int) -> bool:
        """Supprime la liaison document ↔ expertise"""
        try:
            result = self.service.supprimer_document_expertise(document_expertise_id)
            if result:
                self.handle_success("Liaison supprimée")
            return result
        except Exception as e:
            self.handle_error(e)
            return False

    def get_statistiques_expertises(self, sinistre_id: Optional[int] = None) -> dict:
        """Récupère les statistiques des expertises"""
        try:
            return self.service.get_statistiques_expertises(sinistre_id)
        except Exception as e:
            self.handle_error(e)
            return {}

    def creer_avocat(self, data: Dict[str, Any]) -> Optional[dict]:
        """Crée un avocat dans le référentiel"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return None
            
            data['created_by'] = self.get_current_user_id()
            avocat = self.service.creer_avocat(data)
            if avocat:
                self.handle_success(f"Avocat {avocat.nom} créé")
                return self.get_avocat(avocat.id)
            return None
        except Exception as e:
            self.handle_error(e)
            return None

    def update_avocat(self, avocat_id: int, data: Dict[str, Any]) -> Optional[dict]:
        """Met à jour un avocat"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return None
            
            data['updated_by'] = self.get_current_user_id()
            avocat = self.service.update_avocat(avocat_id, data)
            if avocat:
                self.handle_success("Avocat mis à jour")
                return self.get_avocat(avocat.id)
            return None
        except Exception as e:
            self.handle_error(e)
            return None

    def toggle_avocat(self, avocat_id: int, actif: bool) -> bool:
        """Active/désactive un avocat"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            result = self.service.toggle_avocat(avocat_id, actif)
            if result:
                self.handle_success("Avocat activé" if actif else "Avocat désactivé")
            return result
        except Exception as e:
            self.handle_error(e)
            return False

    def get_experts_by_zone(self, zone: str) -> List[dict]:
        """Récupère les experts actifs intervenant dans une zone géographique"""
        try:
            experts = self.service.get_experts_by_zone(zone)
            return [self._serialize_expert(e) for e in experts]
        except Exception as e:
            self.handle_error(e)
            return []