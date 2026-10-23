"""
Contrôleur de gestion des rôles et permissions
"""
import string
from typing import Optional, List, Dict, Any
from PySide6.QtCore import Signal

from addons.sinistres.controllers.controleur_base import BaseController
from addons.sinistres.services.permission_service import PermissionService


class PermissionController(BaseController):
    """Contrôleur RBAC"""
    
    roles_updated = Signal()
    user_role_updated = Signal(int)
    
    def __init__(self):
        super().__init__()
        self.service = PermissionService()
    
    def init_default_roles(self) -> int:
        """Initialise les rôles par défaut"""
        try:
            nb = self.service.init_default_roles()
            self.roles_updated.emit()
            return nb
        except Exception as e:
            self.handle_error(e)
            return 0
    
    def get_all_roles(self) -> List[dict]:
        """Récupère tous les rôles"""
        try:
            roles = self.service.get_all_roles()
            return [self._serialize_role(r) for r in roles]
        except Exception as e:
            self.handle_error(e)
            return []
    
    def assign_role(self, user_id: int, role_code: str) -> bool:
        """Attribue un rôle à un utilisateur"""
        try:
            result = self.service.assign_role(
                user_id, role_code, assigned_by=self.get_current_user_id()
            )
            if result:
                self.user_role_updated.emit(user_id)
            return bool(result)
        except Exception as e:
            self.handle_error(e)
            return False
    
    def revoke_role(self, user_id: int, role_code: str) -> bool:
        """Retire un rôle"""
        try:
            result = self.service.revoke_role(user_id, role_code)
            if result:
                self.user_role_updated.emit(user_id)
            return result
        except Exception as e:
            self.handle_error(e)
            return False
    
    def add_permission_to_role(self, role_code: str, resource: str, action: str) -> bool:
        """Ajoute une permission à un rôle"""
        try:
            result = self.service.add_permission_to_role(role_code, resource, action)
            if result:
                self.roles_updated.emit()
            return result
        except Exception as e:
            self.handle_error(e)
            return False
    
    def remove_permission_from_role(self, role_code: str, resource: str, action: str) -> bool:
        """Retire une permission"""
        try:
            result = self.service.remove_permission_from_role(role_code, resource, action)
            if result:
                self.roles_updated.emit()
            return result
        except Exception as e:
            self.handle_error(e)
            return False

    # ═══════════════════════════════════════════════════════════════════
    # ✅ CRUD RÔLES (à ajouter dans PermissionController)
    # ═══════════════════════════════════════════════════════════════════

    def create_role(self, data: dict) -> Optional[dict]:
        """
        Crée un nouveau rôle.
        
        Args:
            data: dict contenant {'code', 'libelle', 'description', 'niveau'}
        
        Returns:
            dict du rôle créé ou None
        """
        try:
            role = self.service.creer_role({
                'code': data.get('code', '').strip().upper(),
                'libelle': data.get('libelle', '').strip(),
                'description': data.get('description'),
                'niveau': data.get('niveau', 50),
                'created_by': self.get_current_user_id(),
            })
            
            # ✅ Ajouter les permissions si présentes
            permissions = data.get('permissions', [])
            if permissions:
                for p in permissions:
                    if isinstance(p, dict):
                        res = p.get('ressource')
                        act = p.get('action')
                        if res and act:
                            self.service.add_permission_to_role(
                                role.code, res, act
                            )
            
            self.roles_updated.emit()
            return self._serialize_role(role)
        except Exception as e:
            self.handle_error(e)
            return None

    def update_role(self, role_id: int, data: dict) -> Optional[dict]:
        """Met à jour un rôle existant."""
        try:
            from addons.sinistres.models.permissions import LometaRole
            
            # Récupérer le rôle par ID
            role = self.service.session.query(LometaRole).filter_by(id=role_id).first()
            if not role:
                self.error_occurred.emit(f"Rôle ID {role_id} introuvable")
                return None
            
            # Utiliser la méthode du service avec le code
            updated = self.service.update_role(role.code, {
                'libelle': data.get('libelle'),
                'description': data.get('description'),
                'niveau': data.get('niveau'),
            })
            
            if updated:
                self.roles_updated.emit()
                return self._serialize_role(updated)
            return None
        except Exception as e:
            self.handle_error(e)
            return None

    def delete_role(self, role_id: int) -> bool:
        """Supprime un rôle (soft delete)"""
        try:
            # Trouver le rôle par ID
            from addons.sinistres.models.permissions import LometaRole
            role = self.service.session.query(LometaRole).filter_by(id=role_id).first()
            
            if not role:
                return False
            
            result = self.service.supprimer_role(role.code)
            if result:
                self.roles_updated.emit()
            return bool(result)
        except Exception as e:
            self.handle_error(e)
            return False


    def activate_role(self, role_id: int) -> bool:
        """Réactive un rôle"""
        try:
            from addons.sinistres.models.permissions import LometaRole
            role = self.service.session.query(LometaRole).filter_by(id=role_id).first()
            if not role:
                return False
            
            role.est_actif = True
            self.service.session.commit()
            self.roles_updated.emit()
            return True
        except Exception as e:
            self.service.session.rollback()
            self.handle_error(e)
            return False


    def deactivate_role(self, role_id: int) -> bool:
        """Désactive un rôle"""
        try:
            from addons.sinistres.models.permissions import LometaRole
            role = self.service.session.query(LometaRole).filter_by(id=role_id).first()
            if not role:
                return False
            
            if role.est_systeme:
                raise ValueError("Impossible de désactiver un rôle système")
            
            role.est_actif = False
            self.service.session.commit()
            self.roles_updated.emit()
            return True
        except Exception as e:
            self.service.session.rollback()
            self.handle_error(e)
            return False


    def set_role_permissions(self, role_code: str, permissions: list) -> bool:
        """
        Remplace toutes les permissions d'un rôle.
        
        Args:
            role_code: code du rôle
            permissions: liste de dicts [{'ressource': str, 'action': str}]
        
        Returns:
            True si succès
        """
        try:
            role = self.service.get_role(role_code)
            if not role:
                return False
            
            # ✅ Vider les permissions actuelles
            role.permissions.clear()
            self.service.session.flush()
            
            # ✅ Ajouter les nouvelles
            for p in permissions:
                res = p.get('ressource')
                act = p.get('action')
                if res and act:
                    perm_code = f"{role_code}:{res}:{act}"
                    
                    from addons.sinistres.models.permissions import LometaPermission
                    perm = self.service.session.query(LometaPermission).filter(
                        LometaPermission.code == perm_code
                    ).first()
                    
                    if not perm:
                        perm = LometaPermission(
                            code=perm_code,
                            ressource=res,
                            action=act,
                            autorise=True,
                        )
                        self.service.session.add(perm)
                        self.service.session.flush()
                    
                    role.permissions.append(perm)
            
            self.service.session.commit()
            self.roles_updated.emit()
            return True
        except Exception as e:
            self.service.session.rollback()
            self.handle_error(e)
            return False


    def get_all_users(self) -> List[dict]:
        """Récupère tous les utilisateurs (pour l'onglet Utilisateurs)"""
        try:
            # Adapter selon votre modèle User
            from addons.Parametres.models.models import User
            users = self.service.session.query(User).all()
            
            result = []
            for u in users:
                # Récupérer les rôles
                try:
                    roles = self.service.get_user_roles(u.id)
                    roles_list = [
                        {'code': r.code, 'libelle': r.libelle}
                        for r in roles
                    ]
                except Exception:
                    roles_list = []
                
                result.append({
                    'id': u.id,
                    'username': getattr(u, 'username', ''),
                    'nom': getattr(u, 'nom', ''),
                    'prenom': getattr(u, 'prenom', ''),
                    'nom_complet': f"{getattr(u, 'prenom', '')} {getattr(u, 'nom', '')}".strip(),
                    'email': getattr(u, 'email', ''),
                    'est_actif': getattr(u, 'est_actif', True),
                    'roles': roles_list,
                })
            
            return result
        except Exception as e:
            print(f"Erreur get_all_users: {e}")
            return []


    def toggle_user_active(self, user_id: int, active: bool) -> bool:
        """Active/désactive un utilisateur"""
        try:
            from addons.Parametres.models.models import User
            user = self.service.session.query(User).filter_by(id=user_id).first()
            if not user:
                return False
            
            user.est_actif = active
            self.service.session.commit()
            return True
        except Exception as e:
            self.service.session.rollback()
            self.handle_error(e)
            return False


    def reset_user_password(self, user_id: int) -> Optional[str]:
        """
        Réinitialise le mot de passe d'un utilisateur.
        
        Returns:
            Le nouveau mot de passe en clair (à communiquer à l'utilisateur),
            ou None en cas d'erreur.
        """
        try:
            import secrets
            import string
            import bcrypt
            
            # ✅ Générer un mot de passe temporaire sécurisé (12 caractères)
            new_pwd = ''.join(
                secrets.choice(string.ascii_letters + string.digits)
                for _ in range(12)
            )
            
            # ✅ Adapter au modèle User de votre projet
            from addons.Parametres.models.models import User
            user = self.service.session.query(User).filter_by(id=user_id).first()
            if not user:
                return None
            
            # ✅ Hacher avec bcrypt (comme dans votre LoginController)
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(new_pwd.encode('utf-8'), salt)
            
            # ✅ Adapter le nom du champ selon votre modèle :
            #    - 'password_hash' 
            #    - 'mot_de_passe'
            #    - 'password'
            # Décommentez la ligne qui correspond :
            user.password_hash = hashed.decode('utf-8')   # ← si le champ s'appelle password_hash
            # user.mot_de_passe = hashed.decode('utf-8')  # ← si le champ s'appelle mot_de_passe
            # user.password = hashed.decode('utf-8')      # ← si le champ s'appelle password
            
            # Optionnel : forcer le changement au prochain login
            # user.must_change_password = True
            
            self.service.session.commit()
            return new_pwd
        except Exception as e:
            self.service.session.rollback()
            self.handle_error(e)
            return None
    
    def _serialize_role(self, role) -> dict:
        return {
            'id': role.id,
            'code': role.code,
            'libelle': role.libelle,
            'description': role.description,
            'niveau': role.niveau,
            'est_systeme': role.est_systeme,
            'est_actif': role.est_actif,
            'permissions': [
                {'ressource': p.ressource, 'action': p.action}
                for p in (role.permissions or [])
            ],
        }