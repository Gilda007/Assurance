"""
Décorateurs de contrôle d'accès
"""
from functools import wraps
from typing import Callable

from addons.sinistres.services.permission_service import PermissionService


def require_permission(resource: str, action: str):
    """
    Décorateur pour vérifier une permission avant d'exécuter une méthode.
    
    Usage:
        @require_permission(Resources.SINISTRE, Actions.CREATE)
        def creer_sinistre(self, data):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Récupérer l'ID de l'utilisateur courant (depuis le contrôleur)
            user_id = self.get_current_user_id()
            
            if not user_id:
                raise PermissionError("Aucun utilisateur connecté")
            
            # Vérifier la permission
            perm_service = PermissionService()
            has_perm = perm_service.has_permission(user_id, resource, action)
            
            if not has_perm:
                raise PermissionError(
                    f"Permission refusée : {action} sur {resource} "
                    f"(utilisateur #{user_id})"
                )
            
            return func(self, *args, **kwargs)
        
        return wrapper
    return decorator


def require_role(*role_codes: str):
    """
    Décorateur pour vérifier un rôle spécifique.
    
    Usage:
        @require_role(Roles.ADMIN, Roles.RESPONSABLE)
        def valider_sinistre(self, sinistre_id):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            user_id = self.get_current_user_id()
            
            if not user_id:
                raise PermissionError("Aucun utilisateur connecté")
            
            perm_service = PermissionService()
            user_roles = perm_service.get_user_roles(user_id)
            user_role_codes = [r.code for r in user_roles]
            
            if not any(code in user_role_codes for code in role_codes):
                raise PermissionError(
                    f"Rôle requis : {role_codes} "
                    f"(utilisateur a : {user_role_codes})"
                )
            
            return func(self, *args, **kwargs)
        
        return wrapper
    return decorator