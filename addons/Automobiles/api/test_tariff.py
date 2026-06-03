# test_tariff.py
"""
Test du contrôle tarifaire RC
"""

import sys
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from addons.Automobiles.api.schemas import ProductionItemSchema
from addons.Automobiles.api.services.tariff import TariffMatrix, TariffCalculator, TariffController
from addons.Automobiles.api.services import AdditionalSurcharges


def test_tariff_matrix():
    """Test de la matrice tarifaire"""
    print("\n" + "="*50)
    print("TEST 1: MATRICE TARIFAIRE")
    print("="*50)
    
    # Test 1.1: Catégorie 01, Zone A, 7 CV
    amount = TariffMatrix.get_rc_amount("01", "A", 7)
    print(f"Catégorie 01, Zone A, 7 CV: {amount} FCFA")
    assert amount == 63784, f"Attendu 63784, obtenu {amount}"
    
    # Test 1.2: Avec remorque
    amount_with_trailer = TariffMatrix.get_rc_amount("01", "A", 7, has_trailer=True)
    print(f"Avec remorque: {amount_with_trailer} FCFA")
    assert amount_with_trailer == int(63784 * 1.25), f"Attendu {int(63784 * 1.25)}, obtenu {amount_with_trailer}"
    
    # Test 1.3: Zone B
    amount_zone_b = TariffMatrix.get_rc_amount("01", "B", 7)
    print(f"Zone B: {amount_zone_b} FCFA")
    
    print("✅ Tests matrice tarifaire réussis")
    return True


def test_tariff_calculator():
    """Test du calculateur tarifaire"""
    print("\n" + "="*50)
    print("TEST 2: CALCULATEUR TARIFAIRE")
    print("="*50)
    
    # Créer une production de test
    prod = ProductionItemSchema(
        certificate_variant_code="JAUNE",
        police_number="POL-001",
        starts_at=date.today(),
        ends_at=date.today() + timedelta(days=365),
        rc=63784,  # Montant correct
        dta=0,
        customer_name="TEST",
        customer_phone="690000000",
        customer_type="TSPP",
        insured_name="TEST",
        insured_phone="690000001",
        insured_email="test@test.com",
        insured_postal_code="BP",
        insured_code="CODE",
        insured_profession="ST09",
        insured_city="DOUALA",
        driver_name="CONDUCTEUR",
        driver_birthdate=date(1990, 1, 1),
        driver_licence_number="P123",
        driver_licence_category="B",
        driver_licence_issued_at=date(2010, 1, 1),
        licence_plate="LT-001-AB",
        vehicle_chassis="CHASSIS",
        vehicle_brand="TOYOTA",
        vehicle_model="COROLLA",
        vehicle_category="01",
        vehicle_genre="GV04",
        vehicle_type="TV10",
        vehicle_usage="UV01",
        vehicle_energy="SEES",
        circulation_zone="A",
        nb_of_seats=5,
        fiscal_power=7,
        vehicle_has_trailer=False,
        taxpayer_number="123"
    )
    
    calculator = TariffCalculator()
    result = calculator.calculate_rc(prod)
    
    print(f"Montant calculé: {result['calculated_amount']}")
    print(f"Montant fourni: {result['provided_amount']}")
    print(f"Valide: {result['is_valid']}")
    
    if result['is_valid']:
        print("✅ Montant RC correct")
    else:
        print("❌ Montant RC incorrect")
    
    return result['is_valid']


def test_tariff_controller():
    """Test du contrôleur tarifaire"""
    print("\n" + "="*50)
    print("TEST 3: CONTRÔLEUR TARIFAIRE")
    print("="*50)
    
    # Production avec montant correct
    prod_correct = ProductionItemSchema(
        certificate_variant_code="JAUNE",
        police_number="POL-001",
        starts_at=date.today(),
        ends_at=date.today() + timedelta(days=365),
        rc=63784,
        dta=0,
        customer_name="TEST",
        customer_phone="690000000",
        customer_type="TSPP",
        insured_name="TEST",
        insured_phone="690000001",
        insured_email="test@test.com",
        insured_postal_code="BP",
        insured_code="CODE",
        insured_profession="ST09",
        insured_city="DOUALA",
        driver_name="CONDUCTEUR",
        driver_birthdate=date(1990, 1, 1),
        driver_licence_number="P123",
        driver_licence_category="B",
        driver_licence_issued_at=date(2010, 1, 1),
        licence_plate="LT-001-AB",
        vehicle_chassis="CHASSIS",
        vehicle_brand="TOYOTA",
        vehicle_model="COROLLA",
        vehicle_category="01",
        vehicle_genre="GV04",
        vehicle_type="TV10",
        vehicle_usage="UV01",
        vehicle_energy="SEES",
        circulation_zone="A",
        nb_of_seats=5,
        fiscal_power=7,
        vehicle_has_trailer=False,
        taxpayer_number="123"
    )
    
    # Production avec montant incorrect
    prod_incorrect = ProductionItemSchema(
        certificate_variant_code="JAUNE",
        police_number="POL-002",
        starts_at=date.today(),
        ends_at=date.today() + timedelta(days=365),
        rc=50000,  # Montant incorrect
        dta=0,
        customer_name="TEST2",
        customer_phone="690000002",
        customer_type="TSPP",
        insured_name="TEST2",
        insured_phone="690000003",
        insured_email="test2@test.com",
        insured_postal_code="BP",
        insured_code="CODE2",
        insured_profession="ST09",
        insured_city="DOUALA",
        driver_name="CONDUCTEUR2",
        driver_birthdate=date(1990, 1, 1),
        driver_licence_number="P456",
        driver_licence_category="B",
        driver_licence_issued_at=date(2010, 1, 1),
        licence_plate="LT-002-CD",
        vehicle_chassis="CHASSIS2",
        vehicle_brand="TOYOTA",
        vehicle_model="COROLLA",
        vehicle_category="01",
        vehicle_genre="GV04",
        vehicle_type="TV10",
        vehicle_usage="UV01",
        vehicle_energy="SEES",
        circulation_zone="A",
        nb_of_seats=5,
        fiscal_power=7,
        vehicle_has_trailer=False,
        taxpayer_number="456"
    )
    
    controller = TariffController()
    
    # Tester la production correcte
    is_valid, error = controller.validate_rc_amount(prod_correct, 0)
    print(f"Production correcte: {is_valid}")
    
    # Tester la production incorrecte
    is_valid, error = controller.validate_rc_amount(prod_incorrect, 1)
    print(f"Production incorrecte: {is_valid}")
    if error:
        print(f"  Erreur: {error['productions'][0]['message']}")
    
    # Tester le lot
    is_valid, errors = controller.validate_batch([prod_correct, prod_incorrect])
    print(f"\nLot complet valide: {is_valid}")
    if errors:
        print(f"  {len(errors.get('errors', []))} erreur(s) détectée(s)")
    
    return not is_valid  # Doit retourner False car une production est invalide


def test_additional_surcharges():
    """Test des suppléments supplémentaires"""
    print("\n" + "="*50)
    print("TEST 4: SUPPLÉMENTS SUPPLÉMENTAIRES")
    print("="*50)
    
    # Test conducteur expérimenté
    discount = AdditionalSurcharges.get_driver_experience_discount(15)
    print(f"Réduction pour 15 ans d'expérience: {discount}")
    assert discount == 0.85, f"Attendu 0.85, obtenu {discount}"
    
    # Test jeune conducteur
    surcharge = AdditionalSurcharges.get_young_driver_surcharge(1)
    print(f"Surprime pour 1 an d'expérience: {surcharge}")
    assert surcharge == 1.25, f"Attendu 1.25, obtenu {surcharge}"
    
    print("✅ Tests supplémentaires réussis")
    return True


if __name__ == "__main__":
    print("\n" + "🚀" * 20)
    print("   TEST DU CONTRÔLE TARIFAIRE RC")
    print("🚀" * 20)
    
    results = []
    results.append(("Matrice tarifaire", test_tariff_matrix()))
    results.append(("Calculateur tarifaire", test_tariff_calculator()))
    results.append(("Contrôleur tarifaire", test_tariff_controller()))
    results.append(("Suppléments supplémentaires", test_additional_surcharges()))
    
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
        print("   Le contrôle tarifaire RC est opérationnel.")