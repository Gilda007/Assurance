from PySide6.QtCore import QObject, Signal
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
        # Connexion du signal venant de la vue
        self.view.login_requested.connect(self.handle_login)

    def handle_login(self, username, password):
        """Logique d'authentification principale"""
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

                # 3. Succès : Initialisation de la session globale
                Session.start(user)
                logger.info(f"Authentification réussie pour : {username}")
                
                # 4. Émission du signal pour ouvrir la MainWindow
                self.login_success.emit(user)
                
                # 5. Fermeture de la fenêtre de login
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

        # Dans handle_login
        user = db.query(User).filter(User.username == username).first()

        print(f"--- DEBUG LOGIN ---")
        print(f"Username saisi: '{username}'")
        if user:
            print(f"User trouvé en BDD: '{user.username}'")
            print(f"Hash stocké: {user.password_hash}")
            # Test direct de bcrypt ici
            import bcrypt
            is_ok = bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8'))
            print(f"Résultat test bcrypt direct: {is_ok}")
        else:
            print("ERREUR: Aucun utilisateur trouvé avec ce nom.")