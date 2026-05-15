# import os
# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import configure_mappers, sessionmaker
# from sqlalchemy.engine import URL
# from dotenv import load_dotenv
# from core.logger import logger
# from sqlalchemy.exc import SQLAlchemyError

# # Charger les variables d'environnement
# load_dotenv()

# # Création de l'URL de manière structurée
# # Priorité à DATABASE_URL (par exemple pour PyInstaller/onefile), sinon variables séparées
# database_url = os.getenv("DATABASE_URL")
# if database_url:
#     url_object = database_url
# else:
#     drivername = os.getenv("DRIVERNAME", "postgresql")
#     if not isinstance(drivername, str) or not drivername.strip():
#         raise RuntimeError("DRIVERNAME doit être défini et une chaîne non vide")

#     username = os.getenv("DB_USER")
#     password = os.getenv("DB_PASS")
#     host = os.getenv("DB_HOST", "212.47.73.151")
#     port = os.getenv("DB_PORT", "5432")
#     database = os.getenv("DB_NAME", "ams_db")

#     if not database:
#         raise RuntimeError("DB_NAME doit être défini")

#     url_object = URL.create(
#         drivername=drivername,
#         username=username,
#         password=password,
#         host=host,
#         port=port,
#         database=database,
#     )

# # On ajoute explicitement le paramètre client_encoding
# try:
#     engine = create_engine(url_object)
#     with engine.connect() as conn:
#         logger.info("✅ Connexion à PostgreSQL établie avec succès.")
# except SQLAlchemyError as e:
#     logger.error(f"❌ Erreur critique de base de données : {str(e)}")
# except Exception as e:
#     logger.critical(f"❌ Erreur inattendue lors du démarrage : {str(e)}")

# # Création de la fabrique de sessions
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Classe de base pour les modèles (ORM)
# Base = declarative_base()

# def get_db():
#     """Fournit une session de base de données."""
#     db = SessionLocal()
#     try:
#         return db
#     finally:
#         db.close()

# # core/database.py

# def init_db():
#     try:
#         from addons.Paramètres.models.models import User
#         # from addons.contact_manager.models.models import Contact # (ton models.py)
#         # from addons.vehicule_management.models.models import Fleet, Vehicle# (ton models1.py)
#         # from addons.contrats_management.models.models import Contract # (ton models2.py)
        
#         from sqlalchemy.orm import configure_mappers
#         configure_mappers() # Scelle les relations 'owner' et 'vehicles'
        
#         Base.metadata.create_all(bind=engine)
#         logger.info("✅ Mappers configurés et base de données synchronisée.")
#     except Exception as e:
#         logger.error(f"❌ Erreur configuration mappers : {str(e)}")
#         raise e


# core/database.py - Version optimisée avec pool de connexions
import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import configure_mappers, sessionmaker, scoped_session
from sqlalchemy.engine import URL
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv
from core.logger import logger
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# Charger les variables d'environnement
load_dotenv()


# ============================================================================
# CONFIGURATION DU POOL DE CONNEXIONS POUR SERVEUR DISTANT
# ============================================================================

# Création de l'URL de manière structurée
database_url = os.getenv("DATABASE_URL")
if database_url:
    url_object = database_url
else:
    drivername = os.getenv("DRIVERNAME", "postgresql")
    if not isinstance(drivername, str) or not drivername.strip():
        raise RuntimeError("DRIVERNAME doit être défini et une chaîne non vide")

    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST", "212.47.73.151")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME", "ams_db")

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


# ============================================================================
# CRÉATION DU MOTEUR AVEC POOL OPTIMISÉ
# ============================================================================

# core/database.py - Modifier la configuration du pool

try:
    engine = create_engine(
        url_object,
        
        # Configuration du pool OPTIMISÉE
        poolclass=QueuePool,
        pool_size=20,              # Augmenté de 15 à 20
        max_overflow=30,           # Augmenté de 25 à 30
        pool_pre_ping=True,
        pool_recycle=1800,         # Recycle après 30 minutes (au lieu de 5)
        pool_timeout=60,           # Timeout augmenté à 60 secondes
        
        # Désactiver l'expiration des connexions trop agressive
        pool_use_lifo=True,        # Utiliser LIFO pour réutiliser les connexions récentes
        
        # Optimisations
        echo=False,
        echo_pool=False,
        
        # Paramètres de connexion
        connect_args={
            'connect_timeout': 15,      # Augmenté à 15 secondes
            'keepalives': 1,
            'keepalives_idle': 30,      # Augmenté à 30 secondes
            'keepalives_interval': 10,  # Augmenté à 10 secondes
            'keepalives_count': 5,
            'sslmode': 'prefer',
            'options': '-c statement_timeout=120000'  # Timeout requêtes 2 minutes
        }
    )
    
    # Tester la connexion
    with engine.connect() as conn:
        logger.info("✅ Connexion à PostgreSQL établie avec succès.")
        logger.info(f"   Host: {host}:{port}")
        logger.info(f"   Database: {database}")
        logger.info(f"   Pool size: 15 (max_overflow: 25)")
        
except SQLAlchemyError as e:
    logger.error(f"❌ Erreur critique de base de données : {str(e)}")
    raise
except Exception as e:
    logger.critical(f"❌ Erreur inattendue lors du démarrage : {str(e)}")
    raise


# ============================================================================
# CONFIGURATION DE LA SESSION
# ============================================================================

# Session locale avec autoflush désactivé pour performance
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,          # Désactive l'autoflush (réduit les requêtes)
    bind=engine,
    expire_on_commit=False    # Garde les objets en cache après commit
)

# Session thread-safe (pour les accès depuis plusieurs threads)
ScopedSession = scoped_session(SessionLocal)


# ============================================================================
# CLASSE DE BASE
# ============================================================================

Base = declarative_base()


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def get_db():
    """Fournit une session de base de données (compatible avec FastAPI/Depends)"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


def get_scoped_db():
    """Fournit une session thread-safe"""
    db = ScopedSession()
    try:
        return db
    finally:
        ScopedSession.remove()


def init_db():
    """Initialise la base de données avec les modèles"""
    try:
        # Importer les modèles (forcer leur enregistrement)
        from addons.Paramètres.models.models import User
        # Ajoutez vos autres modèles ici
        # from addons.Automobiles.models import ...
        
        # Configurer les mappers
        configure_mappers()
        
        # Créer les tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Mappers configurés et base de données synchronisée.")
    except Exception as e:
        logger.error(f"❌ Erreur configuration mappers : {str(e)}")
        raise e


def dispose_engine():
    """Ferme proprement le moteur et libère les connexions"""
    try:
        engine.dispose()
        logger.info("✅ Moteur de base de données fermé proprement.")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la fermeture du moteur: {e}")


# ============================================================================
# EVENT LISTENERS POUR LE DEBUG
# ============================================================================

@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log les requêtes SQL lentes (optionnel, à activer en debug)"""
    conn.info.setdefault('query_start_time', []).append(datetime.now())


@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log les requêtes SQL lentes (>1s)"""
    if 'query_start_time' in conn.info and conn.info['query_start_time']:
        total = datetime.now() - conn.info['query_start_time'].pop()
        if total.total_seconds() > 1:
            logger.warning(f"⚠️ Requête lente ({total.total_seconds():.2f}s): {statement[:100]}")