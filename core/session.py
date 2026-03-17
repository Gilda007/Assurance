from core.logger import logger

class Session:
    """
    Gestionnaire de session statique. 
    Permet d'accéder à l'utilisateur connecté depuis n'importe quel module.
    """
    _current_user = None

    @classmethod
    def start(cls, user):
        """Initialise la session avec l'objet utilisateur."""
        cls._current_user = user
        logger.info(f"🚀 Session active pour l'utilisateur : {user.username} (Rôle: {user.role})")

    @classmethod
    def get_user(cls):
        """Récupère l'utilisateur actuel."""
        return cls._current_user

    @classmethod
    def is_logged_in(cls):
        """Vérifie si une session est active."""
        return cls._current_user is not None

    @classmethod
    def logout(cls):
        """Détruit la session actuelle."""
        if cls._current_user:
            logger.info(f"👋 Déconnexion de l'utilisateur : {cls._current_user.username}")
        cls._current_user = None