
from socket import socket
import requests
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from addons.Automobiles.controllers.automobile_controller import VehicleController
from addons.Automobiles.models.automobile_models import AuditVehicleLog, Vehicle
from addons.Automobiles.models.contact_models import Contact
from addons.Automobiles.models.flottes_models import Fleet
from datetime import date, datetime, timezone
import json
import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas


class FleetController:
    def __init__(self, session: Session, current_user_id):
        self.session = session
        self.current_user_id = current_user_id
        self.vehicle_service = VehicleController(session)

    # ==================== CRÉATION DE FLOTTE ====================
    
    def create_fleet(self, data, user_id):
        """
        Crée une nouvelle flotte en incluant les totaux financiers 
        issus de la dernière ligne du tableau et gère l'audit.
        """
        try:
            local_ip, public_ip = self.get_network_info()

            def to_f(key):
                val = data.get(key)
                try:
                    return float(val) if val is not None else 0.0
                except (ValueError, TypeError):
                    return 0.0

            new_fleet = Fleet(
                nom_flotte=data.get('nom_flotte'),
                code_flotte=str(data.get('code_flotte', '')).strip().upper(),
                owner_id=data.get('owner_id'),
                assureur=data.get('assureur'),
                type_gestion=data.get('type_gestion'),
                remise_flotte=to_f('remise_flotte'),
                
                # Totaux des garanties
                total_rc=to_f('total_rc'),
                total_dr=to_f('total_dr'),
                total_vol=to_f('total_vol'),
                total_vb=to_f('total_vb'),
                total_in=to_f('total_in'),
                total_bris=to_f('total_bris'),
                total_ar=to_f('total_ar'),
                total_dta=to_f('total_dta'),
                total_ipt=to_f('total_ipt'),
                total_pttc=to_f('total_pttc'),
                total_prime_nette=to_f('total_prime_nette'),
                
                statut=data.get('statut', 'Actif'),
                is_active=data.get('is_active', True),
                date_debut=data.get('date_debut'),
                date_fin=data.get('date_fin'),
                observations=data.get('observations'),
                created_by=user_id,
                created_ip=public_ip,
                last_ip=local_ip
            )

            self.session.add(new_fleet)
            self.session.flush()

            # Audit
            serializable_data = data.copy()
            for key, value in serializable_data.items():
                if isinstance(value, (date, datetime)):
                    serializable_data[key] = value.isoformat()

            log = AuditVehicleLog(
                user_id=user_id,
                action="CREATION_FLOTTE_COMPLETE",
                module="FLEET_MANAGEMENT",
                item_id=new_fleet.id,
                old_values=None,
                new_values=json.dumps(serializable_data),
                ip_local=local_ip,
                ip_public=public_ip
            )
            self.session.add(log)
            self.session.commit()
            
            return True, new_fleet.id

        except Exception as e:
            self.session.rollback()
            print(f"❌ Erreur SQL create_fleet: {e}")
            if "unique constraint" in str(e).lower():
                return False, f"Le code flotte '{data.get('code_flotte')}' est déjà utilisé."
            return False, str(e)

    # ==================== MISE À JOUR DE FLOTTE ====================
    
    def update_fleet_data(self, fleet_id, data, user_id):
        """
        Met à jour une flotte existante avec les totaux financiers et l'audit.
        """
        try:
            local_ip, public_ip = self.get_network_info()

            def to_f(key):
                val = data.get(key)
                try:
                    return float(val) if val is not None and val != '' else 0.0
                except (ValueError, TypeError):
                    return 0.0

            code_flotte = data.get('code_flotte')
            if isinstance(code_flotte, str):
                code_flotte = code_flotte.strip().upper()
                if not code_flotte:
                    code_flotte = None

            owner_id = data.get('owner_id')
            if isinstance(owner_id, str) and not owner_id.isdigit():
                owner_id = None

            old_fleet = self.session.query(Fleet).filter(Fleet.id == fleet_id).first()
            if not old_fleet:
                return False, "Flotte introuvable."

            self.session.query(Fleet).filter(Fleet.id == fleet_id).update({
                "nom_flotte": data.get('nom_flotte'),
                "code_flotte": code_flotte,
                "owner_id": owner_id,
                "assureur": data.get('assureur'),
                "type_gestion": data.get('type_gestion'),
                "remise_flotte": to_f('remise_flotte'),
                
                "total_rc": to_f('total_rc'),
                "total_dr": to_f('total_dr'),
                "total_vol": to_f('total_vol'),
                "total_vb": to_f('total_vb'),
                "total_in": to_f('total_in'),
                "total_bris": to_f('total_bris'),
                "total_ar": to_f('total_ar'),
                "total_dta": to_f('total_dta'),
                "total_ipt": to_f('total_ipt'),
                "total_pttc": to_f('total_pttc'),
                "total_prime_nette": to_f('total_prime_nette'),
                
                "statut": data.get('statut'),
                "is_active": data.get('is_active'),
                "date_debut": data.get('date_debut'),
                "date_fin": data.get('date_fin'),
                "observations": data.get('observations'),
                
                "updated_at": datetime.now(timezone.utc),
                "updated_by": user_id,
                "last_ip": local_ip
            }, synchronize_session=False)

            serializable_data = data.copy()
            for key, value in serializable_data.items():
                if isinstance(value, (date, datetime)):
                    serializable_data[key] = value.isoformat()

            audit_log = AuditVehicleLog(
                user_id=user_id,
                action="UPDATE_FLOTTE_COMPLETE",
                module="FLEET_MANAGEMENT",
                item_id=fleet_id,
                old_values=None,
                new_values=json.dumps(serializable_data),
                ip_local=local_ip,
                ip_public=public_ip
            )
            self.session.add(audit_log)
            self.session.commit()
            
            return True, "Flotte mise à jour avec succès."

        except Exception as e:
            self.session.rollback()
            print(f"❌ Erreur SQL update_fleet_data: {e}")
            if "unique constraint" in str(e).lower():
                return False, f"Le code flotte '{data.get('code_flotte')}' est déjà utilisé."
            return False, str(e)

    # ==================== GESTION DES VÉHICULES DANS LA FLOTTE ====================
    
    def update_fleet_vehicles(self, fleet_id, selected_vehicle_ids, user_id):
        """
        Met à jour la relation entre une flotte et ses véhicules.
        Lors de l'ajout d'un véhicule, initialise les champs amt_fleet_*_val
        avec les valeurs amt_* du véhicule.
        """
        try:
            if isinstance(selected_vehicle_ids, dict):
                print("ERREUR: Le contrôleur a reçu un dictionnaire au lieu d'une liste d'IDs.")
                return False, "Format de données invalide (attendu: liste d'IDs)."

            clean_ids = [int(i) for i in selected_vehicle_ids if str(i).isdigit() or isinstance(i, int)]
            local_ip, public_ip = self.get_network_info()

            # 1. Détacher les véhicules qui ne sont plus sélectionnés
            self.session.query(Vehicle).filter(
                Vehicle.fleet_id == fleet_id,
                ~Vehicle.id.in_(clean_ids)
            ).update({"fleet_id": None}, synchronize_session=False)

            # 2. Attacher les nouveaux véhicules sélectionnés
            # ⭐ IMPORTANT: Initialiser les champs amt_fleet_*_val avec les valeurs amt_*
            if clean_ids:
                # Récupérer les véhicules concernés
                vehicles_to_update = self.session.query(Vehicle).filter(
                    Vehicle.id.in_(clean_ids)
                ).all()
                
                for vehicle in vehicles_to_update:
                    # Mettre à jour la flotte
                    vehicle.fleet_id = fleet_id
                    
                    # ⭐ Initialiser les champs de flotte si ils sont à 0
                    if vehicle.amt_fleet_rc_val == 0:
                        vehicle.amt_fleet_rc_val = vehicle.amt_rc or 0
                    if vehicle.amt_fleet_dr_val == 0:
                        vehicle.amt_fleet_dr_val = vehicle.amt_dr or 0
                    if vehicle.amt_fleet_vol_val == 0:
                        vehicle.amt_fleet_vol_val = vehicle.amt_vol or 0
                    if vehicle.amt_fleet_vb_val == 0:
                        vehicle.amt_fleet_vb_val = vehicle.amt_vb or 0
                    if vehicle.amt_fleet_in_val == 0:
                        vehicle.amt_fleet_in_val = vehicle.amt_in or 0
                    if vehicle.amt_fleet_bris_val == 0:
                        vehicle.amt_fleet_bris_val = vehicle.amt_bris or 0
                    if vehicle.amt_fleet_ar_val == 0:
                        vehicle.amt_fleet_ar_val = vehicle.amt_ar or 0
                    if vehicle.amt_fleet_dta_val == 0:
                        vehicle.amt_fleet_dta_val = vehicle.amt_dta or 0
                    if vehicle.amt_fleet_ipt_val == 0:
                        vehicle.amt_fleet_ipt_val = vehicle.amt_ipt or 0

            # 3. Audit
            audit = AuditVehicleLog(
                user_id=user_id,
                action="UPDATE_RELATION_FLEET",
                module="FLEETS",
                item_id=fleet_id,
                new_values=json.dumps({"vehicle_ids": clean_ids}), 
                ip_local=local_ip,
                ip_public=public_ip,
                timestamp=datetime.now(timezone.utc)
            )
            self.session.add(audit)
            self.session.commit()
            
            return True, "Relation Flotte-Véhicules mise à jour avec succès."

        except Exception as e:
            self.session.rollback()
            print(f"Erreur Update Fleet Relation: {str(e)}")
            return False, f"Erreur base de données : {str(e)}"

    # ==================== GESTION DES GARANTIES DANS LA FLOTTE ====================
    
    def update_vehicle_guarantees_in_fleet(self, vehicle_id, garanties):
        """
        Met à jour les montants des garanties d'un véhicule dans le cadre d'une flotte.
        ⭐ Les valeurs sont stockées dans les champs amt_fleet_*_val.
        
        Args:
            vehicle_id: ID du véhicule
            garanties: Dictionnaire des garanties avec leurs montants
                    Ex: {'rc': 50000, 'dr': 25000, 'vol': 100000, ...}
        
        Returns:
            tuple: (success, message)
        """
        try:
            vehicle = self.vehicle_service.get_vehicles_by_id(vehicle_id)
            if not vehicle:
                return False, f"Véhicule {vehicle_id} non trouvé"
            
            # ⭐ Mapping vers les nouveaux champs amt_fleet_*_val
            mapping = {
                'rc': 'amt_fleet_rc_val',
                'dr': 'amt_fleet_dr_val',
                'vol': 'amt_fleet_vol_val',
                'vb': 'amt_fleet_vb_val',
                'in': 'amt_fleet_in_val',
                'bris': 'amt_fleet_bris_val',
                'ar': 'amt_fleet_ar_val',
                'dta': 'amt_fleet_dta_val',
                'ipt': 'amt_fleet_ipt_val',
            }
            
            # Mettre à jour les attributs
            for key, amount in garanties.items():
                if key in mapping:
                    setattr(vehicle, mapping[key], amount)
            
            # Sauvegarder
            update_data = {
                'amt_fleet_rc_val': garanties.get('rc', 0),
                'amt_fleet_dr_val': garanties.get('dr', 0),
                'amt_fleet_vol_val': garanties.get('vol', 0),
                'amt_fleet_vb_val': garanties.get('vb', 0),
                'amt_fleet_in_val': garanties.get('in', 0),
                'amt_fleet_bris_val': garanties.get('bris', 0),
                'amt_fleet_ar_val': garanties.get('ar', 0),
                'amt_fleet_dta_val': garanties.get('dta', 0),
                'amt_fleet_ipt_val': garanties.get('ipt', 0),
            }
            
            success, result = self.vehicle_service.update_vehicle(vehicle_id, update_data, self.current_user_id)
            
            if success:
                return True, "Garanties mises à jour avec succès"
            else:
                return False, result
            
        except Exception as e:
            print(f"Erreur update_vehicle_guarantees_in_fleet: {e}")
            import traceback
            traceback.print_exc()
            return False, str(e)

    def get_vehicle_guarantees_for_fleet(self, vehicle_id):
        """
        Récupère les montants des garanties d'un véhicule pour l'affichage dans la flotte.
        ⭐ Utilise les champs amt_fleet_*_val.
        
        Args:
            vehicle_id: ID du véhicule
        
        Returns:
            dict: Dictionnaire des garanties avec leurs montants actuels dans la flotte
        """
        try:
            vehicle = self.vehicle_service.get_vehicles_by_id(vehicle_id)
            if not vehicle:
                return {}
            
            return {
                'rc': float(getattr(vehicle, 'amt_fleet_rc_val', 0) or 0),
                'dr': float(getattr(vehicle, 'amt_fleet_dr_val', 0) or 0),
                'vol': float(getattr(vehicle, 'amt_fleet_vol_val', 0) or 0),
                'vb': float(getattr(vehicle, 'amt_fleet_vb_val', 0) or 0),
                'in': float(getattr(vehicle, 'amt_fleet_in_val', 0) or 0),
                'bris': float(getattr(vehicle, 'amt_fleet_bris_val', 0) or 0),
                'ar': float(getattr(vehicle, 'amt_fleet_ar_val', 0) or 0),
                'dta': float(getattr(vehicle, 'amt_fleet_dta_val', 0) or 0),
                'ipt': float(getattr(vehicle, 'amt_fleet_ipt_val', 0) or 0),
            }
            
        except Exception as e:
            print(f"Erreur get_vehicle_guarantees_for_fleet: {e}")
            return {}

    def reset_vehicle_guarantees_to_original(self, vehicle_id):
        """
        Remet les garanties d'un véhicule à leurs valeurs originales (amt_*)
        
        Args:
            vehicle_id: ID du véhicule
        
        Returns:
            tuple: (success, message)
        """
        try:
            vehicle = self.vehicle_service.get_vehicles_by_id(vehicle_id)
            if not vehicle:
                return False, "Véhicule non trouvé"
            
            update_data = {
                'amt_fleet_rc_val': float(vehicle.amt_rc or 0),
                'amt_fleet_dr_val': float(vehicle.amt_dr or 0),
                'amt_fleet_vol_val': float(vehicle.amt_vol or 0),
                'amt_fleet_vb_val': float(vehicle.amt_vb or 0),
                'amt_fleet_in_val': float(vehicle.amt_in or 0),
                'amt_fleet_bris_val': float(vehicle.amt_bris or 0),
                'amt_fleet_ar_val': float(vehicle.amt_ar or 0),
                'amt_fleet_dta_val': float(vehicle.amt_dta or 0),
                'amt_fleet_ipt_val': float(vehicle.amt_ipt or 0),
            }
            
            success, result = self.vehicle_service.update_vehicle(vehicle_id, update_data, self.current_user_id)
            
            if success:
                return True, "Garanties réinitialisées avec succès"
            else:
                return False, result
            
        except Exception as e:
            return False, str(e)

    # ==================== CALCULS ET STATISTIQUES ====================
    
    def calculate_fleet_total_premium(self, fleet_id):
        """
        Calcule le total des primes pour une flotte.
        ⭐ Utilise la propriété total_fleet_amount du véhicule
        """
        try:
            fleet = self.session.query(Fleet).filter(Fleet.id == fleet_id).first()
            if not fleet or not fleet.vehicles:
                return 0
            
            total = 0
            for vehicle in fleet.vehicles:
                total += vehicle.total_fleet_amount
            
            return total
        except Exception as e:
            print(f"Erreur calculate_fleet_total_premium: {e}")
            return 0

    def get_fleet_vehicles_with_custom_guarantees(self, fleet_id):
        """
        Récupère les véhicules d'une flotte avec leurs garanties personnalisées.
        ⭐ Utilise les propriétés du modèle Vehicle.
        """
        try:
            fleet = self.session.query(Fleet).options(
                joinedload(Fleet.vehicles)
            ).filter(Fleet.id == fleet_id).first()
            
            if not fleet:
                return []
            
            result = []
            for vehicle in fleet.vehicles:
                result.append({
                    'id': vehicle.id,
                    'immatriculation': vehicle.immatriculation,
                    'marque': vehicle.marque,
                    'modele': vehicle.modele,
                    'original_amount': vehicle.total_original_amount,
                    'fleet_amount': vehicle.total_fleet_amount,
                    'reduction': vehicle.total_fleet_reduction,
                    'reduction_percent': vehicle.fleet_reduction_percent,
                    'has_custom': vehicle.has_custom_fleet_guarantees,
                    'guarantees': vehicle.get_fleet_guarantees_dict()
                })
            
            return result
        except Exception as e:
            print(f"Erreur get_fleet_vehicles_with_custom_guarantees: {e}")
            return []

    def get_fleet_stats(self, fleet_id):
        """Récupère les indicateurs clés (KPI) pour le tableau de bord d'une flotte."""
        try:
            fleet = self.session.query(Fleet).filter(Fleet.id == fleet_id).first()
            if not fleet:
                return {"total_vehicules": 0, "prime_globale": 0}
            
            total_vehicules = len(fleet.vehicles) if fleet.vehicles else 0
            prime_globale = sum(v.total_fleet_amount for v in fleet.vehicles) if fleet.vehicles else 0
            
            return {
                "total_vehicules": total_vehicules,
                "prime_globale": prime_globale,
            }
        except Exception as e:
            print(f"Erreur get_fleet_stats: {e}")
            return {"total_vehicules": 0, "prime_globale": 0}

    # ==================== RÉCUPÉRATION DE DONNÉES ====================
    
    def get_all_fleets(self):
        try:
            from sqlalchemy.orm import joinedload
            return self.session.query(Fleet).options(joinedload(Fleet.owner)).all()
        except Exception as e:
            print(f"Erreur lors de la récupération des flottes : {e}")
            return []
    
    def get_fleets_by_owner(self, owner_id):
        """Récupère les flottes d'un propriétaire"""
        try:
            from addons.Automobiles.models import Fleet, Compagnie
            from sqlalchemy.orm import joinedload
            
            results = self.session.query(Fleet).filter(
                Fleet.owner_id == owner_id
            ).options(
                joinedload(Fleet.compagnie)
            ).all()
            
            return results
        except Exception as e:
            print(f"Erreur: {e}")
            return []

    def get_fleet_with_details(self, fleet_id):
        """Récupère une flotte avec toutes ses relations chargées"""
        try:
            fleet = self.session.query(Fleet).options(
                joinedload(Fleet.owner),
                joinedload(Fleet.vehicles)
            ).filter(Fleet.id == fleet_id).first()
            
            return fleet
        except Exception as e:
            print(f"Erreur lors de la récupération de la flotte {fleet_id}: {e}")
            return None

    def get_all_vehicles(self):
        return self.vehicle_service.get_all_vehicles()

    # flotte_controller.py - Ajouter ces méthodes

    def create_fleet_contract(self, fleet_id, data, user_id):
        """Crée un contrat pour une flotte entière"""
        try:
            from addons.Automobiles.models.contract_models import Contrat, ContractStatus
            
            local_ip, public_ip = self.get_network_info()
            
            fleet = self.session.query(Fleet).filter(Fleet.id == fleet_id).first()
            if not fleet:
                return False, "Flotte non trouvée"
            
            # Générer un numéro de police unique pour la flotte
            numero_police = self._generate_fleet_police_number(fleet)
            
            # Créer le contrat de flotte
            contrat = Contrat(
                numero_police=numero_police,
                owner_id=fleet.owner_id,
                company_id=fleet.assureur,
                fleet_id=fleet_id,
                vehicle_id=None,
                type_contrat="FLOTTE",
                statut=ContractStatus.ACTIF,
                date_debut=fleet.date_debut,
                date_fin=fleet.date_fin,
                prime_pure=data.get('prime_pure', fleet.total_prime_nette or 0),
                accessoires=data.get('accessoires', 0),
                taxes_totales=data.get('taxes_totales', 0),
                commission_intermediaire=data.get('commission_intermediaire', 0),
                prime_totale_ttc=data.get('prime_totale_ttc', fleet.total_pttc or 0),
                montant_paye=0,
                statut_paiement="NON_PAYE",
                created_by=user_id,
                created_ip=public_ip,
                last_ip=local_ip
            )
            
            self.session.add(contrat)
            self.session.flush()  # Pour obtenir l'ID du contrat
            
            # Optionnel: Enregistrer l'audit (si la méthode existe)
            if hasattr(self, '_log_action'):
                self._log_action(
                    action="CREATE_FLEET_CONTRACT",
                    fleet_id=fleet_id,
                    contrat_id=contrat.id,
                    user_id=user_id,
                    local_ip=local_ip,
                    public_ip=public_ip,
                    new_values={
                        'numero_police': numero_police,
                        'montant_total': contrat.prime_totale_ttc
                    }
                )
            
            self.session.commit()
            
            return True, contrat
            
        except Exception as e:
            self.session.rollback()
            print(f"Erreur create_fleet_contract: {e}")
            return False, str(e)
    
    def _create_vehicle_sub_contract(self, vehicle, parent_contract_id, user_id, local_ip, public_ip):
        """
        Crée un sous-contrat pour un véhicule individuel dans une flotte
        """
        from addons.Automobiles.models.contract_models import Contrat, ContractStatus
        
        # Calculer la prime individuelle du véhicule
        vehicle_prime = vehicle.total_fleet_amount or vehicle.prime_nette or 0
        
        sub_contract = Contrat(
            numero_police=f"{vehicle.immatriculation}-FLT-{parent_contract_id}",
            owner_id=vehicle.owner_id,
            company_id=vehicle.compagny_id,
            vehicle_id=vehicle.id,
            fleet_id=vehicle.fleet_id,
            contrat_flotte_id=parent_contract_id,
            type_contrat="VEHICULE_FLOTTE",
            statut=ContractStatus.ACTIF,
            date_debut=vehicle.date_debut,
            date_fin=vehicle.date_fin,
            prime_pure=vehicle_prime,
            prime_totale_ttc=vehicle_prime,
            montant_paye=0,
            statut_paiement="NON_PAYE",
            created_by=user_id,
            created_ip=public_ip,
            last_ip=local_ip
        )
        
        self.session.add(sub_contract)
        return sub_contract

    def _generate_fleet_police_number(self, fleet):
        """Génère un numéro de police unique pour la flotte"""
        from datetime import datetime
        import random
        
        year = datetime.now().year
        fleet_code = fleet.code_flotte or fleet.nom_flotte[:5].upper()
        random_num = random.randint(1000, 9999)
        
        return f"FLT-{fleet_code}-{year}-{random_num}"

    def get_fleet_contract(self, fleet_id):
        """Récupère le contrat principal d'une flotte"""
        from addons.Automobiles.models.contract_models import Contrat
        
        return self.session.query(Contrat).filter(
            Contrat.fleet_id == fleet_id,
            Contrat.type_contrat == "FLOTTE"
        ).first()

    def get_fleet_vehicle_contracts(self, fleet_id):
        """Récupère les contrats des véhicules d'une flotte"""
        from addons.Automobiles.models.contract_models import Contrat
        
        return self.session.query(Contrat).filter(
            Contrat.fleet_id == fleet_id,
            Contrat.type_contrat == "VEHICULE_FLOTTE"
        ).all()

    def get_all_contacts_for_combo(self):
        """Retourne les contacts de nature physique depuis la table Contact."""
        try:
            compagnies = self.session.query(Contact.id, Contact.nom)\
                .filter(Contact.nature == "Physique")\
                .all()
            
            return [(contact_id, contact_nom) for contact_id, contact_nom in compagnies]
        except Exception as e:
            print(f"Erreur lors de la récupération des contacts : {e}")
            return []

    def get_all_compagnies_for_combo(self):
        """Retourne la liste des compagnies d'assurance pour les combobox."""
        try:
            from addons.Automobiles.models import Compagnie
            
            compagnies = self.session.query(Compagnie.id, Compagnie.nom).filter(
                Compagnie.is_active == True
            ).all()
            
            return [(comp_id, comp_nom) for comp_id, comp_nom in compagnies]
        except Exception as e:
            print(f"Erreur lors de la récupération des compagnies : {e}")
            return []

    def get_all_fleets_for_combo(self):
        try:
            return self.session.query(Fleet).order_by(Fleet.nom_flotte).all()
        except Exception as e:
            print(f"Erreur lors de la récupération : {e}")
            return []

    # ==================== MISE À JOUR STATUT ====================

    def get_fleet_full_details(self, fleet_id):
        """
        Récupère une flotte avec toutes ses relations chargées pour les rapports PDF
        
        Args:
            fleet_id: ID de la flotte
        
        Returns:
            Objet Fleet avec toutes les relations chargées
        """
        try:
            from sqlalchemy.orm import joinedload
            
            fleet = self.session.query(Fleet).options(
                joinedload(Fleet.owner),
                joinedload(Fleet.vehicles),
                joinedload(Fleet.compagnie),
                joinedload(Fleet.contract)
            ).filter(Fleet.id == fleet_id).first()
            
            return fleet
        except Exception as e:
            print(f"Erreur get_fleet_full_details: {e}")
            return None
    
    def update_status(self, fleet_id, is_active):
        try:
            fleet = self.session.query(Fleet).get(fleet_id)
            if fleet:
                fleet.is_active = is_active
                fleet.updated_by = self.current_user_id
                self.session.commit()
                return True
        except Exception as e:
            print(f"Erreur status: {e}")
            self.session.rollback()
            return False

    # ==================== GÉNÉRATION PDF ====================
    
    def generate_fleet_pdf(self, fleet_id, output_path):
        """
        Génère un rapport PDF professionnel pour une flotte
        """
        try:
            from datetime import datetime
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, KeepTogether
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import cm, mm
            from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
            import os
            
            # Récupération des données
            fleet = self.get_fleet_full_details(fleet_id)
            if not fleet:
                return False, "Flotte introuvable en base de données."
            
            fleet_contract = self.get_fleet_contract(fleet_id)
            
            # Configuration du document - Marges plus élégantes
            doc = SimpleDocTemplate(
                output_path, 
                pagesize=landscape(A4), 
                rightMargin=1.8*cm, 
                leftMargin=1.8*cm, 
                topMargin=2*cm, 
                bottomMargin=1.8*cm,
                title=f"Rapport_Flotte_{fleet.code_flotte}",
                author="AMS Assurance"
            )
            elements = []
            styles = getSampleStyleSheet()
            
            # ==================== PALETTE DE COULEURS PROFESSIONNELLE ====================
            # Palette sobre et élégante (bleu marine, gris, touches de bleu clair)
            colors_dict = {
                'primary': colors.HexColor('#1a365d'),      # Bleu marine profond
                'secondary': colors.HexColor('#2d3748'),    # Gris anthracite
                'accent': colors.HexColor('#3182ce'),       # Bleu professionnel
                'accent_light': colors.HexColor('#ebf8ff'), # Bleu très clair
                'success': colors.HexColor('#276749'),      # Vert foncé
                'danger': colors.HexColor('#9b2c2c'),       # Bordeaux
                'warning': colors.HexColor('#dd6b20'),      # Orange doux
                'light': colors.HexColor('#f7fafc'),        # Gris très clair
                'light_gray': colors.HexColor('#edf2f7'),   # Gris clair
                'border': colors.HexColor('#e2e8f0'),       # Gris bordure
                'text': colors.HexColor('#2d3748'),         # Texte principal
                'text_light': colors.HexColor('#718096'),   # Texte secondaire
                'white': colors.white,
                'black': colors.black,
            }
            
            # ==================== STYLES TYPOGRAPHIQUES ====================
            styles.add(ParagraphStyle(
                name='TitleStyle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=24,
                textColor=colors_dict['primary'],
                alignment=TA_CENTER,
                spaceAfter=8,
                leading=28
            ))
            
            styles.add(ParagraphStyle(
                name='SubtitleStyle',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=11,
                textColor=colors_dict['text_light'],
                alignment=TA_CENTER,
                spaceAfter=25,
                leading=14
            ))
            
            styles.add(ParagraphStyle(
                name='SectionHeaderStyle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=13,
                textColor=colors_dict['primary'],
                spaceAfter=10,
                spaceBefore=20,
                leading=16,
                borderPadding=5
            ))
            
            styles.add(ParagraphStyle(
                name='SectionHeaderWithLine',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=13,
                textColor=colors_dict['primary'],
                spaceAfter=12,
                spaceBefore=20,
                leading=16
            ))
            
            styles.add(ParagraphStyle(
                name='InfoLabelStyle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=9,
                textColor=colors_dict['secondary'],
                leading=12
            ))
            
            styles.add(ParagraphStyle(
                name='InfoValueStyle',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=9,
                textColor=colors_dict['text'],
                leading=12
            ))
            
            styles.add(ParagraphStyle(
                name='TableHeaderStyle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=8.5,
                textColor=colors_dict['white'],
                alignment=TA_CENTER,
                leading=11
            ))
            
            styles.add(ParagraphStyle(
                name='TableCellStyle',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=8,
                textColor=colors_dict['text'],
                leading=10
            ))
            
            styles.add(ParagraphStyle(
                name='TableCellBoldStyle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=8,
                textColor=colors_dict['secondary'],
                leading=10
            ))
            
            styles.add(ParagraphStyle(
                name='FooterStyle',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=8,
                textColor=colors_dict['text_light'],
                alignment=TA_CENTER,
                leading=10
            ))
            
            # ==================== 1. EN-TÊTE ÉLÉGANT ====================
            logo_path = "addons/Automobiles/static/logo.png"
            
            # En-tête avec fond gris très clair
            header_bg = Table([['']], colWidths=[37*cm], rowHeights=[0.2*cm])
            header_bg.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors_dict['light'])]))
            elements.append(header_bg)
            
            # Logo et infos
            if os.path.exists(logo_path):
                try:
                    logo = Image(logo_path, width=2.2*cm, height=2.2*cm)
                except:
                    logo = None
            else:
                logo = None
            
            if logo:
                header_data = [
                    [logo, 
                    Paragraph("<b>AMS ASSURANCE</b><br/><font size=8>Assurance de confiance depuis 2020</font>", styles['InfoValueStyle']),
                    Paragraph(f"<b>Document</b><br/>Rapport de flotte", styles['InfoValueStyle']),
                    Paragraph(f"<b>Date</b><br/>{datetime.now().strftime('%d/%m/%Y')}", styles['InfoValueStyle'])]
                ]
                header_table = Table(header_data, colWidths=[2.5*cm, 8*cm, 5*cm, 5*cm])
            else:
                header_data = [
                    [Paragraph("<b>AMS ASSURANCE</b><br/><font size=8>Assurance de confiance depuis 2020</font>", styles['InfoValueStyle']),
                    Paragraph(f"<b>Document</b><br/>Rapport de flotte", styles['InfoValueStyle']),
                    Paragraph(f"<b>Date</b><br/>{datetime.now().strftime('%d/%m/%Y')}", styles['InfoValueStyle'])]
                ]
                header_table = Table(header_data, colWidths=[10*cm, 6*cm, 6*cm])
            
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('ALIGN', (-2, 0), (-1, 0), 'RIGHT'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(header_table)
            elements.append(Spacer(1, 0.2*cm))
            
            # Séparateur fin
            sep_line = Table([['']], colWidths=[37*cm], rowHeights=[0.03*cm])
            sep_line.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors_dict['accent'])]))
            elements.append(sep_line)
            elements.append(Spacer(1, 0.5*cm))
            
            # ==================== 2. TITRE PRINCIPAL ====================
            elements.append(Paragraph(f"RAPPORT DE FLOTTE", styles['TitleStyle']))
            elements.append(Paragraph(f"{fleet.nom_flotte.upper()} - {fleet.code_flotte}", styles['SubtitleStyle']))
            elements.append(Spacer(1, 0.3*cm))
            
            # ==================== 3. CARTE D'IDENTITÉ DE LA FLOTTE ====================
            # Utilisation d'un tableau avec fond coloré pour la carte
            card_bg = Table([['']], colWidths=[37*cm], rowHeights=[0.3*cm])
            card_bg.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors_dict['accent_light'])]))
            elements.append(card_bg)
            
            elements.append(Paragraph("INFORMATIONS GÉNÉRALES", styles['SectionHeaderStyle']))
            
            # Grille d'informations - 2 colonnes
            fleet_info_data = [
                ["Nom de la flotte", fleet.nom_flotte or 'N/A', "Code flotte", fleet.code_flotte or 'N/A'],
                ["Statut", fleet.statut or 'Actif', "Type de gestion", fleet.type_gestion or 'N/A'],
                ["Remise commerciale", f"{fleet.remise_flotte or 0}%", "Véhicules", str(len(fleet.vehicles) if fleet.vehicles else 0)],
                ["Date début", fleet.date_debut.strftime('%d/%m/%Y') if fleet.date_debut else 'N/A', "Date fin", fleet.date_fin.strftime('%d/%m/%Y') if fleet.date_fin else 'N/A'],
                ["Assureur", fleet.compagnie.nom if fleet.compagnie else 'N/A', "Période", f"{fleet.date_debut.strftime('%d/%m/%Y') if fleet.date_debut else 'N/A'} - {fleet.date_fin.strftime('%d/%m/%Y') if fleet.date_fin else 'N/A'}"],
            ]
            
            fleet_info_table = Table(fleet_info_data, colWidths=[5*cm, 8*cm, 5*cm, 8*cm])
            fleet_info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors_dict['light']),
                ('BACKGROUND', (2, 0), (2, -1), colors_dict['light']),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.3, colors_dict['border']),
            ]))
            elements.append(fleet_info_table)
            elements.append(Spacer(1, 0.5*cm))
            
            # ==================== 4. PROPRIÉTAIRE ====================
            elements.append(Paragraph("PROPRIÉTAIRE", styles['SectionHeaderStyle']))
            
            owner = fleet.owner
            if owner:
                owner_info_data = [
                    ["Nom complet", f"{owner.nom or ''} {owner.prenom or ''}".strip() or 'N/A', "Nature", owner.nature or 'N/A'],
                    ["Téléphone", owner.telephone or 'N/A', "Email", owner.email or 'N/A'],
                    ["Adresse", owner.adresse or 'N/A', "Code client", owner.code_client or 'N/A'],
                    ["Chargé clientèle", owner.charge_clientele or 'N/A', "Catégorie", owner.cat_socio_prof or 'N/A'],
                ]
            else:
                owner_info_data = [["Propriétaire", "Non renseigné", "", ""]]
            
            owner_info_table = Table(owner_info_data, colWidths=[5*cm, 8*cm, 5*cm, 8*cm])
            owner_info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors_dict['light']),
                ('BACKGROUND', (2, 0), (2, -1), colors_dict['light']),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.3, colors_dict['border']),
            ]))
            elements.append(owner_info_table)
            elements.append(Spacer(1, 0.5*cm))
            
            # ==================== 5. CONTRAT ====================
            elements.append(Paragraph("CONTRAT", styles['SectionHeaderStyle']))
            
            if fleet_contract:
                montant_total = float(fleet_contract.prime_totale_ttc or 0)
                montant_paye = float(fleet_contract.montant_paye or 0)
                solde = montant_total - montant_paye
                pourcentage = int((montant_paye / montant_total) * 100) if montant_total > 0 else 0
                
                contract_info_data = [
                    ["Numéro de police", fleet_contract.numero_police or 'N/A', "Statut", fleet_contract.statut.value if hasattr(fleet_contract.statut, 'value') else str(fleet_contract.statut)],
                    ["Prime totale", f"{montant_total:,.0f} FCFA".replace(",", " "), "Montant payé", f"{montant_paye:,.0f} FCFA".replace(",", " ")],
                    ["Solde restant", f"{solde:,.0f} FCFA".replace(",", " "), "Statut paiement", fleet_contract.statut_paiement or 'NON_PAYE'],
                ]
                
                contract_table = Table(contract_info_data, colWidths=[5*cm, 8*cm, 5*cm, 8*cm])
                contract_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors_dict['light']),
                    ('BACKGROUND', (2, 0), (2, -1), colors_dict['light']),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.3, colors_dict['border']),
                ]))
                elements.append(contract_table)
                
                # Barre de progression élégante
                if montant_total > 0:
                    progress_width = 30 * cm
                    filled_width = progress_width * (pourcentage / 100)
                    
                    progress_bg = Table([['']], colWidths=[progress_width], rowHeights=[0.4*cm])
                    progress_bg.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors_dict['light_gray'])]))
                    
                    progress_fill = Table([['']], colWidths=[filled_width], rowHeights=[0.4*cm])
                    progress_fill.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors_dict['accent'])]))
                    
                    progress_data = [
                        [Paragraph(f"{pourcentage}% payé", styles['InfoLabelStyle']), ""],
                        [progress_bg, ""],
                    ]
                    progress_table = Table(progress_data, colWidths=[progress_width, 0])
                    elements.append(Spacer(1, 0.2*cm))
                    elements.append(progress_table)
            else:
                no_contract = Paragraph("Aucun contrat n'a encore été généré pour cette flotte.", styles['InfoValueStyle'])
                elements.append(no_contract)
            
            elements.append(Spacer(1, 0.5*cm))
            
            # ==================== 6. LISTE DES VÉHICULES ====================
            elements.append(Paragraph("VÉHICULES", styles['SectionHeaderStyle']))
            
            vehicle_list_data = [["N°", "Immatriculation", "Marque", "Modèle", "Année", "Énergie", "Statut"]]
            
            if fleet.vehicles:
                for idx, vehicle in enumerate(fleet.vehicles, 1):
                    vehicle_list_data.append([
                        str(idx),
                        vehicle.immatriculation or 'N/A',
                        vehicle.marque or 'N/A',
                        vehicle.modele or 'N/A',
                        str(vehicle.annee) if vehicle.annee else 'N/A',
                        vehicle.energie or 'N/A',
                        vehicle.statut or 'En circulation',
                    ])
            
            vehicle_list_table = Table(vehicle_list_data, colWidths=[0.8*cm, 3.5*cm, 3.5*cm, 4*cm, 2.2*cm, 2.8*cm, 3.5*cm])
            vehicle_list_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BACKGROUND', (0, 0), (-1, 0), colors_dict['primary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors_dict['white']),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors_dict['white'], colors_dict['light']]),
                ('GRID', (0, 0), (-1, -1), 0.3, colors_dict['border']),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(vehicle_list_table)
            elements.append(Spacer(1, 0.6*cm))
            
            # ==================== 7. TABLEAU DES GARANTIES ====================
            elements.append(Paragraph("GARANTIES PAR VÉHICULE", styles['SectionHeaderStyle']))
            
            # En-têtes professionnels
            garanties_headers = [
                "N°", "Immatriculation",
                "RC", "DR", "Vol", "VB",
                "Incendie", "Bris", "AR", "DTA", "IPT",
                "TOTAL"
            ]
            
            garanties_data = [garanties_headers]
            
            def fmt(val):
                return f"{val:,.0f}".replace(",", " ") if val > 0 else "-"
            
            totals = {
                'rc': 0, 'dr': 0, 'vol': 0, 'vb': 0,
                'in': 0, 'bris': 0, 'ar': 0, 'dta': 0, 'ipt': 0,
                'total': 0
            }
            
            if fleet.vehicles:
                for idx, vehicle in enumerate(fleet.vehicles, 1):
                    pttc = vehicle.total_fleet_amount
                    
                    garanties_data.append([
                        str(idx),
                        vehicle.immatriculation or 'N/A',
                        fmt(vehicle.amt_fleet_rc_val or 0),
                        fmt(vehicle.amt_fleet_dr_val or 0),
                        fmt(vehicle.amt_fleet_vol_val or 0),
                        fmt(vehicle.amt_fleet_vb_val or 0),
                        fmt(vehicle.amt_fleet_in_val or 0),
                        fmt(vehicle.amt_fleet_bris_val or 0),
                        fmt(vehicle.amt_fleet_ar_val or 0),
                        fmt(vehicle.amt_fleet_dta_val or 0),
                        fmt(vehicle.amt_fleet_ipt_val or 0),
                        fmt(pttc),
                    ])
                    
                    totals['rc'] += vehicle.amt_fleet_rc_val or 0
                    totals['dr'] += vehicle.amt_fleet_dr_val or 0
                    totals['vol'] += vehicle.amt_fleet_vol_val or 0
                    totals['vb'] += vehicle.amt_fleet_vb_val or 0
                    totals['in'] += vehicle.amt_fleet_in_val or 0
                    totals['bris'] += vehicle.amt_fleet_bris_val or 0
                    totals['ar'] += vehicle.amt_fleet_ar_val or 0
                    totals['dta'] += vehicle.amt_fleet_dta_val or 0
                    totals['ipt'] += vehicle.amt_fleet_ipt_val or 0
                    totals['total'] += pttc
            
            # Ligne de total
            garanties_data.append([
                "", "", 
                fmt(totals['rc']),
                fmt(totals['dr']),
                fmt(totals['vol']),
                fmt(totals['vb']),
                fmt(totals['in']),
                fmt(totals['bris']),
                fmt(totals['ar']),
                fmt(totals['dta']),
                fmt(totals['ipt']),
                fmt(totals['total']),
            ])
            
            col_widths = [
                0.7*cm, 3.2*cm,
                2.2*cm, 2.2*cm, 2.2*cm, 2.2*cm,
                2.2*cm, 2.2*cm, 2.2*cm, 2.2*cm, 2.2*cm,
                2.5*cm
            ]
            
            garanties_table = Table(garanties_data, colWidths=col_widths, repeatRows=1)
            garanties_table.setStyle(TableStyle([
                # En-tête
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 0), (-1, 0), colors_dict['primary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors_dict['white']),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # Alignement
                ('ALIGN', (0, 1), (1, -2), 'LEFT'),
                ('ALIGN', (2, 1), (-1, -2), 'RIGHT'),
                ('ALIGN', (0, -1), (1, -1), 'CENTER'),
                ('ALIGN', (2, -1), (-1, -1), 'RIGHT'),
                
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (0, 1), (-1, -2), 7.5),
                ('FONTSIZE', (0, -1), (-1, -1), 8),
                
                # Alternance des couleurs
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors_dict['white'], colors_dict['light']]),
                
                # Ligne de total
                ('BACKGROUND', (0, -1), (-1, -1), colors_dict['light_gray']),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors_dict['primary']),
                ('SPAN', (0, -1), (1, -1)),
                
                # Bordures
                ('GRID', (0, 0), (-1, -1), 0.3, colors_dict['border']),
                ('BOX', (0, 0), (-1, -1), 0.5, colors_dict['primary']),
                
                # Padding
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(garanties_table)
            elements.append(Spacer(1, 0.6*cm))
            
            # ==================== 8. RÉSUMÉ STATISTIQUE ====================
            elements.append(Paragraph("SYNTHÈSE", styles['SectionHeaderStyle']))
            
            nb_vehicules = len(fleet.vehicles) if fleet.vehicles else 0
            prime_moyenne = (totals['total'] / nb_vehicules) if nb_vehicules > 0 else 0
            
            # Deux colonnes pour le résumé
            summary_left = [
                ["Indicateur", "Valeur"],
                ["Nombre de véhicules", f"{nb_vehicules}"],
                ["Total des garanties", fmt(totals['total'])],
            ]
            
            summary_right = [
                ["Indicateur", "Valeur"],
                ["Prime moyenne", fmt(prime_moyenne)],
                ["Couverture moyenne", f"{self._calculate_fleet_coverage_rate(fleet):.0f}%"],
            ]
            
            summary_left_table = Table(summary_left, colWidths=[8*cm, 8*cm])
            summary_left_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors_dict['accent_light']),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('GRID', (0, 0), (-1, -1), 0.3, colors_dict['border']),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            summary_right_table = Table(summary_right, colWidths=[8*cm, 8*cm])
            summary_right_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors_dict['accent_light']),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('GRID', (0, 0), (-1, -1), 0.3, colors_dict['border']),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            summary_row = Table([[summary_left_table, summary_right_table]], colWidths=[18*cm, 18*cm])
            summary_row.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            elements.append(summary_row)
            
            # ==================== 9. OBSERVATIONS ====================
            if fleet.observations:
                elements.append(Spacer(1, 0.5*cm))
                elements.append(Paragraph("OBSERVATIONS", styles['SectionHeaderStyle']))
                obs_text = Paragraph(fleet.observations, styles['InfoValueStyle'])
                elements.append(obs_text)
            
            # ==================== 10. PIED DE PAGE ====================
            elements.append(Spacer(1, 1.5*cm))
            
            # Ligne fine
            footer_line = Table([['']], colWidths=[37*cm], rowHeights=[0.03*cm])
            footer_line.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors_dict['border'])]))
            elements.append(footer_line)
            elements.append(Spacer(1, 0.2*cm))
            
            footer_data = [
                ["AMS Assurance - Rapport généré automatiquement", f"Page 1/1", f"Fait à Douala, le {datetime.now().strftime('%d/%m/%Y')}"],
            ]
            footer_table = Table(footer_data, colWidths=[15*cm, 10*cm, 12*cm])
            footer_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors_dict['text_light']),
            ]))
            elements.append(footer_table)
            
            # Génération du PDF
            doc.build(elements)
            
            return True, f"PDF généré avec succès : {output_path}"
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"❌ Erreur critique lors de la génération PDF : {e}\nDetails:\n{error_details}")
            return False, f"Erreur technique : {str(e)}"

    def _format_currency(self, value):
        """Formate un montant en FCFA avec séparateurs"""
        return f"{value:,.0f}".replace(",", " ") if value > 0 else "0"


    def _calculate_fleet_coverage_rate(self, fleet):
        """Calcule le taux de couverture moyen de la flotte"""
        if not fleet.vehicles:
            return 0
        
        garanties_list = ['amt_rc', 'amt_dr', 'amt_vol', 'amt_vb', 'amt_in', 'amt_bris', 'amt_ar', 'amt_dta', 'amt_ipt']
        total_coverage = 0
        
        for vehicle in fleet.vehicles:
            coverage = 0
            for g in garanties_list:
                value = getattr(vehicle, g, 0)
                if value and float(value) > 0:
                    coverage += 1
            total_coverage += (coverage / len(garanties_list)) * 100
        
        return int(total_coverage / len(fleet.vehicles)) if fleet.vehicles else 0
    # ==================== UTILITAIRES ====================
    
    # flotte_controller.py - Ajoutez cette méthode

    def _log_action(self, action, fleet_id, contrat_id, user_id, local_ip, public_ip, old_values=None, new_values=None):
        """
        Enregistre une action dans les logs d'audit pour les flottes
        
        Args:
            action: Type d'action (CREATE_FLEET_CONTRACT, UPDATE_FLEET_CONTRACT, etc.)
            fleet_id: ID de la flotte concernée
            contrat_id: ID du contrat associé
            user_id: ID de l'utilisateur
            local_ip: IP locale
            public_ip: IP publique
            old_values: Anciennes valeurs (optionnel)
            new_values: Nouvelles valeurs (optionnel)
        """
        try:
            from addons.Automobiles.models.automobile_models import AuditVehicleLog
            from datetime import datetime
            import json
            
            audit = AuditVehicleLog(
                user_id=user_id,
                action=action,
                module="FLEET_MANAGEMENT",
                item_id=fleet_id,
                old_values=json.dumps(old_values, default=str) if old_values else None,
                new_values=json.dumps({
                    'action': action,
                    'fleet_id': fleet_id,
                    'contrat_id': contrat_id,
                    'details': new_values or {}
                }, default=str),
                ip_local=local_ip,
                ip_public=public_ip,
                timestamp=datetime.now()
            )
            
            self.session.add(audit)
            self.session.commit()
            
        except Exception as e:
            print(f"Erreur _log_action: {e}")
            # On ne fait pas de rollback ici pour ne pas affecter l'action principale
    def get_network_info(self):
        """Récupère simultanément l'IP Locale et l'IP Publique."""
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
        except:
            local_ip = "127.0.0.1"

        try:
            response = requests.get('https://api.ipify.org?format=json', timeout=1.5)
            public_ip = response.json().get('ip')
        except:
            public_ip = "Offline"

        return local_ip, public_ip