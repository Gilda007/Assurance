
from PySide6.QtCore import QObject, Signal
from datetime import datetime, timedelta
from core.database import SessionLocal
from core.alerts import AlertManager
from core.session import Session
from core.logger import logger
from ..models.models import User  # Import relatif vers le modèle du même module


class LoginController(QObject):
    # Signal émis en cas de succès, transmettant l'objet utilisateur
    login_success = Signal(object)

    def __init__(self, view):
        super().__init__()
        self.view = view
        # Connexion du signal venant de la vue (maintenant avec 3 paramètres)
        self.view.login_requested.connect(self.handle_login)

    def handle_login(self, username, password, remember=False):
        """Logique d'authentification principale avec gestion de session"""
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

                # 3. Création de la session avec durée selon "remember"
                token = self._create_session(db, user.id, remember)
                
                # 4. Initialisation de la session globale
                Session.start(user)
                
                # 5. Ajouter le token à l'objet user pour une utilisation ultérieure
                user.session_token = token
                
                logger.info(f"Authentification réussie pour : {username} (remember={remember})")
                
                # 6. Émission du signal pour ouvrir la MainWindow
                self.login_success.emit(user)
                
                # 7. Fermeture de la fenêtre de login
                self.view.close()
            else:
                # Sécurité : On ne précise pas si c'est le user ou le pass qui est faux
                logger.warning(f"Tentative de connexion échouée pour : {username}")
                AlertManager.show_error(self.view, "Échec", "Identifiants invalides.")

        except Exception as e:
            logger.error(f"Erreur lors de l'authentification : {str(e)}")
            AlertManager.show_error(self.view, "Erreur Système", "Impossible de contacter la base de données.", str(e))
        finally:
            db.close()

    # def _create_session(self, db, user_id: int, remember: bool) -> str:
    #     """Crée une session dans la base de données"""
    #     import secrets
    #     import base64
        
    #     # Générer un token unique
    #     token = base64.b64encode(secrets.token_bytes(32)).decode('utf-8')
        
    #     # Définir la durée de la session
    #     if remember:
    #         expires_at = datetime.now() + timedelta(days=30)  # 30 jours
    #         logger.info(f"Session créée pour 30 jours (remember=True)")
    #     else:
    #         expires_at = datetime.now() + timedelta(hours=8)   # 8 heures
    #         logger.info(f"Session créée pour 8 heures (remember=False)")
        
    #     # Supprimer les anciennes sessions de l'utilisateur
    #     from ..models.models import Session as SessionModel
    #     db.query(SessionModel).filter(SessionModel.user_id == user_id).delete()
        
    #     # Créer la nouvelle session
    #     new_session = SessionModel(
    #         user_id=user_id,
    #         token=token,
    #         expires_at=expires_at
    #     )
    #     db.add(new_session)
    #     db.commit()
    #     db.refresh(new_session)
        
    #     return token


    def _create_session(self, db, user_id: int, remember: bool) -> str:
        """Crée une session avec le format attendu par update_server.py"""
        import base64
        import datetime
        
        # Format attendu par update_server.py: base64(user_id:timestamp)
        timestamp = datetime.datetime.now().timestamp()
        token_data = f"{user_id}:{timestamp}"
        token = base64.b64encode(token_data.encode()).decode()
        
        # Définir la durée de la session
        if remember:
            expires_at = datetime.datetime.now() + datetime.timedelta(days=30)
        else:
            expires_at = datetime.datetime.now() + datetime.timedelta(hours=8)
        
        # Supprimer les anciennes sessions
        from ..models.models import Session as SessionModel
        db.query(SessionModel).filter(SessionModel.user_id == user_id).delete()
        
        # Créer la nouvelle session
        new_session = SessionModel(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        print(f"✅ Session créée avec token: {token[:30]}... (expire le {expires_at})")
        return token

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