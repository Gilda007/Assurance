"""
Contrôleur des référentiels - Interface entre l'UI et ReferentielService
"""
from PySide6.QtCore import Signal
from typing import Optional, List, Dict, Any

from addons.sinistres.controllers.controleur_base import BaseController
from addons.sinistres.services.referentiel_service import ReferentielService
from addons.sinistres.models.referentiel import LometaReferentiel


class ReferentielController(BaseController):
    """Contrôleur pour la gestion des référentiels"""
    
    # Signaux spécifiques
    referentiel_created = Signal(dict)
    referentiel_updated = Signal(dict)
    referentiel_deleted = Signal(int)
    referentiel_list_updated = Signal(list)
    
    def __init__(self):
        super().__init__()
        self.service = ReferentielService()
    
    # ============================================================
    # CRUD
    # ============================================================
    
    def creer_referentiel(self, data: Dict[str, Any]) -> Optional[dict]:
        """Crée un nouveau référentiel"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return None
            
            data['created_by'] = self.get_current_user_id()
            referentiel = self.service.creer_referentiel(data)
            result = self._serialize_referentiel(referentiel)
            
            self.referentiel_created.emit(result)
            self.handle_success(f"Référentiel {referentiel.code} créé avec succès")
            return result
            
        except Exception as e:
            self.handle_error(e)
            return None
    
    def get_referentiel(self, referentiel_id: int) -> Optional[dict]:
        """Récupère un référentiel par son ID"""
        try:
            referentiel = self.service.get_referentiel(referentiel_id)
            if referentiel:
                return self._serialize_referentiel(referentiel)
            return None
        except Exception as e:
            self.handle_error(e)
            return None
    
    def get_referentiel_by_code(self, famille: str, code: str) -> Optional[dict]:
        """Récupère un référentiel par sa famille et son code"""
        try:
            referentiel = self.service.get_referentiel_by_code(famille, code)
            if referentiel:
                return self._serialize_referentiel(referentiel)
            return None
        except Exception as e:
            self.handle_error(e)
            return None
    
    def get_referentiels_by_famille(self, famille: str) -> List[dict]:
        """Récupère tous les référentiels d'une famille"""
        try:
            referentiels = self.service.get_referentiels_by_famille(famille)
            result = [self._serialize_referentiel(r) for r in referentiels]
            self.referentiel_list_updated.emit(result)
            return result
        except Exception as e:
            self.handle_error(e)
            return []
    
    def update_referentiel(self, referentiel_id: int, data: Dict[str, Any]) -> bool:
        """Met à jour un référentiel"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            data['updated_by'] = self.get_current_user_id()
            referentiel = self.service.update_referentiel(referentiel_id, data)
            
            if referentiel:
                self.referentiel_updated.emit(self._serialize_referentiel(referentiel))
                self.handle_success("Référentiel mis à jour avec succès")
                return True
            
            self.error_occurred.emit("Référentiel non trouvé")
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    def desactiver_referentiel(self, referentiel_id: int) -> bool:
        """Désactive un référentiel"""
        try:
            result = self.service.desactiver_referentiel(referentiel_id)
            if result:
                self.referentiel_deleted.emit(referentiel_id)
                self.handle_success("Référentiel désactivé avec succès")
            return result
        except Exception as e:
            self.handle_error(e)
            return False
    
    # ============================================================
    # IMPORTS / EXPORTS
    # ============================================================
    
    def export_referentiels(self, famille: str = None) -> List[dict]:
        """Exporte les référentiels vers une liste de dictionnaires"""
        try:
            return self.service.export_to_list(famille)
        except Exception as e:
            self.handle_error(e)
            return []
    
    def import_referentiels(self, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Importe des référentiels depuis une liste de dictionnaires"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return {'crees': 0, 'mis_a_jour': 0, 'erreurs': ['Utilisateur non connecté']}
            
            result = self.service.import_from_list(data_list, self.get_current_user_id())
            self.handle_success(f"Import terminé: {result['crees']} créés, {result['mis_a_jour']} mis à jour")
            return result
        except Exception as e:
            self.handle_error(e)
            return {'crees': 0, 'mis_a_jour': 0, 'erreurs': [str(e)]}
    
    # ============================================================
    # DONNÉES INITIALES
    # ============================================================
    
    def init_donnees_initiales(self) -> Dict[str, Any]:
        """Initialise les données des référentiels"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return {'crees': 0, 'erreurs': ['Utilisateur non connecté']}
            
            result = self.service.init_donnees_initiales(self.get_current_user_id())
            self.handle_success(f"Données initiales créées: {result['crees']} référentiels")
            return result
        except Exception as e:
            self.handle_error(e)
            return {'crees': 0, 'erreurs': [str(e)]}
    
    # ============================================================
    # MÉTHODES PRIVÉES
    # ============================================================
    
    def _serialize_referentiel(self, referentiel: LometaReferentiel) -> dict:
        """Sérialise un référentiel en dictionnaire"""
        return {
            'id': referentiel.id,
            'famille': referentiel.famille,
            'code': referentiel.code,
            'libelle': referentiel.libelle,
            'description': referentiel.description,
            'date_effet': referentiel.date_effet.isoformat() if referentiel.date_effet else None,
            'date_fin': referentiel.date_fin.isoformat() if referentiel.date_fin else None,
            'societe': referentiel.societe,
            'branche': referentiel.branche,
            'valeur': referentiel.valeur,
            'donnees_supplementaires': referentiel.donnees_supplementaires,
            'est_actif': referentiel.est_actif,
            'est_obsolete': referentiel.est_obsolete,
            'version': referentiel.version,
            'created_at': referentiel.created_at.isoformat() if referentiel.created_at else None,
            'created_by': referentiel.created_by,
            'updated_at': referentiel.updated_at.isoformat() if referentiel.updated_at else None,
            'updated_by': referentiel.updated_by,
            'is_active': referentiel.is_active,
        }