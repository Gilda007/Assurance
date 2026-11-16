# test_schemas.py - Script de test
from addons.Automobiles.api.schemas import ProductionRequestSchema, CustomerType, VehicleCategory

# Test de validation
test_data = {
  "office_code": "100C179",
  "organization_code": "711",
  "certificate_type": "cima",
  "channel": "api",
  "productions": [
    {
      "certificate_variant_code": "auto",
      "rc": 70877,
      "police_number": "3211-202611-0013",
      "starts_at": "2026-11-10",
      "ends_at": "2027-11-10",
      "customer_name": "TAGNE Sylvestre",
      "customer_phone": "+237670479936",
      "customer_email": "delorsekani@gmail.com",
      "customer_postal_code": "BP YAOUNDE",
      "customer_type": "TSPM",
      "insured_name": "TAGNE Sylvestre",
      "insured_phone": "+237670479936",
      "insured_email": "delorsekani@gmail.com",
      "insured_postal_code": "BP YAOUNDE",
      "licence_plate": "CE858HT",
      "vehicle_chassis": "CH000000000981517",
      "vehicle_brand": "ASTON MARTIN",
      "vehicle_model": "AS007",
      "vehicle_category": "VP01",
      "vehicle_genre": "GV04",
      "vehicle_type": "TV10",
      "vehicule_usage": "UV001",
      "vehicle_energy": "SEES",
      "nb_of_seats": 5,
      "fiscal_power": 5,
      "circulation_zone": "A",
      "driver_name": "N/A",
      "driver_birthdate": "1990-01-01",
      "driver_licence_issued_at": "2010-01-01",
      "vehicle_has_trailer": false,
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