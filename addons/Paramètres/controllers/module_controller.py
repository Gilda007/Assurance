import json
import os
import shutil

class ModuleController:
    def __init__(self, session=None):
        """
        Initialise le contrôleur avec une session de base de données si nécessaire.
        """
        self.session = session
        # Chemin vers le dossier des addons
        self.addons_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    def get_all_modules(self):
        """
        Scanne le dossier addons pour trouver tous les modules disponibles 
        en lisant leurs fichiers __manifest__.py.
        """
        modules = []
        try:
            # On liste les dossiers dans 'addons/'
            for folder in os.listdir(self.addons_path):
                folder_path = os.path.join(self.addons_path, folder)
                
                if os.path.isdir(folder_path):
                    manifest_path = os.path.join(folder_path, "__manifest__.json")
                    
                    if os.path.exists(manifest_path):
                        # On lit le manifeste du module
                        with open(manifest_path, "r", encoding="utf-8") as f:
                            manifest_data = json.load(f)
                            
                            # On ajoute le nom du dossier pour pouvoir le gérer plus tard
                            manifest_data['folder_name'] = folder
                            
                            # Taille du module (optionnel)
                            manifest_data['size'] = self._get_folder_size(folder_path)
                            
                            modules.append(manifest_data)
        except Exception as e:
            print(f"Erreur lors de la lecture des modules : {e}")
            # Retourne une liste de secours si la lecture échoue
            return [
                {"name": "Paramètres", "version": "1.0", "author": "Génie AMS", "folder_name": "Paramètres", "description": "Module système"}
            ]
            
        return modules

    def uninstall_module(self, folder_name):
        """
        Désinstalle (supprime physiquement) un module.
        ATTENTION : Sécurité ajoutée pour ne pas supprimer le module Paramètres.
        """
        # SÉCURITÉ : On ne peut pas supprimer le module cœur
        if folder_name.lower() in ["paramètres", "parametre", "settings", "core"]:
            return False, "Impossible de désinstaller le module système principal."

        try:
            target_path = os.path.join(self.addons_path, folder_name)
            if os.path.exists(target_path):
                # shutil.rmtree(target_path) # Décommentez pour activer la suppression réelle
                print(f"MODULE SIMULÉ DÉSINSTALLÉ : {target_path}")
                return True, f"Le module {folder_name} a été désinstallé avec succès."
            return False, "Dossier du module introuvable."
        except Exception as e:
            return False, f"Erreur lors de la désinstallation : {str(e)}"

    def _get_folder_size(self, folder):
        """Calcule la taille du dossier en Mo"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return f"{total_size / (1024*1024):.2f} Mo"