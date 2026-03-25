import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from addons.Automobiles.models.tarif_models import AutomobileTarif  # Assurez-vous du chemin d'import
from core.alerts import AlertManager
from addons.Automobiles.models import Compagnie

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
        try:
            self.db.rollback() 

            # --- 1. FONCTIONS UTILITAIRES (DÉPLACÉES EN HAUT) ---
            def to_f(val):
                try:
                    if pd.isna(val) or str(val).strip() == "": return 0.0
                    return float(str(val).replace(',', '.').replace(' ', ''))
                except: return 0.0

            def to_i(val):
                try:
                    if pd.isna(val) or str(val).strip() == "": return 0
                    # On gère le cas où Excel lit "1.0" pour un entier 1
                    return int(float(str(val).strip()))
                except: return 0

            # --- 2. PRÉPARATION DU MAPPING ---
            # On stocke les codes en STRING MAJUSCULE pour la comparaison
            cie_map = {str(c.code).strip().upper(): c.id for c in self.db.query(Compagnie.id, Compagnie.code).all()}
            
            # --- 3. LECTURE ET NORMALISATION ---
            df = pd.read_excel(file_path) if not file_path.endswith('.csv') else pd.read_csv(file_path)
            df.columns = [str(c).strip().upper() for c in df.columns]

            success_count = 0
            ignored_count = 0
            total_rows = len(df) # On stocke le total pour le callback

            # --- 4. BOUCLE DE TRAITEMENT ---
            for index, row in df.iterrows():
                try:
                    # 1. Récupération du code (ex: "1" ou "AXA")
                    raw_code = row.get('CODE')
                    if pd.isna(raw_code):
                        ignored_count += 1
                        continue
                    
                    code_excel = str(raw_code).split('.')[0].strip().upper()
                    
                    # 2. VÉRIFICATION DE LA CLÉ ÉTRANGÈRE
                    if code_excel not in cie_map:
                        print(f"⚠️ Ligne {index} ignorée : Compagnie '{code_excel}' inexistante.")
                        ignored_count += 1
                        continue 

                    actual_cie_id = cie_map[code_excel]

                    # INSERTION DANS LE MODÈLE (Note : Clés de row.get en MAJUSCULES)
                    new_tarif = AutomobileTarif(
                        cie_id=actual_cie_id,  # <--- CORRIGÉ : On utilise l'ID validé
                        tarif_code=str(row.get('TARIF', '')),
                        lib_tarif=str(row.get('LIB_TARIF', 'Inconnu')),
                        categorie=str(row.get('CATEGORIE', '')),
                        zone=str(row.get('ZONE', '')),
                        nbre_place=to_i(row.get('NBRE PLACE', 0)),
                        
                        # Primes RC (Mapping en majuscules)
                        prime1=to_f(row.get('PRIME1')), prime2=to_f(row.get('PRIME2')),
                        prime3=to_f(row.get('PRIME3')), prime4=to_f(row.get('PRIME4')),
                        prime5=to_f(row.get('PRIME5')), prime6=to_f(row.get('PRIME6')),
                        prime7=to_f(row.get('PRIME7')), prime8=to_f(row.get('PRIME8')),
                        prime9=to_f(row.get('PRIME9')), prime10=to_f(row.get('PRIME10')),

                        # Énergie Essence
                        essence_1=to_f(row.get('ESSENCE 1')), essence_2=to_f(row.get('ESSENCE 2')),
                        essence_3=to_f(row.get('ESSENCE 3')), essence_4=to_f(row.get('ESSENCE 4')),
                        essence_5=to_f(row.get('ESSENCE 5')), essence_6=to_f(row.get('ESSENCE 6')),
                        essence_7=to_f(row.get('ESSENCE 7')), essence_8=to_f(row.get('ESSENCE 8')),
                        essence_9=to_f(row.get('ESSENCE 9')), essence_10=to_f(row.get('ESSENCE 10')),

                        # Énergie Diesel
                        diesel_1=to_f(row.get('DIESEL 1')), diesel_2=to_f(row.get('DIESEL 2')),
                        diesel_3=to_f(row.get('DIESEL 3')), diesel_4=to_f(row.get('DIESEL 4')),
                        diesel_5=to_f(row.get('DIESEL 5')), diesel_6=to_f(row.get('DIESEL 6')),
                        diesel_7=to_f(row.get('DIESEL 7')), diesel_8=to_f(row.get('DIESEL 8')),
                        diesel_9=to_f(row.get('DIESEL 9')), diesel_10=to_f(row.get('DIESEL 10')),

                        # Remorquage
                        remorq1=to_f(row.get('REMORQ1')), remorq2=to_f(row.get('REMORQ2')),
                        remorq3=to_f(row.get('REMORQ3')), remorq4=to_f(row.get('REMORQ4')),
                        remorq5=to_f(row.get('REMORQ5')), remorq6=to_f(row.get('REMORQ6')),
                        remorq7=to_f(row.get('REMORQ7')), remorq8=to_f(row.get('REMORQ8')),
                        remorq9=to_f(row.get('REMORQ9')), remorq10=to_f(row.get('REMORQ10')),

                        max_corpo=str(row.get('MAX CORPO', '')),
                        max_materiel=to_f(row.get('MAX_MATERIEL')),
                        
                        created_by=user_id,
                        created_at=datetime.now(),
                        is_active=True
                    )

                    self.db.add(new_tarif)
                    success_count += 1
                    current_row = index + 1
                    if progress_callback:
                        # On met à jour toutes les 10 lignes OU si c'est la fin du fichier
                        if success_count % 10 == 0 or current_row == total_rows:
                            progress_callback(current_row, total_rows)

                    if success_count % 100 == 0:
                        self.db.commit()

                except Exception as line_err:
                    print(f"❌ Erreur ligne {index}: {line_err}")
                    self.db.rollback()
                    continue

            self.db.commit()
            return True, f"{success_count} tarifs importés. {ignored_count} ignorés."

        except Exception as e:
            self.db.rollback()
            return False, f"Erreur critique : {str(e)}"

    def get_premium(self, cie_id, zone, categorie, chevaux, energie):
        """
        Recherche la prime RC correspondante dans la matrice
        :param energie: 'ESSENCE' ou 'DIESEL'
        """
        # 1. On récupère le tarif qui correspond aux critères fixes
        tarif = self.db.query(AutomobileTarif).filter(
            AutomobileTarif.cie_id == cie_id,
            AutomobileTarif.zone == zone,
            AutomobileTarif.categorie == categorie,
            AutomobileTarif.is_active == True
        ).first()

        if not tarif:
            return 0.0, "Aucun tarif trouvé pour ces critères"

        # 2. Détermination de la colonne en fonction des chevaux (Matrix Mapping)
        # On limite à 10 car votre modèle s'arrête à essence_10 / diesel_10
        index = min(max(int(chevaux), 1), 10) 
        
        # Dynamiquement, on va chercher l'attribut (ex: essence_5)
        field_name = f"{energie.lower()}_{index}"
        premium = getattr(tarif, field_name, 0.0)

        return premium, None
    
    def get_rc_premium(self, cie_id, zone, categorie, energie, cv):
        """
        Récupère la prime RC exacte en fonction de la matrice.
        """
        try:
            # 1. Normalisation des entrées
            # On s'assure que l'ID est un entier pour éviter l'erreur SQL précédente
            cie_id = int(cie_id) 
            cv = int(cv)
            
            # 2. Détermination de la colonne cible (Mapping Matriciel)
            # On plafonne entre 1 et 10 selon votre structure de table
            index = min(max(cv, 1), 10)
            # 'Essence' -> 'essence_7' | 'Diesel' -> 'diesel_7'
            colonne_nom = f"{energie.lower()}_{index}"

            # 3. Requête SQLAlchemy
            tarif = self.db.query(AutomobileTarif).filter(
                AutomobileTarif.cie_id == cie_id,
                AutomobileTarif.zone == str(zone).strip().upper(),
                AutomobileTarif.categorie == str(categorie).strip(),
                AutomobileTarif.is_active == True
            ).first()

            if not tarif:
                return 0.0, "Aucun tarif correspondant trouvé."

            # 4. Récupération dynamique de la valeur de la colonne
            montant = getattr(tarif, colonne_nom, 0.0)
            return montant, None

        except Exception as e:
            return 0.0, f"Erreur de mapping : {str(e)}"
     
    def create_tarif(self, data):
        """
        Crée un nouveau tarif automobile en base de données.
        'data' est un dictionnaire contenant les valeurs du formulaire.
        """
        try:
            # On crée l'instance du modèle avec les données reçues
            new_tarif = AutomobileTarif(**data)
            
            # Ajout à la session et sauvegarde
            self.db.add(new_tarif)
            self.db.commit()
            self.db.refresh(new_tarif) # Pour récupérer l'ID généré
            
            return True, "Tarif créé avec succès."
        except Exception as e:
            self.db.rollback()
            print(f"Erreur lors de la création du tarif : {e}")
            return False, str(e)