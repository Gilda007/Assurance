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

    # def import_tarifs_from_file(self, file_path, user_id, progress_callback=None):
    #     try:
    #         # 1. Toujours commencer par un rollback de sécurité au cas où une erreur précédente bloque la session
    #         self.db.rollback()

    #         if file_path.endswith('.csv'):
    #             df = pd.read_csv(file_path)
    #         else:
    #             engine = 'xlrd' if file_path.endswith('.xls') else 'openpyxl'
    #             df = pd.read_excel(file_path, engine=engine)

    #         success_count = 0

    #         # À mettre juste avant la boucle for
    #         def to_f(val):
    #             try:
    #                 if pd.isna(val) or str(val).strip() == "": return 0.0
    #                 return float(str(val).replace(',', '.').replace(' ', ''))
    #             except: return 0.0

    #         def to_i(val):
    #             try:
    #                 if pd.isna(val) or str(val).strip() == "": return 0
    #                 return int(float(val))
    #             except: return 0

    #         for index, row in df.iterrows():
    #             try:
    #                 # RÉCUPÉRATION DE L'ID CIE
    #                 val_cie = row.get('Cie')
    #                 # Si c'est vide ou NaN, on met 0
    #                 cie_id = int(float(val_cie)) if pd.notna(val_cie) and str(val_cie).strip() != "" else 0

    #                 # --- CONDITION CRITIQUE ---
    #                 # Si l'ID est 0, on ignore cette ligne car elle fera planter la base de données
    #                 if cie_id == 0:
    #                     print(f">>> DEBUG: Ligne {index} ignorée (ID Compagnie est 0 ou vide)")
    #                     continue

    #                 new_tarif = AutomobileTarif(
    #                     # --- Identification ---
    #                     cie_id=cie_id,
    #                     tarif_code=str(row.get('Tarif', '')),
    #                     lib_tarif=str(row.get('Lib_Tarif', 'Inconnu')),
    #                     categorie=str(row.get('Categorie', '')),
    #                     zone=str(row.get('Zone', '')),
    #                     nbre_place=to_i(row.get('Nbre Place', 0)),
    #                     libelle_option=str(row.get('Libelle_Option', '')),

    #                     # --- Primes RC (1 à 10) ---
    #                     prime1=to_f(row.get('Prime1')),
    #                     prime2=to_f(row.get('Prime2')),
    #                     prime3=to_f(row.get('Prime3')),
    #                     prime4=to_f(row.get('Prime4')),
    #                     prime5=to_f(row.get('Prime5')),
    #                     prime6=to_f(row.get('Prime6')),
    #                     prime7=to_f(row.get('Prime7')),
    #                     prime8=to_f(row.get('Prime8')),
    #                     prime9=to_f(row.get('Prime9')),
    #                     prime10=to_f(row.get('Prime10')),

    #                     # --- Énergie Essence (1 à 10) ---
    #                     essence_1=to_f(row.get('Essence 1')),
    #                     essence_2=to_f(row.get('Essence 2')),
    #                     essence_3=to_f(row.get('Essence 3')),
    #                     essence_4=to_f(row.get('Essence 4')),
    #                     essence_5=to_f(row.get('Essence 5')),
    #                     essence_6=to_f(row.get('Essence 6')),
    #                     essence_7=to_f(row.get('Essence 7')),
    #                     essence_8=to_f(row.get('Essence 8')),
    #                     essence_9=to_f(row.get('Essence 9')),
    #                     essence_10=to_f(row.get('Essence 10')),

    #                     # --- Énergie Diesel (1 à 10) ---
    #                     diesel_1=to_f(row.get('Diesel 1')),
    #                     diesel_2=to_f(row.get('Diesel 2')),
    #                     diesel_3=to_f(row.get('Diesel 3')),
    #                     diesel_4=to_f(row.get('Diesel 4')),
    #                     diesel_5=to_f(row.get('Diesel 5')),
    #                     diesel_6=to_f(row.get('Diesel 6')),
    #                     diesel_7=to_f(row.get('Diesel 7')),
    #                     diesel_8=to_f(row.get('Diesel 8')),
    #                     diesel_9=to_f(row.get('Diesel 9')),
    #                     diesel_10=to_f(row.get('Diesel 10')),

    #                     # --- Remorquage (1 à 10) ---
    #                     remorq1=to_f(row.get('Remorq1')),
    #                     remorq2=to_f(row.get('Remorq2')),
    #                     remorq3=to_f(row.get('Remorq3')),
    #                     remorq4=to_f(row.get('Remorq4')),
    #                     remorq5=to_f(row.get('Remorq5')),
    #                     remorq6=to_f(row.get('Remorq6')),
    #                     remorq7=to_f(row.get('Remorq7')),
    #                     remorq8=to_f(row.get('Remorq8')),
    #                     remorq9=to_f(row.get('Remorq9')),
    #                     remorq10=to_f(row.get('Remorq10')),

    #                     # --- Limites et Garanties ---
    #                     max_corpo=str(row.get('Max Corpo', '')),
    #                     max_materiel=to_f(row.get('Max_Materiel')),
                        
    #                     # --- Métadonnées (Vérifiez bien ces noms dans votre modèle) ---
    #                     created_by=user_id,
    #                     created_at=datetime.now(),
    #                     is_active=True
    #                 )

    #                 self.db.add(new_tarif)
    #                 success_count += 1

    #                 if progress_callback:
    #                     progress_callback(index + 1, len(df))

    #                 # On commit par petits paquets
    #                 if success_count % 50 == 0:
    #                     self.db.commit()

    #             except Exception as line_err:
    #                 print(f">>> DEBUG: Erreur ligne {index}: {line_err}")
    #                 self.db.rollback() # Important pour continuer après une erreur de ligne
    #                 continue

    #         self.db.commit()
    #         return True, f"Importation terminée : {success_count} tarifs ajoutés."

    #     except Exception as e:
    #         self.db.rollback()
    #         print(f">>> DEBUG: ERREUR GÉNÉRALE: {e}")
    #         return False, f"Erreur d'import: {str(e)}"
        
    def import_tarifs_from_file(self, file_path, user_id, progress_callback=None):
        try:
            self.db.rollback() # Nettoyage de sécurité

            # 1. Récupérer tous les IDs de compagnies existants
            # On utilise un set() pour une recherche instantanée (O(1))
            from addons.Automobiles.models.compagnies_models import Compagnie # Assurez-vous d'importer votre modèle Compagnie
            valid_cie_ids = {c.id for c in self.db.query(Compagnie.id).all()}
            
            print(f">>> DEBUG: {len(valid_cie_ids)} compagnies trouvées en base.")

            # 2. Lecture du fichier
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                engine = 'xlrd' if file_path.endswith('.xls') else 'openpyxl'
                df = pd.read_excel(file_path, engine=engine)

            success_count = 0
            ignored_count = 0

            # Fonctions utilitaires de conversion
            def to_f(val):
                try:
                    if pd.isna(val) or str(val).strip() == "": return 0.0
                    return float(str(val).replace(',', '.').replace(' ', ''))
                except: return 0.0

            def to_i(val):
                try:
                    if pd.isna(val) or str(val).strip() == "": return 0
                    return int(float(val))
                except: return 0

            # 3. Boucle de traitement
            for index, row in df.iterrows():
                try:
                    cie_id = to_i(row.get('Cie'))

                    # --- LA VÉRIFICATION CRITIQUE ---
                    if cie_id not in valid_cie_ids:
                        print(f">>> Ligne {index} ignorée : La compagnie ID {cie_id} n'existe pas en base.")
                        ignored_count += 1
                        continue 

                    # 4. Création de l'objet complet
                    new_tarif = AutomobileTarif(
                        cie_id=cie_id,
                        tarif_code=str(row.get('Tarif', '')),
                        lib_tarif=str(row.get('Lib_Tarif', 'Inconnu')),
                        categorie=str(row.get('Categorie', '')),
                        zone=str(row.get('Zone', '')),
                        nbre_place=to_i(row.get('Nbre Place', 0)),
                        
                        # Primes RC
                        prime1=to_f(row.get('Prime1')), prime2=to_f(row.get('Prime2')),
                        prime3=to_f(row.get('Prime3')), prime4=to_f(row.get('Prime4')),
                        prime5=to_f(row.get('Prime5')), prime6=to_f(row.get('Prime6')),
                        prime7=to_f(row.get('Prime7')), prime8=to_f(row.get('Prime8')),
                        prime9=to_f(row.get('Prime9')), prime10=to_f(row.get('Prime10')),

                        # Énergie Essence
                        essence_1=to_f(row.get('Essence 1')), essence_2=to_f(row.get('Essence 2')),
                        essence_3=to_f(row.get('Essence 3')), essence_4=to_f(row.get('Essence 4')),
                        essence_5=to_f(row.get('Essence 5')), essence_6=to_f(row.get('Essence 6')),
                        essence_7=to_f(row.get('Essence 7')), essence_8=to_f(row.get('Essence 8')),
                        essence_9=to_f(row.get('Essence 9')), essence_10=to_f(row.get('Essence 10')),

                        # Énergie Diesel
                        diesel_1=to_f(row.get('Diesel 1')), diesel_2=to_f(row.get('Diesel 2')),
                        diesel_3=to_f(row.get('Diesel 3')), diesel_4=to_f(row.get('Diesel 4')),
                        diesel_5=to_f(row.get('Diesel 5')), diesel_6=to_f(row.get('Diesel 6')),
                        diesel_7=to_f(row.get('Diesel 7')), diesel_8=to_f(row.get('Diesel 8')),
                        diesel_9=to_f(row.get('Diesel 9')), diesel_10=to_f(row.get('Diesel 10')),

                        # Remorquage
                        remorq1=to_f(row.get('Remorq1')), remorq2=to_f(row.get('Remorq2')),
                        remorq3=to_f(row.get('Remorq3')), remorq4=to_f(row.get('Remorq4')),
                        remorq5=to_f(row.get('Remorq5')), remorq6=to_f(row.get('Remorq6')),
                        remorq7=to_f(row.get('Remorq7')), remorq8=to_f(row.get('Remorq8')),
                        remorq9=to_f(row.get('Remorq9')), remorq10=to_f(row.get('Remorq10')),

                        max_corpo=str(row.get('Max Corpo', '')),
                        max_materiel=to_f(row.get('Max_Materiel')),
                        
                        created_by=user_id,
                        created_at=datetime.now(),
                        is_active=True
                    )

                    self.db.add(new_tarif)
                    success_count += 1

                    if progress_callback and success_count % 10 == 0:
                        progress_callback(index + 1, len(df))

                    if success_count % 100 == 0:
                        self.db.commit()

                except Exception as line_err:
                    print(f"Erreur ligne {index}: {line_err}")
                    self.db.rollback()
                    continue

            self.db.commit()
            msg = f"{success_count} tarifs importés. {ignored_count} lignes ignorées (Cie inexistante)."
            return True, msg

        except Exception as e:
            self.db.rollback()
            return False, f"Erreur critique : {str(e)}"

