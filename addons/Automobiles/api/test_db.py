# addons/Automobiles/api/test_db.py - Version corrigée
"""
Script de test pour la base de données
"""

import sys
import os
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from addons.Automobiles.api.database import init_db, SessionLocal, engine
from addons.Automobiles.api import models_db
from addons.Automobiles.api.config import settings


def test_connection():
    """Test 1: Vérifier la connexion à la base de données"""
    print("\n" + "="*50)
    print("TEST 1: CONNEXION À LA BASE DE DONNÉES")
    print("="*50)
    
    try:
        # Tester la connexion avec une méthode compatible SQLite
        with engine.connect() as conn:
            # Pour SQLite, utiliser une méthode différente
            # Méthode 1: Vérifier que la connexion est active
            if conn.closed:
                print("❌ Connexion fermée")
                return False
            
            # Méthode 2: Exécuter une requête simple avec text()
            from sqlalchemy import text
            result = conn.execute(text("SELECT 1"))
            row = result.fetchone()
            
            if row and row[0] == 1:
                print("✅ Connexion à la base de données réussie")
                return True
            else:
                print("❌ La requête de test a échoué")
                return False
                
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False


def test_init_db():
    """Test 2: Initialiser la base de données"""
    print("\n" + "="*50)
    print("TEST 2: INITIALISATION DE LA BASE DE DONNÉES")
    print("="*50)
    
    try:
        init_db()
        print("✅ Base de données initialisée avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur d'initialisation: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tables_creation():
    """Test 3: Vérifier que les tables ont été créées"""
    print("\n" + "="*50)
    print("TEST 3: VÉRIFICATION DES TABLES")
    print("="*50)
    
    expected_tables = [
        'organizations',
        'offices', 
        'users',
        'user_tokens',
        'certificate_types',
        'certificate_variants',
        'productions',
        'certificates',
        'production_logs',
        'stocks',
        'tariff_matrices'
    ]
    
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"📋 Tables trouvées: {len(tables)}")
        for table in expected_tables:
            if table in tables:
                print(f"   ✅ {table}")
            else:
                print(f"   ❌ {table} - MANQUANTE")
        
        all_exist = all(table in tables for table in expected_tables)
        return all_exist
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_default_data():
    """Test 4: Vérifier les données par défaut"""
    print("\n" + "="*50)
    print("TEST 4: DONNÉES PAR DÉFAUT")
    print("="*50)
    
    db = SessionLocal()
    try:
        # Vérifier les types d'attestation
        cert_types = db.query(models_db.CertificateType).all()
        print(f"\n📄 Types d'attestation ({len(cert_types)}):")
        for ct in cert_types:
            print(f"   - {ct.code}: {ct.name}")
        
        # Vérifier les variantes
        variants = db.query(models_db.CertificateVariant).all()
        print(f"\n🎨 Variantes ({len(variants)}):")
        for v in variants:
            print(f"   - {v.code}: {v.name}")
        
        # Vérifier la relation entre types et variantes
        if len(cert_types) > 0 and len(variants) > 0:
            print("\n✅ Données par défaut correctement initialisées")
            return True
        else:
            print("\n❌ Données par défaut incomplètes")
            return False
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_crud_operations():
    """Test 5: Tester les opérations CRUD de base"""
    print("\n" + "="*50)
    print("TEST 5: OPÉRATIONS CRUD")
    print("="*50)
    
    db = SessionLocal()
    try:
        # 5.1 Tester la récupération des types d'attestation
        cert_type = db.query(models_db.CertificateType).filter(
            models_db.CertificateType.code == "cima"
        ).first()
        
        if cert_type:
            print(f"✅ Récupération type attestation: {cert_type.code} - {cert_type.name}")
        else:
            print("❌ Type attestation non trouvé")
        
        # 5.2 Tester la récupération des variantes
        variant = db.query(models_db.CertificateVariant).filter(
            models_db.CertificateVariant.code == "JAUNE"
        ).first()
        
        if variant:
            print(f"✅ Récupération variante: {variant.code} - {variant.name}")
        else:
            print("❌ Variante non trouvée")
        
        # 5.3 Tester l'insertion d'une organisation (test)
        test_org = models_db.Organization(
            code="TEST_ORG",
            name="Organisation de Test",
            email="test@test.com"
        )
        db.add(test_org)
        db.commit()
        
        # Vérifier l'insertion
        saved_org = db.query(models_db.Organization).filter(
            models_db.Organization.code == "TEST_ORG"
        ).first()
        
        if saved_org:
            print(f"✅ Insertion organisation: {saved_org.name}")
            # Nettoyer - supprimer l'organisation de test
            db.delete(saved_org)
            db.commit()
        else:
            print("❌ Échec de l'insertion")
        
        return cert_type is not None and variant is not None
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_inspect_database():
    """Test 6: Inspecter le contenu de la base de données"""
    print("\n" + "="*50)
    print("TEST 6: INSPECTION DE LA BASE DE DONNÉES")
    print("="*50)
    
    db = SessionLocal()
    try:
        # Compter les enregistrements dans chaque table
        tables_count = {
            'certificate_types': db.query(models_db.CertificateType).count(),
            'certificate_variants': db.query(models_db.CertificateVariant).count(),
            'organizations': db.query(models_db.Organization).count(),
            'offices': db.query(models_db.Office).count(),
            'users': db.query(models_db.User).count(),
            'productions': db.query(models_db.Production).count(),
            'certificates': db.query(models_db.Certificate).count(),
        }
        
        print("\n📊 Statistiques des tables:")
        for table, count in tables_count.items():
            print(f"   - {table}: {count} enregistrement(s)")
        
        # Vérifier les relations
        if tables_count['certificate_types'] >= 2:
            print("\n✅ Structure de base de données OK")
            return True
        else:
            print("\n⚠️ Structure de base de données incomplète")
            return False
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_file_storage():
    """Test 7: Vérifier les dossiers de stockage"""
    print("\n" + "="*50)
    print("TEST 7: DOSSIERS DE STOCKAGE")
    print("="*50)
    
    storage_path = Path(settings.STORAGE_PATH)
    db_path = Path("./addons/Automobiles/api/storage")
    
    print(f"📁 Dossier de stockage: {storage_path}")
    print(f"📁 Dossier de la base: {db_path.absolute()}")
    
    try:
        # Vérifier ou créer les dossiers
        storage_path.mkdir(parents=True, exist_ok=True)
        db_path.mkdir(parents=True, exist_ok=True)
        
        if storage_path.exists():
            print(f"✅ Dossier de stockage: {storage_path}")
        else:
            print(f"❌ Dossier de stockage introuvable")
            return False
        
        if db_path.exists():
            print(f"✅ Dossier de la base: {db_path}")
            db_file = db_path / "asac.db"
            if db_file.exists():
                size = db_file.stat().st_size
                print(f"✅ Base de données: {db_file.name} ({size:,} octets)")
            else:
                print(f"⚠️ Base de données non encore créée")
        else:
            print(f"❌ Dossier de la base introuvable")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def run_all_tests():
    """Exécute tous les tests"""
    print("\n" + "🚀" * 20)
    print("   TEST DE L'API ASAC - ÉTAPE 3 (BASE DE DONNÉES)")
    print("🚀" * 20)
    
    results = []
    
    # Exécuter les tests
    results.append(("Connexion DB", test_connection()))
    results.append(("Initialisation DB", test_init_db()))
    results.append(("Création tables", test_tables_creation()))
    results.append(("Données par défaut", test_default_data()))
    results.append(("Opérations CRUD", test_crud_operations()))
    results.append(("Inspection DB", test_inspect_database()))
    results.append(("Stockage fichiers", test_file_storage()))
    
    # Résumé
    print("\n" + "="*50)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*50)
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        if result:
            passed += 1
        print(f"{status} - {name}")
    
    print(f"\n🎯 Score: {passed}/{len(results)} tests réussis")
    
    if passed == len(results):
        print("\n🎉 FÉLICITATIONS! TOUS LES TESTS SONT PASSÉS!")
        print("   L'API ASAC est prête pour l'étape suivante.")
    else:
        print("\n⚠️ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
    
    return passed == len(results)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)