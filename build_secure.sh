#!/bin/bash
# ============================================================================
# COMPILATION SÉCURISÉE DE LOMETA AVEC CYTHON + PYINSTALLER
# Mode : --onedir (pas onefile)
# ============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
NC='\033[0m'

set -e

# ============================================================================
# FONCTIONS
# ============================================================================

print_header() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${WHITE}            COMPILATION SÉCURISÉE LOMETA (CYTHON)              ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_step() {
    echo ""
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}  $1${NC}"
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# ============================================================================
# VÉRIFICATION DE L'ENVIRONNEMENT
# ============================================================================

check_environment() {
    print_step "ÉTAPE 1: VÉRIFICATION DE L'ENVIRONNEMENT"
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        print_success "Python3 trouvé: $(python3 --version)"
    else
        print_error "Python3 non trouvé"
        exit 1
    fi
    
    if ! pip3 show Cython &> /dev/null; then
        print_info "Installation de Cython..."
        pip3 install Cython
    fi
    print_success "Cython installé"
    
    if ! pip3 show pyinstaller &> /dev/null; then
        print_info "Installation de PyInstaller..."
        pip3 install pyinstaller
    fi
    print_success "PyInstaller installé"
    
    if [ ! -d "addons" ]; then
        print_error "Dossier addons non trouvé"
        exit 1
    fi
    
    mkdir -p build_temp
    mkdir -p dist
    
    # Nettoyer les anciennes compilations
    rm -rf dist/LOMETA dist/LOMETA_DEBUG
}

# ============================================================================
# ÉTAPE 2: CRÉATION D'UNE COPIE DE TRAVAIL
# ============================================================================

create_working_copy() {
    print_step "ÉTAPE 2: CRÉATION D'UNE COPIE DE TRAVAIL"
    
    WORK_DIR="build_temp/addons_working"
    rm -rf "$WORK_DIR"
    
    print_info "Copie du dossier addons vers $WORK_DIR..."
    cp -r addons "$WORK_DIR"
    print_success "Copie créée"
    
    nb_files=$(find "$WORK_DIR" -name "*.py" | wc -l)
    print_info "Fichiers Python à compiler: $nb_files"
}

# ============================================================================
# ÉTAPE 3: COMPILATION CYTHON SUR LA COPIE
# ============================================================================

compile_cython() {
    print_step "ÉTAPE 3: COMPILATION CYTHON"
    
    WORK_DIR="build_temp/addons_working"
    CYTHON_BUILD_DIR="build_temp/cython_build"
    rm -rf "$CYTHON_BUILD_DIR"
    mkdir -p "$CYTHON_BUILD_DIR"
    
    for module_dir in "$WORK_DIR"/*/; do
        if [ -d "$module_dir" ]; then
            module_name=$(basename "$module_dir")
            print_info "Compilation du module: $module_name"
            
            module_build_dir="$CYTHON_BUILD_DIR/$module_name"
            mkdir -p "$module_build_dir"
            
            cp -r "$module_dir"/* "$module_build_dir/" 2>/dev/null || true
            
            cat > "$module_build_dir/setup.py" << 'EOF'
import os
import sys
from setuptools import setup, Extension
from Cython.Build import cythonize

py_files = []
exclude_patterns = ['test*.py', '*_test.py', 'conftest.py', 'old.py', 'test.py', 'settings_local.py']

for root, dirs, files in os.walk('.'):
    if 'tests' in root.split(os.sep):
        continue
    if '__pycache__' in root:
        continue
    if '.git' in root:
        continue
    
    for file in files:
        if file.endswith('.py') and file != '__init__.py':
            is_excluded = False
            for pattern in exclude_patterns:
                if file.startswith('test') or file.endswith('_test.py') or file == 'test.py' or file == 'old.py':
                    is_excluded = True
                    break
            if not is_excluded:
                py_files.append(os.path.join(root, file))

extensions = []
for py_file in py_files:
    module_name = py_file.replace('/', '.').replace('.py', '')
    module_name = module_name.lstrip('.')
    if not module_name or module_name.startswith('.'):
        continue
    if module_name.startswith('_'):
        continue
    ext = Extension(
        module_name,
        [py_file],
        extra_compile_args=['-O3'],
        extra_link_args=['-O3']
    )
    extensions.append(ext)

if extensions:
    setup(
        name='cython_module',
        ext_modules=cythonize(
            extensions,
            compiler_directives={
                'language_level': 3,
                'boundscheck': False,
                'wraparound': False,
                'initializedcheck': False,
                'nonecheck': False,
                'cdivision': True,
                'profile': False
            },
            nthreads=1
        )
    )
else:
    print("Aucun fichier à compiler")
EOF
            
            cd "$module_build_dir"
            python3 setup.py build_ext --inplace 2>&1 | grep -v "warning:" | grep -v "not a valid module name" || true
            cd - > /dev/null
            
            find "$module_build_dir" -name "*.so" -o -name "*.pyd" 2>/dev/null | while read -r so_file; do
                rel_path="${so_file#$module_build_dir/}"
                if [[ "$rel_path" == *".cpython-"* ]]; then
                    base_name=$(echo "$rel_path" | sed 's/\.cpython-[0-9]*\.so$/.py/')
                    py_name="$base_name"
                else
                    py_name="${rel_path%.so}.py"
                fi
                dest_file="$WORK_DIR/$module_name/$py_name"
                dest_dir=$(dirname "$dest_file")
                mkdir -p "$dest_dir"
                cp "$so_file" "$dest_file"
                print_info "   ✅ Compilé: $py_name"
            done
        fi
    done
    
    print_info "Suppression des fichiers .py originaux..."
    for module_dir in "$WORK_DIR"/*/; do
        if [ -d "$module_dir" ]; then
            find "$module_dir" -name "*.py" -not -name "__init__.py" -type f 2>/dev/null | while read -r py_file; do
                base_name=$(basename "$py_file" .py)
                py_dir=$(dirname "$py_file")
                if [ -f "$py_dir/$base_name.py" ]; then
                    if [ $(stat -c%s "$py_dir/$base_name.py" 2>/dev/null || echo 0) -gt 10000 ]; then
                        rm -f "$py_file"
                        print_info "   🗑️ Supprimé: $(basename "$py_file")"
                    fi
                fi
            done
        fi
    done
    
    find "$WORK_DIR" -type d -exec sh -c 'if [ ! -f "$1/__init__.py" ]; then touch "$1/__init__.py"; fi' _ {} \;
    
    print_success "Compilation Cython terminée"
}

# ============================================================================
# ÉTAPE 4: PRÉPARATION POUR PYINSTALLER
# ============================================================================

prepare_for_pyinstaller() {
    print_step "ÉTAPE 4: PRÉPARATION POUR PYINSTALLER"
    
    WORK_DIR="build_temp/addons_working"
    
    if [ ! -d "addons_original_backup" ]; then
        print_info "Sauvegarde du dossier addons original..."
        cp -r addons addons_original_backup
    fi
    
    print_info "Remplacement du dossier addons par la version compilée..."
    rm -rf addons
    cp -r "$WORK_DIR" addons
    
    print_success "Dossier addons mis à jour avec les modules compilés"
}

# ============================================================================
# ÉTAPE 5: COMPILATION PYINSTALLER EN MODE --onedir
# ============================================================================

compile_pyinstaller() {
    print_step "ÉTAPE 5: COMPILATION PYINSTALLER (--onedir)"
    
    print_info "Compilation de LOMETA avec PyInstaller en mode --onedir..."
    
    cat > "lometa_secure.spec" << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('addons', 'addons'),
    ],
    hiddenimports=[
        'core', 'core.loader', 'core.workers', 'core.workers.database_worker',
        'core.workers.query_cache', 'core.base_module', 'core.alerts',
        'core.logger', 'core.database', 'core.widgets.global_loader',
        'core.local_db', 'module_detector', 'certificate_manager',
        'addons.Paramètres.views.setup_view',
        'addons.Paramètres.controllers.setup_controller',
        'addons.Paramètres.views.loggin_view',
        'addons.Paramètres.controllers.login_controller',
        'addons.Paramètres.models.models',
        'numpy', 'numpy.core', 'numpy.core._multiarray_umath',
        'numpy.random', 'numpy.linalg', 'numpy.fft',
        'pandas', 'pandas.core', 'pandas.io', 'pandas.io.sql',
        'pandas.io.parsers', 'pandas.io.excel', 'pandas.io.json',
        'sqlalchemy', 'sqlalchemy.dialects.postgresql',
        'sqlalchemy.ext.declarative', 'sqlalchemy.orm',
        'psycopg2', 'psycopg2._psycopg', 'psycopg2.extensions',
        'psycopg2.extras', 'psycopg2.pool', 'psycopg2.sql',
        'psycopg2.errorcodes', 'PySide6', 'PySide6.QtCore',
        'PySide6.QtWidgets', 'PySide6.QtGui', 'PySide6.QtNetwork',
        'PySide6.QtSvg', 'PySide6.QtPrintSupport', 'PySide6.QtOpenGL',
        'PySide6.QtOpenGLWidgets', 'PySide6.QtMultimedia',
        'PySide6.QtMultimediaWidgets', 'PySide6.QtSql', 'PySide6.QtXml',
        'PySide6.QtCharts', 'qrcode', 'qrcode.image.pil',
        'PIL', 'PIL.Image', 'PIL.ImageDraw', 'PIL.ImageFont',
        'PIL.ImageFilter', 'PIL.ImageEnhance', 'PIL.ImageColor',
        'reportlab', 'reportlab.lib', 'reportlab.lib.pagesizes',
        'reportlab.lib.units', 'reportlab.lib.colors',
        'reportlab.pdfbase', 'reportlab.pdfgen',
        'reportlab.platypus', 'openpyxl', 'openpyxl.cell',
        'openpyxl.reader', 'openpyxl.workbook', 'openpyxl.writer',
        'openpyxl.styles', 'openpyxl.formatting', 'openpyxl.chart',
        'openpyxl.utils', 'bcrypt', 'flask', 'flask.views',
        'flask.json', 'flask_cors', 'requests',
        'requests.packages', 'requests.packages.urllib3',
        'urllib3', 'certifi', 'idna', 'charset_normalizer',
        'python_dateutil', 'dateutil.parser', 'dateutil.tz',
        'dateutil.relativedelta', 'dotenv', 'greenlet',
        'packaging', 'packaging.version', 'packaging.specifiers',
        'typing_extensions', 'six', 'et_xmlfile', 'xlrd',
        'altgraph', 'colorama', 'setuptools', 'shiboken6',
        'cffi', 'cryptography', 'jinja2', 'markupsafe',
        'itsdangerous', 'click', 'werkzeug', 'pytz', 'tzdata',
        'pyqtgraph', 'pyqtgraph.Qt', 'pyqtgraph.graphicsItems',
        'pyqtgraph.widgets', 'email', 'email.mime', 'email.mime.multipart',
        'email.mime.text', 'email.mime.base', 'email.mime.image',
        'email.mime.application', 'email.encoders', 'email.utils',
        'smtplib'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyd = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyd,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LOMETA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
EOF

    # ✅ Utiliser --onedir (pas --onefile)
    python3 -m PyInstaller --noconfirm --onedir lometa_secure.spec
    
    if [ $? -eq 0 ]; then
        print_success "Compilation PyInstaller réussie"
    else
        print_error "Échec de la compilation PyInstaller"
        exit 1
    fi
}

# ============================================================================
# ÉTAPE 6: COMPILATION DEBUG
# ============================================================================

compile_debug() {
    print_step "ÉTAPE 6: COMPILATION DEBUG (avec console)"
    
    print_info "Compilation DEBUG de LOMETA avec console..."
    
    cat > "lometa_debug.spec" << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('addons', 'addons'),
    ],
    hiddenimports=[
        'core', 'core.loader', 'core.workers', 'core.workers.database_worker',
        'core.workers.query_cache', 'core.base_module', 'core.alerts',
        'core.logger', 'core.database', 'core.widgets.global_loader',
        'core.local_db', 'module_detector', 'certificate_manager',
        'addons.Paramètres.views.setup_view',
        'addons.Paramètres.controllers.setup_controller',
        'addons.Paramètres.views.loggin_view',
        'addons.Paramètres.controllers.login_controller',
        'addons.Paramètres.models.models',
        'numpy', 'numpy.core', 'numpy.core._multiarray_umath',
        'numpy.random', 'numpy.linalg', 'numpy.fft',
        'pandas', 'pandas.core', 'pandas.io', 'pandas.io.sql',
        'pandas.io.parsers', 'pandas.io.excel', 'pandas.io.json',
        'sqlalchemy', 'sqlalchemy.dialects.postgresql',
        'sqlalchemy.ext.declarative', 'sqlalchemy.orm',
        'psycopg2', 'psycopg2._psycopg', 'psycopg2.extensions',
        'psycopg2.extras', 'psycopg2.pool', 'psycopg2.sql',
        'psycopg2.errorcodes', 'PySide6', 'PySide6.QtCore',
        'PySide6.QtWidgets', 'PySide6.QtGui', 'PySide6.QtNetwork',
        'PySide6.QtSvg', 'PySide6.QtPrintSupport', 'PySide6.QtOpenGL',
        'PySide6.QtOpenGLWidgets', 'PySide6.QtMultimedia',
        'PySide6.QtMultimediaWidgets', 'PySide6.QtSql', 'PySide6.QtXml',
        'PySide6.QtCharts', 'qrcode', 'qrcode.image.pil',
        'PIL', 'PIL.Image', 'PIL.ImageDraw', 'PIL.ImageFont',
        'PIL.ImageFilter', 'PIL.ImageEnhance', 'PIL.ImageColor',
        'reportlab', 'reportlab.lib', 'reportlab.lib.pagesizes',
        'reportlab.lib.units', 'reportlab.lib.colors',
        'reportlab.pdfbase', 'reportlab.pdfgen',
        'reportlab.platypus', 'openpyxl', 'openpyxl.cell',
        'openpyxl.reader', 'openpyxl.workbook', 'openpyxl.writer',
        'openpyxl.styles', 'openpyxl.formatting', 'openpyxl.chart',
        'openpyxl.utils', 'bcrypt', 'flask', 'flask.views',
        'flask.json', 'flask_cors', 'requests',
        'requests.packages', 'requests.packages.urllib3',
        'urllib3', 'certifi', 'idna', 'charset_normalizer',
        'python_dateutil', 'dateutil.parser', 'dateutil.tz',
        'dateutil.relativedelta', 'dotenv', 'greenlet',
        'packaging', 'packaging.version', 'packaging.specifiers',
        'typing_extensions', 'six', 'et_xmlfile', 'xlrd',
        'altgraph', 'colorama', 'setuptools', 'shiboken6',
        'cffi', 'cryptography', 'jinja2', 'markupsafe',
        'itsdangerous', 'click', 'werkzeug', 'pytz', 'tzdata',
        'pyqtgraph', 'pyqtgraph.Qt', 'pyqtgraph.graphicsItems',
        'pyqtgraph.widgets', 'email', 'email.mime', 'email.mime.multipart',
        'email.mime.text', 'email.mime.base', 'email.mime.image',
        'email.mime.application', 'email.encoders', 'email.utils',
        'smtplib'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyd = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyd,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LOMETA_DEBUG',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # ✅ Console active pour le debug
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
EOF

    python3 -m PyInstaller --noconfirm --onedir lometa_debug.spec
    
    if [ $? -eq 0 ]; then
        print_success "Compilation DEBUG réussie"
    else
        print_warning "Échec de la compilation DEBUG (non bloquant)"
    fi
    
    rm -f lometa_debug.spec
}

# ============================================================================
# ÉTAPE 7: NETTOYAGE ET FINALISATION
# ============================================================================

finalize() {
    print_step "ÉTAPE 7: NETTOYAGE ET FINALISATION"
    
    # ✅ Restaurer le dossier addons original
    if [ -d "addons_original_backup" ]; then
        print_info "Restauration du dossier addons original..."
        rm -rf addons
        mv addons_original_backup addons
    fi
    
    # ✅ Nettoyer les fichiers temporaires
    print_info "Nettoyage des fichiers temporaires..."
    rm -rf build_temp
    rm -f lometa_secure.spec
    
    if [ -f "dist/LOMETA/LOMETA" ]; then
        chmod +x "dist/LOMETA/LOMETA"
        print_success "Permissions ajoutées"
    fi
    
    if [ -f "dist/LOMETA_DEBUG/LOMETA_DEBUG" ]; then
        chmod +x "dist/LOMETA_DEBUG/LOMETA_DEBUG"
        print_success "Permissions ajoutées (DEBUG)"
    fi
    
    # Tailles
    if [ -d "dist/LOMETA" ]; then
        size=$(du -sh dist/LOMETA 2>/dev/null | cut -f1)
        print_info "Taille finale: $size"
    fi
    
    print_success "Compilation terminée"
}

# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

main() {
    print_header
    
    if [ ! -f "main.py" ]; then
        print_error "main.py non trouvé. Exécutez depuis le dossier racine de LOMETA."
        exit 1
    fi
    
    check_environment
    create_working_copy
    compile_cython
    prepare_for_pyinstaller
    compile_pyinstaller
    compile_debug
    finalize
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${WHITE}              COMPILATION SÉCURISÉE TERMINÉE                 ${GREEN}║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${WHITE}📁 Production :${NC} ${CYAN}dist/LOMETA/LOMETA${NC}"
    echo -e "${WHITE}🐛 DEBUG      :${NC} ${CYAN}dist/LOMETA_DEBUG/LOMETA_DEBUG${NC}"
    echo -e "${WHITE}🔒 Protection :${NC} Cython (code machine)"
    echo -e "${WHITE}📦 Mode       :${NC} --onedir"
    echo ""
}

main