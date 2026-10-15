"""
Tests unitaires RBAC
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from addons.sinistres.services.permission_service import PermissionService
from addons.sinistres.security.constants import Roles, Actions, Resources


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture(scope="module")
def service():
    """Service de permissions avec rôles initialisés"""
    svc = PermissionService()
    svc.init_default_roles()
    return svc


@pytest.fixture
def test_user(db_session):
    """Utilisateur de test"""
    from addons.Paramètres.models.models import User
    
    user = User(
        username="rbac_test_user",
        email="rbac@test.com",
        full_name="RBAC Test",
        role="agent",
        is_active=True,
    )
    user.set_password("Test@123456")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    yield user
    
    # Nettoyage
    db_session.delete(user)
    db_session.commit()


# ============================================================
# TESTS
# ============================================================

class TestInitRoles:
    """Tests d'initialisation des rôles"""
    
    def test_init_creates_roles(self, service):
        roles = service.get_all_roles()
        codes = [r.code for r in roles]
        
        assert 'admin' in codes
        assert 'gestionnaire' in codes
        assert 'responsable' in codes
        assert 'comptable' in codes
        assert 'expert' in codes
        assert 'lecteur' in codes
    
    def test_admin_has_all_permissions(self, service):
        admin_role = service.get_role('admin')
        # Admin doit avoir au moins 70 permissions
        assert len(admin_role.permissions) >= 70


class TestAdminPermissions:
    """Tests des permissions Admin"""
    
    def test_admin_can_do_everything(self, service, test_user):
        service.assign_role(test_user.id, 'admin')
        service.invalidate_cache(test_user.id)
        
        # Admin peut tout faire
        assert service.has_permission(test_user.id, 'sinistre', 'CREATE')
        assert service.has_permission(test_user.id, 'sinistre', 'DELETE')
        assert service.has_permission(test_user.id, 'reglement', 'PAY')
        assert service.has_permission(test_user.id, 'role', 'CREATE')
        assert service.has_permission(test_user.id, 'utilisateur', 'DELETE')


class TestGestionnairePermissions:
    """Tests des permissions Gestionnaire"""
    
    def test_gestionnaire_can_create_sinistre(self, service, test_user):
        service.assign_role(test_user.id, 'gestionnaire')
        service.invalidate_cache(test_user.id)
        
        assert service.has_permission(test_user.id, 'sinistre', 'CREATE') is True
        assert service.has_permission(test_user.id, 'sinistre', 'READ') is True
        assert service.has_permission(test_user.id, 'sinistre', 'UPDATE') is True
    
    def test_gestionnaire_cannot_delete(self, service, test_user):
        service.assign_role(test_user.id, 'gestionnaire')
        service.invalidate_cache(test_user.id)
        
        assert service.has_permission(test_user.id, 'sinistre', 'DELETE') is False
    
    def test_gestionnaire_cannot_validate(self, service, test_user):
        service.assign_role(test_user.id, 'gestionnaire')
        service.invalidate_cache(test_user.id)
        
        assert service.has_permission(test_user.id, 'evaluation', 'VALIDATE') is False


class TestResponsablePermissions:
    """Tests des permissions Responsable"""
    
    def test_responsable_can_validate(self, service, test_user):
        service.assign_role(test_user.id, 'responsable')
        service.invalidate_cache(test_user.id)
        
        assert service.has_permission(test_user.id, 'evaluation', 'VALIDATE') is True
        assert service.has_permission(test_user.id, 'sinistre', 'CLOSE') is True
    
    def test_responsable_cannot_create(self, service, test_user):
        service.assign_role(test_user.id, 'responsable')
        service.invalidate_cache(test_user.id)
        
        assert service.has_permission(test_user.id, 'sinistre', 'CREATE') is False


class TestComptablePermissions:
    """Tests des permissions Comptable"""
    
    def test_comptable_can_pay(self, service, test_user):
        service.assign_role(test_user.id, 'comptable')
        service.invalidate_cache(test_user.id)
        
        assert service.has_permission(test_user.id, 'reglement', 'PAY') is True
        assert service.has_permission(test_user.id, 'reglement', 'CREATE') is True
    
    def test_comptable_cannot_create_sinistre(self, service, test_user):
        service.assign_role(test_user.id, 'comptable')
        service.invalidate_cache(test_user.id)
        
        assert service.has_permission(test_user.id, 'sinistre', 'CREATE') is False


class TestMultipleRoles:
    """Tests avec plusieurs rôles"""
    
    def test_multiple_roles_union_permissions(self, service, test_user):
        """Avoir 2 rôles = union des permissions"""
        service.assign_role(test_user.id, 'gestionnaire')
        service.assign_role(test_user.id, 'comptable')
        service.invalidate_cache(test_user.id)
        
        # Du gestionnaire
        assert service.has_permission(test_user.id, 'sinistre', 'CREATE') is True
        # Du comptable
        assert service.has_permission(test_user.id, 'reglement', 'PAY') is True
        # Ni l'un ni l'autre
        assert service.has_permission(test_user.id, 'role', 'CREATE') is False


class TestRoleRevocation:
    """Tests de révocation"""
    
    def test_revoke_removes_permissions(self, service, test_user):
        service.assign_role(test_user.id, 'gestionnaire')
        service.invalidate_cache(test_user.id)
        assert service.has_permission(test_user.id, 'sinistre', 'CREATE') is True
        
        service.revoke_role(test_user.id, 'gestionnaire')
        service.invalidate_cache(test_user.id)
        assert service.has_permission(test_user.id, 'sinistre', 'CREATE') is False


class TestAccessiblePages:
    """Tests des pages accessibles"""
    
    def test_admin_accesses_all_pages(self, service, test_user):
        service.assign_role(test_user.id, 'admin')
        service.invalidate_cache(test_user.id)
        
        pages = service.get_accessible_pages(test_user.id)
        assert 'dashboard' in pages
        assert 'nouveau' in pages
        assert 'expertises' in pages
        assert 'evaluations' in pages
        assert 'reglements' in pages
        assert 'recours' in pages
        assert 'roles' in pages
        assert 'parametres' in pages
    
    def test_expert_limited_pages(self, service, test_user):
        service.assign_role(test_user.id, 'expert')
        service.invalidate_cache(test_user.id)
        
        pages = service.get_accessible_pages(test_user.id)
        # Expert voit les sinistres et expertises
        assert 'dashboard' in pages
        assert 'expertises' in pages
        # Mais PAS la gestion des rôles
        assert 'roles' not in pages
        assert 'reglements' not in pages


class TestNoRole:
    """Tests sans rôle attribué"""
    
    def test_user_without_role_has_no_permission(self, service, test_user):
        # Aucun rôle attribué
        assert service.has_permission(test_user.id, 'sinistre', 'READ') is False
        assert service.has_permission(test_user.id, 'sinistre', 'CREATE') is False
        assert len(service.get_user_roles(test_user.id)) == 0