"""
Service de gestion des permissions (RBAC)
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Set, Any, Tuple
from datetime import datetime

from addons.sinistres.services.base_service import BaseService
from addons.sinistres.models.permissions import (
    LometaRole, LometaPermission, LometaUserRole, role_permissions
)
from addons.sinistres.security.constants import (
    Roles, Actions, Resources, DEFAULT_PERMISSIONS
)


class PermissionService(BaseService):
    """Service RBAC — Gestion des rôles et permissions"""
    
    def __init__(self, session: Session = None):
        super().__init__(session)
        self._cache_permissions = {} 
        self.cache_roles = {}
    
    # ============================================================
    # INITIALISATION
    # ============================================================
    
    def invalidate_cache(self, utilisateur_id: int = None):
        """Invalide le cache des permissions"""
        if utilisateur_id:
            self._cache_permissions.pop(utilisateur_id, None)
            self.cache_roles.pop(utilisateur_id, None)
        else:
            self._cache_permissions.clear()
            self.cache_roles.clear()


    def init_default_roles(self) -> int:
        """Initialise les rôles et permissions par défaut"""
        try:
            nb_crees = 0
            
            for role_code, perms_dict in DEFAULT_PERMISSIONS.items():
                # Créer le rôle
                role = self.session.query(LometaRole).filter(
                    LometaRole.code == role_code
                ).first()
                
                if not role:
                    role = LometaRole(
                        code=role_code,
                        libelle=role_code.capitalize(),
                        niveau=self._get_role_niveau(role_code),
                        est_systeme=True,
                        est_actif=True,
                    )
                    self.session.add(role)
                    self.session.flush()
                    nb_crees += 1
                
                # Créer les permissions
                for ressource, actions in perms_dict.items():
                    for action in actions:
                        perm_code = f"{role_code}:{ressource}:{action}"
                        
                        perm = self.session.query(LometaPermission).filter(
                            LometaPermission.code == perm_code
                        ).first()
                        
                        if not perm:
                            perm = LometaPermission(
                                code=perm_code,
                                ressource=ressource,
                                action=action,
                                autorise=True,
                            )
                            self.session.add(perm)
                            self.session.flush()
                        
                        # Lier si pas déjà fait
                        if perm not in role.permissions:
                            role.permissions.append(perm)
            
            self.session.commit()
            return nb_crees
        except Exception as e:
            self.session.rollback()
            raise e
    
    def _get_role_niveau(self, role_code: str) -> int:
        """Retourne le niveau hiérarchique d'un rôle"""
        niveaux = {
            Roles.ADMIN: 100,
            Roles.RESPONSABLE: 80,
            Roles.GESTIONNAIRE: 60,
            Roles.COMPTABLE: 60,
            Roles.EXPERT: 40,
            Roles.LECTEUR: 10,
        }
        return niveaux.get(role_code, 0)
    
    # ============================================================
    # VÉRIFICATION DES PERMISSIONS
    # ============================================================
    
    def has_permission(
        self,
        utilisateur_id: int,
        resource: str,
        action: str
    ) -> bool:
        """
        Vérifie si un utilisateur a la permission (resource, action)
        """
        try:
            # Récupérer les rôles actifs de l'utilisateur
            user_roles = self.session.query(LometaUserRole).filter(
                LometaUserRole.utilisateur_id == utilisateur_id,
                LometaUserRole.est_actif == True,
                LometaUserRole.date_fin.is_(None) | (LometaUserRole.date_fin > datetime.utcnow())
            ).all()
            
            if not user_roles:
                return False
            
            # Vérifier chaque rôle
            for ur in user_roles:
                role = ur.role
                if role and role.est_actif:
                    if role.has_permission(resource, action):
                        return True
            
            return False
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_user_permissions(self, utilisateur_id: int) -> Dict[str, Set[str]]:
        """
        Retourne toutes les permissions d'un utilisateur
        Format: {resource: {actions}}
        """
        try:
            user_roles = self.session.query(LometaUserRole).filter(
                LometaUserRole.utilisateur_id == utilisateur_id,
                LometaUserRole.est_actif == True,
            ).all()
            
            permissions = {}
            
            for ur in user_roles:
                if not ur.role or not ur.role.est_actif:
                    continue
                for perm in ur.role.permissions:
                    if perm.autorise:
                        permissions.setdefault(perm.ressource, set()).add(perm.action)
            
            return permissions
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_user_roles(self, utilisateur_id: int) -> List[LometaRole]:
        """Récupère les rôles actifs d'un utilisateur"""
        try:
            user_roles = self.session.query(LometaUserRole).filter(
                LometaUserRole.utilisateur_id == utilisateur_id,
                LometaUserRole.est_actif == True,
            ).all()
            return [ur.role for ur in user_roles if ur.role]
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # ATTRIBUTION DE RÔLES
    # ============================================================
    
    def assign_role(
        self,
        utilisateur_id: int,
        role_code: str,
        assigned_by: int = None,
        societe: str = None,
        branche: str = None,
    ) -> Optional[LometaUserRole]:
        """Attribue un rôle à un utilisateur"""
        try:
            # Vérifier que le rôle existe
            role = self.session.query(LometaRole).filter(
                LometaRole.code == role_code,
                LometaRole.est_actif == True,
            ).first()
            
            if not role:
                raise ValueError(f"Rôle {role_code} introuvable")
            
            # Vérifier s'il y a déjà une attribution active
            existant = self.session.query(LometaUserRole).filter(
                LometaUserRole.utilisateur_id == utilisateur_id,
                LometaUserRole.role_id == role.id,
                LometaUserRole.est_actif == True,
            ).first()
            
            if existant:
                return existant
            
            # Créer l'association
            user_role = LometaUserRole(
                utilisateur_id=utilisateur_id,
                role_id=role.id,
                societe=societe,
                branche=branche,
                date_debut=datetime.utcnow(),
                est_actif=True,
                created_by=assigned_by,
            )
            
            self.session.add(user_role)
            self.session.commit()
            return user_role
        except Exception as e:
            self.session.rollback()
            raise e
    
    def revoke_role(self, utilisateur_id: int, role_code: str) -> bool:
        """Retire un rôle à un utilisateur"""
        try:
            role = self.session.query(LometaRole).filter(
                LometaRole.code == role_code
            ).first()
            
            if not role:
                return False
            
            user_role = self.session.query(LometaUserRole).filter(
                LometaUserRole.utilisateur_id == utilisateur_id,
                LometaUserRole.role_id == role.id,
                LometaUserRole.est_actif == True,
            ).first()
            
            if user_role:
                user_role.est_actif = False
                user_role.date_fin = datetime.utcnow()
                self.session.commit()
                return True
            
            return False
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # CRUD RÔLES
    # ============================================================
    
    def get_all_roles(self) -> List[LometaRole]:
        """Récupère tous les rôles"""
        return self.session.query(LometaRole).filter(
            LometaRole.est_actif == True
        ).order_by(LometaRole.niveau.desc()).all()
    
    def get_role(self, role_code: str) -> Optional[LometaRole]:
        return self.session.query(LometaRole).filter(
            LometaRole.code == role_code
        ).first()
    
    def creer_role(self, data: Dict[str, Any]) -> LometaRole:
        """Crée un nouveau rôle"""
        try:
            role = LometaRole(
                code=data['code'],
                libelle=data['libelle'],
                description=data.get('description'),
                niveau=data.get('niveau', 0),
                est_systeme=False,
                est_actif=True,
                created_by=data.get('created_by'),
            )
            self.session.add(role)
            self.session.commit()
            return role
        except Exception as e:
            self.session.rollback()
            raise e
    
    def update_role(self, role_code: str, data: Dict[str, Any]) -> Optional[LometaRole]:
        """Met à jour un rôle"""
        try:
            role = self.get_role(role_code)
            if not role:
                return None
            
            if role.est_systeme:
                # Ne pas modifier un rôle système
                raise ValueError(f"Le rôle {role_code} est système et ne peut pas être modifié")
            
            for key, value in data.items():
                if hasattr(role, key) and key not in ('id', 'code', 'est_systeme'):
                    setattr(role, key, value)
            
            self.session.commit()
            return role
        except Exception as e:
            self.session.rollback()
            raise e
    
    def supprimer_role(self, role_code: str) -> bool:
        """Supprime (soft delete) un rôle"""
        try:
            role = self.get_role(role_code)
            if not role:
                return False
            
            if role.est_systeme:
                raise ValueError(f"Impossible de supprimer le rôle système {role_code}")
            
            role.est_actif = False
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # CRUD PERMISSIONS
    # ============================================================
    
    def has_any_permission(
        self,
        utilisateur_id: int,
        permissions: List[Tuple[str, str]],
    ) -> bool:
        """
        Vérifie si l'utilisateur a AU MOINS UNE des permissions listées.
        
        Usage :
            a_acces = service.has_any_permission(user_id, [
                ('sinistre', 'READ'),
                ('sinistre', 'CREATE'),
            ])
        """
        for resource, action in permissions:
            if self.has_permission(utilisateur_id, resource, action):
                return True
        return False


    def has_all_permissions(
        self,
        utilisateur_id: int,
        permissions: List[Tuple[str, str]],
    ) -> bool:
        """Vérifie si l'utilisateur a TOUTES les permissions listées."""
        for resource, action in permissions:
            if not self.has_permission(utilisateur_id, resource, action):
                return False
        return True


    def get_accessible_pages(self, utilisateur_id: int) -> Set[str]:
        """
        Retourne la liste des pages accessibles à l'utilisateur.
        Utilisé par la Sidebar pour masquer les pages non autorisées.
        
        Convention : une page est accessible si l'utilisateur a au moins
        UNE permission sur la ressource principale.
        """
        PAGE_RESOURCES = {
            'dashboard': [('sinistre', 'READ')],
            'nouveau': [('sinistre', 'CREATE')],
            'recherche': [('sinistre', 'READ')],
            'expertises': [('expertise', 'READ')],
            'evaluations': [('evaluation', 'READ')],
            'reglements': [('reglement', 'READ')],
            'recours': [('recours', 'READ')],
            'referentiels': [('referentiel', 'READ')],
            'parametres': [('utilisateur', 'READ'), ('role', 'READ')],
            'comptabilite': [('ecriture', 'READ'), ('comptabilite', 'READ')],

            # ✅ AJOUTER ces pages
            'lots':         [('reglement', 'READ')],
            'documents':    [('document', 'READ'), ('sinistre', 'READ')],
            'audit':        [('sinistre', 'READ'), ('utilisateur', 'READ')],
            'roles':        [('role', 'READ'), ('utilisateur', 'READ')],
        }
        
        accessible = set()
        for page, perms in PAGE_RESOURCES.items():
            if self.has_any_permission(utilisateur_id, perms):
                accessible.add(page)
        return accessible

    def add_permission_to_role(
        self,
        role_code: str,
        resource: str,
        action: str,
    ) -> bool:
        """Ajoute une permission à un rôle"""
        try:
            role = self.get_role(role_code)
            if not role:
                return False
            
            perm_code = f"{role_code}:{resource}:{action}"
            
            perm = self.session.query(LometaPermission).filter(
                LometaPermission.code == perm_code
            ).first()
            
            if not perm:
                perm = LometaPermission(
                    code=perm_code,
                    ressource=resource,
                    action=action,
                    autorise=True,
                )
                self.session.add(perm)
                self.session.flush()
            
            if perm not in role.permissions:
                role.permissions.append(perm)
                self.session.commit()
            
            return True
        except Exception as e:
            self.session.rollback()
            raise e
    
    def remove_permission_from_role(
        self,
        role_code: str,
        resource: str,
        action: str,
    ) -> bool:
        """Retire une permission d'un rôle"""
        try:
            role = self.get_role(role_code)
            if not role:
                return False
            
            perm_code = f"{role_code}:{resource}:{action}"
            
            perm = self.session.query(LometaPermission).filter(
                LometaPermission.code == perm_code
            ).first()
            
            if perm and perm in role.permissions:
                role.permissions.remove(perm)
                self.session.commit()
                return True
            
            return False
        except Exception as e:
            self.session.rollback()
            raise e