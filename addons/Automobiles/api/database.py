# addons/Automobiles/api/database.py - Ajouter la fonction get_lometa_db

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from .config import settings

# Importation de la base LOMETA
from core.database import SessionLocal as LometaSessionLocal

logger = logging.getLogger(__name__)

# Création du moteur SQLAlchemy pour ASAC
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# Session locale pour ASAC
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles ASAC
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dépendance pour obtenir une session de base de données ASAC
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_lometa_db() -> Generator[Session, None, None]:
    """
    Dépendance pour obtenir une session de base de données LOMETA
    """
    db = LometaSessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialise la base de données ASAC (crée les tables)
    """
    try:
        # Importer les modèles pour créer les tables
        from . import models_db
        
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Base de données ASAC initialisée avec succès")
        
        # Créer les données par défaut
        init_default_data()
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation de la DB: {e}")
        raise


def init_default_data():
    """
    Initialise les données par défaut (types d'attestation, etc.)
    """
    db = SessionLocal()
    try:
        from . import models_db
        
        # Vérifier si des données existent déjà
        if db.query(models_db.CertificateType).count() == 0:
            # Types d'attestation
            cert_types = [
                {"code": "cima", "name": "Attestation CIMA"},
                {"code": "carte-rose", "name": "Carte Rose"},
            ]
            for ct in cert_types:
                cert_type = models_db.CertificateType(**ct)
                db.add(cert_type)
            
            # Variantes d'attestation (couleurs)
            variants = [
                {"code": "JAUNE", "name": "Attestation Jaune", "certificate_type_id": 1},
                {"code": "VERTE", "name": "Attestation Verte", "certificate_type_id": 1},
                {"code": "BLEUE", "name": "Attestation Bleue", "certificate_type_id": 1},
                {"code": "ROSE", "name": "Carte Rose", "certificate_type_id": 2},
            ]
            for var in variants:
                variant = models_db.CertificateVariant(**var)
                db.add(variant)
            
            db.commit()
            logger.info("✅ Données par défaut initialisées")
            
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation des données: {e}")
        db.rollback()
    finally:
        db.close()