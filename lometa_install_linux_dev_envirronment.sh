#!/bin/bash

# Couleurs pour les messages
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}   INSTALLATION DE L'ENVIRONNEMENT DEV (AMS_Project)${NC}"
echo -e "${BLUE}======================================================${NC}"

# 1. Mise à jour et installation des dépendances système
echo -e "${GREEN}[INFO] Installation des dépendances système...${NC}"
sudo apt update
sudo apt install -y python3-pip python3-venv git \
    libpq-dev python3-dev \
    libgl1-mesa-dev libxkbcommon-x11-0 libegl1-mesa

# 2. Gestion du dépôt
if [ ! -d "Assurance" ]; then
    echo -e "${GREEN}[INFO] Clonage du dépôt GitHub...${NC}"
    git clone https://github.com/Gilda007/Assurance.git
    cd Assurance
else
    echo -e "${GREEN}[INFO] Le dossier Assurance existe déjà.${NC}"
    cd Assurance
fi

# 3. Création de l'environnement virtuel
if [ ! -d "venv" ]; then
    echo -e "${GREEN}[INFO] Création de l'environnement virtuel (venv)...${NC}"
    python3 -m venv venv
fi

# 4. Activation et Installation des packages Python
echo -e "${GREEN}[INFO] Activation de venv et installation des packages...${NC}"
source venv/bin/activate

# Mise à jour de pip
pip install --upgrade pip

# Installation des dépendances critiques
echo -e "${GREEN}[INFO] Installation de PySide6, SQLAlchemy et psycopg2...${NC}"
pip install PySide6 sqlalchemy psycopg2-binary qrcode

# Installation depuis requirements.txt si présent
if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}[INFO] Installation des dépendances depuis requirements.txt...${NC}"
    pip install -r requirements.txt
fi

# 5. Structure des dossiers
echo -e "${GREEN}[INFO] Vérification de la structure des dossiers...${NC}"
mkdir -p addons core logs assets

# 6. Finalisation
echo -e "${BLUE}======================================================${NC}"
echo -e "${GREEN}[SUCCESS] Environnement Linux configuré !${NC}"
echo -e ""
echo -e "Pour lancer l'application :"
echo -e "1. source venv/bin/activate"
echo -e "2. python3 main.py"
echo -e "${BLUE}======================================================${NC}"