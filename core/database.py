import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import configure_mappers, sessionmaker
from sqlalchemy.engine import URL
from dotenv import load_dotenv
from core.logger import logger
from sqlalchemy.exc import SQLAlchemyError

# Charger les variables d'environnement
load_dotenv()

# Création de l'URL de manière structurée
url_object = URL.create(
    drivername=os.getenv("DRIVERNAME"),
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    host=os.getenv("DB_HOST"), # Valeur par défaut si vide
    port=os.getenv("DB_PORT", 5432),
    database=os.getenv("DB_NAME")
)

# On ajoute explicitement le paramètre client_encoding
try:
    engine = create_engine(url_object)
    with engine.connect() as conn:
        logger.info("✅ Connexion à PostgreSQL établie avec succès.")
except SQLAlchemyError as e:
    logger.error(f"❌ Erreur critique de base de données : {str(e)}")
except Exception as e:
    logger.critical(f"❌ Erreur inattendue lors du démarrage : {str(e)}")

# Création de la fabrique de sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base pour les modèles (ORM)
Base = declarative_base()

def get_db():
    """Fournit une session de base de données."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

# core/database.py

def init_db():
    try:
        from addons.Paramètres.models.models import User
        # from addons.contact_manager.models.models import Contact # (ton models.py)
        # from addons.vehicule_management.models.models import Fleet, Vehicle# (ton models1.py)
        # from addons.contrats_management.models.models import Contract # (ton models2.py)
        
        from sqlalchemy.orm import configure_mappers
        configure_mappers() # Scelle les relations 'owner' et 'vehicles'
        
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Mappers configurés et base de données synchronisée.")
    except Exception as e:
        logger.error(f"❌ Erreur configuration mappers : {str(e)}")
        raise e