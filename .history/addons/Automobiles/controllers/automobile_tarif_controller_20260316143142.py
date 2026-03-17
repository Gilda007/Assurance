import socket
import requests
import logging
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from addons.Automobiles.models.compagnies_models import Compagnie  # Assurez-vous du chemin d'import

class CompagnieController:
    def __init__(self, session: Session, current_user_id):
        self.session = session
        self.current_user_id = current_user_id

    def _get_network_info(self):
        """Récupère les adresses IP locale et publique pour la traçabilité."""
        local_ip = "127.0.0.1"
        network_ip = "127.0.0.1"
        try:
            # IP Locale
            local_ip = socket.gethostbyname(socket.gethostname())
            # IP Publique (via un service externe avec timeout court)
            network_ip = requests.get('https://api.ipify.org', timeout=1).text
        except Exception:
            network_ip = local_ip  # Repli sur l'IP locale en cas d'échec
        return local_ip, network_ip

    def create_compagnie(self, data, user_login):
        """
        Crée une nouvelle compagnie avec traçabilité complète.
        :param data: dictionnaire issu du formulaire (nom, code, email, etc.)
        :param user_login: le login de l'utilisateur connecté
        """
        try:
            local_ip, network_ip = self._get_network_info()
            
            nouvelle_cie = Compagnie(
                code=data.get('code').upper(),
                nom=data.get('nom').upper(),
                email=data.get('email'),
                telephone=data.get('telephone'),
                adresse=data.get('adresse'),
                
                # Traçabilité
                create_by=user_login,
                modify_by=user_login,
                created_at=datetime.now(),
                modify_at=datetime.now(),
                local_ip=local_ip,
                network_ip=network_ip
            )

            self.db.add(nouvelle_cie)
            self.db.commit()
            return True, nouvelle_cie
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Erreur DB lors de la création compagnie: {str(e)}")
            return False, str(e)

    def update_compagnie(self, compagnie_id, data, user_login):
        """Met à jour une compagnie existante et trace la modification."""
        try:
            cie = self.db.query(Compagnie).filter(Compagnie.id == compagnie_id).first()
            if not cie:
                return False, "Compagnie introuvable"

            local_ip, network_ip = self._get_network_info()

            # Mise à jour des champs
            cie.nom = data.get('nom', cie.nom).upper()
            cie.email = data.get('email', cie.email)
            cie.telephone = data.get('telephone', cie.telephone)
            cie.adresse = data.get('adresse', cie.adresse)
            
            # Traçabilité de modification
            cie.modify_by = user_login
            cie.modify_at = datetime.now()
            cie.local_ip = local_ip
            cie.network_ip = network_ip

            self.db.commit()
            return True, cie
        except SQLAlchemyError as e:
            self.db.rollback()
            return False, str(e)

    def delete_compagnie(self, compagnie_id, user_login):
        """
        Désactive une compagnie au lieu de la supprimer physiquement (Soft Delete).
        Met à jour la traçabilité de modification.
        """
        try:
            # 1. Récupérer la compagnie
            cie = self.db.query(Compagnie).filter(Compagnie.id == compagnie_id).first()
            
            if not cie:
                return False, "Compagnie introuvable"

            # 2. Récupérer les infos réseau
            local_ip, network_ip = self._get_network_info()

            # 3. Appliquer le Soft Delete
            cie.is_active = False # Désactivation
            
            # 4. Tracer qui a effectué cette désactivation
            cie.modify_by = user_login
            cie.modify_at = datetime.now()
            cie.local_ip = local_ip
            cie.network_ip = network_ip

            self.db.commit()
            self.logger.info(f"Compagnie ID {compagnie_id} désactivée par {user_login}")
            return True, "La compagnie a été archivée avec succès."
        
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Erreur lors de la désactivation : {str(e)}")
            return False, str(e)

    def get_archived_compagnies(self):
        """Récupère la liste des compagnies supprimées logiquement."""
        return self.db.query(Compagnie).filter(Compagnie.is_active == False).all()

    def restore_compagnie(self, compagnie_id, user_login):
        """Permet de restaurer une compagnie précédemment désactivée."""
        try:
            cie = self.db.query(Compagnie).filter(Compagnie.id == compagnie_id).first()
            if cie:
                cie.is_active = True
                cie.modify_by = user_login
                cie.modify_at = datetime.now()
                self.db.commit()
                return True
            return False
        except SQLAlchemyError:
            self.db.rollback()
            return False