"""
Test rapide des permissions RBAC
Usage : python -m addons.sinistres.tests.test_permissions_quick
"""
import sys
from pathlib import Path

# Ajouter la racine au PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.database import SessionLocal
from addons.Parametres.models.models import User
from addons.sinistres.services.permission_service import PermissionService


def main():
    print("\n" + "=" * 70)
    print("🧪 TEST DES PERMISSIONS RBAC")
    print("=" * 70)
    
    session = SessionLocal()
    try:
        # ============================================================
        # 1. Initialiser les rôles par défaut
        # ============================================================
        print("\n📌 Étape 1 : Initialisation des rôles par défaut")
        service = PermissionService(session)
        nb = service.init_default_roles()
        print(f"   ✅ {nb} rôle(s) créé(s) ou mis à jour")
        
        # ============================================================
        # 2. Lister les rôles
        # ============================================================
        print("\n📌 Étape 2 : Rôles en base")
        roles = service.get_all_roles()
        for r in roles:
            nb_perm = len(r.permissions)
            print(f"   • {r.code:15} | {r.libelle:25} | {nb_perm} permission(s)")
        
        # ============================================================
        # 3. Prendre un utilisateur existant
        # ============================================================
        print("\n📌 Étape 3 : Utilisateur de test")
        user = session.query(User).filter(User.is_active == True).first()
        if not user:
            print("   ⚠️  Aucun utilisateur actif — créez-en un avant")
            return
        
        print(f"   👤 Utilisateur : {user.username} (ID: {user.id})")
        
        # ============================================================
        # 4. Vérifier les permissions AVANT attribution
        # ============================================================
        print("\n📌 Étape 4 : Permissions AVANT attribution de rôle")
        print(f"   sinistre.CREATE    : {service.has_permission(user.id, 'sinistre', 'CREATE')}")
        print(f"   sinistre.READ      : {service.has_permission(user.id, 'sinistre', 'READ')}")
        print(f"   evaluation.VALIDATE: {service.has_permission(user.id, 'evaluation', 'VALIDATE')}")
        
        # ============================================================
        # 5. Attribuer un rôle "gestionnaire"
        # ============================================================
        print("\n📌 Étape 5 : Attribution du rôle 'gestionnaire'")
        service.assign_role(user.id, 'admin')
        service.invalidate_cache(user.id)   # ⚠️ Vider le cache
        print(f"   ✅ Rôle attribué")
        
        # ============================================================
        # 6. Vérifier les permissions APRÈS
        # ============================================================
        print("\n📌 Étape 6 : Permissions APRÈS attribution")
        print(f"   sinistre.CREATE    : {service.has_permission(user.id, 'sinistre', 'CREATE')}  (attendu : True)")
        print(f"   sinistre.READ      : {service.has_permission(user.id, 'sinistre', 'READ')}    (attendu : True)")
        print(f"   sinistre.DELETE    : {service.has_permission(user.id, 'sinistre', 'DELETE')}  (attendu : False)")
        print(f"   evaluation.VALIDATE: {service.has_permission(user.id, 'evaluation', 'VALIDATE')}  (attendu : False)")
        
        # ============================================================
        # 7. Tester l'accès aux pages
        # ============================================================
        print("\n📌 Étape 7 : Pages accessibles")
        pages = service.get_accessible_pages(user.id)
        for p in sorted(pages):
            print(f"   ✅ {p}")
        
        # ============================================================
        # 8. Attribuer aussi "responsable"
        # ============================================================
        print("\n📌 Étape 8 : Ajout du rôle 'responsable'")
        service.assign_role(user.id, 'responsable')
        service.invalidate_cache(user.id)
        
        print(f"   evaluation.VALIDATE: {service.has_permission(user.id, 'evaluation', 'VALIDATE')}  (attendu : True)")
        
        # ============================================================
        # 9. Révocation
        # ============================================================
        print("\n📌 Étape 9 : Révocation du rôle 'responsable'")
        service.revoke_role(user.id, 'responsable')
        service.invalidate_cache(user.id)
        
        print(f"   evaluation.VALIDATE: {service.has_permission(user.id, 'evaluation', 'VALIDATE')}  (attendu : False)")
        
        # ============================================================
        # 10. Résumé final
        # ============================================================
        print("\n📌 Étape 10 : Résumé des rôles de l'utilisateur")
        roles_user = service.get_user_roles(user.id)
        for r in roles_user:
            print(f"   • {r.code} — {r.libelle}")
        
        print("\n" + "=" * 70)
        print("✅ TEST TERMINÉ")
        print("=" * 70 + "\n")
    
    finally:
        session.close()


if __name__ == "__main__":
    main()