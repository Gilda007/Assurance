#!/bin/bash
# ============================================================
#  LOMETA — Compilation sécurisée complète (Linux)
#  Cœur (--standalone) + addons (--module)
#  Aucune source Python exposée dans la distribution
# ============================================================
#  Usage :
#    ./build_linux.sh                    # build complet
#    ./build_linux.sh --clean            # nettoyage + build
#    ./build_linux.sh --no-zip           # sans créer le ZIP
#    ./build_linux.sh --verbose          # logs détaillés
# ============================================================

set -euo pipefail

# Sourcer la bibliothèque commune
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib_build.sh"

# ─── Arguments ───
DO_ZIP=1
VERBOSE=0
CLEAN=0
for arg in "$@"; do
    case "$arg" in
        --clean)   CLEAN=1 ;;
        --no-zip)  DO_ZIP=0 ;;
        --verbose) VERBOSE=1 ;;
        --help|-h)
            sed -n '2,15p' "$0"
            exit 0
            ;;
        *) warn "Argument inconnu : $arg" ;;
    esac
done

LOG_FILE="$PROJECT_ROOT/build_secure_$(date +%Y%m%d_%H%M%S).log"
log() { echo "$1" | tee -a "$LOG_FILE"; }

# ─── 0. Prérequis ───
check_prerequisites
echo -e "${BLUE}📋 Log : $LOG_FILE${NC}"

# ─── 1. Nettoyage ───
section "1 · Nettoyage"

if [ "$CLEAN" -eq 1 ]; then
    rm -rf "$PROJECT_ROOT/build" "$PROJECT_ROOT/dist" "$PROJECT_ROOT/dist_obf" \
           "$PROJECT_ROOT/src_clean" "$DIST_ROOT" "$ADDONS_BUILD" 2>/dev/null || true
    log "Nettoyage complet effectué"
fi

rm -rf "$PROJECT_ROOT/src_clean" 2>/dev/null || true
mkdir -p "$PROJECT_ROOT/src_clean"

ok "Espace de travail prêt"

# ─── 2. Préparation du cœur ───
section "2 · Préparation de la source cœur"

OBF_DIR="$PROJECT_ROOT/src_clean"

for pkg in core server icons; do
    [ -d "$PROJECT_ROOT/$pkg" ] || { warn "$pkg/ absent, ignoré"; continue; }
    rsync -a \
        --exclude='.history' --exclude='__pycache__' \
        --exclude='.venv' --exclude='node_modules' \
        --exclude='*.pyc' --exclude='*.pyo' \
        --exclude='test_*.py' --exclude='.pytest_cache' \
        "$PROJECT_ROOT/$pkg" "$OBF_DIR/"
done

for f in version_manager.py update_manager.py update_dialog.py \
         update_client.py update_widget.py module_detector.py main.py; do
    [ -f "$PROJECT_ROOT/$f" ] && cp "$PROJECT_ROOT/$f" "$OBF_DIR/"
done

ok "Source cœur : $(du -sh "$OBF_DIR" | cut -f1)"

# ─── 3. Compilation du cœur ───
section "3 · Compilation Nuitka du cœur (20–40 min la 1ère fois)"

DATA_ARGS=()
[ -d "$PROJECT_ROOT/icons" ] && DATA_ARGS+=(--include-data-dir="$PROJECT_ROOT/icons=icons")
[ -f "$PROJECT_ROOT/module_registry.json" ] && DATA_ARGS+=(--include-data-file="$PROJECT_ROOT/module_registry.json=.")



set +e
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
    --output-dir="$DIST_ROOT" \
    --output-filename=LOMETA \
    --report="$LOG_FILE.nuitka.xml" \
    "${DATA_ARGS[@]}" \
    "$OBF_DIR/main.py" 2>&1 | tee -a "$LOG_FILE"
CORE_EXIT=${PIPESTATUS[0]}
set -e

[ "$CORE_EXIT" -eq 0 ] || die "Compilation du cœur échouée (exit=$CORE_EXIT)"

# Localiser le .dist
DIST_DIR=$(find "$DIST_ROOT" -maxdepth 1 -type d -name "*.dist" | head -n1)
[ -z "$DIST_DIR" ] && die "Dossier .dist introuvable dans $DIST_ROOT"
export DIST_DIR
BINARY="$DIST_DIR/LOMETA"
[ -f "$BINARY" ] || die "Binaire LOMETA introuvable dans $DIST_DIR"

chmod +x "$BINARY"
ok "Cœur compilé : $BINARY ($(du -h "$BINARY" | cut -f1))"

# ─── 4. Compilation des addons (via fonction partagée) ───
section "4 · Compilation des addons en modules natifs"

mkdir -p "$ADDONS_BUILD" "$DIST_DIR/addons"

ADDONS_TO_BUILD=()
for pkg in "$ADDONS_SRC"/*/; do
    [ -d "$pkg" ] || continue
    ADDONS_TO_BUILD+=("$(basename "$pkg")")
done
[ ${#ADDONS_TO_BUILD[@]} -eq 0 ] && warn "Aucun addon à compiler"

echo -e "${WHITE}🎯 Addons à compiler : ${ADDONS_TO_BUILD[*]}${NC}"

FAILED_ADDONS=()
SUCCESS_ADDONS=()

for name in "${ADDONS_TO_BUILD[@]}"; do
    if prepare_addon_source "$name" && compile_addon "$name" && install_addon "$name"; then
        SUCCESS_ADDONS+=("$name")
    else
        FAILED_ADDONS+=("$name")
    fi
done

# Copier les métadonnées racine
[ -f "$PROJECT_ROOT/module_registry.json" ] && cp "$PROJECT_ROOT/module_registry.json" "$DIST_DIR/"
[ -f "$PROJECT_ROOT/.env" ] && cp "$PROJECT_ROOT/.env" "$DIST_DIR/" 2>/dev/null || true

# Créer le dossier data/ (utilisé par l'app pour les PDF)
mkdir -p "$DIST_DIR/data/evaluations"

# Résultat addons
if [ ${#SUCCESS_ADDONS[@]} -gt 0 ]; then
    ok "Addons compilés : ${#SUCCESS_ADDONS[@]} → ${SUCCESS_ADDONS[*]}"
fi
if [ ${#FAILED_ADDONS[@]} -gt 0 ]; then
    for f in "${FAILED_ADDONS[@]}"; do
        echo -e "${RED}  ✗ $f${NC}"
    done
    die "Certains addons n'ont pas été compilés"
fi

# ─── 5. Vérifications de protection ───
section "5 · Vérification de la protection"

# 5a. Aucun .py du cœur exposé
LEAKED_CORE=$(find "$DIST_DIR" -name "*.py" \
    \( -path "*/core/*" -o -path "*/server/*" -o -path "*/icons/*" \) 2>/dev/null | wc -l)
[ "$LEAKED_CORE" -gt 0 ] && die "$LEAKED_CORE fichiers .py du cœur exposés !"
ok "Aucun .py du cœur dans le dist"

# 5b. Aucun .py dans les addons
LEAKED_ADDONS=$(find "$DIST_DIR/addons" -name "*.py" 2>/dev/null | wc -l)
[ "$LEAKED_ADDONS" -gt 0 ] && die "$LEAKED_ADDONS fichiers .py exposés dans addons/ !"
ok "Aucun .py dans addons/ (tout est .so)"

# 5c. Chaque addon a bien son .so avec suffixe ABI
for d in "$DIST_DIR/addons"/*/; do
    [ -d "$d" ] || continue
    name=$(basename "$d")
    so_count=$(find "$d" -maxdepth 1 -name "__init*.so" | wc -l)
    [ "$so_count" -eq 0 ] && die "$name/__init*.so manquant"
    verify_so "$(find "$d" -maxdepth 1 -name "__init*.so" | head -n1)" "$name"
done
ok "Tous les addons ont un .so valide"

# 5d. Code métier non lisible
if strings "$BINARY" 2>/dev/null | grep -qE "def create_vehicle|def get_rc_premium|class VehicleController"; then
    die "Code source Python lisible dans le binaire !"
fi
ok "Aucun code métier lisible dans le binaire"

# 5e. Type ELF
file "$BINARY" | tee -a "$LOG_FILE"

DIST_SIZE=$(du -sh "$DIST_DIR" | cut -f1)
echo -e "${BLUE}📊 Taille totale : $DIST_SIZE${NC}"

# ─── 6. Packaging ───
if [ "$DO_ZIP" -eq 1 ]; then
    section "6 · Packaging de la distribution"

    ZIP_NAME="$PROJECT_ROOT/LOMETA_linux_$(date +%Y%m%d_%H%M%S).zip"
    (cd "$DIST_ROOT" && zip -r9 "$ZIP_NAME" . >/dev/null 2>&1)
    [ -f "$ZIP_NAME" ] || die "Échec création du ZIP"
    ok "Archive : $ZIP_NAME ($(du -h "$ZIP_NAME" | cut -f1))"
fi

section "6 · Manifeste de distribution"

VERSION=$(grep -oP '"version"\s*:\s*"\K[^"]+' "$PROJECT_ROOT/module_registry.json" | head -n1 || echo "0.0.0")
[ -z "$VERSION" ] && VERSION="dev-$(date +%Y%m%d)"

MANIFEST="$DIST_ROOT/manifest.json"
bash "$SCRIPT_DIR/generate_manifest.sh" "$DIST_DIR" "$VERSION" "$MANIFEST"

# Signature RSA (optionnelle, si la clé existe)
if [ -f "$PROJECT_ROOT/lometa_module_generator/lometa_private_key.pem" ]; then
    openssl dgst -sha256 -sign "$PROJECT_ROOT/lometa_module_generator/lometa_private_key.pem" \
        -out "$MANIFEST.sig" "$MANIFEST"
    ok "Manifeste signé : $MANIFEST.sig"
else
    warn "Clé privée absente — manifeste non signé"
fi

ok "Manifeste : $MANIFEST ($(du -h "$MANIFEST" | cut -f1))"
# Nettoyage des artefacts intermédiaires
rm -rf "$ADDONS_BUILD" "$PROJECT_ROOT/src_clean" 2>/dev/null || true

# ─── 7. Résumé ───
section "7 · Compilation terminée"

echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${WHITE}            ✅ COMPILATION SÉCURISÉE RÉUSSIE                    ${GREEN}║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${WHITE}📦 Binaire   :${NC}  ${CYAN}$BINARY${NC}"
echo -e "${WHITE}📂 Dist      :${NC}  ${CYAN}$DIST_DIR${NC}  ($DIST_SIZE)"
[ "$DO_ZIP" -eq 1 ] && echo -e "${WHITE}🗜  Archive   :${NC}  ${CYAN}$ZIP_NAME${NC}"
echo -e "${WHITE}📋 Log       :${NC}  ${CYAN}$LOG_FILE${NC}"
echo ""
echo -e "${YELLOW}🧪 Tester :${NC}"
echo -e "   ${CYAN}cd $DIST_DIR && ./LOMETA${NC}"
echo ""

log "Compilation terminée avec succès"