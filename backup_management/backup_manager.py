#!/usr/bin/env python3
# backup_manager.py - Script de backup automatisé

import gzip
import logging
import os
import shlex
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configuration PostgreSQL
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ams_db")
DB_USER = os.getenv("DB_USER", "ams_admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", os.getenv("DB_PASS", ""))

# Configuration de transfert SCP optionnel
SCP_TARGET = os.getenv("SCP_TARGET", "").strip()
SCP_USER = os.getenv("SCP_USER", "").strip()
SCP_PORT = os.getenv("SCP_PORT", "22").strip()
SCP_REMOTE_PATH = os.getenv("SCP_REMOTE_PATH", "~/backups_lometa").strip()
SCP_PRIVATE_KEY = os.getenv("SCP_PRIVATE_KEY", "").strip()

BACKUP_DIR = "/var/backups/lometa"
LOG_FILE = "/var/log/lometa_backup.log"
RETENTION_DAYS = 30  # Garder 30 jours de backups


def setup_logging():
    """Configure le logging"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
    )


def ensure_backup_dir():
    """Crée le dossier de backup s'il n'existe pas"""
    Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)


def cleanup_old_backups():
    """Supprime les backups plus vieux que RETENTION_DAYS"""
    cutoff = datetime.now().timestamp() - (RETENTION_DAYS * 86400)
    deleted_count = 0

    for filename in os.listdir(BACKUP_DIR):
        filepath = os.path.join(BACKUP_DIR, filename)
        if os.path.getmtime(filepath) < cutoff:
            os.remove(filepath)
            deleted_count += 1
            logging.info(f"Ancien backup supprimé: {filename}")

    if deleted_count > 0:
        logging.info(f"{deleted_count} ancien(s) backup(s) supprimé(s)")


def transfer_backup(compressed_file):
    """Transfère le fichier compressé vers une machine distante via SCP si configuré"""
    if not SCP_TARGET:
        logging.info("Aucune cible SCP configurée: sauvegarde locale uniquement")
        return True

    if "@" not in SCP_TARGET and not SCP_USER:
        logging.error("SCP_USER doit être défini si SCP_TARGET ne contient pas un préfixe utilisateur@hôte")
        return False

    target = SCP_TARGET if "@" in SCP_TARGET else f"{SCP_USER}@{SCP_TARGET}"
    remote_dir = SCP_REMOTE_PATH or "~/backups_lometa"

    ssh_args = ["ssh", "-p", str(SCP_PORT)]
    if SCP_PRIVATE_KEY:
        ssh_args.extend(["-i", SCP_PRIVATE_KEY])
    ssh_args.extend([target, f"mkdir -p {shlex.quote(remote_dir)}"])

    logging.info(f"Création du dossier distant: {target}:{remote_dir}")
    mkdir_result = subprocess.run(ssh_args, capture_output=True, text=True, check=False)
    if mkdir_result.returncode != 0:
        logging.error(f"Impossible de créer le dossier distant: {mkdir_result.stderr or mkdir_result.stdout}")
        return False

    scp_args = ["scp", "-P", str(SCP_PORT)]
    if SCP_PRIVATE_KEY:
        scp_args.extend(["-i", SCP_PRIVATE_KEY])
    scp_args.extend([compressed_file, f"{target}:{remote_dir}/"])

    logging.info(f"Transfert SCP vers {target}:{remote_dir}")
    result = subprocess.run(scp_args, capture_output=True, text=True, check=False)
    if result.returncode == 0:
        logging.info(f"✅ Fichier envoyé via SCP: {compressed_file}")
        return True

    logging.error(f"❌ Erreur SCP: {result.stderr or result.stdout}")
    return False


def perform_backup():
    """Effectue le backup de la base de données"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"backup_{DB_NAME}_{timestamp}.sql")
    compressed_file = f"{backup_file}.gz"

    try:
        logging.info(f"Début du backup: {DB_NAME}")
        env = os.environ.copy()
        env["PGPASSWORD"] = DB_PASSWORD

        with open(backup_file, "w", encoding="utf-8") as output_file:
            result = subprocess.run(
                ["pg_dump", "-U", DB_USER, "-h", DB_HOST, "-p", str(DB_PORT), "-d", DB_NAME],
                stdout=output_file,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                check=False,
            )

        if result.returncode == 0:
            with open(backup_file, "rb") as f_in:
                with gzip.open(compressed_file, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            os.remove(backup_file)

            file_size = os.path.getsize(compressed_file) / (1024 * 1024)
            logging.info(f"✅ Backup réussi: {compressed_file} ({file_size:.2f} MB)")

            if transfer_backup(compressed_file):
                return True
            return False

        logging.error(f"❌ Erreur pg_dump: {result.stderr}")
        return False

    except Exception as e:
        logging.error(f"❌ Exception lors du backup: {str(e)}")
        return False


def main():
    """Fonction principale"""
    setup_logging()
    ensure_backup_dir()

    logging.info("=" * 60)
    logging.info("Démarrage du script de backup LOMETA")
    logging.info("=" * 60)

    success = perform_backup()

    if success:
        cleanup_old_backups()
        logging.info("Backup terminé avec succès")
    else:
        logging.error("Échec du backup")
        sys.exit(1)


if __name__ == "__main__":
    main()