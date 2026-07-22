# test_rc_calculation.py
"""
Script de test pour la méthode get_rc_premium_from_matrix
Vérifie les calculs pour Essence et Diesel avec différentes puissances
"""

import sys
import os
from pathlib import Path

# ✅ Ajouter le chemin du projet correctement
# Le projet est dans /home/fearless/Documents/Assurance
project_root = Path(__file__).parent.parent.parent.parent  # Remonte jusqu'à Assurance/
print(f"📁 Project root: {project_root}")

# Ajouter le chemin du projet au PYTHONPATH
sys.path.insert(0, str(project_root))

# Vérifier que les modules sont accessibles
print(f"🔍 PYTHONPATH: {sys.path[0]}")

try:
    from core.database import SessionLocal
    from addons.Automobiles.controllers.automobile_controller import VehicleController
    print("✅ Modules importés avec succès")
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("\n📋 Pour corriger, exécutez depuis le dossier du projet:")
    print("   cd /home/fearless/Documents/Assurance")
    print("   python -m addons.Automobiles.tests.test_rc_calculation")
    sys.exit(1)


def test_rc_calculation():
    """Teste la méthode get_rc_premium_from_matrix"""
    
    print("=" * 70)
    print("🧪 TEST DE get_rc_premium_from_matrix")
    print("=" * 70)
    
    # Créer une session
    session = SessionLocal()
    controller = VehicleController(session)
    
    # Paramètres de test
    cie_id = 1  # ID d'une compagnie existante
    zone = "A"
    categorie = "VP01"  # Catégorie du véhicule
    
    # Types d'énergie à tester
    energies = [
        ("Essence", "Essence"),
        ("Diesel", "Diesel"),
        ("SEE", "Essence"),
        ("SED", "Diesel"),
    ]
    
    # Puissances à tester
    cv_values = [2, 4, 6, 7, 10, 14, 16, 20, 25, 30]
    
    # Résultats attendus (approximatifs)
    expected_results = {
        "essence": {
            2: {"tranche": 1, "range": "≤ 2 CV"},
            4: {"tranche": 2, "range": "3-6 CV"},
            6: {"tranche": 2, "range": "3-6 CV"},
            7: {"tranche": 3, "range": "7-10 CV"},
            10: {"tranche": 3, "range": "7-10 CV"},
            14: {"tranche": 4, "range": "11-14 CV"},
            16: {"tranche": 5, "range": "15-23 CV"},
            20: {"tranche": 5, "range": "15-23 CV"},
            25: {"tranche": 6, "range": "> 23 CV"},
            30: {"tranche": 6, "range": "> 23 CV"},
        },
        "diesel": {
            2: {"tranche": 1, "range": "≤ 2 CV"},
            4: {"tranche": 2, "range": "3-4 CV"},
            6: {"tranche": 3, "range": "5-7 CV"},
            7: {"tranche": 3, "range": "5-7 CV"},
            10: {"tranche": 4, "range": "8-10 CV"},
            14: {"tranche": 5, "range": "11-16 CV"},
            16: {"tranche": 5, "range": "11-16 CV"},
            20: {"tranche": 6, "range": "> 16 CV"},
            25: {"tranche": 6, "range": "> 16 CV"},
            30: {"tranche": 6, "range": "> 16 CV"},
        }
    }
    
    print("\n📋 Paramètres de test:")
    print(f"   Compagnie ID: {cie_id}")
    print(f"   Zone: {zone}")
    print(f"   Catégorie: {categorie}")
    print(f"   Avec remorque: False\n")
    
    # ============================================================
    # TEST 1: VÉRIFICATION DES TRANCHES PAR ÉNERGIE
    # ============================================================
    print("=" * 70)
    print("📊 TEST 1: VÉRIFICATION DES TRANCHES")
    print("=" * 70)
    
    test_passed = 0
    test_failed = 0
    
    for energie_label, energie_code in energies:
        print(f"\n🔹 Énergie: {energie_label} ({energie_code})")
        print("-" * 50)
        print(f"{'CV':<6} {'Tranche':<10} {'Plage attendue':<20} {'RC':<12} {'Statut':<10}")
        print("-" * 50)
        
        for cv in cv_values:
            try:
                result = controller.get_rc_premium_from_matrix(
                    cie_id=cie_id,
                    zone_saisie=zone,
                    categorie=categorie,
                    energie=energie_code,
                    cv_saisi=cv,
                    avec_remorque=False,
                    code_tarif=None
                )
                
                is_diesel = energie_code.lower() in ['diesel', 'sed']
                energy_key = "diesel" if is_diesel else "essence"
                
                expected = expected_results[energy_key].get(cv, {})
                expected_tranche = expected.get("tranche", "?")
                expected_range = expected.get("range", "?")
                
                actual_tranche = result.get("tranche", 0)
                
                # Vérifier que la tranche est correcte
                is_correct = actual_tranche == expected_tranche
                status = "✅" if is_correct else "❌"
                
                if is_correct:
                    test_passed += 1
                else:
                    test_failed += 1
                
                print(f"{cv:<6} {actual_tranche:<10} {expected_range:<20} {result.get('rc', 0):<12.0f} {status:<10}")
                
            except Exception as e:
                print(f"{cv:<6} {'ERR':<10} {'Erreur':<20} {'-':<12} ❌")
                test_failed += 1
                print(f"   Erreur: {e}")
    
    # ============================================================
    # TEST 2: COMPARAISON ESSENCE VS DIESEL
    # ============================================================
    print("\n" + "=" * 70)
    print("📊 TEST 2: COMPARAISON ESSENCE vs DIESEL")
    print("=" * 70)
    print(f"\n{'CV':<6} {'Essence':<15} {'Diesel':<15} {'Différence':<15} {'% Diff':<10}")
    print("-" * 70)
    
    for cv in cv_values:
        try:
            # Essence
            result_essence = controller.get_rc_premium_from_matrix(
                cie_id=cie_id,
                zone_saisie=zone,
                categorie=categorie,
                energie="Essence",
                cv_saisi=cv,
                avec_remorque=False
            )
            
            # Diesel
            result_diesel = controller.get_rc_premium_from_matrix(
                cie_id=cie_id,
                zone_saisie=zone,
                categorie=categorie,
                energie="Diesel",
                cv_saisi=cv,
                avec_remorque=False
            )
            
            rc_essence = result_essence.get("rc", 0)
            rc_diesel = result_diesel.get("rc", 0)
            diff = rc_diesel - rc_essence
            pct_diff = (diff / rc_essence * 100) if rc_essence > 0 else 0
            
            print(f"{cv:<6} {rc_essence:<15.0f} {rc_diesel:<15.0f} {diff:<15.0f} {pct_diff:<10.1f}%")
            
        except Exception as e:
            print(f"{cv:<6} {'ERR':<15} {'ERR':<15} {'ERR':<15} {'ERR':<10}")
    
    # ============================================================
    # TEST 3: VÉRIFICATION AVEC REMORQUE
    # ============================================================
    print("\n" + "=" * 70)
    print("📊 TEST 3: AVEC REMORQUE")
    print("=" * 70)
    
    cv_test = 10
    print(f"\nTest avec CV = {cv_test}, Énergie = Essence")
    print("-" * 50)
    
    try:
        result_without = controller.get_rc_premium_from_matrix(
            cie_id=cie_id,
            zone_saisie=zone,
            categorie=categorie,
            energie="Essence",
            cv_saisi=cv_test,
            avec_remorque=False
        )
        
        result_with = controller.get_rc_premium_from_matrix(
            cie_id=cie_id,
            zone_saisie=zone,
            categorie=categorie,
            energie="Essence",
            cv_saisi=cv_test,
            avec_remorque=True
        )
        
        print(f"   Sans remorque: RC = {result_without.get('rc', 0):.0f} FCFA")
        print(f"   Avec remorque:  RC = {result_with.get('rc', 0):.0f} FCFA")
        print(f"   Différence:     {result_with.get('rc', 0) - result_without.get('rc', 0):.0f} FCFA")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # ============================================================
    # TEST 4: VÉRIFICATION DE LA VIGNETTE
    # ============================================================
    print("\n" + "=" * 70)
    print("📊 TEST 4: VÉRIFICATION DE LA VIGNETTE")
    print("=" * 70)
    print(f"\n{'CV':<6} {'Vignette (FCFA)':<20} {'Attendu':<15} {'Statut':<10}")
    print("-" * 60)
    
    expected_vignette = {
        2: 30000,
        5: 30000,
        7: 30000,
        8: 50000,
        10: 50000,
        13: 50000,
        14: 75000,
        18: 75000,
        20: 75000,
        21: 200000,
        25: 200000,
        30: 200000,
    }
    
    for cv, expected in expected_vignette.items():
        try:
            result = controller.get_rc_premium_from_matrix(
                cie_id=cie_id,
                zone_saisie=zone,
                categorie=categorie,
                energie="Essence",
                cv_saisi=cv,
                avec_remorque=False
            )
            
            vignette = result.get("vignette", 0)
            is_correct = vignette == expected
            status = "✅" if is_correct else "❌"
            
            print(f"{cv:<6} {vignette:<20.0f} {expected:<15} {status:<10}")
            
            if not is_correct:
                test_failed += 1
            else:
                test_passed += 1
                
        except Exception as e:
            print(f"{cv:<6} {'ERR':<20} {expected:<15} ❌")
            test_failed += 1
    
    # ============================================================
    # RÉSUMÉ DES TESTS
    # ============================================================
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 70)
    
    total_tests = test_passed + test_failed
    success_rate = (test_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n   ✅ Tests réussis: {test_passed}")
    print(f"   ❌ Tests échoués: {test_failed}")
    print(f"   📊 Taux de succès: {success_rate:.1f}%")
    
    if test_failed == 0:
        print("\n🎉 TOUS LES TESTS ONT RÉUSSI !")
    else:
        print(f"\n⚠️ {test_failed} test(s) ont échoué. Veuillez vérifier les résultats.")
    
    print("\n" + "=" * 70)
    
    # Fermer la session
    session.close()
    
    return test_failed == 0


def test_detailed_case():
    """
    Test détaillé d'un cas spécifique où Essence et Diesel diffèrent
    """
    print("\n" + "=" * 70)
    print("📊 TEST DÉTAILLÉ - CAS SPÉCIFIQUE")
    print("=" * 70)
    
    session = SessionLocal()
    controller = VehicleController(session)
    
    test_cases = [
        {"cv": 7, "energie": "Essence", "expected_tranche": 3},
        {"cv": 7, "energie": "Diesel", "expected_tranche": 3},
        {"cv": 8, "energie": "Essence", "expected_tranche": 3},
        {"cv": 8, "energie": "Diesel", "expected_tranche": 4},
        {"cv": 11, "energie": "Essence", "expected_tranche": 4},
        {"cv": 11, "energie": "Diesel", "expected_tranche": 5},
        {"cv": 17, "energie": "Essence", "expected_tranche": 5},
        {"cv": 17, "energie": "Diesel", "expected_tranche": 6},
    ]
    
    print("\n   Cas de test (où Essence et Diesel diffèrent):")
    print("-" * 70)
    print(f"{'CV':<6} {'Énergie':<12} {'Tranche attendue':<18} {'Tranche obtenue':<16} {'RC':<15} {'Statut':<10}")
    print("-" * 70)
    
    for test in test_cases:
        try:
            result = controller.get_rc_premium_from_matrix(
                cie_id=1,
                zone_saisie="A",
                categorie="VP01",
                energie=test["energie"],
                cv_saisi=test["cv"],
                avec_remorque=False
            )
            
            actual_tranche = result.get("tranche", 0)
            is_correct = actual_tranche == test["expected_tranche"]
            status = "✅" if is_correct else "❌"
            
            print(f"{test['cv']:<6} {test['energie']:<12} {test['expected_tranche']:<18} {actual_tranche:<16} {result.get('rc', 0):<15.0f} {status:<10}")
            
        except Exception as e:
            print(f"{test['cv']:<6} {test['energie']:<12} {test['expected_tranche']:<18} {'ERR':<16} {'-':<15} ❌")
            print(f"   Erreur: {e}")
    
    session.close()


def test_with_real_vehicles():
    """
    Test avec des véhicules réels de la base de données
    """
    print("\n" + "=" * 70)
    print("📊 TEST AVEC VÉHICULES RÉELS")
    print("=" * 70)
    
    session = SessionLocal()
    controller = VehicleController(session)
    
    try:
        # Récupérer des véhicules réels
        from addons.Automobiles.models.automobile_models import Vehicle
        vehicles = session.query(Vehicle).limit(10).all()
        
        if not vehicles:
            print("   ⚠️ Aucun véhicule trouvé pour le test réel")
            session.close()
            return
        
        print("\n   Véhicules testés:")
        print("-" * 80)
        print(f"{'Immatriculation':<15} {'CV':<8} {'Énergie':<12} {'RC (FCFA)':<15} {'Tranche':<10} {'Vignette':<12}")
        print("-" * 80)
        
        for vehicle in vehicles:
            try:
                # Récupérer l'énergie (essayer plusieurs champs)
                energie = getattr(vehicle, 'energie', 'Essence')
                if not energie or energie == '':
                    energie = 'Essence'
                
                result = controller.get_rc_premium_from_matrix(
                    cie_id=1,
                    zone_saisie="A",
                    categorie=getattr(vehicle, 'categorie', 'VP01'),
                    energie=energie,
                    cv_saisi=getattr(vehicle, 'puissance_fiscale', 0),
                    avec_remorque=False
                )
                
                print(f"{getattr(vehicle, 'immatriculation', 'N/A'):<15} "
                      f"{getattr(vehicle, 'puissance_fiscale', 0):<8} "
                      f"{energie:<12} "
                      f"{result.get('rc', 0):<15.0f} "
                      f"{result.get('tranche', 'N/A'):<10} "
                      f"{result.get('vignette', 0):<12.0f}")
                
            except Exception as e:
                print(f"   ❌ Erreur pour {getattr(vehicle, 'immatriculation', 'N/A')}: {e}")
    
    except Exception as e:
        print(f"   ❌ Erreur lors du test réel: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    print("\n🚀 DÉMARRAGE DES TESTS...\n")
    
    # Exécuter tous les tests
    all_passed = test_rc_calculation()
    
    print("\n" + "=" * 70)
    print("📋 TESTS SUPPLÉMENTAIRES")
    print("=" * 70)
    
    test_detailed_case()
    test_with_real_vehicles()
    
    print("\n✅ Tests terminés.\n")
    
    # Quitter avec le code approprié
    sys.exit(0 if all_passed else 1)