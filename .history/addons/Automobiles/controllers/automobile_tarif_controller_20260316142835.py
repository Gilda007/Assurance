import socket
import requests
import logging
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from models.compagnie import Compagnie

class CompagnieController:
    def __init__(self, db_session):
        self.db = db_session
        self.logger = logging.getLogger("AMS_Project")

    def _get_network_info(self):
        """Récupère les informations réseau pour la traçabilité."""
        local_ip = "127.0.0.1"
        network_ip = "127.0.0.1"
        try:
            local_ip = socket.gethostbyname(socket.gethostname())
            network_ip = requests.get('https://api.ipify.org', timeout=1).text
        except Exception:
            network_ip = local_ip
        return local_ip, network_ip

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

    def get_all_compagnies(self):
        """
        Récupère uniquement les compagnies actives pour l'affichage courant.
        """
        return self.db.query(Compagnie).filter(Compagnie.is_active == True).order_by(Compagnie.nom).all()

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