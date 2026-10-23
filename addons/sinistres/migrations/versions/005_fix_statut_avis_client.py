"""fix chk_statut_evaluation to allow CLIENT_ACCEPTE / CLIENT_REFUSE

Revision ID: 005_fix_statut_avis
Revises: 004_rename_eval_fields
Create Date: 2026-10-23
"""
from alembic import op


revision = '005_fix_statut_avis'
down_revision = '004_rename_eval_fields'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('chk_statut_evaluation', 'lometa_evaluations', type_='check')
    op.create_check_constraint(
        'chk_statut_evaluation',
        'lometa_evaluations',
        "statut IN ("
        "'BROUILLON','AVIS_CLIENT_EN_ATTENTE',"
        "'CLIENT_ACCEPTE','CLIENT_REFUSE',"
        "'ACCEPTEE','REFUSEE',"
        "'VALIDEE','ANNULEE'"
        ")",
    )


def downgrade():
    op.drop_constraint('chk_statut_evaluation', 'lometa_evaluations', type_='check')
    op.create_check_constraint(
        'chk_statut_evaluation',
        'lometa_evaluations',
        "statut IN ("
        "'BROUILLON','AVIS_CLIENT_EN_ATTENTE',"
        "'ACCEPTEE','REFUSEE',"
        "'VALIDEE','ANNULEE'"
        ")",
    )