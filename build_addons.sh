#!/bin/bash
# ============================================================
#  build_addons.sh - Orchestrateur de compilation des addons
#  Lance compile_flat.sh dans les dossiers de modules
#
#  Usage :
#    bash build_addons.sh                    # tous les modules
#    bash build_addons.sh all                # tous les modules
#    bash build_addons.sh Automobiles        # un module
#    bash build_addons.sh Automobiles sinistres
#    bash build_addons.sh --list             # liste les modules
#    bash build_addons.sh --clean            # nettoie les .so du dist
#    bash build_addons.sh --root-only        # compile uniquement le dossier racine de chaque module
# ============================================================

set -e


SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
ADDONS_SRC="$PROJECT_ROOT/addons"
DIST_ROOT="$PROJECT_ROOT/dist_secure"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()  { [ "$QUIET" -eq 1 ] && return 0; printf "${BLUE}[INFO]${NC} %s\n" "$1"; }
log_ok()    { [ "$QUIET" -eq 1 ] && return 0; printf "${GREEN}[OK]${NC} %s\n" "$1"; }
log_warn()  { [ "$QUIET" -eq 1 ] && return 0; printf "${YELLOW}[!]${NC} %s\n" "$1"; }
log_err()   { printf "${RED}[X]${NC} %s\n" "$1" >&2; }
die()       { log_err "$1"; exit 1; }

section() {
    [ "$QUIET" -eq 1 ] && return 0
    printf "\n${CYAN}============================================================${NC}\n"
    printf "${CYAN}  %s${NC}\n" "$1"
    printf "${CYAN}============================================================${NC}\n"
}

# ============================================================
#  Vérifications de base
# ============================================================
[ -d "$ADDONS_SRC" ] || die "Dossier addons/ introuvable : $ADDONS_SRC"
command -v "$PYTHON" >/dev/null 2>&1 || export PYTHON="${PYTHON:-python3}"
command -v "$PYTHON" >/dev/null || die "python3 introuvable"

DIST_DIR=$(find "$DIST_ROOT" -maxdepth 1 -type d -name "*.dist" 2>/dev/null | head -n1)
[ -z "$DIST_DIR" ] && die "Aucun dist_secure/*.dist. Lancez build_windows.sh d'abord."
DIST_DIR_ABS="$(cd "$(dirname "$DIST_DIR")" && pwd)/$(basename "$DIST_DIR")"

# ============================================================
#  Parsing des arguments
# ============================================================
if [ $# -eq 0 ]; then
    set -- "all"
fi

MODE=""
MODULES=()
for arg in "$@"; do
    case "$arg" in
        --list)
            printf "Modules disponibles :\n"
            for pkg in "$ADDONS_SRC"/*/; do
                [ -d "$pkg" ] || continue
                name=$(basename "$pkg")
                marker=""
                [ -d "$DIST_DIR_ABS/addons/$name" ] && marker=" [compiled]"
                printf "  - %s%s\n" "$name" "$marker"
            done
            exit 0
            ;;
        --clean)
            MODE="clean" ;;
        --root-only)
            MODE="root-only" ;;
        all|ALL)
            MODULES=()
            for pkg in "$ADDONS_SRC"/*/; do
                [ -d "$pkg" ] || continue
                MODULES+=("$(basename "$pkg")")
            done
            ;;
        -*)
            log_warn "Argument inconnu : $arg" ;;
        *)
            MODULES+=("$arg") ;;
    esac
done

if [ "$MODE" = "clean" ]; then
    section "Nettoyage des .so dans le dist"
    for m in "${MODULES[@]:-}"; do
        [ -z "$m" ] && continue
        rm -rf "$DIST_DIR_ABS/addons/$m"
        log_ok "$m nettoyé"
    done
    if [ ${#MODULES[@]} -eq 0 ]; then
        find "$DIST_DIR_ABS/addons" -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} + 2>/dev/null || true
        log_ok "Tous les addons nettoyés"
    fi
    exit 0
fi

if [ ${#MODULES[@]} -eq 0 ]; then
    die "Aucun module à compiler (utilisez 'all' ou un nom de module)"
fi

# ============================================================
#  Trouver compile_flat.sh
# ============================================================
COMPILE_FLAT="$PROJECT_ROOT/compile_flat.sh"
if [ ! -f "$COMPILE_FLAT" ]; then
    # chercher dans un module (rétrocompatibilité)
    for pkg in "$ADDONS_SRC"/*/; do
        if [ -f "$pkg/compile_flat.sh" ]; then
            COMPILE_FLAT="$pkg/compile_flat.sh"
            break
        fi
    done
fi
[ -f "$COMPILE_FLAT" ] || die "compile_flat.sh introuvable à la racine ou dans un module"

log_info "Orchestrateur : $COMPILE_FLAT"
log_info "Dist          : $DIST_DIR_ABS"

# ============================================================
#  Décider des dossiers à compiler
# ============================================================
#
# Mode par défaut : TOUS les dossiers contenant un __init__.py
# sous addons/<Module>/, sauf tests/.
#
# Mode --root-only : uniquement addons/<Module>/ (le dossier du module).
#
collect_dirs() {
    local module="$1"
    local mode="$2"
    local module_dir="$ADDONS_SRC/$module"

    [ -d "$module_dir" ] || return 0

    if [ "$mode" = "root-only" ]; then
        printf "%s\n" "$module_dir"
        return 0
    fi

    # Récursif contrôlé : tous les dossiers avec __init__.py
    find "$module_dir" -type f -name "__init__.py" 2>/dev/null | while read -r f; do
        dir=$(dirname "$f")
        # Ignorer tests
        case "$dir" in
            */tests|*/tests/*) continue ;;
        esac
        # Vérifier qu'il y a au moins un .py autre que __init__
        if find "$dir" -maxdepth 1 -type f -name "*.py" ! -name "__init__.py" 2>/dev/null | grep -q .; then
            printf "%s\n" "$dir"
        else
            # Que __init__.py : on le compile quand même pour créer __init.so
            printf "%s\n" "$dir"
        fi
    done | sort
}

# ============================================================
#  Compilation
# ============================================================
TOTAL_OK=0
TOTAL_FAIL=0
FAILED_MODULES=()

for module in "${MODULES[@]}"; do
    module_dir="$ADDONS_SRC/$module"
    if [ ! -d "$module_dir" ]; then
        log_warn "Module introuvable : $module"
        TOTAL_FAIL=$((TOTAL_FAIL + 1))
        FAILED_MODULES+=("$module (absent)")
        continue
    fi

    section "Module : $module"

    DIRS=()
    while IFS= read -r d; do
        [ -z "$d" ] && continue
        DIRS+=("$d")
    done < <(collect_dirs "$module" "$MODE")

    if [ ${#DIRS[@]} -eq 0 ]; then
        log_warn "Aucun dossier à compiler pour $module"
        continue
    fi

    log_info "${#DIRS[@]} dossier(s) à compiler :"
    for d in "${DIRS[@]}"; do
        printf "  - %s\n" "${d#$ADDONS_SRC/}"
    done

    MODULE_OK=0
    MODULE_FAIL=0

    for dir in "${DIRS[@]}"; do
        rel="${dir#$ADDONS_SRC/}"
        echo ""
        log_info "→ $rel"

        # Copier compile_flat.sh dans le dossier s'il n'y est pas
        if [ ! -f "$dir/compile_flat.sh" ]; then
            cp "$COMPILE_FLAT" "$dir/compile_flat.sh" 2>/dev/null || true
        fi

        if bash "$dir/compile_flat.sh" --quiet >/dev/null 2>&1; then
            MODULE_OK=$((MODULE_OK + 1))
        else
            MODULE_FAIL=$((MODULE_FAIL + 1))
            log_err "Échec : $rel"
        fi
    done

    if [ "$MODULE_FAIL" -eq 0 ]; then
        log_ok "$module : $MODULE_OK/$MODULE_OK dossier(s) compilé(s)"
        TOTAL_OK=$((TOTAL_OK + 1))
    else
        log_err "$module : $MODULE_OK OK / $MODULE_FAIL échec(s)"
        TOTAL_FAIL=$((TOTAL_FAIL + 1))
        FAILED_MODULES+=("$module")
    fi
done

# ============================================================
#  Résumé
# ============================================================
section "Résumé"

log_ok "Modules compilés : $TOTAL_OK"
[ "$TOTAL_FAIL" -gt 0 ] && log_err "Modules en échec : $TOTAL_FAIL"

if [ ${#FAILED_MODULES[@]} -gt 0 ]; then
    printf "\n"
    log_warn "Modules échoués :"
    for f in "${FAILED_MODULES[@]}"; do
        printf "  - %s\n" "$f"
    done
    exit 1
fi

printf "\n"
log_ok "Tous les modules ont été compilés"
printf "\n"
log_info "Tester : cd %s && ./LOMETA" "$DIST_DIR_ABS"
printf "\n"