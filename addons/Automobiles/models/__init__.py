# addons/Automobiles/models/__init__.py

"""
Package des modèles Automobiles
"""

from core.database import Base

# ============================================
# IMPORTS DE TOUS LES MODÈLES
# ============================================

# Modèles existants
from addons.Automobiles.models.contract_models import Contrat, ContractStatus
from addons.Automobiles.models.contact_models import Contact, ContactAuditLog
from addons.Automobiles.models.flottes_models import Fleet, AuditFlotteLog
from addons.Automobiles.models.compagnies_models import Compagnie
from addons.Automobiles.models.tarif_models import AutomobileTarif
from addons.Automobiles.models.automobile_tranche import AutomobileTranche
from addons.Automobiles.models.paiement_models import Paiement
from addons.Automobiles.models.driver_models import Driver
from addons.Automobiles.models.sinistre_models import Sinistre, Indemnisation, StatutSinistre, TypeSinistre
from addons.Automobiles.models.expertise_models import Expertise, TypeExpertise, StatutExpertise
from addons.Automobiles.models.garage_models import Garage, Intervention, TypeGarage, StatutAgrement

# Modèles Vehicle (tous dans automobile_models.py)
from addons.Automobiles.models.automobile_models import (
    Vehicle,
    AuditVehicleLog,
    VehicleCategory,
    VehicleGenre,
    VehicleType,
    VehicleUsage,
    VehicleEnergy,
    CirculationZone,
    VehicleCategoryRef,
    VehicleGenreRef,
    VehicleTypeRef,
    VehicleUsageRef,
    VehicleEnergyRef,
    VehicleZoneRef,
    VehicleGuarantee,
    VehicleGuaranteeReduction,
    VehicleGuaranteeRate,
    VehicleGuaranteeOption,
    VehicleFleetGuarantee,
    VehicleClassification,
)

# Exposer tous les modèles
__all__ = [
    'Base',
    'Contact',
    'ContactAuditLog',
    'Compagnie',
    'Fleet',
    'AuditFlotteLog',
    'Driver',
    'Contrat',
    'ContractStatus',
    'AutomobileTarif',
    'AutomobileTranche',
    'Paiement',
    'Vehicle',
    'AuditVehicleLog',
    'VehicleCategory',
    'VehicleGenre',
    'VehicleType',
    'VehicleUsage',
    'VehicleEnergy',
    'CirculationZone',
    'VehicleCategoryRef',
    'VehicleGenreRef',
    'VehicleTypeRef',
    'VehicleUsageRef',
    'VehicleEnergyRef',
    'VehicleZoneRef',
    'VehicleGuarantee',
    'VehicleGuaranteeReduction',
    'VehicleGuaranteeRate',
    'VehicleGuaranteeOption',
    'VehicleFleetGuarantee',
    'VehicleClassification',
]