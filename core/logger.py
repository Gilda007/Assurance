import logging
import os
from datetime import datetime

# Création du dossier logs à la racine du projet
LOG_DIR = os.path.join(os.getcwd(), "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Nom du fichier basé sur la date du jour
log_filename = datetime.now().strftime("%Y-%m-%d") + ".log"
log_path = os.path.join(LOG_DIR, log_filename)

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(log_path, encoding='utf-8'),
        logging.StreamHandler() # Affiche aussi dans la console
    ]
)

logger = logging.getLogger("AMS_Project")

def log_error(message):
    logger.error(message)

def log_info(message):
    logger.info(message)