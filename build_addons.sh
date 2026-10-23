#!/bin/bash
# ============================================================
#  LOMETA — Compilation des addons en modules .so
#  Utilise Nuitka --module (Option A)
#  Peut être lancé indépendamment du build principal
# ============================================================
#  Usage :
#    ./build_addons.sh                       # tous les addons
#    ./build_addons.sh Automobiles           # un seul addon
#    ./build_addons.sh Automobiles sinistres # plusieurs addons
#    ./build_addons.sh --list                # lister les addons
#    ./build_addons.sh --clean               # nettoyer les builds
# ============================================================

set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; WHITE='\033[1;37m'; NC='\033[0m'

LOG_FILE="build_addons_$(date +%Y%m%d_%H%M%S).log"
PYTHON=${PYTHON:-python3}

log()     { echo "$1" | tee -a "$LOG_FILE"; }
section() {
    echo -e "\n${CYAN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}  $1${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
}
die() { echo -e "${RED}✗ $1${NC}"; exit 1; }

# ============================================================
# Chemins absolus (CWD-independent)
# ============================================================
PROJECT_ROOT="$(pwd)"
ADDONS_SRC="$PROJECT_ROOT/addons"
ADDONS_BUILD="$PROJECT_ROOT/addons_compiled"

# Détection du dossier .dist (main.dist ou LOMETA.dist)
DIST_DIR=""
if [ -d "$PROJECT_ROOT/dist_secure" ]; then
    DIST_DIR=$(find "$PROJECT_ROOT/dist_secure" -maxdepth 1 -type d -name "*.dist" | head -n1)
fi
if [ -z "$DIST_DIR" ]; then
    die "Aucun dossier dist_secure/*.dist trouvé. Lancez d'abord build_windows.sh (partie cœur)."
fi
ADDONS_DEST="$DIST_DIR/addons"

# ============================================================
# Gestion des arguments
# ============================================================
SELECTED=()
DO_CLEAN=0

for arg in "$@"; do
    case "$arg" in
        --list)
            echo -e "${WHITE}Addons disponibles :${NC}"
            for pkg in "$ADDONS_SRC"/*/; do
                [ -d "$pkg" ] || continue
                echo -e "  • $(basename "$pkg")"
            done
            exit 0
            ;;
        --clean)
            DO_CLEAN=1
            ;;
        --help|-h)
            sed -n '2,15p' "$0"
            exit 0
            ;;
        *)
            SELECTED+=("$arg")
            ;;
    esac
done

# ============================================================
# Nettoyage optionnel
# ============================================================
if [ "$DO_CLEAN" -eq 1 ]; then
    section "Nettoyage"
    rm -rf "$ADDONS_BUILD"
    if [ ${#SELECTED[@]} -eq 0 ]; then
        # Nettoyer tous les addons dans le dist aussi
        find "$ADDONS_DEST" -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} + 2>/dev/null || true
        echo -e "${GREEN}✓ Tous les builds et addons compilés supprimés${NC}"
    else
        for name in "${SELECTED[@]}"; do
            rm -rf "$ADDONS_BUILD/$name" "$ADDONS_DEST/$name"
            echo -e "${GREEN}✓ $name nettoyé${NC}"
        done
    fi
    [ ${#SELECTED[@]} -eq 0 ] && exit 0
fi

# ============================================================
# Environnement
# ============================================================
section "0/4 · Vérification de l'environnement"

[ -d "$ADDONS_SRC" ] || die "Dossier addons/ source introuvable à $ADDONS_SRC"
command -v rsync >/dev/null || die "rsync requis"
command -v gcc   >/dev/null || die "gcc requis"

if ! $PYTHON -m nuitka --version &>/dev/null; then
    die "Nuitka non installé. Lancez : $PYTHON -m pip install nuitka ordered-set zstandard"
fi

NUITKA_VER=$($PYTHON -m nuitka --version 2>/dev/null | head -n1)
echo -e "${BLUE}🐍 Python : $($PYTHON --version)${NC}"
echo -e "${BLUE}🔨 Nuitka : $NUITKA_VER${NC}"
echo -e "${BLUE}📂 Source  : $ADDONS_SRC${NC}"
echo -e "${BLUE}📦 Cible   : $ADDONS_DEST${NC}"
echo -e "${BLUE}📋 Log     : $LOG_FILE${NC}"

mkdir -p "$ADDONS_BUILD" "$ADDONS_DEST"

# ============================================================
# Déterminer la liste des addons à compiler
# ============================================================
if [ ${#SELECTED[@]} -eq 0 ]; then
    ADDONS_TO_BUILD=()
    for pkg in "$ADDONS_SRC"/*/; do
        [ -d "$pkg" ] || continue
        ADDONS_TO_BUILD+=("$(basename "$pkg")")
    done
else
    ADDONS_TO_BUILD=("${SELECTED[@]}")
fi

if [ ${#ADDONS_TO_BUILD[@]} -eq 0 ]; then
    die "Aucun addon à compiler"
fi

echo -e "\n${WHITE}🎯 Addons à compiler (${#ADDONS_TO_BUILD[@]}) :${NC}"
for name in "${ADDONS_TO_BUILD[@]}"; do
    echo -e "  • ${CYAN}$name${NC}"
done

# ============================================================
# 1. Préparation (copie propre)
# ============================================================
section "1/4 · Préparation des sources"

for name in "${ADDONS_TO_BUILD[@]}"; do
    src="$ADDONS_SRC/$name"
    dst="$ADDONS_BUILD/$name"

    if [ ! -d "$src" ]; then
        echo -e "${RED}✗ Addon introuvable : $name${NC}"
        continue
    fi

    # Nettoyage ciblé
    rm -rf "$dst"
    mkdir -p "$dst"

    rsync -a \
        --exclude='.history' --exclude='__pycache__' \
        --exclude='*.pyc' --exclude='*.pyo' \
        --exclude='test_*.py' --exclude='.pytest_cache' \
        --exclude='*.db' --exclude='*.sqlite' \
        "$src/" "$dst/"

    # Garantir un __init__.py (nécessaire pour --module)
    if [ ! -f "$dst/__init__.py" ]; then
        echo -e "${YELLOW}  ⚠ $name/__init__.py absent — création${NC}"
        printf '# Auto-generated for Nuitka --module\n' > "$dst/__init__.py"
    fi

    echo -e "${GREEN}✓ $name prêt${NC}"
done

# ============================================================
# 2. Compilation Nuitka --module (avec inclusion récursive)
# ============================================================
section "2/5 · Compilation Nuitka --module"

SUCCESS=()
FAILED=()

for name in "${ADDONS_TO_BUILD[@]}"; do
    pkg="$ADDONS_BUILD/$name"
    [ -d "$pkg" ] || continue

    echo -e "\n${CYAN}──────────────────────────────────────────────────────────${NC}"
    echo -e "${WHITE}  → $name${NC}"
    echo -e "${CYAN}──────────────────────────────────────────────────────────${NC}"

    BUILD_OUT="$pkg/_build"
    rm -rf "$BUILD_OUT"
    mkdir -p "$BUILD_OUT"

    # ---- AUTO-DÉCOUVERTE des sous-packages et sous-modules ----
    INCLUDE_ARGS=()

    # 1. Le package racine
    INCLUDE_ARGS+=(--include-package="addons.$name")

    # 2. Tous les sous-packages (dossiers contenant __init__.py)
    while IFS= read -r subpkg_init; do
        [ -z "$subpkg_init" ] && continue
        rel_path="${subpkg_init#$pkg/}"
        rel_dir=$(dirname "$rel_path")
        [ "$rel_dir" = "." ] && continue
        dotted=$(echo "$rel_dir" | tr '/' '.')
        INCLUDE_ARGS+=(--include-package="addons.$name.$dotted")
    done < <(find "$pkg" -type f -name "__init__.py" 2>/dev/null | sort)

    # 3. Tous les modules .py isolés (qui ne sont pas __init__.py)
    while IFS= read -r py_file; do
        [ -z "$py_file" ] && continue
        basename_py=$(basename "$py_file" .py)
        [ "$basename_py" = "__init__" ] && continue
        rel_path="${py_file#$pkg/}"
        rel_noext="${rel_path%.py}"
        dotted=$(echo "$rel_noext" | tr '/' '.')
        INCLUDE_ARGS+=(--include-module="addons.$name.$dotted")
    done < <(find "$pkg" -type f -name "*.py" 2>/dev/null | sort)

    # ══════════════════════════════════════════════════════════════
    # 4. ICI : dossiers SANS __init__.py → namespace packages
    # ══════════════════════════════════════════════════════════════
    while IFS= read -r dir; do
        [ -z "$dir" ] && continue
        [ "$dir" = "$pkg" ] && continue

        rel="${dir#$pkg/}"
        # Ignorer les dossiers techniques
        echo "$rel" | grep -qE '^(\.|_|tests?/|migrations/|__pycache__)' && continue

        # Ne pas ajouter si déjà couvert par un __init__.py (étape 2)
        [ -f "$dir/__init__.py" ] && continue

        # Ne pas ajouter si un fichier .py du même nom est déjà inclus
        # (évite les doublons --include-package / --include-module)
        dotted=$(echo "$rel" | tr '/' '.')
        INCLUDE_ARGS+=(--include-package="addons.$name.$dotted")
    done < <(find "$pkg" -type d 2>/dev/null | sort)
    # ══════════════════════════════════════════════════════════════

    echo -e "${BLUE}  📦 ${#INCLUDE_ARGS[@]} inclusions détectées${NC}"

    # ---- Compilation ----
    START=$(date +%s)
    NUITKA_LOG="$BUILD_OUT/nuitka.log"

    set +e
    $PYTHON -m nuitka \
        --module \
        --assume-yes-for-downloads \
        --enable-plugin=pyside6 \
        --nofollow-import-to=pytest \
        --nofollow-import-to=tkinter \
        --nofollow-import-to=PyQt5 \
        --nofollow-import-to=PyQt6 \
        --nofollow-import-to=matplotlib \
        "${INCLUDE_ARGS[@]}" \
        --include-package-data="addons.$name" \
        --output-dir="$BUILD_OUT" \
        --no-pyi-file \
        "$pkg" > "$NUITKA_LOG" 2>&1
    NUITKA_EXIT=$?
    set -e

    ELAPSED=$(( $(date +%s) - START ))
    cat "$NUITKA_LOG" >> "$LOG_FILE"

    if [ "$NUITKA_EXIT" -ne 0 ]; then
        echo -e "${RED}  ✗ Nuitka exit $NUITKA_EXIT${NC}"
        grep -iE "error|fatal|traceback" "$NUITKA_LOG" | tail -8 | sed 's/^/    /'
        FAILED+=("$name (exit=$NUITKA_EXIT)")
        continue
    fi

    # Vérifier les .so produites
    SO_COUNT=$(find "$BUILD_OUT" -maxdepth 1 -type f -name "*.so" | wc -l)
    echo -e "${GREEN}  ✓ ${ELAPSED}s · ${SO_COUNT} .so générée(s)${NC}"

    find "$BUILD_OUT" -maxdepth 1 -type f -name "*.so" -exec ls -lh {} \; \
        | awk '{print "    " $9 " (" $5 ")"}'

    SUCCESS+=("$name|$BUILD_OUT|$ELAPSED")
done


# ============================================================
# 3. Installation dans le dist (arborescence préservée)
# ============================================================
section "3/5 · Installation dans le dist"

for entry in "${SUCCESS[@]}"; do
    IFS='|' read -r name build_out elapsed <<< "$entry"

    dest="$ADDONS_DEST/$name"
    rm -rf "$dest"
    mkdir -p "$dest"

    # Copier TOUS les .so en préservant l'arborescence relative
    # (les .so sont soit à la racine, soit dans _build/addons/X/...)
    while IFS= read -r so_file; do
        [ -z "$so_file" ] && continue

        # Chemin relatif depuis build_out
        rel="${so_file#$build_out/}"

        # Si le chemin contient "addons/<name>/", on extrait la partie après
        if echo "$rel" | grep -q "^addons/$name/"; then
            sub_rel="${rel#addons/$name/}"
        else
            sub_rel="$rel"
        fi

        target="$dest/$sub_rel"
        mkdir -p "$(dirname "$target")"
        cp "$so_file" "$target"
    done < <(find "$build_out" -type f -name "*.so" | sort)

    # Copier les données non-Python
    rsync -a \
        --exclude='*.py' --exclude='__pycache__' \
        --exclude='.history' --exclude='*.pyc' \
        --exclude='_build' --exclude='*.db' --exclude='*.sqlite' \
        --exclude='*.so' \
        "$ADDONS_BUILD/$name/" "$dest/"

    SO_NB=$(find "$dest" -name "*.so" | wc -l)
    echo -e "${GREEN}  ✓ $name → $SO_NB .so + $(find "$dest" -type f ! -name '*.so' | wc -l) données${NC}"
done
# ============================================================
# 4. Résumé
# ============================================================
section "4/4 · Résumé"

echo -e "${WHITE}📊 Résultats :${NC}"
echo -e "   ${GREEN}✓ Succès  : ${#SUCCESS[@]}${NC}"
echo -e "   ${RED}✗ Échecs  : ${#FAILED[@]}${NC}"

if [ ${#SUCCESS[@]} -gt 0 ]; then
    echo -e "\n${WHITE}✓ Addons compilés :${NC}"
    for entry in "${SUCCESS[@]}"; do
        IFS='|' read -r name so elapsed <<< "$entry"
        size=$(du -h "$ADDONS_DEST/$name/__init__.so" 2>/dev/null | cut -f1)
        echo -e "   ${GREEN}•${NC} $name  ${CYAN}($size, ${elapsed}s)${NC}"
    done
fi

if [ ${#FAILED[@]} -gt 0 ]; then
    echo -e "\n${WHITE}✗ Addons échoués :${NC}"
    for f in "${FAILED[@]}"; do
        echo -e "   ${RED}•${NC} $f"
    done
    echo -e "\n${YELLOW}💡 Consultez le log : $LOG_FILE${NC}"
    exit 1
fi

echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${WHITE}       ✅ TOUS LES ADDONS COMPILÉS AVEC SUCCÈS                  ${GREEN}║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${WHITE}📂 Contenu final de $ADDONS_DEST :${NC}"
for d in "$ADDONS_DEST"/*/; do
    [ -d "$d" ] || continue
    name=$(basename "$d")
    so_size=$(du -h "$d/__init__.so" 2>/dev/null | cut -f1 || echo "?")
    nb_data=$(find "$d" -type f ! -name "*.so" | wc -l)
    echo -e "   ${CYAN}$name${NC} : __init__.so ${so_size}, $nb_data fichier(s) de données"
done

echo ""
log "========================================"
log "Compilation des addons terminée"
log "Succès : ${#SUCCESS[@]} / Échecs : ${#FAILED[@]}"
log "========================================"