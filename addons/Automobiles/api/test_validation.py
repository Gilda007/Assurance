# test_validation.py - Version corrigée
"""
Test de la validation des données
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from addons.Automobiles.api.schemas import ProductionRequestSchema, ProductionItemSchema
from addons.Automobiles.api.services import ProductionValidator
from datetime import date, timedelta


def test_valid_production():
    """Test avec des données valides - utiliser des VALEURS STRING"""
    print("\n" + "="*50)
    print("TEST 1: PRODUCTION VALIDE")
    print("="*50)
    
    # ⚠️ IMPORTANT: Utiliser les VALEURS STRING des énumérations, PAS les objets Enum
    request = ProductionRequestSchema(
        office_code="AG-DLA-001",
        organization_code="ACTIVA",
        productions=[
            ProductionItemSchema(
                # Valeurs string (pas les objets Enum)
                certificate_variant_code="JAUNE",
                police_number="POL-2024-001",
                starts_at=date.today(),
                ends_at=date.today() + timedelta(days=365),
                rc=63784,
                dta=0,
                customer_name="TEST CLIENT",
                customer_phone="690000000",
                customer_type="TSPP",  # ← string, pas CustomerType.PHYSICAL
                insured_name="TEST ASSURE",
                insured_phone="690000001",
                insured_email="test@test.com",
                insured_postal_code="BP 1234",
                insured_code="CODE001",
                insured_profession="ST09",  # ← string, pas InsuredProfession.SALARIE
                insured_city="DOUALA",
                driver_name="CONDUCTEUR TEST",
                driver_birthdate=date(1990, 1, 1),
                driver_licence_number="P123456",
                driver_licence_category="B",
                driver_licence_issued_at=date(2010, 1, 1),
                licence_plate="LT-001-AB",
                vehicle_chassis="VF1ABCDEF12345678",
                vehicle_brand="TOYOTA",
                vehicle_model="COROLLA",
                vehicle_category="01",  # ← string, pas VehicleCategory.TOURISME_PP
                vehicle_genre="GV04",  # ← string, pas VehicleGenre.VOITURE
                vehicle_type="TV10",  # ← string, pas VehicleType.PARTICULIER
                vehicle_usage="UV01",  # ← string, pas VehicleUsage.PROMENADE_AFFAIRE
                vehicle_energy="SEES",  # ← string, pas VehicleEnergy.ESSENCE
                circulation_zone="A",  # ← string, pas CirculationZone.ZONE_A
                nb_of_seats=5,
                fiscal_power=7,
                vehicle_has_trailer=False,
                taxpayer_number="123456789"
            )
        ]
    )
    
    validator = ProductionValidator()
    is_valid, errors = validator.validate_production_request(request)
    
    if is_valid:
        print("✅ Validation réussie!")
    else:
        print(f"❌ Validation échouée: {errors}")
    
    return is_valid


def test_valid_production_with_enum_objects():
    """Test avec des objets Enum (convertit automatiquement en string)"""
    print("\n" + "="*50)
    print("TEST 1b: PRODUCTION VALIDE AVEC ENUM")
    print("="*50)
    
    from addons.Automobiles.api.schemas import (
        CustomerType, VehicleCategory, VehicleGenre, VehicleType,
        VehicleUsage, VehicleEnergy, CirculationZone, InsuredProfession,
        CertificateVariant
    )
    
    # Utiliser les objets Enum - Pydantic les convertit automatiquement
    request = ProductionRequestSchema(
        office_code="AG-DLA-001",
        organization_code="ACTIVA",
        productions=[
            ProductionItemSchema(
                certificate_variant_code=CertificateVariant.JAUNE,
                police_number="POL-2024-001",
                starts_at=date.today(),
                ends_at=date.today() + timedelta(days=365),
                rc=63784,
                dta=0,
                customer_name="TEST CLIENT",
                customer_phone="690000000",
                customer_type=CustomerType.PHYSICAL,
                insured_name="TEST ASSURE",
                insured_phone="690000001",
                insured_email="test@test.com",
                insured_postal_code="BP 1234",
                insured_code="CODE001",
                insured_profession=InsuredProfession.SALARIE,
                insured_city="DOUALA",
                driver_name="CONDUCTEUR TEST",
                driver_birthdate=date(1990, 1, 1),
                driver_licence_number="P123456",
                driver_licence_category="B",
                driver_licence_issued_at=date(2010, 1, 1),
                licence_plate="LT-001-AB",
                vehicle_chassis="VF1ABCDEF12345678",
                vehicle_brand="TOYOTA",
                vehicle_model="COROLLA",
                vehicle_category=VehicleCategory.TOURISME_PP,
                vehicle_genre=VehicleGenre.VOITURE,
                vehicle_type=VehicleType.PARTICULIER,
                vehicle_usage=VehicleUsage.PROMENADE_AFFAIRE,
                vehicle_energy=VehicleEnergy.ESSENCE,
                circulation_zone=CirculationZone.ZONE_A,
                nb_of_seats=5,
                fiscal_power=7,
                vehicle_has_trailer=False,
                taxpayer_number="123456789"
            )
        ]
    )
    
    validator = ProductionValidator()
    is_valid, errors = validator.validate_production_request(request)
    
    if is_valid:
        print("✅ Validation réussie avec objets Enum!")
    else:
        print(f"❌ Validation échouée: {errors}")
    
    return is_valid


def test_invalid_production():
    """Test avec des données invalides"""
    print("\n" + "="*50)
    print("TEST 2: PRODUCTION INVALIDE")
    print("="*50)
    
    try:
        request = ProductionRequestSchema(
            office_code="",  # Code bureau vide
            organization_code="ACTIVA",
            productions=[
                ProductionItemSchema(
                    certificate_variant_code="INVALIDE",
                    police_number="",
                    starts_at=date.today(),
                    ends_at=date.today() + timedelta(days=400),
                    rc=-100,
                    dta=0,
                    customer_name="",
                    customer_phone="",
                    customer_type="INVALIDE",
                    insured_name="",
                    insured_phone="",
                    insured_email="",
                    insured_postal_code="",
                    insured_code="",
                    insured_profession="INVALIDE",
                    insured_city="",
                    driver_name="",
                    driver_birthdate=date(1990, 1, 1),
                    driver_licence_number="",
                    driver_licence_category="",
                    driver_licence_issued_at=date(2010, 1, 1),
                    licence_plate="",
                    vehicle_chassis="",
                    vehicle_brand="",
                    vehicle_model="",
                    vehicle_category="99",
                    vehicle_genre="INVALIDE",
                    vehicle_type="INVALIDE",
                    vehicle_usage="INVALIDE",
                    vehicle_energy="INVALIDE",
                    circulation_zone="Z",
                    nb_of_seats=0,
                    fiscal_power=0,
                    vehicle_has_trailer=False,
                    taxpayer_number=""
                )
            ]
        )
        
        validator = ProductionValidator()
        is_valid, errors = validator.validate_production_request(request)
        
        if not is_valid:
            print("✅ Validation échouée (normal) - Erreurs détectées:")
            # Afficher seulement les premières erreurs pour ne pas surcharger
            count = 0
            for field, errs in errors.items():
                if count < 10:
                    print(f"   - {field}: {errs[0]}")
                count += 1
            if len(errors) > 10:
                print(f"   ... et {len(errors) - 10} autres erreurs")
            return True
        else:
            print("❌ La validation aurait dû échouer!")
            return False
            
    except Exception as e:
        print("✅ Erreurs détectées par Pydantic (normal):")
        print(f"   {str(e)[:200]}...")
        return True


def test_duplicate_plates():
    """Test avec des immatriculations en doublon"""
    print("\n" + "="*50)
    print("TEST 3: IMMATRICULATIONS EN DOUBLON")
    print("="*50)
    
    from addons.Automobiles.api.schemas import (
        CustomerType, VehicleCategory, VehicleGenre, VehicleType,
        VehicleUsage, VehicleEnergy, CirculationZone, InsuredProfession,
        CertificateVariant
    )
    
    request = ProductionRequestSchema(
        office_code="AG-DLA-001",
        organization_code="ACTIVA",
        productions=[
            ProductionItemSchema(
                certificate_variant_code=CertificateVariant.JAUNE,
                police_number="POL-2024-001",
                starts_at=date.today(),
                ends_at=date.today() + timedelta(days=365),
                rc=63784,
                dta=0,
                customer_name="TEST 1",
                customer_phone="690000000",
                customer_type=CustomerType.PHYSICAL,
                insured_name="TEST 1",
                insured_phone="690000001",
                insured_email="test1@test.com",
                insured_postal_code="BP 1234",
                insured_code="CODE001",
                insured_profession=InsuredProfession.SALARIE,
                insured_city="DOUALA",
                driver_name="CONDUCTEUR 1",
                driver_birthdate=date(1990, 1, 1),
                driver_licence_number="P123456",
                driver_licence_category="B",
                driver_licence_issued_at=date(2010, 1, 1),
                licence_plate="LT-001-AB",
                vehicle_chassis="VF1ABCDEF12345678",
                vehicle_brand="TOYOTA",
                vehicle_model="COROLLA",
                vehicle_category=VehicleCategory.TOURISME_PP,
                vehicle_genre=VehicleGenre.VOITURE,
                vehicle_type=VehicleType.PARTICULIER,
                vehicle_usage=VehicleUsage.PROMENADE_AFFAIRE,
                vehicle_energy=VehicleEnergy.ESSENCE,
                circulation_zone=CirculationZone.ZONE_A,
                nb_of_seats=5,
                fiscal_power=7,
                vehicle_has_trailer=False,
                taxpayer_number="123456789"
            ),
            ProductionItemSchema(
                certificate_variant_code=CertificateVariant.JAUNE,
                police_number="POL-2024-002",
                starts_at=date.today(),
                ends_at=date.today() + timedelta(days=365),
                rc=63784,
                dta=0,
                customer_name="TEST 2",
                customer_phone="690000002",
                customer_type=CustomerType.PHYSICAL,
                insured_name="TEST 2",
                insured_phone="690000003",
                insured_email="test2@test.com",
                insured_postal_code="BP 5678",
                insured_code="CODE002",
                insured_profession=InsuredProfession.SALARIE,
                insured_city="DOUALA",
                driver_name="CONDUCTEUR 2",
                driver_birthdate=date(1990, 1, 1),
                driver_licence_number="P123457",
                driver_licence_category="B",
                driver_licence_issued_at=date(2010, 1, 1),
                licence_plate="LT-001-AB",  # Même plaque!
                vehicle_chassis="VF1ABCDEF87654321",
                vehicle_brand="TOYOTA",
                vehicle_model="COROLLA",
                vehicle_category=VehicleCategory.TOURISME_PP,
                vehicle_genre=VehicleGenre.VOITURE,
                vehicle_type=VehicleType.PARTICULIER,
                vehicle_usage=VehicleUsage.PROMENADE_AFFAIRE,
                vehicle_energy=VehicleEnergy.ESSENCE,
                circulation_zone=CirculationZone.ZONE_A,
                nb_of_seats=5,
                fiscal_power=7,
                vehicle_has_trailer=False,
                taxpayer_number="987654321"
            )
        ]
    )
    
    validator = ProductionValidator()
    is_valid, errors = validator.validate_production_request(request)
    
    # Vérifier que l'erreur de doublon est présente
    has_duplicate_error = False
    for field, errs in errors.items():
        if "licence_plate" in field and "unique" in errs[0]:
            has_duplicate_error = True
            break
    
    if has_duplicate_error:
        print("✅ Doublon détecté!")
        return True
    else:
        print("❌ Le doublon n'a pas été détecté!")
        print(f"   Erreurs: {errors}")
        return False


def test_date_validation():
    """Test de validation des dates"""
    print("\n" + "="*50)
    print("TEST 4: VALIDATION DES DATES")
    print("="*50)
    
    from addons.Automobiles.api.services import DateRangeValidator
    
    # Test date d'effet antérieure
    is_valid, error = DateRangeValidator.validate_starts_at(date(2020, 1, 1))
    if not is_valid:
        print(f"✅ Date antérieure détectée: {error}")
    else:
        print("❌ La date antérieure aurait dû être rejetée!")
        return False
    
    # Test durée trop courte
    starts_at = date.today()
    ends_at = date.today()
    is_valid, error = DateRangeValidator.validate_contract_duration(starts_at, ends_at, min_days=1)
    if not is_valid:
        print(f"✅ Durée trop courte détectée: {error}")
    else:
        print("❌ La durée trop courte aurait dû être rejetée!")
        return False
    
    # Test durée trop longue
    ends_at = date.today() + timedelta(days=400)
    is_valid, error = DateRangeValidator.validate_contract_duration(starts_at, ends_at, max_days=365)
    if not is_valid:
        print(f"✅ Durée trop longue détectée: {error}")
    else:
        print("❌ La durée trop longue aurait dû être rejetée!")
        return False
    
    # Test durée valide
    ends_at = date.today() + timedelta(days=180)
    is_valid, error = DateRangeValidator.validate_contract_duration(starts_at, ends_at)
    if is_valid:
        print("✅ Durée valide acceptée")
    else:
        print("❌ La durée valide a été rejetée!")
        return False
    
    return True


def test_field_validation():
    """Test de validation des champs individuels"""
    print("\n" + "="*50)
    print("TEST 5: VALIDATION DES CHAMPS INDIVIDUELS")
    print("="*50)
    
    from addons.Automobiles.api.services import FieldValidator, ValidationError
    
    validator = FieldValidator()
    passed = 0
    total = 0
    
    # Test validation string
    total += 1
    try:
        result = validator.validate_string("Test", "champ_test", max_length=10)
        if result == "Test":
            print("✅ Validation string OK")
            passed += 1
        else:
            print("❌ Validation string échouée")
    except ValidationError as e:
        print(f"❌ Validation string: {e.errors}")
    
    # Test validation string trop longue
    total += 1
    try:
        validator.validate_string("Ceci est une très longue chaîne", "champ_test", max_length=10)
        print("❌ La chaîne trop longue aurait dû être rejetée")
    except ValidationError:
        print("✅ Chaîne trop longue correctement rejetée")
        passed += 1
    
    # Test validation entier
    total += 1
    try:
        result = validator.validate_integer(42, "champ_test", min_value=0, max_value=100)
        if result == 42:
            print("✅ Validation entier OK")
            passed += 1
        else:
            print("❌ Validation entier échouée")
    except ValidationError as e:
        print(f"❌ Validation entier: {e.errors}")
    
    # Test validation entier hors limites
    total += 1
    try:
        validator.validate_integer(150, "champ_test", max_value=100)
        print("❌ L'entier hors limite aurait dû être rejeté")
    except ValidationError:
        print("✅ Entier hors limite correctement rejeté")
        passed += 1
    
    # Test validation date
    total += 1
    try:
        result = validator.validate_date("2024-01-15", "champ_test")
        if result and result.year == 2024:
            print("✅ Validation date OK")
            passed += 1
        else:
            print("❌ Validation date échouée")
    except ValidationError as e:
        print(f"❌ Validation date: {e.errors}")
    
    # Test validation date invalide
    total += 1
    try:
        validator.validate_date("2024-13-45", "champ_test")
        print("❌ La date invalide aurait dû être rejetée")
    except ValidationError:
        print("✅ Date invalide correctement rejetée")
        passed += 1
    
    print(f"\n📊 Résultat: {passed}/{total} tests réussis")
    return passed == total


if __name__ == "__main__":
    print("\n" + "🚀" * 20)
    print("   TEST DE VALIDATION DES DONNÉES")
    print("🚀" * 20)
    
    results = []
    results.append(("Production valide (strings)", test_valid_production()))
    results.append(("Production valide (Enum)", test_valid_production_with_enum_objects()))
    results.append(("Production invalide", test_invalid_production()))
    results.append(("Doublons d'immatriculations", test_duplicate_plates()))
    results.append(("Validation des dates", test_date_validation()))
    results.append(("Validation des champs", test_field_validation()))
    
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