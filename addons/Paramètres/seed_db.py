import os
from core.database import SessionLocal, engine, Base
from addons.user_manager.models import User
from core.logger import logger

def seed():
    logger.info("Début du processus de seeding...")
    
    # 1. S'assurer que les tables existent
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 2. Vérifier si l'admin existe déjà
        # On cherche par username ou par email pour être sûr
        admin_exists = db.query(User).filter(
            (User.username == "admin") | (User.email == "admin@assurance.cm")
        ).first()

        if not admin_exists:
            logger.info("Création de l'utilisateur administrateur par défaut...")
            new_admin = User(
                username="admin",
                email="admin@assurance.cm",
                full_name="Administrateur Système",
                role="admin",
                is_active=True
            )
            # Hachage du mot de passe
            new_admin.set_password("Admin123_@")
            
            db.add(new_admin)
            db.commit() # Enregistrement définitif
            logger.info("✅ Utilisateur 'admin' créé avec succès !")
        else:
            logger.info(f"ℹ️ L'utilisateur '{admin_exists.username}' existe déjà en base.")

    except Exception as e:
        db.rollback() # Annuler en cas d'erreur
        logger.error(f"❌ Erreur lors du seeding : {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()