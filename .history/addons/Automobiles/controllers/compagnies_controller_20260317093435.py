import socket
import requests
import logging
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from addons.Automobiles.models.compagnies_models import Compagnie  # Assurez-vous que le chemin est correct
import logging
import pandas as pd

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


    def import_from_excel(self, file_path, user_id):
        try:
            # Lecture du fichier
            df = pd.read_excel(file_path)
            
            # Vérification des colonnes minimales requises
            required_columns = ['code', 'nom']
            for col in required_columns:
                if col not in df.columns:
                    return False, f"La colonne '{col}' est manquante dans le fichier."

            success_count = 0
            for _, row in df.iterrows():
                # On prépare les données (gestion des valeurs vides)
                data = {
                    'code': str(row['code']).strip(),
                    'nom': str(row['nom']).strip(),
                    'email': str(row.get('email', '')),
                    'telephone': str(row.get('telephone', '')),
                    'adresse': str(row.get('adresse', '')),
                    'num_debut': str(row.get('num_debut', '')),
                    'num_fin': str(row.get('num_fin', ''))
                }

                # Vérifier si la compagnie existe déjà
                existing = self.db.query(Compagnie).filter(Compagnie.code == data['code']).first()
                if not existing:
                    self.create_compagnie(data, user_id)
                    success_count += 1
            
            return True, f"{success_count} compagnies importées avec succès."
        except Exception as e:
            return False, f"Erreur lors de la lecture : {str(e)}"

    def import_tarifs_full(self, file_path, user_id):
        try:
            # 1. Lecture du fichier (Gestion CSV car le fichier fourni est un CSV)
            df = pd.read_csv(file_path)
            
            # Nettoyage des colonnes : on enlève les espaces en début/fin
            df.columns = [c.strip() for c in df.columns]

            success_count = 0
            
            for _, row in df.iterrows():
                # Fonction utilitaire pour convertir en float ou 0.0 si vide/NaN
                def clean_f(val):
                    try:
                        return float(val) if pd.notna(val) else 0.0
                    except: return 0.0

                # Création de l'instance selon votre modèle tarif_models.py
                new_tarif = AutomobileTarif(
                    cie_id=int(row['Cie']),
                    tarif_code=str(row['Tarif']),
                    lib_tarif=str(row['Lib_Tarif']),
                    categorie=str(row['Categorie']),
                    zone=str(row['Zone']),
                    nbre_place=int(clean_f(row.get('Nbre Place', 0))),
                    libelle_option=str(row.get('LIBELLE OPTION', '')),

                    # --- PRIMES RC ---
                    prime1=clean_f(row['Prime1']), prime2=clean_f(row['Prime2']),
                    prime3=clean_f(row['Prime3']), prime4=clean_f(row['Prime4']),
                    prime5=clean_f(row['Prime5']), prime6=clean_f(row['Prime6']),
                    prime7=clean_f(row['Prime7']), prime8=clean_f(row['Prime8']),
                    prime9=clean_f(row['Prime9']), prime10=clean_f(row['Prime10']),

                    # --- REMORQUAGE ---
                    remorq1=clean_f(row.get('Remorq1')), remorq2=clean_f(row.get('Remorq2')),
                    remorq3=clean_f(row.get('Remorq3')), remorq4=clean_f(row.get('Remorq4')),
                    remorq5=clean_f(row.get('Remorq5')), remorq6=clean_f(row.get('Remorq6')),

                    # --- INFLAMMABLE ---
                    inflamble1=clean_f(row.get('Inflamble1')), inflamble2=clean_f(row.get('Inflamble2')),

                    # --- ÉNERGIE ---
                    essence_1=clean_f(row.get('Essence 1')), essence_2=clean_f(row.get('Essence 2')),
                    diesel_1=clean_f(row.get('Diesel 1')), diesel_2=clean_f(row.get('Diesel 2')),
                    # ... continuez pour les autres indices essence/diesel si nécessaire ...

                    # --- LIMITES ---
                    max_corpo=str(row.get('Max Corpo', '')),
                    max_materiel=clean_f(row.get('Max_Materiel')),
                    surprime_1=clean_f(row.get('Surprime 1')),
                    surprime_2=clean_f(row.get('Surprime 2')),

                    # --- AUDIT ---
                    create_by=user_id,
                    create_at=datetime.now(),
                    is_active=True
                )

                self.db.add(new_tarif)
                success_count += 1
                
                # Performance : commit toutes les 200 lignes
                if success_count % 200 == 0:
                    self.db.commit()

            self.db.commit()
            return True, f"Importation réussie : {success_count} tarifs ajoutés."

        except Exception as e:
            self.db.rollback()
            return False, f"Erreur lors de l'import : {str(e)}"