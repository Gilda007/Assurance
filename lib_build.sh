#!/bin/bash
# ============================================================
#  LOMETA — Bibliothèque commune de compilation
#  Sourcée par build_linux.sh et build_addons.sh
#  Ne pas exécuter directement.
# ============================================================
#  Modes supportés :
#    • --module     → compile_addon + install_addon
#    • --standalone → run_addon_standalone (Solution 1)
# ============================================================

# ─── Couleurs ───
export RED='\033[0;31m'; export GREEN='\033[0;32m'; export YELLOW='\033[1;33m'
export BLUE='\033[0;34m'; export CYAN='\033[0;36m'; export WHITE='\033[1;37m'
export NC='\033[0m'

# ─── Résolution du dossier projet ───
LIB_BUILD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PROJECT_ROOT="${PROJECT_ROOT:-$LIB_BUILD_DIR}"
export ADDONS_SRC="$PROJECT_ROOT/addons"
export ADDONS_BUILD="$PROJECT_ROOT/addons_compiled"
export DIST_ROOT="$PROJECT_ROOT/dist_secure"
export TOOLS_DIR="$PROJECT_ROOT/tools"

# ─── Suffixe ABI Python ───
if [ -n "${PYTHON:-}" ]; then
    export PY_ABI_SUFFIX=$($PYTHON -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))" 2>/dev/null || echo ".so")
else
    export PY_ABI_SUFFIX=".so"
fi

# ─── Fonctions d'affichage ───
section() {
    echo -e "\n${CYAN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}  $1${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
}

die() {
    echo -e "${RED}✗ $1${NC}" >&2
    exit 1
}

warn() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

ok() {
    echo -e "${GREEN}✓ $1${NC}"
}

info() {
    echo -e "${BLUE}$1${NC}"
}

# ─── Vérification des prérequis ───
check_prerequisites() {
    section "0 · Vérification de l'environnement"

    export PYTHON="${PYTHON:-python3}"
    command -v "$PYTHON" >/dev/null || die "python3 introuvable"

    command -v rsync >/dev/null || die "rsync requis (apt install rsync)"
    command -v gcc   >/dev/null || die "gcc requis (apt install build-essential)"
    command -v zip   >/dev/null || die "zip requis (apt install zip)"

    if ! $PYTHON -m nuitka --version &>/dev/null; then
        warn "Nuitka manquant — installation…"
        $PYTHON -m pip install --upgrade "nuitka>=2.7" ordered-set zstandard || \
            die "Échec installation Nuitka"
    fi

    local nuitka_ver
    nuitka_ver=$($PYTHON -m nuitka --version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -n1)
    if [ -n "$nuitka_ver" ]; then
        local major minor
        major=$(echo "$nuitka_ver" | cut -d. -f1)
        minor=$(echo "$nuitka_ver" | cut -d. -f2)
        if [ "$major" -lt 2 ] || { [ "$major" -eq 2 ] && [ "$minor" -lt 7 ]; }; then
            die "Nuitka $nuitka_ver trop ancien (≥ 2.7 requis). Mettez à jour : $PYTHON -m pip install --upgrade nuitka"
        fi
    fi

    export PY_ABI_SUFFIX=$($PYTHON -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))" 2>/dev/null || echo ".so")

    echo -e "${BLUE}🐍 Python : $($PYTHON --version)  (ABI: $PY_ABI_SUFFIX)${NC}"
    echo -e "${BLUE}🔨 Nuitka : ${nuitka_ver}${NC}"
    echo -e "${BLUE}📂 Racine : $PROJECT_ROOT${NC}"

    [ -f "$TOOLS_DIR/scan_addon_tree.py" ]           || die "Outil manquant : $TOOLS_DIR/scan_addon_tree.py"
    [ -f "$TOOLS_DIR/manifest_to_nuitka_args.py" ]   || die "Outil manquant : $TOOLS_DIR/manifest_to_nuitka_args.py"

    if command -v ccache >/dev/null; then
        export CC="ccache gcc"
        export CXX="ccache g++"
        echo -e "${BLUE}⚡ ccache activé${NC}"
    fi
}

# ============================================================
#  SCAN ARBORESCENT — inventaire exhaustif d'un addon
# ============================================================

# scan_addon <nom>
# Produit $ADDONS_BUILD/<nom>/manifest.json
# Expose ADDON_MANIFEST, ADDON_PKGS, ADDON_MODS, ADDON_DATA,
#        ADDON_SO_PREBUILT, ADDON_IGNORED
scan_addon() {
    local name="$1"
    local manifest_dir="$ADDONS_BUILD/$name"
    local manifest="$manifest_dir/manifest.json"

    mkdir -p "$manifest_dir"

    if ! $PYTHON "$TOOLS_DIR/scan_addon_tree.py" "$name" \
            --project-root "$PROJECT_ROOT" \
            --output "$manifest" \
            --ascii 2>&1 | tee -a "${LOG_FILE:-/dev/null}"; then
        warn "Scan arborescent échoué pour $name"
        return 1
    fi

    [ -f "$manifest" ] || { warn "Manifeste introuvable : $manifest"; return 1; }

    local summary
    summary=$($PYTHON - "$manifest" <<'PYEOF'
import json, sys
m = json.load(open(sys.argv[1]))
s = m["summary"]
pkgs = s["packages"] + s["namespace_packages"]
print(f"{pkgs}|{s['modules']}|{s['data_files']}|{s['prebuilt_extensions']}|{s['ignored']}|{s['total_py_bytes']}")
PYEOF
    )

    IFS='|' read -r n_pkgs n_mods n_data n_so n_ign n_bytes <<< "$summary"

    export ADDON_MANIFEST="$manifest"
    export ADDON_PKGS="$n_pkgs"
    export ADDON_MODS="$n_mods"
    export ADDON_DATA="$n_data"
    export ADDON_SO_PREBUILT="$n_so"
    export ADDON_IGNORED="$n_ign"

    info "  📦 $name — packages=$n_pkgs, modules=$n_mods, data=$n_data, .so=$n_so, ignorés=$n_ign (${n_bytes} B .py)"
    return 0
}

# ============================================================
#  GÉNÉRATION DES ARGS NUITKA depuis le manifeste
# ============================================================

generate_nuitka_include_args() {
    local manifest="$1"
    $PYTHON "$TOOLS_DIR/manifest_to_nuitka_args.py" "$manifest"
}

# ============================================================
#  PRÉPARATION DES SOURCES  (Option B)
# ============================================================
#  Arborescence produite :
#    $ADDONS_BUILD/addons/<name>/...     ← package importable
#    $ADDONS_BUILD/<name>/manifest.json  ← métadonnées (hors arbre)
# ============================================================

prepare_addon_source() {
    local name="$1"
    local src="$ADDONS_SRC/$name"
    local meta_dir="$ADDONS_BUILD/$name"                 # métadonnées (manifest)
    local dst="$ADDONS_BUILD/addons/$name"               # package réel

    [ -d "$src" ] || { warn "Addon introuvable : $name"; return 1; }

    # Conserver manifeste existant
    local preserve_manifest=""
    if [ -f "$meta_dir/manifest.json" ]; then
        preserve_manifest=$(mktemp)
        cp "$meta_dir/manifest.json" "$preserve_manifest"
    fi

    rm -rf "$dst"
    mkdir -p "$dst" "$meta_dir"

    rsync -a \
        --exclude='.history' --exclude='__pycache__' \
        --exclude='*.pyc' --exclude='*.pyo' \
        --exclude='test_*.py' --exclude='.pytest_cache' \
        --exclude='*.db' --exclude='*.sqlite' \
        --exclude='_build' \
        "$src/" "$dst/"

    if [ -n "$preserve_manifest" ] && [ -f "$preserve_manifest" ]; then
        cp "$preserve_manifest" "$meta_dir/manifest.json"
        rm -f "$preserve_manifest"
    fi

    if [ ! -f "$dst/__init__.py" ]; then
        warn "$name/__init__.py absent — création d'un fichier minimal"
        printf '"""%s addon package."""\n' "$name" > "$dst/__init__.py"
    fi

    # Assurer un __init__.py à la racine du conteneur "addons"
    if [ ! -f "$ADDONS_BUILD/addons/__init__.py" ]; then
        printf '"""Addons namespace package (Nuitka build)."""\n' \
            > "$ADDONS_BUILD/addons/__init__.py"
    fi
    return 0
}

# ============================================================
#  COMPILATION --module  (mode classique, conservé)
# ============================================================

# compile_addon <nom>
# Expose ADDON_SO_PATH et ADDON_BUILD_OUT en cas de succès
compile_addon() {
    local name="$1"
    local pkg="$ADDONS_BUILD/addons/$name"
    [ -d "$pkg" ] || { warn "Source non préparée : $name"; return 1; }

    echo -e "\n${CYAN}──────────────────────────────────────────────────────────${NC}"
    echo -e "${WHITE}  → Compilation --module : $name${NC}"
    echo -e "${CYAN}──────────────────────────────────────────────────────────${NC}"

    local build_out="$ADDONS_BUILD/$name/_build"
    rm -rf "$build_out"
    mkdir -p "$build_out"

    # 1. Scan
    scan_addon "$name" || return 1

    # 2. Args Nuitka
    local -a include_args
    mapfile -t include_args < <(generate_nuitka_include_args "$ADDON_MANIFEST")
    if [ ${#include_args[@]} -eq 0 ]; then
        warn "Aucun module détecté pour $name — compilation annulée"
        return 1
    fi
    info "  🔧 $name — ${#include_args[@]} inclusions Nuitka générées"

    # 3. Nuitka (exec dans $ADDONS_BUILD pour résoudre addons.<name>)
    local nuitka_log="$build_out/nuitka.log"
    local start; start=$(date +%s)

    set +e
    (
        cd "$ADDONS_BUILD"
        $PYTHON -m nuitka \
            --module \
            --assume-yes-for-downloads \
            --enable-plugin=pyside6 \
            --nofollow-import-to=pytest \
            --nofollow-import-to=tkinter \
            --nofollow-import-to=PyQt5 \
            --nofollow-import-to=PyQt6 \
            --nofollow-import-to=matplotlib \
            "${include_args[@]}" \
            --output-dir="$build_out" \
            "addons/$name"
    ) > "$nuitka_log" 2>&1
    local exit_code=$?
    set -e

    local elapsed=$(( $(date +%s) - start ))
    [ -n "${LOG_FILE:-}" ] && cat "$nuitka_log" >> "$LOG_FILE"

    if [ "$exit_code" -ne 0 ]; then
        echo -e "${RED}  ✗ Nuitka exit $exit_code (voir $nuitka_log)${NC}"
        grep -iE "error|fatal|traceback" "$nuitka_log" | tail -10 | sed 's/^/    /'
        return 1
    fi

    local main_so
    main_so=$(find "$build_out" -maxdepth 3 -type f -name "${name}*.so" | head -n1)
    [ -z "$main_so" ] && main_so=$(find "$build_out" -maxdepth 3 -type f -name "*.so" | head -n1)

    if [ -z "$main_so" ]; then
        echo -e "${RED}  ✗ Aucune .so générée${NC}"
        ls -la "$build_out" | sed 's/^/    /'
        return 1
    fi

    echo -e "${GREEN}  ✓ compilé en ${elapsed}s → $(basename "$main_so") ($(du -h "$main_so" | cut -f1))${NC}"

    export ADDON_SO_PATH="$main_so"
    export ADDON_BUILD_OUT="$build_out"
    return 0
}

# ============================================================
#  INSTALLATION D'UN --module  (mode classique)
# ============================================================

install_addon() {
    local name="$1"
    local build_out="${ADDON_BUILD_OUT:-}"
    local main_so="${ADDON_SO_PATH:-}"

    [ -n "$main_so" ] && [ -f "$main_so" ] || { warn "Pas de .so à installer pour $name"; return 1; }
    [ -n "${DIST_DIR:-}" ] || { warn "DIST_DIR non défini"; return 1; }

    local dest="$DIST_DIR/addons/$name"
    rm -rf "$dest"
    mkdir -p "$dest"

    # Arborescence préservée depuis build_out (les .so peuvent être imbriqués)
    while IFS= read -r so_file; do
        [ -z "$so_file" ] && continue
        local rel="${so_file#$build_out/}"
        # Nuitka nomme parfois "addons/<name>/..." → préserver tel quel
        local target="$dest/$rel"
        mkdir -p "$(dirname "$target")"
        cp "$so_file" "$target"
    done < <(find "$build_out" -type f -name "*.so" | sort)

    # Renommer l'éventuel "<name>.so" racine en __init<suffix>.so
    if [ -f "$dest/$name.so" ] && [ ! -f "$dest/__init${PY_ABI_SUFFIX}" ]; then
        mv "$dest/$name.so" "$dest/__init${PY_ABI_SUFFIX}"
    fi

    # Données non-Python
    rsync -a \
        --exclude='*.py' --exclude='__pycache__' \
        --exclude='.history' --exclude='*.pyc' \
        --exclude='_build' --exclude='*.db' --exclude='*.sqlite' \
        --exclude='*.so' \
        "$ADDONS_BUILD/addons/$name/" "$dest/"

    # Archiver le manifeste
    if [ -f "${ADDON_MANIFEST:-}" ]; then
        cp "$ADDON_MANIFEST" "$dest/.manifest.json"
        info "  📄 manifeste archivé → $dest/.manifest.json"
    fi

    echo -e "${GREEN}  ✓ installé → $dest${NC}"
    return 0
}

# ============================================================
#  SOLUTION 1 — COMPILATION --standalone PAR ADDON
# ============================================================
#  Étapes :
#    1. prepare_addon_source (assure $ADDONS_BUILD/addons/<name>/)
#    2. scan_addon + génération des args
#    3. Nuitka --standalone depuis $ADDONS_BUILD
#    4. Extraction ciblée : <standalone>/addons/<name>/**/*.so
#       + données non-Python depuis la source
#       → $DIST_DIR/addons/<name>/
#    5. Suppression du standalone intermédiaire (volumineux)
# ============================================================

# run_addon_standalone <nom> [includes...]
# run_addon_standalone() {
#     local name="$1"; shift
#     local -a explicit_includes=("$@")

#     prepare_addon_source "$name" || return 1

#     local src_pkg="$ADDONS_BUILD/addons/$name"
#     local build_root="$ADDONS_BUILD/_standalone"
#     local build_out="$build_root/$name"
#     rm -rf "$build_out"; mkdir -p "$build_out"

#     # 1. Scan + args
#     scan_addon "$name" || return 1

#     local -a include_args
#     if [ ${#explicit_includes[@]} -gt 0 ]; then
#         include_args=("${explicit_includes[@]}")
#         info "  📦 $name — ${#include_args[@]} inclusions (script dédié)"
#     else
#         mapfile -t include_args < <(generate_nuitka_include_args "$ADDON_MANIFEST")
#         info "  📦 $name — ${#include_args[@]} inclusions (manifeste)"
#     fi
#     if [ ${#include_args[@]} -eq 0 ]; then
#         warn "Aucune inclusion pour $name — abandon"; return 1
#     fi

#     # 2. Nuitka --standalone
#     local nuitka_log="$build_out/nuitka.log"
#     local start; start=$(date +%s)

#     info "  🏗  --standalone (cela peut être long…)"
#     set +e
#     (
#         cd "$ADDONS_BUILD"
#         $PYTHON -m nuitka \
#             --standalone \
#             --assume-yes-for-downloads \
#             --enable-plugin=pyside6 \
#             --nofollow-import-to=pytest \
#             --nofollow-import-to=tkinter \
#             --nofollow-import-to=PyQt5 \
#             --nofollow-import-to=PyQt6 \
#             --nofollow-import-to=matplotlib \
#             "${include_args[@]}" \
#             --include-package-data="addons.$name" \
#             --output-dir="$build_out" \
#             --output-filename="__main_addon_$name" \
#             "addons/$name/__init__.py"
#     ) > "$nuitka_log" 2>&1
#     local exit_code=$?
#     set -e

#     local elapsed=$(( $(date +%s) - start ))
#     [ -n "${LOG_FILE:-}" ] && cat "$nuitka_log" >> "$LOG_FILE"

#     if [ "$exit_code" -ne 0 ]; then
#         echo -e "${RED}  ✗ Nuitka --standalone exit $exit_code${NC}"
#         grep -iE "error|fatal|traceback" "$nuitka_log" | tail -12 | sed 's/^/    /'
#         return 1
#     fi

#     # 3. Localiser le dossier .dist du standalone
#     local standalone_dir
#     standalone_dir=$(find "$build_out" -maxdepth 1 -type d -name "*.dist" | head -n1)
#     if [ -z "$standalone_dir" ]; then
#         echo -e "${RED}  ✗ Dossier *.dist du standalone introuvable dans $build_out${NC}"
#         find "$build_out" -maxdepth 2 -type d | sed 's/^/    /'
#         return 1
#     fi

#     # 4. Extraire UNIQUEMENT les .so de l'addon
#     local addon_so_root="$standalone_dir/addons/$name"
#     if [ ! -d "$addon_so_root" ]; then
#         echo -e "${RED}  ✗ $addon_so_root absent du standalone${NC}"
#         echo -e "${YELLOW}    Arborescence disponible :${NC}"
#         find "$standalone_dir/addons" -maxdepth 3 -type d 2>/dev/null | sed 's/^/      /' | head -30
#         return 1
#     fi

#     [ -n "${DIST_DIR:-}" ] || { warn "DIST_DIR non défini"; return 1; }
#     local dest="$DIST_DIR/addons/$name"
#     rm -rf "$dest"; mkdir -p "$dest"

#     local so_count=0
#     while IFS= read -r so_file; do
#         [ -z "$so_file" ] && continue
#         local rel="${so_file#$addon_so_root/}"
#         local target="$dest/$rel"
#         mkdir -p "$(dirname "$target")"
#         cp "$so_file" "$target"
#         so_count=$((so_count + 1))
#     done < <(find "$addon_so_root" -type f -name "*.so" | sort)

#     if [ "$so_count" -eq 0 ]; then
#         echo -e "${RED}  ✗ Aucun .so trouvé sous $addon_so_root${NC}"
#         return 1
#     fi

#     # 5. Données non-Python depuis la source préparée
#     rsync -a \
#         --exclude='*.py' --exclude='__pycache__' \
#         --exclude='.history' --exclude='*.pyc' --exclude='*.pyo' \
#         --exclude='_build' --exclude='*.db' --exclude='*.sqlite' \
#         --exclude='*.so' \
#         "$src_pkg/" "$dest/"

#     local data_count
#     data_count=$(find "$dest" -type f ! -name '*.so' | wc -l)

#     # 6. Archiver manifeste
#     if [ -f "$ADDON_MANIFEST" ]; then
#         cp "$ADDON_MANIFEST" "$dest/.manifest.json"
#     fi

#     # 7. Nettoyer le standalone intermédiaire
#     rm -rf "$standalone_dir"

#     echo -e "${GREEN}  ✓ ${elapsed}s · ${so_count} .so + ${data_count} données → $dest${NC}"

#     # 8. Log arborescence
#     if [ -n "${LOG_FILE:-}" ]; then
#         {
#             echo "# Arborescence installée : $name"
#             find "$dest" -type f | sed "s|$dest/||" | sort
#         } >> "$LOG_FILE"
#     fi

#     export ADDON_SO_PATH="$dest/__init${PY_ABI_SUFFIX}"
#     export ADDON_BUILD_OUT="$build_out"
#     return 0
# }
# ============================================================
#  SOLUTION 1 — COMPILATION --standalone PAR ADDON
# ============================================================
#  Nuitka --standalone exige un POINT D'ENTRÉE programme (.py).
#  Un package-addon (addons/<name>/__init__.py) ne peut PAS être
#  la cible directe → on génère un stub minimal hors du package.
# ============================================================
run_addon_standalone() {
    local name="$1"; shift
    local -a explicit_includes=("$@")

    # ─── Auto-défense ───
    export PYTHON="${PYTHON:-python3}"
    export LOG_FILE="${LOG_FILE:-/dev/null}"
    if [ -z "${PY_ABI_SUFFIX:-}" ] || [ "${PY_ABI_SUFFIX}" = ".so" ]; then
        export PY_ABI_SUFFIX=$("$PYTHON" -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))" 2>/dev/null || echo ".so")
    fi

    # ─── Auto-détection DIST_DIR si non fourni ───
    if [ -z "${DIST_DIR:-}" ]; then
        DIST_DIR=$(find "$DIST_ROOT" -maxdepth 1 -type d -name "*.dist" 2>/dev/null | head -n1)
        if [ -z "$DIST_DIR" ]; then
            warn "Aucun dist_secure/*.dist trouvé. Lancez ./build_linux.sh d'abord."
            return 1
        fi
        export DIST_DIR
        info "  📂 DIST_DIR auto-détecté : $DIST_DIR"
    fi

    prepare_addon_source "$name" || return 1

    local src_pkg="$ADDONS_BUILD/addons/$name"
    local build_root="$ADDONS_BUILD/_standalone"
    local build_out="$build_root/$name"
    rm -rf "$build_out"; mkdir -p "$build_out"

    # 1. Scan + args Nuitka
    scan_addon "$name" || return 1

    local -a include_args
    if [ ${#explicit_includes[@]} -gt 0 ]; then
        include_args=("${explicit_includes[@]}")
        info "  📦 $name — ${#include_args[@]} inclusions (script dédié)"
    else
        mapfile -t include_args < <(generate_nuitka_include_args "$ADDON_MANIFEST")
        info "  📦 $name — ${#include_args[@]} inclusions (manifeste)"
    fi
    if [ ${#include_args[@]} -eq 0 ]; then
        warn "Aucune inclusion pour $name — abandon"; return 1
    fi

    # 1bis. Exclusion des tests (optionnel mais recommandé)
    include_args+=(--nofollow-import-to="addons.${name}.tests")

    # 2. Stub d'entrée HORS du package (dossier temporaire neutre)
    local stub_dir; stub_dir=$(mktemp -d)
    local entry_stub="$stub_dir/__main_addon_${name}.py"
    cat > "$entry_stub" <<PYEOF
# Stub neutre — NE PAS importer addons.${name}.
# L'inclusion du package est assurée uniquement par
# --include-package=addons.${name} (passé dans include_args).
# Ce fichier n'est qu'un point d'entrée minimal pour Nuitka.
import sys

if __name__ == "__main__":
    sys.exit(0)
PYEOF

    # 3. Nuitka --standalone
    local nuitka_log="$build_out/nuitka.log"
    local start; start=$(date +%s)

    info "  🏗  --standalone (cela peut être long…)"
    set +e
    (
        cd "$ADDONS_BUILD"
        $PYTHON -m nuitka \
            --standalone \
            --assume-yes-for-downloads \
            --enable-plugin=pyside6 \
            --nofollow-import-to=pytest \
            --nofollow-import-to=tkinter \
            --nofollow-import-to=PyQt5 \
            --nofollow-import-to=PyQt6 \
            --nofollow-import-to=matplotlib \
            "${include_args[@]}" \
            --include-package-data="addons.$name" \
            --output-dir="$build_out" \
            --output-filename="__main_addon_${name}" \
            "$entry_stub"
    ) > "$nuitka_log" 2>&1
    local exit_code=$?
    set -e

    rm -rf "$stub_dir"

    local elapsed=$(( $(date +%s) - start ))
    [ -n "${LOG_FILE:-}" ] && cat "$nuitka_log" >> "$LOG_FILE"

    if [ "$exit_code" -ne 0 ]; then
        echo -e "${RED}  ✗ Nuitka --standalone exit $exit_code${NC}"
        grep -iE "error|fatal|traceback" "$nuitka_log" | tail -12 | sed 's/^/    /'
        return 1
    fi

    # 4. Localiser le dossier .dist du standalone
    local standalone_dir
    standalone_dir=$(find "$build_out" -maxdepth 2 -type d -name "*.dist" | head -n1)
    if [ -z "$standalone_dir" ]; then
        echo -e "${RED}  ✗ Dossier *.dist du standalone introuvable dans $build_out${NC}"
        find "$build_out" -maxdepth 2 -type d | sed 's/^/    /'
        return 1
    fi

    # 5. Extraire UNIQUEMENT les .so de l'addon
    local addon_so_root="$standalone_dir/addons/$name"
    if [ ! -d "$addon_so_root" ]; then
        echo -e "${RED}  ✗ $addon_so_root absent du standalone${NC}"
        echo -e "${YELLOW}    Arborescence disponible :${NC}"
        find "$standalone_dir/addons" -maxdepth 3 -type d 2>/dev/null | sed 's/^/      /' | head -30
        return 1
    fi

    [ -n "${DIST_DIR:-}" ] || { warn "DIST_DIR non défini"; return 1; }
    local dest="$DIST_DIR/addons/$name"
    rm -rf "$dest"; mkdir -p "$dest"

    local so_count=0
    while IFS= read -r so_file; do
        [ -z "$so_file" ] && continue
        local rel="${so_file#$addon_so_root/}"
        # Exclure les .so issus des tests (si présents)
        case "$rel" in
            tests/*|*/tests/*) continue ;;
        esac
        local target="$dest/$rel"
        mkdir -p "$(dirname "$target")"
        cp "$so_file" "$target"
        so_count=$((so_count + 1))
    done < <(find "$addon_so_root" -type f -name "*.so" | sort)

    if [ "$so_count" -eq 0 ]; then
        echo -e "${RED}  ✗ Aucun .so trouvé sous $addon_so_root${NC}"
        return 1
    fi

    # 6. Données non-Python depuis la source préparée
    rsync -a \
        --exclude='*.py' --exclude='__pycache__' \
        --exclude='.history' --exclude='*.pyc' --exclude='*.pyo' \
        --exclude='_build' --exclude='*.db' --exclude='*.sqlite' \
        --exclude='*.so' \
        --exclude='tests/' \
        "$src_pkg/" "$dest/"

    local data_count
    data_count=$(find "$dest" -type f ! -name '*.so' | wc -l)

    # 7. Archiver manifeste
    if [ -f "$ADDON_MANIFEST" ]; then
        cp "$ADDON_MANIFEST" "$dest/.manifest.json"
    fi

    # 8. Nettoyer le standalone intermédiaire
    rm -rf "$standalone_dir"

    echo -e "${GREEN}  ✓ ${elapsed}s · ${so_count} .so + ${data_count} données → $dest${NC}"

    if [ -n "${LOG_FILE:-}" ]; then
        {
            echo "# Arborescence installée : $name"
            find "$dest" -type f | sed "s|$dest/||" | sort
        } >> "$LOG_FILE"
    fi

    export ADDON_SO_PATH="$dest/__init${PY_ABI_SUFFIX}"
    export ADDON_BUILD_OUT="$build_out"
    return 0
}


# ============================================================
#  VÉRIFICATION D'UN .so
# ============================================================

verify_so() {
    local so_file="$1"
    local name="$2"

    if [ ! -f "$so_file" ]; then
        warn "Le .so $so_file n'existe pas"; return 1
    fi

    local count size
    count=$(find "$(dirname "$so_file")" -name "*.so" | wc -l)
    size=$(du -h "$so_file" | cut -f1)

    if ! file "$so_file" | grep -q "ELF"; then
        warn "$so_file n'est pas un ELF"; return 1
    fi

    if command -v nm >/dev/null; then
        local symbols
        symbols=$(nm -D "$so_file" 2>/dev/null | grep -cE "PyInit_|main_ui|ModuleManager" || echo 0)
        if [ "$symbols" -lt 2 ]; then
            warn "$so_file contient peu de symboles ($symbols) — possible contenu vide"
        fi
    fi

    ok "$name : $size, $count .so au total"
    return 0
}

# ============================================================
#  IMPORT CHECK (optionnel) — test rapide post-install
# ============================================================
#  Usage : check_addon_import <name> [<dist_dir>]
#  Vérifie que addons.<name> est importable depuis le .dist
check_addon_import() {
    local name="$1"
    local dist="${2:-${DIST_DIR:-}}"
    [ -n "$dist" ] && [ -d "$dist" ] || { warn "dist introuvable pour import check"; return 1; }

    info "  🔎 import check : addons.$name"
    if (
        cd "$dist" &&
        "$PYTHON" - <<PYEOF


import sys
sys.path.insert(0, ".")
try:
    import addons.$name as m
    print("OK:", m.__file__)
except Exception as e:
    print("FAIL:", type(e).__name__, e)
    sys.exit(1)
PYEOF
    ); then
        ok "  addons.$name importable"
        return 0
    else
        warn "  addons.$name NON importable"
        return 1
    fi
}