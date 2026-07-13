import os
import json
import importlib.util
from core.logger import logger
from core.base_module import BaseModule
import traceback
from datetime import datetime

try:
    from lometa_module_generator.certificate_manager import CertificateManager
    CERT_MANAGER_AVAILABLE = True
except ImportError:
    CERT_MANAGER_AVAILABLE = False

class AddonLoader:
    def __init__(self, addons_path="addons"):
        self.addons_path = addons_path
        self.cert_manager = CertificateManager() if CERT_MANAGER_AVAILABLE else None

    def load_all(self, main_window):
        addons_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "addons")
        logger.info(f"--- DÉBUT DU CHARGEMENT DES MODULES ---")
        logger.info(f"Recherche dans : {addons_path}")

        loaded_instances = []

        if not os.path.exists(addons_path):
            logger.error(f"Le dossier addons n'existe pas : {addons_path}")
            return loaded_instances

        for folder in os.listdir(addons_path):
            folder_path = os.path.join(addons_path, folder)
            
            if not os.path.isdir(folder_path) or folder.startswith("__"):
                continue

            manifest_path = os.path.join(folder_path, "manifest.json")
            if not os.path.exists(manifest_path):
                logger.warning(f"  ! Manquant : manifest.json dans {folder} -> module ignoré")
                continue

            certificate_path = os.path.join(folder_path, "certificate.json")
            if not os.path.exists(certificate_path):
                logger.warning(f"le module {folder} n'a pas de certificat (certificate.json). Il est recommandé d'en avoir un pour la sécurité.")
                logger.warning(f"  ! Manquant : certificate.json dans {folder} -> module ignoré")
                continue

            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
            except Exception as e:
                logger.error(f"  ! Impossible de lire manifest.json dans {folder} : {e}")
                continue

            try:
                with open(certificate_path, "r", encoding="utf-8") as f:
                    certificate = json.load(f)
            except Exception as e:
                logger.error(f"  ! Impossible de lire certificate.json dans {folder} : {e}")
                continue

            if not manifest.get("enabled", True):
                logger.info(f"  - Module {folder} désactivé dans manifest, passage")
                continue

            if self.cert_manager:
                success, message = self.cert_manager.verify_module(folder_path)
                if not success:
                    logger.warning(f"  ! {message} -> module ignoré")
                    continue
                else:
                    logger.info(f"  ✅ {message}")
            else:
                # Fallback: vérifications manuelles basiques
                required_fields = ["module_name", "module_version", "certificate_id", "signature"]
                valid = True
                for field in required_fields:
                    if field not in certificate:
                        logger.warning(f"  ! Champ '{field}' manquant dans certificate.json -> module ignoré")
                        valid = False
                        break
                if not valid:
                    continue
                
                if certificate.get("module_name") != manifest.get("name", folder):
                    logger.warning(f"  ! Nom du module ne correspond pas -> module ignoré")
                    continue
                
                logger.info(f"  ✅ Vérification manuelle: module {folder} valide")

            # ============================================================
            #  VÉRIFICATIONS DU CERTIFICAT
            # ============================================================
            
            # 1. Vérification de la structure du certificat
            required_cert_fields = [
                "version", "module_name", "module_version", 
                "certified_by", "certified_date", "certificate_id",
                "checksums", "signature", "public_key"
            ]
            
            cert_valid = True
            for field in required_cert_fields:
                if field not in certificate:
                    logger.warning(f"  ! Champ '{field}' manquant dans certificate.json du module {folder} -> module ignoré")
                    cert_valid = False
                    break
            
            if not cert_valid:
                continue
            
            # 2. Vérification que le nom du module correspond
            if certificate.get("module_name") != manifest.get("name", folder):
                logger.warning(f"  ! Nom du module dans certificat '{certificate.get('module_name')}' ne correspond pas au manifest '{manifest.get('name', folder)}' -> module ignoré")
                continue
            
            # 3. Vérification de la version
            if certificate.get("module_version") != manifest.get("version"):
                logger.warning(f"  ! Version du certificat '{certificate.get('module_version')}' ne correspond pas au manifest '{manifest.get('version')}' -> module ignoré")
                continue
            
            # 4. Vérification de la date de certification
            try:
                cert_date = datetime.fromisoformat(certificate.get("certified_date"))
                if cert_date > datetime.now():
                    logger.warning(f"  ! Certificat du module {folder} avec date future ({certificate.get('certified_date')}) -> module ignoré")
                    continue
            except (ValueError, TypeError):
                logger.warning(f"  ! Date de certification invalide dans le module {folder} -> module ignoré")
                continue
            
            # 5. Vérification que checksums est un dictionnaire
            if not isinstance(certificate.get("checksums"), dict):
                logger.warning(f"  ! Le champ 'checksums' doit être un dictionnaire dans le module {folder} -> module ignoré")
                continue
            
            # 6. Vérification de la signature
            signature = certificate.get("signature", "")
            if not signature or len(signature) < 32:
                logger.warning(f"  ! Signature invalide dans le module {folder} -> module ignoré")
                continue
            
            # 7. Vérification de la clé publique
            public_key = certificate.get("public_key", "")
            if not public_key or len(public_key) < 32:
                logger.warning(f"  ! Clé publique invalide dans le module {folder} -> module ignoré")
                continue
            
            # 8. Vérification que le certificat n'a pas été révoqué (si vous avez une liste de révocation)
            # revoked_certificates = self.get_revoked_certificates()  # À implémenter
            # if certificate.get("certificate_id") in revoked_certificates:
            #     logger.warning(f"  ! Certificat révoqué pour le module {folder} -> module ignoré")
            #     continue
            
            # 9. Vérification des checksums des fichiers
            # (Optionnel - vérifier que les fichiers du module correspondent aux checksums)
            # logger.info(f"  > Vérification des checksums pour le module {folder}...")
            # for file_path, checksum in certificate.get("checksums", {}).items():
            #     full_path = os.path.join(folder_path, file_path)
            #     if not os.path.exists(full_path):
            #         logger.warning(f"    ! Fichier manquant: {file_path}")
            #         continue
            #     # Calculer le checksum du fichier et comparer
            #     # ...
            
            # 10. Vérification que le certificat est valide (certificate.json contient "valid": True)
            if not certificate.get("valid", True):
                logger.warning(f"  ! Certificat du module {folder} marqué comme invalide (valid: false) -> module ignoré")
                continue
            
            # ============================================================
            #  FIN DES VÉRIFICATIONS DU CERTIFICAT
            # ============================================================

            if not manifest.get("version"):
                logger.warning(f"  ! module {folder} sans version dans manifest (requis). Ignoré")
                continue

            logger.info(f"✅ Module certifié : [{folder}] version={manifest.get('version')}")
            logger.info(f"   Certifié par: {certificate.get('certified_by')}")
            logger.info(f"   ID: {certificate.get('certificate_id')}")
            
            try:
                module_file = os.path.join(folder_path, "main_ui.py")
                if not os.path.exists(module_file):
                    logger.warning(f"  ! Manquant : main_ui.py dans {folder}")
                    continue

                module_name = f"addons.{folder}.main_ui"
                spec = importlib.util.spec_from_file_location(module_name, module_file)
                if spec is None:
                    continue
                
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                logger.info(f"  > Importation réussie : {module_name}")

                module_found = False
                for name, obj in vars(module).items():
                    if isinstance(obj, type) and issubclass(obj, BaseModule) and obj is not BaseModule:
                        logger.info(f"  > Classe de module valide trouvée : {name}")
                        instance = obj(main_window)
                        instance.setup()
                        loaded_instances.append(instance)
                        module_found = True
                        logger.info(f"  [OK] Module {folder} chargé et initialisé.")
                        break
                
                if not module_found:
                    logger.warning(f"  ! Aucune classe héritant de BaseModule trouvée dans {folder}")
                                        
            except Exception as e:
                logger.error(f"  [ERREUR] Échec du chargement de {folder} : {str(e)}")
                logger.error(traceback.format_exc())

        logger.info(f"--- FIN DU CHARGEMENT DES MODULES ({len(loaded_instances)} chargés) ---")
        return loaded_instances

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