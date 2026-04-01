import os
import json
import zipfile
import logging
import shutil
import tempfile
import hashlib
from urllib.parse import urlparse
import requests

from core.loader import AddonLoader

logger = logging.getLogger("AMS_ModuleManager")

class ModuleManager:
    def __init__(self, addons_path=None):
        self.addons_path = addons_path or os.path.join(os.path.dirname(os.path.dirname(__file__)), "addons")
        self.loader = AddonLoader(self.addons_path)

    def list_local_modules(self):
        modules = []
        if not os.path.exists(self.addons_path):
            return modules

        for folder in os.listdir(self.addons_path):
            folder_path = os.path.join(self.addons_path, folder)
            if not os.path.isdir(folder_path) or folder.startswith("__"):
                continue
            manifest = self.loader.get_manifest(folder)
            if manifest:
                modules.append({
                    "name": folder,
                    "version": manifest.get("version", "0.0.0"),
                    "enabled": manifest.get("enabled", True),
                })
        return modules

    def _version_tuple(self, value):
        if not value:
            return (0,)
        parts = [p for p in str(value).split('.') if p.strip()]
        result = []
        for p in parts:
            try:
                result.append(int(p))
            except ValueError:
                # ignore non-numérique ou suffixes
                digits = ''.join([c for c in p if c.isdigit()])
                result.append(int(digits) if digits else 0)
        return tuple(result)

    def compare_version(self, local, remote):
        try:
            return self._version_tuple(remote) > self._version_tuple(local)
        except Exception:
            return False

    def update_available(self, module_name, remote_info):
        manifest = self.loader.get_manifest(module_name)
        if not manifest or "version" not in manifest:
            return False
        return self.compare_version(manifest["version"], remote_info.get("version", "0.0.0"))

    def install_module_archive(self, archive_path):
        if not os.path.exists(archive_path):
            raise FileNotFoundError(archive_path)

        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            members = zip_ref.namelist()
            root_folder = members[0].split('/')[0]
            if os.path.exists(os.path.join(self.addons_path, root_folder)):
                raise FileExistsError(f"Module existe déjà: {root_folder}")
            zip_ref.extractall(self.addons_path)
            logger.info(f"Module installé: {root_folder}")
        return root_folder

    def remove_module(self, module_name):
        folder = os.path.join(self.addons_path, module_name)
        if not os.path.isdir(folder):
            raise FileNotFoundError(module_name)
        for dirpath, dirnames, filenames in os.walk(folder, topdown=False):
            for f in filenames:
                os.remove(os.path.join(dirpath, f))
            for d in dirnames:
                os.rmdir(os.path.join(dirpath, d))
        os.rmdir(folder)
        logger.info(f"Module supprimé: {module_name}")

    def lock_and_migrate(self, module_name):
        # placeholder: ajouter ici invocation migrations DB, si nécessaire.
        logger.info(f"Migration demandée pour {module_name}. À implémenter.")

    def _download_archive(self, url):
        logger.info(f"Téléchargement de l'archive du module depuis: {url}")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".zip")
        os.close(tmp_fd)

        with open(tmp_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        logger.info(f"Archive téléchargée dans : {tmp_path}")
        return tmp_path

    def _check_hash(self, filepath, expected_hash):
        if not expected_hash:
            return True
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        computed = h.hexdigest()
        if computed.lower() != expected_hash.lower():
            raise ValueError(f"Hash de l'archive invalide ({computed} != {expected_hash})")
        return True

    def _extract_archive(self, archive_path, target_dir):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)

    def install_or_update_module(self, remote_info):
        name = remote_info.get("name")
        version_remote = str(remote_info.get("version", "0.0.0"))
        url = remote_info.get("download_url")
        expected_hash = remote_info.get("sha256")

        if not name or not url:
            raise ValueError("Remote info must include name and download_url")

        local_manifest = self.loader.get_manifest(name)
        local_version = local_manifest.get("version") if local_manifest else "0.0.0"

        if not self.compare_version(local_version, version_remote):
            logger.info(f"Module '{name}' est déjà à jour ({local_version} >= {version_remote})")
            return "noop"

        tmp_archive = self._download_archive(url)
        try:
            self._check_hash(tmp_archive, expected_hash)

            target_path = os.path.join(self.addons_path, name)
            backup_path = None
            if os.path.exists(target_path):
                backup_path = f"{target_path}.backup.{int(os.path.getmtime(target_path))}"
                shutil.move(target_path, backup_path)
                logger.info(f"Backup du module existant dans {backup_path}")

            os.makedirs(self.addons_path, exist_ok=True)
            self._extract_archive(tmp_archive, self.addons_path)

            # Recharger manifest et appliquer version du module si besoin
            if os.path.exists(os.path.join(target_path, "manifest.json")):
                manifest = self.loader.get_manifest(name)
                if manifest:
                    manifest["version"] = version_remote
                    manifest["enabled"] = True
                    self.loader.set_manifest(name, manifest)

            logger.info(f"Module '{name}' mis à jour vers {version_remote}")
            return "updated"

        except Exception as exc:
            logger.error(f"Echec mise à jour module {name}: {exc}")
            if backup_path and os.path.exists(backup_path):
                if os.path.exists(target_path):
                    shutil.rmtree(target_path)
                shutil.move(backup_path, target_path)
                logger.info(f"Rollback du module {name} depuis backup")
            raise
        finally:
            if os.path.exists(tmp_archive):
                os.remove(tmp_archive)

    def sync_from_repository(self, repository_manifest):
        # repository_manifest = [{"name":"Automobiles","version":"x.y.z","download_url":"..."}, ...]
        mises_a_jour = []
        locaux = {m["name"]: m for m in self.list_local_modules()}
        for remote in repository_manifest:
            name = remote.get("name")
            if not name:
                continue
            local = locaux.get(name)
            if not local:
                mises_a_jour.append({"name": name, "action": "install", "version": remote.get("version")})
                continue
            if self.compare_version(local["version"], remote.get("version", "0.0.0")):
                mises_a_jour.append({"name": name, "action": "upgrade", "version": remote.get("version")})
        return mises_a_jour
