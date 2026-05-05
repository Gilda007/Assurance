# migrate_contracts.py
"""
Script de migration pour ajouter les nouveaux champs à la table contrats
"""

import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from core.database import engine, Base
from addons.Automobiles.models.contract_models import Contrat


def migrate_contracts_table():
    """Ajoute les nouvelles colonnes à la table contrats"""
    
    print("🔍 Vérification de la table contrats...")
    
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('contrats')]
    
    # Ajouter la colonne type_contrat
    if 'type_contrat' not in columns:
        print("➕ Ajout de la colonne type_contrat...")
        with engine.connect() as conn:
            conn.execute(sa.text(
                "ALTER TABLE contrats ADD COLUMN type_contrat VARCHAR(20) DEFAULT 'VEHICULE'"
            ))
            conn.commit()
        print("✅ Colonne type_contrat ajoutée")
    else:
        print("ℹ️ Colonne type_contrat existe déjà")
    
    # Ajouter la colonne contrat_flotte_id
    if 'contrat_flotte_id' not in columns:
        print("➕ Ajout de la colonne contrat_flotte_id...")
        with engine.connect() as conn:
            conn.execute(sa.text(
                "ALTER TABLE contrats ADD COLUMN contrat_flotte_id INTEGER"
            ))
            conn.commit()
        print("✅ Colonne contrat_flotte_id ajoutée")
    else:
        print("ℹ️ Colonne contrat_flotte_id existe déjà")
    
    # Mettre à jour les contrats existants
    print("🔄 Mise à jour des contrats existants...")
    session = Session(engine)
    try:
        # Mettre à jour les contrats de flotte
        result = session.execute(
            sa.text(
                "UPDATE contrats SET type_contrat = 'FLOTTE' "
                "WHERE fleet_id IS NOT NULL AND vehicle_id IS NULL AND type_contrat = 'VEHICULE'"
            )
        )
        session.commit()
        print(f"   - {result.rowcount} contrat(s) de flotte mis à jour")
        
        # Mettre à jour les contrats de véhicules individuels
        result = session.execute(
            sa.text(
                "UPDATE contrats SET type_contrat = 'VEHICULE' "
                "WHERE vehicle_id IS NOT NULL AND type_contrat IS NULL"
            )
        )
        session.commit()
        print(f"   - {result.rowcount} contrat(s) de véhicule mis à jour")
        
        print("✅ Migration terminée avec succès")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erreur lors de la migration: {e}")
    finally:
        session.close()


def verify_migration():
    """Vérifie que la migration a bien été effectuée"""
    session = Session(engine)
    try:
        # Compter les contrats par type
        result = session.execute(
            sa.text(
                "SELECT type_contrat, COUNT(*) as count FROM contrats "
                "GROUP BY type_contrat"
            )
        )
        
        print("\n📊 État des contrats après migration:")
        for row in result:
            print(f"   - {row.type_contrat}: {row.count} contrat(s)")
        
        # Compter les contrats de flotte avec sous-contrats
        result = session.execute(
            sa.text(
                "SELECT COUNT(*) FROM contrats WHERE type_contrat = 'FLOTTE'"
            )
        )
        fleet_count = result.scalar()
        print(f"\n   Total contrats de flotte: {fleet_count}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 MIGRATION DE LA TABLE CONTRATS")
    print("=" * 50)
    
    migrate_contracts_table()
    verify_migration()
    
    print("\n✅ Migration terminée")