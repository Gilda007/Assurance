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

def create_compagnie(self, form_data, user_id):
        """
        Crée une compagnie en fusionnant les saisies utilisateur et les traces d'audit.
        :param form_data: Dictionnaire contenant les 7 champs du formulaire.
        :param user_id: L'ID numérique (Integer) de l'utilisateur connecté.
        """
        try:
            # 1. Capture des données système (IPs et Date)
            # On passe user_id à la méthode d'audit si celle-ci l'utilise
            audit = self._get_audit_data(user_id)

            # 2. Création de l'objet Compagnie mappé sur le modèle
            nouvelle_cie = Compagnie(
                # --- Données issues du formulaire ---
                code=form_data.get('code', '').upper(),
                nom=form_data.get('nom', '').upper(),
                email=form_data.get('email'),
                telephone=form_data.get('telephone'),
                adresse=form_data.get('adresse'),
                num_debut=form_data.get('num_debut'),
                num_fin=form_data.get('num_fin'),

                # --- Données d'audit (Maintenant en Integer pour les IDs) ---
                create_by=user_id,          # ID de l'utilisateur (Int)
                modify_by=user_id,          # ID de l'utilisateur (Int)
                created_at=audit['now'],
                modify_at=audit['now'],
                local_ip=audit['local_ip'],
                network_ip=audit['network_ip'],
                is_active=True
            )

            # 3. Persistance en base de données
            self.db.add(nouvelle_cie)
            self.db.commit()
            
            # Log de succès (on peut utiliser l'ID dans le log)
            if hasattr(self, 'logger'):
                self.logger.info(f"Compagnie {nouvelle_cie.nom} créée par l'utilisateur ID: {user_id}")
            
            return True, "Compagnie créée avec succès."

        except SQLAlchemyError as e:
            self.db.rollback()
            if hasattr(self, 'logger'):
                self.logger.error(f"Erreur DB création compagnie : {str(e)}")
            return False, f"Erreur de base de données : {str(e)}"
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