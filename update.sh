#!/bin/bash

# ============================================================
# Script de mise à jour du module Automobiles
# ============================================================

# Activation du mode strict
set -e  # Arrêt en cas d'erreur
set -u  # Arrêt si variable non définie

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================
# CONFIGURATION
# ============================================================

MODULE_NAME="Automobiles"
NEW_VERSION="1.2.0"
PROJECT_DIR="/home/fearless/Documents/Assurance"
SERVER_URL="http://192.168.100.17:5000"

# Options
CREATE_ZIP=true
COPY_TO_SERVER=true
UPDATE_VERSIONS=true
CLEANUP=true

# ============================================================
# FONCTIONS
# ============================================================

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_separator() {
    echo "============================================================"
}

check_file_exists() {
    if [ ! -f "$1" ]; then
        print_error "Fichier non trouvé: $1"
        return 1
    fi
    return 0
}

check_directory_exists() {
    if [ ! -d "$1" ]; then
        print_error "Dossier non trouvé: $1"
        return 1
    fi
    return 0
}

# ============================================================
# DÉBUT DU SCRIPT
# ============================================================

print_separator
echo -e "${GREEN}  Mise à jour du module $MODULE_NAME${NC}"
echo -e "${GREEN}  Nouvelle version: $NEW_VERSION${NC}"
print_separator
echo ""

# Vérification du répertoire du projet
print_status "Vérification du répertoire du projet..."
if [ ! -d "$PROJECT_DIR" ]; then
    print_error "Répertoire du projet non trouvé: $PROJECT_DIR"
    exit 1
fi
cd "$PROJECT_DIR"
print_success "Répertoire du projet: $PROJECT_DIR"

# ============================================================
# 1. VÉRIFICATION DU MODULE
# ============================================================
print_separator
echo -e "${GREEN}[1/6] VÉRIFICATION DU MODULE${NC}"
print_separator

MODULE_PATH="addons/$MODULE_NAME"
MANIFEST_PATH="$MODULE_PATH/manifest.json"

if ! check_directory_exists "$MODULE_PATH"; then
    exit 1
fi

if ! check_file_exists "$MANIFEST_PATH"; then
    exit 1
fi

# Affichage de la version actuelle
CURRENT_VERSION=$(grep -o '"version": "[^"]*"' "$MANIFEST_PATH" | cut -d'"' -f4)
print_status "Version actuelle: $CURRENT_VERSION"
print_status "Nouvelle version: $NEW_VERSION"
echo ""

# ============================================================
# 2. MISE À JOUR DU MANIFEST.JSON
# ============================================================
print_separator
echo -e "${GREEN}[2/6] MISE À JOUR DU MANIFEST.JSON${NC}"
print_separator

# Sauvegarde du manifest original
cp "$MANIFEST_PATH" "$MANIFEST_PATH.bak"
print_status "Sauvegarde créée: $MANIFEST_PATH.bak"

# Mise à jour de la version
sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"$NEW_VERSION\"/" "$MANIFEST_PATH"

# Mise à jour du changelog (optionnel)
# Ajoutez ici la mise à jour du changelog si nécessaire

print_success "Manifest.json mis à jour"
echo ""

# ============================================================
# 3. CRÉATION DU FICHIER ZIP
# ============================================================
if [ "$CREATE_ZIP" = true ]; then
    print_separator
    echo -e "${GREEN}[3/6] CRÉATION DU FICHIER ZIP${NC}"
    print_separator
    
    cd addons
    
    # Suppression de l'ancien ZIP s'il existe
    if [ -f "${MODULE_NAME}.zip" ]; then
        rm "${MODULE_NAME}.zip"
        print_status "Ancien ZIP supprimé"
    fi
    
    # Création du ZIP
    print_status "Création du ZIP: ${MODULE_NAME}.zip"
    zip -r "${MODULE_NAME}.zip" "$MODULE_NAME/" \
        -x "*.pyc" \
        -x "*__pycache__/*" \
        -x "*.pyo" \
        -x "*.pyd" \
        -x "*.db" \
        -x "*.log" \
        -x ".git/*" \
        -x "*.bak" \
        -q
    
    if [ -f "${MODULE_NAME}.zip" ]; then
        ZIP_SIZE=$(du -h "${MODULE_NAME}.zip" | cut -f1)
        print_success "ZIP créé: ${MODULE_NAME}.zip ($ZIP_SIZE)"
    else
        print_error "Échec de la création du ZIP"
        exit 1
    fi
    
    cd ..
    echo ""
fi

# ============================================================
# 4. COPIE VERS LE SERVEUR
# ============================================================
if [ "$COPY_TO_SERVER" = true ]; then
    print_separator
    echo -e "${GREEN}[4/6] COPIE VERS LE SERVEUR${NC}"
    print_separator
    
    SERVER_ADDONS_DIR="$PROJECT_DIR/server/addons"
    
    # Création du dossier addons sur le serveur s'il n'existe pas
    if [ ! -d "$SERVER_ADDONS_DIR" ]; then
        mkdir -p "$SERVER_ADDONS_DIR"
        print_status "Dossier créé: $SERVER_ADDONS_DIR"
    fi
    
    # Copie du ZIP
    cp "addons/${MODULE_NAME}.zip" "$SERVER_ADDONS_DIR/"
    
    if [ -f "$SERVER_ADDONS_DIR/${MODULE_NAME}.zip" ]; then
        print_success "ZIP copié vers: $SERVER_ADDONS_DIR/${MODULE_NAME}.zip"
    else
        print_error "Échec de la copie du ZIP"
        exit 1
    fi
    
    echo ""
fi

# ============================================================
# 5. MISE À JOUR DE VERSIONS.JSON
# ============================================================
if [ "$UPDATE_VERSIONS" = true ]; then
    print_separator
    echo -e "${GREEN}[5/6] MISE À JOUR DE VERSIONS.JSON${NC}"
    print_separator
    
    VERSIONS_FILE="$PROJECT_DIR/server/versions.json"
    ZIP_PATH="$SERVER_ADDONS_DIR/${MODULE_NAME}.zip"
    ZIP_SIZE=$(stat -c%s "$ZIP_PATH" 2>/dev/null || echo "0")
    
    # Création du fichier s'il n'existe pas
    if [ ! -f "$VERSIONS_FILE" ]; then
        echo '{"app_version": "1.0.0", "modules": {}}' > "$VERSIONS_FILE"
        print_status "Fichier versions.json créé"
    fi
    
    # Mise à jour avec Python (plus fiable que sed pour le JSON)
    python3 << EOF
import json
from datetime import datetime

# Lecture du fichier
with open('$VERSIONS_FILE', 'r') as f:
    versions = json.load(f)

# Mise à jour du module
versions['modules']['$MODULE_NAME'] = {
    'version': '$NEW_VERSION',
    'download_url': '$SERVER_URL/addons/${MODULE_NAME}.zip',
    'changelog': '• Correction bugs interface\\n• Ajout export PDF\\n• Optimisation performances\\n• Amélioration des performances',
    'size': $ZIP_SIZE,
    'required': False,
    'min_app_version': '1.0.0'
}

# Mise à jour de la date
versions['last_updated'] = datetime.now().isoformat()

# Sauvegarde
with open('$VERSIONS_FILE', 'w') as f:
    json.dump(versions, f, indent=2, ensure_ascii=False)

print('✅ versions.json mis à jour')
EOF
    
    if [ $? -eq 0 ]; then
        print_success "versions.json mis à jour"
    else
        print_error "Échec de la mise à jour de versions.json"
        exit 1
    fi
    
    echo ""
fi

# ============================================================
# 6. NETTOYAGE
# ============================================================
if [ "$CLEANUP" = true ]; then
    print_separator
    echo -e "${GREEN}[6/6] NETTOYAGE${NC}"
    print_separator
    
    # Suppression du ZIP temporaire dans addons
    if [ -f "addons/${MODULE_NAME}.zip" ]; then
        rm "addons/${MODULE_NAME}.zip"
        print_status "ZIP temporaire supprimé"
    fi
    
    # Suppression de la sauvegarde du manifest (optionnel)
    # rm "$MANIFEST_PATH.bak"
    # print_status "Sauvegarde du manifest supprimée"
    
    echo ""
fi

# ============================================================
# RÉSUMÉ FINAL
# ============================================================
print_separator
echo -e "${GREEN}  MISE À JOUR TERMINÉE AVEC SUCCÈS !${NC}"
print_separator
echo ""
echo "📦 Module: $MODULE_NAME"
echo "🔖 Nouvelle version: $NEW_VERSION"
echo "📁 ZIP: $SERVER_ADDONS_DIR/${MODULE_NAME}.zip"
echo ""
echo "🌐 Serveur: $SERVER_URL"
echo "📋 API: $SERVER_URL/api/check_updates"
echo ""
echo "Pour redémarrer le serveur :"
echo "  cd $PROJECT_DIR/server"
echo "  python3 api.py"
echo ""
print_separator

# ============================================================
# OPTION: REDÉMARRAGE AUTOMATIQUE DU SERVEUR
# ============================================================
read -p "Voulez-vous redémarrer le serveur maintenant ? (o/N) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[OoYy]$ ]]; then
    print_status "Redémarrage du serveur..."
    
    # Arrêt du serveur existant
    pkill -f "python3.*api.py" 2>/dev/null || true
    sleep 1
    
    # Démarrage du serveur
    cd "$PROJECT_DIR/server"
    nohup python3 api.py > server.log 2>&1 &
    
    sleep 2
    
    # Vérification
    if pgrep -f "python3.*server/api.py" > /dev/null; then
        print_success "Serveur redémarré avec succès"
        print_status "Logs: tail -f $PROJECT_DIR/server/server.log"
    else
        print_error "Échec du redémarrage du serveur"
    fi
fi

echo ""
print_success "Script terminé !"