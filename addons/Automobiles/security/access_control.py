# addons/Automobiles/security/access_control.py
"""
Système de contrôle d'accès pour le module Automobiles
"""

from enum import Enum
from typing import List, Set, Optional, Any
from functools import wraps


# ============================================================================
# 1. DÉFINITION DES RÔLES
# ============================================================================

class Role(str, Enum):
    """Rôles utilisateurs"""
    ADMIN = "admin"
    MANAGER = "manager"
    AGENT = "agent"
    USER = "user"
    GUEST = "guest"
    
    @classmethod
    def get_hierarchy(cls):
        return {
            cls.ADMIN: 100,
            cls.MANAGER: 80,
            cls.AGENT: 60,
            cls.USER: 40,
            cls.GUEST: 0
        }
    
    def level(self) -> int:
        return self.get_hierarchy().get(self, 0)


# ============================================================================
# 2. DÉFINITION DES PERMISSIONS
# ============================================================================

class Permissions:
    """Permissions disponibles dans le module Automobiles"""
    
    # Permissions des contacts
    CONTACT_VIEW = "contact_view"
    CONTACT_ADD = "contact_add"
    CONTACT_EDIT = "contact_edit"
    CONTACT_DELETE = "contact_delete"
    CONTACT_EXPORT = "contact_export"
    CONTACT_IMPORT = "contact_import"
    
    # Permissions des véhicules
    VEHICLE_VIEW = "vehicle_view"
    VEHICLE_ADD = "vehicle_add"
    VEHICLE_EDIT = "vehicle_edit"
    VEHICLE_DELETE = "vehicle_delete"
    VEHICLE_EXPORT = "vehicle_export"
    
    # Permissions des contrats
    CONTRACT_VIEW = "contract_view"
    CONTRACT_ADD = "contract_add"
    CONTRACT_EDIT = "contract_edit"
    CONTRACT_DELETE = "contract_delete"
    CONTRACT_RENEW = "contract_renew"
    CONTRACT_EXPORT = "contract_export"
    
    # Permissions des paiements
    PAYMENT_VIEW = "payment_view"
    PAYMENT_ADD = "payment_add"
    PAYMENT_EDIT = "payment_edit"
    PAYMENT_DELETE = "payment_delete"
    PAYMENT_EXPORT = "payment_export"
    
    # Permissions des flottes
    FLEET_VIEW = "fleet_view"
    FLEET_ADD = "fleet_add"
    FLEET_EDIT = "fleet_edit"
    FLEET_DELETE = "fleet_delete"
    FLEET_EXPORT = "fleet_export"
    
    # Permissions des rapports
    REPORT_VIEW = "report_view"
    REPORT_GENERATE = "report_generate"
    REPORT_EXPORT = "report_export"
    
    # Permissions d'audit
    AUDIT_VIEW = "audit_view"
    AUDIT_EXPORT = "audit_export"


# ============================================================================
# 3. MAPPING DES PERMISSIONS PAR RÔLE
# ============================================================================

ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permissions.CONTACT_VIEW,
        Permissions.CONTACT_ADD,
        Permissions.CONTACT_EDIT,
        Permissions.CONTACT_DELETE,
        Permissions.CONTACT_EXPORT,
        Permissions.CONTACT_IMPORT,
        Permissions.VEHICLE_VIEW,
        Permissions.VEHICLE_ADD,
        Permissions.VEHICLE_EDIT,
        Permissions.VEHICLE_DELETE,
        Permissions.VEHICLE_EXPORT,
        Permissions.CONTRACT_VIEW,
        Permissions.CONTRACT_ADD,
        Permissions.CONTRACT_EDIT,
        Permissions.CONTRACT_DELETE,
        Permissions.CONTRACT_RENEW,
        Permissions.CONTRACT_EXPORT,
        Permissions.PAYMENT_VIEW,
        Permissions.PAYMENT_ADD,
        Permissions.PAYMENT_EDIT,
        Permissions.PAYMENT_DELETE,
        Permissions.PAYMENT_EXPORT,
        Permissions.FLEET_VIEW,
        Permissions.FLEET_ADD,
        Permissions.FLEET_EDIT,
        Permissions.FLEET_DELETE,
        Permissions.FLEET_EXPORT,
        Permissions.REPORT_VIEW,
        Permissions.REPORT_GENERATE,
        Permissions.REPORT_EXPORT,
        Permissions.AUDIT_VIEW,
        Permissions.AUDIT_EXPORT,
    ],
    Role.MANAGER: [
        Permissions.CONTACT_VIEW,
        Permissions.CONTACT_ADD,
        Permissions.CONTACT_EDIT,
        Permissions.CONTACT_EXPORT,
        Permissions.VEHICLE_VIEW,
        Permissions.VEHICLE_ADD,
        Permissions.VEHICLE_EDIT,
        Permissions.VEHICLE_EXPORT,
        Permissions.CONTRACT_VIEW,
        Permissions.CONTRACT_ADD,
        Permissions.CONTRACT_EDIT,
        Permissions.CONTRACT_RENEW,
        Permissions.CONTRACT_EXPORT,
        Permissions.PAYMENT_VIEW,
        Permissions.PAYMENT_ADD,
        Permissions.PAYMENT_EDIT,
        Permissions.PAYMENT_EXPORT,
        Permissions.FLEET_VIEW,
        Permissions.FLEET_ADD,
        Permissions.FLEET_EDIT,
        Permissions.FLEET_EXPORT,
        Permissions.REPORT_VIEW,
        Permissions.REPORT_GENERATE,
        Permissions.REPORT_EXPORT,
    ],
    Role.AGENT: [
        Permissions.CONTACT_VIEW,
        Permissions.CONTACT_ADD,
        Permissions.CONTACT_EDIT,
        Permissions.VEHICLE_VIEW,
        Permissions.VEHICLE_ADD,
        Permissions.VEHICLE_EDIT,
        Permissions.CONTRACT_VIEW,
        Permissions.CONTRACT_ADD,
        Permissions.CONTRACT_EDIT,
        Permissions.CONTRACT_RENEW,
        Permissions.PAYMENT_VIEW,
        Permissions.PAYMENT_ADD,
        Permissions.FLEET_VIEW,
    ],
    Role.USER: [
        Permissions.CONTACT_VIEW,
        Permissions.VEHICLE_VIEW,
        Permissions.CONTRACT_VIEW,
        Permissions.PAYMENT_VIEW,
        Permissions.FLEET_VIEW,
    ],
    Role.GUEST: [],
}


# ============================================================================
# 4. SECURITY MANAGER
# ============================================================================

class SecurityManager:
    """Gestionnaire des permissions"""
    
    @staticmethod
    def has_permission(user_role, permission) -> bool:
        """
        Vérifie si un rôle a une permission spécifique.
        
        Args:
            user_role: Le rôle de l'utilisateur (str ou Role)
            permission: La permission à vérifier
            
        Returns:
            True si l'utilisateur a la permission, False sinon
        """
        if not user_role:
            return False
        
        # Convertir en Role si c'est une chaîne
        if isinstance(user_role, str):
            try:
                user_role = Role(user_role)
            except ValueError:
                return False
        
        allowed_permissions = ROLE_PERMISSIONS.get(user_role, [])
        return permission in allowed_permissions
    
    @staticmethod
    def has_any_permission(user_role, permissions: List[str]) -> bool:
        """Vérifie si l'utilisateur a au moins une des permissions"""
        return any(SecurityManager.has_permission(user_role, p) for p in permissions)
    
    @staticmethod
    def has_all_permissions(user_role, permissions: List[str]) -> bool:
        """Vérifie si l'utilisateur a toutes les permissions"""
        return all(SecurityManager.has_permission(user_role, p) for p in permissions)
    
    @staticmethod
    def get_permissions(user_role) -> List[str]:
        """Retourne toutes les permissions d'un rôle"""
        if isinstance(user_role, str):
            try:
                user_role = Role(user_role)
            except ValueError:
                return []
        
        return ROLE_PERMISSIONS.get(user_role, [])
    
    @staticmethod
    def filter_by_role(query, user_role, user_id=None, owner_field="created_by_id"):
        """
        Filtre une requête selon le rôle de l'utilisateur.
        
        Args:
            query: La requête SQLAlchemy à filtrer
            user_role: Le rôle de l'utilisateur
            user_id: L'ID de l'utilisateur (pour les agents)
            owner_field: Le champ qui identifie le propriétaire
            
        Returns:
            La requête filtrée
        """
        if not user_role:
            return query
        
        if isinstance(user_role, str):
            try:
                user_role = Role(user_role)
            except ValueError:
                return query
        
        # Les admins voient tout
        if user_role == Role.ADMIN:
            return query
        
        # Les agents ne voient que leurs propres données
        if user_role == Role.AGENT and user_id:
            return query.filter(getattr(query.column_descriptions[0]['entity'], owner_field) == user_id)
        
        return query


# ============================================================================
# 5. DÉCORATEUR POUR LA VÉRIFICATION DES PERMISSIONS
# ============================================================================

def require_permission(permission: str):
    """
    Décorateur pour vérifier les permissions dans les méthodes.
    
    Utilisation:
        @require_permission(Permissions.CONTACT_EDIT)
        def edit_contact(self, contact_id):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            user_role = getattr(self, 'user_role', None)
            if not user_role:
                raise PermissionError("Utilisateur non authentifié")
            
            if not SecurityManager.has_permission(user_role, permission):
                raise PermissionError(
                    f"Permission {permission} requise pour cette action"
                )
            
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def require_any_permission(permissions: List[str]):
    """
    Décorateur pour vérifier qu'au moins une permission est accordée.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            user_role = getattr(self, 'user_role', None)
            if not user_role:
                raise PermissionError("Utilisateur non authentifié")
            
            if not SecurityManager.has_any_permission(user_role, permissions):
                raise PermissionError(
                    f"Une des permissions {permissions} est requise"
                )
            
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# 6. CONTEXTE DE SÉCURITÉ
# ============================================================================

class SecurityContext:
    """Contexte de sécurité pour une session utilisateur"""
    
    def __init__(self, user_id: int, role):
        self.user_id = user_id
        self.role = role
        self._permissions = SecurityManager.get_permissions(role)
    
    @classmethod
    def from_user(cls, user):
        """Crée un contexte depuis un objet utilisateur"""
        return cls(
            user_id=user.id,
            role=user.role
        )
    
    def can(self, permission: str) -> bool:
        """Vérifie si l'utilisateur a une permission"""
        return permission in self._permissions
    
    def can_any(self, permissions: List[str]) -> bool:
        """Vérifie si l'utilisateur a au moins une permission"""
        return any(p in self._permissions for p in permissions)
    
    def can_all(self, permissions: List[str]) -> bool:
        """Vérifie si l'utilisateur a toutes les permissions"""
        return all(p in self._permissions for p in permissions)