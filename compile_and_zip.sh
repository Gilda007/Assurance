#!/bin/bash

# ========================================
#  Compilation et Archivage des Modules .pyc
#  Version 2.0 - Linux/Mac
#  Usage: ./compile_and_zip.sh [dossier_source]
#  Exemple: ./compile_and_zip.sh addons
# ========================================

# ========================================
#  CONFIGURATION
# ========================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

SCRIPT_NAME="compile_modules"
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${SCRIPT_NAME}_${DATE}.log"

# Dossier source (paramètre ou défaut)
SOURCE_DIR="${1:-addons}"

# Vérifier que le dossier source existe
if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}❌ Erreur: Le dossier '$SOURCE_DIR' n'existe pas${NC}"
    echo -e "${YELLOW}Usage: $0 [dossier_source]${NC}"
    echo -e "${YELLOW}Exemple: $0 addons${NC}"
    exit 1
fi

# Nom du dossier source (pour le nom de l'archive)
SOURCE_NAME=$(basename "$SOURCE_DIR")
OUTPUT_DIR="dist_compiled"
MODULES_DIR="${OUTPUT_DIR}/${SOURCE_NAME}"
ARCHIVE_NAME="${SOURCE_NAME}_compiled_${DATE}.zip"

# ========================================
#  FONCTIONS
# ========================================
log() {
    local msg="[$(date +%Y-%m-%d_%H:%M:%S)] $1"
    echo -e "$msg" | tee -a "$LOG_FILE"
}

print_header() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${WHITE}         COMPILATION & ARCHIVAGE MODULES .PYC                ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    log "${WHITE}📂 Source: ${SOURCE_DIR}${NC}"
    log "${WHITE}📦 Archive: ${ARCHIVE_NAME}${NC}"
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
    mkdir -p "$MODULES_DIR"
    
    log "${GREEN}✅ Dossiers préparés${NC}"
}

compile_modules() {
    log "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    log "${WHITE}🔒 ÉTAPE 1/2 : Compilation des modules en .pyc${NC}"
    log "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    
    # Compiler tous les .py du dossier source en .pyc avec optimisation
    log "${YELLOW}📝 Compilation des fichiers Python dans ${SOURCE_DIR}...${NC}"
    
    # Compiler en .pyc (optimisé)
    $PYTHON_CMD -O -m compileall -b -f -q "$SOURCE_DIR" \
        -x "(__pycache__|\.history)(/|$)" \
        2>&1 | tee -a "$LOG_FILE"
    
    if [ ${PIPESTATUS[0]} -ne 0 ]; then
        log "${RED}❌ Erreur lors de la compilation${NC}"
        exit 1
    fi
    
    # Copier et organiser les .pyc
    log "${YELLOW}📦 Organisation des modules compilés...${NC}"
    
    local count=0
    local total=$(find "$SOURCE_DIR" -name "*.py" -not -path "*/__pycache__/*" | wc -l)
    
    # Trouver tous les .pyc générés
    find "$SOURCE_DIR" -name "*.pyc" -type f | while read -r pyc_file; do
        # Ignorer les fichiers dans __pycache__
        if [[ "$pyc_file" == *"__pycache__"* ]]; then
            continue
        fi
        
        # Reconstruire la structure relative
        rel_path="${pyc_file#$SOURCE_DIR/}"
        dest_file="$MODULES_DIR/${rel_path%.pyc}.py"
        
        # Créer le dossier de destination
        mkdir -p "$(dirname "$dest_file")"
        
        # Copier le .pyc
        cp "$pyc_file" "${dest_file}c"
        
        # Créer un fichier .py wrapper
        cat > "$dest_file" << 'EOFWRAPPER'
# -*- coding: utf-8 -*-
# ⚠️ MODULE COMPILÉ - Code source non disponible
import os
import sys
import importlib.util

def __load_compiled():
    """Charge le module compilé en .pyc"""
    module_name = __name__
    pyc_path = __file__ + 'c'
    
    if not os.path.isfile(pyc_path):
        raise ImportError(f"Fichier compilé manquant: {pyc_path}")
    
    spec = importlib.util.spec_from_file_location(module_name, pyc_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Remplacer dans sys.modules
    sys.modules[module_name] = module
    
    # Exporter le contenu
    for attr_name in dir(module):
        if not attr_name.startswith('_'):
            globals()[attr_name] = getattr(module, attr_name)
    
    if hasattr(module, '__all__'):
        globals()['__all__'] = module.__all__
    
    return module

__load_compiled()
EOFWRAPPER
        
        # Supprimer le .pyc original
        rm -f "$pyc_file"
        
        count=$((count + 1))
        echo -ne "\r${BLUE}Progression: $((count * 100 / total))%${NC}    "
    done
    
    echo ""
    
    # Supprimer les fichiers .py originaux (ne garder que les .pyc et les wrappers)
    log "${YELLOW}🗑️ Suppression des fichiers source originaux...${NC}"
    find "$SOURCE_DIR" -name "*.py" -type f -not -path "*/__pycache__/*" -delete
    
    log "${GREEN}✅ ${count} modules compilés avec succès${NC}"
}

create_zip_archive() {
    log "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    log "${WHITE}📦 ÉTAPE 2/2 : Création de l'archive ZIP${NC}"
    log "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    
    # Déterminer la taille des modules
    local size=$(du -sh "$MODULES_DIR" 2>/dev/null | cut -f1)
    
    log "${YELLOW}📦 Compression des modules (taille: ${size})...${NC}"
    
    cd "$OUTPUT_DIR" || exit 1
    
    # Créer l'archive avec zip ou Python
    if command -v zip &> /dev/null; then
        zip -r "$ARCHIVE_NAME" "$SOURCE_NAME" -q
    else
        log "${YELLOW}⚠ zip non trouvé, utilisation de Python...${NC}"
        
        cat > create_zip.py << 'EOFPYTHON'
import os
import zipfile

def create_zip():
    source_name = os.environ.get('SOURCE_NAME', 'modules')
    zip_name = os.environ.get('ARCHIVE_NAME', 'modules.zip')
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_name):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, file_path)
    
    print(f"✅ Archive créée: {zip_name}")

if __name__ == "__main__":
    create_zip()
EOFPYTHON
        
        export SOURCE_NAME="$SOURCE_NAME"
        export ARCHIVE_NAME="$ARCHIVE_NAME"
        $PYTHON_CMD create_zip.py
        rm -f create_zip.py
    fi
    
    cd - > /dev/null || exit 1
    
    if [ -f "$OUTPUT_DIR/$ARCHIVE_NAME" ]; then
        local archive_size=$(du -sh "$OUTPUT_DIR/$ARCHIVE_NAME" 2>/dev/null | cut -f1)
        log "${GREEN}✅ Archive créée: ${ARCHIVE_NAME} (${archive_size})${NC}"
        
        # Supprimer le dossier modules non compressé (optionnel)
        # rm -rf "$MODULES_DIR"
    else
        log "${RED}❌ Erreur lors de la création de l'archive${NC}"
        exit 1
    fi
}

create_metadata() {
    # Créer un fichier de métadonnées
    cat > "$OUTPUT_DIR/metadata.json" << EOF
{
    "source_directory": "$SOURCE_DIR",
    "build_date": "$(date -Iseconds)",
    "python_version": "$PYTHON_VERSION",
    "modules_count": $(find "$MODULES_DIR" -name "*.pyc" | wc -l),
    "compilation_level": "optimized",
    "compiler": "$PYTHON_CMD",
    "archive": "$ARCHIVE_NAME"
}
EOF
    
    log "${GREEN}✅ Métadonnées générées${NC}"
}

show_summary() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${WHITE}                    🎉 OPERATION TERMINÉE                     ${GREEN}║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${WHITE}📂 Source compilé:${NC} ${CYAN}$SOURCE_DIR${NC}"
    echo -e "${WHITE}📦 Archive:${NC}        ${CYAN}$OUTPUT_DIR/$ARCHIVE_NAME${NC}"
    echo -e "${WHITE}📋 Log:${NC}            ${CYAN}$LOG_FILE${NC}"
    echo ""
    echo -e "${YELLOW}📝 Pour utiliser les modules compilés:${NC}"
    echo -e "  ${WHITE}unzip $OUTPUT_DIR/$ARCHIVE_NAME -d /mon/projet/${NC}"
    echo -e "  ${WHITE}export PYTHONPATH=\"\${PYTHONPATH}:/mon/projet/${SOURCE_NAME}\"${NC}"
    echo ""
}

# ========================================
#  EXÉCUTION PRINCIPALE
# ========================================
main() {
    clear
    print_header
    
    check_python
    clean_directories
    compile_modules
    create_zip_archive
    create_metadata
    show_summary
    
    log "${GREEN}✅ Script terminé avec succès${NC}"
}

# Lancer le script
main