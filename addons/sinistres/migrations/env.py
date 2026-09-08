"""
Environnement Alembic pour LOMETA
"""
import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Importer les modèles LOMETA
from models import Base
from models.sinistre import Sinistre, Dommage, Tiers, CommentaireSinistre, HistoriqueSinistre
from models.expertise import Expertise, DocumentExpertise, Evaluation, RevisionEvaluation, Provision, MouvementProvision
from models.reglement import Beneficiaire, CompteBancaire, Reglement, LotPaiement, NoteCredit
from models.recours import Recours, EncaissementRecours, ReversementRecours, RelanceRecours
from models.referentiel import Referentiel, ReferentielHistorique
from models.audit import AuditLog

# Configuration
config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    """Exécute les migrations en mode offline."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Exécute les migrations en mode online."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()