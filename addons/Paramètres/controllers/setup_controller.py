from PySide6.QtCore import QObject, Signal
from core.database import SessionLocal
from core.alerts import AlertManager
from core.logger import logger
from ..models.models import User # On garde ton chemin d'import actuel

class SetupController(QObject):
    # Signal émis quand l'admin est créé avec succès
    setup_finished = Signal()

    def __init__(self, view):
        super().__init__()
        self.view = view
        # Connexion au bouton de validation de la vue Setup
        self.view.btn_create.clicked.connect(self.handle_setup)

    def handle_setup(self):
        """Logique de création du premier administrateur"""
        username = self.view.username.text().strip()
        full_name = self.view.full_name.text().strip()
        password = self.view.password.text().strip()
        email = self.view.email.text().strip() if hasattr(self.view, 'email') else f"{username}@system.local"

        # 1. Validation basique
        if not username or not password or not full_name:
            AlertManager.show_error(self.view, "Champs requis", "Veuillez remplir tous les champs pour initialiser le système.")
            return

        if len(password) < 6:
            AlertManager.show_error(self.view, "Sécurité", "Le mot de passe doit contenir au moins 6 caractères.")
            return

        db = SessionLocal()
        try:
            logger.info(f"Initialisation du premier compte administrateur : {username}")
            
            # 2. Création de l'objet User
            new_admin = User(
                username=username,
                full_name=full_name,
                email=email,
                role="admin",  # Forcé en admin car c'est le setup initial
                is_active=True
            )
            
            # 3. Hachage sécurisé (utilise ta méthode set_password du modèle)
            new_admin.set_password(password)
            
            # 4. Enregistrement en BDD
            db.add(new_admin)
            db.commit()
            
            logger.info("✅ Système initialisé avec succès.")
            AlertManager.show_info(self.view, "Succès", "Le compte administrateur a été créé. Vous pouvez maintenant vous connecter.")
            
            # 5. Signal au main.py pour basculer vers le Login
            self.setup_finished.emit()
            self.view.close()

        except Exception as e:
            db.rollback()
            logger.error(f"Erreur lors de l'initialisation : {str(e)}")
            AlertManager.show_error(self.view, "Erreur Fatale", "Impossible d'enregistrer l'administrateur.", str(e))
        finally:
            db.close()