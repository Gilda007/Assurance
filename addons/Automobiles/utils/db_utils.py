# core/database.py ou addons/Automobiles/utils/db_utils.py

from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

def with_rollback(func):
    """Décorateur pour rollback automatique en cas d'erreur"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Trouver le premier argument qui a 'db_session' ou 'session'
        session = None
        for arg in args:
            if hasattr(arg, 'rollback'):
                session = arg
                break
        
        # Chercher dans les kwargs
        if not session:
            session = kwargs.get('db_session') or kwargs.get('session')
        
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as e:
            if session:
                session.rollback()
                logger.error(f"Rollback automatique pour {func.__name__}: {e}")
            raise
    return wrapper

def safe_query(func):
    """Décorateur pour exécuter une requête avec rollback automatique"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        session = None
        for arg in args:
            if hasattr(arg, 'rollback'):
                session = arg
                break
        if not session:
            session = kwargs.get('db_session') or kwargs.get('session')
        
        try:
            result = func(*args, **kwargs)
            return result
        except SQLAlchemyError as e:
            if session:
                session.rollback()
                logger.warning(f"Erreur dans {func.__name__}, rollback effectué: {e}")
            return None
    return wrapper