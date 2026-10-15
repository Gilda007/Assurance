# alembic/versions/00X_add_beneficiaire_source_to_reglements.py

def upgrade():
    op.add_column(
        'lometa_reglements',
        sa.Column(
            'beneficiaire_source',
            sa.String(20),
            nullable=False,
            server_default='BENEFICIAIRE',
        )
    )
    op.create_index(
        'ix_lometa_reglements_beneficiaire_source',
        'lometa_reglements',
        ['beneficiaire_source']
    )

def downgrade():
    op.drop_index('ix_lometa_reglements_beneficiaire_source')
    op.drop_column('lometa_reglements', 'beneficiaire_source')