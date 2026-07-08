#!/bin/bash

# ========================================
#  Compilation et Archivage des Modules .pyc
#  Version 1.0 - Linux/Mac
# ========================================

# ========================================
#  CONFIGURATION
# ========================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
NC='\033[0m'

VERSION="1.0.0"
DATE=$(date +%Y%m%d_%H%M%S)
SCRIPT_NAME="compile_modules"
LOG_FILE="${SCRIPT_NAME}_${DATE}.log"

# Dossiers
SOURCE_DIR="."
OUTPUT_DIR="dist_compiled"
TEMP_DIR="${OUTPUT_DIR}/temp"
MODULES_DIR="${OUTPUT_DIR}/modules"
ARCHIVE_NAME="modules_compiled_${VERSION}_${DATE}.zip"

# Exclusions
EXCLUDE_PATTERNS=(
    "venv"
    ".git"
    "__pycache__"
    "dist"
    "build"
    "*.pyc"
    "*.pyo"
    "*.pyd"
    "*.so"
    "*.dylib"
    "*.dll"
    "*.exe"
    "*.log"
    "*.tmp"
    "node_modules"
    ".idea"
    ".vscode"
)

# ========================================
#  FONCTIONS UTILITAIRES
# ========================================
log() {
    local msg="[$(date +%Y-%m-%d_%H:%M:%S)] $1"
    echo -e "$msg" | tee -a "$LOG_FILE"
}

print_header() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${WHITE}            COMPILATION & ARCHIVAGE MODULES .PYC              ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    log "${WHITE}📦 Version: ${VERSION}${NC}"
    log "${WHITE}📅 Date: ${DATE}${NC}"
    echo ""
}

check_python() {
    log "${YELLOW}🔍 Vérification de Python...${NC}"
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        log "${RED}❌ Python non trouvé !${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
    log "${GREEN}✅ Python trouvé: ${PYTHON_VERSION}${NC}"
}

clean_directories() {
    log "${YELLOW}🧹 Nettoyage des dossiers existants...${NC}"
    
    rm -rf "$OUTPUT_DIR"
    mkdir -p "$TEMP_DIR"
    mkdir -p "$MODULES_DIR"
    
    log "${GREEN}✅ Dossiers préparés${NC}"
}

should_exclude() {
    local file="$1"
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        if [[ "$file" == *"$pattern"* ]]; then
            return 0
        fi
    done
    return 1
}

compile_modules() {
    log "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    log "${WHITE}🔒 ÉTAPE 1/3 : Compilation des modules en .pyc${NC}"
    log "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    
    # Compiler tous les .py en .pyc avec optimisation
    log "${YELLOW}📝 Compilation des fichiers Python...${NC}"
    
    $PYTHON_CMD -O -m compileall -b -f -q "$SOURCE_DIR" \
        --exclude="venv" \
        --exclude=".git" \
        --exclude="__pycache__" \
        --exclude="dist" \
        --exclude="build" \
        --exclude="dist_compiled" \
        2>&1 | tee -a "$LOG_FILE"
    
    if [ ${PIPESTATUS[0]} -ne 0 ]; then
        log "${RED}❌ Erreur lors de la compilation${NC}"
        exit 1
    fi
    
    # Copier et organiser les .pyc
    log "${YELLOW}📦 Organisation des modules compilés...${NC}"
    
    local count=0
    local total=$(find "$SOURCE_DIR" -name "*.py" -not -path "*/venv/*" -not -path "*/.git/*" -not -path "*/__pycache__/*" -not -path "*/dist/*" -not -path "*/build/*" -not -path "*/dist_compiled/*" | wc -l)
    
    find "$SOURCE_DIR" -name "*.pyc" -type f | while read -r pyc_file; do
        # Vérifier les exclusions
        if should_exclude "$pyc_file"; then
            continue
        fi
        
        # Reconstruire la structure
        rel_path="${pyc_file#$SOURCE_DIR/}"
        dest_file="$MODULES_DIR/${rel_path%.pyc}.py"
        
        # Créer le dossier de destination
        mkdir -p "$(dirname "$dest_file")"
        
        # Copier le .pyc
        cp "$pyc_file" "${dest_file}c"
        
        # Créer un fichier .py minimal
        cat > "$dest_file" << 'EOF'
# -*- coding: utf-8 -*-
# ⚠️  MODULE COMPILÉ - Code source non disponible
# 📦 Version protégée - Ne pas modifier
import os
import sys
import importlib.util

__all__ = []

def __load_module():
    """Charge le module compilé en .pyc"""
    module_name = __name__
    pyc_path = __file__ + 'c'
    
    if not os.path.isfile(pyc_path):
        raise ImportError(f"Fichier compilé manquant: {pyc_path}")
    
    try:
        # Charger le module compilé
        spec = importlib.util.spec_from_file_location(module_name, pyc_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Remplacer le module dans sys.modules
        sys.modules[module_name] = module
        
        # Copier le contenu du module dans le module courant
        for attr_name in dir(module):
            if not attr_name.startswith('_'):
                globals()[attr_name] = getattr(module, attr_name)
        
        # Mettre à jour __all__
        if hasattr(module, '__all__'):
            globals()['__all__'] = module.__all__
        
        return module
    except Exception as e:
        raise ImportError(f"Erreur de chargement du module compilé: {e}")

# Charger automatiquement le module
__load_module()
EOF
        
        # Supprimer le .pyc original
        rm -f "$pyc_file"
        
        count=$((count + 1))
        progress=$((count * 100 / total))
        echo -ne "\r${BLUE}Progression: ${progress}%${NC}    "
    done
    
    echo ""
    log "${GREEN}✅ ${count} modules compilés avec succès${NC}"
}

create_zip_archive() {
    log "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    log "${WHITE}📦 ÉTAPE 2/3 : Création de l'archive ZIP${NC}"
    log "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    
    # Déterminer la taille des modules
    local size=$(du -sh "$MODULES_DIR" 2>/dev/null | cut -f1)
    
    log "${YELLOW}📦 Compression des modules (taille: ${size})...${NC}"
    
    # Créer l'archive
    cd "$OUTPUT_DIR" || exit 1
    
    # Vérifier si zip est installé
    if ! command -v zip &> /dev/null; then
        log "${YELLOW}⚠ zip non trouvé, utilisation de Python...${NC}"
        
        # Utiliser Python pour créer le zip
        cat > create_zip.py << 'EOF'
import os
import zipfile
from pathlib import Path

def create_zip():
    zip_path = "../modules_compiled_${VERSION}_${DATE}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('modules'):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, file_path)
    
    print(f"✅ Archive créée: {zip_path}")

if __name__ == "__main__":
    create_zip()
EOF
        
        $PYTHON_CMD create_zip.py
        rm -f create_zip.py
    else
        # Utiliser zip
        zip -r "../$ARCHIVE_NAME" modules/* -q
    fi
    
    cd - > /dev/null || exit 1
    
    if [ -f "$OUTPUT_DIR/../$ARCHIVE_NAME" ]; then
        mv "$OUTPUT_DIR/../$ARCHIVE_NAME" "$OUTPUT_DIR/"
        local archive_size=$(du -sh "$OUTPUT_DIR/$ARCHIVE_NAME" 2>/dev/null | cut -f1)
        log "${GREEN}✅ Archive créée: ${ARCHIVE_NAME} (${archive_size})${NC}"
    else
        log "${RED}❌ Erreur lors de la création de l'archive${NC}"
        exit 1
    fi
}

create_metadata() {
    log "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    log "${WHITE}📋 ÉTAPE 3/3 : Création des métadonnées${NC}"
    log "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    
    # Créer un fichier de métadonnées
    cat > "$OUTPUT_DIR/metadata.json" << EOF
{
    "version": "$VERSION",
    "build_date": "$(date -Iseconds)",
    "python_version": "$PYTHON_VERSION",
    "modules_count": $(find "$MODULES_DIR" -name "*.pyc" | wc -l),
    "compilation_level": "optimized",
    "compiler": "$PYTHON_CMD",
    "archive": "$ARCHIVE_NAME"
}
EOF
    
    # Créer un README
    cat > "$OUTPUT_DIR/README.md" << 'EOF'
# Modules Python Compilés

## 📦 Description
Ce package contient des modules Python pré-compilés en bytecode (.pyc).

## 🔒 Protection
- Le code source original n'est pas inclus
- Les modules sont compilés avec optimisation (-O)
- Chargement automatique via import

## 📁 Structure