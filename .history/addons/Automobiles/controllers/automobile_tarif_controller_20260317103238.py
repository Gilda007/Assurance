import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from addons.Automobiles.models.tarif_models import AutomobileTarif  # Assurez-vous du chemin d'import
from core.alerts import AlertManager

class TarifController:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_all_tarifs(self):
        """Récupère tous les tarifs actifs."""
        return self.db.query(AutomobileTarif).filter(AutomobileTarif.is_active == True).all()

    def get_tarifs_by_compagnie(self, cie_id):
        """Récupère les tarifs d'une compagnie spécifique."""
        return self.db.query(AutomobileTarif).filter(
            AutomobileTarif.cie_id == cie_id,
            AutomobileTarif.is_active == True
        ).all()

    def delete_tarif(self, tarif_id):
        """Suppression logique d'un tarif."""
        tarif = self.db.query(AutomobileTarif).filter(AutomobileTarif.id == tarif_id).first()
        if tarif:
            tarif.is_active = False
            self.db.commit()
            return True, "Tarif supprimé"
        return False, "Tarif non trouvé"

    def import_tarifs_from_file(self, file_path, user_id, progress_callback=None):
        """
        Importation massive avec suivi de progression et validation des colonnes spécifiques.
        """
        try:
            # 1. Lecture du fichier selon l'extension
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                engine = 'xlrd' if file_path.endswith('.xls') else 'openpyxl'
                df = pd.read_excel(file_path, engine=engine)

            # Nettoyage des noms de colonnes
            df.columns = [c.strip() for c in df.columns]
            total_rows = len(df)

            # 2. Validation des colonnes réelles du fichier 'tarif.xls'
            required_columns = ["code",	"Nom",	"Tarif", "Lib_Tarif",	"Categorie",	"Zone	Prime1	Prime2	Prime3	Prime4	Prime5	Prime6	Prime7	Prime8	Prime9	Prime10	Remorq1	Remorq2	Remorq3	Remorq4	Remorq5	Remorq6	Remorq7	Remorq8	Remorq9	Remorq10	Inflamble1	Inflamble2	Inflamble3	Inflamble4	Inflamble5	Inflamble6	Inflamble7	Inflamble8	Inflamble9	Inflamble10	IDTarif	Cat	Type RC	Essence 1	Essence 2	Essence 3	Essence 4	Essence 5	Essence 6	Essence 7	Essence 8	Essence 9	Essence 10	Diesel 1	Diesel 2	Diesel 3	Diesel 4	Diesel 5	Diesel 6	Diesel 7	Diesel 8 	Diesel 9 	Diesel 10	Max Corpo	Max_Materiel	Surprime 1	Nbre Place	Surprime 2	LIBELLE OPTION	Date Création	Initiales Création	Initiales Mise à Jour	Date Mise à Jour	IdTarif]
            for col in required_columns:
                if col not in df.columns:
                    return False, f"La colonne obligatoire '{col}' est manquante dans le fichier."

            success_count = 0
            errors = []

            # Fonctions de nettoyage locales
            def to_f(val):
                try:
                    if pd.isna(val) or str(val).strip() == "": return 0.0
                    return float(str(val).replace(',', '.'))
                except: return 0.0

            def to_i(val):
                try:
                    if pd.isna(val) or str(val).strip() == "": return 0
                    return int(float(val))
                except: return 0

            # 3. Traitement des lignes
            for index, row in df.iterrows():
                try:
                    # Sauter les lignes vides
                    if pd.isna(row.get('Cie')): continue

                    new_tarif = AutomobileTarif(
                        cie_id=to_i(row.get('Cie')),
                        tarif_code=str(row.get('Tarif', '')),
                        lib_tarif=str(row.get('Lib_Tarif', '')),
                        categorie=str(row.get('Categorie', '')),
                        zone=str(row.get('Zone', '')),
                        nbre_place=to_i(row.get('Nbre Place')),
                        libelle_option=str(row.get('LIBELLE OPTION', '')),

                        # PRIMES RC
                        prime1=to_f(row.get('Prime1')), prime2=to_f(row.get('Prime2')),
                        prime3=to_f(row.get('Prime3')), prime4=to_f(row.get('Prime4')),
                        prime5=to_f(row.get('Prime5')), prime6=to_f(row.get('Prime6')),
                        prime7=to_f(row.get('Prime7')), prime8=to_f(row.get('Prime8')),
                        prime9=to_f(row.get('Prime9')), prime10=to_f(row.get('Prime10')),

                        # REMORQUAGE
                        remorq1=to_f(row.get('Remorq1')), remorq2=to_f(row.get('Remorq2')),
                        remorq3=to_f(row.get('Remorq3')), remorq4=to_f(row.get('Remorq4')),
                        remorq5=to_f(row.get('Remorq5')), remorq6=to_f(row.get('Remorq6')),

                        # INFLAMMABLE
                        inflamble1=to_f(row.get('Inflamble1')),
                        inflamble2=to_f(row.get('Inflamble2')),

                        # ÉNERGIE (Mapping exact avec les espaces du CSV)
                        essence_1=to_f(row.get('Essence 1')), essence_2=to_f(row.get('Essence 2')),
                        essence_3=to_f(row.get('Essence 3')), essence_4=to_f(row.get('Essence 4')),
                        essence_5=to_f(row.get('Essence 5')), essence_6=to_f(row.get('Essence 6')),
                        essence_7=to_f(row.get('Essence 7')), essence_8=to_f(row.get('Essence 8')),
                        essence_9=to_f(row.get('Essence 9')), essence_10=to_f(row.get('Essence 10')),

                        diesel_1=to_f(row.get('Diesel 1')), diesel_2=to_f(row.get('Diesel 2')),
                        diesel_3=to_f(row.get('Diesel 3')), diesel_4=to_f(row.get('Diesel 4')),
                        diesel_5=to_f(row.get('Diesel 5')), diesel_6=to_f(row.get('Diesel 6')),
                        diesel_7=to_f(row.get('Diesel 7')), diesel_8=to_f(row.get('Diesel 8')),
                        diesel_9=to_f(row.get('Diesel 9')), diesel_10=to_f(row.get('Diesel 10')),

                        # LIMITES
                        max_corpo=str(row.get('Max Corpo', '')),
                        max_materiel=to_f(row.get('Max_Materiel')),
                        surprime_1=to_f(row.get('Surprime 1')),
                        surprime_2=to_f(row.get('Surprime 2')),

                        create_by=user_id,
                        create_at=datetime.now(),
                        is_active=True
                    )

                    self.db.add(new_tarif)
                    success_count += 1

                    # Mise à jour de la progression (toutes les 20 lignes pour fluidité)
                    if progress_callback and index % 20 == 0:
                        progress_callback(index, total_rows)

                    # Commit par paquets pour la performance
                    if success_count % 200 == 0:
                        self.db.commit()

                except Exception as line_err:
                    errors.append(f"Ligne {index}: {str(line_err)}")
                    continue

            self.db.commit()
            return True, f"{success_count} tarifs importés avec succès."

        except Exception as e:
            self.db.rollback()
            return False, f"Erreur critique : {str(e)}"