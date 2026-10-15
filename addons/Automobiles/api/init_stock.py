# addons/Automobiles/api/init_stock.py
"""
Script pour initialiser l'organisation, le bureau et le stock d'attestations
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from addons.Automobiles.api.database import SessionLocal, init_db
from addons.Automobiles.api import models_db


def init_organization_and_office():
    """Initialise l'organisation et le bureau par défaut"""
    print("🔧 Initialisation de l'organisation et du bureau...")
    
    db = SessionLocal()
    try:
        # 1. Créer l'organisation ACTIVA
        org = db.query(models_db.Organization).filter(
            models_db.Organization.code == "ACTIVA"
        ).first()
        
        if not org:
            org = models_db.Organization(
                code="ACTIVA",
                name="ACTIVA Assurances",
                address="Douala, Cameroun",
                email="contact@activa.cm",
                telephone="+237 690 000 000",
                is_active=True,
                is_sanctioned=False
            )
            db.add(org)
            db.flush()
            print(f"✅ Organisation créée: {org.name} (code: {org.code})")
        else:
            print(f"⚠️ Organisation déjà existante: {org.name}")
        
        # 2. Créer le bureau principal
        office = db.query(models_db.Office).filter(
            models_db.Office.code == "AG-DLA-001"
        ).first()
        
        if not office:
            office = models_db.Office(
                code="AG-DLA-001",
                name="Agence Principale Douala",
                address="Douala, Boulevard de la Liberté",
                email="agence@activa.cm",
                telephone="+237 690 000 001",
                organization_id=org.id,
                is_master_office=True,
                is_active=True
            )
            db.add(office)
            db.flush()
            print(f"✅ Bureau créé: {office.name} (code: {office.code})")
        else:
            print(f"⚠️ Bureau déjà existant: {office.name}")
        
        db.commit()
        return org, office
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
        return None, None
    finally:
        db.close()


def init_stock():
    """Initialise le stock d'attestations"""
    print("\n🔧 Initialisation du stock d'attestations...")
    
    db = SessionLocal()
    try:
        # Récupérer l'organisation
        org = db.query(models_db.Organization).filter(
            models_db.Organization.code == "ACTIVA"
        ).first()
        
        if not org:
            print("❌ Organisation ACTIVA non trouvée")
            return
        
        # Récupérer le bureau
        office = db.query(models_db.Office).filter(
            models_db.Office.code == "AG-DLA-001"
        ).first()
        
        # Récupérer les variantes d'attestation
        variants = db.query(models_db.CertificateVariant).all()
        
        if not variants:
            print("❌ Aucune variante d'attestation trouvée")
            return
        
        print(f"\n📋 Variantes trouvées: {len(variants)}")
        
        for variant in variants:
            # Vérifier si le stock existe déjà
            existing = db.query(models_db.Stock).filter(
                models_db.Stock.organization_id == org.id,
                models_db.Stock.certificate_variant_id == variant.id,
                models_db.Stock.office_id == (office.id if office else None)
            ).first()
            
            if not existing:
                stock = models_db.Stock(
                    organization_id=org.id,
                    certificate_variant_id=variant.id,
                    office_id=office.id if office else None,
                    quantity=1000,  # Stock initial
                    used_quantity=0
                )
                db.add(stock)
                print(f"✅ Stock créé pour {variant.name}: 1000 attestations")
            else:
                print(f"⚠️ Stock déjà existant pour {variant.name}")
        
        db.commit()
        print("\n✅ Initialisation du stock terminée!")
        
        # Afficher un résumé
        print("\n📊 RÉSUMÉ DU STOCK:")
        stocks = db.query(models_db.Stock).filter(
            models_db.Stock.organization_id == org.id
        ).all()
        
        for stock in stocks:
            variant = db.query(models_db.CertificateVariant).filter(
                models_db.CertificateVariant.id == stock.certificate_variant_id
            ).first()
            print(f"   - {variant.name}: {stock.available_quantity} disponibles sur {stock.quantity}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def init_user():
    """Initialise un utilisateur de test"""
    print("\n🔧 Initialisation de l'utilisateur de test...")
    
    db = SessionLocal()
    try:
        # Récupérer le bureau
        office = db.query(models_db.Office).filter(
            models_db.Office.code == "AG-DLA-001"
        ).first()
        
        if not office:
            print("❌ Bureau non trouvé")
            return
        
        # Vérifier si l'utilisateur existe
        user = db.query(models_db.User).filter(
            models_db.User.username == "asac_admin"
        ).first()
        
        if not user:
            import json
            user = models_db.User(
                username="asac_admin",
                email="admin@asac.cm",
                full_name="Administrateur ASAC",
                app_key="TEST_APP_KEY_2024",
                office_id=office.id,
                is_active=True,
                permissions=json.dumps(["create", "createOnBehalf"])
            )
            db.add(user)
            db.flush()
            print(f"✅ Utilisateur créé: {user.username}")
            print(f"   Clé applicative: {user.app_key}")
        else:
            print(f"⚠️ Utilisateur déjà existant: {user.username}")
        
        db.commit()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "🚀" * 20)
    print("   INITIALISATION DE L'API ASAC")
    print("🚀" * 20)
    
    # 1. Initialiser la base de données
    print("\n📦 Étape 1: Initialisation de la base de données...")
    init_db()
    
    # 2. Créer l'organisation et le bureau
    print("\n📦 Étape 2: Création de l'organisation et du bureau...")
    org, office = init_organization_and_office()
    
    if org and office:
        # 3. Créer l'utilisateur
        print("\n📦 Étape 3: Création de l'utilisateur...")
        init_user()
        
        # 4. Initialiser le stock
        print("\n📦 Étape 4: Initialisation du stock...")
        init_stock()
        
        print("\n" + "="*50)
        print("✅ INITIALISATION COMPLÈTE!")
        print("="*50)
        print("\n📋 Informations de connexion:")
        print(f"   URL: http://localhost:8001/api/v1/auth/tokens/app-key")
        print(f"   Paramètres: app_key=TEST_APP_KEY_2024&username=asac_admin")
        print("\n💡 Pour tester l'API:")
        print("   curl -X POST 'http://localhost:8001/api/v1/auth/tokens/app-key?app_key=TEST_APP_KEY_2024&username=asac_admin'")
    else:
        print("\n❌ Échec de l'initialisation")