"""
Test : vérifie que les permissions UI sont bien appliquées
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from addons.sinistres.services.permission_service import PermissionService
from addons.sinistres.security.permissions_helper import PermissionsUI
from addons.Paramètres.models.models import User


class FakeUser:
    def __init__(self, user_id, username, role):
        self.id = user_id
        self.username = username
        self.role = role


def test_permissions_par_role():
    """Vérifie ce que chaque rôle peut faire"""
    svc = PermissionService()
    
    # Rôles à tester
    roles = ['admin', 'gestionnaire', 'responsable', 'comptable', 'expert', 'lecteur']
    
    actions = [
        ('evaluation', 'CREATE'),
        ('evaluation', 'VALIDATE'),
        ('reglement', 'CREATE'),
        ('reglement', 'VALIDATE'),
        ('reglement', 'PAY'),
        ('expertise', 'CREATE'),
        ('expertise', 'VALIDATE'),
    ]
    
    print("\n" + "=" * 80)
    print(f"{'Rôle':<15} | " + " | ".join(f"{r}.{a[:3]}" for r, a in actions))
    print("=" * 80)
    
    for role in roles:
        user = FakeUser(1, f"user_{role}", role)
        
        # Simuler temporairement : attribuer ce rôle au user 1
        svc.revoke_all_roles(1) if hasattr(svc, 'revoke_all_roles') else None
        # (ou utiliser un user réel)
        
        perms = []
        for res, act in actions:
            has = svc.has_permission(1, res, act)
            perms.append("✅" if has else "❌")
        
        print(f"{role:<15} | " + " | ".join(f"  {p}  " for p in perms))


if __name__ == "__main__":
    test_permissions_par_role()