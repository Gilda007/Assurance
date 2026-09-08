"""
Contrôleur des expertises - Interface entre l'UI et ExpertiseService
"""
from PySide6.QtCore import Signal
from typing import Optional, List, Dict, Any

from addons.sinistres.controllers.controleur_base import BaseController
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
    # MÉTHODE PRIVÉE
    # ============================================================
    
    def _serialize_mission(self, mission) -> dict:
        """Sérialise une mission en dictionnaire"""
        # Récupérer le nom de l'expert
        expert_nom = None
        if mission.expert_id:
            expert = self.service.get_user(mission.expert_id)
            if expert:
                expert_nom = expert.full_name or expert.username
        
        return {
            'id': mission.id,
            'numero_mission': mission.numero_mission,
            'sinistre_id': mission.sinistre_id,
            'expert_id': mission.expert_id,
            'expert_nom': expert_nom or mission.expert_nom,
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