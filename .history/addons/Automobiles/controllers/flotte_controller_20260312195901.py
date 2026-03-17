from socket import socket

import requests
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from addons.Automobiles.models.models import AuditFlotteLog, Vehicle, Fleet
from addons.Automobiles.models.models import Contact
from addons.Automobiles.models.models import Vehicle, Fleet, AuditVehicleLog
from addons.Automobiles.controller.vehicle_controller import VehicleController
from datetime import date, datetime, timezone
import json

class FleetController:
    def __init__(self, session: Session, current_user_id):
        self.session = session
        self.current_user_id = current_user_id

        self.vehicle_service = VehicleController(session)

    def create_fleet(self, data, user_id):
        try:
            local_ip, public_ip = self.get_network_info()

            data['created_by'] = user_id
            data['created_ip'] = public_ip
            data['last_ip'] = local_ip # On peut stocker la locale ici pour savoir quel PC a touché en dernier
            # On utilise les clés du dictionnaire 'data' pour remplir le modèle 'Fleet'
            new_fleet = Fleet(
                nom_flotte=data.get('nom_flotte'), # <-- CORRECTION ICI
                code_flotte=data.get('code_flotte'),
                owner_id=data.get('owner_id'),
                assureur=data.get('assureur'),
                type_gestion=data.get('type_gestion'),
                remise_flotte=data.get('remise_flotte'),
                statut=data.get('statut'),
                is_active=data.get('is_active'),
                date_debut=data.get('date_debut'),
                date_fin=data.get('date_fin'),
                observations=data.get('observations')
            )
            self.session.add(new_fleet)
            self.session.flush()

            serializable_data = data.copy()
            for key, value in serializable_data.items():
                if isinstance(value, (date, datetime)):
                    serializable_data[key] = value.isoformat() # Transforme en "2023-10-27"
            # LOG D'AUDIT POUR LA TRAÇABILITÉ
            log = AuditFlotteLog(
                user_id=user_id,
                action="CREATION",
                module="VEHICULE_MANAGEMENT", # Nom de votre module pour le filtrage
                item_id=new_fleet.id,
                old_values=None,
                new_values=json.dumps(serializable_data), # On transforme le dictionnaire en texte
                ip_local=local_ip,   # Doit correspondre au nom dans models.py
                ip_public=public_ip, # Doit correspondre au nom dans models.py
                # timestamp est géré par défaut par la base de données (server_default)
            )
            self.session.add(log)
            
            self.session.commit()
            return True, new_fleet.id
        except Exception as e:
            self.session.rollback()
            return False, str(e)

    def get_fleet_stats(self, fleet_id):
        """Récupère les indicateurs clés (KPI) pour le tableau de bord d'une flotte."""
        # Nombre de véhicules, somme des primes, etc.
        stats = self.session.query(
            func.count(Vehicle.id).label("total"),
            func.sum(Vehicle.prime_emise).label("prime_totale")
        ).filter(Vehicle.fleet_id == fleet_id).first()
        
        return {
            "total_vehicules": stats.total or 0,
            "prime_globale": stats.prime_totale or 0,
            # Vous pourrez ajouter ici le calcul des véhicules expirés
        }

    # --- GESTION DES VÉHICULES ---

    def add_vehicle_to_fleet(self, data):
        """Enregistre un véhicule avec ses données techniques et garanties."""
        try:
            # Conversion des données de garanties (dict) en colonnes si nécessaire
            new_vehicle = Vehicle(
                immatriculation=data['immatriculation'],
                fleet_id=data['fleet_id'],
                owner_id=data['owner_id'],
                marque=data['marque'],
                genre=data['genre'],
                poids=data['poids'],
                puissance=data['puissance'],
                val_neuf=data['val_neuf'],
                val_venale=data['val_venale'],
                prime_emise=data['prime_emise'],
                # Stockage des garanties (en colonnes booléennes ou JSON selon votre choix de modèle)
                rc=data['garanties']['rc'],
                tc=data['garanties']['tc'],
                vol=data['garanties']['vol'],
                bris=data['garanties']['bris'],
                dommages=data['garanties']['dommages'],
                individuelle=data['garanties']['individuelle'],
                dr=data['garanties']['dr']
            )
            self.session.add(new_vehicle)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            return False, str(e)

    # --- RÉCUPÉRATION DES DONNÉES POUR LES COMBOS ---

    def get_all_fleets_for_combo(self):
        try:
            return self.session.query(Fleet).order_by(Fleet.nom_flotte).all()
        except Exception as e:
            print(f"Erreur lors de la récupération : {e}")
            return []

    def get_all_contacts_for_combo(self):
        """Retourne les contacts de nature physique depuis la table Contact."""
        try:
            # On récupère spécifiquement les colonnes ID et NOM
            compagnies = self.session.query(Contact.id, Contact.nom)\
                .filter(Contact.nature == "Physique")\
                .all()
            
            # Debug : affiche la liste brute pour vérification
            print(f"DEBUG Contacts : {compagnies}")
            
            # Correction de la compréhension de liste :
            # Puisque ce sont des tuples (id, nom), on les dépaquette directement
            return [(contact_id, contact_nom) for contact_id, contact_nom in compagnies]

        except Exception as e:
            print(f"Erreur lors de la récupération des contacts : {e}")
            return []

    def get_all_compagnies_for_combo(self):
        """Retourne les contacts de nature physique depuis la table Contact."""
        try:
            # On récupère spécifiquement les colonnes ID et NOM
            compagnies = self.session.query(Contact.id, Contact.nom)\
                .filter(Contact.nature == "Morale")\
                .all()
            
            # Debug : affiche la liste brute pour vérification
            print(f"DEBUG Contacts : {compagnies}")
            
            # Correction de la compréhension de liste :
            # Puisque ce sont des tuples (id, nom), on les dépaquette directement
            return [(contact_id, contact_nom) for contact_id, contact_nom in compagnies]

        except Exception as e:
            print(f"Erreur lors de la récupération des contacts : {e}")
            return []
    
    # --- DANS controllers/fleet_controller.py ---
    def get_all_fleets(self):
        try:
            # On utilise joinedload pour récupérer le nom du propriétaire en une seule fois
            from sqlalchemy.orm import joinedload
            return self.session.query(Fleet).options(joinedload(Fleet.owner)).all()
        except Exception as e:
            print(f"Erreur lors de la récupération des flottes : {e}")
            return []
        
    def update_status(self, fleet_id, is_active):
        try:
            fleet = self.session.query(Fleet).get(fleet_id)
            if fleet:
                fleet.is_active = is_active
                # On met aussi à jour le updated_by
                fleet.updated_by = self.current_user_id
                self.session.commit()
                return True
        except Exception as e:
            print(f"Erreur status: {e}")
            self.session.rollback()
            return False

    def update_fleet_vehicles(self, fleet_id, selected_vehicle_ids, user_id, ip_local=None, ip_public=None):
        try:
            # --- 1. Logique métier : Mise à jour des véhicules ---
            # On détache ceux qui ne sont plus sélectionnés
            self.session.query(Vehicle).filter(
                Vehicle.fleet_id == fleet_id,
                ~Vehicle.id.in_(selected_vehicle_ids)
            ).update({Vehicle.fleet_id: None}, synchronize_session=False)

            # On attache les nouveaux sélectionnés
            if selected_vehicle_ids:
                self.session.query(Vehicle).filter(
                    Vehicle.id.in_(selected_vehicle_ids)
                ).update({Vehicle.fleet_id: fleet_id}, synchronize_session=False)

            # --- 2. LOG D'AUDIT (C'est ici que vous insérez le code) ---
            audit = AuditFlotteLog(
                user_id=user_id,
                action="UPDATE_RELATION",
                module="FLEETS",
                item_id=fleet_id,
                new_values=json.dumps({"vehicle_ids": selected_vehicle_ids}), # Liste des IDs sélectionnés
                ip_local=ip_local,
                ip_public=ip_public,
                timestamp=datetime.now(timezone.utc)
            )
            self.session.add(audit)

            # --- 3. Validation finale ---
            self.session.commit()
            return True, "Relation Flotte-Véhicules mise à jour."

        except Exception as e:
            self.session.rollback()
            print(f"Erreur Update Fleet Relation: {e}")
            return False, str(e)

    def get_all_vehicles(self):
        # On délègue le travail au service véhicule
        return self.vehicle_service.get_all_vehicles()

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

