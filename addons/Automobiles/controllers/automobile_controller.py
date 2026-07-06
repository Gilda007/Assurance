from typing import Dict, Optional, Tuple, Any
import json
import socket

from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func
from addons.Automobiles.models.contact_models import Contact
from addons.Automobiles.models.compagnies_models import Compagnie
from addons.Automobiles.models.automobile_models import Vehicle, AuditVehicleLog
from addons.Automobiles.controllers.contract_controller import ContractController
from core.workers.query_cache import query_cache
from datetime import date, datetime
import requests

from addons.Automobiles.models.contract_models import Contrat
from core import logger
from core.database import timeout, TimeoutError
from functools import wraps
import time


# Ajoutez ce décorateur après les imports
def with_db_timeout(seconds=30):
    """Décorateur pour ajouter un timeout aux méthodes DB"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                with timeout(seconds):
                    return func(self, *args, **kwargs)
            except TimeoutError as e:
                logger.error(f"Timeout dans {func.__name__}: {e}")
                return None if kwargs.get('default_on_timeout', True) else []
            except Exception as e:
                logger.error(f"Erreur dans {func.__name__}: {e}")
                raise
        return wrapper
    return decorator

class VehicleController:
    def __init__(self, session: Session):
        self.session = session
        self.contract_ctrl = ContractController(self.session)
        self._vehicle_cache = {} 
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()  # Correction: session au lieu de db
    
    def get_vehicle_with_relations_cached(self, vehicle_id: int, force_refresh: bool = False) -> Optional[Vehicle]:
        """
        Récupère un véhicule avec relations, avec cache mémoire.
        """
        cache_key = f"vehicle_relations_{vehicle_id}"
        
        if not force_refresh and cache_key in self._vehicle_cache:
            logger.info(f"📦 Cache hit: {cache_key}")
            return self._vehicle_cache[cache_key]
        
        vehicle = self.get_vehicle_with_relations(vehicle_id)
        if vehicle:
            self._vehicle_cache[cache_key] = vehicle
        
        return vehicle
    
    def invalidate_vehicle_cache(self, vehicle_id: int = None):
        """Invalide le cache pour un véhicule spécifique ou tout le cache."""
        if vehicle_id:
            cache_key = f"vehicle_relations_{vehicle_id}"
            if cache_key in self._vehicle_cache:
                del self._vehicle_cache[cache_key]
                logger.info(f"🗑️ Cache invalidé: {cache_key}")
        else:
            self._vehicle_cache.clear()
            logger.info("🗑️ Cache véhicules vidé")

    @with_db_timeout(seconds=30)
    def get_all_vehicles(self, force_refresh: bool = False, timeout_seconds: int = 30):
        """
        Récupère tous les véhicules avec cache mémoire et timeout
        """
        cache_key = "automobiles:vehicles:list"
        
        # 1. Essayer le cache
        if not force_refresh:
            cached = self._get_cached(cache_key)
            if cached is not None:
                logger.info(f"📦 Cache hit: {len(cached)} véhicules")
                return cached
        
        # 2. Charger depuis la base avec timeout
        logger.info(f"💾 Cache miss: Chargement depuis la base")
        
        try:
            with timeout(timeout_seconds):
                vehicles = self.session.query(Vehicle).options(
                    selectinload(Vehicle.contract),
                    joinedload(Vehicle.owner),
                    joinedload(Vehicle.compagny),
                    selectinload(Vehicle.fleet)
                ).filter(Vehicle.is_active == True).all()
                
                # 3. Sauvegarder en cache
                self._set_cache(cache_key, vehicles)
                
                logger.info(f"✅ {len(vehicles)} véhicules chargés")
                return vehicles
                
        except TimeoutError as e:
            logger.error(f"Timeout lors du chargement des véhicules: {e}")
            return []
        except Exception as e:
            logger.error(f"Erreur chargement véhicules: {e}")
            return []


    def get_vehicles_by_id(self, vehicle_id, load_relations: bool = False):
        """
        Récupère un véhicule par son ID.
        
        Args:
            vehicle_id: ID du véhicule
            load_relations: Si True, charge toutes les relations (driver, classification, garanties, etc.)
        
        Returns:
            Vehicle: Objet véhicule avec ou sans relations
        """
        try:
            from sqlalchemy.orm import selectinload, joinedload
            
            vehicle = self.session.query(Vehicle).options(
                selectinload(Vehicle.driver),
                selectinload(Vehicle.classification),
                selectinload(Vehicle.guarantees),
                selectinload(Vehicle.guarantee_reductions),
                selectinload(Vehicle.guarantee_rates),
                selectinload(Vehicle.guarantee_options),
                selectinload(Vehicle.fleet_guarantees),
                joinedload(Vehicle.owner),
                joinedload(Vehicle.compagny),
                selectinload(Vehicle.fleet),
                selectinload(Vehicle.contract)
            ).filter(Vehicle.id == vehicle_id).first()
            
            # ✅ Détacher l'objet de la session pour qu'il puisse être utilisé librement
            if vehicle:
                self.session.expunge(vehicle)
            
            return vehicle
            
        except Exception as e:
            logger.error(f"Erreur get_vehicle_with_relations: {e}")
            import traceback
            traceback.print_exc()
            return None

    # def get_vehicles_by_owner_id(self, owner_id: int, force_refresh: bool = False):
    #     """Récupère les véhicules d'un propriétaire (avec cache)"""
        
    #     def load_vehicles():
    #         return self.session.query(Vehicle).options(
    #             selectinload(Vehicle.contract),
    #             joinedload(Vehicle.owner)
    #         ).filter(
    #             Vehicle.owner_id == owner_id,
    #             Vehicle.is_active == True
    #         ).all()
        
    #     if force_refresh:
    #         query_cache.invalidate(f"owner_{owner_id}")
    #         return load_vehicles()
        
    #     return query_cache.get_or_compute(
    #         f"vehicles_by_owner_{owner_id}",
    #         compute_func=load_vehicles,
    #         ttl=300
    #     )

    # def get_dashboard_stats(self, fleet_id=None):
    #     """Calcule les KPI pour les widgets du haut de l'interface."""
    #     query = self.session.query(Vehicle)
    #     if fleet_id:
    #         query = query.filter(Vehicle.fleet_id == fleet_id)

    #     total = query.count()
    #     actifs = query.filter(Vehicle.statut == "ACTIF").count()
    #     expires = query.filter(Vehicle.statut == "EXPIRE").count()
    #     prime_totale = self.session.query(func.sum(Vehicle.prime_emise)).scalar() or 0

    #     return {
    #         "total": total,
    #         "actifs": actifs,
    #         "expires": expires,
    #         "prime_totale": f"{prime_totale:,.0f} FCFA"
    #     }

    @with_db_timeout(30)
    def get_vehicles_by_owner_id(self, owner_id: int, force_refresh: bool = False):
        """Récupère les véhicules d'un propriétaire (avec cache)"""
        
        def load_vehicles():
            return self.session.query(Vehicle).options(
                selectinload(Vehicle.contract),
                joinedload(Vehicle.owner)
            ).filter(
                Vehicle.owner_id == owner_id,
                Vehicle.is_active == True
            ).all()
        
        if force_refresh:
            query_cache.invalidate(f"owner_{owner_id}")
            return load_vehicles()
        
        return query_cache.get_or_compute(
            f"vehicles_by_owner_{owner_id}",
            compute_func=load_vehicles,
            ttl=300
        )

    @with_db_timeout(45)
    def get_dashboard_stats(self, fleet_id=None):
        """Calcule les KPI pour les widgets du haut de l'interface."""
        query = self.session.query(Vehicle)
        if fleet_id:
            query = query.filter(Vehicle.fleet_id == fleet_id)

        total = query.count()
        actifs = query.filter(Vehicle.statut == "ACTIF").count()
        expires = query.filter(Vehicle.statut == "EXPIRE").count()
        prime_totale = self.session.query(func.sum(Vehicle.prime_emise)).scalar() or 0

        return {
            "total": total,
            "actifs": actifs,
            "expires": expires,
            "prime_totale": f"{prime_totale:,.0f} FCFA"
        }

    def bulk_update_status(self, vehicle_ids, new_status):
        """Mise à jour groupée (ex: passer plusieurs véhicules en 'Expiré')."""
        try:
            self.session.query(Vehicle).filter(Vehicle.id.in_(vehicle_ids)).update(
                {"statut": new_status}, synchronize_session=False
            )
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            return False, str(e)
        
    def get_compgnies_for_combo(self, text):
        """Récupère les clients/entreprises depuis la table CONTACT."""

        return self.session.query(Compagnie).filter(
            (Compagnie.nom.ilike(f"%{text}%")) | 
            (Compagnie.telephone.ilike(f"%{text}%"))
        ).all()

    # Dans la classe VehicleController
    def get_all_contacts(self):
        """Récupère tous les contacts (Clients/Propriétaires) depuis la base de données"""
        try:
            # On utilise la session pour récupérer les données réelles
            return self.session.query(Contact).all()
        except Exception as e:
            print(f"Erreur lors de la récupération des contacts: {e}")
            return []

    def get_contact_by_id(self, compagnie_id):
        """Récupère un contact par son ID (utile pour pré-remplir un formulaire)."""
        try:
            return self.session.get(Compagnie, compagnie_id)
        except Exception as e:
            print(f"Erreur lors de la récupération du contact {compagnie_id}: {e}")
            return None

    def get_client_by_id(self, contact_id: int):
        """Récupère un contact (personne physique/morale) par son ID"""
        try:
            # Utiliser le modèle Contact, pas Compagnie
            from addons.Automobiles.models.contact_models import Contact
            return self.session.query(Contact).filter(Contact.id == contact_id).first()
        except Exception as e:
            print(f"Erreur lors de la récupération du contact {contact_id}: {e}")
            return None

    @with_db_timeout(seconds=30)
    def get_vehicles_by_fleet(self, fleet_id: int, timeout_seconds: int = 30):
        """Récupère tous les véhicules d'une flotte avec timeout"""
        try:
            with timeout(timeout_seconds):
                vehicles = self.session.query(Vehicle).options(
                    joinedload(Vehicle.fleet),
                    joinedload(Vehicle.owner),
                    selectinload(Vehicle.contract)
                ).filter(
                    Vehicle.fleet_id == fleet_id,
                    Vehicle.is_active == True
                ).all()
                return vehicles
        except TimeoutError as e:
            logger.error(f"Timeout lors du chargement des véhicules fleet {fleet_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Erreur récupération véhicules par flotte: {e}")
            return []

    def get_report_data(self):
        """Méthode requise par ContactListView pour les statistiques et le PDF"""
        contacts = self.get_all_contacts()
        # On prépare des stats basiques pour le PieChart du Dashboard
        stats = {
            'total': len(contacts),
            'Physique': len([c for c in contacts if c.type_contact == 'Physique']),
            'Morale': len([c for c in contacts if c.type_contact == 'Morale'])
        }
        return contacts, stats
    

    def create_vehicle(self, data: Dict, user_id: int, local_ip=None, public_ip=None, max_retries: int = 3) -> Tuple[bool, str, int]:
        """
        Crée un véhicule ET son contrat proformat associé avec la nouvelle structure de BD.
        
        Returns:
            Tuple (succès, message, id_vehicule)
        """
        for attempt in range(max_retries):
            try:
                # 1. Vérification préalable des données critiques
                owner_id = data.get('owner_id')
                if not owner_id:
                    print("❌ owner_id manquant dans les données")
                    print(f"Clés disponibles: {list(data.keys())}")
                    return False, "Le propriétaire du véhicule est requis (owner_id manquant)", None
                
                company_id = data.get('company_id', data.get('compagny_id'))
                if not company_id:
                    return False, "La compagnie d'assurance est requise", None

                # 2. Gestion des infos réseau si manquantes
                if local_ip is None or public_ip is None:
                    local_ip, public_ip = self.get_network_info()

                # 3. Préparation du log d'audit
                audit_data = data.copy()
                audit_data['ip_info'] = {'local': local_ip, 'public': public_ip}

                # 4. Nettoyage de 'data' pour SQLAlchemy (champs du modèle Vehicle)
                vehicle_columns = Vehicle.__table__.columns.keys()
                vehicle_data = {k: v for k, v in data.items() if k in vehicle_columns}
                vehicle_data['owner_id'] = owner_id
                print(f"✅ owner_id = {owner_id} ajouté aux données du véhicule")

                # 5. Création du véhicule principal
                new_vehicle = Vehicle(**vehicle_data)
                
                if hasattr(new_vehicle, 'created_by'):
                    new_vehicle.created_by = user_id
                if hasattr(new_vehicle, 'created_ip'):
                    new_vehicle.created_ip = public_ip

                self.session.add(new_vehicle)
                self.session.flush()
                print(f"✓ Véhicule créé avec ID: {new_vehicle.id}")

                # ============================================================
                # 6. CRÉATION DE LA CLASSIFICATION ASAC
                # ============================================================
                classification_data = {
                    'categorie_id': data.get('categorie'),
                    'genre_id': data.get('genre'),
                    'type_id': data.get('type_vehicule'),
                    'usage_id': data.get('usage'),
                    'energie_id': data.get('energie'),
                    'zone_id': data.get('zone'),
                }
                
                if any(classification_data.values()):
                    from addons.Automobiles.models.automobile_models import VehicleClassification
                    classification = VehicleClassification(
                        vehicle_id=new_vehicle.id,
                        **classification_data
                    )
                    self.session.add(classification)
                    print(f"✓ Classification ASAC créée: {classification_data}")

                # ============================================================
                # 7. CRÉATION DES GARANTIES
                # ============================================================
                from addons.Automobiles.models.automobile_models import (
                    VehicleGuarantee,
                    VehicleGuaranteeReduction,
                    VehicleGuaranteeRate,
                    VehicleGuaranteeOption,
                    VehicleFleetGuarantee
                )

                # 7.1 Garanties brutes
                guarantee_data = {
                    'rc': float(data.get('amt_rc', data.get('amt_rc_brut', 0))),
                    'dr': float(data.get('amt_dr', data.get('amt_dr_brut', 0))),
                    'vol': float(data.get('amt_vol', data.get('amt_vol_brut', 0))),
                    'vb': float(data.get('amt_vb', data.get('amt_vb_brut', 0))),
                    'ipt': float(data.get('amt_in', data.get('amt_in_brut', 0))),
                    'bris': float(data.get('amt_bris', data.get('amt_bris_brut', 0))),
                    'ar': float(data.get('amt_ar', data.get('amt_ar_brut', 0))),
                    'dta': float(data.get('amt_dta', data.get('amt_dta_brut', 0))),
                    'in_garantie': float(data.get('amt_ipt', data.get('amt_ipt_brut', 0))),
                }
                
                guarantees = VehicleGuarantee(vehicle_id=new_vehicle.id, **guarantee_data)
                self.session.add(guarantees)
                print(f"✓ Garanties brutes créées")

                # 7.2 Garanties avec réduction
                reduction_data = {
                    'rc': float(data.get('amt_val_red_rc', 0)),
                    'dr': float(data.get('amt_val_red_dr', 0)),
                    'vol': float(data.get('amt_val_red_vol', 0)),
                    'vb': float(data.get('amt_val_red_vb', 0)),
                    'ipt': float(data.get('amt_val_red_in', 0)),
                    'bris': float(data.get('amt_val_red_bris', 0)),
                    'ar': float(data.get('amt_val_red_ar', 0)),
                    'dta': float(data.get('amt_val_red_dta', 0)),
                    'in_garantie': float(data.get('amt_val_red_ipt', 0)),
                }
                
                reductions = VehicleGuaranteeReduction(vehicle_id=new_vehicle.id, **reduction_data)
                self.session.add(reductions)
                print(f"✓ Garanties avec réduction créées")

                # 7.3 Taux des garanties
                rate_data = {
                    'rc': float(data.get('red_rc', 0)),
                    'dr': float(data.get('red_dr', 0)),
                    'vol': float(data.get('red_vol', 0)),
                    'vb': float(data.get('red_vb', 0)),
                    'ipt': float(data.get('red_in', 0)),
                    'bris': float(data.get('red_bris', 0)),
                    'ar': float(data.get('red_ar', 0)),
                    'dta': float(data.get('red_dta', 0)),
                    'in_garantie': float(data.get('red_ipt', 0)),
                }
                
                rates = VehicleGuaranteeRate(vehicle_id=new_vehicle.id, **rate_data)
                self.session.add(rates)
                print(f"✓ Taux des garanties créés")

                # 7.4 Options des garanties
                option_data = {
                    'rc': bool(data.get('check_rc', False)),
                    'dr': bool(data.get('check_dr', False)),
                    'vol': bool(data.get('check_vol', False)),
                    'vb': bool(data.get('check_vb', False)),
                    'ipt': bool(data.get('check_in', False)),
                    'bris': bool(data.get('check_bris', False)),
                    'ar': bool(data.get('check_ar', False)),
                    'dta': bool(data.get('check_dta', False)),
                    'in_garantie': bool(data.get('check_ipt', False)),
                }
                
                options = VehicleGuaranteeOption(vehicle_id=new_vehicle.id, **option_data)
                self.session.add(options)
                print(f"✓ Options des garanties créées")

                # 7.5 Garanties flotte
                fleet_guarantee_data = {
                    'rc': float(data.get('amt_fleet_rc_val', 0)),
                    'dr': float(data.get('amt_fleet_dr_val', 0)),
                    'vol': float(data.get('amt_fleet_vol_val', 0)),
                    'vb': float(data.get('amt_fleet_vb_val', 0)),
                    'ipt': float(data.get('amt_fleet_in_val', 0)),
                    'bris': float(data.get('amt_fleet_bris_val', 0)),
                    'ar': float(data.get('amt_fleet_ar_val', 0)),
                    'dta': float(data.get('amt_fleet_dta_val', 0)),
                    'in_garantie': float(data.get('amt_fleet_ipt_val', 0)),
                }
                
                if not any(fleet_guarantee_data.values()):
                    fleet_guarantee_data = {
                        'rc': float(data.get('amt_val_red_rc', 0)),
                        'dr': float(data.get('amt_val_red_dr', 0)),
                        'vol': float(data.get('amt_val_red_vol', 0)),
                        'vb': float(data.get('amt_val_red_vb', 0)),
                        'ipt': float(data.get('amt_val_red_in', 0)),
                        'bris': float(data.get('amt_val_red_bris', 0)),
                        'ar': float(data.get('amt_val_red_ar', 0)),
                        'dta': float(data.get('amt_val_red_dta', 0)),
                        'in_garantie': float(data.get('amt_val_red_ipt', 0)),
                    }
                    print("ℹ️ Valeurs flotte copiées depuis les garanties avec réduction")
                
                fleet_guarantees = VehicleFleetGuarantee(vehicle_id=new_vehicle.id, **fleet_guarantee_data)
                self.session.add(fleet_guarantees)
                print(f"✓ Garanties flotte créées")

                # ============================================================
                # 8. CRÉATION AUTOMATIQUE DU CONTRAT PROFORMAT
                # ============================================================
                contrat_data = self._prepare_contract_data(new_vehicle, data, user_id)
                print(f"📋 Contrat data préparé - owner_id: {contrat_data.get('owner_id')}")
                
                success, contrat, contrat_message = self.contract_ctrl.create_proformat_contract(
                    vehicle_id=new_vehicle.id,
                    user_id=user_id,
                    data=contrat_data,
                    commit=False
                )
                
                if not success:
                    self.session.rollback()
                    return False, f"Erreur création contrat: {contrat_message}", None
                
                if contrat is None:
                    from addons.Automobiles.models.contract_models import Contrat
                    contrat = self.session.query(Contrat).filter(Contrat.vehicle_id == new_vehicle.id).first()
                    
                    if contrat is None:
                        self.session.rollback()
                        return False, "Le contrat a été créé mais n'a pas pu être récupéré", None
                    
                    print(f"✓ Contrat récupéré depuis la base: {contrat.id}")
                else:
                    print(f"✓ Contrat proformat créé: {contrat.numero_police}")

                # ============================================================
                # 9. AUDIT DE CRÉATION DU VÉHICULE
                # ============================================================
                audit = AuditVehicleLog(
                    user_id=user_id,
                    action="CREATE",
                    module="VEHICLES",
                    item_id=new_vehicle.id,
                    old_values=None,
                    new_values=json.dumps(audit_data, default=str),
                    ip_public=public_ip,
                    ip_local=local_ip,
                    timestamp=datetime.now()
                )

                # ============================================================
                # 10. CRÉATION DU CONDUCTEUR (Driver)
                # ============================================================
                driver_data = data.get('driver', {})
                if driver_data and driver_data.get('nom'):
                    from addons.Automobiles.models.driver_models import Driver
                    
                    # ✅ Vérifier les noms de colonnes
                    # Essayer plusieurs possibilités
                    licence_field = None
                    for field_name in ['num_permis', 'driver_licence_number', 'licence_number']:
                        if hasattr(Driver, field_name):
                            licence_field = field_name
                            break
                    
                    if licence_field:
                        # Utiliser le champ trouvé comme expression SQLAlchemy
                        licence_value = driver_data.get('num_permis', '')
                        existing_driver = self.session.query(Driver).filter(
                            getattr(Driver, licence_field) == licence_value
                        ).first()
                    else:
                        # Fallback: vérifier par nom et prénom
                        existing_driver = self.session.query(Driver).filter(
                            Driver.driver_name == driver_data.get('nom', '')
                        ).first()
                    
                    if existing_driver:
                        new_vehicle.driver_id = existing_driver.id
                        print(f"✓ Conducteur existant trouvé: {existing_driver.id}")
                    else:
                        # Créer un nouveau conducteur
                        # ✅ Utiliser les bons noms de colonnes
                        driver_kwargs = {
                            'driver_name': f"{driver_data.get('nom', '')} {driver_data.get('prenom', '')}".strip(),
                            'driver_birth_date': driver_data.get('date_naissance'),
                            'driver_licence_number': driver_data.get('num_permis', ''),
                            'driver_licence_category': driver_data.get('categorie_permis', ''),
                            'driver_licence_issued_at': driver_data.get('date_permis'),
                            'driver_licence_issued_by': driver_data.get('autorite_delivrance', '')
                        }
                        
                        # Supprimer les clés avec valeur None
                        driver_kwargs = {k: v for k, v in driver_kwargs.items() if v is not None}
                        
                        new_driver = Driver(**driver_kwargs)
                        self.session.add(new_driver)
                        self.session.flush()
                        new_vehicle.driver_id = new_driver.id
                        print(f"✓ Nouveau conducteur créé: {new_driver.id}")
                
                self.session.add(audit)
                self.session.commit()
                
                logger.log_info(f"Véhicule {new_vehicle.immatriculation} créé avec contrat {contrat.numero_police}")
                
                # ✅ Format attendu par _on_save_finished : (succès, message, id)
                return True, f"Véhicule {new_vehicle.immatriculation} créé avec succès", new_vehicle.id

            except Exception as e:
                last_error = e
                self.session.rollback()
                logger.warning(f"Tentative {attempt + 1}/{max_retries} échouée: {e}")
                import traceback
                traceback.print_exc()
                
                if attempt < max_retries - 1:
                    time.sleep(1)
                    from core.database import SessionLocal
                    self.session.close()
                    self.session = SessionLocal()
                    self.contract_ctrl.session = self.session
        
        return False, str(last_error), None

    def _prepare_contract_data(self, vehicle: Vehicle, data: Dict, user_id: int) -> Dict:
        """Prépare les données pour le contrat proformat"""
        
        # Valeurs par défaut
        prime_pure = float(data.get('prime_pure', 100000))
        taxes = prime_pure * 0.1925  # TVA 19.25%
        
        # Frais optionnels
        carte_rose = float(data.get('carte_rose', 25000))
        vignette = float(data.get('vignette', 5000))
        fichier_asac = float(data.get('fichier_asac', 2000))
        timbre = float(data.get('timbre', 1000))
        accessoires = float(data.get('accessoires', 0))
        commission = float(data.get('commission_intermediaire', 0))
        
        # Total TTC
        total_ttc = float(data.get('pttc', 0))
        print(f'le montant à payer est de {total_ttc} FCFA')
        
        return {
            'owner_id': data.get('owner_id'),
            'company_id': data.get('company_id', 1),
            'prime_pure': prime_pure,
            'accessoires': accessoires,
            'taxes_totales': taxes,
            'commission_intermediaire': commission,
            'prime_totale_ttc': total_ttc,
            'fleet_id': data.get('fleet_id')
        }
    
    def deactivate_vehicle(self, vehicle_id, user_id):
        try:
            vehicle = self.session.query(Vehicle).get(vehicle_id)
            if not vehicle:
                return False, "Véhicule introuvable."

            vehicle.is_active = False
            
            # 1. Convertir les dictionnaires en chaînes JSON
            new_values_json = json.dumps({"is_active": False})
            
            # 2. Création de l'audit
            audit = AuditVehicleLog(
                user_id=user_id,
                action="ARCHIVE",
                module="VEHICLES",
                item_id=vehicle_id,
                old_values=None, # Ou json.dumps(old_dict) si vous en avez un
                new_values=new_values_json, # On envoie la chaîne JSON
                timestamp=datetime.now(),
                ip_public=None,
                ip_local=None
            )
            
            self.session.add(audit)
            self.session.commit()
            return True, "Véhicule archivé."
        except Exception as e:
            self.session.rollback()
            return False, str(e)
      
    def get_client_ip(self):
        """Récupère l'IP locale de la machine."""
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return "None"
        
    def get_network_info(self):
        """Récupère simultanément l'IP Locale et l'IP Publique."""
        # 1. IP Locale (Rapide)
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
        except:
            local_ip = "127.0.0.1"

        # 2. IP Publique (Requête HTTP avec timeout court)
        try:
            # On utilise ipify avec un timeout de 1.5s pour ne pas bloquer l'UI
            response = requests.get('https://api.ipify.org?format=json', timeout=1.5)
            public_ip = response.json().get('ip')
        except:
            public_ip = "Offline"

        return local_ip, public_ip

    def update_vehicle(self, vehicle_id, new_data, user_id, ip_local=None, ip_public=None, **kwargs):
        """Met à jour un véhicule existant et ses relations."""
        
        local_ip = ip_local or self._get_local_ip()
        
        try:
            vehicle = self.session.query(Vehicle).get(vehicle_id)
            if not vehicle:
                return False, "Véhicule introuvable."
            
            # Capturer l'ancien état
            old_values = {
                "immatriculation": vehicle.immatriculation,
                "chassis": vehicle.chassis,
                "marque": vehicle.marque,
                "modele": vehicle.modele,
                "categorie": vehicle.categorie,
                "genre": vehicle.genre,
                "type_vehicule": vehicle.type_vehicule,
                "usage": vehicle.usage,
                "energie": vehicle.energie,
                "zone": vehicle.zone
            }
            
            # Mettre à jour les champs du véhicule
            vehicle_columns = Vehicle.__table__.columns.keys()
            for key, value in new_data.items():
                if key in vehicle_columns and key != 'id':
                    setattr(vehicle, key, value)
            
            # ============================================================
            # MISE À JOUR DU CONDUCTEUR - Adapté au modèle Driver existant
            # ============================================================
            driver_data = new_data.get('driver', {})
            if driver_data and driver_data.get('nom'):  # La clé 'nom' vient du formulaire
                from addons.Automobiles.models.driver_models import Driver
                
                if vehicle.driver_id:
                    # Mettre à jour le conducteur existant
                    driver = self.session.query(Driver).filter(Driver.id == vehicle.driver_id).first()
                    if driver:
                        # ✅ Utiliser les noms de colonnes du modèle Driver
                        driver.driver_name = driver_data.get('nom', driver.driver_name)
                        # Si le formulaire envoie 'prenom', on l'ajoute au nom
                        if driver_data.get('prenom'):
                            driver.driver_name = f"{driver_data.get('nom', '')} {driver_data.get('prenom', '')}".strip()
                        driver.driver_birth_date = driver_data.get('date_naissance', driver.driver_birth_date)
                        driver.driver_licence_number = driver_data.get('num_permis', driver.driver_licence_number)
                        driver.driver_licence_category = driver_data.get('categorie_permis', driver.driver_licence_category)
                        driver.driver_licence_issued_at = driver_data.get('date_permis', driver.driver_licence_issued_at)
                        driver.driver_licence_issued_by = driver_data.get('autorite_delivrance', driver.driver_licence_issued_by)
                        driver.updated_at = datetime.now()
                        print(f"✓ Conducteur mis à jour: {driver.id}")
                else:
                    # ✅ Créer un nouveau conducteur avec les colonnes du modèle
                    # Combiner nom et prénom si les deux sont présents
                    full_name = driver_data.get('nom', '')
                    if driver_data.get('prenom'):
                        full_name = f"{full_name} {driver_data.get('prenom', '')}".strip()
                    
                    new_driver = Driver(
                        driver_name=full_name,
                        driver_birth_date=driver_data.get('date_naissance'),
                        driver_licence_number=driver_data.get('num_permis', ''),
                        driver_licence_category=driver_data.get('categorie_permis', ''),
                        driver_licence_issued_at=driver_data.get('date_permis'),
                        driver_licence_issued_by=driver_data.get('autorite_delivrance', '')
                    )
                    self.session.add(new_driver)
                    self.session.flush()
                    vehicle.driver_id = new_driver.id
                    print(f"✓ Nouveau conducteur créé: {new_driver.id}")
            
            # Mettre à jour les garanties (si présentes dans les données)
            self._update_vehicle_guarantees(vehicle, new_data)
            
            # Mise à jour des champs de traçabilité
            vehicle.updated_at = datetime.now()
            vehicle.updated_by = user_id
            vehicle.last_ip = local_ip
            
            self.session.commit()
            self.session.refresh(vehicle)
            
            return True, "Véhicule mis à jour avec succès"
            
        except Exception as e:
            self.session.rollback()
            print(f"ERREUR update_vehicle: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, str(e)

    def _update_vehicle_guarantees(self, vehicle, data):
        """Met à jour les garanties du véhicule."""
        try:
            from addons.Automobiles.models.automobile_models import (
                VehicleGuarantee,
                VehicleGuaranteeReduction,
                VehicleGuaranteeRate,
                VehicleGuaranteeOption,
                VehicleFleetGuarantee
            )
            
            # Mise à jour des garanties brutes
            if vehicle.guarantees:
                for key in ['rc', 'dr', 'vol', 'vb', 'ipt', 'bris', 'ar', 'dta', 'in_garantie']:
                    value = data.get(f'amt_{key}', data.get(f'guarantees_{key}', 0))
                    if hasattr(vehicle.guarantees, key):
                        setattr(vehicle.guarantees, key, float(value or 0))
            
            # Mise à jour des réductions
            if vehicle.guarantee_reductions:
                for key in ['rc', 'dr', 'vol', 'vb', 'ipt', 'bris', 'ar', 'dta', 'in_garantie']:
                    value = data.get(f'red_{key}', data.get(f'reduction_{key}', 0))
                    if hasattr(vehicle.guarantee_reductions, key):
                        setattr(vehicle.guarantee_reductions, key, float(value or 0))
            
        except Exception as e:
            print(f"Erreur mise à jour garanties: {e}")

    def get_audit_logs(self, module_name):
        """
        Récupère les logs d'audit pour un module spécifique.
        """
        try:
            # On récupère tous les champs du modèle AuditLog
            return self.session.query(AuditVehicleLog)\
                .filter(AuditVehicleLog.module == module_name)\
                .order_by(AuditVehicleLog.timestamp.desc())\
                .all()
        except Exception as e:
            print(f"Erreur lors de la récupération des audits : {e}")
            return []
        
    def get_contact_stats(self):
        """Calcule les statistiques pour le camembert (Pie Chart) des contacts"""
        contacts = self.get_all_contacts()
        
        # On compte par type (Physique vs Morale)
        physique = len([c for c in contacts if getattr(c, 'type_contact', '') == 'Physique'])
        morale = len([c for c in contacts if getattr(c, 'type_contact', '') == 'Morale'])
        
        # On retourne le dictionnaire attendu par contacts_view.py
        return {
            'Physique': physique,
            'Morale': morale,
            'Total': len(contacts)
        }
          
    def get_all_compagnies(self):
        """
        Récupère la liste de toutes les compagnies d'assurance actives.
        Utile pour remplir le QComboBox dans le formulaire.
        """
        try:
            from addons.Automobiles.models.compagnies_models import Compagnie
            return self.session.query(Compagnie).filter(Compagnie.is_active == True).all()
        except Exception as e:
            print(f"Erreur lors de la récupération des compagnies : {e}")
            return []

    def get_compagnie_by_id(self, cie_id):
        """
        Récupère les détails d'une compagnie spécifique.
        """
        try:
            from addons.Automobiles.models.compagnies_models import Compagnie
            return self.session.query(Compagnie).filter(Compagnie.id == cie_id).first()
        except Exception as e:
            print(f"Erreur lors de la récupération de la compagnie {cie_id} : {e}")
            return None


    def get_rc_premium_from_matrix(self, cie_id, zone_saisie, categorie, energie, cv_saisi, avec_remorque=False, code_tarif=None):
        """
        Calcule la prime RC et la vignette Cameroun avec la nouvelle structure de table.
        """
        try:
            from addons.Automobiles.models.tarif_models import AutomobileTarif
            from addons.Automobiles.models.automobile_tranche import AutomobileTranche
            import re

            # --- 1. NORMALISATION ---
            zone_match = re.search(r'[A-C]', str(zone_saisie).upper())
            clean_zone = zone_match.group(0) if zone_match else str(zone_saisie).strip()
            
            clean_energie = str(energie).lower().strip()
            
            # Extraire uniquement les chiffres pour la catégorie (ex: "Cat 01" -> "01")
            # Mais la table utilise 'categorie' comme VARCHAR, donc on conserve la valeur telle quelle
            clean_cat = str(categorie).strip() if categorie else None

            # --- 2. RECHERCHE SQL ---
            query = self.session.query(AutomobileTarif).filter(
                AutomobileTarif.cie_id == cie_id,
                AutomobileTarif.zone == clean_zone
            )
            
            # Filtrer par code tarif si fourni
            if code_tarif and str(code_tarif).strip():
                query = query.filter(AutomobileTarif.tarif_code == str(code_tarif).strip())
            else:
                # Sinon filtrer par catégorie
                if clean_cat:
                    query = query.filter(AutomobileTarif.categorie == clean_cat)

            tarif = query.first()

            if not tarif:
                print(f"⚠️ Aucun tarif pour Cie:{cie_id}, Zone:{clean_zone}, Code:{code_tarif}, Cat:{clean_cat}")
                return {"rc": 0.0, "vignette": 0.0, "libelle": "", "categorie": clean_cat}

            # --- 3. DÉTERMINER LA TRANCHE DE PUISSANCE ---
            cv_val = int(cv_saisi or 0)
            
            # Définir les tranches manuellement (adapté à votre table)
            # Les colonnes prime1 à prime10 correspondent aux tranches
            if cv_val <= 2:
                tranche_index = 1
            elif cv_val <= 4:
                tranche_index = 2
            elif cv_val <= 6:
                tranche_index = 3
            elif cv_val <= 8:
                tranche_index = 4
            elif cv_val <= 10:
                tranche_index = 5
            elif cv_val <= 12:
                tranche_index = 6
            elif cv_val <= 14:
                tranche_index = 7
            elif cv_val <= 16:
                tranche_index = 8
            elif cv_val <= 18:
                tranche_index = 9
            else:
                tranche_index = 10

            # --- 4. SÉLECTIONNER LA BONNE COLONNE ---
            if avec_remorque:
                # Utiliser les colonnes remorq1 à remorq10
                col_name = f"remorq{tranche_index}"
            else:
                # Utiliser les colonnes prime1 à prime10
                col_name = f"prime{tranche_index}"

            # Récupérer la valeur
            prime_rc = float(getattr(tarif, col_name, 0.0))

            # --- 5. CALCUL VIGNETTE CAMEROUN ---
            vignette = 0
            if 2 <= cv_val <= 7:
                vignette = 30000
            elif 8 <= cv_val <= 13:
                vignette = 50000
            elif 14 <= cv_val <= 20:
                vignette = 75000
            elif cv_val > 20:
                vignette = 200000

            return {
                "rc": prime_rc,
                "vignette": vignette,
                "libelle": getattr(tarif, 'lib_tarif', ''),
                "categorie": getattr(tarif, 'categorie', clean_cat),
                "tranche": tranche_index,
                "tarif_code": getattr(tarif, 'tarif_code', '')
            }

        except Exception as e:
            print(f"❌ Erreur get_rc_premium: {e}")
            import traceback
            traceback.print_exc()
            return {"rc": 0.0, "vignette": 0.0, "libelle": "", "categorie": ""}


    def get_rc_premium_from_matrix_persistent(self, cie_id: int, zone_saisie: str, 
                                            categorie: str, energie: str, 
                                            cv_saisi: int, avec_remorque: bool = False,
                                            code_tarif: str = None) -> Dict:
        """
        Version avec cache SQLite pour le calcul des primes RC.
        """
        from core.local_db import cache
        
        # Générer une clé unique pour ce calcul
        cache_key = f"automobiles:rc:calc:{cie_id}:{zone_saisie}:{categorie}:{energie}:{cv_saisi}:{avec_remorque}:{code_tarif}"
        
        # Essayer le cache
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Calculer
        result = self.get_rc_premium_from_matrix(
            cie_id, zone_saisie, categorie, energie, 
            cv_saisi, avec_remorque, code_tarif
        )
        
        # Mettre en cache (TTL 24h car dépend des tarifs, rarement modifiés)
        cache.set(cache_key, result, module="automobiles", ttl_seconds=86400)
        
        return result

    def get_tarif_codes_by_compagnie(self, cie_id):
        """
        Récupère la liste des codes tarif disponibles pour une compagnie donnée.
        Retourne une liste de tuples (code, libelle) pour le QComboBox.
        """
        try:
            from addons.Automobiles.models.tarif_models import AutomobileTarif
            
            # Récupérer tous les tarifs distincts pour cette compagnie
            tarifs = self.session.query(AutomobileTarif.tarif_code, AutomobileTarif.lib_tarif)\
                .filter(AutomobileTarif.cie_id == cie_id)\
                .distinct()\
                .all()
            
            # Retourner une liste de tuples (code, libelle)
            return [(t.tarif_code, f"{t.tarif_code} - {t.lib_tarif}") for t in tarifs if t.tarif_code]
        except Exception as e:
            print(f"Erreur lors de la récupération des codes tarif : {e}")
            return []

    def get_tarif_categories_by_compagnie(self, cie_id):
        """
        Récupère les catégories disponibles pour une compagnie donnée.
        Retourne une liste de catégories distinctes pour le QComboBox.
        """
        try:
            from addons.Automobiles.models.tarif_models import AutomobileTarif

            categories = self.session.query(AutomobileTarif.categorie)\
                .filter(AutomobileTarif.cie_id == cie_id)\
                .distinct()\
                .all()

            return [c.categorie for c in categories if c.categorie]
        except Exception as e:
            print(f"Erreur lors de la récupération des catégories tarif : {e}")
            return []

    def get_tarif_categories_by_compagnie_and_code(self, cie_id, code_tarif):
        """
        Récupère les catégories disponibles pour un code tarif et une compagnie.
        """
        try:
            from addons.Automobiles.models.tarif_models import AutomobileTarif

            categories = self.session.query(AutomobileTarif.categorie)\
                .filter(
                    AutomobileTarif.cie_id == cie_id,
                    AutomobileTarif.tarif_code == str(code_tarif).strip()
                )\
                .distinct()\
                .all()

            return [c.categorie for c in categories if c.categorie]
        except Exception as e:
            print(f"Erreur lors de la récupération des catégories tarif pour le code {code_tarif}: {e}")
            return []
    
    def add_tranche(self, libelle, max_cv, user_id, local_ip, network_ip):
        from addons.Automobiles.models.tarif_models import AutomobileTarif
        new_tranche = AutomobileTarif(
            libelle=libelle,
            max_cv=max_cv,
            created_by=user_id,
            local=local_ip,
            network=network_ip
        )
        self.session.add(new_tranche)
        self.session.commit()

    def print_carte_rose(self, vehicle_data, parent_widget=None):
        """Lance l'impression de la carte rose avec les données reçues"""
        try:
            from addons.Automobiles.views.carte_rose_printer import CarteRosePrinter
            printer_tool = CarteRosePrinter(vehicle_data)
            printer_tool.print(parent_widget)  # ← Passer le parent_widget
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            print(f"Erreur impression : {e}")
            import traceback
            traceback.print_exc()
            # Correction 2: Utiliser un QMessageBox avec un parent valide
            if parent_widget:
                QMessageBox.warning(
                    parent_widget, 
                    "Impression", 
                    f"Erreur lors de l'impression : {str(e)}"
                )
            else:
                print(f"Erreur impression (pas de parent): {e}")

    def print_attestation(self, vehicle_data, parent_widget=None):
        """Lance l'impression de la carte rose avec les données reçues"""
        try:
            from addons.Automobiles.views.attestation_print import AttestationPrinter
            printer_tool = AttestationPrinter(vehicle_data)
            printer_tool.print(parent_widget)  # ← Passer le parent_widget
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            print(f"Erreur impression : {e}")
            import traceback
            traceback.print_exc()
            # Correction 2: Utiliser un QMessageBox avec un parent valide
            if parent_widget:
                QMessageBox.warning(
                    parent_widget, 
                    "Impression", 
                    f"Erreur lors de l'impression : {str(e)}"
                )
            else:
                print(f"Erreur impression (pas de parent): {e}")

    def print_vignette(self, vehicle_data, parent_widget=None):
        """
        Gère la génération et l'impression de l'Attestation de Timbre (Vignette).
        
        Args:
            vehicle_data (dict): Données du véhicule
            parent_widget (QWidget, optional): Widget parent pour les dialogues
        """
        try:
            # 1. Vérification des données essentielles
            required_fields = ['immatriculation', 'marque', 'modele', 'owner']
            missing_fields = [field for field in required_fields if not vehicle_data.get(field)]
            
            if missing_fields:
                from PySide6.QtWidgets import QMessageBox
                if parent_widget:
                    QMessageBox.warning(
                        parent_widget,
                        "Données manquantes",
                        f"Impossible de générer l'attestation.\n\n"
                        f"Champs manquants : {', '.join(missing_fields)}"
                    )
                print(f"Erreur : Données manquantes - {missing_fields}")
                return
            
            # 2. Vérification du montant du timbre
            montant_timbre = vehicle_data.get('amt_dta', 0)
            if not montant_timbre or float(montant_timbre) == 0:
                print("Avertissement : Le montant du droit de timbre est à 0.")
                if parent_widget:
                    from PySide6.QtWidgets import QMessageBox
                    reply = QMessageBox.question(
                        parent_widget,
                        "Montant nul",
                        "Le montant du droit de timbre est à 0.\n\n"
                        "Voulez-vous continuer quand même ?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        return
            
            # 3. Importation de l'outil d'impression
            try:
                from addons.Automobiles.views.vignette_printer import VignettePrinter
            except ImportError as e:
                print(f"Erreur d'import : {e}")
                if parent_widget:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.critical(
                        parent_widget,
                        "Erreur d'import",
                        "Impossible de charger le module d'impression.\n\n"
                        "Vérifiez que le fichier vignette_printer.py est présent."
                    )
                return
            
            # 4. Création du dossier d'export si nécessaire
            import os
            export_dir = os.path.join(os.path.expanduser("~"), "Documents", "Attestations_Assurance")
            if not os.path.exists(export_dir):
                try:
                    os.makedirs(export_dir)
                    print(f"Dossier créé : {export_dir}")
                except Exception as e:
                    print(f"Impossible de créer le dossier d'export : {e}")
            
            # 5. Initialisation de l'imprimeur
            printer_tool = VignettePrinter(vehicle_data, export_dir=export_dir)
            
            # 6. Lancement de l'impression
            # Le parent widget est passé pour centrer les dialogues
            printer_tool.print(parent_widget)
            
        except ImportError:
            print("Erreur : Le fichier vignette_printer.py est introuvable dans le dossier.")
            if parent_widget:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(
                    parent_widget,
                    "Erreur",
                    "Le module d'impression est introuvable.\n\n"
                    "Vérifiez l'installation de l'application."
                )
                
        except Exception as e:
            print(f"Erreur lors de l'exécution de l'impression : {str(e)}")
            import traceback
            traceback.print_exc()
            
            if parent_widget:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(
                    parent_widget,
                    "Erreur d'impression",
                    f"Une erreur est survenue lors de la génération du document :\n\n{str(e)}"
                )
    
    def print_devis(self, vehicle_data, parent_widget=None):
        """
        Gère la génération et l'impression du devis d'assurance.
        
        Args:
            vehicle_data (dict): Données du véhicule et du contrat
            parent_widget (QWidget, optional): Widget parent pour les dialogues
        """
        try:
            # 1. Vérification des données essentielles
            required_fields = ['immatriculation', 'marque', 'modele', 'owner']
            missing_fields = [field for field in required_fields if not vehicle_data.get(field)]
            
            if missing_fields:
                from PySide6.QtWidgets import QMessageBox
                if parent_widget:
                    QMessageBox.warning(
                        parent_widget,
                        "Données manquantes",
                        f"Impossible de générer le devis.\n\n"
                        f"Champs manquants : {', '.join(missing_fields)}"
                    )
                print(f"Erreur : Données manquantes - {missing_fields}")
                return
            
            # 2. Vérification du montant total
            prime_totale = vehicle_data.get('prime_nette', 0)
            if not prime_totale or float(prime_totale) == 0:
                print("Avertissement : Le montant de la prime est à 0.")
                if parent_widget:
                    from PySide6.QtWidgets import QMessageBox
                    reply = QMessageBox.question(
                        parent_widget,
                        "Montant nul",
                        "Le montant de la prime est à 0.\n\n"
                        "Voulez-vous continuer quand même ?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        return
            
            # 3. Importation de l'outil d'impression
            try:
                from addons.Automobiles.views.devis_printer import DevisPrinter
            except ImportError as e:
                print(f"Erreur d'import : {e}")
                if parent_widget:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.critical(
                        parent_widget,
                        "Erreur d'import",
                        "Impossible de charger le module d'impression du devis.\n\n"
                        "Vérifiez que le fichier devis_printer.py est présent."
                    )
                return
            
            # 4. Création du dossier d'export si nécessaire
            import os
            export_dir = os.path.join(os.path.expanduser("~"), "Documents", "Devis_Assurance")
            if not os.path.exists(export_dir):
                try:
                    os.makedirs(export_dir)
                    print(f"Dossier créé : {export_dir}")
                except Exception as e:
                    print(f"Impossible de créer le dossier d'export : {e}")
            
            # 5. Initialisation de l'imprimeur
            printer_tool = DevisPrinter(vehicle_data, export_dir=export_dir)
            
            # 6. Lancement de l'impression
            printer_tool.print(parent_widget)
            
        except ImportError:
            print("Erreur : Le fichier devis_printer.py est introuvable dans le dossier.")
            if parent_widget:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(
                    parent_widget,
                    "Erreur",
                    "Le module d'impression du devis est introuvable.\n\n"
                    "Vérifiez l'installation de l'application."
                )
                
        except Exception as e:
            print(f"Erreur lors de l'exécution de l'impression du devis : {str(e)}")
            import traceback
            traceback.print_exc()
            
            if parent_widget:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(
                    parent_widget,
                    "Erreur d'impression",
                    f"Une erreur est survenue lors de la génération du devis :\n\n{str(e)}"
                )

    def _calculate_base_premium(self, vehicle: Vehicle, data: Dict) -> float:
        """Calcule la prime de base selon les caractéristiques du véhicule"""
        base = 75000  # Prime de base
        
        # Ajustement selon la puissance fiscale
        puissance = data.get('puissance', getattr(vehicle, 'puissance', 0))
        if puissance:
            if puissance <= 5:
                base = 50000
            elif puissance <= 7:
                base = 65000
            elif puissance <= 10:
                base = 85000
            else:
                base = 100000 + (puissance - 10) * 5000
        
        # Ajustement selon la zone
        zone = data.get('zone', getattr(vehicle, 'zone', 'urbain'))
        zone_coeff = {'urbain': 1.1, 'rural': 0.9, 'mixte': 1.0}
        base *= zone_coeff.get(zone, 1.0)
        
        # Ajustement selon la catégorie
        categorie = data.get('categorie', getattr(vehicle, 'categorie', 'particulier'))
        categorie_coeff = {'particulier': 1.0, 'utilitaire': 1.2, 'luxe': 1.5, 'transport': 1.3}
        base *= categorie_coeff.get(categorie, 1.0)
        
        return round(base, 0)
    
    def _get_local_ip(self) -> str:
        """Récupère l'IP locale"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def validate_contract(self, vehicle_id: int, user_id: int, data: Dict = None) -> Tuple[bool, str]:
        """
        Valide le contrat proformat d'un véhicule et le transforme en contrat actif
        """
        try:
            # Récupérer le proformat
            proformat = self.contract_ctrl.get_proformat_by_vehicle(vehicle_id)
            if not proformat:
                return False, "Aucun proformat trouvé pour ce véhicule"
            
            # Transformer en contrat actif
            success, message = self.contract_ctrl.update_proformat_to_active(
                contrat_id=proformat.id,
                user_id=user_id,
                data=data
            )
            
            return success, message
            
        except Exception as e:
            logger.error(f"Erreur validation contrat: {e}")
            return False, str(e)

    # vehicle_controller.py

    # Dans le contrôleur des véhicules
    def get_all(self):
        return self.session.query(Vehicle).all()

    def count_all(self):
        return self.session.query(Vehicle).count()

    def update_vehicle_garantees(self, vehicle_id, data):
        """
        Met à jour un véhicule avec les données fournies.
        
        Args:
            vehicle_id: ID du véhicule
            data: Dictionnaire des champs à mettre à jour
        
        Returns:
            tuple: (success, message/vehicle)
        """
        try:
            session = self.session
            vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
            
            if not vehicle:
                return False, f"Véhicule {vehicle_id} non trouvé"
            
            # Mettre à jour les attributs
            for key, value in data.items():
                if hasattr(vehicle, key):
                    setattr(vehicle, key, value)
            
            session.commit()
            session.refresh(vehicle)
            
            return True, vehicle
            
        except Exception as e:
            session.rollback()
            print(f"Erreur update_vehicle: {e}")
            return False, str(e)

    # addons/Automobiles/controllers/automobile_controller.py
    # Ajouter ces méthodes à la classe VehicleController

    # ============================================================================
    # MÉTHODES SQLITE PERSISTANT (entre deux sessions)
    # ============================================================================
    
    def get_vehicle_stats(self):
        """
        Calcule les statistiques des véhicules.
        
        Returns:
            dict: Statistiques des véhicules
        """
        try:
            total = self.session.query(Vehicle).count()
            
            # Véhicules actifs
            actifs = self.session.query(Vehicle).filter(
                Vehicle.is_active == True
            ).count() if hasattr(Vehicle, 'is_active') else total
            
            # Véhicules par statut
            by_status = {}
            if hasattr(Vehicle, 'statut'):
                results = self.session.query(
                    Vehicle.statut, 
                    func.count(Vehicle.id)
                ).group_by(Vehicle.statut).all()
                by_status = {status: count for status, count in results}
            
            # Prime totale
            total_premium = self.session.query(
                func.sum(Vehicle.prime_nette)
            ).scalar() or 0
            
            return {
                'total': total,
                'actifs': actifs,
                'by_status': by_status,
                'total_premium': total_premium
            }
            
        except Exception as e:
            print(f"Erreur get_vehicle_stats: {e}")
            return {'total': 0, 'actifs': 0, 'by_status': {}, 'total_premium': 0}

    def get_all_vehicles_persistent(self, force_refresh: bool = False, 
                                     async_callback: callable = None) -> list[Vehicle]:
        """
        Récupère les véhicules avec cache SQLite persistant
        Les données restent disponibles même après redémarrage de l'application
        """
        from core.local_db import cache
        import json
        
        cache_key = "automobiles:vehicles:persistent"
        
        if not force_refresh:
            # Essayer le cache SQLite
            cached_data = cache.get(cache_key)
            if cached_data:
                # Reconstruire les objets à partir des dictionnaires
                vehicles = [self._dict_to_vehicle(v) for v in cached_data]
                if async_callback:
                    async_callback(vehicles)
                return vehicles
        
        # Charger depuis la base
        vehicles = self.get_all_vehicles(force_refresh=True)
        
        # Sérialiser pour SQLite
        serialized = [self._vehicle_to_dict(v) for v in vehicles]
        
        # Sauvegarder en cache (TTL 24h = 86400 secondes)
        cache.set(cache_key, serialized, module="automobiles", ttl_seconds=86400)
        
        if async_callback:
            async_callback(vehicles)
        return vehicles
    
    def get_vehicle_by_id_persistent(self, vehicle_id: int):
        """
        Récupère un véhicule depuis le cache SQLite par ID
        Utile pour les accès rapides sans base de données
        """
        from core.local_db import cache
        
        cache_key = f"automobiles:vehicles:id:{vehicle_id}"
        
        # Essayer le cache
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Charger depuis la base
        vehicle = self.get_vehicles_by_id(vehicle_id)
        if vehicle:
            vehicle_dict = self._vehicle_to_dict(vehicle)
            cache.set(cache_key, vehicle_dict, module="automobiles", ttl_seconds=86400)
            return vehicle_dict
        
        return None
    
    def get_vehicles_owner_persistent(self, owner_id: int):
        """
        Récupère les véhicules d'un propriétaire depuis le cache SQLite
        """
        from core.local_db import cache
        
        cache_key = f"automobiles:vehicles:owner:{owner_id}"
        
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        vehicles = self.get_vehicles_by_owner_id(owner_id)
        result = [self._vehicle_to_dict(v) for v in vehicles]
        
        cache.set(cache_key, result, module="automobiles", ttl_seconds=86400)
        return result
    
    def get_dashboard_stats_persistent(self, fleet_id: int = None, timeout_seconds: int = 30):
        """
        Récupère les statistiques dashboard depuis le cache SQLite avec timeout
        """
        from core.local_db import cache
        
        cache_key = f"automobiles:dashboard:stats:fleet:{fleet_id}"
        
        # Essayer le cache SQLite
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Charger depuis la base avec timeout
        try:
            with timeout(timeout_seconds):
                stats = self.get_dashboard_stats(fleet_id)
                # Sauvegarder en cache SQLite (TTL 1 heure)
                cache.set(cache_key, stats, module="automobiles", ttl_seconds=3600)
                return stats
        except TimeoutError as e:
            logger.error(f"Timeout dashboard stats fleet {fleet_id}: {e}")
            return {"total": 0, "actifs": 0, "expires": 0, "prime_totale": "0 FCFA"}
        
    def get_compagnies_persistent(self):
        """
        Récupère toutes les compagnies depuis le cache SQLite
        (Référentiel - rarement modifié)
        """
        from core.local_db import cache
        
        cache_key = "automobiles:compagnies:persistent"
        
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        compagnies = self.get_all_compagnies()
        result = [self._compagnie_to_dict(c) for c in compagnies]
        
        # TTL plus long pour les référentiels (7 jours)
        cache.set(cache_key, result, module="automobiles", ttl_seconds=604800)
        
        return result
    
    def get_contacts_persistent(self):
        """
        Récupère tous les contacts depuis le cache SQLite
        """
        from core.local_db import cache
        
        cache_key = "automobiles:contacts:persistent"
        
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        contacts = self.get_all_contacts()
        result = [self._contact_to_dict(c) for c in contacts]
        
        cache.set(cache_key, result, module="automobiles", ttl_seconds=86400)
        
        return result
    
    def get_tarif_compagnie_persistent(self, cie_id: int):
        """
        Récupère les tarifs d'une compagnie depuis le cache SQLite
        """
        from core.local_db import cache
        
        cache_key = f"automobiles:tarifs:compagnie:{cie_id}"
        
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        from addons.Automobiles.models.tarif_models import AutomobileTarif
        
        tarifs = self.session.query(AutomobileTarif).filter(
            AutomobileTarif.cie_id == cie_id,
            AutomobileTarif.is_active == True
        ).all()
        
        result = [self._tarif_to_dict(t) for t in tarifs]
        
        # TTL plus long pour les tarifs (peu modifiés)
        cache.set(cache_key, result, module="automobiles", ttl_seconds=604800)
        
        return result
    
    
    # ============================================================================
    # MÉTHODES D'INVALIDATION DU CACHE SQLITE
    # ============================================================================
    
    def invalidate_all_cache(self):
        """
        Invalide tout le cache SQLite pour le module automobiles
        À appeler après des modifications importantes (création, modification, suppression)
        """
        from core.local_db import cache
        
        # Supprimer tout le module
        cache.clear_module("automobiles")
        
        # Supprimer aussi le cache mémoire
        self._invalidate_cache()
        
        logger.info("🗑️ Cache SQLite du module automobiles invalidé")
    
    def invalidate_vehicle_cache(self, vehicle_id: int = None):
        """
        Invalide le cache spécifique aux véhicules
        """
        from core.local_db import cache
        
        # Supprimer la liste générale
        cache.delete("automobiles:vehicles:persistent")
        
        # Supprimer un véhicule spécifique si fourni
        if vehicle_id:
            cache.delete(f"automobiles:vehicles:id:{vehicle_id}")
        
        # Supprimer les stats dashboard
        cache.delete("automobiles:dashboard:stats:fleet:None")
        
        self._invalidate_cache("automobiles:vehicles")
        
        logger.info(f"🗑️ Cache véhicules invalidé (id={vehicle_id})")
    
    def invalidate_compagnies_cache(self):
        """Invalide le cache des compagnies"""
        from core.local_db import cache
        
        cache.delete("automobiles:compagnies:persistent")
        self._invalidate_cache("automobiles:compagnies")
        
        logger.info("🗑️ Cache compagnies invalidé")
    
    def invalidate_contacts_cache(self):
        """Invalide le cache des contacts"""
        from core.local_db import cache
        
        cache.delete("automobiles:contacts:persistent")
        self._invalidate_cache("automobiles:contacts")
        
        logger.info("🗑️ Cache contacts invalidé")
       
    def _get_cached(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache mémoire"""
        if not hasattr(self, '_cache'):
            self._cache = {}
        
        cached = self._cache.get(key)
        if cached and 'timestamp' in cached:
            import time
            # Cache valide 5 minutes (300 secondes)
            if time.time() - cached['timestamp'] < 300:
                return cached['data']
            else:
                del self._cache[key]
        return None
    
    def _set_cache(self, key: str, data: Any):
        """Sauvegarde une valeur dans le cache mémoire"""
        if not hasattr(self, '_cache'):
            self._cache = {}
        
        import time
        self._cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def _invalidate_cache(self, pattern: str = None):
        """Invalide le cache mémoire"""
        if not hasattr(self, '_cache'):
            self._cache = {}
        
        if pattern:
            keys_to_remove = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self._cache[key]
        else:
            self._cache.clear()
        
        logger.info(f"🗑️ Cache invalidé: {pattern or 'tous'}")
    
    def refresh_cache(self):
        """Force le rafraîchissement du cache"""
        self._invalidate_cache()
        return self.get_all_vehicles(force_refresh=True)
    # ============================================================================
    # MÉTHODES DE SÉRIALISATION
    # ============================================================================
    
    def _vehicle_to_dict(self, vehicle: Vehicle) -> Dict:
        """Convertit un véhicule en dictionnaire pour SQLite"""
        return {
            'id': vehicle.id,
            'immatriculation': vehicle.immatriculation,
            'chassis': vehicle.chassis,
            'marque': vehicle.marque,
            'modele': vehicle.modele,
            'annee': vehicle.annee,
            'energie': vehicle.energie,
            'categorie': vehicle.categorie,
            'zone': vehicle.zone,
            'usage': vehicle.usage,
            'places': vehicle.places,
            'statut': vehicle.statut,
            'owner_id': vehicle.owner_id,
            'compagny_id': vehicle.compagny_id,
            'fleet_id': vehicle.fleet_id,
            'prime_nette': vehicle.prime_nette,
            'prime_brute': vehicle.prime_brute,
            'pttc': vehicle.pttc,
            'is_active': vehicle.is_active,
            'created_at': vehicle.created_at.isoformat() if vehicle.created_at else None,
            # Garanties
            'amt_rc': getattr(vehicle, 'amt_rc', getattr(getattr(vehicle, 'guarantees', None), 'rc', 0)),
            'amt_dr': getattr(vehicle, 'amt_dr', getattr(getattr(vehicle, 'guarantees', None), 'dr', 0)),
            'amt_vol': getattr(vehicle, 'amt_vol', getattr(getattr(vehicle, 'guarantees', None), 'vol', 0)),
            'amt_vb': getattr(vehicle, 'amt_vb', getattr(getattr(vehicle, 'guarantees', None), 'vb', 0)),
            'amt_in': getattr(vehicle, 'amt_in', getattr(getattr(vehicle, 'guarantees', None), 'in_garantie', 0)),
            'amt_bris': getattr(vehicle, 'amt_bris', getattr(getattr(vehicle, 'guarantees', None), 'bris', 0)),
            'amt_ar': getattr(vehicle, 'amt_ar', getattr(getattr(vehicle, 'guarantees', None), 'ar', 0)),
            'amt_dta': getattr(vehicle, 'amt_dta', getattr(getattr(vehicle, 'guarantees', None), 'dta', 0)),
            'amt_ipt': getattr(vehicle, 'amt_ipt', getattr(getattr(vehicle, 'guarantees', None), 'ipt', 0)),
        }
    
    def _dict_to_vehicle(self, data: Dict) -> Vehicle:
        """Reconstruit un véhicule à partir d'un dictionnaire"""
        # Créer un objet Vehicle temporaire
        vehicle = Vehicle()
        
        # Remplir les attributs
        for key, value in data.items():
            if hasattr(vehicle, key):
                setattr(vehicle, key, value)
        
        return vehicle
    
    def _compagnie_to_dict(self, compagnie: Compagnie) -> Dict:
        """Convertit une compagnie en dictionnaire"""
        return {
            'id': compagnie.id,
            'code': compagnie.code,
            'nom': compagnie.nom,
            'email': compagnie.email,
            'telephone': compagnie.telephone,
            'adresse': compagnie.adresse,
            'num_debut': compagnie.num_debut,
            'num_fin': compagnie.num_fin,
            'is_active': compagnie.is_active,
        }
    
    def _contact_to_dict(self, contact: Contact) -> Dict:
        """Convertit un contact en dictionnaire"""
        return {
            'id': contact.id,
            'nom': contact.nom,
            'prenom': contact.prenom,
            'telephone': contact.telephone,
            'email': contact.email,
            'adresse': contact.adresse,
            'ville': contact.ville,
            'type_client': contact.type_client,
            'nature': contact.nature,
            'code_client': contact.code_client,
            'vip_status': contact.vip_status,
        }
    
    def _tarif_to_dict(self, tarif) -> Dict:
        """Convertit un tarif en dictionnaire"""
        return {
            'id': tarif.id,
            'cie_id': tarif.cie_id,
            'tarif_code': tarif.tarif_code,
            'lib_tarif': tarif.lib_tarif,
            'categorie': tarif.categorie,
            'zone': tarif.zone,
        }
    
    # ============================================================================
    # MÉTHODES DE SYNCHRONISATION
    # ============================================================================

    # automobile_controller.py - Ajoutez ces méthodes optimisées

    def get_vehicles_light(self, fleet_id: int = None, limit: int = 50):
        """
        Récupère les véhicules avec seulement les champs essentiels
        Utilisé pour l'affichage initial
        """
        try:
            query = self.session.query(
                Vehicle.id,
                Vehicle.immatriculation,
                Vehicle.marque,
                Vehicle.modele,
                Vehicle.categorie,
                Vehicle.statut,
                Vehicle.prime_nette,
                Vehicle.date_debut,
                Vehicle.date_fin,
                Vehicle.owner_id
            ).filter(Vehicle.is_active == True)
            
            if fleet_id:
                query = query.filter(Vehicle.fleet_id == fleet_id)
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        except Exception as e:
            logger.error(f"Erreur get_vehicles_light: {e}")
            return []

    def get_vehicle_with_relations_optimized(self, vehicle_id: int):
        """
        Récupère un véhicule avec ses relations en une seule requête
        Utilise selectinload pour éviter N+1
        """
        try:
            from sqlalchemy.orm import selectinload, joinedload
            
            vehicle = self.session.query(Vehicle).options(
                selectinload(Vehicle.contrat).selectinload(Contrat.paiements),
                joinedload(Vehicle.owner),
                joinedload(Vehicle.compagny),
                selectinload(Vehicle.fleet)
            ).filter(Vehicle.id == vehicle_id).first()
            
            return vehicle
        except Exception as e:
            logger.error(f"Erreur get_vehicle_with_relations_optimized: {e}")
            return None

    def sync_from_server(self):
        """
        Synchronise les données du cache SQLite avec le serveur
        Appelé périodiquement ou au démarrage
        """
        from core.local_db import cache
        import threading
        
        def sync():
            logger.info("🔄 Synchronisation des données automobiles...")
            
            # Forcer le rafraîchissement des listes principales
            self.get_all_vehicles_persistent(force_refresh=True)
            self.get_compagnies_persistent(force_refresh=True)
            self.get_contacts_persistent(force_refresh=True)
            self.get_dashboard_stats_persistent(force_refresh=True)
            
            logger.info("✅ Synchronisation terminée")
        
        thread = threading.Thread(target=sync, daemon=True)
        thread.start()
    
    def get_cache_stats(self) -> Dict:
        """Retourne les statistiques du cache SQLite"""
        from core.local_db import cache
        
        stats = cache.get_stats()
        return {
            'sqlite_size_mb': stats.get('db_size_mb', 0),
            'sqlite_entries': stats.get('total_entries', 0),
            'memory_entries': len(self._object_cache),
            'memory_keys': list(self._object_cache.keys())
        }

    def check_connection(self) -> bool:
        """
        Vérifie si la connexion à la base de données est active
        """
        try:
            with timeout(5):
                self.session.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Connexion DB perdue: {e}")
            return False

    def reconnect(self):
        """
        Force la reconnexion à la base de données
        """
        try:
            from core.database import SessionLocal
            self.session.close()
            self.session = SessionLocal()
            self.contract_ctrl.session = self.session
            logger.info("✅ Reconnexion DB réussie")
            return True
        except Exception as e:
            logger.error(f"❌ Échec reconnexion DB: {e}")
            return False

    def get_vehicle_guarantees(self, vehicle_id):
        """
        Récupère toutes les garanties d'un véhicule (brutes et avec réduction).
        
        Args:
            vehicle_id: ID du véhicule
        
        Returns:
            dict: Dictionnaire des garanties
        """
        try:
            vehicle = self.get_vehicles_by_id(vehicle_id)
            print(vehicle.date_debut)
            if not vehicle:
                return {}
            
            # Utiliser les relations guarantees et guarantee_reductions si présentes
            guarantees = getattr(vehicle, 'guarantees', None)
            reductions = getattr(vehicle, 'guarantee_reductions', None)

            return {
                'date_debut': vehicle.date_debut,
                'date_fin': vehicle.date_fin,
                # Garanties brutes
                'rc': float(getattr(guarantees, 'rc', 0) if guarantees else 0),
                'dr': float(getattr(guarantees, 'dr', 0) if guarantees else 0),
                'vol': float(getattr(guarantees, 'vol', 0) if guarantees else 0),
                'vb': float(getattr(guarantees, 'vb', 0) if guarantees else 0),
                'in': float(getattr(guarantees, 'in_garantie', 0) if guarantees else 0),
                'bris': float(getattr(guarantees, 'bris', 0) if guarantees else 0),
                'ar': float(getattr(guarantees, 'ar', 0) if guarantees else 0),
                'dta': float(getattr(guarantees, 'dta', 0) if guarantees else 0),
                'ipt': float(getattr(guarantees, 'ipt', 0) if guarantees else 0),
                # Garanties avec réduction (pour la flotte)
                'val_red_rc': float(getattr(reductions, 'rc', 0) if reductions else 0),
                'val_red_dr': float(getattr(reductions, 'dr', 0) if reductions else 0),
                'val_red_vol': float(getattr(reductions, 'vol', 0) if reductions else 0),
                'val_red_vb': float(getattr(reductions, 'vb', 0) if reductions else 0),
                'val_red_in': float(getattr(reductions, 'in_garantie', 0) if reductions else 0),
                'val_red_bris': float(getattr(reductions, 'bris', 0) if reductions else 0),
                'val_red_ar': float(getattr(reductions, 'ar', 0) if reductions else 0),
                'val_red_dta': float(getattr(reductions, 'dta', 0) if reductions else 0),
                'val_red_ipt': float(getattr(reductions, 'ipt', 0) if reductions else 0),
                # Taux de réduction
                'red_rc': float(getattr(vehicle, 'red_rc', 0) or 0),
                'red_dr': float(getattr(vehicle, 'red_dr', 0) or 0),
                'red_vol': float(vehicle.red_vol or 0),
                'red_vb': float(vehicle.red_vb or 0),
                'red_in': float(vehicle.red_in or 0),
                'red_bris': float(vehicle.red_bris or 0),
                'red_ar': float(vehicle.red_ar or 0),
                'red_dta': float(vehicle.red_dta or 0),
                'red_ipt': float(vehicle.red_ipt or 0),
            }
            
        except Exception as e:
            print(f"Erreur get_vehicle_guarantees: {e}")
            return {}

    def format_phone_number(self, phone):
        """
        Formate un numéro de téléphone avec le préfixe +237
        
        Args:
            phone: Numéro de téléphone (str, int ou None)
        
        Returns:
            str: Numéro formaté avec +237
        """
        if not phone:
            return 'N/A'
        
        # Convertir en string
        phone_str = str(phone).strip()
        
        # Supprimer les espaces et caractères spéciaux
        phone_str = phone_str.replace(' ', '').replace('-', '').replace('.', '')
        
        # Si le numéro commence déjà par +237, le retourner tel quel
        if phone_str.startswith('+237'):
            return phone_str
        
        # Si le numéro commence par 237 (sans le +)
        if phone_str.startswith('237'):
            return f'+{phone_str}'
        
        # Si le numéro commence par 0 (ex: 0XXXXXXXXX)
        if phone_str.startswith('0'):
            return f'+237{phone_str[1:]}'  # Enlever le 0 et ajouter +237
        
        # Si le numéro a 9 chiffres (format local sans indicatif)
        if len(phone_str) == 9 and phone_str.isdigit():
            return f'+237{phone_str}'
        
        # Si le numéro a 8 chiffres (format sans indicatif)
        if len(phone_str) == 8 and phone_str.isdigit():
            return f'+237{phone_str}'
        
        # Si le numéro commence par un indicatif international différent
        if phone_str.startswith('+') and not phone_str.startswith('+237'):
            # Garder l'indicatif existant
            return phone_str
        
        # Par défaut, ajouter +237
        return f'+237{phone_str}'

    # addons/Automobiles/controllers/automobile_controller.py

    def get_vehicle_details_data(self, vehicle_id: int) -> Optional[Dict]:
        """
        Récupère toutes les données d'un véhicule pour l'affichage des détails.
        Cette méthode contient TOUTES les requêtes SQL et s'exécute dans un thread.
        
        Args:
            vehicle_id: ID du véhicule
        
        Returns:
            Dict: Dictionnaire contenant toutes les données du véhicule
        """
        try:
            from sqlalchemy.orm import selectinload, joinedload
            from addons.Automobiles.models.automobile_models import (
                Vehicle, VehicleClassification, VehicleGuarantee,
                VehicleGuaranteeReduction, VehicleGuaranteeRate,
                VehicleGuaranteeOption, VehicleFleetGuarantee
            )
            from addons.Automobiles.models.contact_models import Contact
            from addons.Automobiles.models.compagnies_models import Compagnie
            from addons.Automobiles.models.driver_models import Driver
            from addons.Automobiles.models.contract_models import Contrat
            
            # ============================================================
            # 1. CHARGEMENT DU VÉHICULE AVEC SES RELATIONS
            # ============================================================
            vehicle = self.session.query(Vehicle).options(
                selectinload(Vehicle.driver),
                selectinload(Vehicle.classification),
                selectinload(Vehicle.guarantees),
                selectinload(Vehicle.guarantee_reductions),
                selectinload(Vehicle.guarantee_rates),
                selectinload(Vehicle.guarantee_options),
                selectinload(Vehicle.fleet_guarantees),
                joinedload(Vehicle.owner),
                joinedload(Vehicle.compagny),
                selectinload(Vehicle.fleet),
                selectinload(Vehicle.contract)
            ).filter(Vehicle.id == vehicle_id).first()
            if not vehicle:
                return None

            # ============================================================
            # 2. CONTRAT
            # ============================================================
            contract = vehicle.contract

            # ============================================================
            # 3. PROPRIÉTAIRE
            # ============================================================
            owner_name = "N/A"
            owner_phone = "N/A"
            owner_email = "N/A"
            owner_city = "Yaoundé"
            if vehicle.owner:
                owner = vehicle.owner
                owner_name = f"{getattr(owner, 'nom', '')} {getattr(owner, 'prenom', '')}".strip()
                owner_phone = self.format_phone_number(getattr(owner, 'telephone', 'N/A'))
                owner_email = getattr(owner, 'email', 'N/A')
                owner_city = getattr(owner, 'ville', 'Yaoundé')

            # ============================================================
            # 4. COMPAGNIE
            # ============================================================
            compagny_name = "Non définie"
            if vehicle.compagny:
                compagny_name = getattr(vehicle.compagny, 'nom', 'N/A')

            # ============================================================
            # 5. CONDUCTEUR (Driver)
            # ============================================================
            driver_name = "N/A"
            driver_birth = "N/A"
            driver_licence = "N/A"
            driver_category = "N/A"
            driver_issued_at = "N/A"
            driver_issued_by = "N/A"
            
            if vehicle.driver:
                driver = vehicle.driver
                driver_name = getattr(driver, 'driver_name', 'N/A')
                driver_birth = driver.driver_birth_date.strftime('%Y/%m/%d') if driver.driver_birth_date else "N/A"
                driver_licence = getattr(driver, 'driver_licence_number', 'N/A')
                driver_category = getattr(driver, 'driver_licence_category', 'N/A')
                driver_issued_at = driver.driver_licence_issued_at.strftime('%Y/%m/%d') if driver.driver_licence_issued_at else "N/A"
                driver_issued_by = getattr(driver, 'driver_licence_issued_by', 'N/A')

            # ============================================================
            # 6. CLASSIFICATION ASAC
            # ============================================================
            classification = vehicle.classification
            if classification:
                categorie = getattr(classification, 'categorie_id', 'N/A')
                genre = getattr(classification, 'genre_id', 'N/A')
                type_vehicule = getattr(classification, 'type_id', 'N/A')
                usage = getattr(classification, 'usage_id', 'N/A')
                energie = getattr(classification, 'energie_id', 'N/A')
                zone = getattr(classification, 'zone_id', 'N/A')
            else:
                categorie = getattr(vehicle, 'categorie', 'N/A')
                genre = getattr(vehicle, 'genre', 'N/A')
                type_vehicule = getattr(vehicle, 'type_vehicule', 'N/A')
                usage = getattr(vehicle, 'usage', 'N/A')
                energie = getattr(vehicle, 'energie', 'N/A')
                zone = getattr(vehicle, 'zone', 'N/A')

            # ============================================================
            # 7. GARANTIES
            # ============================================================
            guarantees = vehicle.guarantees
            guarantee_reductions = vehicle.guarantee_reductions
            guarantee_rates = vehicle.guarantee_rates
            guarantee_options = vehicle.guarantee_options
            fleet_guarantees = vehicle.fleet_guarantees

            # ============================================================
            # 8. DATES
            # ============================================================
            def format_date(date_obj):
                if date_obj is None:
                    return ""
                if hasattr(date_obj, 'strftime'):
                    return date_obj.strftime('%Y/%m/%d')
                return str(date_obj)

            date_debut_str = format_date(vehicle.date_debut)
            date_fin_str = format_date(vehicle.date_fin)
            date_mise_circulation_str = format_date(vehicle.date_mise_circulation)

            # ============================================================
            # 9. CONSTRUCTION DU DICTIONNAIRE DE RÉSULTATS
            # ============================================================
            vehicle_data = {
                # --- IDENTIFICATION ---
                'id': getattr(vehicle, 'id', None),
                'immatriculation': getattr(vehicle, 'immatriculation', 'N/A'),
                'chassis': getattr(vehicle, 'chassis', 'N/A'),
                'marque': getattr(vehicle, 'marque', 'N/A'),
                'modele': getattr(vehicle, 'modele', 'N/A'),
                'annee': str(getattr(vehicle, 'annee', 'N/A')),
                'date_mise_circulation': date_mise_circulation_str,
                
                # --- CLASSIFICATION ASAC ---
                'categorie': categorie,
                'genre': genre,
                'type_vehicule': type_vehicule,
                'usage': usage,
                'energie': energie,
                'zone': zone,
                
                # --- CONTRAT ---
                'numero_police': getattr(contract, 'numero_police', 'Aucun contrat actif') if contract else 'Aucun contrat actif',
                'date_debut': date_debut_str,
                'date_fin': date_fin_str,
                'prime_totale': getattr(contract, 'prime_totale_ttc', 0.0) if contract else 0.0,
                'montant_paye': getattr(contract, 'montant_paye', 0.0) if contract else 0.0,
                'statut_paiement': getattr(contract, 'statut_paiement', 'NON_PAYE') if contract else 'NON_PAYE',
                
                # --- CARACTÉRISTIQUES ---
                'puissance_fiscale': getattr(vehicle, 'puissance_fiscale', 0),
                'places': str(getattr(vehicle, 'places', '5')),
                'cylindree': getattr(vehicle, 'cylindree', 0),
                'ptac': getattr(vehicle, 'ptac', 0),
                'charge_utile': getattr(vehicle, 'charge_utile', 0),
                
                # --- OPTIONS ---
                'has_remorque': getattr(vehicle, 'has_remorque', False),
                'remorque_inflammable': getattr(vehicle, 'remorque_inflammable', False),
                'remorque_immat': getattr(vehicle, 'remorque_immat', ''),
                'double_commande': getattr(vehicle, 'double_commande', False),
                'engin_portuaire': getattr(vehicle, 'engin_portuaire', False),
                'rc_eleves': getattr(vehicle, 'rc_eleves', False),
                
                # --- CODES TARIFAIRES ---
                'code_tarif': getattr(vehicle, 'code_tarif', 'N/A'),
                'libele_tarif': getattr(vehicle, 'libele_tarif', 'N/A'),
                'code_assure': getattr(vehicle, 'code_assure', 'N/A'),
                
                # --- FINANCES ---
                'prime_emise': getattr(vehicle, 'prime_emise', 0),
                'valeur_neuf': getattr(vehicle, 'valeur_neuf', 0),
                'valeur_venale': getattr(vehicle, 'valeur_venale', 0),
                'prime_nette': getattr(vehicle, 'prime_nette', 0),
                'prime_brute': getattr(vehicle, 'prime_brute', 0),
                'reduction': getattr(vehicle, 'reduction', 0),
                'carte_rose': getattr(vehicle, 'carte_rose', 0),
                'accessoires': getattr(vehicle, 'accessoires', 0),
                'tva': getattr(vehicle, 'tva', 0),
                'fichier_asac': getattr(vehicle, 'fichier_asac', 0),
                'vignette': getattr(vehicle, 'vignette', 0),
                'pttc': getattr(vehicle, 'pttc', 0),
                'nbr_jour': getattr(vehicle, 'nbr_jour', 0),
                
                # --- PROPRIÉTAIRES ---
                'owner': owner_name,
                'owner_id': getattr(vehicle, 'owner_id', None),
                'compagny': compagny_name,
                'compagny_id': getattr(vehicle, 'compagny_id', None),
                'phone': owner_phone,
                'email': owner_email,
                'city': owner_city,
                
                # --- CONDUCTEUR ---
                'driver_name': driver_name,
                'driver_birth': driver_birth,
                'driver_licence': driver_licence,
                'driver_category': driver_category,
                'driver_issued_at': driver_issued_at,
                'driver_issued_by': driver_issued_by,
                
                # --- GARANTIES BRUTES (Montants) ---
                'amt_rc': getattr(guarantees, 'rc', 0) if guarantees else 0,
                'amt_dr': getattr(guarantees, 'dr', 0) if guarantees else 0,
                'amt_vol': getattr(guarantees, 'vol', 0) if guarantees else 0,
                'amt_vb': getattr(guarantees, 'vb', 0) if guarantees else 0,
                'amt_ipt': getattr(guarantees, 'ipt', 0) if guarantees else 0,
                'amt_bris': getattr(guarantees, 'bris', 0) if guarantees else 0,
                'amt_ar': getattr(guarantees, 'ar', 0) if guarantees else 0,
                'amt_dta': getattr(guarantees, 'dta', 0) if guarantees else 0,
                'amt_in_garantie': getattr(guarantees, 'in_garantie', 0) if guarantees else 0,
                
                # --- GARANTIES AVEC RÉDUCTION ---
                'red_rc': getattr(guarantee_reductions, 'rc', 0) if guarantee_reductions else 0,
                'red_dr': getattr(guarantee_reductions, 'dr', 0) if guarantee_reductions else 0,
                'red_vol': getattr(guarantee_reductions, 'vol', 0) if guarantee_reductions else 0,
                'red_vb': getattr(guarantee_reductions, 'vb', 0) if guarantee_reductions else 0,
                'red_ipt': getattr(guarantee_reductions, 'ipt', 0) if guarantee_reductions else 0,
                'red_bris': getattr(guarantee_reductions, 'bris', 0) if guarantee_reductions else 0,
                'red_ar': getattr(guarantee_reductions, 'ar', 0) if guarantee_reductions else 0,
                'red_dta': getattr(guarantee_reductions, 'dta', 0) if guarantee_reductions else 0,
                'red_in_garantie': getattr(guarantee_reductions, 'in_garantie', 0) if guarantee_reductions else 0,
                
                # --- TAUX DES GARANTIES ---
                'rate_rc': getattr(guarantee_rates, 'rc', 0) if guarantee_rates else 0,
                'rate_dr': getattr(guarantee_rates, 'dr', 0) if guarantee_rates else 0,
                'rate_vol': getattr(guarantee_rates, 'vol', 0) if guarantee_rates else 0,
                'rate_vb': getattr(guarantee_rates, 'vb', 0) if guarantee_rates else 0,
                'rate_ipt': getattr(guarantee_rates, 'ipt', 0) if guarantee_rates else 0,
                'rate_bris': getattr(guarantee_rates, 'bris', 0) if guarantee_rates else 0,
                'rate_ar': getattr(guarantee_rates, 'ar', 0) if guarantee_rates else 0,
                'rate_dta': getattr(guarantee_rates, 'dta', 0) if guarantee_rates else 0,
                'rate_in_garantie': getattr(guarantee_rates, 'in_garantie', 0) if guarantee_rates else 0,
                
                # --- OPTIONS (Checkboxes) ---
                'check_rc': getattr(guarantee_options, 'rc', False) if guarantee_options else False,
                'check_dr': getattr(guarantee_options, 'dr', False) if guarantee_options else False,
                'check_vol': getattr(guarantee_options, 'vol', False) if guarantee_options else False,
                'check_vb': getattr(guarantee_options, 'vb', False) if guarantee_options else False,
                'check_ipt': getattr(guarantee_options, 'ipt', False) if guarantee_options else False,
                'check_bris': getattr(guarantee_options, 'bris', False) if guarantee_options else False,
                'check_ar': getattr(guarantee_options, 'ar', False) if guarantee_options else False,
                'check_dta': getattr(guarantee_options, 'dta', False) if guarantee_options else False,
                'check_in_garantie': getattr(guarantee_options, 'in_garantie', False) if guarantee_options else False,
                
                # --- GARANTIES FLOTTE ---
                'fleet_rc': getattr(fleet_guarantees, 'rc', 0) if fleet_guarantees else 0,
                'fleet_dr': getattr(fleet_guarantees, 'dr', 0) if fleet_guarantees else 0,
                'fleet_vol': getattr(fleet_guarantees, 'vol', 0) if fleet_guarantees else 0,
                'fleet_vb': getattr(fleet_guarantees, 'vb', 0) if fleet_guarantees else 0,
                'fleet_ipt': getattr(fleet_guarantees, 'ipt', 0) if fleet_guarantees else 0,
                'fleet_bris': getattr(fleet_guarantees, 'bris', 0) if fleet_guarantees else 0,
                'fleet_ar': getattr(fleet_guarantees, 'ar', 0) if fleet_guarantees else 0,
                'fleet_dta': getattr(fleet_guarantees, 'dta', 0) if fleet_guarantees else 0,
                'fleet_in_garantie': getattr(fleet_guarantees, 'in_garantie', 0) if fleet_guarantees else 0,
                
                # --- STATUT ---
                'statut': getattr(vehicle, 'statut', 'ACTIF'),
                'is_active': getattr(vehicle, 'is_active', True),
                
                # --- TRACABILITÉ ---
                'created_at': vehicle.created_at.strftime('%d/%m/%Y %H:%M') if vehicle.created_at else None,
                'updated_at': vehicle.updated_at.strftime('%d/%m/%Y %H:%M') if vehicle.updated_at else None,
            }
            
            return vehicle_data
            
        except Exception as e:
            logger.error(f"Erreur get_vehicle_details_data: {e}")
            import traceback
            traceback.print_exc()
            return None