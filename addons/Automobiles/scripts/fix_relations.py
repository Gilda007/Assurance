# scripts/migrate_vehicle_models.py

"""
Script pour migrer les modèles de véhicules
"""

import sys
from pathlib import Path

# Ajouter le chemin racine
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from sqlalchemy import create_engine, inspect, text
from core.database import SessionLocal
from core.database import Base
from addons.Automobiles.models.automobile_models import Vehicle
from addons.Automobiles.models.vehicle_identification import VehicleIdentification
from addons.Automobiles.models.vehicle_classification import VehicleClassification
from addons.Automobiles.models.vehicle_technical import VehicleTechnical
from addons.Automobiles.models.vehicle_valuation import VehicleValuation
from addons.Automobiles.models.vehicle_options import VehicleOptions
from addons.Automobiles.models.vehicle_tariff import VehicleTariff
from addons.Automobiles.models.vehicle_guarantee import VehicleGuarantee

def migrate():
    """Migre les données du modèle Vehicle existant vers les nouveaux modèles"""
    
    engine = create_engine('postgresql://ams_admin:Ams123_@localhost:5432/ams_db')
    
    # Créer les nouvelles tables
    Base.metadata.create_all(engine)
    print("✅ Tables créées")
    
    session = SessionLocal()
    
    try:
        # Récupérer tous les véhicules existants
        old_vehicles = session.query(Vehicle).all()
        print(f"📊 {len(old_vehicles)} véhicules à migrer")
        
        for old in old_vehicles:
            # 1. Identification
            ident = VehicleIdentification(
                vehicle_id=old.id,
                licence_plate=getattr(old, 'immatriculation', ''),
                chassis=getattr(old, 'chassis', ''),
                brand=getattr(old, 'marque', ''),
                model=getattr(old, 'modele', ''),
                year=getattr(old, 'annee', None),
                first_registration_date=getattr(old, 'date_mise_circulation', None)
            )
            session.add(ident)
            
            # 2. Classification
            # (à adapter selon les champs existants)
            classif = VehicleClassification(
                vehicle_id=old.id,
                category=getattr(old, 'categorie', 'VP10'),
                genre=getattr(old, 'genre', 'GV04'),
                type=getattr(old, 'type_vehicule', 'TV10'),
                usage=getattr(old, 'usage', 'UV01'),
                energy=getattr(old, 'energie', 'SEE'),
                circulation_zone=getattr(old, 'zone', 'ZA')
            )
            session.add(classif)
            
            # 3. Technique
            tech = VehicleTechnical(
                vehicle_id=old.id,
                nb_of_seats=getattr(old, 'places', 5),
                fiscal_power=getattr(old, 'puissance_fiscale', 5),
                displacement=getattr(old, 'cylindree', 0),
                gross_weight=getattr(old, 'ptac', 0),
                payload_capacity=getattr(old, 'charge_utile', 0)
            )
            session.add(tech)
            
            # 4. Valuation
            val = VehicleValuation(
                vehicle_id=old.id,
                valeur_neuf=getattr(old, 'valeur_neuf', 0),
                valeur_venale=getattr(old, 'valeur_venale', 0)
            )
            session.add(val)
            
            # 5. Options
            opts = VehicleOptions(
                vehicle_id=old.id,
                has_trailer=getattr(old, 'has_remorque', False),
                trailer_flammable=getattr(old, 'remorque_inflammable', False),
                trailer_licence_plate=getattr(old, 'remorque_immat', ''),
                dual_control=getattr(old, 'double_commande', False),
                engine_type=getattr(old, 'engin_portuaire', False),
                civil_liability=getattr(old, 'rc_eleves', False)
            )
            session.add(opts)
            
            # 6. Tariff
            tariff = VehicleTariff(
                vehicle_id=old.id,
                code_tarif=getattr(old, 'code_tarif', ''),
                libele_tarif=getattr(old, 'libele_tarif', ''),
                code_assure=getattr(old, 'code_assure', '')
            )
            session.add(tariff)
            
            # 7. Garanties
            # (à adapter selon les champs existants)
            garanties = [
                ('rc', 'Responsabilité Civile', 'amt_rc', 'amt_val_red_rc', 'red_rc'),
                ('dr', 'Défense Recours', 'amt_dr', 'amt_val_red_dr', 'red_dr'),
                ('vol', 'Vol/Vol partie', 'amt_vol', 'amt_val_red_vol', 'red_vol'),
                ('vb', 'Vol/Braquage', 'amt_vb', 'amt_val_red_vb', 'red_vb'),
                ('in', 'Incendie', 'amt_in', 'amt_val_red_in', 'red_in'),
                ('bris', 'Bris de Glace', 'amt_bris', 'amt_val_red_bris', 'red_bris'),
                ('ar', 'Assistance Réparation', 'amt_ar', 'amt_val_red_ar', 'red_ar'),
                ('dta', 'Dommages', 'amt_dta', 'amt_val_red_dta', 'red_dta'),
                ('ipt', 'Indiv. Personnes Transportées', 'amt_ipt', 'amt_val_red_ipt', 'red_ipt')
            ]
            
            for code, label, brut_field, net_field, taux_field in garanties:
                if hasattr(old, brut_field):
                    guarantee = VehicleGuarantee(
                        vehicle_id=old.id,
                        code=code,
                        label=label,
                        montant_brut=getattr(old, brut_field, 0),
                        montant_net=getattr(old, net_field, 0),
                        taux=getattr(old, taux_field, 0),
                        is_active=getattr(old, f'check_{code}', False)
                    )
                    session.add(guarantee)
        
        session.commit()
        print("✅ Migration terminée avec succès!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erreur: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    migrate()