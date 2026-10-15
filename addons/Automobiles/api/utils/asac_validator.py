# addons/Automobiles/utils/asac_validator.py
import re

class AsacDataValidator:
    """Validateur de données pour le format ASAC"""
    
    REQUIRED_FIELDS = ["office_code", "organization_code", "certificate_type", "channel", "productions"]
    REQUIRED_PRODUCTION_FIELDS = [
        "certificate_variant_code", "rc", "police_number", "starts_at", "ends_at",
        "customer_name", "customer_phone", "licence_plate", "vehicle_chassis",
        "vehicle_brand", "vehicle_model", "vehicle_category", "vehicle_genre",
        "vehicle_type", "vehicule_usage", "vehicle_energy", "nb_of_seats",
        "fiscal_power", "circulation_zone"
    ]
    
    @classmethod
    def validate_request(cls, data):
        errors = []
        warnings = []
        
        for field in cls.REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"❌ Champ obligatoire manquant: '{field}'")
        
        productions = data.get("productions", [])
        for idx, prod in enumerate(productions):
            for field in cls.REQUIRED_PRODUCTION_FIELDS:
                if field not in prod:
                    errors.append(f"❌ Production[{idx}]: Champ manquant '{field}'")
        
        return {"is_compliant": len(errors) == 0, "errors_count": len(errors), 
                "warnings_count": len(warnings), "errors": errors, "warnings": warnings,
                "compliance_rate": max(0, 100 - len(errors) * 5)}
    
    @classmethod
    def get_compliance_report(cls, data):
        return cls.validate_request(data)