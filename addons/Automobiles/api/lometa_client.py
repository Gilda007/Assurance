# # addons/Automobiles/api/lometa_client.py
# """
# Client pour interagir avec la base de données LOMETA
# """

# from sqlalchemy.orm import Session
# from typing import Optional, Dict, Any, List
# from datetime import date, datetime
# import logging

# from addons.Automobiles.models import Vehicle, Contrat, Contact
# from addons.Paramètres.models.models import User

# logger = logging.getLogger(__name__)


# class LometaDataProvider:
#     """Fournisseur de données depuis LOMETA"""
    
#     def __init__(self, db_session: Session):
#         self.db = db_session
    
#     def get_vehicle_by_id(self, vehicle_id: int) -> Optional[Dict[str, Any]]:
#         """Récupère un véhicule LOMETA et le convertit au format ASAC"""
#         vehicle = self.db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
#         if not vehicle:
#             return None
        
#         return self._convert_vehicle_to_asac(vehicle)
    
#     def get_vehicle_by_plate(self, licence_plate: str) -> Optional[Dict[str, Any]]:
#         """Récupère un véhicule par son immatriculation"""
#         vehicle = self.db.query(Vehicle).filter(
#             Vehicle.immatriculation == licence_plate
#         ).first()
#         if not vehicle:
#             return None
        
#         return self._convert_vehicle_to_asac(vehicle)
    
#     def get_contract_by_vehicle(self, vehicle_id: int) -> Optional[Dict[str, Any]]:
#         """Récupère le contrat actif d'un véhicule"""
#         contract = self.db.query(Contrat).filter(
#             Contrat.vehicle_id == vehicle_id,
#             Contrat.date_fin >= date.today()
#         ).first()
        
#         if not contract:
#             return None
        
#         return self._convert_contract_to_asac(contract)
    
#     def get_contact_by_id(self, contact_id: int) -> Optional[Dict[str, Any]]:
#         """Récupère un contact LOMETA"""
#         contact = self.db.query(Contact).filter(Contact.id == contact_id).first()
#         if not contact:
#             return None
        
#         return self._convert_contact_to_asac(contact)
    
#     def build_production_from_vehicle(
#         self, 
#         vehicle_id: int,
#         office_code: str = "AG-DLA-001",
#         organization_code: str = "ACTIVA"
#     ) -> Optional[Dict[str, Any]]:
#         """
#         Construit une demande de production à partir d'un véhicule LOMETA
#         """
#         # Récupérer les données
#         vehicle_data = self.get_vehicle_by_id(vehicle_id)
#         if not vehicle_data:
#             logger.error(f"Véhicule {vehicle_id} non trouvé")
#             return None
        
#         contract_data = self.get_contract_by_vehicle(vehicle_id)
#         if not contract_data:
#             logger.error(f"Aucun contrat actif pour le véhicule {vehicle_id}")
#             return None
        
#         contact_data = self.get_contact_by_id(vehicle_data.get("owner_id"))
#         if not contact_data:
#             logger.error(f"Contact {vehicle_data.get('owner_id')} non trouvé")
#             return None
        
#         # Construire la production
#         return {
#             "office_code": office_code,
#             "organization_code": organization_code,
#             "certificate_type": "cima",
#             "productions": [self._build_production_item(
#                 vehicle_data, contract_data, contact_data
#             )]
#         }
    
#     def _convert_vehicle_to_asac(self, vehicle: Vehicle) -> Dict[str, Any]:
#         """Convertit un véhicule LOMETA au format ASAC"""
        
#         # Mapper la catégorie
#         category_map = {
#             "VP": "01",  # Tourisme personne physique
#             "VL": "01",  # Tourisme
#             "VU": "11",  # Utilitaire
#             "PL": "03",  # Transport marchandises
#         }
        
#         # Mapper le genre
#         genre_map = {
#             "VP": "GV04",  # Voiture
#             "VL": "GV04",
#             "VU": "GV07",  # Fourgonnette
#             "PL": "GV01",  # Camion
#         }
        
#         # Mapper le type
#         type_map = {
#             "VP": "TV10",  # Particulier
#             "VL": "TV10",
#             "VU": "TV11",  # Utilitaire
#             "PL": "TV11",
#         }
        
#         # Mapper l'usage
#         usage_map = {
#             "Particulier": "UV01",
#             "Professionnel": "UV02",
#             "Mixte": "UV01",
#         }
        
#         # Mapper l'énergie
#         energy_map = {
#             "Essence": "SEES",
#             "Diesel": "SEDI",
#             "Electrique": "SEEL",
#             "Hybride": "SEHY",
#         }
        
#         # Mapper la zone
#         zone_map = {
#             "A": "A",
#             "B": "B", 
#             "C": "C",
#         }
        
#         return {
#             "licence_plate": vehicle.immatriculation,
#             "vehicle_chassis": vehicle.chassis or f"CH-{vehicle.immatriculation}",
#             "vehicle_brand": vehicle.marque,
#             "vehicle_model": vehicle.modele,
#             "vehicle_category": category_map.get(vehicle.categorie, "01"),
#             "vehicle_genre": genre_map.get(vehicle.categorie, "GV04"),
#             "vehicle_type": type_map.get(vehicle.categorie, "TV10"),
#             "vehicle_usage": usage_map.get(vehicle.usage, "UV01"),
#             "vehicle_energy": energy_map.get(vehicle.energie, "SEES"),
#             "circulation_zone": zone_map.get(vehicle.zone, "A"),
#             "nb_of_seats": vehicle.places or 5,
#             "fiscal_power": int(vehicle.usage) if vehicle.usage and vehicle.usage.isdigit() else 5,
#             "vehicle_has_trailer": vehicle.has_remorque or False,
#             "vehicle_first_registration_date": vehicle.annee,
#             "owner_id": vehicle.owner_id
#         }
    
#     def _convert_contract_to_asac(self, contract: Contrat) -> Dict[str, Any]:
#         """Convertit un contrat LOMETA au format ASAC"""
#         return {
#             "police_number": contract.numero_police,
#             "starts_at": contract.date_debut.isoformat(),
#             "ends_at": contract.date_fin.isoformat(),
#             "rc": int(contract.prime_totale_ttc or 0),
#             "dta": 0
#         }
    
#     def _convert_contact_to_asac(self, contact: Contact) -> Dict[str, Any]:
#         """Convertit un contact LOMETA au format ASAC"""
        
#         # Type de souscripteur
#         customer_type = "TSPP"  # Personne physique par défaut
#         if contact.type_client == "Entreprise" or contact.nature == "Moral":
#             customer_type = "TSPM"
        
#         # Profession
#         profession_map = {
#             "Commerçant": "ST01",
#             "Agent commercial": "ST01",
#             "Agriculteur": "ST03",
#             "Artisan": "ST04",
#             "Employé": "ST09",
#             "Fonctionnaire": "ST09",
#             "Retraité": "ST08",
#             "Sans emploi": "ST10",
#         }
#         profession = profession_map.get(contact.cat_socio_prof, "ST12")
        
#         return {
#             "customer_name": f"{contact.nom} {contact.prenom or ''}".strip(),
#             "customer_phone": contact.telephone or "",
#             "customer_type": customer_type,
#             "customer_email": contact.email,
#             "insured_name": f"{contact.nom} {contact.prenom or ''}".strip(),
#             "insured_phone": contact.telephone or "",
#             "insured_email": contact.email or "",
#             "insured_postal_code": contact.adresse or "",
#             "insured_code": contact.code_client or "",
#             "insured_profession": profession,
#             "insured_city": contact.ville or "DOUALA",
#             "insured_birthdate": contact.date_naissance.isoformat() if contact.date_naissance else None,
#             "driver_name": f"{contact.nom} {contact.prenom or ''}".strip(),
#             "driver_birthdate": (contact.date_naissance or date(1990, 1, 1)).isoformat(),
#             "driver_licence_number": contact.num_permis or "",
#             "driver_licence_category": "B",
#             "driver_licence_issued_at": (contact.date_naissance or date(2010, 1, 1)).isoformat(),
#             "taxpayer_number": contact.num_contribuable or ""
#         }
    
#     def _build_production_item(self, vehicle_data, contract_data, contact_data) -> Dict[str, Any]:
#         """Construit un élément de production complet"""
#         return {
#             **vehicle_data,
#             **contract_data,
#             **contact_data,
#             "certificate_variant_code": "JAUNE"
#         }


# addons/Automobiles/api/lometa_client.py
"""
Client pour interagir avec les données LOMETA via le contrôleur
"""

from typing import Optional, Dict, Any, List
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


class LometaDataProvider:
    """Fournisseur de données depuis LOMETA via le contrôleur"""
    
    def __init__(self, controller):
        """
        Initialise avec le contrôleur automobile
        
        Args:
            controller: AutomobileMainController ou VehicleController
        """
        self.controller = controller
        self.vehicles = controller.vehicles if hasattr(controller, 'vehicles') else controller
    
    def get_vehicle_by_id(self, vehicle_id: int) -> Optional[Dict[str, Any]]:
        """Récupère un véhicule LOMETA et le convertit au format ASAC"""
        try:
            vehicle = self.vehicles.get_vehicles_by_id(vehicle_id)
            if not vehicle:
                logger.error(f"Véhicule {vehicle_id} non trouvé")
                return None
            
            logger.info(f"✅ Véhicule trouvé: {vehicle.immatriculation}")
            return self._convert_vehicle_to_asac(vehicle)
            
        except Exception as e:
            logger.error(f"Erreur get_vehicle_by_id: {e}")
            return None
    
    def get_vehicle_by_plate(self, licence_plate: str) -> Optional[Dict[str, Any]]:
        """Récupère un véhicule par son immatriculation"""
        try:
            # Chercher le véhicule par immatriculation
            from addons.Automobiles.models import Vehicle
            vehicle = self.vehicles.session.query(Vehicle).filter(
                Vehicle.immatriculation == licence_plate
            ).first()
            
            if not vehicle:
                logger.error(f"Véhicule {licence_plate} non trouvé")
                return None
            
            return self._convert_vehicle_to_asac(vehicle)
            
        except Exception as e:
            logger.error(f"Erreur get_vehicle_by_plate: {e}")
            return None
    
    def get_contract_by_vehicle(self, vehicle_id: int) -> Optional[Dict[str, Any]]:
        """Récupère le contrat actif d'un véhicule via le contrôleur"""
        try:
            # Utiliser le contract_ctrl du contrôleur
            if hasattr(self.vehicles, 'contract_ctrl'):
                contract = self.vehicles.contract_ctrl.get_contract_by_vehicle(vehicle_id)
            else:
                # Fallback: chercher directement
                from addons.Automobiles.models import Contrat
                contract = self.vehicles.session.query(Contrat).filter(
                    Contrat.vehicle_id == vehicle_id
                ).first()
            
            if not contract:
                logger.warning(f"Aucun contrat pour le véhicule {vehicle_id}")
                return None
            
            logger.info(f"✅ Contrat trouvé: {contract.numero_police}")
            
            return {
                "police_number": contract.numero_police,
                "starts_at": contract.date_debut.isoformat() if contract.date_debut else None,
                "ends_at": contract.date_fin.isoformat() if contract.date_fin else None,
                "rc": int(contract.prime_totale_ttc or 0),
                "dta": 0
            }
            
        except Exception as e:
            logger.error(f"Erreur get_contract_by_vehicle: {e}")
            return None
    
    def get_contact_by_id(self, contact_id: int) -> Optional[Dict[str, Any]]:
        """Récupère un contact LOMETA"""
        try:
            # Utiliser la méthode du contrôleur
            contact = self.vehicles.get_client_by_id(contact_id)
            
            if not contact:
                logger.error(f"Contact {contact_id} non trouvé")
                return None
            
            logger.info(f"✅ Contact trouvé: {contact.nom} {contact.prenom or ''}")
            return self._convert_contact_to_asac(contact)
            
        except Exception as e:
            logger.error(f"Erreur get_contact_by_id: {e}")
            return None
    
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
            # 1. Récupérer les données du véhicule
            vehicle_data = self.get_vehicle_by_id(vehicle_id)
            if not vehicle_data:
                logger.error(f"Véhicule {vehicle_id} non trouvé")
                return None
            
            # 2. Récupérer le contrat
            contract_data = self.get_contract_by_vehicle(vehicle_id)
            if not contract_data:
                logger.warning(f"Aucun contrat pour le véhicule {vehicle_id}")
                # Créer un contrat par défaut
                contract_data = {
                    "police_number": f"POL-AUTO-{vehicle_id}",
                    "starts_at": date.today().isoformat(),
                    "ends_at": (date.today() + timedelta(days=365)).isoformat(),
                    "rc": int(vehicle_data.get('prime_nette', 50000)),
                    "dta": 0
                }
            
            # 3. Récupérer le contact propriétaire
            owner_id = vehicle_data.get("owner_id")
            if not owner_id:
                logger.error(f"Pas d'owner_id pour le véhicule {vehicle_id}")
                return None
            
            contact_data = self.get_contact_by_id(owner_id)
            if not contact_data:
                logger.error(f"Contact {owner_id} non trouvé")
                return None
            
            # 4. Construire la production
            return {
                "office_code": office_code,
                "organization_code": organization_code,
                "certificate_type": "cima",
                "productions": [self._build_production_item(
                    vehicle_data, contract_data, contact_data
                )]
            }
            
        except Exception as e:
            logger.error(f"Erreur build_production_from_vehicle: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _convert_vehicle_to_asac(self, vehicle) -> Dict[str, Any]:
        """Convertit un véhicule LOMETA au format ASAC"""
        
        # Gérer la date de première mise en circulation
        first_reg_date = None
        if vehicle.annee:
            # Convertir l'année (ex: 2007) en date complète
            try:
                # Si c'est un nombre (année)
                if isinstance(vehicle.annee, int):
                    first_reg_date = date(vehicle.annee, 1, 1)
                # Si c'est une string
                elif isinstance(vehicle.annee, str) and vehicle.annee.isdigit():
                    first_reg_date = date(int(vehicle.annee), 1, 1)
                # Si c'est déjà une date
                elif isinstance(vehicle.annee, date):
                    first_reg_date = vehicle.annee
            except:
                first_reg_date = date(2000, 1, 1)
        
        # Mapper les catégories
        category_map = {
            "VP": "01",
            "VL": "01",
            "VU": "11",
            "PL": "03",
        }
        
        genre_map = {
            "VP": "GV04",
            "VL": "GV04",
            "VU": "GV07",
            "PL": "GV01",
        }
        
        type_map = {
            "VP": "TV10",
            "VL": "TV10",
            "VU": "TV11",
            "PL": "TV11",
        }
        
        usage_map = {
            "Particulier": "UV01",
            "Professionnel": "UV02",
            "Mixte": "UV01",
        }
        
        energy_map = {
            "Essence": "SEES",
            "Diesel": "SEDI",
            "Electrique": "SEEL",
            "Hybride": "SEHY",
        }
        
        zone_map = {
            "A": "A",
            "B": "B", 
            "C": "C",
        }
        
        return {
            "licence_plate": vehicle.immatriculation,
            "vehicle_chassis": vehicle.chassis or f"CH-{vehicle.immatriculation}",
            "vehicle_brand": vehicle.marque,
            "vehicle_model": vehicle.modele,
            "vehicle_category": category_map.get(vehicle.categorie, "01"),
            "vehicle_genre": genre_map.get(vehicle.categorie, "GV04"),
            "vehicle_type": type_map.get(vehicle.categorie, "TV10"),
            "vehicle_usage": usage_map.get(vehicle.usage, "UV01"),
            "vehicle_energy": energy_map.get(vehicle.energie, "SEES"),
            "circulation_zone": zone_map.get(vehicle.zone, "A"),
            "nb_of_seats": vehicle.places or 5,
            "fiscal_power": int(vehicle.usage) if vehicle.usage and str(vehicle.usage).isdigit() else 7,
            "vehicle_has_trailer": vehicle.has_remorque or False,
            "vehicle_first_registration_date": first_reg_date.isoformat() if first_reg_date else None,
            "prime_nette": float(vehicle.prime_nette or 0),
            "owner_id": vehicle.owner_id,
            "dta": int(vehicle.amt_dta or 0)
        }
    
    def _convert_contract_to_asac(self, contract) -> Dict[str, Any]:
        """Convertit un contrat LOMETA au format ASAC avec valeurs par défaut"""
        
        # Valeurs par défaut si les dates sont nulles
        starts_at = contract.date_debut if contract.date_debut else date.today()
        ends_at = contract.date_fin if contract.date_fin else (date.today() + timedelta(days=365))
        print(ends_at, starts_at)
        
        return {
            "police_number": contract.numero_police,
            "starts_at": starts_at.isoformat(),  # Maintenant non-null
            "ends_at": ends_at.isoformat(),      # Maintenant non-null
            "rc": int(contract.prime_totale_ttc or 0),
            "dta": 0
        }
    
    def _convert_contact_to_asac(self, contact) -> Dict[str, Any]:
        """Convertit un contact LOMETA au format ASAC"""
        
        # Type de souscripteur
        customer_type = "TSPP"  # Personne physique par défaut
        if contact.type_client == "Entreprise" or contact.nature == "Moral":
            customer_type = "TSPM"
        
        # Profession
        profession_map = {
            "Commerçant": "ST01",
            "Agent commercial": "ST01",
            "Agriculteur": "ST03",
            "Artisan": "ST04",
            "Employé": "ST09",
            "Fonctionnaire": "ST09",
            "Retraité": "ST08",
            "Sans emploi": "ST10",
        }
        profession = profession_map.get(contact.cat_socio_prof, "ST12")
        
        return {
            "customer_name": f"{contact.nom} {contact.prenom or ''}".strip(),
            "customer_phone": contact.telephone or "",
            "customer_type": customer_type,
            "customer_email": contact.email,
            "insured_name": f"{contact.nom} {contact.prenom or ''}".strip(),
            "insured_phone": contact.telephone or "",
            "insured_email": contact.email or "",
            "insured_postal_code": contact.adresse or "",
            "insured_code": contact.code_client or "",
            "insured_profession": profession,
            "insured_city": contact.ville or "DOUALA",
            "insured_birthdate": contact.date_naissance.isoformat() if contact.date_naissance else None,
            "driver_name": f"{contact.nom} {contact.prenom or ''}".strip(),
            "driver_birthdate": (contact.date_naissance or date(1990, 1, 1)).isoformat(),
            "driver_licence_number": contact.num_permis or "",
            "driver_licence_category": "B",
            "driver_licence_issued_at": (contact.date_naissance or date(2010, 1, 1)).isoformat(),
            "taxpayer_number": contact.num_contribuable or ""
        }
    
    def _build_production_item(self, vehicle_data, contract_data, contact_data) -> Dict[str, Any]:
        """Construit un élément de production complet"""
        return {
            **vehicle_data,
            **contract_data,
            **contact_data,
            "certificate_variant_code": "JAUNE"
        }