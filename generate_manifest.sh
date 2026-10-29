#!/bin/bash
# ============================================================
#  LOMETA — Génération du manifeste de distribution
#  Produit manifest.json avec hashes SHA-256 de tous les fichiers
# ============================================================
#  Usage :
#    ./generate_manifest.sh <chemin_dist> <version> [sortie.json]
#    ./generate_manifest.sh dist_secure/main.dist 1.2.3 dist_secure/manifest.json
# ============================================================

set -euo pipefail

DIST_PATH="${1:-}"
VERSION="${2:-0.0.0}"
OUTPUT="${3:-$DIST_PATH/manifest.json}"

[ -z "$DIST_PATH" ] && { echo "Usage: $0 <dist_path> <version> [output]"; exit 1; }
[ -d "$DIST_PATH" ] || { echo "Erreur: $DIST_PATH n'existe pas"; exit 1; }

DIST_PATH_ABS="$(cd "$DIST_PATH" && pwd)"
DIST_NAME="$(basename "$DIST_PATH_ABS")"

echo "🔍 Génération du manifeste…"
echo "   Dist    : $DIST_PATH_ABS"
echo "   Version : $VERSION"
echo "   Sortie  : $OUTPUT"

# ─── Trouver le binaire principal ───
BINARY=""
for candidate in "LOMETA" "LOMETA.exe" "LOMETA.bin"; do
    [ -f "$DIST_PATH_ABS/$candidate" ] && { BINARY="$candidate"; break; }
done
[ -z "$BINARY" ] && { echo "Erreur: binaire LOMETA introuvable"; exit 1; }

# ─── Générer la liste des fichiers avec hashes ───
cd "$DIST_PATH_ABS"

# Format JSON compatible avec update_manager.py
{
    echo "{"
    echo "  \"schema_version\": 1,"
    echo "  \"app_name\": \"LOMETA\","
    echo "  \"version\": \"$VERSION\","
    echo "  \"generated_at\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\","
    echo "  \"platform\": \"$(uname -s | tr '[:upper:]' '[:lower:]')\","
    echo "  \"arch\": \"$(uname -m)\","
    echo "  \"python_abi\": \"$(python3 -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX') or '')")\","
    echo "  \"binaire\": \"$BINARY\","
    echo "  \"binaire_sha256\": \"$(sha256sum "$BINARY" | cut -d' ' -f1)\","
    echo "  \"binaire_taille\": $(stat -c%s "$BINARY"),"
    echo ""

    # ─── Fichiers (hors binaire, hors manifeste) ───
    echo "  \"fichiers\": ["
    first=1
    # Lister tous les fichiers réguliers, trier pour un diff stable
    find . -type f \
        ! -path "./manifest.json" \
        ! -path "./manifest.json.sig" \
        ! -name "*.log" \
        ! -path "./__pycache__/*" \
        ! -path "./data/*" \
        | sed 's|^\./||' \
        | sort \
        | while IFS= read -r rel; do
            [ -z "$rel" ] && continue
            size=$(stat -c%s "$rel")
            hash=$(sha256sum "$rel" | cut -d' ' -f1)
            [ "$first" -eq 0 ] && echo ","
            first=0
            printf '    {"path": "%s", "size": %d, "sha256": "%s"}' \
                "$rel" "$size" "$hash"
        done
    echo ""
    echo "  ],"
    echo ""

    # ─── Dépendances système (optionnel) ───
    echo "  \"requirements\": {"
    echo "    \"python_min\": \"3.10\","
    echo "    \"os\": [\"linux\", \"windows\"],"
    echo "    \"libs_systeme\": [\"libGL\", \"libxkbcommon\", \"libxcb\"]"
    echo "  },"
    echo ""

    # ─── Statistiques ───
    total_files=$(find . -type f ! -path "./manifest.json*" ! -name "*.log" ! -path "./__pycache__/*" | wc -l)
    total_size=$(du -sb . 2>/dev/null | cut -f1)
    echo "  \"total_fichiers\": $total_files,"
    echo "  \"total_taille\": $total_size"
    echo "}"
} > "$OUTPUT"

echo ""
echo "✅ Manifeste généré : $OUTPUT"
echo "   Taille : $(du -h "$OUTPUT" | cut -f1)"
echo "   Fichiers : $(grep -c '"path"' "$OUTPUT" || echo 0)"
