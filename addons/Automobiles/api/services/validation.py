# addons/Automobiles/api/services/validation.py - Version corrigée
"""
Service de validation des données (Étape 1)
Validation des champs individuels, formats et codifications
"""

from datetime import datetime, date
from typing import List, Dict, Any, Tuple, Optional
import re
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Exception personnalisée pour les erreurs de validation"""
    def __init__(self, errors: Dict[str, List[str]]):
        self.errors = errors
        super().__init__(str(errors))


class FieldValidator:
    """Validateur de champs individuels"""
    
    @staticmethod
    def validate_string(value: Any, field_name: str, max_length: int = 255, required: bool = True) -> Optional[str]:
        """
        Valide une chaîne de caractères
        """
        if value is None or (isinstance(value, str) and value.strip() == ""):
            if required:
                raise ValidationError({field_name: [f"Le champ {field_name} est obligatoire."]})
            return None
        
        # Convertir en string si ce n'est pas déjà une string (ex: Enum)
        cleaned = str(value).strip()
        if len(cleaned) > max_length:
            raise ValidationError({field_name: [f"Le champ {field_name} ne peut pas dépasser {max_length} caractères."]})
        
        return cleaned
    
    @staticmethod
    def validate_integer(value: Any, field_name: str, min_value: int = 0, max_value: int = None, required: bool = True) -> Optional[int]:
        """
        Valide un entier
        """
        if value is None:
            if required:
                raise ValidationError({field_name: [f"Le champ {field_name} est obligatoire."]})
            return None
        
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise ValidationError({field_name: [f"Le champ {field_name} doit être un nombre entier."]})
        
        if int_value < min_value:
            raise ValidationError({field_name: [f"Le champ {field_name} doit être supérieur ou égal à {min_value}."]})
        
        if max_value is not None and int_value > max_value:
            raise ValidationError({field_name: [f"Le champ {field_name} doit être inférieur ou égal à {max_value}."]})
        
        return int_value
    
    @staticmethod
    def validate_boolean(value: Any, field_name: str, required: bool = False) -> Optional[bool]:
        """
        Valide un booléen
        """
        if value is None:
            return False if not required else None
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            if value.lower() in ['true', '1', 'yes', 'on']:
                return True
            if value.lower() in ['false', '0', 'no', 'off']:
                return False
        
        raise ValidationError({field_name: [f"Le champ {field_name} doit être un booléen (true/false)."]})
    
    @staticmethod
    def validate_date(value: Any, field_name: str, required: bool = True) -> Optional[date]:
        """
        Valide une date au format YYYY-MM-DD
        """
        if value is None:
            if required:
                raise ValidationError({field_name: [f"Le champ {field_name} est obligatoire."]})
            return None
        
        # Si c'est déjà un objet date
        if isinstance(value, date):
            return value
        
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                raise ValidationError({field_name: [f"Le champ {field_name} doit être au format YYYY-MM-DD."]})
        
        raise ValidationError({field_name: [f"Le champ {field_name} doit être une date valide."]})
    
    @staticmethod
    def validate_enum(value: Any, field_name: str, enum_class, required: bool = True) -> Optional[str]:
        """
        Valide une valeur d'énumération
        
        Accepte à la fois les objets Enum et les valeurs string
        """
        if value is None:
            if required:
                raise ValidationError({field_name: [f"Le champ {field_name} est obligatoire."]})
            return None
        
        # Extraire la valeur réelle (si c'est un objet Enum)
        if hasattr(value, 'value'):
            actual_value = value.value
        else:
            actual_value = str(value).strip().upper()
        
        # Récupérer toutes les valeurs valides de l'énumération
        valid_values = [e.value for e in enum_class]
        
        if actual_value not in valid_values:
            raise ValidationError({
                field_name: [f"La valeur '{actual_value}' pour le champ {field_name} est invalide. Valeurs acceptées: {', '.join(valid_values)}"]
            })
        
        return actual_value


class ProductionValidator:
    """Validateur principal pour les productions"""
    
    def __init__(self):
        self.field_validator = FieldValidator()
    
    def validate_production_request(self, request) -> Tuple[bool, Optional[Dict[str, List[str]]]]:
        """
        Valide une requête de production complète (Étape 1)
        
        Args:
            request: Soit un dict, soit un objet ProductionRequestSchema
        
        Returns:
            (is_valid, errors_dict)
        """
        errors = {}
        
        # Convertir en dict si c'est un objet Pydantic
        if hasattr(request, 'model_dump'):
            request_dict = request.model_dump()
            productions_list = request.productions
        else:
            request_dict = request
            productions_list = request.get('productions', [])
        
        # 1. Valider les champs de la requête principale
        self._validate_request_header(request, errors)
        
        # 2. Valider chaque production
        for idx, production in enumerate(productions_list):
            self._validate_production_item(production, idx, errors)
        
        # 3. Vérifier l'unicité des immatriculations dans le lot
        self._validate_unique_licence_plates(productions_list, errors)
        
        return len(errors) == 0, errors if errors else None
    
    def _validate_request_header(self, request, errors: Dict):
        """Valide l'en-tête de la requête"""
        try:
            office_code = getattr(request, 'office_code', None)
            self.field_validator.validate_string(office_code, "office_code", max_length=50)
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            org_code = getattr(request, 'organization_code', None)
            self.field_validator.validate_string(org_code, "organization_code", max_length=50)
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            cert_type = getattr(request, 'certificate_type', 'cima')
            self.field_validator.validate_string(cert_type, "certificate_type", max_length=50, required=False)
        except ValidationError as e:
            errors.update(e.errors)
    
    def _validate_production_item(self, prod, idx: int, errors: Dict):
        """Valide un élément de production"""
        prefix = f"productions.{idx}"
        
        # Fonction helper pour récupérer un attribut
        def get_attr(obj, name, default=None):
            if hasattr(obj, name):
                return getattr(obj, name)
            if isinstance(obj, dict):
                return obj.get(name, default)
            return default
        
        # === ATTESTATION ET CONTRAT ===
        try:
            cert_variant = get_attr(prod, 'certificate_variant_code')
            self.field_validator.validate_enum(cert_variant, f"{prefix}.certificate_variant_code", self._get_enum_class('certificate_variant'))
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            police = get_attr(prod, 'police_number', '')
            self.field_validator.validate_string(police, f"{prefix}.police_number", max_length=50, required=False)
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            starts_at = get_attr(prod, 'starts_at')
            self.field_validator.validate_date(starts_at, f"{prefix}.starts_at")
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            ends_at = get_attr(prod, 'ends_at')
            self.field_validator.validate_date(ends_at, f"{prefix}.ends_at")
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            rc = get_attr(prod, 'rc', 0)
            self.field_validator.validate_integer(rc, f"{prefix}.rc", min_value=0)
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            dta = get_attr(prod, 'dta', 0)
            self.field_validator.validate_integer(dta, f"{prefix}.dta", min_value=0)
        except ValidationError as e:
            errors.update(e.errors)
        
        # === SOUSCRIPTEUR ===
        try:
            customer_name = get_attr(prod, 'customer_name', '')
            self.field_validator.validate_string(customer_name, f"{prefix}.customer_name", max_length=255)
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            customer_phone = get_attr(prod, 'customer_phone', '')
            self.field_validator.validate_string(customer_phone, f"{prefix}.customer_phone", max_length=50)
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            customer_type = get_attr(prod, 'customer_type')
            self.field_validator.validate_enum(customer_type, f"{prefix}.customer_type", self._get_enum_class('customer_type'))
        except ValidationError as e:
            errors.update(e.errors)
        
        # === ASSURÉ ===
        try:
            insured_name = get_attr(prod, 'insured_name', '')
            self.field_validator.validate_string(insured_name, f"{prefix}.insured_name", max_length=255)
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            insured_phone = get_attr(prod, 'insured_phone', '')
            self.field_validator.validate_string(insured_phone, f"{prefix}.insured_phone", max_length=50)
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            insured_email = get_attr(prod, 'insured_email', '')
            self.field_validator.validate_string(insured_email, f"{prefix}.insured_email", max_length=255)
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            insured_postal = get_attr(prod, 'insured_postal_code', '')
            self.field_validator.validate_string(insured_postal, f"{prefix}.insured_postal_code", max_length=100)
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            insured_code = get_attr(prod, 'insured_code', '')
            self.field_validator.validate_string(insured_code, f"{prefix}.insured_code", max_length=50)
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            insured_prof = get_attr(prod, 'insured_profession')
            self.field_validator.validate_enum(insured_prof, f"{prefix}.insured_profession", self._get_enum_class('insured_profession'))
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            insured_city = get_attr(prod, 'insured_city', '')
            self.field_validator.validate_string(insured_city, f"{prefix}.insured_city", max_length=100)
        except ValidationError as e:
            errors.update(e.errors)
        
        # === CONDUCTEUR ===
        try:
            driver_name = get_attr(prod, 'driver_name', '')
            self.field_validator.validate_string(driver_name, f"{prefix}.driver_name", max_length=255)
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            driver_birth = get_attr(prod, 'driver_birthdate')
            self.field_validator.validate_date(driver_birth, f"{prefix}.driver_birthdate")
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            licence_num = get_attr(prod, 'driver_licence_number', '')
            self.field_validator.validate_string(licence_num, f"{prefix}.driver_licence_number", max_length=50)
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            licence_cat = get_attr(prod, 'driver_licence_category', '')
            self.field_validator.validate_string(licence_cat, f"{prefix}.driver_licence_category", max_length=10)
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            licence_issued = get_attr(prod, 'driver_licence_issued_at')
            self.field_validator.validate_date(licence_issued, f"{prefix}.driver_licence_issued_at")
        except ValidationError as e:
            errors.update(e.errors)
        
        # === VÉHICULE ===
        try:
            plate = get_attr(prod, 'licence_plate', '')
            self.field_validator.validate_string(plate, f"{prefix}.licence_plate", max_length=20)
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            chassis = get_attr(prod, 'vehicle_chassis', '')
            self.field_validator.validate_string(chassis, f"{prefix}.vehicle_chassis", max_length=50)
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            brand = get_attr(prod, 'vehicle_brand', '')
            self.field_validator.validate_string(brand, f"{prefix}.vehicle_brand", max_length=100)
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            model = get_attr(prod, 'vehicle_model', '')
            self.field_validator.validate_string(model, f"{prefix}.vehicle_model", max_length=100)
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            category = get_attr(prod, 'vehicle_category')
            self.field_validator.validate_enum(category, f"{prefix}.vehicle_category", self._get_enum_class('vehicle_category'))
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            genre = get_attr(prod, 'vehicle_genre')
            self.field_validator.validate_enum(genre, f"{prefix}.vehicle_genre", self._get_enum_class('vehicle_genre'))
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            vtype = get_attr(prod, 'vehicle_type')
            self.field_validator.validate_enum(vtype, f"{prefix}.vehicle_type", self._get_enum_class('vehicle_type'))
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            usage = get_attr(prod, 'vehicle_usage')
            self.field_validator.validate_enum(usage, f"{prefix}.vehicle_usage", self._get_enum_class('vehicle_usage'))
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            energy = get_attr(prod, 'vehicle_energy')
            self.field_validator.validate_enum(energy, f"{prefix}.vehicle_energy", self._get_enum_class('vehicle_energy'))
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            zone = get_attr(prod, 'circulation_zone')
            self.field_validator.validate_enum(zone, f"{prefix}.circulation_zone", self._get_enum_class('circulation_zone'))
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            seats = get_attr(prod, 'nb_of_seats', 0)
            self.field_validator.validate_integer(seats, f"{prefix}.nb_of_seats", min_value=1, max_value=100)
        except ValidationError as e:
            errors.update(e.errors)
        
        try:
            power = get_attr(prod, 'fiscal_power', 0)
            self.field_validator.validate_integer(power, f"{prefix}.fiscal_power", min_value=1, max_value=1000)
        except ValidationError as e:
            errors.update(e.errors)
        
        # === FISCAL ===
        try:
            taxpayer = get_attr(prod, 'taxpayer_number', '')
            self.field_validator.validate_string(taxpayer, f"{prefix}.taxpayer_number", max_length=50)
        except ValidationError as e:
            errors.update(e.errors)
    
    def _validate_unique_licence_plates(self, productions: List, errors: Dict):
        """Vérifie l'unicité des immatriculations dans le lot"""
        licence_plates = []
        
        def get_plate(prod):
            if hasattr(prod, 'licence_plate'):
                return getattr(prod, 'licence_plate', '').strip().upper()
            if isinstance(prod, dict):
                return prod.get('licence_plate', '').strip().upper()
            return ''
        
        for idx, prod in enumerate(productions):
            plate = get_plate(prod)
            if plate and plate in licence_plates:
                errors[f"productions.{idx}.licence_plate"] = [
                    "Le champ d'immatriculation doit être unique pour chaque demande."
                ]
                break
            if plate:
                licence_plates.append(plate)
    
    def _get_enum_class(self, enum_name: str):
        """Retourne la classe d'énumération correspondante"""
        # Import tardif pour éviter les imports circulaires
        from ..schemas import (
            CertificateVariant, CustomerType, InsuredProfession,
            VehicleCategory, VehicleGenre, VehicleType,
            VehicleUsage, VehicleEnergy, CirculationZone
        )
        
        enums = {
            'certificate_variant': CertificateVariant,
            'customer_type': CustomerType,
            'insured_profession': InsuredProfession,
            'vehicle_category': VehicleCategory,
            'vehicle_genre': VehicleGenre,
            'vehicle_type': VehicleType,
            'vehicle_usage': VehicleUsage,
            'vehicle_energy': VehicleEnergy,
            'circulation_zone': CirculationZone,
        }
        return enums.get(enum_name)


class DateRangeValidator:
    """Validateur des plages de dates"""
    
    @staticmethod
    def validate_contract_duration(starts_at: date, ends_at: date, min_days: int = 1, max_days: int = 365) -> Tuple[bool, Optional[str]]:
        """
        Valide la durée du contrat
        """
        delta = (ends_at - starts_at).days
        
        if delta < min_days:
            return False, f"La durée du contrat doit être d'au moins {min_days} jour(s)."
        
        if delta > max_days:
            return False, f"La durée du contrat ne doit pas excéder {max_days} jours."
        
        return True, None
    
    @staticmethod
    def validate_starts_at(starts_at: date) -> Tuple[bool, Optional[str]]:
        """
        Valide que la date d'effet n'est pas antérieure à aujourd'hui
        """
        today = date.today()
        
        if starts_at < today:
            return False, "La date d'effet ne peut pas être antérieure à la date du jour."
        
        return True, None