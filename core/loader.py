import os
import json
import importlib.util
from core.logger import logger
from core.base_module import BaseModule
import traceback

class AddonLoader:
    def __init__(self, addons_path="addons"):
        self.addons_path = addons_path

    def load_all(self, main_window):
        addons_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "addons")
        logger.info(f"--- DÉBUT DU CHARGEMENT DES MODULES ---")
        logger.info(f"Recherche dans : {addons_path}")

        loaded_instances = [] # <--- Initialisation de la liste à retourner

        if not os.path.exists(addons_path):
            logger.error(f"Le dossier addons n'existe pas : {addons_path}")
            return loaded_instances

        for folder in os.listdir(addons_path):
            folder_path = os.path.join(addons_path, folder)
            
            # On ignore les fichiers et les dossiers de cache
            if not os.path.isdir(folder_path) or folder.startswith("__"):
                continue

            manifest_path = os.path.join(folder_path, "manifest.json")
            if not os.path.exists(manifest_path):
                logger.warning(f"  ! Manquant : manifest.json dans {folder} -> module ignoré")
                continue

            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
            except Exception as e:
                logger.error(f"  ! Impossible de lire manifest.json dans {folder} : {e}")
                continue

            if not manifest.get("enabled", True):
                logger.info(f"  - Module {folder} désactivé dans manifest, passage")
                continue

            if not manifest.get("version"):
                logger.warning(f"  ! module {folder} sans version dans manifest (requis). Ignoré")
                continue

            logger.info(f"Module détecté : [{folder}] version={manifest.get('version')}")
            
            try:
                # 1. Vérification du fichier main_ui.py
                module_file = os.path.join(folder_path, "main_ui.py")
                if not os.path.exists(module_file):
                    logger.warning(f"  ! Manquant : main_ui.py dans {folder}")
                    continue

                # 2. Importation dynamique
                module_name = f"addons.{folder}.main_ui"
                spec = importlib.util.spec_from_file_location(module_name, module_file)
                if spec is None: continue
                
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                logger.info(f"  > Importation réussie : {module_name}")

                # 3. Recherche de la classe qui hérite de BaseModule
                module_found = False
                for name, obj in vars(module).items():
                    if isinstance(obj, type) and issubclass(obj, BaseModule) and obj is not BaseModule:
                        logger.info(f"  > Classe de module valide trouvée : {name}")
                        instance = obj(main_window)
                        
                        # 4. Exécution du setup (Ajout du bouton, etc.)
                        instance.setup() 
                        loaded_instances.append(instance) # <--- On ajoute à la liste
                        module_found = True
                        logger.info(f"  [OK] Module {folder} chargé et initialisé.")
                        break 
                
                if not module_found:
                    logger.warning(f"  ! Aucune classe héritant de BaseModule trouvée dans {folder}")
                                        
            except Exception as e:
                logger.error(f"  [ERREUR] Échec du chargement de {folder} : {str(e)}")
                logger.error(traceback.format_exc())

        logger.info(f"--- FIN DU CHARGEMENT DES MODULES ({len(loaded_instances)} chargés) ---")
        return loaded_instances # <--- TRÈS IMPORTANT : Évite l'erreur 'NoneType' object est pas iterable

    def get_manifest(self, folder_name):
        manifest_path = os.path.join(self.addons_path, folder_name, "manifest.json")
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Manifest non trouvé pour module {folder_name}")
            return None
        except Exception as e:
            logger.error(f"Erreur lecture manifest {folder_name} : {e}")
            return None

    def set_manifest(self, folder_name, data):
        manifest_path = os.path.join(self.addons_path, folder_name, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def enable_module(self, folder_name):
        manifest = self.get_manifest(folder_name)
        if not manifest:
            return False
        manifest["enabled"] = True
        self.set_manifest(folder_name, manifest)
        return True

    def disable_module(self, folder_name):
        manifest = self.get_manifest(folder_name)
        if not manifest:
            return False
        manifest["enabled"] = False
        self.set_manifest(folder_name, manifest)
        return True

    def update_module_version(self, folder_name, new_version):
        manifest = self.get_manifest(folder_name)
        if not manifest:
            return False
        manifest["version"] = str(new_version)
        self.set_manifest(folder_name, manifest)
        return True

    def _load_addon(self, module_name, main_window):
        try:
            # Chercher le manifest.json
            manifest_path = f"addons/{module_name}/manifest.json"
            with open(manifest_path, "r", encoding="utf-8") as f:
                info = json.load(f)

            # Import dynamique du widget principal défini dans le manifest
            # Exemple: "entry_point": "views.main_view.MainWidget"
            module_path, class_name = info['entry_point'].rsplit('.', 1)
            mod = importlib.import_module(f"addons.{module_name}.{module_path}")
            widget_class = getattr(mod, class_name)
            
            # Création de l'objet addon
            class Addon: pass
            a = Addon()
            a.name = info.get("name", module_name)
            a.icon = info.get("icon", "📦")
            a.widget = widget_class(parent=main_window)
            return a
        except Exception as e:
            print(f"Erreur chargement addon {module_name}: {e}")
            return None