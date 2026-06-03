# addons/Automobiles/api/services/business_rules.py
"""
Règles métier avancées (Étape 2 de la documentation)
- Unicité des immatriculations avec contrats existants
- Validation selon type de personne (physique/morale)
- Validation selon catégorie de véhicule
- Validation des champs obligatoires spécifiques
"""

from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
import logging

from .. import models_db
from ..schemas import (
    ProductionItemSchema, CustomerType, VehicleCategory,
    InsuredProfession
)

logger = logging.getLogger(__name__)


class BusinessRuleError(Exception):
    """Exception pour les erreurs de règles métier"""
    def __init__(self, errors: Dict[str, List[str]]):
        self.errors = errors
        super().__init__(str(errors))


class BusinessRuleValidator:
    """Validateur des règles métier"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def validate_production_item(
        self, 
        prod: ProductionItemSchema, 
        idx: int,
        errors: Dict[str, List[str]]
    ):
        """
        Valide toutes les règles métier pour un élément de production
        """
        prefix = f"productions.{idx}"
        
        # 1. Validation selon le type de personne (physique/morale)
        self._validate_person_type_rules(prod, prefix, errors)
        
        # 2. Validation selon la catégorie de véhicule
        self._validate_vehicle_category_rules(prod, prefix, errors)
        
        # 3. Vérification de l'unicité de l'immatriculation
        self._validate_unique_licence_plate(prod, prefix, errors)
        
        # 4. Validation de la remorque
        self._validate_trailer_rules(prod, prefix, errors)
        
        # 5. Validation du PTAC et charge utile
        self._validate_gross_weight_rules(prod, prefix, errors)
        
        # 6. Validation de la cylindrée pour 2/3 roues
        self._validate_displacement_rules(prod, prefix, errors)
        
        # 7. Validation des dates de contrat
        self._validate_contract_dates(prod, prefix, errors)
    
    def _validate_person_type_rules(self, prod: ProductionItemSchema, prefix: str, errors: Dict):
        """
        Validation selon le type de personne (section 6.2.3)
        
        Pour les personnes physiques:
        - insured_birthdate (date de naissance de l'assuré)
        - driver_name, driver_birthdate, driver_licence_number
        - driver_licence_category, driver_licence_issued_at
        
        Pour les personnes morales: ces champs sont optionnels
        """
        is_physical = prod.customer_type == CustomerType.PHYSICAL
        
        if is_physical:
            # Champs obligatoires pour les personnes physiques
            if not prod.insured_birthdate:
                errors[f"{prefix}.insured_birthdate"] = [
                    "La date de naissance de l'assuré est obligatoire pour les personnes physiques."
                ]
            
            if not prod.driver_name or prod.driver_name.strip() == "":
                errors[f"{prefix}.driver_name"] = [
                    "Le nom du conducteur est obligatoire pour les personnes physiques."
                ]
            
            if not prod.driver_birthdate:
                errors[f"{prefix}.driver_birthdate"] = [
                    "La date de naissance du conducteur est obligatoire pour les personnes physiques."
                ]
            
            if not prod.driver_licence_number or prod.driver_licence_number.strip() == "":
                errors[f"{prefix}.driver_licence_number"] = [
                    "Le numéro du permis de conduire est obligatoire pour les personnes physiques."
                ]
            
            if not prod.driver_licence_category or prod.driver_licence_category.strip() == "":
                errors[f"{prefix}.driver_licence_category"] = [
                    "La catégorie du permis est obligatoire pour les personnes physiques."
                ]
            
            if not prod.driver_licence_issued_at:
                errors[f"{prefix}.driver_licence_issued_at"] = [
                    "La date de délivrance du permis est obligatoire pour les personnes physiques."
                ]
    
    def _validate_vehicle_category_rules(self, prod: ProductionItemSchema, prefix: str, errors: Dict):
        """
        Validation selon la catégorie de véhicule (section 6.2.4)
        """
        category = prod.vehicle_category
        
        # Catégorie 02: Transport pour propre compte - PTAC requis
        if category == VehicleCategory.TRANSPORT_PROPRE:
            if not prod.vehicle_gross_weight or prod.vehicle_gross_weight == 0:
                errors[f"{prefix}.vehicle_gross_weight"] = [
                    "Le PTAC est requis pour la catégorie 02 (Transport pour propre compte)."
                ]
        
        # Catégorie 03: Transport public de marchandises - PTAC requis
        elif category == VehicleCategory.TRANSPORT_MARCHANDISES:
            if not prod.vehicle_gross_weight or prod.vehicle_gross_weight == 0:
                errors[f"{prefix}.vehicle_gross_weight"] = [
                    "Le PTAC est requis pour la catégorie 03 (Transport public de marchandises)."
                ]
        
        # Catégorie 05: 2/3 roues - Cylindrée requise
        elif category == VehicleCategory.DEUX_TROIS_ROUES:
            if not prod.vehicle_displacement or prod.vehicle_displacement == 0:
                errors[f"{prefix}.vehicle_displacement"] = [
                    "La cylindrée est requise pour la catégorie 05 (Véhicule motorisé à 2 ou 3 roues)."
                ]
        
        # Catégorie 06: Garagistes - Responsabilité civile requise
        elif category == VehicleCategory.GARAGISTE:
            if not prod.civil_liability:
                errors[f"{prefix}.civil_liability"] = [
                    "La garantie Responsabilité Civile est requise pour les garagistes (catégorie 06)."
                ]
        
        # Catégorie 07: Auto-école - Double commande requise
        elif category == VehicleCategory.AUTO_ECOLE:
            if not prod.vehicle_dual_control:
                errors[f"{prefix}.vehicle_dual_control"] = [
                    "La double commande est requise pour les véhicules d'auto-école (catégorie 07)."
                ]
        
        # Catégorie 08: Location - Champ utilitaire requis
        elif category == VehicleCategory.LOCATION:
            if prod.vehicle_is_utility is None:
                errors[f"{prefix}.vehicle_is_utility"] = [
                    "Le champ 'véhicule utilitaire' est requis pour les véhicules de location (catégorie 08)."
                ]
        
        # Catégorie 09: Engin de chantier - Type d'engin requis
        elif category == VehicleCategory.ENGIN_CHANTIER:
            if not prod.vehicle_engine_type:
                errors[f"{prefix}.vehicle_engine_type"] = [
                    "Le type d'engin est requis pour les engins de chantier (catégorie 09)."
                ]
    
    def _validate_unique_licence_plate(self, prod: ProductionItemSchema, prefix: str, errors: Dict):
        """
        Vérification de l'unicité de l'immatriculation (section 6.2.2)
        
        Un véhicule ne peut pas avoir deux attestations valides sur la même période.
        """
        try:
            # Chercher les contrats actifs pour cette immatriculation
            existing_certificates = self.db.query(models_db.Certificate).filter(
                models_db.Certificate.licence_plate == prod.licence_plate,
                models_db.Certificate.state == "active",
                models_db.Certificate.ends_at >= date.today()
            ).all()
            
            for cert in existing_certificates:
                # Vérifier le chevauchement des dates
                if not (prod.ends_at < cert.starts_at or prod.starts_at > cert.ends_at):
                    errors[f"{prefix}.licence_plate"] = [
                        f"Le véhicule immatriculé {prod.licence_plate} a une attestation valide "
                        f"jusqu'au {cert.ends_at.strftime('%d/%m/%Y')}. "
                        f"Veuillez choisir une date d'effet commençant à partir du "
                        f"{(cert.ends_at + timedelta(days=1)).strftime('%d/%m/%Y')}."
                    ]
                    break
                    
        except Exception as e:
            logger.error(f"Erreur lors de la vérification d'unicité: {e}")
    
    def _validate_trailer_rules(self, prod: ProductionItemSchema, prefix: str, errors: Dict):
        """
        Validation des règles liées à la remorque (section 6.2.6)
        
        Si vehicle_has_trailer = true, alors trailer_licence_plate est obligatoire
        """
        if prod.vehicle_has_trailer:
            if not prod.trailer_licence_plate or prod.trailer_licence_plate.strip() == "":
                errors[f"{prefix}.trailer_licence_plate"] = [
                    "L'immatriculation de la remorque est requise lorsqu'une remorque est déclarée."
                ]
    
    def _validate_gross_weight_rules(self, prod: ProductionItemSchema, prefix: str, errors: Dict):
        """
        Validation du PTAC et charge utile (section 6.2.7)
        
        Lorsque PTAC > 3500 kg, payload_capacity est obligatoire
        """
        if prod.vehicle_gross_weight and prod.vehicle_gross_weight > 3500:
            if not prod.payload_capacity or prod.payload_capacity == 0:
                errors[f"{prefix}.payload_capacity"] = [
                    "La charge utile est requise lorsque le PTAC dépasse 3500 kg."
                ]
    
    def _validate_displacement_rules(self, prod: ProductionItemSchema, prefix: str, errors: Dict):
        """
        Validation de la cylindrée (section 6.2.5)
        
        vehicle_first_registration_date est obligatoire pour toutes les catégories
        sauf la catégorie 06 (garagistes)
        """
        if prod.vehicle_category != VehicleCategory.GARAGISTE:
            if not prod.vehicle_first_registration_date:
                errors[f"{prefix}.vehicle_first_registration_date"] = [
                    "La date de première mise en circulation est obligatoire pour cette catégorie."
                ]
    
    def _validate_contract_dates(self, prod: ProductionItemSchema, prefix: str, errors: Dict):
        """
        Validation supplémentaire des dates de contrat
        """
        # Vérifier que la date d'émission n'est pas dans le futur
        if prod.issued_at and prod.issued_at > date.today():
            errors[f"{prefix}.issued_at"] = [
                "La date d'émission ne peut pas être dans le futur."
            ]
        
        # Vérifier que la date d'effet est antérieure à la date d'échéance
        if prod.starts_at and prod.ends_at and prod.starts_at >= prod.ends_at:
            errors[f"{prefix}.ends_at"] = [
                "La date d'échéance doit être postérieure à la date d'effet."
            ]
    
    def validate_batch(
        self, 
        productions: List[ProductionItemSchema]
    ) -> Tuple[bool, Optional[Dict[str, List[str]]]]:
        """
        Valide toutes les productions du lot
        """
        errors = {}
        
        for idx, prod in enumerate(productions):
            self.validate_production_item(prod, idx, errors)
        
        return len(errors) == 0, errors if errors else None


from datetime import timedelta


class AdditionalValidators:
    """Validateurs supplémentaires"""
    
    @staticmethod
    def validate_insured_age(birthdate: date, min_age: int = 18, max_age: int = 120) -> Tuple[bool, Optional[str]]:
        """
        Valide l'âge de l'assuré
        """
        if not birthdate:
            return True, None
        
        today = date.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        
        if age < min_age:
            return False, f"L'assuré doit avoir au moins {min_age} ans."
        
        if age > max_age:
            return False, f"L'âge maximum de l'assuré est {max_age} ans."
        
        return True, None
    
    @staticmethod
    def validate_driver_age(birthdate: date, min_age: int = 18, max_age: int = 80) -> Tuple[bool, Optional[str]]:
        """
        Valide l'âge du conducteur
        """
        if not birthdate:
            return True, None
        
        today = date.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        
        if age < min_age:
            return False, f"Le conducteur doit avoir au moins {min_age} ans."
        
        if age > max_age:
            return False, f"L'âge maximum du conducteur est {max_age} ans."
        
        return True, None
    
    @staticmethod
    def validate_licence_experience(issued_at: date, min_years: int = 1) -> Tuple[bool, Optional[str]]:
        """
        Valide l'ancienneté du permis de conduire
        """
        if not issued_at:
            return True, None
        
        today = date.today()
        years = today.year - issued_at.year - ((today.month, today.day) < (issued_at.month, issued_at.day))
        
        if years < min_years:
            return False, f"Le permis de conduire doit avoir au moins {min_years} an(s) d'ancienneté."
        
        return True, None