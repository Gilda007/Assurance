#!/bin/bash
# ============================================================
#  LOMETA — Compilation d'UN SEUL addon (itération rapide)
#  Usage : ./build_addon_one.sh <nom_addon>
#  Exemple : ./build_addon_one.sh Automobiles
# ============================================================

set -e

ADDON="${1:-}"
if [ -z "$ADDON" ]; then
    echo "Usage : $0 <nom_addon>"
    echo "Addons disponibles :"
    for p in addons/*/; do [ -d "$p" ] && echo "  - $(basename "$p")"; done
    exit 1
fi

# Vérifier que l'addon existe
[ -d "addons/$ADDON" ] || { echo "✗ Addon introuvable : addons/$ADDON"; exit 1; }

# Trouver le dist
DIST_DIR=$(find dist_secure -maxdepth 1 -type d -name "*.dist" 2>/dev/null | head -n1)
[ -z "$DIST_DIR" ] && { echo "✗ dist_secure/*.dist introuvable — lancez build_windows.sh d'abord"; exit 1; }

echo "════════════════════════════════════════════════════════════════"
echo "  Compilation rapide de : $ADDON"
echo "  Cible : $DIST_DIR/addons/$ADDON"
echo "════════════════════════════════════════════════════════════════"

# --- Préparer ---
BUILD_DIR="addons_compiled/$ADDON"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

rsync -a \
    --exclude='.history' --exclude='__pycache__' \
    --exclude='*.pyc' --exclude='test_*.py' \
    --exclude='*.db' --exclude='*.sqlite' \
    "addons/$ADDON/" "$BUILD_DIR/"

[ -f "$BUILD_DIR/__init__.py" ] || printf '# auto\n' > "$BUILD_DIR/__init__.py"

# --- Compiler ---
mkdir -p "$BUILD_DIR/_build"
START=$(date +%s)

python3 -m nuitka \
    --module \
    --assume-yes-for-downloads \
    --enable-plugin=pyside6 \
    --nofollow-import-to=pytest \
    --nofollow-import-to=tkinter \
    --nofollow-import-to=PyQt5 \
    --nofollow-import-to=PyQt6 \
    --nofollow-import-to=matplotlib \
    --include-package="addons.$ADDON" \
    --include-package-data="addons.$ADDON" \
    --output-dir="$BUILD_DIR/_build" \
    --no-pyi-file \
    "$BUILD_DIR"

ELAPSED=$(( $(date +%s) - START ))

# --- Vérifier ---
SO_FILE=$(find "$BUILD_DIR/_build" -name "*.so" | head -n1)
[ -z "$SO_FILE" ] && { echo "✗ Aucune .so générée"; exit 1; }

# --- Installer dans le dist ---
DEST="$DIST_DIR/addons/$ADDON"
rm -rf "$DEST"
mkdir -p "$DEST"
cp "$SO_FILE" "$DEST/__init__.so"
find "$BUILD_DIR/_build" -name "*.so" ! -path "$SO_FILE" -exec cp {} "$DEST/" \; 2>/dev/null || true
rsync -a \
    --exclude='*.py' --exclude='__pycache__' \
    --exclude='_build' --exclude='*.db' --exclude='*.sqlite' \
    "$BUILD_DIR/" "$DEST/"

echo ""
echo "✅ $ADDON compilé en ${ELAPSED}s"
echo "   .so     : $(du -h "$DEST/__init__.so" | cut -f1)"
echo "   Installé : $DEST"
echo ""
echo "🧪 Tester :"
echo "   cd $DIST_DIR && ./LOMETA"