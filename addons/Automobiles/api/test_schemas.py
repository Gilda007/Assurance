# test_schemas.py - Script de test
from addons.Automobiles.api.schemas import ProductionRequestSchema, CustomerType, VehicleCategory

# Test de validation
test_data = {
    "office_code": "AG-DLA-001",
    "organization_code": "711",
    "certificate_type": "cima",
    "channel": "api",
    "productions": [
        {
            "certificate_variant_code": "JAUNE",
            "police_number": "POL-2024-001",
            "starts_at": "2024-01-01",
            "ends_at": "2024-12-31",
            "rc": 63784,
            "dta": 0,
            "customer_name": "TEST CLIENT",
            "customer_phone": "690000000",
            "customer_type": "TSPP",
            "insured_name": "TEST ASSURE",
            "insured_phone": "690000001",
            "insured_email": "test@test.com",
            "insured_postal_code": "BP 1234",
            "insured_code": "CODE001",
            "insured_profession": "ST09",
            "insured_city": "DOUALA",
            "driver_name": "CONDUCTEUR TEST",
            "driver_birthdate": "1990-01-01",
            "driver_licence_number": "P123456",
            "driver_licence_category": "B",
            "driver_licence_issued_at": "2010-01-01",
            "licence_plate": "LT-001-AB",
            "vehicle_chassis": "VF1ABCDEF12345678",
            "vehicle_brand": "TOYOTA",
            "vehicle_model": "COROLLA",
            "vehicle_category": "01",
            "vehicle_genre": "GV04",
            "vehicle_type": "TV10",
            "vehicle_usage": "UV01",
            "vehicle_energy": "SEES",
            "circulation_zone": "A",
            "nb_of_seats": 5,
            "fiscal_power": 7,
            "vehicle_has_trailer": False,
            "taxpayer_number": "123456789"
        }
    ]
}

try:
    request = ProductionRequestSchema(**test_data)
    print("✅ Validation réussie!")
    print(f"   Office: {request.office_code}")
    print(f"   Productions: {len(request.productions)}")
except Exception as e:
    print(f"❌ Erreur: {e}")