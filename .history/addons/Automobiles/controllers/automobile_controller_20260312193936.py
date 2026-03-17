import json
import socket

from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from addons.Automobiles.models.models import Contact
from addons.vehicule_management.models.models import Vehicle, AuditVehicleLog
from datetime import date, datetime
import requests


class VehicleController:
    def __init__(self, session: Session):
        self.session = session

    def get_all_vehicles(self):
        """Récupère uniquement les véhicules actifs."""
        return self.session.query(Vehicle).filter(Vehicle.is_active == True).all()

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
        
    def get_contacts_for_combo(self, text):
        """Récupère les clients/entreprises depuis la table CONTACT."""

        return self.session.query(Contact).filter(
        (Contact.nom.ilike(f"%{text}%")) | 
        (Contact.telephone.ilike(f"%{text}%"))
    ).all()

    def create_vehicle(self, data, user_id, local_ip=None, public_ip=None):
        try:
            # 1. Gestion des infos réseau si manquantes
            if local_ip is None or public_ip is None:
                local_ip, public_ip = self.get_network_info()

            # 2. Préparation du log d'audit (AVANT de modifier 'data')
            # On garde une copie propre pour le JSON
            audit_data = data.copy()
            audit_data['ip_info'] = {'local': local_ip, 'public': public_ip}

            # 3. Nettoyage de 'data' pour SQLAlchemy
            # On ne garde que les clés qui existent réellement dans le modèle Vehicle
            vehicle_columns = Vehicle.__table__.columns.keys()
            filtered_data = {k: v for k, v in data.items() if k in vehicle_columns}

            # 4. Création du véhicule
            new_vehicle = Vehicle(**filtered_data)
            
            # Attribution forcée des champs de traçabilité sur l'objet (si ils existent)
            if hasattr(new_vehicle, 'created_by'):
                new_vehicle.created_by = user_id
            if hasattr(new_vehicle, 'created_ip'):
                new_vehicle.created_ip = public_ip

            self.session.add(new_vehicle)
            self.session.flush() # Récupère new_vehicle.id

            # 5. Remplissage de la table Audit
            # Utilisation de json.dumps avec default=str pour les dates
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
            
            self.session.add(audit)
            self.session.commit()
            return True, new_vehicle.id # Retourner l'ID est plus utile pour la vue

        except Exception as e:
            self.session.rollback()
            import traceback
            print(traceback.format_exc()) # Log console pour le debug
            return False, str(e)

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

    def update_vehicle(self, vehicle_id, new_data, user_id, ip_local=None, ip_public=None):
        try:
            vehicle = self.session.query(Vehicle).get(vehicle_id)
            if not vehicle:
                return False, "Véhicule introuvable."

            # Fonction interne pour transformer les dates en texte pour le JSON
            def date_encoder(obj):
                if isinstance(obj, (datetime, date)):
                    return obj.isoformat()
                raise TypeError(f"Type {type(obj)} non sérialisable")

            # 1. Capturer l'ancien état proprement
            old_values = {
                "immatriculation": vehicle.immatriculation,
                "chassis": vehicle.chassis,
                "date_debut": vehicle.date_debut,
                "date_fin": vehicle.date_fin
            }

            # 2. Appliquer les modifications sur l'objet SQL
            for key, value in new_data.items():
                if hasattr(vehicle, key):
                    setattr(vehicle, key, value)

            vehicle.updated_at = datetime.now()
            vehicle.updated_by = user_id
            vehicle.last_ip = ip_local

            # 3. Audit avec l'argument 'default' pour gérer les dates
            audit = AuditVehicleLog(
                user_id=user_id,
                action="UPDATE",
                module="VEHICLES",
                item_id=vehicle_id,
                # 'default=date_encoder' règle le problème du JSON
                old_values=json.dumps(old_values, default=date_encoder),
                new_values=json.dumps(new_data, default=date_encoder),
                ip_local=ip_local,
                ip_public=ip_public,
                timestamp=datetime.now()
            )

            self.session.add(audit)
            self.session.commit()
            return True, "Mise à jour réussie"
        except Exception as e:
            self.session.rollback()
            # On affiche l'erreur exacte dans la console pour débugger
            print(f"ERREUR DEBUG: {str(e)}")
            return False, str(e)

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
        
    def update_vehicle(self, vehicle_id, new_data, user_id, ip_local=None, ip_public=None):
        vehicle = self.session.query(Vehicle).get(vehicle_id)
        if not vehicle:
            return False, "Véhicule introuvable."
