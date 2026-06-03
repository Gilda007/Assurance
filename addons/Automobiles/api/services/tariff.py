# addons/Automobiles/api/services/tariff.py
"""
Service de calcul et contrôle tarifaire RC (Étape 3 de la documentation)
Barème officiel de l'association ASAC
"""

from typing import Dict, Any, Tuple, Optional
from datetime import date
import logging

from ..schemas import ProductionItemSchema, VehicleCategory, CirculationZone

logger = logging.getLogger(__name__)


class TariffError(Exception):
    """Exception pour les erreurs de tarif"""
    def __init__(self, message: str, expected: int, provided: int):
        self.message = message
        self.expected = expected
        self.provided = provided
        super().__init__(message)


class TariffMatrix:
    """
    Matrice tarifaire RC selon le barème ASAC
    
    Structure: 
    - Catégorie du véhicule
    - Zone de circulation (A, B, C)
    - Tranche de puissance fiscale
    - Option remorque
    """
    
    # Barème RC en FCFA (données indicatives, à remplacer par le barème officiel)
    TARIFFS = {
        # Catégorie 01: Véhicule de tourisme (Personne physique)
        "01": {
            "A": {
                # Puissance fiscale: (min_cv, max_cv, montant)
                (0, 4): 37800,
                (5, 7): 63784,
                (8, 10): 88450,
                (11, 13): 125600,
                (14, 100): 189200,
            },
            "B": {
                (0, 4): 32400,
                (5, 7): 54672,
                (8, 10): 75800,
                (11, 13): 107600,
                (14, 100): 162200,
            },
            "C": {
                (0, 4): 27000,
                (5, 7): 45560,
                (8, 10): 63150,
                (11, 13): 89600,
                (14, 100): 135200,
            }
        },
        
        # Catégorie 02: Transport pour propre compte
        "02": {
            "A": {
                (0, 4): 48600,
                (5, 7): 81950,
                (8, 10): 113600,
                (11, 13): 161300,
                (14, 100): 243000,
            },
            "B": {
                (0, 4): 41650,
                (5, 7): 70250,
                (8, 10): 97400,
                (11, 13): 138300,
                (14, 100): 208300,
            },
            "C": {
                (0, 4): 34700,
                (5, 7): 58550,
                (8, 10): 81150,
                (11, 13): 115200,
                (14, 100): 173700,
            }
        },
        
        # Catégorie 03: Transport public de marchandises
        "03": {
            "A": {
                (0, 4): 56700,
                (5, 7): 95600,
                (8, 10): 132500,
                (11, 13): 188200,
                (14, 100): 283500,
            },
            "B": {
                (0, 4): 48600,
                (5, 7): 81950,
                (8, 10): 113600,
                (11, 13): 161300,
                (14, 100): 243000,
            },
            "C": {
                (0, 4): 40500,
                (5, 7): 68300,
                (8, 10): 94650,
                (11, 13): 134400,
                (14, 100): 202500,
            }
        },
        
        # Catégorie 04: Transport public de voyageurs
        "04": {
            "A": {
                (0, 4): 63200,
                (5, 7): 106600,
                (8, 10): 147800,
                (11, 13): 209900,
                (14, 100): 316000,
            },
            "B": {
                (0, 4): 54200,
                (5, 7): 91400,
                (8, 10): 126700,
                (11, 13): 179900,
                (14, 100): 271000,
            },
            "C": {
                (0, 4): 45200,
                (5, 7): 76200,
                (8, 10): 105600,
                (11, 13): 149900,
                (14, 100): 226000,
            }
        },
        
        # Catégorie 05: 2/3 roues (utilise la cylindrée au lieu de la puissance)
        "05": {
            "A": {
                (0, 125): 18750,
                (126, 250): 31250,
                (251, 500): 43750,
                (501, 1000): 62500,
            },
            "B": {
                (0, 125): 16070,
                (126, 250): 26790,
                (251, 500): 37500,
                (501, 1000): 53570,
            },
            "C": {
                (0, 125): 13390,
                (126, 250): 22320,
                (251, 500): 31250,
                (501, 1000): 44640,
            }
        },
        
        # Catégorie 06: Garagistes
        "06": {
            "A": { (0, 1000): 85000 },
            "B": { (0, 1000): 72850 },
            "C": { (0, 1000): 60700 },
        },
        
        # Catégorie 07: Auto-école
        "07": {
            "A": { (0, 1000): 94800 },
            "B": { (0, 1000): 81250 },
            "C": { (0, 1000): 67700 },
        },
        
        # Catégorie 08: Location
        "08": {
            "A": { (0, 4): 48600, (5, 7): 81950, (8, 10): 113600, (11, 100): 189200 },
            "B": { (0, 4): 41650, (5, 7): 70250, (8, 10): 97400, (11, 100): 162200 },
            "C": { (0, 4): 34700, (5, 7): 58550, (8, 10): 81150, (11, 100): 135200 },
        },
        
        # Catégorie 09: Engin de chantier
        "09": {
            "A": { (0, 1000): 125000 },
            "B": { (0, 1000): 107150 },
            "C": { (0, 1000): 89250 },
        },
        
        # Catégorie 10: Véhicules spéciaux
        "10": {
            "A": { (0, 1000): 110000 },
            "B": { (0, 1000): 94300 },
            "C": { (0, 1000): 78550 },
        },
        
        # Catégorie 12: Véhicule de tourisme (Personne morale)
        "12": {
            "A": { (0, 4): 43200, (5, 7): 72850, (8, 10): 101000, (11, 100): 168500 },
            "B": { (0, 4): 37050, (5, 7): 62450, (8, 10): 86550, (11, 100): 144500 },
            "C": { (0, 4): 30850, (5, 7): 52050, (8, 10): 72150, (11, 100): 120500 },
        }
    }
    
    # Suppléments pour remorque (%) 
    TRAILER_SURCHARGE = 1.25  # +25%
    
    # Réduction pour double commande (auto-école)
    DUAL_CONTROL_DISCOUNT = 0.9  # -10%
    
    # Coefficient pour les zones
    ZONE_COEFFICIENTS = {
        "A": 1.0,
        "B": 0.857,
        "C": 0.714,
    }
    
    @classmethod
    def get_rc_amount(
        cls, 
        category: str, 
        zone: str, 
        fiscal_power: int,
        has_trailer: bool = False,
        displacement: Optional[int] = None,
        dual_control: bool = False
    ) -> int:
        """
        Calcule le montant RC selon le barème
        
        Args:
            category: Catégorie du véhicule (01, 02, etc.)
            zone: Zone de circulation (A, B, C)
            fiscal_power: Puissance fiscale en CV
            has_trailer: Présence d'une remorque
            displacement: Cylindrée (pour les 2/3 roues)
            dual_control: Double commande (auto-école)
            
        Returns:
            Montant RC en FCFA
        """
        # Vérifier que la catégorie existe
        if category not in cls.TARIFFS:
            logger.warning(f"Catégorie {category} non trouvée, utilisation de la catégorie 01")
            category = "01"
        
        # Vérifier que la zone existe
        if zone not in cls.TARIFFS[category]:
            logger.warning(f"Zone {zone} non trouvée pour catégorie {category}, utilisation zone A")
            zone = "A"
        
        # Trouver la bonne tranche
        amount = cls._find_tariff(category, zone, fiscal_power, displacement)
        
        # Appliquer les suppléments/réductions
        if has_trailer:
            amount = int(amount * cls.TRAILER_SURCHARGE)
        
        if dual_control:
            amount = int(amount * cls.DUAL_CONTROL_DISCOUNT)
        
        return amount
    
    @classmethod
    def _find_tariff(cls, category: str, zone: str, fiscal_power: int, displacement: Optional[int] = None) -> int:
        """Trouve le tarif correspondant à la puissance/cylindrée"""
        tariffs = cls.TARIFFS[category][zone]
        
        # Pour les 2/3 roues, utiliser la cylindrée
        if category == "05" and displacement:
            for (min_val, max_val), amount in tariffs.items():
                if min_val <= displacement <= max_val:
                    return amount
        else:
            # Pour les autres catégories, utiliser la puissance fiscale
            for (min_cv, max_cv), amount in tariffs.items():
                if min_cv <= fiscal_power <= max_cv:
                    return amount
        
        # Si aucune tranche trouvée, prendre la dernière
        last_amount = list(tariffs.values())[-1]
        logger.warning(f"Tranche non trouvée pour CV={fiscal_power}, utilisation du dernier tarif: {last_amount}")
        return last_amount


class TariffCalculator:
    """Calculateur de primes RC"""
    
    def __init__(self, db_session=None):
        self.db_session = db_session
    
    def calculate_rc(self, production: ProductionItemSchema) -> Dict[str, Any]:
        """
        Calcule le montant RC attendu pour une production
        
        Returns:
            Dict contenant le montant calculé et les détails
        """
        # Récupérer les paramètres
        category = production.vehicle_category
        zone = production.circulation_zone
        fiscal_power = production.fiscal_power
        has_trailer = production.vehicle_has_trailer
        displacement = production.vehicle_displacement
        dual_control = production.vehicle_dual_control
        
        # Calculer le montant de base
        base_amount = TariffMatrix.get_rc_amount(
            category=category,
            zone=zone,
            fiscal_power=fiscal_power,
            has_trailer=has_trailer,
            displacement=displacement,
            dual_control=dual_control
        )
        
        # Calculer le prorata si applicable
        prorata = 1.0
        if production.starts_at and production.ends_at:
            days = (production.ends_at - production.starts_at).days
            if days < 365:
                prorata = days / 365.0
        
        final_amount = int(base_amount * prorata)
        
        return {
            "base_amount": base_amount,
            "prorata": prorata,
            "calculated_amount": final_amount,
            "provided_amount": production.rc,
            "is_valid": final_amount == production.rc,
            "category": category,
            "zone": zone,
            "fiscal_power": fiscal_power,
            "has_trailer": has_trailer,
            "dual_control": dual_control
        }


class TariffController:
    """Contrôleur pour la validation tarifaire (Étape 3)"""
    
    def __init__(self, db_session=None):
        self.calculator = TariffCalculator(db_session)
    
    def validate_rc_amount(self, production: ProductionItemSchema, idx: int) -> Tuple[bool, Optional[Dict]]:
        """
        Valide le montant RC soumis
        
        Returns:
            (is_valid, error_details)
        """
        result = self.calculator.calculate_rc(production)
        
        if not result["is_valid"]:
            error_detail = {
                "productions": [{
                    "index": idx,
                    "expected": result["calculated_amount"],
                    "provided": result["provided_amount"],
                    "message": f"Le montant de la prime RC ({result['provided_amount']}) ne correspond pas "
                              f"au barème tarifaire attendu ({result['calculated_amount']})."
                }]
            }
            return False, error_detail
        
        return True, None
    
    def validate_batch(self, productions: list) -> Tuple[bool, Optional[Dict]]:
        """
        Valide les montants RC pour tout un lot
        """
        errors = []
        
        for idx, production in enumerate(productions):
            is_valid, error = self.validate_rc_amount(production, idx)
            if not is_valid:
                errors.append(error)
        
        if errors:
            return False, {"errors": errors}
        
        return True, None


class AdditionalSurcharges:
    """Suppléments et réductions supplémentaires"""
    
    # Réduction pour les jeunes conducteurs (0-2 ans de permis)
    YOUNG_DRIVER_SURCHARGE = {
        0: 1.50,   # 0-1 an: +50%
        1: 1.25,   # 1-2 ans: +25%
        2: 1.10,   # 2-3 ans: +10%
    }
    
    # Réduction pour les conducteurs expérimentés
    EXPERIENCED_DRIVER_DISCOUNT = {
        5: 0.95,   # 5-10 ans: -5%
        10: 0.90,  # 10-15 ans: -10%
        15: 0.85,  # 15-20 ans: -15%
        20: 0.80,  # 20+ ans: -20%
    }
    
    # Réduction pour les véhicules équipés
    EQUIPMENT_DISCOUNTS = {
        "ABS": 0.98,      # -2%
        "AIRBAG": 0.98,   # -2%
        "ALARM": 0.97,    # -3%
        "GPS": 0.99,      # -1%
    }
    
    @classmethod
    def get_driver_experience_discount(cls, years_of_experience: int) -> float:
        """
        Calcule la réduction basée sur l'expérience du conducteur
        """
        for threshold, discount in sorted(cls.EXPERIENCED_DRIVER_DISCOUNT.items(), reverse=True):
            if years_of_experience >= threshold:
                return discount
        return 1.0
    
    @classmethod
    def get_young_driver_surcharge(cls, years_of_experience: int) -> float:
        """
        Calcule la surprime pour les jeunes conducteurs
        """
        if years_of_experience in cls.YOUNG_DRIVER_SURCHARGE:
            return cls.YOUNG_DRIVER_SURCHARGE[years_of_experience]
        return 1.0