import socket
import requests
import logging
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from addons.Automobiles.models.compagnies_models import Compagnie  # Assurez-vous que le chemin est correct
import logging
import pandas as pd
from addons.Automobiles.models.tarif_models import AutomobileTarif  # Assurez-vous du chemin d'import

class CompagnieController:
    def __init__(self, db_session, current_user_id):
        self.db = db_session
        # Accepte soit l'ID utilisateur, soit l'objet User.
        # Dans le second cas, on prend simplement l'attribut .id pour éviter
        # d'essayer d'insérer tout l'objet dans la colonne created_by.
        self.current_user_id = getattr(current_user_id, 'id', current_user_id)
        self.logger = logging.getLogger(__name__)

    def _get_audit_data(self, user_login):
        """
        Méthode privée pour capturer les données système (Audit).
        Cette méthode garantit que l'utilisateur ne peut pas falsifier sa trace.
        """
        local_ip = "127.0.0.1"
        network_ip = "127.0.0.1"
        
        try:
            # Récupération de l'IP Locale
            local_ip = socket.gethostbyname(socket.gethostname())
            # Récupération de l'IP Publique (via API externe avec timeout 1s)
            network_ip = requests.get('https://api.ipify.org', timeout=1).text
        except Exception:
            # En cas d'échec (pas d'internet), on utilise l'IP locale
            network_ip = local_ip

        return {
            "user": user_login,
            "local_ip": local_ip,
            "network_ip": network_ip,
            "now": datetime.now()
        }

    def create_compagnie(self, data, user_id):
        """
        :param data: dict venant de get_data()
        :param user_id: int (ID de l'utilisateur connecté)
        """
        print(user_id)
        try:
            # Récupération des IPs
            local_ip = socket.gethostbyname(socket.gethostname())
            try:
                net_ip = requests.get('https://api.ipify.org', timeout=1).text
            except:
                net_ip = local_ip

            nouvelle_cie = Compagnie(
                **data,  # Injecte nom, code, email, telephone, adresse, num_debut, num_fin
                create_by=user_id,
                modify_by=user_id,
                local_ip=local_ip,
                network_ip=net_ip,
                created_at=datetime.now(),
                modify_at=datetime.now(),
                is_active=True
            )
            
            self.db.add(nouvelle_cie)
            self.db.commit()
            return True, "Enregistré"
        except Exception as e:
            self.db.rollback()
            return False, str(e)
        
    def update_compagnie(self, compagnie_id, form_data, user_login):
        """
        Met à jour une compagnie et trace l'auteur de la modification.
        """
        try:
            cie = self.db.query(Compagnie).filter(Compagnie.id == compagnie_id).first()
            if not cie:
                return False, "Compagnie introuvable."

            audit = self._get_audit_data(user_login)

            # Mise à jour des informations
            cie.nom = form_data.get('nom', cie.nom).upper()
            cie.email = form_data.get('email', cie.email)
            cie.telephone = form_data.get('telephone', cie.telephone)
            cie.adresse = form_data.get('adresse', cie.adresse)
            cie.num_debut = form_data.get('num_debut', cie.num_debut)
            cie.num_fin = form_data.get('num_fin', cie.num_fin)

            # Mise à jour de l'audit de modification
            cie.modify_by = audit['user']
            cie.modify_at = audit['now']
            cie.local_ip = audit['local_ip']
            cie.network_ip = audit['network_ip']

            self.db.commit()
            return True, "Mise à jour effectuée."

        except SQLAlchemyError as e:
            self.db.rollback()
            return False, str(e)

    def delete_compagnie(self, compagnie_id, user_login):
        """
        Suppression logique (is_active = False) avec audit de qui a 'supprimé'.
        """
        try:
            cie = self.db.query(Compagnie).filter(Compagnie.id == compagnie_id).first()
            if not cie:
                return False, "Compagnie introuvable."

            audit = self._get_audit_data(user_login)

            cie.is_active = False
            cie.modify_by = audit['user']
            cie.modify_at = audit['now']
            cie.local_ip = audit['local_ip']
            cie.network_ip = audit['network_ip']

            self.db.commit()
            return True, "Compagnie archivée."
        except SQLAlchemyError as e:
            self.db.rollback()
            return False, str(e)

    def get_active_compagnies(self):
        """Retourne la liste des compagnies non archivées."""
        return self.db.query(Compagnie).filter(Compagnie.is_active == True).order_by(Compagnie.nom).all()
    
    def get_all_active_compagnies(self):
        """Retourne la liste des objets Compagnie actifs."""
        try:
            # Assurez-vous que le nom de la classe est 'Compagnie'
            return self.db.query(Compagnie).filter(Compagnie.is_active == True).all()
        except Exception as e:
            print(f"Erreur DB get_all: {e}")
            return []

    def get_by_id(self, compagnie_id):
        """
        Récupère une compagnie spécifique par son ID.
        """
        try:
            compagnie = self.db.query(Compagnie).filter(Compagnie.id == compagnie_id).first()
            if compagnie:
                # On retourne un dictionnaire pour faciliter le remplissage du formulaire
                return {
                    "id": compagnie.id,
                    "code": compagnie.code,
                    "nom": compagnie.nom,
                    "email": compagnie.email,
                    "telephone": compagnie.telephone,
                    "adresse": compagnie.adresse,
                    "num_debut": compagnie.num_debut,
                    "num_fin": compagnie.num_fin
                }
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération de la compagnie {compagnie_id}: {e}")
            return None
        
    def delete_compagnie_logic(self, compagnie_id, user_id):
        """Désactive une compagnie au lieu de la supprimer."""
        try:
            compagnie = self.db.query(Compagnie).filter(Compagnie.id == compagnie_id).first()
            if not compagnie:
                return False, "Compagnie introuvable."

            compagnie.is_active = False # Elle ne s'affichera plus dans le tableau
            compagnie.modify_by = user_id
            compagnie.modify_at = datetime.now()

            self.db.commit()
            return True, "La compagnie a été désactivée."
        except Exception as e:
            self.db.rollback()
            return False, str(e)
    
    def update_compagnie(self, cie_id, data, user_id):
        try:
            cie = self.db.query(Compagnie).filter(Compagnie.id == cie_id).first()
            if not cie:
                return False, "Compagnie introuvable"

            # Mise à jour des champs
            cie.code = data.get('code', cie.code).upper()
            cie.nom = data.get('nom', cie.nom).upper()
            cie.email = data.get('email', cie.email)
            cie.telephone = data.get('telephone', cie.telephone)
            cie.adresse = data.get('adresse', cie.adresse)
            cie.num_debut = data.get('num_debut', cie.num_debut)
            cie.num_fin = data.get('num_fin', cie.num_fin)
            
            # Audit
            cie.modify_by = user_id
            cie.modify_at = datetime.now()
            # cie.local_ip = ... (récupérer IP comme dans le create)

            self.db.commit()
            return True, "Mise à jour réussie"
        except Exception as e:
            self.db.rollback()
            return False, str(e)


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
            required_columns = [
                "Cie", "Nom_Cie", "Tarif", "Lib_Tarif", "Categorie", "Zone", 
                "Prime1", "Prime2", "Prime3", "Prime4", "Prime5", "Prime6", "Prime7", "Prime8", "Prime9", "Prime10", 
                "Remorq1", "Remorq2", "Remorq3", "Remorq4", "Remorq5", "Remorq6", 
                "Inflamble1", "Inflamble2", 
                "Essence 1", "Essence 2", "Essence 3", "Essence 4", "Essence 5", "Essence 6", "Essence 7", "Essence 8", "Essence 9", "Essence 10", 
                "Diesel 1", "Diesel 2", "Diesel 3", "Diesel 4", "Diesel 5", "Diesel 6", "Diesel 7", "Diesel 8", "Diesel 9", "Diesel 10", 
                "Max Corpo", "Max_Materiel", "Surprime 1", "Nbre Place", "Surprime 2", "LIBELLE OPTION"
            ]            
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
    