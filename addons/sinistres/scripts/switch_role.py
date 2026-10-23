"""
Change le rôle d'un utilisateur.
Usage : python -m addons.sinistres.scripts.switch_role <username> <role_code>

Exemples :
  python -m addons.sinistres.scripts.switch_role Admin admin
  python -m addons.sinistres.scripts.switch_role damsk gestionnaire
  python -m addons.sinistres.scripts.switch_role marie responsable
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.database import SessionLocal
from addons.Parametres.models.models import User
from addons.sinistres.services.permission_service import PermissionService


# Rôles valides
VALID_ROLES = ['admin', 'gestionnaire', 'responsable', 'comptable', 'expert', 'lecteur', 'test']


def main():
    if len(sys.argv) != 3:
        print("Usage : python -m addons.sinistres.scripts.switch_role <username> <role_code>")
        print()
        print("Rôles disponibles :")
        for r in VALID_ROLES:
            print(f"  - {r}")
        sys.exit(1)
    
    username = sys.argv[1]
    new_role = sys.argv[2].lower()
    
    if new_role not in VALID_ROLES:
        print(f"❌ Rôle invalide : '{new_role}'")
        print(f"   Rôles valides : {', '.join(VALID_ROLES)}")
        sys.exit(1)
    
    session = SessionLocal()
    try:
        # Trouver l'utilisateur
        user = session.query(User).filter(User.username == username).first()
        if not user:
            print(f"❌ Utilisateur '{username}' non trouvé")
            sys.exit(1)
        
        print(f"👤 Utilisateur : {user.username} (ID: {user.id})")
        
        service = PermissionService(session)
        
        # Révoquer tous les rôles actuels
        current_roles = service.get_user_roles(user.id)
        if current_roles:
            print(f"📋 Rôles actuels : {[r.code for r in current_roles]}")
            for r in current_roles:
                service.revoke_role(user.id, r.code)
                print(f"   ❌ Rôle révoqué : {r.code}")
        else:
            print("📋 Aucun rôle actuel")
        
        # Attribuer le nouveau
        service.assign_role(user.id, new_role)
        print(f"   ✅ Rôle attribué : {new_role}")
        
        # Vérifier
        print()
        print("🔍 Vérification :")
        new_roles = service.get_user_roles(user.id)
        print(f"   Rôles actifs : {[r.code for r in new_roles]}")
        pages = service.get_accessible_pages(user.id)
        print(f"   Pages accessibles ({len(pages)}) :")
        for p in sorted(pages):
            print(f"      ✅ {p}")
        
        print()
        print(f"✅ {username} a maintenant le rôle '{new_role}'")
        print("   Relancez l'application pour voir les changements.")
    
    finally:
        session.close()


if __name__ == "__main__":
    main()