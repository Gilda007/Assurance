# addons/Automobiles/api/init_users.py
"""
Script pour initialiser les utilisateurs de test
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from addons.Automobiles.api.database import SessionLocal, init_db
from addons.Automobiles.api import models_db
from addons.Automobiles.api.config import settings


def init_test_users():
    """Initialise les utilisateurs de test"""
    print("🔧 Initialisation des utilisateurs de test...")
    
    db = SessionLocal()
    try:
        # Vérifier si des organisations existent
        org = db.query(models_db.Organization).filter(
            models_db.Organization.code == "ACTIVA"
        ).first()
        
        if not org:
            org = models_db.Organization(
                code="ACTIVA",
                name="ACTIVA Assurances",
                email="contact@activa.cm",
                telephone="+237 690 000 000",
                is_active=True
            )
            db.add(org)
            db.flush()
            print(f"✅ Organisation créée: {org.name}")
        
        # Vérifier si des bureaux existent
        office = db.query(models_db.Office).filter(
            models_db.Office.code == "AG-DLA-001"
        ).first()
        
        if not office:
            office = models_db.Office(
                code="AG-DLA-001",
                name="Agence Douala",
                address="Douala, Cameroun",
                organization_id=org.id,
                is_master_office=True,
                is_active=True
            )
            db.add(office)
            db.flush()
            print(f"✅ Bureau créé: {office.name}")
        
        # Créer un utilisateur de test
        user = db.query(models_db.User).filter(
            models_db.User.username == "asac_admin"
        ).first()
        
        if not user:
            user = models_db.User(
                username="asac_admin",
                email="admin@asac.cm",
                full_name="Administrateur ASAC",
                app_key="TEST_APP_KEY_2024",
                office_id=office.id,
                is_active=True,
                permissions='["create", "createOnBehalf"]'
            )
            db.add(user)
            db.flush()
            print(f"✅ Utilisateur créé: {user.username}")
            print(f"   Clé applicative: {user.app_key}")
        else:
            print(f"✅ Utilisateur existant: {user.username}")
            print(f"   Clé applicative: {user.app_key}")
        
        db.commit()
        print("\n📋 Informations de connexion:")
        print(f"   URL: http://{settings.HOST}:{settings.PORT}{settings.API_V1_PREFIX}")
        print(f"   Endpoint: /auth/tokens/app-key")
        print(f"   Paramètres: app_key={user.app_key}&username={user.username}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    init_test_users()