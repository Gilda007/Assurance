

from typing import Optional, Dict, Any
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


class LometaDataProvider:
    """Fournisseur de données depuis LOMETA via le contrôleur principal"""
    
    def __init__(self, main_controller):
        """
        Initialise avec le contrôleur principal AutomobileMainController
        
        Args:
            main_controller: AutomobileMainController
        """
        self.main_controller = main_controller
        self.session = main_controller.session

    def build_production_from_vehicle(
        self, 
        vehicle_id: int,
        office_code: str = "AG-DLA-001",
        organization_code: str = "ACTIVA"
    ) -> Optional[Dict[str, Any]]:
        """
        Construit une demande de production à partir d'un véhicule LOMETA
        """
        try:
            # 1. Récupérer les données
            vehicle = self.main_controller.vehicles.get_vehicles_by_id(vehicle_id)
            if not vehicle:
                logger.error(f"Véhicule {vehicle_id} non trouvé")
                return None
            
            contract = self.main_controller.contracts.get_contract_by_vehicle(vehicle_id)
            if not contract:
                logger.warning(f"Aucun contrat pour le véhicule {vehicle_id}, utilisation valeurs par défaut")
                contract = self._get_default_contract(vehicle_id)
            
            owner_id = getattr(vehicle, 'owner_id', None)
            if not owner_id:
                logger.error(f"Pas d'owner_id pour le véhicule {vehicle_id}")
                return None
            
            contact = self.main_controller.contacts.get_contact_by_id(owner_id)
            if not contact:
                logger.error(f"Contact {owner_id} non trouvé")
                return None
            
            # 2. Construire la production au format exact ASAC
            production = self._build_production_item(vehicle, contract, contact, vehicle_id)
            
            return {
                "office_code": office_code,
                "organization_code": organization_code,
                "certificate_type": "cima",
                "channel": "api",
                "productions": [production]
            }
            
        except Exception as e:
            logger.error(f"Erreur build_production_from_vehicle: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _build_production_item(self, vehicle, contract, contact, vehicle_id: int) -> Dict[str, Any]:
        """Construit un élément de production au format exact ASAC"""
        
        # Déterminer le type de souscripteur
        customer_type = "TSPP"  # Personne physique
        if hasattr(contact, 'type_client') and contact.type_client == "Entreprise":
            customer_type = "TSPM"
        
        # Déterminer la profession
        profession = self._get_profession_code(contact)
        
        # Dates
        starts_at = date.today()
        ends_at = getattr(contract, 'date_fin', None) or (date.today() + timedelta(days=365))
        
        # Nom complet
        full_name = f"{contact.nom} {getattr(contact, 'prenom', '')}".strip()
        
        # Téléphone (s'assurer qu'il commence par +237)
        phone = getattr(contact, 'telephone', '') or "690000000"
        if not phone.startswith('+237'):
            phone = f"+237{phone}"
        
        # Date de naissance
        birthdate = getattr(contact, 'date_naissance', None) or date(1990, 1, 1)
        
        return {
            # Attestation
            "certificate_variant_code": "auto",
            "rc": int(getattr(vehicle, 'amt_rc', 0) or 0),
            "police_number": getattr(contract, 'numero_police', f"POL-{vehicle_id}"),
            "starts_at": starts_at.isoformat(),
            "ends_at": ends_at.isoformat(),
            
            # Souscripteur
            "customer_name": full_name,
            "customer_phone": phone,
            "customer_email": getattr(contact, 'email', '') or "",
            "customer_postal_code": getattr(contact, 'adresse', '') or "",
            "customer_type": customer_type,
            
            # Assuré
            "insured_name": full_name,
            "insured_phone": phone,
            "insured_email": getattr(contact, 'email', '') or "",
            "insured_postal_code": getattr(contact, 'adresse', '') or "",
            "insured_code": getattr(contact, 'code_client', '') or f"CLT{contact.id}",
            "insured_profession": profession,
            "insured_city": getattr(contact, 'ville', '') or "DOUALA",
            "insured_birthdate": birthdate.isoformat(),
            
            # Conducteur
            "driver_name": full_name,
            "driver_birthdate": birthdate.isoformat(),
            "driver_licence_number": getattr(contact, 'num_permis', '') or "P123456",
            "driver_licence_category": "B",
            "driver_licence_issued_at": (getattr(contact, 'date_naissance', None) or date(2010, 1, 1)).isoformat(),
            
            # Véhicule
            "licence_plate": getattr(vehicle, 'immatriculation', ''),
            "vehicle_chassis": getattr(vehicle, 'chassis', '') or f"CH-{getattr(vehicle, 'immatriculation', '')}",
            "vehicle_brand": getattr(vehicle, 'marque', ''),
            "vehicle_model": getattr(vehicle, 'modele', ''),
            "vehicle_category": self._get_category_code(getattr(vehicle, 'categorie', 'VP')),
            "vehicle_genre": self._get_genre_code(getattr(vehicle, 'categorie', 'VP')),
            "vehicle_type": self._get_type_code(getattr(vehicle, 'categorie', 'VP')),
            "vehicule_usage": self._get_usage_code(getattr(vehicle, 'usage', 'Particulier')),
            "vehicle_energy": self._get_energy_code(getattr(vehicle, 'energie', 'Essence')),
            "nb_of_seats": getattr(vehicle, 'places', 5),
            "fiscal_power": int(getattr(vehicle, 'usage', 5)) if str(getattr(vehicle, 'usage', '5')).isdigit() else 5,
            "circulation_zone": getattr(vehicle, 'zone', 'A'),
            
            # Options
            "vehicle_has_trailer": getattr(vehicle, 'has_remorque', False),
            
            # Fiscal
            "taxpayer_number": getattr(contact, 'num_contribuable', '') or "123456789",
            "dta": int(getattr(vehicle, 'amt_dta', 0) or 0)
        }

    def _get_default_contract(self, vehicle_id: int):
        """Crée un contrat par défaut (objet)"""
        import types
        contract = types.SimpleNamespace()
        contract.numero_police = f"POL-AUTO-{vehicle_id}"
        contract.date_debut = date.today()
        contract.date_fin = date.today() + timedelta(days=365)
        contract.prime_totale_ttc
        return contract

    def _get_profession_code(self, contact) -> str:
        """Retourne le code profession ASAC (ST01 à ST12)"""
        profession_map = {
            "Commerçant": "ST01",
            "Agent commercial": "ST01",
            "Agriculteur": "ST03",
            "Artisan": "ST04",
            "Employé": "ST09",
            "Fonctionnaire": "ST09",
            "Retraité": "ST08",
            "Sans emploi": "ST10",
            "VRP (Vendeur, Représentant, Placier)": "ST02",
            "Autre profession": "ST12"
        }
        cat = getattr(contact, 'cat_socio_prof', '')
        return profession_map.get(cat, "ST12")

    def _get_category_code(self, categorie: str) -> str:
        """Retourne le code catégorie ASAC (01 à 12)"""
        mapping = {"VP": "01", "VL": "01", "VU": "11", "PL": "03"}
        return mapping.get(categorie, "01")

    def _get_genre_code(self, categorie: str) -> str:
        """Retourne le code genre ASAC (GV01 à GV12)"""
        mapping = {"VP": "GV04", "VL": "GV04", "VU": "GV07", "PL": "GV01"}
        return mapping.get(categorie, "GV04")

    def _get_type_code(self, categorie: str) -> str:
        """Retourne le code type ASAC (TV01 à TV13)"""
        mapping = {"VP": "TV10", "VL": "TV10", "VU": "TV11", "PL": "TV11"}
        return mapping.get(categorie, "TV10")

    def _get_usage_code(self, usage: str) -> str:
        """Retourne le code usage ASAC (UV01 à UV10)"""
        mapping = {"Particulier": "UV01", "Professionnel": "UV02", "Mixte": "UV01"}
        return mapping.get(usage, "UV01")

    def _get_energy_code(self, energie: str) -> str:
        """Retourne le code énergie ASAC (SEES, SEDI, SEEL, SEHY)"""
        mapping = {"Essence": "SEES", "Diesel": "SEDI", "Electrique": "SEEL", "Hybride": "SEHY"}
        return mapping.get(energie, "SEES")