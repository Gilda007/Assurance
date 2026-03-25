from socket import socket

import requests
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from addons.Automobiles.controllers.automobile_controller import VehicleController
from addons.Automobiles.models.automobile_models import AuditVehicleLog, Vehicle
from addons.Automobiles.models.contact_models import Contact
from addons.Automobiles.models.flottes_models import Fleet
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
            log = AuditVehicleLog(
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

    def get_all_vehicles(self):
        # On délègue le travail au service véhicule
        return self.vehicle_service.get_all_vehicles()

    def update_fleet_relation(self, fleet_id, selected_vehicle_ids, user_id, ip_local=None, ip_public=None):
        """Met à jour les véhicules appartenant à cette flotte."""
        try:
            # SÉCURITÉ : On s'assure que selected_vehicle_ids est une liste d'entiers
            # Si c'est un dictionnaire, on ne traite rien pour éviter le crash SQL
            if isinstance(selected_vehicle_ids, dict):
                print("ERREUR : Le contrôleur a reçu un dictionnaire au lieu d'une liste d'IDs")
                return False, "Données de véhicules invalides"

            # On convertit en liste d'entiers propre
            clean_ids = [int(i) for i in selected_vehicle_ids if str(i).isdigit()]

            # 1. Détacher les véhicules qui étaient dans cette flotte mais ne sont plus sélectionnés
            self.session.query(Vehicle).filter(
                Vehicle.fleet_id == fleet_id,
                ~Vehicle.id.in_(clean_ids)
            ).update({"fleet_id": None}, synchronize_session=False)

            # 2. Attacher les nouveaux véhicules sélectionnés
            if clean_ids:
                self.session.query(Vehicle).filter(
                    Vehicle.id.in_(clean_ids)
                ).update({"fleet_id": fleet_id}, synchronize_session=False)

            audit = AuditVehicleLog(
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

            self.session.commit()
            return True, "Véhicules mis à jour"
        except Exception as e:
            self.session.rollback()
            print(f"Erreur SQL Relation : {e}")
            return False, str(e)
    
    def update_fleet_data(self, fleet_id, data):
        try:

            code_flotte = data.get('code_flotte')
            if isinstance(code_flotte, str):
                code_flotte = code_flotte.strip()
                if not code_flotte:
                    code_flotte = None
            # Nettoyage des données numériques avant envoi à SQL
            remise = data.get('remise_flotte')
            try:
                remise = float(remise) if remise not in [None, ''] else 0.0
            except:
                remise = 0.0

            # Vérification de l'owner_id (doit être un entier ou None)
            owner_id = data.get('owner_id')
            if isinstance(owner_id, str) and not owner_id.isdigit():
                # Si c'est du texte (comme 'dil'), on cherche l'ID correspondant 
                # ou on met None pour éviter le crash
                owner_id = None 

            self.session.query(Fleet).filter(Fleet.id == fleet_id).update({
                "nom_flotte": data.get('nom_flotte'),
                "code_flotte": data.get('code_flotte'),
                "owner_id": owner_id,
                "assureur": data.get('assureur'),
                "type_gestion": data.get('type_gestion'),
                "remise_flotte": remise, # <--- Garanti comme float
                "statut": data.get('statut'),
                "is_active": data.get('is_active'),
                "date_debut": data.get('date_debut'),
                "date_fin": data.get('date_fin'),
                "observations": data.get('observations'),
                "updated_at": datetime.now(timezone.utc)
            }, synchronize_session=False)

            self.session.commit()
            return True, "Succès"
        except Exception as e:
            self.session.rollback()
            # On attrape l'erreur d'unicité pour renvoyer un message clair à l'utilisateur
            if "unique constraint" in str(e).lower():
                return False, f"Le code flotte '{data.get('code_flotte')}' est déjà utilisé par une autre flotte."
            return False, str(e)
    
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
    
    # ... (le reste de votre code actuel est correct pour gérer les IDs) ...
    def update_fleet_vehicles(self, fleet_id, selected_vehicle_ids, user_id):
        """
        Met à jour la relation entre une flotte et ses véhicules.
        """
        try:
            # --- SÉCURITÉ CRUCIALE ---
            # Si selected_vehicle_ids est un dictionnaire (erreur de vue), 
            # on ne fait rien pour éviter le crash SQL "InvalidTextRepresentation"
            if isinstance(selected_vehicle_ids, dict):
                print("ERREUR : Le contrôleur a reçu un dictionnaire au lieu d'une liste d'IDs.")
                return False, "Format de données invalide (attendu: liste d'IDs)."

            # Nettoyage de la liste pour s'assurer qu'on n'a que des entiers
            clean_ids = [int(i) for i in selected_vehicle_ids if str(i).isdigit() or isinstance(i, int)]

            # Récupération des infos réseau pour l'audit
            local_ip, public_ip = self.get_network_info()

            # --- 1. DÉTACHEMENT ---
            # On met à None le fleet_id de tous les véhicules qui pointaient sur cette flotte 
            # mais qui ne sont plus dans la nouvelle sélection.
            self.session.query(Vehicle).filter(
                Vehicle.fleet_id == fleet_id,
                ~Vehicle.id.in_(clean_ids)
            ).update({"fleet_id": None}, synchronize_session=False)

            # --- 2. ATTACHEMENT ---
            # On lie les véhicules de la nouvelle sélection à cette flotte
            if clean_ids:
                self.session.query(Vehicle).filter(
                    Vehicle.id.in_(clean_ids)
                ).update({"fleet_id": fleet_id}, synchronize_session=False)

            # --- 3. LOG D'AUDIT ---
            audit = AuditVehicleLog(
                user_id=user_id,
                action="UPDATE_RELATION_FLEET",
                module="FLEETS",
                item_id=fleet_id,
                # On stocke la liste des IDs sélectionnés pour l'historique
                new_values=json.dumps({"vehicle_ids": clean_ids}), 
                ip_local=local_ip,
                ip_public=public_ip,
                timestamp=datetime.now(timezone.utc)
            )
            self.session.add(audit)

            # --- 4. VALIDATION ---
            self.session.commit()
            return True, "Relation Flotte-Véhicules mise à jour avec succès."

        except Exception as e:
            self.session.rollback()
            print(f"Erreur Update Fleet Relation: {str(e)}")
            return False, f"Erreur base de données : {str(e)}"