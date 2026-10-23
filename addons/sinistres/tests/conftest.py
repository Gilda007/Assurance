"""
Configuration pytest + fixtures partagées
"""
import sys
from pathlib import Path

# Ajouter la racine au PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from core.database import Base, SessionLocal


# ============================================================
# FIXTURES BASE DE DONNÉES
# ============================================================

@pytest.fixture(scope="session")
def engine():
    """Engine de test — utilise une base PostgreSQL de test ou SQLite mémoire"""
    # Option 1 : SQLite en mémoire (rapide, isolé)
    # return create_engine("sqlite:///:memory:", echo=False)
    
    # Option 2 : PostgreSQL réel (recommandé en CI/CD)
    from core.database import engine as prod_engine
    return prod_engine


@pytest.fixture(scope="function")
def db_session(engine) -> Generator[Session, None, None]:
    """
    Session de test transactionnelle.
    Rollback automatique après chaque test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def sample_user(db_session):
    """Utilisateur de test"""
    from addons.Parametres.models.models import User
    
    user = User(
        username="test_user",
        email="test@lometa.com",
        full_name="Test User",
        role="admin",
        is_active=True,
    )
    user.set_password("Test@123456")
    
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user