
from PySide6.QtCore import QObject, Signal
from datetime import datetime, timedelta
from core.database import SessionLocal
from core.alerts import AlertManager
from core.session import Session
from core.logger import logger
from ..models.models import User
import socket
import requests


class LoginController(QObject):
    # Signal émis en cas de succès, transmettant l'objet utilisateur
    login_success = Signal(object)

    def __init__(self, view):
        super().__init__()
        self.view = view
        # Connexion du signal venant de la vue (maintenant avec 3 paramètres)
        self.view.login_requested.connect(self.handle_login)

    def _get_client_ip(self):
        """Récupère l'adresse IP du client"""
        try:
            # IP locale
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # Tentative de récupération IP publique
            try:
                public_ip = requests.get('https://api.ipify.org', timeout=2).text
            except:
                public_ip = local_ip
            
            return f"{local_ip} (pub: {public_ip})"
        except:
            return "127.0.0.1"

    def _get_user_agent(self):
        """Récupère l'User-Agent pour la session"""
        # À adapter selon votre framework
        return "LOMETA-Desktop-Client/1.0"

    def handle_login(self, username, password, remember=False):
        """Logique d'authentification principale avec session sécurisée"""
        if not username or not password:
            AlertManager.show_error(self.view, "Champs vides", "Veuillez saisir un identifiant et un mot de passe.")
            return

        db = SessionLocal()
        try:
            # 1. Recherche de l'utilisateur en BDD
            user = db.query(User).filter(User.username == username).first()

            # 2. Vérification de l'existence et du mot de passe haché
            if user and user.check_password(password):
                if not user.is_active:
                    AlertManager.show_error(self.view, "Compte inactif", "Votre compte a été désactivé. Contactez l'administrateur.")
                    return

                # 3. Création de la session SÉCURISÉE avec durée selon "remember"
                # La méthode start() de Session gère maintenant le chiffrement et retourne le token
                encrypted_token = Session.start(user, remember=remember)
                
                # 4. Récupérer les informations de session
                session_expiry = Session._session_expiry
                session_token_plain = Session.get_session_token()
                
                # 5. Sauvegarde en base de données (token chiffré)
                from ..models.models import Session as SessionModel
                
                # Supprimer les anciennes sessions de l'utilisateur (optionnel)
                db.query(SessionModel).filter(SessionModel.user_id == user.id).delete()
                
                # Créer la nouvelle session en base
                new_session = SessionModel(
                    user_id=user.id,
                    token_encrypted=encrypted_token,  # ✅ Utilise la bonne colonne
                    expires_at=session_expiry,
                    ip_address=self._get_client_ip(),
                    user_agent=self._get_user_agent(),
                    last_activity=datetime.now()
                )
                db.add(new_session)
                db.commit()
                db.refresh(new_session)
                
                # 6. Ajouter le token à l'objet user pour une utilisation ultérieure
                user.session_token = session_token_plain  # Token brut pour les API
                user.encrypted_token = encrypted_token    # Token chiffré pour stockage
                
                logger.info(f"🔐 Authentification réussie pour : {username} (remember={remember})")
                logger.debug(f"   Session ID: {Session.get_session_id()}")
                logger.debug(f"   Expiration: {session_expiry.strftime('%d/%m/%Y %H:%M:%S') if session_expiry else 'N/A'}")
                logger.debug(f"   IP: {self._get_client_ip()}")
                
                # 7. Émission du signal pour ouvrir la MainWindow
                self.login_success.emit(user)
                
                # 8. Fermeture de la fenêtre de login
                self.view.close()
            else:
                # Sécurité : On ne précise pas si c'est le user ou le pass qui est faux
                logger.warning(f"⚠️ Tentative de connexion échouée pour : {username}")
                AlertManager.show_error(self.view, "Échec", "Identifiants invalides.")

        except Exception as e:
            logger.error(f"❌ Erreur lors de l'authentification : {str(e)}")
            AlertManager.show_error(self.view, "Erreur Système", "Impossible de contacter la base de données.", str(e))
        finally:
            db.close()

    def _create_session(self, db, user_id: int, remember: bool) -> str:
        """
        Ancienne méthode conservée pour compatibilité
        Utilise maintenant le nouveau système de session
        """
        encrypted_token = Session.start(None, remember=remember)  # Temporaire
        return encrypted_token
    
    def _verify_password(self, input_password: str, stored_hash: str) -> bool:
        """Vérifie le mot de passe (bcrypt ou clair)"""
        if not stored_hash:
            return False
        
        if stored_hash.startswith('$2'):
            try:
                import bcrypt
                return bcrypt.checkpw(input_password.encode('utf-8'), stored_hash.encode('utf-8'))
            except:
                return False
        
        return input_password == stored_hash