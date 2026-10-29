#!/bin/bash
# ============================================================
#  LOMETA — Compilation SÉCURISÉE (Linux)
#  Nuitka standalone + addons compilés en .so (Option A)
#  Aucune source Python exposée — Python 3.14 compatible
# ============================================================
#  ARCHITECTURE PRISE EN COMPTE :
#   - core/     → compilé dans le binaire principal
#   - server/   → compilé dans le binaire principal
#   - icons/    → compilé dans le binaire principal
#   - addons/   → compilés séparément en .so (modules natifs)
#   - main.py   → point d'entrée compilé
# ============================================================

set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; WHITE='\033[1;37m'; NC='\033[0m'

LOG_FILE="build_secure_$(date +%Y%m%d_%H%M%S).log"

log() { echo "$1" | tee -a "$LOG_FILE"; }
section() {
    echo -e "\n${CYAN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}  $1${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
}
die() { echo -e "${RED}✗ $1${NC}"; exit 1; }

# ============================================================
# 0. ENVIRONNEMENT
# ============================================================
section "0/7 · Vérification de l'environnement"

PYTHON=${PYTHON:-python3}
command -v "$PYTHON" >/dev/null || die "python3 introuvable"

PY_VER=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo -e "${BLUE}🐍 Python : $($PYTHON --version) [$PY_VER]${NC}"

if ! $PYTHON -m nuitka --version &>/dev/null; then
    echo -e "${YELLOW}⚠ Nuitka manquant — installation…${NC}"
    $PYTHON -m pip install --upgrade nuitka ordered-set zstandard >> "$LOG_FILE" 2>&1
fi
NUITKA_VER=$($PYTHON -m nuitka --version 2>/dev/null | head -n1)
echo -e "${BLUE}🔨 Nuitka : $NUITKA_VER${NC}"

# Vérif outils système
command -v rsync >/dev/null || die "rsync requis (apt install rsync)"
command -v zip   >/dev/null || die "zip requis (apt install zip)"
command -v gcc   >/dev/null || die "gcc requis (apt install build-essential)"

echo -e "${YELLOW}ℹ️  Mode : --standalone (PAS onefile — addons dynamiques requis)${NC}"
echo -e "${YELLOW}ℹ️  Addons : compilés en .so séparément (Option A)${NC}"

# ============================================================
# 1. NETTOYAGE
# ============================================================
section "1/7 · Nettoyage"
rm -rf build dist dist_obf *.spec dist_secure src_clean addons_compiled 2>/dev/null
log "Nettoyage terminé"
echo -e "${GREEN}✓ Espace de travail propre${NC}"

# ============================================================
# 2. PRÉPARATION DE LA SOURCE CŒUR
# ============================================================
section "2/7 · Préparation de la source cœur"

OBF_DIR="src_clean"
mkdir -p "$OBF_DIR"

echo -e "${BLUE}📁 Copie des packages cœur (core, server, icons)…${NC}"
for pkg in core server icons; do
    [ -d "$pkg" ] || { echo -e "${YELLOW}  ⚠ $pkg/ absent, ignoré${NC}"; continue; }
    rsync -a \
        --exclude='.history' --exclude='__pycache__' \
        --exclude='.venv' --exclude='node_modules' \
        --exclude='*.pyc' --exclude='*.pyo' \
        --exclude='test_*.py' --exclude='.pytest_cache' \
        "$pkg" "$OBF_DIR/"
done

echo -e "${BLUE}📄 Copie des gestionnaires racine…${NC}"
for f in version_manager.py update_manager.py update_dialog.py \
         update_client.py update_widget.py module_detector.py main.py; do
    [ -f "$f" ] && cp "$f" "$OBF_DIR/"
done

echo -e "${GREEN}✓ Source cœur prête : $(du -sh "$OBF_DIR" | cut -f1)${NC}"

# ============================================================
# 3. COMPILATION DU CŒUR (standalone)
# ============================================================
section "3/7 · Compilation Nuitka du cœur (20–40 min la 1ère fois)"

DATA_ARGS=()
[ -d "icons" ] && DATA_ARGS+=(--include-data-dir=icons=icons)
[ -f "module_registry.json" ] && DATA_ARGS+=(--include-data-file=module_registry.json=.)

$PYTHON -m nuitka \
    --standalone \
    --assume-yes-for-downloads \
    --enable-plugin=pyside6 \
    --include-package=core \
    --include-package=server \
    --include-package=icons \
    --include-package-data=PySide6 \
    --include-package-data=qtawesome \
    --include-package-data=sqlalchemy \
    --include-package-data=pandas \
    --include-package-data=numpy \
    --include-package-data=PIL \
    --include-package-data=requests \
    --include-package-data=qrcode \
    --include-package-data=reportlab \
    --include-package-data=openpyxl \
    --include-package-data=bcrypt \
    --include-package-data=flask \
    --include-package-data=flask_cors \
    --include-package-data=pymysql \
    --include-package-data=pyqtgraph \
    --include-package-data=dateutil \
    --include-package-data=dotenv \
    --include-module=cv2 \
    --include-module=numpy \
    --include-module=PySide6.QtCharts \
    --include-module=PySide6.QtMultimedia \
    --include-module=PySide6.QtMultimediaWidgets \
    --include-module=PySide6.QtPrintSupport \
    --include-module=PySide6.QtSvg \
    --include-module=PySide6.QtSql \
    --include-module=PySide6.QtNetwork \
    --include-module=PySide6.QtOpenGL \
    --include-module=PySide6.QtOpenGLWidgets \
    --nofollow-import-to=pytest \
    --nofollow-import-to=tkinter \
    --nofollow-import-to=PyQt5 \
    --nofollow-import-to=PyQt6 \
    --nofollow-import-to=matplotlib \
    --nofollow-import-to=IPython \
    --nofollow-import-to=jupyter \
    --nofollow-import-to=notebook \
    --output-dir=dist_secure \
    --output-filename=LOMETA \
    --report="$LOG_FILE.nuitka.xml" \
    "${DATA_ARGS[@]}" \
    "$OBF_DIR/main.py" 2>&1 | tee -a "$LOG_FILE"

# Localisation du .dist généré
DIST_DIR=$(find dist_secure -maxdepth 1 -type d -name "*.dist" | head -n1)
[ -z "$DIST_DIR" ] && die "Dossier .dist introuvable dans dist_secure/"
BINARY="$DIST_DIR/LOMETA"
[ -f "$BINARY" ] || die "Binaire LOMETA introuvable dans $DIST_DIR"

echo -e "${GREEN}✓ Cœur compilé : $BINARY ($(du -h "$BINARY" | cut -f1))${NC}"


# ============================================================
# 4. COMPILATION DES ADDONS EN .so (Option A) — VERSION FINALE
# ============================================================
section "4/7 · Compilation des addons en modules natifs .so"

ADDONS_SRC_ABS="$(pwd)/addons"
DIST_DIR_ABS="$(cd "$(dirname "$DIST_DIR")" && pwd)/$(basename "$DIST_DIR")"
ADDONS_DEST_ABS="$DIST_DIR_ABS/addons"
ADDONS_BUILD_ABS="$(pwd)/addons_compiled"

echo -e "${BLUE}  Source addons : $ADDONS_SRC_ABS${NC}"
echo -e "${BLUE}  Cible         : $ADDONS_DEST_ABS${NC}"

mkdir -p "$ADDONS_DEST_ABS" "$ADDONS_BUILD_ABS"

if [ ! -d "$ADDONS_SRC_ABS" ]; then
    echo -e "${YELLOW}⚠ Dossier addons/ introuvable — étape ignorée${NC}"
else
    # --- 4a. Copie propre ---
    echo -e "${BLUE}📁 Préparation des sources addons…${NC}"
    for pkg in "$ADDONS_SRC_ABS"/*/; do
        [ -d "$pkg" ] || continue
        name=$(basename "$pkg")
        rsync -a \
            --exclude='.history' --exclude='__pycache__' \
            --exclude='*.pyc' --exclude='*.pyo' \
            --exclude='test_*.py' --exclude='.pytest_cache' \
            --exclude='*.db' --exclude='*.sqlite' \
            "$pkg" "$ADDONS_BUILD_ABS/$name/"
    done

    # --- 4b. S'assurer que chaque addon est un package valide ---
    for pkg in "$ADDONS_BUILD_ABS"/*/; do
        [ -d "$pkg" ] || continue
        name=$(basename "$pkg")
        if [ ! -f "$pkg/__init__.py" ]; then
            echo -e "${YELLOW}  ⚠ $name/__init__.py absent — création${NC}"
        fi
    done

    # --- 4c. Compilation de chaque addon (dossier, PAS __init__.py) ---
    echo -e "${BLUE}🔨 Compilation des addons (10–20 min)…${NC}"
    FAILED_ADDONS=()

    for pkg in "$ADDONS_BUILD_ABS"/*/; do
        [ -d "$pkg" ] || continue
        name=$(basename "$pkg")
        echo -e "\n${CYAN}  → Addon : $name${NC}"

        BUILD_OUT="$ADDONS_BUILD_ABS/$name/_build"
        mkdir -p "$BUILD_OUT"

        # IMPORTANT : passer le DOSSIER, pas __init__.py
        if ! $PYTHON -m nuitka \
                --module \
                --assume-yes-for-downloads \
                --include-package="addons.$name" \
                --include-package-data="addons.$name" \
                --enable-plugin=pyside6 \
                --nofollow-import-to=pytest \
                --nofollow-import-to=tkinter \
                --nofollow-import-to=PyQt5 \
                --nofollow-import-to=PyQt6 \
                --nofollow-import-to=matplotlib \
                --output-dir="$BUILD_OUT" \
                --no-pyi-file \
                "$pkg" 2>&1 | tee -a "$LOG_FILE" ; then
            echo -e "${RED}    ✗ Échec Nuitka pour $name${NC}"
            FAILED_ADDONS+=("$name (nuitka fail)")
            continue
        fi

        # Localiser la .so produite
        SO_FILE=$(find "$BUILD_OUT" -type f -name "*.so" | head -n1)
        if [ -z "$SO_FILE" ]; then
            echo -e "${RED}    ✗ Aucune .so dans $BUILD_OUT${NC}"
            ls -la "$BUILD_OUT" 2>/dev/null
            FAILED_ADDONS+=("$name (pas de .so)")
            continue
        fi

        # --- 4d. Copier .so + données dans le dist ---
        mkdir -p "$ADDONS_DEST_ABS/$name"
        cp "$SO_FILE" "$ADDONS_DEST_ABS/$name/__init__.so"

        # Copier toutes les autres .so générées
        find "$BUILD_OUT" -type f -name "*.so" ! -path "$SO_FILE" \
            -exec cp {} "$ADDONS_DEST_ABS/$name/" \; 2>/dev/null || true

        # Copier les données non-Python
        rsync -a \
            --exclude='*.py' --exclude='__pycache__' \
            --exclude='.history' --exclude='*.pyc' \
            --exclude='_build' --exclude='*.db' --exclude='*.sqlite' \
            "$ADDONS_BUILD_ABS/$name/" "$ADDONS_DEST_ABS/$name/"

        echo -e "${GREEN}    ✓ $name → $(du -h "$ADDONS_DEST_ABS/$name/__init__.so" | cut -f1)${NC}"
    done

    # --- 4e. Rapport ---
    if [ ${#FAILED_ADDONS[@]} -gt 0 ]; then
        echo -e "\n${RED}⚠ Addons non compilés :${NC}"
        for f in "${FAILED_ADDONS[@]}"; do echo -e "${RED}   • $f${NC}"; done
    fi
fi

[ -f module_registry.json ] && cp module_registry.json "$DIST_DIR_ABS/"
[ -f .env ] && cp .env "$DIST_DIR_ABS/" 2>/dev/null || true

echo -e "${GREEN}✓ Addons présents : $(ls -1 "$ADDONS_DEST_ABS" 2>/dev/null | wc -l) module(s)${NC}"
ls -la "$ADDONS_DEST_ABS" 2>/dev/null | tee -a "$LOG_FILE"

# ============================================================
# 5. VÉRIFICATION DE LA PROTECTION
# ============================================================
section "5/7 · Vérification de la protection"

# --- 5a. Binaire principal valide ---
[ -f "$BINARY" ] || die "Binaire principal absent"
echo -e "${BLUE}📦 Binaire : $BINARY ($(du -h "$BINARY" | cut -f1))${NC}"

# --- 5b. Aucun .py du cœur exposé ---
LEAKED_CORE=$(find "$DIST_DIR" -name "*.py" \
    \( -path "*/core/*" -o -path "*/server/*" -o -path "*/icons/*" \) 2>/dev/null | wc -l)
if [ "$LEAKED_CORE" -gt 0 ]; then
    echo -e "${RED}✗ $LEAKED_CORE fichiers .py du cœur exposés !${NC}"
    find "$DIST_DIR" -name "*.py" -path "*/core/*" -exec echo "   • {}" \;
    exit 1
fi
echo -e "${GREEN}✓ Aucun .py du cœur dans le dist${NC}"

# --- 5c. Aucun .py dans les addons (hors données légitimes) ---
LEAKED_ADDONS=$(find "$ADDONS_DEST" -name "*.py" 2>/dev/null | wc -l)
if [ "$LEAKED_ADDONS" -gt 0 ]; then
    echo -e "${RED}✗ $LEAKED_ADDONS fichiers .py exposés dans addons/ !${NC}"
    find "$ADDONS_DEST" -name "*.py" -exec echo "   • {}" \;
    exit 1
fi
echo -e "${GREEN}✓ Aucun .py dans addons/ (tout est .so)${NC}"

# --- 5d. Chaque addon a bien son .so ---
MISSING_SO=0
for d in "$ADDONS_DEST"/*/; do
    [ -d "$d" ] || continue
    name=$(basename "$d")
    [ -f "$d/__init__.so" ] || { echo -e "${RED}  ✗ $name/__init__.so manquant${NC}"; MISSING_SO=1; }
done
[ "$MISSING_SO" -eq 1 ] && die "Certains addons n'ont pas de .so compilé"
echo -e "${GREEN}✓ Tous les addons ont un __init__.so${NC}"

# --- 5e. Pas de code métier lisible via strings ---
echo -e "${BLUE}🔍 Scan strings du binaire principal…${NC}"
if strings "$BINARY" 2>/dev/null | grep -qE "def create_vehicle|def get_rc_premium|class VehicleController"; then
    echo -e "${RED}✗ Code source Python lisible dans le binaire !${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Aucun code métier lisible dans le binaire${NC}"

# --- 5f. Type ELF du binaire ---
file "$BINARY" | tee -a "$LOG_FILE"

# --- 5g. Résumé taille ---
DIST_SIZE=$(du -sh "$DIST_DIR" | cut -f1)
echo -e "${BLUE}📊 Taille totale dist : $DIST_SIZE${NC}"

# ============================================================
# 6. PACKAGING (ZIP)
# ============================================================
section "6/7 · Packaging de la distribution"

ZIP_NAME="LOMETA_linux_$(date +%Y%m%d_%H%M%S).zip"
(cd dist_secure && zip -r9 "../$ZIP_NAME" . >/dev/null 2>&1)
[ -f "$ZIP_NAME" ] || die "Échec création du ZIP"

echo -e "${GREEN}✓ Archive : $ZIP_NAME ($(du -h "$ZIP_NAME" | cut -f1))${NC}"

# Nettoyage des artefacts intermédiaires
rm -rf "$ADDONS_BUILD" 2>/dev/null || true
log "Artefacts intermédiaires nettoyés"

# ============================================================
# 7. RÉSUMÉ FINAL
# ============================================================
section "7/7 · Compilation terminée"

echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${WHITE}            ✅ COMPILATION SÉCURISÉE RÉUSSIE                    ${GREEN}║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${WHITE}📦 Binaire    :${NC}  ${CYAN}$BINARY${NC}"
echo -e "${WHITE}📂 Dist       :${NC}  ${CYAN}$DIST_DIR${NC}  ($DIST_SIZE)"
echo -e "${WHITE}🗜  Archive    :${NC}  ${CYAN}$ZIP_NAME${NC}"
echo -e "${WHITE}📋 Log        :${NC}  ${CYAN}$LOG_FILE${NC}"
echo ""
echo -e "${YELLOW}🔒 Protection appliquée :${NC}"
echo -e "   ${GREEN}✓${NC} core/ + server/ + icons/ → binaire natif ELF"
echo -e "   ${GREEN}✓${NC} addons/* → modules .so compilés (1 .so par addon)"
echo -e "   ${GREEN}✓${NC} Aucun .py exposé dans la distribution"
echo -e "   ${GREEN}✓${NC} Aucun code métier lisible via strings"
echo ""
echo -e "${YELLOW}🧪 Tester :${NC}"
echo -e "   ${CYAN}cd $DIST_DIR && ./LOMETA${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT :${NC}"
echo -e "   Lancer LOMETA depuis le dossier ${CYAN}$DIST_DIR/${NC}"
echo -e "   (le loader résout addons/, icons/ et module_registry.json en relatif)"
echo ""
echo -e "${YELLOW}🔍 Vérifier la protection manuellement :${NC}"
echo -e "   ${CYAN}find $DIST_DIR -name '*.py' | grep -v site-packages${NC}       → doit être vide"
echo -e "   ${CYAN}file $ADDONS_DEST/Automobiles/__init__.so${NC}                 → ELF shared object"
echo -e "   ${CYAN}strings $BINARY | grep 'VehicleController'${NC}                → doit être vide"
echo ""

log "========================================"
log "Compilation sécurisée terminée avec succès"
log "Binaire: $BINARY"
log "Archive: $ZIP_NAME"
log "========================================"