
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
import threading
import ctypes
from contextlib import contextmanager
from functools import wraps
import time

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
    host = os.getenv("DB_HOST", "")
    port = os.getenv("DB_PORT", "")
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
        from addons.Automobiles import models as automobiles_models
        # Ajoutez vos autres modèles ici si besoin
        
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


class TimeoutError(Exception):
    """Exception levée quand une opération dépasse le délai"""
    pass


def _raise_timeout(thread_id, exception):
    """Lève une exception dans un thread cible en utilisant ctypes."""
    if thread_id is None:
        return
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread_id), ctypes.py_object(exception)
    )
    if res == 0:
        return
    if res > 1:
        # Annuler si plusieurs états ont été modifiés
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), None)
        raise SystemError("PyThreadState_SetAsyncExc a modifié plusieurs threads")


@contextmanager
def timeout(seconds):
    """Context manager pour limiter le temps d'exécution d'une opération
    Version thread-safe utilisant threading.Timer au lieu de signal
    """
    if seconds <= 0:
        yield
        return

    timer = threading.Timer(
        seconds,
        _raise_timeout,
        args=(threading.current_thread().ident, TimeoutError(f"L'opération a dépassé le délai de {seconds} secondes")),
    )
    timer.daemon = True
    timer.start()

    try:
        yield
    finally:
        timer.cancel()


def db_timeout(seconds=30):
    """Décorateur pour ajouter un timeout aux opérations DB
    
    Utilisation:
        @db_timeout(30)
        def get_vehicles(self, fleet_id):
            return self.session.query(Vehicle).filter(Vehicle.fleet_id == fleet_id).all()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with timeout(seconds):
                return func(*args, **kwargs)
        return wrapper
    return decorator

# core/database.py - Ajoutez ces fonctions à la fin du fichier

# ============================================================================
# FONCTIONS DE CONNEXION ROBUSTE AVEC RETRY
# ============================================================================

def get_db_with_retry(max_retries=3, delay=1):
    """
    Obtient une session DB avec mécanisme de retry
    Utilisation: db = get_db_with_retry()
    """
    last_error = None
    
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            # Tester la connexion
            db.execute("SELECT 1")
            return db
        except Exception as e:
            last_error = e
            logger.warning(f"Tentative connexion DB {attempt + 1}/{max_retries} échouée: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(delay)  # MAINTENANT time est défini
                # Forcer la fermeture des connexions existantes
                try:
                    engine.dispose()
                except:
                    pass
    
    logger.error(f"Impossible de se connecter à la DB après {max_retries} tentatives")
    raise last_error


def execute_with_retry(func, *args, max_retries=3, delay=1, **kwargs):
    """
    Exécute une fonction DB avec retry automatique
    
    Utilisation:
        result = execute_with_retry(session.query, Vehicle).filter(...).all
    """
    last_error = None
    
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as e:
            last_error = e
            logger.warning(f"Tentative {attempt + 1}/{max_retries} échouée: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(delay)
                # Recréer la session si nécessaire
                if 'session' in kwargs:
                    kwargs['session'].rollback()
    
    raise last_error


class RobustSession:
    """Wrapper pour une session DB avec gestion automatique des erreurs"""
    
    def __init__(self, session):
        self.session = session
        self._closed = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def execute(self, query, *args, **kwargs):
        """Exécute une requête avec retry"""
        return execute_with_retry(self.session.execute, query, *args, **kwargs)
    
    def commit(self):
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def rollback(self):
        self.session.rollback()
    
    def close(self):
        if not self._closed:
            self.session.close()
            self._closed = True
    
    def refresh(self, obj):
        self.session.refresh(obj)


def get_robust_db():
    """Obtient une session DB robuste avec retry"""
    db = get_db_with_retry()
    return RobustSession(db)