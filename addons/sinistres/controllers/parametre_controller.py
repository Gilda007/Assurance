"""
Contrôleur des paramètres applicatifs
"""
from PySide6.QtCore import Signal
from typing import Optional, List, Dict, Any

from addons.sinistres.controllers.controleur_base import BaseController
from addons.sinistres.services.parametre_service import ParametreService


class ParametreController(BaseController):
    """Contrôleur pour la gestion des paramètres"""
    
    parametres_loaded = Signal(list)
    parametre_updated = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.service = ParametreService()
    
    def get_all_parametres(self, categorie: str = None) -> List[dict]:
        """Récupère tous les paramètres"""
        try:
            params = self.service.get_all_parametres(categorie)
            result = [self._serialize(p) for p in params]
            self.parametres_loaded.emit(result)
            return result
        except Exception as e:
            self.handle_error(e)
            return []
    
    def get_parametres_by_categorie(self, categorie: str) -> List[dict]:
        """Récupère les paramètres d'une catégorie"""
        try:
            params = self.service.get_parametres_by_categorie(categorie)
            return [self._serialize(p) for p in params]
        except Exception as e:
            self.handle_error(e)
            return []
    
    def get_valeur(self, code: str, default: Any = None) -> Any:
        """Récupère la valeur typée d'un paramètre"""
        try:
            return self.service.get_valeur(code, default)
        except Exception as e:
            self.handle_error(e)
            return default
    
    def set_valeur(self, code: str, valeur: Any) -> bool:
        """Met à jour un paramètre"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            param = self.service.set_valeur(
                code=code,
                valeur=valeur,
                utilisateur_id=self.get_current_user_id()
            )
            if param:
                self.parametre_updated.emit(self._serialize(param))
                self.handle_success(f"Paramètre {code} mis à jour")
                return True
            return False
        except Exception as e:
            self.handle_error(e)
            return False
    
    def creer_parametre(self, data: Dict[str, Any]) -> Optional[dict]:
        """Crée un nouveau paramètre"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return None
            
            param = self.service.creer_parametre(
                data=data,
                utilisateur_id=self.get_current_user_id()
            )
            return self._serialize(param)
        except Exception as e:
            self.handle_error(e)
            return None
    
    def _serialize(self, p) -> dict:
        """Sérialise un paramètre"""
        return {
            'id': p.id,
            'code': p.code,
            'libelle': p.libelle,
            'valeur': p.valeur,
            'type_donnee': p.type_donnee,
            'categorie': p.categorie,
            'description': p.description,
            'ordre_affichage': p.ordre_affichage,
            'is_active': p.is_active,
            'created_at': p.created_at.isoformat() if p.created_at else None,
            'updated_at': p.updated_at.isoformat() if p.updated_at else None,
        }