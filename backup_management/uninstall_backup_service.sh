#!/bin/bash
# uninstall_backup_service.sh - Désinstallation du service de backup

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Désinstallation du service de backup LOMETA${NC}"
echo "============================================================"

# Arrêter et désactiver le timer
echo -e "${YELLOW}Arrêt du timer...${NC}"
systemctl stop lometa-backup.timer 2>/dev/null || true
systemctl disable lometa-backup.timer 2>/dev/null || true

# Supprimer les fichiers
echo -e "${YELLOW}Suppression des fichiers...${NC}"
rm -f /etc/systemd/system/lometa-backup.service
rm -f /etc/systemd/system/lometa-backup.timer
rm -f /usr/local/bin/backup_manager.py
rm -f /usr/local/bin/lometa-backup.sh

# Recharger systemd
systemctl daemon-reload

echo -e "${GREEN}✓ Service désinstallé${NC}"

# Option: Supprimer les backups
read -p "Voulez-vous supprimer les dossiers de backup ? (o/N): " -r response
if [[ $response =~ ^[OoYy]$ ]]; then
    rm -rf /var/backups/lometa
    echo -e "${GREEN}✓ Dossier de backup supprimé${NC}"
fi

echo "============================================================"
echo -e "${GREEN}Désinstallation terminée${NC}"