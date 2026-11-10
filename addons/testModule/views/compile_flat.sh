#!/bin/bash
# ============================================================
#  compile_flat.sh - Compilation plate d'un repertoire
#  Compile TOUS les .py du dossier COURANT (PAS recursif)
#  Produit 1 .so par fichier .py via Nuitka --module
#  Installe dans dist_secure/*.dist/addons/<Module>/<sous-rep>/
#
#  Cas special : __init__.py -> compile le DOSSIER en __init.so
# ============================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()  { printf "${BLUE}[INFO]${NC} %s\n" "$1"; }
log_ok()    { printf "${GREEN}[OK]${NC} %s\n" "$1"; }
log_warn()  { printf "${YELLOW}[!]${NC} %s\n" "$1"; }
log_err()   { printf "${RED}[X]${NC} %s\n" "$1" >&2; }
die()       { log_err "$1"; exit 1; }

section() {
    printf "\n${CYAN}============================================================${NC}\n"
    printf "${CYAN}  %s${NC}\n" "$1"
    printf "${CYAN}============================================================${NC}\n"
}

# ============================================================
#  Chemins
# ============================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export PYTHON="${PYTHON:-python3}"
export PY_ABI_SUFFIX=$("$PYTHON" -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))" 2>/dev/null || echo ".so")

LOG_FILE="$SCRIPT_DIR/compile_flat_$(date +%Y%m%d_%H%M%S).log"

# ============================================================
#  Arguments
# ============================================================
if [ "$1" = "--list" ] || [ "$1" = "-l" ]; then
    printf "Fichiers .py dans %s :\n" "$SCRIPT_DIR"
    find "$SCRIPT_DIR" -maxdepth 1 -type f -name "*.py" | sort | while read -r f; do
        printf "  - %s\n" "$(basename "$f")"
    done
    exit 0
fi

DO_CLEAN=0
MODULE_NAME=""
while [ $# -gt 0 ]; do
    case "$1" in
        --clean) DO_CLEAN=1 ;;
        -*) log_warn "Argument inconnu : $1" ;;
        *) MODULE_NAME="$1" ;;
    esac
    shift
done

# ============================================================
#  Trouver PROJECT_ROOT
# ============================================================
CURRENT="$SCRIPT_DIR"
PROJECT_ROOT=""
for i in 1 2 3 4 5 6 7; do
    if [ -d "$CURRENT/dist_secure" ]; then
        PROJECT_ROOT="$CURRENT"
        break
    fi
    PARENT="$(cd "$CURRENT/.." && pwd)"
    [ "$PARENT" = "$CURRENT" ] && break
    CURRENT="$PARENT"
done

[ -z "$PROJECT_ROOT" ] && die "PROJECT_ROOT introuvable"
ADDONS_SRC="$PROJECT_ROOT/addons"
DIST_ROOT="$PROJECT_ROOT/dist_secure"

[ -d "$ADDONS_SRC" ] || die "addons/ introuvable : $ADDONS_SRC"

# ============================================================
#  Nom du module racine
# ============================================================
if [ -z "$MODULE_NAME" ]; then
    TMP="$SCRIPT_DIR"
    for i in 1 2 3 4 5; do
        PARENT="$(cd "$TMP/.." && pwd)"
        if [ "$(basename "$PARENT")" = "addons" ]; then
            MODULE_NAME="$(basename "$TMP")"
            break
        fi
        TMP="$PARENT"
        [ "$TMP" = "/" ] && break
    done
    [ -z "$MODULE_NAME" ] && die "Impossible de detecter le module"
fi

log_info "Dossier    : $SCRIPT_DIR"
log_info "Module     : $MODULE_NAME"

# ============================================================
#  Chemin pointe complet
# ============================================================
REL_FROM_ADDONS="${SCRIPT_DIR#$ADDONS_SRC/}"

if [ "$REL_FROM_ADDONS" = "$SCRIPT_DIR" ]; then
    die "Le dossier n'est pas dans addons/ : $SCRIPT_DIR"
fi

DOTTED_REL=$(printf "%s" "$REL_FROM_ADDONS" | tr '/' '.')
FULL_PREFIX="addons.${DOTTED_REL}"

log_info "Prefixe    : $FULL_PREFIX"

# ============================================================
#  Verifications
# ============================================================
section "0/5 - Verification de l'environnement"

command -v "$PYTHON" >/dev/null || die "python3 introuvable"
command -v gcc >/dev/null || die "gcc requis"

if ! "$PYTHON" -m nuitka --version >/dev/null 2>&1; then
    die "Nuitka non installe : $PYTHON -m pip install nuitka"
fi

NUITKA_VER=$("$PYTHON" -m nuitka --version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -n1)

log_info "Python     : $("$PYTHON" --version)"
log_info "Nuitka     : $NUITKA_VER"
log_info "ABI        : $PY_ABI_SUFFIX"
log_info "Log        : $LOG_FILE"

find "$SCRIPT_DIR" -maxdepth 1 -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# ============================================================
#  Lister les .py
# ============================================================
section "1/5 - Fichiers .py du dossier courant"

PY_FILES=()
while IFS= read -r f; do
    [ -z "$f" ] && continue
    PY_FILES+=("$f")
done < <(find "$SCRIPT_DIR" -maxdepth 1 -type f -name "*.py" | sort)

if [ ${#PY_FILES[@]} -eq 0 ]; then
    die "Aucun fichier .py dans $SCRIPT_DIR"
fi

log_info "${#PY_FILES[@]} fichier(s) .py :"
for f in "${PY_FILES[@]}"; do
    printf "  - %s\n" "$(basename "$f")"
done

# ============================================================
#  Localiser le dist  (CORRIGE : ajout de /addons/ dans DEST)
# ============================================================
section "2/5 - Localisation du dist"

DIST_DIR=$(find "$DIST_ROOT" -maxdepth 1 -type d -name "*.dist" 2>/dev/null | head -n1)
[ -z "$DIST_DIR" ] && die "Aucun dist_secure/*.dist. Lancez build_windows.sh d'abord."

DIST_DIR_ABS="$(cd "$(dirname "$DIST_DIR")" && pwd)/$(basename "$DIST_DIR")"

# /addons/ est OBLIGATOIRE pour que addons.<Module> soit importable
DEST="$DIST_DIR_ABS/addons/$REL_FROM_ADDONS"

if [ "$DO_CLEAN" -eq 1 ]; then
    log_info "Nettoyage : $DEST"
    rm -rf "$DEST"
fi
mkdir -p "$DEST"

log_ok "Dist   : $DIST_DIR_ABS"
log_ok "Cible  : $DEST"

# ============================================================
#  Compilation (CORRIGE : __init__.py -> dossier)
# ============================================================
section "3/5 - Compilation Nuitka --module (1 .so par fichier)"

BUILD_ROOT="$SCRIPT_DIR/_build_flat"
[ "$DO_CLEAN" -eq 1 ] && rm -rf "$BUILD_ROOT"
mkdir -p "$BUILD_ROOT"

SO_SUCCESS=0
SO_FAILED=0
FAILED_NAMES=()

for py_file in "${PY_FILES[@]}"; do
    base=$(basename "$py_file" .py)
    FULL_NAME="${FULL_PREFIX}.${base}"

    BUILD_OUT="$BUILD_ROOT/$base"
    rm -rf "$BUILD_OUT"
    mkdir -p "$BUILD_OUT"

    NUITKA_LOG="$BUILD_OUT/nuitka.log"

    # --- CAS SPECIAL : __init__.py ---
    # Nuitka refuse --module sur un __init__.py.
    # Il faut passer le DOSSIER pour produire __init.so.
    if [ "$base" = "__init__" ]; then
        log_info "Compilation : $FULL_NAME (dossier $REL_FROM_ADDONS)"

        set +e
        (
            cd "$ADDONS_SRC"
            "$PYTHON" -m nuitka \
                --module \
                --assume-yes-for-downloads \
                --enable-plugin=pyside6 \
                --nofollow-import-to=pytest \
                --nofollow-import-to=tkinter \
                --nofollow-import-to=PyQt5 \
                --nofollow-import-to=PyQt6 \
                --nofollow-import-to=matplotlib \
                --nofollow-import-to="addons.${MODULE_NAME}.tests" \
                --no-pyi-file \
                --output-dir="$BUILD_OUT" \
                "$REL_FROM_ADDONS"
        ) > "$NUITKA_LOG" 2>&1
        EXIT_CODE=$?
        set -e

        cat "$NUITKA_LOG" >> "$LOG_FILE"

        if [ "$EXIT_CODE" -ne 0 ]; then
            log_err "Echec Nuitka pour $FULL_NAME (exit=$EXIT_CODE)"
            grep -iE "error|fatal|traceback" "$NUITKA_LOG" | tail -5 | sed 's/^/    /'
            SO_FAILED=$((SO_FAILED + 1))
            FAILED_NAMES+=("$FULL_NAME")
            continue
        fi

        # Le .so produit s'appelle __init*.so (ou <dossier>*.so selon Nuitka)
        SO_FILE=$(find "$BUILD_OUT" -maxdepth 2 -type f -name "__init*.so" 2>/dev/null | head -n1)
        [ -z "$SO_FILE" ] && SO_FILE=$(find "$BUILD_OUT" -type f -name "*.so" 2>/dev/null | head -n1)

        if [ -z "$SO_FILE" ]; then
            log_err "Aucun .so produit pour $FULL_NAME"
            SO_FAILED=$((SO_FAILED + 1))
            FAILED_NAMES+=("$FULL_NAME")
            continue
        fi

        cp "$SO_FILE" "$DEST/"
        SO_SIZE=$(du -h "$SO_FILE" | cut -f1)
        log_ok "  __init$PY_ABI_SUFFIX ($SO_SIZE)"
        SO_SUCCESS=$((SO_SUCCESS + 1))
        continue
    fi

    # --- CAS NORMAL : fichier .py ---
    log_info "Compilation : $FULL_NAME ($base.py)"

    set +e
    (
        cd "$ADDONS_SRC"
        "$PYTHON" -m nuitka \
            --module \
            --assume-yes-for-downloads \
            --enable-plugin=pyside6 \
            --nofollow-import-to=pytest \
            --nofollow-import-to=tkinter \
            --nofollow-import-to=PyQt5 \
            --nofollow-import-to=PyQt6 \
            --nofollow-import-to=matplotlib \
            --nofollow-import-to="addons.${MODULE_NAME}.tests" \
            --no-pyi-file \
            --output-dir="$BUILD_OUT" \
            "$py_file"
    ) > "$NUITKA_LOG" 2>&1
    EXIT_CODE=$?
    set -e

    cat "$NUITKA_LOG" >> "$LOG_FILE"

    if [ "$EXIT_CODE" -ne 0 ]; then
        log_err "Echec Nuitka pour $base.py (exit=$EXIT_CODE)"
        grep -iE "error|fatal|traceback" "$NUITKA_LOG" | tail -5 | sed 's/^/    /'
        SO_FAILED=$((SO_FAILED + 1))
        FAILED_NAMES+=("$base")
        continue
    fi

    SO_FILE=$(find "$BUILD_OUT" -maxdepth 2 -type f -name "${base}*.so" 2>/dev/null | head -n1)
    [ -z "$SO_FILE" ] && SO_FILE=$(find "$BUILD_OUT" -type f -name "*.so" 2>/dev/null | head -n1)

    if [ -z "$SO_FILE" ]; then
        log_err "Aucun .so produit pour $base.py"
        SO_FAILED=$((SO_FAILED + 1))
        FAILED_NAMES+=("$base")
        continue
    fi

    cp "$SO_FILE" "$DEST/"
    SO_SIZE=$(du -h "$SO_FILE" | cut -f1)
    log_ok "  $base$PY_ABI_SUFFIX ($SO_SIZE)"
    SO_SUCCESS=$((SO_SUCCESS + 1))
done

# ============================================================
#  Copier les donnees
# ============================================================
section "4/5 - Copie des donnees (fichiers non-Python)"

rsync -a \
    --exclude='*.py' --exclude='__pycache__' \
    --exclude='.history' --exclude='*.pyc' --exclude='*.pyo' \
    --exclude='_build_flat' --exclude='*.db' --exclude='*.sqlite' \
    --exclude='*.so' --exclude='compile_flat*.log' \
    "$SCRIPT_DIR/" "$DEST/"

DATA_COUNT=$(find "$DEST" -maxdepth 1 -type f ! -name '*.so' ! -name 'compile_flat*.log' | wc -l)
log_ok "$DATA_COUNT fichier(s) de donnees copies"

# ============================================================
#  Resume
# ============================================================
section "5/5 - Resultat"

SO_COUNT=$(find "$DEST" -maxdepth 1 -name "*.so" -type f | wc -l)
TOTAL_SIZE=$(du -sh "$DEST" 2>/dev/null | cut -f1)

log_ok "=== Compilation terminee : $FULL_PREFIX ==="
log_info "  Destination : $DEST"
log_info "  .so reussis  : $SO_SUCCESS / ${#PY_FILES[@]}"
log_info "  .so echoues  : $SO_FAILED"
log_info "  .so presents : $SO_COUNT"
log_info "  Donnees      : $DATA_COUNT"
log_info "  Taille       : $TOTAL_SIZE"

if [ ${#FAILED_NAMES[@]} -gt 0 ]; then
    printf "\n"
    log_warn "Fichiers echoues :"
    for f in "${FAILED_NAMES[@]}"; do
        printf "  - %s\n" "$f"
    done
fi

printf "\n"
log_info "Contenu final :"
find "$DEST" -maxdepth 1 -name "*.so" -exec basename {} \; | sort | sed 's/^/  /'

printf "\n"
log_info "Test import :"
printf "  cd %s\n" "$DIST_DIR_ABS"
printf "  python3 -c \"import sys; sys.path.insert(0,'.'); import %s\"\n" "$FULL_PREFIX"

printf "\n"

[ "$SO_FAILED" -gt 0 ] && exit 1
exit 0