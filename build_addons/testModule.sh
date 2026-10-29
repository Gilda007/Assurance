#!/bin/bash
set -euo pipefail
# ============================================================
#  Addon : testModule — compilation --standalone (Solution 1)
#  Auto-généré le 2026-10-27 10:36:31
#  ⚠ Sera ÉCRASÉ par --gen
# ============================================================

ADDON_NAME="testModule"

ADDON_INCLUDES=(
    --include-package=addons.testModule
    --include-package=addons.testModule.controllers
    --include-package=addons.testModule.migrations
    --include-package=addons.testModule.models
    --include-package=addons.testModule.tests
    --include-package=addons.testModule.views
    --include-package=addons.testModule.views.widgets
    --include-module=addons.testModule.main_ui
    --include-module=addons.testModule.views.view
    --include-module=addons.testModule.views.widgets.loading_page
    --include-package=addons.testModule.static
    --include-package=addons.testModule.templates
)

source "$(dirname "${BASH_SOURCE[0]}")/../lib_build.sh"
export LOG_FILE="${LOG_FILE:-/dev/null}"
check_prerequisites

# Auto-détection du dist
DIST_DIR="${DIST_DIR:-$(find "$DIST_ROOT" -maxdepth 1 -type d -name '*.dist' 2>/dev/null | head -n1)}"
[ -z "$DIST_DIR" ] && die "Aucun dist_secure/*.dist trouvé. Lancez ./build_linux.sh d'abord."
export DIST_DIR

run_addon_standalone "$ADDON_NAME" "${ADDON_INCLUDES[@]}"