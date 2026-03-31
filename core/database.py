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
# Priorité à DATABASE_URL (par exemple pour PyInstaller/onefile), sinon variables séparées
database_url = os.getenv("DATABASE_URL")
if database_url:
    url_object = database_url
else:
    drivername = os.getenv("DRIVERNAME", "postgresql")
    if not isinstance(drivername, str) or not drivername.strip():
        raise RuntimeError("DRIVERNAME doit être défini et une chaîne non vide")

    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME", "")

    if not database:
        raise RuntimeError("DB_NAME doit être défini")

    url_object = URL.create(
        drivername=drivername,
        username=username,
        password=password,
        host=host,
        port=port,
        database=database,
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