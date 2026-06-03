# addons/Automobiles/api/schemas.py
"""
Schémas Pydantic pour la validation des données API ASAC
Conforme à la documentation version 1.2
"""

from datetime import date, datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum
import re


# ============================================================================
# ÉNUMÉRATIONS (CODES)
# ============================================================================

class CustomerType(str, Enum):
    """Type de souscripteur (section 4.1)"""
    PHYSICAL = "TSPP"  # Personne Physique
    LEGAL = "TSPM"      # Personne Morale


class VehicleCategory(str, Enum):
    """Catégorie de véhicule (section 4.2)"""
    TOURISME_PP = "01"
    TRANSPORT_PROPRE = "02"
    TRANSPORT_MARCHANDISES = "03"
    TRANSPORT_VOYAGEURS = "04"
    DEUX_TROIS_ROUES = "05"
    GARAGISTE = "06"
    AUTO_ECOLE = "07"
    LOCATION = "08"
    ENGIN_CHANTIER = "09"
    VEHICULE_SPECIAL = "10"
    CATEGORIE_11 = "11"
    TOURISME_PM = "12"


class VehicleGenre(str, Enum):
    """Genre du véhicule (section 4.3)"""
    CAMION = "GV01"
    CAMIONNETTE = "GV02"
    CYCLOMOTEUR = "GV03"
    VOITURE = "GV04"
    ENGIN_CHANTIER = "GV05"
    CAR = "GV06"
    FOURGONNETTE = "GV07"
    REMORQUE = "GV08"
    SCOOTER = "GV09"
    SEMI_REMORQUE = "GV10"
    TRACTEUR_AGRICOLE = "GV11"
    TRACTEUR_ROUTIER = "GV12"


class VehicleType(str, Enum):
    """Type de véhicule (section 4.4)"""
    AMBULANCE = "TV01"
    AUTO_CAR = "TV02"
    CORBILLARD = "TV03"
    MINI_CAR = "TV04"
    TAXI_COMMUNAL = "TV05"
    TAXI_URBAIN = "TV06"
    AUTO_ECOLE = "TV07"
    SERVICE_PUBLIC = "TV08"
    TOURISME_CHAUFFEUR = "TV09"
    PARTICULIER = "TV10"
    UTILITAIRE = "TV11"
    LOCATION = "TV12"
    CYCLOMOTEUR = "TV13"


class VehicleUsage(str, Enum):
    """Usage du véhicule (section 4.5)"""
    PROMENADE_AFFAIRE = "UV01"
    TRANSPORT_PROPRE = "UV02"
    TRANSPORT_PRIVE_VOYAGEURS = "UV03"
    TRANSPORT_PUBLIC_MARCHANDISES = "UV04"
    TRANSPORT_PUBLIC_VOYAGEURS = "UV05"
    AUTO_ECOLE = "UV06"
    LOCATION = "UV07"
    SPECIAL = "UV08"
    ENGIN_CHANTIER = "UV09"
    DEUX_TROIS_ROUES = "UV10"


class VehicleEnergy(str, Enum):
    """Énergie du véhicule (section 4.6)"""
    ESSENCE = "SEES"
    DIESEL = "SEDI"
    ELECTRIQUE = "SEEL"
    HYBRIDE = "SEHY"


class CirculationZone(str, Enum):
    """Zone de circulation (section 4.7)"""
    ZONE_A = "A"
    ZONE_B = "B"
    ZONE_C = "C"


class InsuredProfession(str, Enum):
    """Profession de l'assuré (section 4.9)"""
    AGENT_COMMERCIAL = "ST01"
    AGENT_RECOUVREMENT = "ST02"
    AGRICULTEUR = "ST03"
    ARTISAN = "ST04"
    CONJOINT = "ST05"
    EMPLOYEUR = "ST06"
    RELIGIEUX = "ST07"
    RETRAITE = "ST08"
    SALARIE = "ST09"
    SANS_EMPLOI = "ST10"
    VRP = "ST11"
    AUTRE = "ST12"


class CertificateVariant(str, Enum):
    """Variante d'attestation (couleur)"""
    JAUNE = "JAUNE"
    VERTE = "VERTE"
    BLEUE = "BLEUE"
    ROSE = "ROSE"


class CertificateType(str, Enum):
    """Type d'attestation"""
    CIMA = "cima"
    CARTE_ROSE = "carte-rose"


class ProductionState(str, Enum):
    """État d'une production"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================================================
# SCHÉMAS D'AUTHENTIFICATION
# ============================================================================

class TokenRequest(BaseModel):
    """Requête d'authentification"""
    app_key: str = Field(..., description="Clé applicative", min_length=1, max_length=255)
    username: str = Field(..., description="Nom d'utilisateur", min_length=1, max_length=255)


class TokenResponse(BaseModel):
    """Réponse d'authentification"""
    token: str = Field(..., description="Token JWT")
    token_name: str = Field(..., description="Nom du token")
    expires_at: datetime = Field(..., description="Date d'expiration du token")


# ============================================================================
# SCHÉMAS DES DONNÉES DE PRODUCTION
# ============================================================================

class SubscriberSchema(BaseModel):
    """Souscripteur"""
    name: str = Field(..., max_length=255, description="Nom complet du souscripteur")
    phone: str = Field(..., max_length=50, description="Téléphone du souscripteur")
    type: CustomerType = Field(..., description="Type de souscripteur")
    email: Optional[str] = Field(None, max_length=255, description="Email du souscripteur")
    postal_code: Optional[str] = Field(None, max_length=100, description="Boîte postale")


class InsuredSchema(BaseModel):
    """Assuré - Champs obligatoires selon version 1.2"""
    name: str = Field(..., max_length=255, description="Nom complet de l'assuré")
    phone: str = Field(..., max_length=50, description="Téléphone mobile de l'assuré")
    email: str = Field(..., max_length=255, description="Email de l'assuré")
    postal_code: str = Field(..., max_length=100, description="Boîte postale")
    code: str = Field(..., max_length=50, description="Code interne de l'assuré")
    profession: InsuredProfession = Field(..., description="Profession de l'assuré")
    birthdate: Optional[date] = Field(None, description="Date de naissance")
    city: str = Field(..., max_length=100, description="Ville de résidence")
    street: Optional[str] = Field(None, max_length=255, description="Rue / adresse")
    
    @field_validator('birthdate', mode='before')
    def validate_birthdate(cls, v):
        if v and isinstance(v, str):
            try:
                return date.fromisoformat(v)
            except ValueError:
                raise ValueError("Date de naissance invalide. Format attendu: YYYY-MM-DD")
        return v


class DriverSchema(BaseModel):
    """Conducteur - Champs obligatoires selon version 1.2"""
    name: str = Field(..., max_length=255, description="Nom et prénom du conducteur")
    birthdate: date = Field(..., description="Date de naissance du conducteur")
    licence_number: str = Field(..., max_length=50, description="Numéro du permis")
    licence_category: str = Field(..., max_length=10, description="Catégorie du permis")
    licence_issued_at: date = Field(..., description="Date de délivrance du permis")
    licence_issued_by: Optional[str] = Field(None, max_length=255, description="Autorité de délivrance")
    
    @field_validator('birthdate', 'licence_issued_at', mode='before')
    def validate_dates(cls, v):
        if v and isinstance(v, str):
            try:
                return date.fromisoformat(v)
            except ValueError:
                raise ValueError(f"Date invalide: {v}. Format attendu: YYYY-MM-DD")
        return v


class VehicleSchema(BaseModel):
    """Véhicule"""
    # Identification
    licence_plate: str = Field(..., max_length=20, description="Immatriculation")
    chassis: str = Field(..., max_length=50, description="Numéro de châssis")
    brand: str = Field(..., max_length=100, description="Marque")
    model: str = Field(..., max_length=100, description="Modèle")
    first_registration_date: Optional[date] = Field(None, description="Date 1ère mise en circulation")
    
    # Classification
    category: VehicleCategory = Field(..., description="Catégorie du véhicule")
    genre: VehicleGenre = Field(..., description="Genre du véhicule")
    type: VehicleType = Field(..., description="Type de véhicule")
    usage: VehicleUsage = Field(..., description="Usage du véhicule")
    energy: VehicleEnergy = Field(..., description="Type d'énergie")
    circulation_zone: CirculationZone = Field(..., description="Zone de circulation")
    nb_of_doors: Optional[int] = Field(None, ge=1, le=10, description="Nombre de portes")
    
    # Caractéristiques
    nb_of_seats: int = Field(..., ge=1, le=100, description="Nombre de places")
    fiscal_power: int = Field(..., ge=1, le=1000, description="Puissance fiscale (CV)")
    displacement: Optional[int] = Field(None, ge=50, le=10000, description="Cylindrée (cm³)")
    gross_weight: Optional[int] = Field(None, ge=0, le=100000, description="PTAC (kg)")
    payload_capacity: Optional[int] = Field(None, ge=0, le=50000, description="Charge utile (kg)")
    
    # Options
    is_utility: Optional[bool] = Field(False, description="Véhicule utilitaire")
    has_trailer: bool = Field(False, description="Présence d'une remorque")
    trailer_flammable: bool = Field(False, description="Remorque matières inflammables")
    trailer_licence_plate: Optional[str] = Field(None, max_length=20, description="Immatriculation remorque")
    dual_control: bool = Field(False, description="Double commande (auto-école)")
    engine_type: bool = Field(False, description="Type d'engin (portuaire)")
    civil_liability: bool = Field(False, description="RC élèves (auto-école)")
    
    @field_validator('first_registration_date', mode='before')
    def validate_registration_date(cls, v):
        if v and isinstance(v, str):
            try:
                return date.fromisoformat(v)
            except ValueError:
                raise ValueError("Date 1ère mise en circulation invalide")
        return v


class ProductionItemSchema(BaseModel):
    """Élément de production individuel"""
    # Attestation et contrat
    certificate_variant_code: CertificateVariant = Field(..., description="Couleur de l'attestation")
    police_number: str = Field(..., max_length=50, description="Numéro de police")
    starts_at: date = Field(..., description="Date d'effet")
    ends_at: date = Field(..., description="Date d'échéance")
    issued_at: Optional[date] = Field(None, description="Date d'émission")
    rc: int = Field(..., ge=0, description="Montant RC (FCFA)")
    dta: int = Field(..., ge=0, description="Montant DTA")
    fleet_discount: Optional[int] = Field(None, ge=0, le=100, description="Réduction flotte (%)")
    
    # Souscripteur
    customer_name: str = Field(..., max_length=255)
    customer_phone: str = Field(..., max_length=50)
    customer_type: CustomerType
    customer_email: Optional[str] = Field(None, max_length=255)
    customer_postal_code: Optional[str] = Field(None, max_length=100)
    
    # Assuré
    insured_name: str = Field(..., max_length=255)
    insured_phone: str = Field(..., max_length=50)
    insured_email: str = Field(..., max_length=255)
    insured_postal_code: str = Field(..., max_length=100)
    insured_code: str = Field(..., max_length=50)
    insured_profession: InsuredProfession
    insured_birthdate: Optional[date] = None
    insured_city: str = Field(..., max_length=100)
    insured_street: Optional[str] = Field(None, max_length=255)
    
    # Conducteur
    driver_name: str = Field(..., max_length=255)
    driver_birthdate: date
    driver_licence_number: str = Field(..., max_length=50)
    driver_licence_category: str = Field(..., max_length=10)
    driver_licence_issued_at: date
    driver_licence_issued_by: Optional[str] = Field(None, max_length=255)
    
    # Véhicule
    licence_plate: str = Field(..., max_length=20)
    vehicle_chassis: str = Field(..., max_length=50)
    vehicle_brand: str = Field(..., max_length=100)
    vehicle_model: str = Field(..., max_length=100)
    vehicle_first_registration_date: Optional[date] = None
    vehicle_category: VehicleCategory
    vehicle_genre: VehicleGenre
    vehicle_type: VehicleType
    vehicle_usage: VehicleUsage
    vehicle_energy: VehicleEnergy
    circulation_zone: CirculationZone
    nb_of_doors: Optional[int] = Field(None, ge=1, le=10)
    nb_of_seats: int = Field(..., ge=1, le=100)
    fiscal_power: int = Field(..., ge=1, le=1000)
    vehicle_displacement: Optional[int] = Field(None, ge=50, le=10000)
    vehicle_gross_weight: Optional[int] = Field(None, ge=0, le=100000)
    payload_capacity: Optional[int] = Field(None, ge=0, le=50000)
    vehicle_is_utility: Optional[bool] = False
    vehicle_has_trailer: bool = False
    trailer_flammable: bool = False
    trailer_licence_plate: Optional[str] = Field(None, max_length=20)
    vehicle_dual_control: bool = False
    vehicle_engine_type: bool = False
    civil_liability: bool = False
    
    # Fiscal
    taxpayer_number: str = Field(..., max_length=50, description="Numéro contribuable")
    
    # ========== VALIDATEURS ==========
    
    @field_validator('starts_at', 'ends_at', mode='before')
    def validate_dates(cls, v):
        if v and isinstance(v, str):
            try:
                return date.fromisoformat(v)
            except ValueError:
                raise ValueError(f"Date invalide: {v}. Format attendu: YYYY-MM-DD")
        return v
    
    @model_validator(mode='after')
    def validate_contract_duration(self):
        """Valide la durée du contrat (1 à 365 jours)"""
        if self.starts_at and self.ends_at:
            delta = (self.ends_at - self.starts_at).days
            if delta < 1:
                raise ValueError("La durée du contrat doit être d'au moins 1 jour")
            if delta > 365:
                raise ValueError("La durée du contrat ne doit pas excéder 365 jours")
        return self
    
    @model_validator(mode='after')
    def validate_trailer_license(self):
        """Valide l'immatriculation de la remorque"""
        if self.vehicle_has_trailer and not self.trailer_licence_plate:
            raise ValueError("L'immatriculation de la remorque est requise")
        return self
    
    @model_validator(mode='after')
    def validate_gross_weight(self):
        """Valide la charge utile si PTAC > 3.5T"""
        if self.vehicle_gross_weight and self.vehicle_gross_weight > 3500:
            if not self.payload_capacity or self.payload_capacity == 0:
                raise ValueError("La charge utile est requise pour PTAC > 3500 kg")
        return self
    
    @model_validator(mode='after')
    def validate_displacement(self):
        """Valide la cylindrée pour les 2/3 roues"""
        if self.vehicle_category == VehicleCategory.DEUX_TROIS_ROUES:
            if not self.vehicle_displacement or self.vehicle_displacement == 0:
                raise ValueError("La cylindrée est requise pour la catégorie 05 (2/3 roues)")
        return self


class ProductionRequestSchema(BaseModel):
    """Requête complète de production"""
    office_code: str = Field(..., max_length=50, description="Code du bureau")
    organization_code: str = Field(..., max_length=50, description="Code de la compagnie")
    certificate_type: CertificateType = Field(default=CertificateType.CIMA, description="Type d'attestation")
    channel: str = Field(default="api", max_length=20, description="Canal d'origine")
    productions: List[ProductionItemSchema] = Field(
        ..., 
        min_length=1, 
        max_length=1000,
        description="Liste des attestations à produire"
    )


# ============================================================================
# SCHÉMAS DE RÉPONSE
# ============================================================================

class CertificateResponseSchema(BaseModel):
    """Attestation dans la réponse"""
    reference: str
    download_link: str
    licence_plate: str
    chassis_number: str
    police_number: str
    insured_name: str
    insured_phone: str
    starts_at: str
    ends_at: str
    child_certificate: Optional[Dict[str, Any]] = None


class ProductionResponseSchema(BaseModel):
    """Réponse de production"""
    id: str
    reference: str
    channel: str
    quantity: int
    sent_to_storage: Optional[bool] = None
    download_link: str
    certificates: List[CertificateResponseSchema]
    created_at: datetime
    formatted_created_at: str


class SuccessResponseSchema(BaseModel):
    """Réponse de succès"""
    status: int = 201
    message: str
    data: ProductionResponseSchema


class ErrorResponseSchema(BaseModel):
    """Réponse d'erreur"""
    message: str
    errors: Optional[Dict[str, List[str]]] = None