# addons/Automobiles/controllers/api_asac_controller.py
"""
Contrôleur pour l'intégration avec l'API ASAC
"""

import requests
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from addons.Automobiles.controllers.automobile_controller import VehicleController
from addons.Automobiles.models.contract_models import Contrat, ContractStatus

logger = logging.getLogger(__name__)


class ASACAPIController:
    """Contrôleur pour l'API ASAC"""
    
    def __init__(self, db_session: Session = None, user_id: int = None):
        self.db_session = db_session
        self.user_id = user_id
        self.controller = VehicleController(db_session)
        self.base_url = "https://api.asac.cm/v1"  # À configurer
        self.api_key = None  # À configurer
        
    def prepare_contract_data(self, contract_id: int) -> Dict[str, Any]:
        """Prépare les données d'un contrat pour l'envoi à l'API ASAC"""
        contract = self.controller.get_contract(contract_id)
        if not contract:
            raise ValueError(f"Contrat {contract_id} non trouvé")
        
        vehicle = self.controller.get_vehicle(contract.vehicle_id) if contract.vehicle_id else None
        owner = self.controller.get_contact(contract.owner_id)
        drivers = self.controller.get_drivers_by_contract(contract_id)
        
        # Structure selon la documentation API
        data = {
            # Section 3.2 - Contrat
            "certificate_variant_code": "auto",  # auto, moto, pooltpv
            "police_number": contract.numero_police,
            "starts_at": contract.date_debut.strftime("%Y-%m-%d") if contract.date_debut else None,
            "ends_at": contract.date_fin.strftime("%Y-%m-%d") if contract.date_fin else None,
            "issued_at": contract.created_at.strftime("%Y-%m-%d") if contract.created_at else None,
            "rc_prime": contract.prime_pure,
            "dta": 0,  # À calculer
            "fleet_discount": contract.fleet_discount or 0,
            
            # Section 3.3 - Souscripteur
            "customer_name": owner.customer_name if owner else None,
            "customer_phone": owner.customer_phone if owner else None,
            "customer_email": owner.customer_email if owner else None,
            "customer_postal_code": owner.customer_postal_code if owner else None,
            "customer_type": owner.customer_type.value if owner and owner.customer_type else None,
            
            # Section 3.3 - Assuré
            "insured_name": owner.insured_name if owner else None,
            "insured_phone": owner.insured_phone if owner else None,
            "insured_email": owner.insured_email if owner else None,
            "insured_postal_code": owner.insured_postal_code if owner else None,
            "insured_code": owner.insured_code if owner else None,
            "insured_profession": owner.insured_profession.value if owner and owner.insured_profession else None,
            "insured_birthdate": owner.insured_birthdate.strftime("%Y-%m-%d") if owner and owner.insured_birthdate else None,
            "insured_city": owner.insured_city if owner else None,
            "insured_street": owner.insured_street if owner else None,
            
            # Section 3.4 - Conducteur
            "driver_name": drivers[0].driver_name if drivers else None,
            "driver_birth_date": drivers[0].driver_birth_date.strftime("%Y-%m-%d") if drivers and drivers[0].driver_birth_date else None,
            "driver_licence_number": drivers[0].driver_licence_number if drivers else None,
            "driver_licence_category": drivers[0].driver_licence_category if drivers else None,
            "driver_licence_issued_at": drivers[0].driver_licence_issued_at.strftime("%Y-%m-%d") if drivers and drivers[0].driver_licence_issued_at else None,
            "driver_licence_issued_by": drivers[0].driver_licence_issued_by if drivers else None,
            
            # Section 3.5 - Véhicule Identification
            "licence_plate": vehicle.licence_plate if vehicle else None,
            "vehicle_chassis": vehicle.vehicle_chassis if vehicle else None,
            "vehicle_brand": vehicle.vehicle_brand if vehicle else None,
            "vehicle_model": vehicle.vehicle_model if vehicle else None,
            "vehicle_first_registration_date": vehicle.vehicle_first_registration_date.strftime("%Y-%m-%d") if vehicle and vehicle.vehicle_first_registration_date else None,
            
            # Section 3.6 - Classification
            "vehicle_category": vehicle.vehicle_category.value if vehicle and vehicle.vehicle_category else None,
            "vehicle_genre": vehicle.vehicle_genre.value if vehicle and vehicle.vehicle_genre else None,
            "vehicle_type": vehicle.vehicle_type.value if vehicle and vehicle.vehicle_type else None,
            "vehicle_usage": vehicle.vehicle_usage.value if vehicle and vehicle.vehicle_usage else None,
            "vehicle_energy": vehicle.vehicle_energy.value if vehicle and vehicle.vehicle_energy else None,
            "circulation_zone": vehicle.circulation_zone.value if vehicle and vehicle.circulation_zone else None,
            
            # Section 3.7 - Caractéristiques techniques
            "nb_of_seats": vehicle.nb_of_seats if vehicle else None,
            "fiscal_power": vehicle.fiscal_power if vehicle else None,
            "vehicle_displacement": vehicle.vehicle_displacement if vehicle else None,
            "vehicle_gross_weight": vehicle.vehicle_gross_weight if vehicle else None,
            "payload_capacity": vehicle.payload_capacity if vehicle else None,
            
            # Section 3.8 - Options
            "vehicle_has_trailer": vehicle.vehicle_has_trailer if vehicle else False,
            "trailer_flammable": vehicle.trailer_flammable if vehicle else False,
            "trailer_licence_plate": vehicle.trailer_licence_plate if vehicle else None,
            "vehicle_dual_control": vehicle.vehicle_dual_control if vehicle else False,
            "vehicle_engine_type": vehicle.vehicle_engine_type if vehicle else False,
            "civil_liability": vehicle.civil_liability if vehicle else False,
        }
        
        return data
    
    def send_contract_to_api(self, contract_id: int) -> Dict[str, Any]:
        """Envoie un contrat à l'API ASAC"""
        try:
            data = self.prepare_contract_data(contract_id)
            
            # Envoi à l'API
            response = requests.post(
                f"{self.base_url}/contracts",
                json=data,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Contrat {contract_id} envoyé avec succès")
                return response.json()
            else:
                logger.error(f"❌ Erreur API: {response.status_code} - {response.text}")
                return {"error": response.text, "status_code": response.status_code}
                
        except Exception as e:
            logger.error(f"❌ Erreur envoi contrat: {e}")
            raise
    
    def import_contract_from_api(self, police_number: str) -> Optional[Contrat]:
        """Importe un contrat depuis l'API ASAC"""
        try:
            response = requests.get(
                f"{self.base_url}/contracts/{police_number}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._create_contract_from_api_data(data)
            else:
                logger.error(f"❌ Erreur import: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur import contrat: {e}")
            raise
    
    def _create_contract_from_api_data(self, data: Dict[str, Any]) -> Contrat:
        """Crée un contrat à partir des données API"""
        # Créer ou récupérer le contact
        contact = self.controller.get_contact_by_code(data.get('insured_code'))
        if not contact:
            contact_data = {
                'customer_name': data.get('customer_name'),
                'customer_phone': data.get('customer_phone'),
                'customer_email': data.get('customer_email'),
                'customer_postal_code': data.get('customer_postal_code'),
                'customer_type': data.get('customer_type'),
                'insured_name': data.get('insured_name'),
                'insured_phone': data.get('insured_phone'),
                'insured_email': data.get('insured_email'),
                'insured_postal_code': data.get('insured_postal_code'),
                'insured_code': data.get('insured_code'),
                'insured_profession': data.get('insured_profession'),
                'insured_birthdate': datetime.strptime(data['insured_birthdate'], '%Y-%m-%d') if data.get('insured_birthdate') else None,
                'insured_city': data.get('insured_city'),
                'insured_street': data.get('insured_street')
            }
            contact = self.controller.create_contact(contact_data)
        
        # Créer ou récupérer le véhicule
        vehicle = self.controller.get_vehicle_by_plate(data.get('licence_plate'))
        if not vehicle:
            vehicle_data = {
                'licence_plate': data.get('licence_plate'),
                'vehicle_chassis': data.get('vehicle_chassis'),
                'vehicle_brand': data.get('vehicle_brand'),
                'vehicle_model': data.get('vehicle_model'),
                'vehicle_first_registration_date': datetime.strptime(data['vehicle_first_registration_date'], '%Y-%m-%d') if data.get('vehicle_first_registration_date') else None,
                'vehicle_category': data.get('vehicle_category'),
                'vehicle_genre': data.get('vehicle_genre'),
                'vehicle_type': data.get('vehicle_type'),
                'vehicle_usage': data.get('vehicle_usage'),
                'vehicle_energy': data.get('vehicle_energy'),
                'circulation_zone': data.get('circulation_zone'),
                'nb_of_seats': data.get('nb_of_seats', 5),
                'fiscal_power': data.get('fiscal_power', 5)
            }
            vehicle = self.controller.create_vehicle(vehicle_data)
        
        # Créer le contrat
        contract_data = {
            'numero_police': data.get('police_number'),
            'owner_id': contact.id,
            'vehicle_id': vehicle.id,
            'date_debut': datetime.strptime(data['starts_at'], '%Y-%m-%d') if data.get('starts_at') else None,
            'date_fin': datetime.strptime(data['ends_at'], '%Y-%m-%d') if data.get('ends_at') else None,
            'prime_pure': data.get('rc_prime', 0),
            'fleet_discount': data.get('fleet_discount', 0),
            'statut': ContractStatus.ACTIF
        }
        
        contract = self.controller.create_contract(contract_data)
        
        # Créer le conducteur
        if data.get('driver_name'):
            driver_data = {
                'driver_name': data.get('driver_name'),
                'driver_birth_date': datetime.strptime(data['driver_birth_date'], '%Y-%m-%d') if data.get('driver_birth_date') else None,
                'driver_licence_number': data.get('driver_licence_number'),
                'driver_licence_category': data.get('driver_licence_category'),
                'driver_licence_issued_at': datetime.strptime(data['driver_licence_issued_at'], '%Y-%m-%d') if data.get('driver_licence_issued_at') else None,
                'driver_licence_issued_by': data.get('driver_licence_issued_by'),
                'contract_id': contract.id
            }
            self.controller.create_driver(driver_data)
        
        return contract