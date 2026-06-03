#!/usr/bin/env python3
# backup_manager.py - Script de backup automatisé

import os
import sys
import subprocess
import logging
from datetime import datetime
import gzip
import shutil
from pathlib import Path

# Configuration
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "ams_db"
DB_USER = "ams_admin"
DB_PASSWORD = "Admin123_@"  # À modifier

BACKUP_DIR = "/var/backups/lometa"
LOG_FILE = "/var/log/lometa_backup.log"
RETENTION_DAYS = 30  # Garder 30 jours de backups

def setup_logging():
    """Configure le logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
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

def perform_backup():
    """Effectue le backup de la base de données"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"backup_{DB_NAME}_{timestamp}.sql")
    compressed_file = f"{backup_file}.gz"
    
    try:
        # Commande pg_dump
        cmd = f'PGPASSWORD="{DB_PASSWORD}" pg_dump -U {DB_USER} -h {DB_HOST} -p {DB_PORT} -d {DB_NAME} > "{backup_file}"'
        
        logging.info(f"Début du backup: {DB_NAME}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Compression
            with open(backup_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            os.remove(backup_file)
            
            # Vérifier la taille
            file_size = os.path.getsize(compressed_file) / (1024 * 1024)
            logging.info(f"✅ Backup réussi: {compressed_file} ({file_size:.2f} MB)")
            return True
        else:
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