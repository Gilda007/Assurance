"""add avis client fields to lometa_evaluations

Revision ID: 003_avis_client
Revises: 002_add_vehicule_flotte_to_sinistre
Create Date: 2026-10-23
"""
from alembic import op
import sqlalchemy as sa


revision = '003_avis_client'
down_revision = '002_add_vehicule_flotte_to_sinistre'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Élargir statut
    op.alter_column(
        'lometa_evaluations', 'statut',
        type_=sa.String(30),
        existing_type=sa.String(20),
        existing_nullable=False,
    )
    op.alter_column(
        'lometa_evaluations', 'statut',
        server_default='AVIS_CLIENT_EN_ATTENTE',
    )

    # 2. PDF proposition
    op.add_column('lometa_evaluations',
        sa.Column('pdf_proposition_path', sa.String(500), nullable=True))
    op.add_column('lometa_evaluations',
        sa.Column('pdf_proposition_genere_at', sa.DateTime(), nullable=True))

    # 3. Avis client
    op.add_column('lometa_evaluations',
        sa.Column('avis_client', sa.String(20), nullable=True))
    op.add_column('lometa_evaluations',
        sa.Column('avis_client_document_path', sa.String(500), nullable=True))
    op.add_column('lometa_evaluations',
        sa.Column('avis_client_document_type', sa.String(20), nullable=True))
    op.add_column('lometa_evaluations',
        sa.Column('avis_client_document_nom', sa.String(255), nullable=True))
    op.add_column('lometa_evaluations',
        sa.Column('avis_client_commentaire', sa.Text(), nullable=True))
    op.add_column('lometa_evaluations',
        sa.Column('avis_client_recu_at', sa.DateTime(), nullable=True))

    # 4. Index
    op.create_index(
        'ix_lometa_evaluations_avis_client',
        'lometa_evaluations', ['avis_client'],
    )

    # 5. Contraintes
    op.create_check_constraint(
        'chk_avis_client', 'lometa_evaluations',
        "avis_client IS NULL OR avis_client IN ('ACCEPTE', 'REFUSE')",
    )
    op.create_check_constraint(
        'chk_statut_evaluation', 'lometa_evaluations',
        "statut IN ('BROUILLON','AVIS_CLIENT_EN_ATTENTE',"
        "'ACCEPTEE','REFUSEE','VALIDEE','ANNULEE')",
    )

    # 6. Migration des données
    op.execute("""
        UPDATE lometa_evaluations
        SET statut = 'VALIDEE'
        WHERE est_validee = TRUE
          AND (statut IS NULL OR statut IN ('BROUILLON', ''))
    """)
    op.execute("""
        UPDATE lometa_evaluations
        SET statut = 'AVIS_CLIENT_EN_ATTENTE'
        WHERE est_validee = FALSE
          AND (statut IS NULL OR statut IN ('BROUILLON', ''))
    """)


def downgrade():
    op.drop_constraint('chk_statut_evaluation', 'lometa_evaluations',
                       type_='check')
    op.drop_constraint('chk_avis_client', 'lometa_evaluations',
                       type_='check')
    op.drop_index('ix_lometa_evaluations_avis_client',
                  table_name='lometa_evaluations')
    op.drop_column('lometa_evaluations', 'avis_client_recu_at')
    op.drop_column('lometa_evaluations', 'avis_client_commentaire')
    op.drop_column('lometa_evaluations', 'avis_client_document_nom')
    op.drop_column('lometa_evaluations', 'avis_client_document_type')
    op.drop_column('lometa_evaluations', 'avis_client_document_path')
    op.drop_column('lometa_evaluations', 'avis_client')
    op.drop_column('lometa_evaluations', 'pdf_proposition_genere_at')
    op.drop_column('lometa_evaluations', 'pdf_proposition_path')
    op.alter_column(
        'lometa_evaluations', 'statut',
        server_default='BROUILLON',
    )