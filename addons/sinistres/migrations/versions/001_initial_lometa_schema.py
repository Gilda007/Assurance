"""
Création du schéma initial LOMETA - Version adaptée pour Integer et utilisateurs existants

Revision ID: 001
Revises: 
Create Date: 2026-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================================
    # 1. TABLES DES RÉFÉRENTIELS (Tome 2)
    # ============================================================
    
    op.create_table(
        'lometa_referentiels',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('famille', sa.String(30), nullable=False, index=True),
        sa.Column('code', sa.String(50), nullable=False, index=True),
        sa.Column('libelle', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('date_effet', sa.DateTime, nullable=False),
        sa.Column('date_fin', sa.DateTime, nullable=True),
        sa.Column('societe', sa.String(100), nullable=True),
        sa.Column('branche', sa.String(50), nullable=True),
        sa.Column('valeur', sa.Float, nullable=True),
        sa.Column('donnees_supplementaires', sa.Text, nullable=True),
        sa.Column('est_actif', sa.Boolean, nullable=False, default=True, index=True),
        sa.Column('est_obsolete', sa.Boolean, nullable=False, default=False),
        sa.Column('version', sa.Integer, nullable=False, default=1),
        sa.Column('version_precedente_id', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('updated_by', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
    )
    op.create_unique_constraint('uq_lometa_referentiels_code_famille', 'lometa_referentiels', ['code', 'famille'])
    op.create_index('idx_lometa_referentiels_famille_actif', 'lometa_referentiels', ['famille', 'est_actif'])
    
    # Foreign Key vers utilisateurs
    op.create_foreign_key('fk_lometa_referentiels_created_by', 'lometa_referentiels', 'utilisateurs', ['created_by'], ['id'])
    op.create_foreign_key('fk_lometa_referentiels_updated_by', 'lometa_referentiels', 'utilisateurs', ['updated_by'], ['id'])
    
    # Table d'historique des référentiels
    op.create_table(
        'lometa_referentiels_historique',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('referentiel_id', sa.Integer, nullable=False, index=True),
        sa.Column('champ_modifie', sa.String(50), nullable=False),
        sa.Column('ancienne_valeur', sa.Text, nullable=True),
        sa.Column('nouvelle_valeur', sa.Text, nullable=True),
        sa.Column('date_modification', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('modifie_par', sa.Integer, nullable=False),
        sa.Column('ip_adresse', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('updated_by', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
    )
    op.create_foreign_key('fk_referentiel_historique_referentiel', 'lometa_referentiels_historique', 'lometa_referentiels', ['referentiel_id'], ['id'])
    op.create_foreign_key('fk_lometa_ref_hist_created_by', 'lometa_referentiels_historique', 'utilisateurs', ['created_by'], ['id'])
    op.create_foreign_key('fk_lometa_ref_hist_updated_by', 'lometa_referentiels_historique', 'utilisateurs', ['updated_by'], ['id'])
    op.create_foreign_key('fk_lometa_ref_hist_modifie_par', 'lometa_referentiels_historique', 'utilisateurs', ['modifie_par'], ['id'])
    
    # ============================================================
    # 2. TABLE DU DOSSIER SINISTRE (Tome 3)
    # ============================================================
    
    op.create_table(
        'lometa_sinistres',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('numero_sinistre', sa.String(20), nullable=False, unique=True, index=True),
        sa.Column('numero_reference', sa.String(20), nullable=True, index=True),
        sa.Column('date_survenance', sa.DateTime, nullable=False),
        sa.Column('date_declaration', sa.DateTime, nullable=False),
        sa.Column('date_ouverture', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('contrat_id', sa.Integer, nullable=False, index=True),
        sa.Column('client_id', sa.Integer, nullable=False, index=True),
        sa.Column('compagnie_id', sa.Integer, nullable=True),
        sa.Column('agence_id', sa.Integer, nullable=True),
        sa.Column('branche', sa.String(50), nullable=False, index=True),
        sa.Column('categorie', sa.String(50), nullable=False, index=True),
        sa.Column('sous_categorie', sa.String(50), nullable=True),
        sa.Column('statut', sa.String(30), nullable=False, default='OUVERT', index=True),
        sa.Column('taux_responsabilite', sa.Float, nullable=False, default=0.0),
        sa.Column('circonstance_principale', sa.String(100), nullable=False),
        sa.Column('circonstance_secondaire', sa.String(100), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('date_cloture', sa.DateTime, nullable=True),
        sa.Column('date_reexamen', sa.DateTime, nullable=True),
        sa.Column('date_derniere_modification', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('responsable_id', sa.Integer, nullable=True, index=True),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('updated_by', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
    )
    
    # Foreign Keys vers utilisateurs
    op.create_foreign_key('fk_lometa_sinistres_created_by', 'lometa_sinistres', 'utilisateurs', ['created_by'], ['id'])
    op.create_foreign_key('fk_lometa_sinistres_updated_by', 'lometa_sinistres', 'utilisateurs', ['updated_by'], ['id'])
    op.create_foreign_key('fk_lometa_sinistres_responsable', 'lometa_sinistres', 'utilisateurs', ['responsable_id'], ['id'])
    
    # Table des dommages
    op.create_table(
        'lometa_dommages',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('sinistre_id', sa.Integer, nullable=False, index=True),
        sa.Column('type_dommage', sa.String(50), nullable=False),
        sa.Column('code_dommage', sa.String(20), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('montant_estime', sa.Float, nullable=False, default=0.0),
        sa.Column('montant_accepte', sa.Float, nullable=True),
        sa.Column('evaluation_id', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('updated_by', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
    )
    op.create_foreign_key('fk_dommages_sinistre', 'lometa_dommages', 'lometa_sinistres', ['sinistre_id'], ['id'])
    op.create_foreign_key('fk_lometa_dommages_created_by', 'lometa_dommages', 'utilisateurs', ['created_by'], ['id'])
    op.create_foreign_key('fk_lometa_dommages_updated_by', 'lometa_dommages', 'utilisateurs', ['updated_by'], ['id'])
    
    # Table des tiers
    op.create_table(
        'lometa_tiers',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('sinistre_id', sa.Integer, nullable=False, index=True),
        sa.Column('type_tiers', sa.String(30), nullable=False),
        sa.Column('code_tiers', sa.String(20), nullable=True),
        sa.Column('nom', sa.String(100), nullable=False),
        sa.Column('prenom', sa.String(100), nullable=True),
        sa.Column('civilite', sa.String(10), nullable=True),
        sa.Column('adresse', sa.Text, nullable=True),
        sa.Column('code_postal', sa.String(10), nullable=True),
        sa.Column('ville', sa.String(50), nullable=True),
        sa.Column('pays', sa.String(50), nullable=True),
        sa.Column('telephone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(100), nullable=True),
        sa.Column('assurance', sa.String(100), nullable=True),
        sa.Column('police_assurance', sa.String(50), nullable=True),
        sa.Column('compagnie_assurance_id', sa.Integer, nullable=True),
        sa.Column('date_naissance', sa.DateTime, nullable=True),
        sa.Column('profession', sa.String(50), nullable=True),
        sa.Column('observations', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('updated_by', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
    )
    op.create_foreign_key('fk_tiers_sinistre', 'lometa_tiers', 'lometa_sinistres', ['sinistre_id'], ['id'])
    op.create_foreign_key('fk_lometa_tiers_created_by', 'lometa_tiers', 'utilisateurs', ['created_by'], ['id'])
    op.create_foreign_key('fk_lometa_tiers_updated_by', 'lometa_tiers', 'utilisateurs', ['updated_by'], ['id'])
    
    # Table des commentaires
    op.create_table(
        'lometa_commentaires',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('sinistre_id', sa.Integer, nullable=False, index=True),
        sa.Column('contenu', sa.Text, nullable=False),
        sa.Column('type_commentaire', sa.String(30), nullable=False),
        sa.Column('version', sa.Integer, nullable=False, default=1),
        sa.Column('version_precedente_id', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('updated_by', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
    )
    op.create_foreign_key('fk_commentaires_sinistre', 'lometa_commentaires', 'lometa_sinistres', ['sinistre_id'], ['id'])
    op.create_foreign_key('fk_lometa_commentaires_created_by', 'lometa_commentaires', 'utilisateurs', ['created_by'], ['id'])
    op.create_foreign_key('fk_lometa_commentaires_updated_by', 'lometa_commentaires', 'utilisateurs', ['updated_by'], ['id'])
    
    # Table d'historique des sinistres
    op.create_table(
        'lometa_historique',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('sinistre_id', sa.Integer, nullable=False, index=True),
        sa.Column('utilisateur_id', sa.Integer, nullable=False, index=True),
        sa.Column('utilisateur_nom', sa.String(100), nullable=True),
        sa.Column('date_action', sa.DateTime, nullable=False, default=datetime.utcnow, index=True),
        sa.Column('ip_adresse', sa.String(45), nullable=True),
        sa.Column('session_id', sa.String(100), nullable=True),
        sa.Column('action', sa.String(50), nullable=False, index=True),
        sa.Column('entite', sa.String(50), nullable=False),
        sa.Column('entite_id', sa.Integer, nullable=True),
        sa.Column('champ_modifie', sa.String(50), nullable=True),
        sa.Column('ancienne_valeur', sa.Text, nullable=True),
        sa.Column('nouvelle_valeur', sa.Text, nullable=True),
        sa.Column('commentaire', sa.Text, nullable=True),
    )
    op.create_foreign_key('fk_historique_sinistre', 'lometa_historique', 'lometa_sinistres', ['sinistre_id'], ['id'])
    op.create_foreign_key('fk_lometa_historique_utilisateur', 'lometa_historique', 'utilisateurs', ['utilisateur_id'], ['id'])
    op.create_index('idx_lometa_historique_utilisateur', 'lometa_historique', ['utilisateur_id', 'date_action'])
    op.create_index('idx_lometa_historique_entite', 'lometa_historique', ['entite', 'entite_id'])
    
    # ============================================================
    # 3. TABLES D'EXPERTISE ET ÉVALUATION (Tome 4)
    # ============================================================
    
    # Table des expertises
    op.create_table(
        'lometa_expertises',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('sinistre_id', sa.Integer, nullable=False, index=True),
        sa.Column('numero_mission', sa.String(20), nullable=False, unique=True, index=True),
        sa.Column('expert_id', sa.Integer, nullable=False, index=True),
        sa.Column('expert_nom', sa.String(100), nullable=True),
        sa.Column('type_expertise', sa.String(50), nullable=False),
        sa.Column('domaine', sa.String(50), nullable=True),
        sa.Column('date_mission', sa.DateTime, nullable=False),
        sa.Column('date_echeance', sa.DateTime, nullable=False),
        sa.Column('date_reception_rapport', sa.DateTime, nullable=True),
        sa.Column('date_validation', sa.DateTime, nullable=True),
        sa.Column('statut', sa.String(30), nullable=False, default='CREEE', index=True),
        sa.Column('rapport_contenu', sa.Text, nullable=True),
        sa.Column('rapport_path', sa.String(255), nullable=True),
        sa.Column('montant_estime', sa.Float, nullable=True),
        sa.Column('photos_path', sa.String(255), nullable=True),
        sa.Column('constats_path', sa.String(255), nullable=True),
        sa.Column('devis_path', sa.String(255), nullable=True),
        sa.Column('observations', sa.Text, nullable=True),
        sa.Column('preconisations', sa.Text, nullable=True),
        sa.Column('valide_par', sa.Integer, nullable=True),
        sa.Column('motif_refus', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('updated_by', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
    )
    op.create_foreign_key('fk_expertises_sinistre', 'lometa_expertises', 'lometa_sinistres', ['sinistre_id'], ['id'])
    op.create_foreign_key('fk_lometa_expertises_created_by', 'lometa_expertises', 'utilisateurs', ['created_by'], ['id'])
    op.create_foreign_key('fk_lometa_expertises_updated_by', 'lometa_expertises', 'utilisateurs', ['updated_by'], ['id'])
    op.create_foreign_key('fk_lometa_expertises_valide_par', 'lometa_expertises', 'utilisateurs', ['valide_par'], ['id'])
    
    # Table des documents d'expertise
    op.create_table(
        'lometa_documents_expertise',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('expertise_id', sa.Integer, nullable=False, index=True),
        sa.Column('type_document', sa.String(30), nullable=False),
        sa.Column('nom_fichier', sa.String(255), nullable=False),
        sa.Column('chemin_fichier', sa.String(255), nullable=False),
        sa.Column('taille', sa.Integer, nullable=True),
        sa.Column('hash_fichier', sa.String(64), nullable=True),
        sa.Column('date_upload', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('upload_par', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('updated_by', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
    )
    op.create_foreign_key('fk_docs_expertise', 'lometa_documents_expertise', 'lometa_expertises', ['expertise_id'], ['id'])
    op.create_foreign_key('fk_lometa_docs_expertise_created_by', 'lometa_documents_expertise', 'utilisateurs', ['created_by'], ['id'])
    op.create_foreign_key('fk_lometa_docs_expertise_updated_by', 'lometa_documents_expertise', 'utilisateurs', ['updated_by'], ['id'])
    op.create_foreign_key('fk_lometa_docs_expertise_upload_par', 'lometa_documents_expertise', 'utilisateurs', ['upload_par'], ['id'])
    
    # Table des évaluations
    op.create_table(
        'lometa_evaluations',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('sinistre_id', sa.Integer, nullable=False, index=True),
        sa.Column('numero_evaluation', sa.String(20), nullable=False, unique=True, index=True),
        sa.Column('type_evaluation', sa.String(50), nullable=False),
        sa.Column('categorie', sa.String(30), nullable=True),
        sa.Column('montant_brut', sa.Float, nullable=False),
        sa.Column('franchise', sa.Float, nullable=False, default=0.0),
        sa.Column('taux_responsabilite', sa.Float, nullable=False, default=1.0),
        sa.Column('montant_net', sa.Float, nullable=False),
        sa.Column('details', sa.Text, nullable=True),
        sa.Column('est_validee', sa.Boolean, nullable=False, default=False, index=True),
        sa.Column('validee_par', sa.Integer, nullable=True),
        sa.Column('date_validation', sa.DateTime, nullable=True),
        sa.Column('date_evaluation', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('updated_by', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
    )
    op.create_foreign_key('fk_evaluations_sinistre', 'lometa_evaluations', 'lometa_sinistres', ['sinistre_id'], ['id'])
    op.create_foreign_key('fk_lometa_evaluations_created_by', 'lometa_evaluations', 'utilisateurs', ['created_by'], ['id'])
    op.create_foreign_key('fk_lometa_evaluations_updated_by', 'lometa_evaluations', 'utilisateurs', ['updated_by'], ['id'])
    op.create_foreign_key('fk_lometa_evaluations_validee_par', 'lometa_evaluations', 'utilisateurs', ['validee_par'], ['id'])
    
    # Table des révisions d'évaluation
    op.create_table(
        'lometa_revisions_evaluation',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('evaluation_id', sa.Integer, nullable=False, index=True),
        sa.Column('ancien_montant_brut', sa.Float, nullable=False),
        sa.Column('ancien_montant_net', sa.Float, nullable=False),
        sa.Column('nouveau_montant_brut', sa.Float, nullable=False),
        sa.Column('nouveau_montant_net', sa.Float, nullable=False),
        sa.Column('motif', sa.String(200), nullable=False),
        sa.Column('date_revision', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('revise_par', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('updated_by', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
    )
    op.create_foreign_key('fk_revisions_evaluation', 'lometa_revisions_evaluation', 'lometa_evaluations', ['evaluation_id'], ['id'])
    op.create_foreign_key('fk_lometa_rev_eval_created_by', 'lometa_revisions_evaluation', 'utilisateurs', ['created_by'], ['id'])
    op.create_foreign_key('fk_lometa_rev_eval_updated_by', 'lometa_revisions_evaluation', 'utilisateurs', ['updated_by'], ['id'])
    op.create_foreign_key('fk_lometa_rev_eval_revise_par', 'lometa_revisions_evaluation', 'utilisateurs', ['revise_par'], ['id'])
    
    # Table des provisions
    op.create_table(
        'lometa_provisions',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('sinistre_id', sa.Integer, nullable=False, index=True),
        sa.Column('numero_provision', sa.String(20), nullable=False, unique=True, index=True),
        sa.Column('type_provision', sa.String(30), nullable=False),
        sa.Column('categorie', sa.String(30), nullable=True),
        sa.Column('montant', sa.Float, nullable=False),
        sa.Column('est_active', sa.Boolean, nullable=False, default=True, index=True),
        sa.Column('est_comptabilisee', sa.Boolean, nullable=False, default=False),
        sa.Column('date_creation', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('date_cloture', sa.DateTime, nullable=True),
        sa.Column('evaluation_id', sa.Integer, nullable=True),
        sa.Column('motif', sa.String(200), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('updated_by', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
    )
    op.create_foreign_key('fk_provisions_sinistre', 'lometa_provisions', 'lometa_sinistres', ['sinistre_id'], ['id'])
    op.create_foreign_key('fk_lometa_provisions_created_by', 'lometa_provisions', 'utilisateurs', ['created_by'], ['id'])
    op.create_foreign_key('fk_lometa_provisions_updated_by', 'lometa_provisions', 'utilisateurs', ['updated_by'], ['id'])
    
    # Table des mouvements de provision
    op.create_table(
        'lometa_mouvements_provision',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('provision_id', sa.Integer, nullable=False, index=True),
        sa.Column('type_mouvement', sa.String(30), nullable=False),
        sa.Column('ancien_montant', sa.Float, nullable=True),
        sa.Column('nouveau_montant', sa.Float, nullable=False),
        sa.Column('variation', sa.Float, nullable=False),
        sa.Column('motif', sa.String(200), nullable=False),
        sa.Column('date_mouvement', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('effectue_par', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('updated_by', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
    )
    op.create_foreign_key('fk_mouvements_provision', 'lometa_mouvements_provision', 'lometa_provisions', ['provision_id'], ['id'])
    op.create_foreign_key('fk_lometa_mouv_prov_created_by', 'lometa_mouvements_provision', 'utilisateurs', ['created_by'], ['id'])
    op.create_foreign_key('fk_lometa_mouv_prov_updated_by', 'lometa_mouvements_provision', 'utilisateurs', ['updated_by'], ['id'])
    op.create_foreign_key('fk_lometa_mouv_prov_effectue_par', 'lometa_mouvements_provision', 'utilisateurs', ['effectue_par'], ['id'])
    
    # ============================================================
    # 4. TABLES FINANCIÈRES (Tome 5)
    # ============================================================
    
    op.create_table(
        'lometa_beneficiaires',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('type_beneficiaire', sa.String(30), nullable=False),
        sa.Column('code_beneficiaire', sa.String(20), unique=True, nullable=True),
        sa.Column('nom', sa.String(100), nullable=False),
        sa.Column('prenom', sa.String(100), nullable=True),
        sa.Column('societe', sa.String(100), nullable=True),
        sa.Column('telephone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(100), nullable=True),
        sa.Column('adresse', sa.Text, nullable=True),
        sa.Column('code_postal', sa.String(10), nullable=True),
        sa.Column('ville', sa.String(50), nullable=True),
        sa.Column('pays', sa.String(50), nullable=False),
        sa.Column('iban', sa.String(34), nullable=True),
        sa.Column('bic_swift', sa.String(11), nullable=True),
        sa.Column('banque', sa.String(100), nullable=True),
        sa.Column('numero_mobile', sa.String(20), nullable=True),
        sa.Column('operateur_mobile', sa.String(20), nullable=True),
        sa.Column('est_actif', sa.Boolean, nullable=False, default=True, index=True),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('updated_by', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
    )
    op.create_foreign_key('fk_lometa_beneficiaires_created_by', 'lometa_beneficiaires', 'utilisateurs', ['created_by'], ['id'])
    op.create_foreign_key('fk_lometa_beneficiaires_updated_by', 'lometa_beneficiaires', 'utilisateurs', ['updated_by'], ['id'])
    
    op.create_table(
        'lometa_comptes_bancaires',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('code_banque', sa.String(20), nullable=False, unique=True, index=True),
        sa.Column('libelle', sa.String(100), nullable=False),
        sa.Column('iban', sa.String(34), nullable=False, unique=True),
        sa.Column('bic_swift', sa.String(11), nullable=True),
        sa.Column('devise', sa.String(3), nullable=False),
        sa.Column('banque', sa.String(100), nullable=False),
        sa.Column('agence', sa.String(100), nullable=True),
        sa.Column('solde', sa.Float, nullable=False, default=0.0),
        sa.Column('date_dernier_mouvement', sa.DateTime, nullable=True),
        sa.Column('statut', sa.String(20), nullable=False, default='ACTIF'),
        sa.Column('est_actif', sa.Boolean, nullable=False, default=True, index=True),
        sa.Column('est_par_defaut', sa.Boolean, nullable=False, default=False),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('updated_by', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
    )
    op.create_foreign_key('fk_lometa_comptes_banc_created_by', 'lometa_comptes_bancaires', 'utilisateurs', ['created_by'], ['id'])
    op.create_foreign_key('fk_lometa_comptes_banc_updated_by', 'lometa_comptes_bancaires', 'utilisateurs', ['updated_by'], ['id'])
    
    op.create_table(
        'lometa_reglements',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('sinistre_id', sa.Integer, nullable=False, index=True),
        sa.Column('numero_reglement', sa.String(20), nullable=False, unique=True, index=True),
        sa.Column('beneficiaire_id', sa.Integer, nullable=False, index=True),
        sa.Column('beneficiaire_nom', sa.String(100), nullable=True),
        sa.Column('montant', sa.Float, nullable=False),
        sa.Column('montant_lettres', sa.String(200), nullable=True),
        sa.Column('type_paiement', sa.String(20), nullable=False),
        sa.Column('date_demande', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('date_validation', sa.DateTime, nullable=True),
        sa.Column('date_paiement', sa.DateTime, nullable=True),
        sa.Column('statut', sa.String(30), nullable=False, default='CREE', index=True),
        sa.Column('numero_cheque', sa.String(20), nullable=True),
        sa.Column('banque_emetteur', sa.String(100), nullable=True),
        sa.Column('date_emission_cheque', sa.DateTime, nullable=True),
        sa.Column('reference_virement', sa.String(50), nullable=True),
        sa.Column('date_virement', sa.DateTime, nullable=True),
        sa.Column('numero_mobile', sa.String(20), nullable=True),
        sa.Column('operateur_mobile', sa.String(20), nullable=True),
        sa.Column('reference_mobile', sa.String(50), nullable=True),
        sa.Column('valide_par', sa.Integer, nullable=True),
        sa.Column('paiement_effectue_par', sa.Integer, nullable=True),
        sa.Column('note_credit_id', sa.Integer, nullable=True),
        sa.Column('est_note_credit', sa.Boolean, nullable=False, default=False),
        sa.Column('evaluation_id', sa.Integer, nullable=True),
        sa.Column('lot_paiement_id', sa.Integer, nullable=True),
        sa.Column('journal_comptable', sa.String(20), nullable=True),
        sa.Column('est_comptabilise', sa.Boolean, nullable=False, default=False),
        sa.Column('date_comptabilisation', sa.DateTime, nullable=True),
        sa.Column('observations', sa.Text, nullable=True),
        sa.Column('motif_annulation', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('updated_by', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
    )
    op.create_foreign_key('fk_reglements_sinistre', 'lometa_reglements', 'lometa_sinistres', ['sinistre_id'], ['id'])
    op.create_foreign_key('fk_reglements_beneficiaire', 'lometa_reglements', 'lometa_beneficiaires', ['beneficiaire_id'], ['id'])
    op.create_foreign_key('fk_lometa_reglements_created_by', 'lometa_reglements', 'utilisateurs', ['created_by'], ['id'])
    op.create_foreign_key('fk_lometa_reglements_updated_by', 'lometa_reglements', 'utilisateurs', ['updated_by'], ['id'])
    op.create_foreign_key('fk_lometa_reglements_valide_par', 'lometa_reglements', 'utilisateurs', ['valide_par'], ['id'])
    op.create_foreign_key('fk_lometa_reglements_paiement_par', 'lometa_reglements', 'utilisateurs', ['paiement_effectue_par'], ['id'])
    
    op.create_table(
        'lometa_lots_paiement',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('numero_lot', sa.String(20), nullable=False, unique=True, index=True),
        sa.Column('date_creation', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('date_traitement', sa.DateTime, nullable=True),
        sa.Column('date_comptabilisation', sa.DateTime, nullable=True),
        sa.Column('banque_id', sa.Integer, nullable=False),
        sa.Column('compte_bancaire_id', sa.Integer, nullable=False),
        sa.Column('nombre_paiements', sa.Integer, nullable=False, default=0),
        sa.Column('montant_total', sa.Float, nullable=False, default=0.0),
        sa.Column('statut', sa.String(20), nullable=False, default='OUVERT', index=True),
        sa.Column('type_lot', sa.String(20), nullable=False, default='STANDARD'),
        sa.Column('valide_par', sa.Integer, nullable=True),
        sa.Column('date_validation', sa.DateTime, nullable=True),
        sa.Column('observations', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('updated_by', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
    )
    op.create_foreign_key('fk_lots_compte_bancaire', 'lometa_lots_paiement', 'lometa_comptes_bancaires', ['compte_bancaire_id'], ['id'])
    op.create_foreign_key('fk_lometa_lots_created_by', 'lometa_lots_paiement', 'utilisateurs', ['created_by'], ['id'])
    op.create_foreign_key('fk_lometa_lots_updated_by', 'lometa_lots_paiement', 'utilisateurs', ['updated_by'], ['id'])
    op.create_foreign_key('fk_lometa_lots_valide_par', 'lometa_lots_paiement', 'utilisateurs', ['valide_par'], ['id'])
    
    op.create_table(
        'lometa_notes_credit',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('sinistre_id', sa.Integer, nullable=False, index=True),
        sa.Column('numero_note', sa.String(20), nullable=False, unique=True, index=True),
        sa.Column('reglement_origine_id', sa.Integer, nullable=True),
        sa.Column('type_note', sa.String(30), nullable=False),
        sa.Column('montant', sa.Float, nullable=False),
        sa.Column('motif', sa.Text, nullable=False),
        sa.Column('date_creation', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('date_validation', sa.DateTime, nullable=True),
        sa.Column('valide_par', sa.Integer, nullable=True),
        sa.Column('est_comptabilise', sa.Boolean, nullable=False, default=False),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('updated_by', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
    )
    op.create_foreign_key('fk_notes_credit_sinistre', 'lometa_notes_credit', 'lometa_sinistres', ['sinistre_id'], ['id'])
    op.create_foreign_key('fk_lometa_notes_credit_created_by', 'lometa_notes_credit', 'utilisateurs', ['created_by'], ['id'])
    op.create_foreign_key('fk_lometa_notes_credit_updated_by', 'lometa_notes_credit', 'utilisateurs', ['updated_by'], ['id'])
    op.create_foreign_key('fk_lometa_notes_credit_valide_par', 'lometa_notes_credit', 'utilisateurs', ['valide_par'], ['id'])
    
    # ============================================================
    # 5. TABLES DES RECOURS (Tome 6)
    # ============================================================
    
    op.create_table(
        'lometa_recours',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('sinistre_id', sa.Integer, nullable=False, index=True),
        sa.Column('numero_recours', sa.String(20), nullable=False, unique=True, index=True),
        sa.Column('type_recours', sa.String(30), nullable=False),
        sa.Column('debiteur_id', sa.Integer, nullable=False, index=True),
        sa.Column('debiteur_nom', sa.String(100), nullable=True),
        sa.Column('montant_reclame', sa.Float, nullable=False),
        sa.Column('montant_accepte', sa.Float, nullable=True),
        sa.Column('montant_encaisse', sa.Float, nullable=False, default=0.0),
        sa.Column('solde', sa.Float, nullable=False, default=0.0),
        sa.Column('date_ouverture', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('date_accord', sa.DateTime, nullable=True),
        sa.Column('date_derniere_relance', sa.DateTime, nullable=True),
        sa.Column('date_prochaine_relance', sa.DateTime, nullable=True),
        sa.Column('date_cloture', sa.DateTime, nullable=True),
        sa.Column('statut', sa.String(30), nullable=False, default='OUVERT', index=True),
        sa.Column('responsable_id', sa.Integer, nullable=False),
        sa.Column('nombre_relances', sa.Integer, nullable=False, default=0),
        sa.Column('relance_max', sa.Integer, nullable=False, default=5),
        sa.Column('reference_accord', sa.String(50), nullable=True),
        sa.Column('document_justificatif', sa.String(255), nullable=True),
        sa.Column('observations', sa.Text, nullable=True),
        sa.Column('motif_cloture', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('updated_by', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
    )
    op.create_foreign_key('fk_recours_sinistre', 'lometa_recours', 'lometa_sinistres', ['sinistre_id'], ['id'])
    op.create_foreign_key('fk_lometa_recours_created_by', 'lometa_recours', 'utilisateurs', ['created_by'], ['id'])
    op.create_foreign_key('fk_lometa_recours_updated_by', 'lometa_recours', 'utilisateurs', ['updated_by'], ['id'])
    op.create_foreign_key('fk_lometa_recours_responsable', 'lometa_recours', 'utilisateurs', ['responsable_id'], ['id'])
    
    op.create_table(
        'lometa_encaissements_recours',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('recours_id', sa.Integer, nullable=False, index=True),
        sa.Column('montant', sa.Float, nullable=False),
        sa.Column('mode_encaissement', sa.String(20), nullable=False),
        sa.Column('reference_bancaire', sa.String(50), nullable=True),
        sa.Column('date_encaissement', sa.DateTime, nullable=False),
        sa.Column('banque', sa.String(100), nullable=True),
        sa.Column('compte_bancaire_id', sa.Integer, nullable=True),
        sa.Column('est_partiel', sa.Boolean, nullable=False, default=False),
        sa.Column('solde_apres_encaissement', sa.Float, nullable=False),
        sa.Column('journal_comptable', sa.String(20), nullable=True),
        sa.Column('est_comptabilise', sa.Boolean, nullable=False, default=False),
        sa.Column('date_comptabilisation', sa.DateTime, nullable=True),
        sa.Column('note_credit_id', sa.Integer, nullable=True),
        sa.Column('observations', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('updated_by', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
    )
    op.create_foreign_key('fk_encaissements_recours', 'lometa_encaissements_recours', 'lometa_recours', ['recours_id'], ['id'])
    op.create_foreign_key('fk_lometa_enc_rec_created_by', 'lometa_encaissements_recours', 'utilisateurs', ['created_by'], ['id'])
    op.create_foreign_key('fk_lometa_enc_rec_updated_by', 'lometa_encaissements_recours', 'utilisateurs', ['updated_by'], ['id'])
    
    op.create_table(
        'lometa_reversements_recours',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('recours_id', sa.Integer, nullable=False, index=True),
        sa.Column('beneficiaire_id', sa.Integer, nullable=False),
        sa.Column('beneficiaire_nom', sa.String(100), nullable=True),
        sa.Column('montant', sa.Float, nullable=False),
        sa.Column('quote_part', sa.Float, nullable=False),
        sa.Column('type_reversement', sa.String(20), nullable=False),
        sa.Column('reglement_id', sa.Integer, nullable=True),
        sa.Column('mode_paiement', sa.String(20), nullable=False),
        sa.Column('reference_paiement', sa.String(50), nullable=True),
        sa.Column('date_reversement', sa.DateTime, nullable=False),
        sa.Column('date_comptabilisation', sa.DateTime, nullable=True),
        sa.Column('est_paye', sa.Boolean, nullable=False, default=False),
        sa.Column('est_comptabilise', sa.Boolean, nullable=False, default=False),
        sa.Column('observations', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('updated_by', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
    )
    op.create_foreign_key('fk_reversements_recours', 'lometa_reversements_recours', 'lometa_recours', ['recours_id'], ['id'])
    op.create_foreign_key('fk_lometa_rev_rec_created_by', 'lometa_reversements_recours', 'utilisateurs', ['created_by'], ['id'])
    op.create_foreign_key('fk_lometa_rev_rec_updated_by', 'lometa_reversements_recours', 'utilisateurs', ['updated_by'], ['id'])
    
    op.create_table(
        'lometa_relances_recours',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('recours_id', sa.Integer, nullable=False, index=True),
        sa.Column('date_relance', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('type_relance', sa.String(20), nullable=False),
        sa.Column('contenu', sa.Text, nullable=True),
        sa.Column('reponse_recue', sa.Boolean, nullable=False, default=False),
        sa.Column('date_reponse', sa.DateTime, nullable=True),
        sa.Column('contenu_reponse', sa.Text, nullable=True),
        sa.Column('effectue_par', sa.Integer, nullable=False),
        sa.Column('prochaine_relance', sa.DateTime, nullable=True),
        sa.Column('statut', sa.String(20), nullable=False, default='EN_ATTENTE'),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('updated_by', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
    )
    op.create_foreign_key('fk_relances_recours', 'lometa_relances_recours', 'lometa_recours', ['recours_id'], ['id'])
    op.create_foreign_key('fk_lometa_rel_rec_created_by', 'lometa_relances_recours', 'utilisateurs', ['created_by'], ['id'])
    op.create_foreign_key('fk_lometa_rel_rec_updated_by', 'lometa_relances_recours', 'utilisateurs', ['updated_by'], ['id'])
    op.create_foreign_key('fk_lometa_rel_rec_effectue_par', 'lometa_relances_recours', 'utilisateurs', ['effectue_par'], ['id'])
    
    # ============================================================
    # 6. TABLE D'AUDIT (Tome 7)
    # ============================================================
    
    op.create_table(
        'lometa_audit_logs',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('utilisateur_id', sa.Integer, nullable=False, index=True),
        sa.Column('utilisateur_nom', sa.String(100), nullable=True),
        sa.Column('utilisateur_role', sa.String(50), nullable=True),
        sa.Column('date_action', sa.DateTime, nullable=False, default=datetime.utcnow, index=True),
        sa.Column('action', sa.String(50), nullable=False, index=True),
        sa.Column('entite', sa.String(50), nullable=False, index=True),
        sa.Column('entite_id', sa.Integer, nullable=True, index=True),
        sa.Column('entite_nom', sa.String(200), nullable=True),
        sa.Column('champ_modifie', sa.String(50), nullable=True),
        sa.Column('ancienne_valeur', sa.Text, nullable=True),
        sa.Column('nouvelle_valeur', sa.Text, nullable=True),
        sa.Column('ip_adresse', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(255), nullable=True),
        sa.Column('session_id', sa.String(100), nullable=True),
        sa.Column('application', sa.String(50), nullable=True),
        sa.Column('commentaire', sa.Text, nullable=True),
        sa.Column('niveau', sa.String(20), nullable=False, default='INFO'),
    )
    op.create_index('idx_lometa_audit_logs_entite', 'lometa_audit_logs', ['entite', 'entite_id'])
    op.create_index('idx_lometa_audit_logs_date', 'lometa_audit_logs', ['date_action'])
    # Pas de FK vers utilisateurs pour l'audit (pour éviter les locks)


def downgrade() -> None:
    # Supprimer dans l'ordre inverse des dépendances
    
    op.drop_table('lometa_audit_logs')
    op.drop_table('lometa_relances_recours')
    op.drop_table('lometa_reversements_recours')
    op.drop_table('lometa_encaissements_recours')
    op.drop_table('lometa_recours')
    op.drop_table('lometa_notes_credit')
    op.drop_table('lometa_lots_paiement')
    op.drop_table('lometa_reglements')
    op.drop_table('lometa_comptes_bancaires')
    op.drop_table('lometa_beneficiaires')
    op.drop_table('lometa_mouvements_provision')
    op.drop_table('lometa_provisions')
    op.drop_table('lometa_revisions_evaluation')
    op.drop_table('lometa_evaluations')
    op.drop_table('lometa_documents_expertise')
    op.drop_table('lometa_expertises')
    op.drop_table('lometa_historique')
    op.drop_table('lometa_commentaires')
    op.drop_table('lometa_tiers')
    op.drop_table('lometa_dommages')
    op.drop_table('lometa_sinistres')
    op.drop_table('lometa_referentiels_historique')
    op.drop_table('lometa_referentiels')