#!/bin/bash
set -euo pipefail
# ============================================================
#  Addon : Parametres — compilation --standalone (Solution 1)
#  Auto-généré le 2026-10-27 10:49:40
#  ⚠ Sera ÉCRASÉ par --gen
# ============================================================

ADDON_NAME="Parametres"

ADDON_INCLUDES=(
    --include-package=addons.Parametres
    --include-package=addons.Parametres.tests
    --include-package=addons.Parametres.tests.integration
    --include-package=addons.Parametres.tests.unit
    --include-package=addons.Parametres.views.widgets
    --include-module=addons.Parametres.controllers.controller
    --include-module=addons.Parametres.controllers.login_controller
    --include-module=addons.Parametres.controllers.module_controller
    --include-module=addons.Parametres.controllers.setup_controller
    --include-module=addons.Parametres.main_ui
    --include-module=addons.Parametres.models.models
    --include-module=addons.Parametres.reports.audit_exporter
    --include-module=addons.Parametres.security.access_control
    --include-module=addons.Parametres.seed_db
    --include-module=addons.Parametres.tests.test_models
    --include-module=addons.Parametres.tests.unit.test_user_logic
    --include-module=addons.Parametres.views.about_us_view
    --include-module=addons.Parametres.views.accout_setting_view
    --include-module=addons.Parametres.views.dialog_form
    --include-module=addons.Parametres.views.loggin_view
    --include-module=addons.Parametres.views.parametre_module_view
    --include-module=addons.Parametres.views.setup_view
    --include-module=addons.Parametres.views.user_from
    --include-module=addons.Parametres.views.user_list_view
    --include-module=addons.Parametres.views.views
    --include-module=addons.Parametres.views.widgets.loading_page
    --include-package=addons.Parametres.controllers
    --include-package=addons.Parametres.controllers.__pycache__
    --include-package=addons.Parametres.models
    --include-package=addons.Parametres.models.__pycache__
    --include-package=addons.Parametres.reports
    --include-package=addons.Parametres.reports.__pycache__
    --include-package=addons.Parametres.security
    --include-package=addons.Parametres.static
    --include-package=addons.Parametres.views
    --include-package=addons.Parametres.views.__pycache__
    --include-package=addons.Parametres.views.widgets.__pycache__
)

source "$(dirname "${BASH_SOURCE[0]}")/../lib_build.sh"
export LOG_FILE="${LOG_FILE:-/dev/null}"
check_prerequisites
run_addon_standalone "$ADDON_NAME" "${ADDON_INCLUDES[@]}"
