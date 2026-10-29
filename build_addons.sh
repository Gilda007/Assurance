#!/bin/bash
# ============================================================
#  LOMETA — Compilation d'addons en --standalone (Solution 1)
#  Chaque addon est compilé en standalone, puis seuls SES .so
#  sont extraits vers dist_secure/*.dist/addons/<name>/
# ============================================================
#  Usage :
#    ./build_addons.sh                       # tous
#    ./build_addons.sh Automobiles           # un seul
#    ./build_addons.sh Automobiles sinistres # plusieurs
#    ./build_addons.sh --list
#    ./build_addons.sh --clean
#    ./build_addons.sh --gen                 # (re)générer scripts
#    ./build_addons.sh --gen Automobiles
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib_build.sh"

ADDON_SCRIPTS_DIR="$PROJECT_ROOT/build_addons"
LOG_FILE="$PROJECT_ROOT/build_addons_$(date +%Y%m%d_%H%M%S).log"

SELECTED=(); DO_CLEAN=0; DO_GEN=0
for arg in "$@"; do
    case "$arg" in
        --list)
            echo -e "${WHITE}Addons disponibles :${NC}"
            for pkg in "$ADDONS_SRC"/*/; do
                [ -d "$pkg" ] || continue
                name=$(basename "$pkg")
                marker=""; [ -f "$ADDON_SCRIPTS_DIR/$name.sh" ] && marker=" ${GREEN}[script ✓]${NC}"
                echo -e "  • $name$marker"
            done
            exit 0 ;;
        --clean) DO_CLEAN=1 ;;
        --gen)   DO_GEN=1 ;;
        --help|-h) sed -n '2,16p' "$0"; exit 0 ;;
        *) SELECTED+=("$arg") ;;
    esac
done

check_prerequisites
mkdir -p "$ADDON_SCRIPTS_DIR"

# ════════════════════════════════════════════════════════════
#  GÉNÉRATION d'un script par addon
# ════════════════════════════════════════════════════════════
generate_addon_script() {
    local name="$1"
    local src="$ADDONS_SRC/$name"
    local script="$ADDON_SCRIPTS_DIR/$name.sh"
    [ -d "$src" ] || { echo -e "${RED}✗ Source introuvable : $name${NC}"; return 1; }

    local includes=(); local seen=" "
    _add() {
        case "$seen" in *" $1 "*) return 0;; esac
        seen+="$1 "; includes+=("$1")
    }

    _add "--include-package=addons.$name"

    while IFS= read -r f; do
        [ -z "$f" ] && continue
        local rel="${f#$src/}"; local d; d=$(dirname "$rel")
        [ "$d" = "." ] && continue
        _add "--include-package=addons.$name.$(echo "$d" | tr '/' '.')"
    done < <(find "$src" -type f -name "__init__.py" 2>/dev/null | sort)

    while IFS= read -r f; do
        [ -z "$f" ] && continue
        [ "$(basename "$f" .py)" = "__init__" ] && continue
        local rel="${f#$src/}"; local noext="${rel%.py}"
        _add "--include-module=addons.$name.$(echo "$noext" | tr '/' '.')"
    done < <(find "$src" -type f -name "*.py" 2>/dev/null | sort)

    while IFS= read -r d; do
        [ -z "$d" ] && continue
        [ "$d" = "$src" ] && continue
        local rel="${d#$src/}"
        echo "$rel" | grep -qE '^(\.|_|tests?/|migrations/|__pycache__)' && continue
        [ -f "$d/__init__.py" ] && continue
        _add "--include-package=addons.$name.$(echo "$rel" | tr '/' '.')"
    done < <(find "$src" -type d 2>/dev/null | sort)

    {
        echo '#!/bin/bash'
        echo 'set -euo pipefail'
        echo "# ============================================================"
        echo "#  Addon : $name — compilation --standalone (Solution 1)"
        echo "#  Auto-généré le $(date '+%Y-%m-%d %H:%M:%S')"
        echo "#  ⚠ Sera ÉCRASÉ par --gen"
        echo "# ============================================================"
        echo
        echo "ADDON_NAME=\"$name\""
        echo
        echo "ADDON_INCLUDES=("
        for inc in "${includes[@]}"; do
            echo "    $(printf '%q' "$inc")"
        done
        echo ")"
        echo
        echo 'source "$(dirname "${BASH_SOURCE[0]}")/../lib_build.sh"'
        echo 'export LOG_FILE="${LOG_FILE:-/dev/null}"'
        echo 'check_prerequisites'
        echo 'run_addon_standalone "$ADDON_NAME" "${ADDON_INCLUDES[@]}"'
    } > "$script"

    chmod +x "$script"
    echo -e "${GREEN}✓${NC} $script ${CYAN}(${#includes[@]} inclusions)${NC}"
}

if [ "$DO_GEN" -eq 1 ]; then
    section "Génération des scripts d'addon"
    if [ ${#SELECTED[@]} -eq 0 ]; then
        for pkg in "$ADDONS_SRC"/*/; do
            [ -d "$pkg" ] && generate_addon_script "$(basename "$pkg")"
        done
        exit 0
    else
        for name in "${SELECTED[@]}"; do generate_addon_script "$name"; done
        exit 0
    fi
fi

# ─── Localiser le dist ───
DIST_DIR=$(find "$DIST_ROOT" -maxdepth 1 -type d -name "*.dist" 2>/dev/null | head -n1)
[ -z "$DIST_DIR" ] && die "Aucun dist_secure/*.dist. Lancez ./build_linux.sh d'abord."
export DIST_DIR

# ─── Nettoyage ───
if [ "$DO_CLEAN" -eq 1 ]; then
    section "Nettoyage"
    rm -rf "$ADDONS_BUILD"
    if [ ${#SELECTED[@]} -eq 0 ]; then
        find "$DIST_DIR/addons" -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} + 2>/dev/null || true
        ok "Tout nettoyé"; exit 0
    else
        for name in "${SELECTED[@]}"; do
            rm -rf "$ADDONS_BUILD/$name" "$DIST_DIR/addons/$name"
            ok "$name nettoyé"
        done
        exit 0
    fi
fi

mkdir -p "$ADDONS_BUILD" "$DIST_DIR/addons"

# ─── Cible ───
if [ ${#SELECTED[@]} -eq 0 ]; then
    ADDONS_TO_BUILD=()
    for pkg in "$ADDONS_SRC"/*/; do
        [ -d "$pkg" ] && ADDONS_TO_BUILD+=("$(basename "$pkg")")
    done
else
    ADDONS_TO_BUILD=("${SELECTED[@]}")
fi
[ ${#ADDONS_TO_BUILD[@]} -eq 0 ] && die "Aucun addon à compiler"

section "Compilation --standalone"
echo -e "${WHITE}🎯 Addons : ${ADDONS_TO_BUILD[*]}${NC}"

FAILED=(); SUCCESS=()
for name in "${ADDONS_TO_BUILD[@]}"; do
    script="$ADDON_SCRIPTS_DIR/$name.sh"
    if [ ! -f "$script" ]; then
        echo -e "${YELLOW}⚠ Script absent → génération${NC}"
        generate_addon_script "$name" || { FAILED+=("$name"); continue; }
    fi

    echo -e "\n${CYAN}──────────────────────────────────────────────────────────${NC}"
    echo -e "${WHITE}  → $name${NC}"
    echo -e "${CYAN}──────────────────────────────────────────────────────────${NC}"

    if ADDON_LOG="$LOG_FILE" bash "$script"; then
        SUCCESS+=("$name")
    else
        FAILED+=("$name")
    fi
done

section "Résumé"
[ ${#SUCCESS[@]} -gt 0 ] && ok "Succès : ${#SUCCESS[@]} → ${SUCCESS[*]}"
if [ ${#FAILED[@]} -gt 0 ]; then
    for f in "${FAILED[@]}"; do echo -e "${RED}  ✗ $f${NC}"; done
    echo -e "\n${YELLOW}💡 Log : $LOG_FILE${NC}"
    exit 1
fi
echo -e "\n${GREEN}✅ Addons compilés${NC}"