"""add type_mission referential and mission_parente

Revision ID: add_types_mission
Revises: <previous_revision>
Create Date: 2026-10-19
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_types_mission'
down_revision = '<mettre_votre_revision_precedente>'
branch_labels = None
depends_on = None


def upgrade():
    # ============================================================
    # 1. TABLE DE RÉFÉRENCE DES TYPES DE MISSION
    # ============================================================
    op.create_table(
        'lometa_types_mission',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=30), nullable=False),
        sa.Column('libelle', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('prefixe_numero', sa.String(length=10),
                  nullable=False, server_default=sa.text("'EXP'")),
        sa.Column('est_actif', sa.Boolean(), nullable=False,
                  server_default=sa.text('1')),
        sa.Column('ordre', sa.Integer(), nullable=True, server_default=sa.text('0')),
        sa.Column('couleur', sa.String(length=10), nullable=True),
        sa.Column('necessite_mission_parente', sa.Boolean(),
                  nullable=False, server_default=sa.text('0')),
        sa.Column('type_mission_parente_code', sa.String(length=30), nullable=True),
        sa.Column('date_effet', sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('date_fin', sa.DateTime(), nullable=True),
        # AuditableMixin
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True,
                  server_default=sa.text('1')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code', name='uq_types_mission_code'),
    )
    op.create_index('ix_lometa_types_mission_code',
                    'lometa_types_mission', ['code'])
    op.create_index('ix_lometa_types_mission_est_actif',
                    'lometa_types_mission', ['est_actif'])

    # ============================================================
    # 2. SEED INITIAL (CURRENT_TIMESTAMP portable)
    # ============================================================
    op.execute("""
        INSERT INTO lometa_types_mission
            (code, libelle, description, prefixe_numero, est_actif, ordre, couleur,
             necessite_mission_parente, type_mission_parente_code,
             date_effet, is_active)
        VALUES
            ('EXPERTISE', 'Expertise', 'Mission d''expertise classique',
             'EXP', 1, 1, '#2563eb', 0, NULL, CURRENT_TIMESTAMP, 1),
            ('GARAGISTE', 'Mission garagiste', 'Réparation / devis garagiste',
             'GAR', 1, 2, '#ea580c', 0, NULL, CURRENT_TIMESTAMP, 1),
            ('CONTRE_EXPERTISE', 'Contre-expertise',
             'Contre-expertise d''une mission garagiste',
             'CEX', 1, 3, '#7c3aed', 1, 'GARAGISTE', CURRENT_TIMESTAMP, 1),
            ('MEDICALE', 'Expertise médicale', 'Expertise médicale',
             'MED', 1, 4, '#0891b2', 0, NULL, CURRENT_TIMESTAMP, 1),
            ('JUDICIAIRE', 'Expertise judiciaire', 'Expertise judiciaire',
             'JUD', 1, 5, '#dc2626', 0, NULL, CURRENT_TIMESTAMP, 1);
    """)

    # ============================================================
    # 3. AJOUT DES COLONNES À lometa_expertises (nullable=True d'abord)
    # ============================================================
    op.add_column('lometa_expertises',
        sa.Column('type_mission_id', sa.Integer(), nullable=True))
    op.add_column('lometa_expertises',
        sa.Column('type_mission_code', sa.String(length=30), nullable=True))
    op.add_column('lometa_expertises',
        sa.Column('mission_parente_id', sa.Integer(), nullable=True))
    op.add_column('lometa_expertises',
        sa.Column('montant_devis_garagiste', sa.Numeric(), nullable=True))
    op.add_column('lometa_expertises',
        sa.Column('motif_contre_expertise', sa.Text(), nullable=True))

    # ============================================================
    # 4. BACKFILL : missions existantes = EXPERTISE
    # ============================================================
    op.execute("""
        UPDATE lometa_expertises
        SET type_mission_code = 'EXPERTISE',
            type_mission_id = (
                SELECT id FROM lometa_types_mission WHERE code = 'EXPERTISE'
            )
        WHERE type_mission_code IS NULL;
    """)

    # ============================================================
    # 5. PASSAGE EN NOT NULL (avec existing_type obligatoire)
    # ============================================================
    op.alter_column(
        'lometa_expertises', 'type_mission_id',
        existing_type=sa.Integer(), nullable=False
    )
    op.alter_column(
        'lometa_expertises', 'type_mission_code',
        existing_type=sa.String(length=30), nullable=False
    )

    # ============================================================
    # 6. CONTRAINTES FK
    # ============================================================
    op.create_foreign_key(
        'fk_expertises_type_mission',
        'lometa_expertises', 'lometa_types_mission',
        ['type_mission_id'], ['id'],
        ondelete='RESTRICT',
    )
    op.create_foreign_key(
        'fk_expertises_mission_parente',
        'lometa_expertises', 'lometa_expertises',
        ['mission_parente_id'], ['id'],
        ondelete='SET NULL',
    )

    # ============================================================
    # 7. INDEX
    # ============================================================
    op.create_index('ix_expertises_type_mission_code',
                    'lometa_expertises', ['type_mission_code'])
    op.create_index('ix_expertises_mission_parente_id',
                    'lometa_expertises', ['mission_parente_id'])


def downgrade():
    # 1. Drop index
    op.drop_index('ix_expertises_mission_parente_id',
                  table_name='lometa_expertises')
    op.drop_index('ix_expertises_type_mission_code',
                  table_name='lometa_expertises')

    # 2. Drop FK
    op.drop_constraint('fk_expertises_mission_parente',
                       'lometa_expertises', type_='foreignkey')
    op.drop_constraint('fk_expertises_type_mission',
                       'lometa_expertises', type_='foreignkey')

    # 3. Drop colonnes
    op.drop_column('lometa_expertises', 'motif_contre_expertise')
    op.drop_column('lometa_expertises', 'montant_devis_garagiste')
    op.drop_column('lometa_expertises', 'mission_parente_id')
    op.drop_column('lometa_expertises', 'type_mission_code')
    op.drop_column('lometa_expertises', 'type_mission_id')

    # 4. Drop table de référence
    op.drop_table('lometa_types_mission')