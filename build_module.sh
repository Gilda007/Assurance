#!/bin/bash
# ============================================================
#  LOMETA - Compilation autonome d'un module en .so
#  Compile addons/<Name> en modules .so individuels (--standalone)
#  Installe dans dist_secure/*.dist/addons/<Name>/
#  Regenere le certificat sur les .so produits
#
#  Usage :
#    bash build_module.sh <Name>              # compile
#    bash build_module.sh <Name> --clean      # nettoie + compile
#    bash build_module.sh <Name> --cert-only  # certificat seul
#    bash build_module.sh --list              # liste les modules
# ============================================================

set -e

# --- Couleurs ASCII ---
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
#  Chemins absolus (independants du CWD)
# ============================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
ADDONS_SRC="$PROJECT_ROOT/addons"
ADDONS_BUILD="$PROJECT_ROOT/addons_compiled"
DIST_ROOT="$PROJECT_ROOT/dist_secure"

export PYTHON="${PYTHON:-python3}"
export PY_ABI_SUFFIX=$("$PYTHON" -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))" 2>/dev/null || echo ".so")

LOG_FILE="$PROJECT_ROOT/build_module_$(date +%Y%m%d_%H%M%S).log"

# ============================================================
#  Parsing des arguments
# ============================================================
if [ $# -eq 0 ]; then
    printf "Usage : bash build_module.sh <Name> [--clean] [--cert-only]\n"
    printf "        bash build_module.sh --list\n"
    exit 1
fi

if [ "$1" = "--list" ] || [ "$1" = "-l" ]; then
    printf "Modules disponibles :\n"
    for pkg in "$ADDONS_SRC"/*/; do
        [ -d "$pkg" ] || continue
        name=$(basename "$pkg")
        marker=""
        [ -d "$DIST_ROOT" ] && find "$DIST_ROOT" -maxdepth 3 -type d -path "*/addons/$name" 2>/dev/null | grep -q . && marker=" [compiled]"
        printf "  - %s%s\n" "$name" "$marker"
    done
    exit 0
fi

MODULE_NAME="$1"
shift || true

DO_CLEAN=0
CERT_ONLY=0
while [ $# -gt 0 ]; do
    case "$1" in
        --clean)     DO_CLEAN=1 ;;
        --cert-only) CERT_ONLY=1 ;;
        *) log_warn "Argument inconnu : $1" ;;
    esac
    shift
done

# ============================================================
#  Verification de l'environnement
# ============================================================
section "0/6 - Verification de l'environnement"

[ -d "$ADDONS_SRC/$MODULE_NAME" ] || die "Module introuvable : addons/$MODULE_NAME/"
command -v "$PYTHON" >/dev/null || die "python3 introuvable"
command -v rsync >/dev/null || die "rsync requis (apt install rsync)"
command -v gcc >/dev/null || die "gcc requis (apt install build-essential)"

if ! "$PYTHON" -m nuitka --version >/dev/null 2>&1; then
    log_warn "Nuitka manquant - installation..."
    "$PYTHON" -m pip install --upgrade "nuitka>=2.7" ordered-set zstandard || \
        die "Echec installation Nuitka"
fi

NUITKA_VER=$("$PYTHON" -m nuitka --version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -n1)
log_info "Python : $("$PYTHON" --version) (ABI: $PY_ABI_SUFFIX)"
log_info "Nuitka : $NUITKA_VER"
log_info "Module : $MODULE_NAME"
log_info "Log    : $LOG_FILE"

# ============================================================
#  Localiser le dist
# ============================================================
section "1/6 - Localisation du dist"

DIST_DIR=$(find "$DIST_ROOT" -maxdepth 1 -type d -name "*.dist" 2>/dev/null | head -n1)
[ -z "$DIST_DIR" ] && die "Aucun dist_secure/*.dist. Lancez build_windows.sh d'abord."

DIST_DIR_ABS="$(cd "$(dirname "$DIST_DIR")" && pwd)/$(basename "$DIST_DIR")"
ADDONS_DEST="$DIST_DIR_ABS/addons"
mkdir -p "$ADDONS_DEST"

log_ok "Dist : $DIST_DIR_ABS"
log_ok "Cible addons : $ADDONS_DEST"

# ============================================================
#  Mode --cert-only : regenerer le certificat et sortir
# ============================================================
if [ "$CERT_ONLY" -eq 1 ]; then
    section "Certificat seul - $MODULE_NAME"
    TARGET_DIR="$ADDONS_DEST/$MODULE_NAME"
    [ -d "$TARGET_DIR" ] || die "Module non installe : $TARGET_DIR"

    regenerate_certificate "$MODULE_NAME" "$TARGET_DIR"
    log_ok "Certificat regenere : $TARGET_DIR/certificate.json"
    exit 0
fi

# ============================================================
#  Nettoyage optionnel
# ============================================================
if [ "$DO_CLEAN" -eq 1 ]; then
    section "1bis - Nettoyage de $MODULE_NAME"
    rm -rf "$ADDONS_BUILD/$MODULE_NAME"
    rm -rf "$ADDONS_BUILD/addons/$MODULE_NAME"
    rm -rf "$ADDONS_BUILD/_standalone/$MODULE_NAME"
    rm -rf "$ADDONS_DEST/$MODULE_NAME"
    log_ok "Ancien build supprime"
fi

# ============================================================
#  Preparation de la source
# ============================================================
section "2/6 - Preparation de la source"

SRC="$ADDONS_SRC/$MODULE_NAME"
META_DIR="$ADDONS_BUILD/$MODULE_NAME"
DST="$ADDONS_BUILD/addons/$MODULE_NAME"

mkdir -p "$META_DIR"
rm -rf "$DST"
mkdir -p "$DST"

rsync -a \
    --exclude='.history' --exclude='__pycache__' \
    --exclude='*.pyc' --exclude='*.pyo' \
    --exclude='test_*.py' --exclude='.pytest_cache' \
    --exclude='*.db' --exclude='*.sqlite' \
    --exclude='_build' --exclude='*.so' \
    "$SRC/" "$DST/"

if [ ! -f "$DST/__init__.py" ]; then
    log_warn "Creation de __init__.py manquant"
    printf '"""%s addon package."""\n' "$MODULE_NAME" > "$DST/__init__.py"
fi

# Conteneur addons/ (pour resoudre import addons.<Name>)
if [ ! -f "$ADDONS_BUILD/addons/__init__.py" ]; then
    printf '"""Addons namespace package (build)."""\n' > "$ADDONS_BUILD/addons/__init__.py"
fi

log_ok "Source preparee : $DST"

# ============================================================
#  Scan : detection des packages et modules
# ============================================================
section "3/6 - Scan du module"

INCLUDE_ARGS=()
_seen=" "

_add_include() {
    local arg="$1"
    case "$_seen" in
        *" $arg "*) return 0 ;;
    esac
    _seen+="$arg "
    INCLUDE_ARGS+=("$arg")
}

# 1. Package racine
_add_include "--include-package=addons.$MODULE_NAME"

# 2. Sous-packages (dossiers avec __init__.py)
while IFS= read -r init_file; do
    [ -z "$init_file" ] && continue
    rel="${init_file#$DST/}"
    dir=$(dirname "$rel")
    [ "$dir" = "." ] && continue
    dotted=$(printf "%s" "$dir" | tr '/' '.')
    _add_include "--include-package=addons.$MODULE_NAME.$dotted"
done < <(find "$DST" -type f -name "__init__.py" 2>/dev/null | sort)

# 3. Modules .py isoles
while IFS= read -r py_file; do
    [ -z "$py_file" ] && continue
    base=$(basename "$py_file" .py)
    [ "$base" = "__init__" ] && continue
    rel="${py_file#$DST/}"
    rel_noext="${rel%.py}"
    dotted=$(printf "%s" "$rel_noext" | tr '/' '.')
    _add_include "--include-module=addons.$MODULE_NAME.$dotted"
done < <(find "$DST" -type f -name "*.py" 2>/dev/null | sort)

# 4. Namespace packages (dossiers sans __init__.py, avec du .py)
while IFS= read -r dir_path; do
    [ -z "$dir_path" ] && continue
    [ "$dir_path" = "$DST" ] && continue
    rel="${dir_path#$DST/}"
    # Ignorer techniques
    case "/$rel/" in
        */tests/*|*/migrations/*|*/__pycache__/*|*/_build/*|*/.*)
            continue
            ;;
    esac
    [ -f "$dir_path/__init__.py" ] && continue
    # Doit contenir au moins un .py (recursif)
    if find "$dir_path" -type f -name "*.py" 2>/dev/null | grep -q .; then
        dotted=$(printf "%s" "$rel" | tr '/' '.')
        _add_include "--include-package=addons.$MODULE_NAME.$dotted"
    fi
done < <(find "$DST" -type d 2>/dev/null | sort)

log_info "$MODULE_NAME : ${#INCLUDE_ARGS[@]} inclusions detectees"

# ============================================================
#  Compilation Nuitka --standalone
# ============================================================
section "4/6 - Compilation --standalone (peut prendre 5-15 min)"

BUILD_OUT="$ADDONS_BUILD/_standalone/$MODULE_NAME"
rm -rf "$BUILD_OUT"
mkdir -p "$BUILD_OUT"

# Stub d'entree neutre (Nuitka --standalone exige un point d'entree programme)
STUB_DIR=$(mktemp -d)
STUB_FILE="$STUB_DIR/__main_addon_${MODULE_NAME}.py"
cat > "$STUB_FILE" <<'STUB_EOF'
# Stub neutre - l'inclusion est assuree par --include-package
import sys

if __name__ == "__main__":
    sys.exit(0)
STUB_EOF

NUITKA_LOG="$BUILD_OUT/nuitka.log"
START=$(date +%s)

log_info "Nuitka --standalone en cours..."
set +e
(
    cd "$ADDONS_BUILD"
    "$PYTHON" -m nuitka \
        --standalone \
        --assume-yes-for-downloads \
        --enable-plugin=pyside6 \
        --nofollow-import-to=pytest \
        --nofollow-import-to=tkinter \
        --nofollow-import-to=PyQt5 \
        --nofollow-import-to=PyQt6 \
        --nofollow-import-to=matplotlib \
        "${INCLUDE_ARGS[@]}" \
        --nofollow-import-to="addons.${MODULE_NAME}.tests" \
        --include-package-data="addons.$MODULE_NAME" \
        --output-dir="$BUILD_OUT" \
        --output-filename="__main_addon_${MODULE_NAME}" \
        "$STUB_FILE"
) > "$NUITKA_LOG" 2>&1
EXIT_CODE=$?
set -e

rm -rf "$STUB_DIR"

ELAPSED=$(( $(date +%s) - START ))
[ -s "$LOG_FILE" ] || true
cat "$NUITKA_LOG" >> "$LOG_FILE"

if [ "$EXIT_CODE" -ne 0 ]; then
    log_err "Nuitka exit $EXIT_CODE - voir $NUITKA_LOG"
    grep -iE "error|fatal|traceback" "$NUITKA_LOG" | tail -10 | sed 's/^/    /'
    exit 1
fi

log_ok "Compilation terminee en ${ELAPSED}s"

# ============================================================
#  Extraction des .so vers le dist
# ============================================================
section "5/6 - Installation dans le dist"

STANDALONE_DIR=$(find "$BUILD_OUT" -maxdepth 2 -type d -name "*.dist" | head -n1)
[ -z "$STANDALONE_DIR" ] && die "Dossier *.dist introuvable dans $BUILD_OUT"

ADDON_SO_ROOT="$STANDALONE_DIR/addons/$MODULE_NAME"
[ -d "$ADDON_SO_ROOT" ] || die "Sous-arbre $ADDON_SO_ROOT absent du standalone"

DEST="$ADDONS_DEST/$MODULE_NAME"
rm -rf "$DEST"
mkdir -p "$DEST"

SO_COUNT=0
while IFS= read -r so_file; do
    [ -z "$so_file" ] && continue
    rel="${so_file#$ADDON_SO_ROOT/}"
    # Exclure tests
    case "/$rel" in
        */tests/*) continue ;;
    esac
    target="$DEST/$rel"
    mkdir -p "$(dirname "$target")"
    cp "$so_file" "$target"
    SO_COUNT=$((SO_COUNT + 1))
done < <(find "$ADDON_SO_ROOT" -type f -name "*.so" | sort)

[ "$SO_COUNT" -eq 0 ] && die "Aucun .so trouve sous $ADDON_SO_ROOT"

log_ok "$SO_COUNT fichiers .so installes"

# Donnees non-Python
rsync -a \
    --exclude='*.py' --exclude='__pycache__' \
    --exclude='.history' --exclude='*.pyc' --exclude='*.pyo' \
    --exclude='_build' --exclude='*.db' --exclude='*.sqlite' \
    --exclude='*.so' \
    --exclude='tests/' \
    "$DST/" "$DEST/"

DATA_COUNT=$(find "$DEST" -type f ! -name '*.so' | wc -l)
log_ok "$DATA_COUNT fichiers de donnees copies"

# Nettoyage standalone intermediaire
rm -rf "$STANDALONE_DIR"

# ============================================================
#  Regeneration du certificat
# ============================================================
section "6/6 - Regeneration du certificat"

regenerate_certificate "$MODULE_NAME" "$DEST"

# ============================================================
#  Resume
# ============================================================
printf "\n"
log_ok "=== Module compile : $MODULE_NAME ==="
log_info "  Destination : $DEST"
log_info "  .so         : $SO_COUNT"
log_info "  Donnees     : $DATA_COUNT"
log_info "  Taille      : $(du -sh "$DEST" 2>/dev/null | cut -f1)"
printf "\n"
log_info "Verification :"
find "$DEST" -maxdepth 1 -name "__init*.so" -exec echo "  - {}" \;
printf "\n"
log_info "Lancer : cd $DIST_DIR_ABS && ./LOMETA"
printf "\n"

exit 0