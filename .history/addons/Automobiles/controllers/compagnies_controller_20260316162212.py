import socket
import requests
import logging
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from addons.Automobiles.models.compagnies_models import Compagnie  # Assurez-vous que le chemin est correct
import logging

class CompagnieController:
    def __init__(self, db_session, current_user_id):
        self.db = db_session
        # Accepte soit l'ID utilisateur, soit l'objet User.
        # Dans le second cas, on prend simplement l'attribut .id pour éviter
        # d'essayer d'insérer tout l'objet dans la colonne created_by.
        self.current_user_id = getattr(current_user_id, 'id', current_user_id)
        self.logger = logging.getLogger(__name__)

    def _get_audit_data(self, user_login):
        """
        Méthode privée pour capturer les données système (Audit).
        Cette méthode garantit que l'utilisateur ne peut pas falsifier sa trace.
        """
        local_ip = "127.0.0.1"
        network_ip = "127.0.0.1"
        
        try:
            # Récupération de l'IP Locale
            local_ip = socket.gethostbyname(socket.gethostname())
            # Récupération de l'IP Publique (via API externe avec timeout 1s)
            network_ip = requests.get('https://api.ipify.org', timeout=1).text
        except Exception:
            # En cas d'échec (pas d'internet), on utilise l'IP locale
            network_ip = local_ip

        return {
            "user": user_login,
            "local_ip": local_ip,
            "network_ip": network_ip,
            "now": datetime.now()
        }

    def create_compagnie(self, data, user_id):
        """
        :param data: dict venant de get_data()
        :param user_id: int (ID de l'utilisateur connecté)
        """
        print(user_id)
        try:
            # Récupération des IPs
            local_ip = socket.gethostbyname(socket.gethostname())
            try:
                net_ip = requests.get('https://api.ipify.org', timeout=1).text
            except:
                net_ip = local_ip

            nouvelle_cie = Compagnie(
                **data,  # Injecte nom, code, email, telephone, adresse, num_debut, num_fin
                create_by=user_id,
                modify_by=user_id,
                local_ip=local_ip,
                network_ip=net_ip,
                created_at=datetime.now(),
                modify_at=datetime.now(),
                is_active=True
            )
            
            self.db.add(nouvelle_cie)
            self.db.commit()
            return True, "Enregistré"
        except Exception as e:
            self.db.rollback()
            return False, str(e)
        
    def update_compagnie(self, compagnie_id, form_data, user_login):
        """
        Met à jour une compagnie et trace l'auteur de la modification.
        """
        try:
            cie = self.db.query(Compagnie).filter(Compagnie.id == compagnie_id).first()
            if not cie:
                return False, "Compagnie introuvable."

            audit = self._get_audit_data(user_login)

            # Mise à jour des informations
            cie.nom = form_data.get('nom', cie.nom).upper()
            cie.email = form_data.get('email', cie.email)
            cie.telephone = form_data.get('telephone', cie.telephone)
            cie.adresse = form_data.get('adresse', cie.adresse)
            cie.num_debut = form_data.get('num_debut', cie.num_debut)
            cie.num_fin = form_data.get('num_fin', cie.num_fin)

            # Mise à jour de l'audit de modification
            cie.modify_by = audit['user']
            cie.modify_at = audit['now']
            cie.local_ip = audit['local_ip']
            cie.network_ip = audit['network_ip']

            self.db.commit()
            return True, "Mise à jour effectuée."

        except SQLAlchemyError as e:
            self.db.rollback()
            return False, str(e)

    def delete_compagnie(self, compagnie_id, user_login):
        """
        Suppression logique (is_active = False) avec audit de qui a 'supprimé'.
        """
        try:
            cie = self.db.query(Compagnie).filter(Compagnie.id == compagnie_id).first()
            if not cie:
                return False, "Compagnie introuvable."

            audit = self._get_audit_data(user_login)

            cie.is_active = False
            cie.modify_by = audit['user']
            cie.modify_at = audit['now']
            cie.local_ip = audit['local_ip']
            cie.network_ip = audit['network_ip']

            self.db.commit()
            return True, "Compagnie archivée."
        except SQLAlchemyError as e:
            self.db.rollback()
            return False, str(e)

    def get_active_compagnies(self):
        """Retourne la liste des compagnies non archivées."""
        return self.db.query(Compagnie).filter(Compagnie.is_active == True).order_by(Compagnie.nom).all()
    def get_all_active_compagnies(self):
        try:
            return self.db.query(Compagnie).filter(Compagnie.is_active == True).all()
        except Exception as e:
            print(f"Erreur lors de la récupération : {e}")
            return []

    def delete_compagnie_logic(self, compagnie_id, user_id):
        """Suppression logique (is_active = False)"""
        try:
            compagnie = self.db.query(Compagnie).filter(Compagnie.id == compagnie_id).first()
            if compagnie:
                compagnie.is_active = False
                compagnie.modify_by = user_id
                self.db.commit()
                return True, "Désactivée avec succès"
            return False, "Compagnie introuvable"
        except Exception as e:
            self.db.rollback()
            return False, str(e)
    
    def update_compagnie(self, compagnie_id, form_data, user_id):
        """
        Met à jour une compagnie existante.
        :param compagnie_id: L'ID de la compagnie à modifier.
        :param form_data: Les nouvelles données du formulaire.
        :param user_id: L'ID de l'utilisateur qui fait la modif (Integer).
        """
        try:
            # 1. Récupérer la compagnie en base
            compagnie = self.db.query(Compagnie).filter(Compagnie.id == compagnie_id).first()
            
            if not compagnie:
                return False, "Compagnie introuvable."

            # 2. Capture des nouvelles données d'audit
            audit = self._get_audit_data(user_id)

            # 3. Mise à jour des champs (on peut boucler sur les clés du dict)
            for key, value in form_data.items():
                if hasattr(compagnie, key):
                    # Transformation en majuscule pour code et nom
                    if key in ['code', 'nom'] and value:
                        value = value.upper()
                    setattr(compagnie, key, value)

            # 4. Mise à jour forcée de l'audit de modification
            compagnie.modify_by = user_id
            compagnie.modify_at = audit['now']
            compagnie.local_ip = audit['local_ip']
            compagnie.network_ip = audit['network_ip']

            self.db.commit()
            return True, "Mise à jour réussie."

        except Exception as e:
            self.db.rollback()
            return False, str(e)