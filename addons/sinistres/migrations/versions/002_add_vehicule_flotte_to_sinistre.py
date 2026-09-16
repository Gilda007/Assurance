"""
Ajout de la gestion des véhicules de flotte dans les sinistres

Revision ID: 002_add_vehicule_flotte
Revises: 001_initial_lometa_schema
Create Date: 2026-09-14
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '002_add_vehicule_flotte'
down_revision = '001_initial_lometa_schema'
branch_labels = None
depends_on = None


def upgrade():
    """
    Ajoute les colonnes de gestion flotte/véhicule à la table lometa_sinistres.
    """
    
    # ============================================================
    # 1. Ajouter les colonnes à lometa_sinistres
    # ============================================================
    
    # Vérifier si les colonnes existent déjà (pour idempotence)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('lometa_sinistres')]
    
    # Colonne : est_flotte (booléen)
    if 'est_flotte' not in columns:
        op.add_column(
            'lometa_sinistres',
            sa.Column(
                'est_flotte',
                sa.Boolean(),
                nullable=False,
                server_default=sa.text('false'),
                comment="Indique si le sinistre concerne un contrat flotte"
            )
        )
        # Index pour filtrage rapide
        op.create_index(
            'ix_lometa_sinistres_est_flotte',
            'lometa_sinistres',
            ['est_flotte'],
            unique=False
        )
    
    # Colonne : vehicule_sinistre_id (FK vers automobiles)
    if 'vehicule_sinistre_id' not in columns:
        op.add_column(
            'lometa_sinistres',
            sa.Column(
                'vehicule_sinistre_id',
                sa.Integer(),
                nullable=True,
                comment="Véhicule sinistré (obligatoire si est_flotte=True)"
            )
        )
        # FK vers la table des véhicules
        # ⚠️ Adaptez 'automobiles' au nom réel de votre table
        op.create_foreign_key(
            'fk_lometa_sinistres_vehicule',
            'lometa_sinistres',
            'vehicles',           # ← nom de la table Vehicle
            ['vehicule_sinistre_id'],
            ['id'],
            ondelete='SET NULL'
        )
        op.create_index(
            'ix_lometa_sinistres_vehicule_sinistre_id',
            'lometa_sinistres',
            ['vehicule_sinistre_id'],
            unique=False
        )
    
    # Colonne : flotte_id (FK vers fleets)
    if 'flotte_id' not in columns:
        op.add_column(
            'lometa_sinistres',
            sa.Column(
                'flotte_id',
                sa.Integer(),
                nullable=True,
                comment="Flotte associée au sinistre (si est_flotte=True)"
            )
        )
        op.create_foreign_key(
            'fk_lometa_sinistres_flotte',
            'lometa_sinistres',
            'fleets',                # ← nom de la table Fleet
            ['flotte_id'],
            ['id'],
            ondelete='SET NULL'
        )
        op.create_index(
            'ix_lometa_sinistres_flotte_id',
            'lometa_sinistres',
            ['flotte_id'],
            unique=False
        )
    
    # ============================================================
    # 2. Ajouter une contrainte de cohérence
    # ============================================================
    
    # Un sinistre flotte DOIT avoir un véhicule
    # (mais pas l'inverse : un sinistre peut avoir un véhicule sans être flotte)
    op.create_check_constraint(
        'ck_lometa_sinistres_flotte_vehicule',
        'lometa_sinistres',
        "(est_flotte = false) OR (est_flotte = true AND vehicule_sinistre_id IS NOT NULL)"
    )
    
    # ============================================================
    # 3. Mise à jour des sinistres existants
    # ============================================================
    
    # Initialiser est_flotte à false pour tous les sinistres existants
    op.execute("""
        UPDATE lometa_sinistres
        SET est_flotte = false
        WHERE est_flotte IS NULL
    """)
    
    print("✅ Migration 002 : colonnes flotte/véhicule ajoutées")


def downgrade():
    """Supprime les ajouts en cas de rollback"""
    
    # Supprimer la contrainte de cohérence
    op.drop_constraint(
        'ck_lometa_sinistres_flotte_vehicule',
        'lometa_sinistres',
        type_='check'
    )
    
    # Supprimer les FK et index
    op.drop_index('ix_lometa_sinistres_flotte_id', table_name='lometa_sinistres')
    op.drop_constraint('fk_lometa_sinistres_flotte', 'lometa_sinistres', type_='foreignkey')
    op.drop_column('lometa_sinistres', 'flotte_id')
    
    op.drop_index('ix_lometa_sinistres_vehicule_sinistre_id', table_name='lometa_sinistres')
    op.drop_constraint('fk_lometa_sinistres_vehicule', 'lometa_sinistres', type_='foreignkey')
    op.drop_column('lometa_sinistres', 'vehicule_sinistre_id')
    
    op.drop_index('ix_lometa_sinistres_est_flotte', table_name='lometa_sinistres')
    op.drop_column('lometa_sinistres', 'est_flotte')
    
    print("✅ Migration 002 : rollback effectué")