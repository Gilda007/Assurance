"""rename evaluation proposition/avis fields to match model

Revision ID: 004_rename_eval_fields
Revises: 003_avis_client
Create Date: 2026-10-23
"""
from alembic import op
import sqlalchemy as sa


revision = '004_rename_eval_fields'
down_revision = '003_avis_client'
branch_labels = None
depends_on = None


def upgrade():
    # Renommer les colonnes
    op.alter_column(
        'lometa_evaluations', 'pdf_proposition_path',
        new_column_name='document_proposition_path',
    )
    op.alter_column(
        'lometa_evaluations', 'pdf_proposition_genere_at',
        new_column_name='document_proposition_generee_le',
    )
    op.alter_column(
        'lometa_evaluations', 'avis_client_recu_at',
        new_column_name='date_avis_client',
    )
    op.alter_column(
        'lometa_evaluations', 'avis_client_commentaire',
        new_column_name='commentaire_client',
    )
    op.alter_column(
        'lometa_evaluations', 'avis_client_document_path',
        new_column_name='piece_jointe_client_path',
    )
    op.alter_column(
        'lometa_evaluations', 'avis_client_document_nom',
        new_column_name='piece_jointe_client_nom',
    )
    op.alter_column(
        'lometa_evaluations', 'avis_client_document_type',
        new_column_name='piece_jointe_client_type',
        type_=sa.String(50),
        existing_type=sa.String(20),
    )


def downgrade():
    op.alter_column(
        'lometa_evaluations', 'piece_jointe_client_type',
        type_=sa.String(20),
        existing_type=sa.String(50),
    )
    op.alter_column(
        'lometa_evaluations', 'piece_jointe_client_type',
        new_column_name='avis_client_document_type',
    )
    op.alter_column(
        'lometa_evaluations', 'piece_jointe_client_nom',
        new_column_name='avis_client_document_nom',
    )
    op.alter_column(
        'lometa_evaluations', 'piece_jointe_client_path',
        new_column_name='avis_client_document_path',
    )
    op.alter_column(
        'lometa_evaluations', 'commentaire_client',
        new_column_name='avis_client_commentaire',
    )
    op.alter_column(
        'lometa_evaluations', 'date_avis_client',
        new_column_name='avis_client_recu_at',
    )
    op.alter_column(
        'lometa_evaluations', 'document_proposition_generee_le',
        new_column_name='pdf_proposition_genere_at',
    )
    op.alter_column(
        'lometa_evaluations', 'document_proposition_path',
        new_column_name='pdf_proposition_path',
    ) 