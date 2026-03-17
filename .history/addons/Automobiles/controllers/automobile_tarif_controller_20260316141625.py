import logging

class AutomobileTarifController:
    def __init__(self, main_controller):
        self.main = main_controller
        self.db = main_controller.db  # Référence à votre session DB
        self.logger = logging.getLogger("AMS_Project")

    def create_tarif(self, form_data):
        """
        Prend le dictionnaire de 62 champs et l'insère en base de données.
        """
        try:
            # 1. Nettoyage et Conversion des types
            processed_data = self._prepare_data_for_db(form_data)
            
            # 2. Appel au modèle (SQLAlchemy ou autre)
            # Exemple : new_record = AutomobileTarif(**processed_data)
            # self.db.add(new_record)
            # self.db.commit()
            
            print(f"DEBUG: Sauvegarde du barème {processed_data.get('Lib_Tarif')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la création du tarif: {str(e)}")
            return False

    def _prepare_data_for_db(self, data):
        """
        Convertit les valeurs du formulaire (strings) en formats acceptés par la DB 
        (Float pour les primes, Int pour les places, etc.)
        """
        clean_data = {}
        
        # Liste des champs qui doivent être convertis en FLOAT
        # On utilise une compréhension de liste pour les séries 1 à 10
        fields_to_float = [
            "Max_Materiel", "Surprime 1", "Surprime 2"
        ]
        for i in range(1, 11):
            fields_to_float.extend([
                f"Prime{i}", f"Remorq{i}", f"Inflamble{i}", 
                f"Essence {i}", f"Diesel {i}"
            ])

        for key, value in data.items():
            if key in fields_to_float:
                try:
                    # Conversion sécurisée en float
                    clean_data[key] = float(value) if value else 0.0
                except ValueError:
                    clean_data[key] = 0.0
            elif key == "Nbre Place":
                try:
                    clean_data[key] = int(value) if value else 0
                except ValueError:
                    clean_data[key] = 0
            else:
                # Champs texte (Cie, Lib_Tarif, etc.)
                clean_data[key] = value.upper() if value else ""
                
        return clean_data

    def get_all_tarifs(self):
        """Récupère la liste des barèmes pour l'affichage"""
        # return self.db.query(AutomobileTarif).all()
        pass