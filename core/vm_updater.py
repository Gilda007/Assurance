import os
import sys
import json
import time
import shutil
import hashlib
import tempfile
import platform
import logging
from pathlib import Path

try:
    import requests
except ImportError:
    raise ImportError("requests est requis : pip install requests")

logger = logging.getLogger("AMS_VM_Updater")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

DEFAULT_CONFIG = {
    "update_server_url": "https://api.github.com/repos/ORG/REPO/releases/latest",
    "install_path": "",
    "binary_name": "main.bin",
    "bin_dir": "",
    "version_file": "version.txt",
    "platform_map": {"Windows": "windows", "Darwin": "macos", "Linux": "linux"},
    "check_interval_seconds": 3600,
}


def _detect_os():
    os_name = platform.system()
    return DEFAULT_CONFIG['platform_map'].get(os_name, os_name.lower())


def load_local_config(config_path="vm_updater_config.json"):
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            on_disk = json.load(f)
        config.update(on_disk)
    else:
        logger.warning(f"Config {config_path} non trouvé, je prends valeurs par défaut")

    if not config.get("install_path"):
        raise ValueError("install_path doit être défini dans vm_updater_config.json")

    if not config.get("binary_name"):
        raise ValueError("binary_name doit être défini dans vm_updater_config.json")

    return config


def get_local_version(install_path, version_file):
    path = os.path.join(install_path, version_file)
    if not os.path.exists(path):
        return "0.0.0"
    return Path(path).read_text(encoding="utf-8").strip()


def write_local_version(install_path, version_file, version):
    Path(os.path.join(install_path, version_file)).write_text(version, encoding="utf-8")


def _shasum(path, algo="sha256"):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def fetch_latest_release(update_server_url):
    headers = {"Accept": "application/vnd.github.v3+json"}
    r = requests.get(update_server_url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()


def choose_asset(release_data, current_os):
    assets = release_data.get("assets", [])
    if not assets:
        raise RuntimeError("Pas d'assets dans la release")

    for asset in assets:
        name = asset.get("name", "").lower()
        if current_os in name:
            return asset

    raise RuntimeError(f"Aucun asset compatible trouvé pour {current_os}")


def download_asset(asset):
    url = asset.get("browser_download_url")
    if not url:
        raise RuntimeError("Asset browser_download_url manquant")

    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".partial")
    os.close(tmp_fd)

    logger.info(f"Téléchargement de {url}")
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(tmp_path, "wb") as fd:
            for chunk in r.iter_content(8192):
                if chunk:
                    fd.write(chunk)

    final_path = tmp_path.replace(".partial", "")
    os.rename(tmp_path, final_path)
    return final_path


def atomic_replace(file_path, new_path):
    backup = f"{file_path}.bak.{int(time.time())}"
    if os.path.exists(file_path):
        shutil.copy2(file_path, backup)
        logger.info(f"Backup créé : {backup}")

    shutil.copy2(new_path, file_path)
    os.chmod(file_path, 0o755)
    logger.info(f"Remplacement réussi de {file_path}")
    return backup if os.path.exists(backup) else None


def check_update_once(config):
    current_os = _detect_os()
    local_version = get_local_version(config['install_path'], config['version_file'])
    logger.info(f"OS détecté: {current_os}, version locale: {local_version}")

    release = fetch_latest_release(config['update_server_url'])
    remote_version = release.get("tag_name") or release.get("name")
    if not remote_version:
        raise RuntimeError("Cannot determine remote version from release")

    remote_version = remote_version.strip().lstrip("v")

    logger.info(f"Remote version: {remote_version}")
    if tuple(map(int, remote_version.split('.'))) <= tuple(map(int, local_version.split('.'))):
        logger.info("Aucune mise à jour requise")
        return False

    asset = choose_asset(release, current_os)
    downloaded = download_asset(asset)

    if config.get("sha256"):
        digest = _shasum(downloaded, "sha256")
        if digest.lower() != config.get("sha256").lower():
            raise ValueError(f"SHA256 mismatch: {digest} != {config.get('sha256')}")

    target_bin = os.path.join(config['install_path'], config['binary_name'])
    backup_path = atomic_replace(target_bin, downloaded)

    write_local_version(config['install_path'], config['version_file'], remote_version)
    logger.info(f"Module mis à jour avec succès vers {remote_version}")
    return True


def loop_updater(config):
    logger.info("Démarrage du service de mise à jour en boucle")
    while True:
        try:
            check_update_once(config)
        except Exception as exc:
            logger.error(f"Update check échoué: {exc}")
        time.sleep(config.get('check_interval_seconds', 3600))


def main(argv=None):
    argv = argv or sys.argv[1:]
    config = load_local_config()

    if len(argv) == 0 or argv[0] in ("check", "status"):
        check_update_once(config)
        return
    if argv[0] in ("run", "loop"):
        loop_updater(config)
        return

    print("Usage: vm_updater.py [check|run]")


if __name__ == '__main__':
    main()
