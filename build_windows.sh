#!/bin/bash

# ========================================
#  Compilation de LOMETA pour Linux avec progression avancée
# ========================================

# Configuration des couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Fichier de log
LOG_FILE="build_log_$(date +%Y%m%d_%H%M%S).log"

# Barre de progression simple
progress_bar() {
    local current=$1
    local total=$2
    local width=60
    local percent=$((current * 100 / total))
    local filled=$((percent * width / 100))
    local empty=$((width - filled))
    
    printf "\r${CYAN}[${NC}"
    printf "%${filled}s" | tr ' ' '█'
    printf "%${empty}s" | tr ' ' '░'
    printf "${CYAN}]${NC} ${WHITE}%3d%%${NC}" "$percent"
}

# Fonction pour compiler avec PyInstaller et afficher la progression
compile_with_pyinstaller() {
    local build_name=$1
    local console_opt=$2
    local log_file=$3
    
    echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}📦 Compilation de ${build_name}${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    
    # Lancer PyInstaller et afficher la sortie en temps réel
    pyinstaller --noconfirm --onedir $console_opt \
        --name "${build_name}" \
        --icon "icon.ico" \
        --add-data "addons:addons" \
        --add-data "server/config.py:." \
        --add-data "version_manager.py:." \
        --add-data "update_manager.py:." \
        --add-data "update_dialog.py:." \
        --collect-all PySide6 \
        --collect-all PySide6.QtCharts \
        --collect-all sqlalchemy \
        --collect-all psycopg2 \
        --collect-all pandas \
        --collect-all numpy \
        --collect-all PIL \
        --collect-all requests \
        --collect-all qrcode \
        --collect-all reportlab \
        --collect-all openpyxl \
        --collect-all bcrypt \
        --collect-all flask \
        --collect-all flask_cors \
        --collect-all PyMySQL \
        --collect-all mysqlclient \
        --collect-all pyqtgraph \
        --collect-all python_dateutil \
        --collect-all dotenv \
        --collect-all urllib3 \
        --collect-all certifi \
        --collect-all idna \
        --collect-all charset_normalizer \
        --collect-all greenlet \
        --collect-all packaging \
        --collect-all typing_extensions \
        --collect-all six \
        --collect-all et_xmlfile \
        --collect-all xlrd \
        --collect-all altgraph \
        --collect-all colorama \
        --collect-all setuptools \
        --collect-all shiboken6 \
        --collect-all pytz \
        --collect-all tzdata \
        --collect-all markupsafe \
        --collect-all jinja2 \
        --collect-all itsdangerous \
        --collect-all click \
        --collect-all werkzeug \
        --collect-all cffi \
        --collect-all pycparser \
        --collect-all cryptography \
        --collect-all opencv_python \
        --collect-all cv2 \
        --collect-all opencv-python \
        --hidden-import "email" \
        --hidden-import "email.mime" \
        --hidden-import "email.mime.multipart" \
        --hidden-import "email.mime.text" \
        --hidden-import "email.mime.base" \
        --hidden-import "email.mime.image" \
        --hidden-import "email.mime.application" \
        --hidden-import "email.encoders" \
        --hidden-import "email.utils" \
        --hidden-import "smtplib" \
        --hidden-import "cv2" \
        --hidden-import "opencv-python" \
        --hidden-import "numpy" \
        --hidden-import "numpy.core" \
        --hidden-import "numpy.core._multiarray_umath" \
        --hidden-import "numpy.random" \
        --hidden-import "numpy.linalg" \
        --hidden-import "PySide6.QtCore" \
        --hidden-import "PySide6.QtWidgets" \
        --hidden-import "PySide6.QtGui" \
        --hidden-import "PySide6.QtNetwork" \
        --hidden-import "PySide6.QtSvg" \
        --hidden-import "PySide6.QtPrintSupport" \
        --hidden-import "PySide6.QtOpenGL" \
        --hidden-import "PySide6.QtOpenGLWidgets" \
        --hidden-import "PySide6.QtMultimedia" \
        --hidden-import "PySide6.QtMultimediaWidgets" \
        --hidden-import "PySide6.QtSql" \
        --hidden-import "PySide6.QtXml" \
        --hidden-import "PySide6.QtCharts" \
        --hidden-import "PySide6.QtCharts.QChart" \
        --hidden-import "PySide6.QtCharts.QChartView" \
        --hidden-import "PySide6.QtCharts.QPieSeries" \
        --hidden-import "PySide6.QtCharts.QBarSeries" \
        --hidden-import "PySide6.QtCharts.QBarSet" \
        --hidden-import "PySide6.QtCharts.QLineSeries" \
        --hidden-import "PySide6.QtCharts.QCategoryAxis" \
        --hidden-import "PySide6.QtCharts.QValueAxis" \
        --hidden-import "qrcode" \
        --hidden-import "qrcode.image.pil" \
        --hidden-import "qrcode.image.svg" \
        --hidden-import "qrcode.image.base" \
        --hidden-import "qrcode.util" \
        --hidden-import "PIL" \
        --hidden-import "PIL.Image" \
        --hidden-import "PIL.ImageDraw" \
        --hidden-import "PIL.ImageFont" \
        --hidden-import "PIL.ImageFilter" \
        --hidden-import "PIL.ImageEnhance" \
        --hidden-import "PIL.ImageColor" \
        --hidden-import "PIL.ImageFile" \
        --hidden-import "PIL.ImagePalette" \
        --hidden-import "PIL.ImageMode" \
        --hidden-import "PIL.ImageSequence" \
        --hidden-import "PIL.TiffImagePlugin" \
        --hidden-import "PIL.JpegImagePlugin" \
        --hidden-import "PIL.PngImagePlugin" \
        --hidden-import "PIL.GifImagePlugin" \
        --hidden-import "pandas" \
        --hidden-import "pandas.core" \
        --hidden-import "pandas.io" \
        --hidden-import "pandas.io.sql" \
        --hidden-import "pandas.io.parsers" \
        --hidden-import "pandas.io.excel" \
        --hidden-import "pandas.io.json" \
        --hidden-import "pandas.io.html" \
        --hidden-import "sqlalchemy" \
        --hidden-import "sqlalchemy.dialects.postgresql" \
        --hidden-import "sqlalchemy.dialects.mysql" \
        --hidden-import "sqlalchemy.dialects.sqlite" \
        --hidden-import "sqlalchemy.ext.declarative" \
        --hidden-import "sqlalchemy.orm" \
        --hidden-import "psycopg2" \
        --hidden-import "psycopg2._psycopg" \
        --hidden-import "psycopg2.extensions" \
        --hidden-import "psycopg2.extras" \
        --hidden-import "psycopg2.pool" \
        --hidden-import "psycopg2.sql" \
        --hidden-import "psycopg2.errorcodes" \
        --hidden-import "requests" \
        --hidden-import "requests.packages" \
        --hidden-import "requests.packages.urllib3" \
        --hidden-import "urllib3" \
        --hidden-import "urllib3.packages" \
        --hidden-import "certifi" \
        --hidden-import "idna" \
        --hidden-import "charset_normalizer" \
        --hidden-import "flask" \
        --hidden-import "flask.views" \
        --hidden-import "flask.json" \
        --hidden-import "flask_cors" \
        --hidden-import "reportlab" \
        --hidden-import "reportlab.lib" \
        --hidden-import "reportlab.lib.pagesizes" \
        --hidden-import "reportlab.lib.units" \
        --hidden-import "reportlab.lib.colors" \
        --hidden-import "reportlab.lib.utils" \
        --hidden-import "reportlab.lib.fonts" \
        --hidden-import "reportlab.lib.sequencer" \
        --hidden-import "reportlab.pdfbase" \
        --hidden-import "reportlab.pdfbase.pdfmetrics" \
        --hidden-import "reportlab.pdfbase.ttfonts" \
        --hidden-import "reportlab.pdfgen" \
        --hidden-import "reportlab.pdfgen.canvas" \
        --hidden-import "reportlab.pdfgen.textobject" \
        --hidden-import "reportlab.platypus" \
        --hidden-import "reportlab.platypus.doctemplate" \
        --hidden-import "reportlab.platypus.flowables" \
        --hidden-import "reportlab.platypus.paragraph" \
        --hidden-import "reportlab.platypus.tables" \
        --hidden-import "reportlab.platypus.frames" \
        --hidden-import "reportlab.graphics" \
        --hidden-import "reportlab.graphics.shapes" \
        --hidden-import "reportlab.graphics.widgets" \
        --hidden-import "reportlab.graphics.renderPDF" \
        --hidden-import "reportlab.graphics.charts" \
        --hidden-import "reportlab.graphics.charts.barcharts" \
        --hidden-import "reportlab.graphics.charts.linecharts" \
        --hidden-import "reportlab.graphics.charts.piecharts" \
        --hidden-import "openpyxl" \
        --hidden-import "openpyxl.cell" \
        --hidden-import "openpyxl.reader" \
        --hidden-import "openpyxl.workbook" \
        --hidden-import "openpyxl.writer" \
        --hidden-import "openpyxl.styles" \
        --hidden-import "openpyxl.formatting" \
        --hidden-import "openpyxl.chart" \
        --hidden-import "openpyxl.utils" \
        --hidden-import "bcrypt" \
        --hidden-import "PyMySQL" \
        --hidden-import "mysqlclient" \
        --hidden-import "pyqtgraph" \
        --hidden-import "pyqtgraph.Qt" \
        --hidden-import "pyqtgraph.graphicsItems" \
        --hidden-import "pyqtgraph.widgets" \
        --hidden-import "dateutil" \
        --hidden-import "dateutil.parser" \
        --hidden-import "dateutil.tz" \
        --hidden-import "dateutil.relativedelta" \
        --hidden-import "dotenv" \
        --hidden-import "greenlet" \
        --hidden-import "packaging" \
        --hidden-import "packaging.version" \
        --hidden-import "packaging.specifiers" \
        --hidden-import "packaging.requirements" \
        --hidden-import "typing_extensions" \
        --hidden-import "six" \
        --hidden-import "et_xmlfile" \
        --hidden-import "xlrd" \
        --hidden-import "altgraph" \
        --hidden-import "colorama" \
        --hidden-import "setuptools" \
        --hidden-import "setuptools._vendor" \
        --hidden-import "shiboken6" \
        --hidden-import "shiboken6.shiboken6" \
        --hidden-import "cffi" \
        --hidden-import "cryptography" \
        --hidden-import "cryptography.hazmat" \
        --hidden-import "cryptography.hazmat.backends" \
        --hidden-import "cryptography.hazmat.primitives" \
        --hidden-import "jinja2" \
        --hidden-import "jinja2.ext" \
        --hidden-import "markupsafe" \
        --hidden-import "itsdangerous" \
        --hidden-import "click" \
        --hidden-import "werkzeug" \
        --hidden-import "werkzeug.utils" \
        --hidden-import "werkzeug.serving" \
        --hidden-import "werkzeug.wsgi" \
        --hidden-import "werkzeug.middleware" \
        --hidden-import "pytz" \
        --hidden-import "tzdata" \
        --runtime-tmpdir "." \
        main.py 2>&1 | while IFS= read -r line; do
            # Afficher chaque ligne avec timestamp
            echo -e "${MAGENTA}[$(date +%H:%M:%S)]${NC} $line"
            echo "$line" >> "$log_file"
        done
    
    local exit_code=${PIPESTATUS[0]}
    return $exit_code
}

# Compteur de temps
timer_start() {
    START_TIME=$(date +%s)
}

timer_stop() {
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    local minutes=$((DURATION / 60))
    local seconds=$((DURATION % 60))
    echo -e "${CYAN}⏱️  Durée: ${minutes}m ${seconds}s${NC}"
}

# Fonction de logging
log() {
    echo "$1" >> "$LOG_FILE"
}

# En-tête
clear
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${WHITE}                    COMPILATION LOMETA LINUX                     ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
log "========================================"
log "Compilation de LOMETA pour Linux"
log "Date: $(date)"
log "========================================"

# Vérification de Python
echo -e "${YELLOW}┌────────────────────────────────────────────────────────────────┐${NC}"
echo -e "${YELLOW}│${NC} ${WHITE}VÉRIFICATION DE L'ENVIRONNEMENT${NC}"
echo -e "${YELLOW}└────────────────────────────────────────────────────────────────┘${NC}"

if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo -e "${GREEN}✓${NC} Python3 trouvé: $(python3 --version)"
    log "Python3 trouve: $(python3 --version)"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo -e "${GREEN}✓${NC} Python trouvé: $(python --version)"
    log "Python trouve: $(python --version)"
else
    echo -e "${RED}✗ Python non trouvé !${NC}"
    log "ERREUR: Python non trouve"
    exit 1
fi

# Vérification de pip
if command -v pip &> /dev/null; then
    echo -e "${GREEN}✓${NC} pip trouvé"
    log "pip trouve"
else
    echo -e "${YELLOW}⚠ pip non trouvé, installation...${NC}"
    sudo apt-get install -y python3-pip
fi
echo ""

# Étape 1: Nettoyage
echo -e "${YELLOW}┌────────────────────────────────────────────────────────────────┐${NC}"
echo -e "${YELLOW}│${NC} ${WHITE}ÉTAPE 1/5 : Nettoyage${NC}"
echo -e "${YELLOW}└────────────────────────────────────────────────────────────────┘${NC}"

for i in {1..3}; do
    progress_bar $i 3
    sleep 0.1
done
rm -rf build dist *.spec 2>/dev/null
echo -e "\r${GREEN}✓ Nettoyage terminé${NC}                    "
log "Nettoyage termine"
echo ""

# Étape 2: Installation des dépendances
echo -e "${YELLOW}┌────────────────────────────────────────────────────────────────┐${NC}"
echo -e "${YELLOW}│${NC} ${WHITE}ÉTAPE 2/5 : Installation des dépendances${NC}"
echo -e "${YELLOW}└────────────────────────────────────────────────────────────────┘${NC}"

REQUIREMENTS_FILE="requirements.txt"

if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo -e "${YELLOW}⚠ $REQUIREMENTS_FILE non trouvé, création...${NC}"
    cat > "$REQUIREMENTS_FILE" << 'EOF'
PySide6>=6.6.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
pandas>=2.0.0
numpy>=1.24.0
Pillow>=10.0.0
requests>=2.31.0
qrcode>=7.4.0
reportlab>=4.0.0
openpyxl>=3.1.0
bcrypt>=4.0.0
Flask>=2.3.0
Flask-CORS>=4.0.0
PyMySQL>=1.1.0
mysqlclient>=2.2.0
pyqtgraph>=0.13.0
python-dateutil>=2.8.0
python-dotenv>=1.0.0
EOF
    log "$REQUIREMENTS_FILE cree"
fi

TOTAL=$(grep -v '^#' "$REQUIREMENTS_FILE" | grep -v '^$' | wc -l)
CURRENT=0
FAILED_PACKAGES=""

timer_start

while IFS= read -r package || [ -n "$package" ]; do
    [[ "$package" =~ ^#.*$ ]] && continue
    [[ -z "$package" ]] && continue
    
    CURRENT=$((CURRENT + 1))
    percent=$((CURRENT * 100 / TOTAL))
    
    printf "\r${CYAN}[${NC}"
    for ((p=0; p<percent/2; p++)); do printf "█"; done
    for ((p=percent/2; p<50; p++)); do printf "░"; done
    printf "${CYAN}]${NC} ${WHITE}%3d%%${NC} - ${BLUE}%-30s${NC}" "$percent" "$package"
    
    if ! pip install "$package" --quiet >> "$LOG_FILE" 2>&1; then
        FAILED_PACKAGES="$FAILED_PACKAGES $package"
        log "ECHEC installation: $package"
    else
        log "OK installation: $package"
    fi
    
done < "$REQUIREMENTS_FILE"

timer_stop

if [ -n "$FAILED_PACKAGES" ]; then
    echo -e "\r${YELLOW}⚠ Certains packages n'ont pas pu être installés:${NC}"
    echo -e "${RED}  $FAILED_PACKAGES${NC}"
    echo -e "${YELLOW}  Continuer malgré tout? (o/N)${NC}"
    read -r response
    if [[ ! "$response" =~ ^[OoYy]$ ]]; then
        exit 1
    fi
else
    echo -e "\r${GREEN}✓ Installation terminée${NC}                                      "
fi
echo ""

# Étape 3: Installation de PyInstaller
echo -e "${YELLOW}┌────────────────────────────────────────────────────────────────┐${NC}"
echo -e "${YELLOW}│${NC} ${WHITE}ÉTAPE 3/5 : Installation de PyInstaller${NC}"
echo -e "${YELLOW}└────────────────────────────────────────────────────────────────┘${NC}"

if ! command -v pyinstaller &> /dev/null; then
    echo -e "${YELLOW}⚠ PyInstaller non trouvé, installation...${NC}"
    pip install pyinstaller >> "$LOG_FILE" 2>&1
fi

if ! command -v pyinstaller &> /dev/null; then
    echo -e "${RED}✗ PyInstaller n'a pas pu être installé !${NC}"
    log "ERREUR: PyInstaller non installe"
    exit 1
fi

echo -e "${GREEN}✓ PyInstaller disponible: $(pyinstaller --version)${NC}"
log "PyInstaller version: $(pyinstaller --version)"
echo ""

# Étape 4: Compilation DEBUG (avec console)
echo -e "${YELLOW}┌────────────────────────────────────────────────────────────────┐${NC}"
echo -e "${YELLOW}│${NC} ${WHITE}ÉTAPE 4/5 : Compilation DEBUG (avec console)${NC}"
echo -e "${YELLOW}└────────────────────────────────────────────────────────────────┘${NC}"

timer_start
compile_with_pyinstaller "LOMETA_DEBUG" "--console" "$LOG_FILE"
if [ $? -eq 0 ]; then
    timer_stop
    echo -e "${GREEN}✓ Compilation DEBUG réussie${NC}"
    log "Compilation DEBUG reussie"
else
    timer_stop
    echo -e "${RED}✗ Erreur lors de la compilation DEBUG${NC}"
    log "ERREUR compilation DEBUG"
    exit 1
fi
echo ""

# Étape 5: Compilation FINALE (sans console)
echo -e "${YELLOW}┌────────────────────────────────────────────────────────────────┐${NC}"
echo -e "${YELLOW}│${NC} ${WHITE}ÉTAPE 5/5 : Compilation FINALE (sans console)${NC}"
echo -e "${YELLOW}└────────────────────────────────────────────────────────────────┘${NC}"

timer_start
compile_with_pyinstaller "LOMETA" "--windowed" "$LOG_FILE"
if [ $? -eq 0 ]; then
    timer_stop
    echo -e "${GREEN}✓ Compilation FINALE réussie${NC}"
    log "Compilation FINALE reussie"
else
    timer_stop
    echo -e "${RED}✗ Erreur lors de la compilation FINALE${NC}"
    log "ERREUR compilation FINALE"
    exit 1
fi
echo ""

# Finalisation
echo -e "${YELLOW}┌────────────────────────────────────────────────────────────────┐${NC}"
echo -e "${YELLOW}│${NC} ${WHITE}FINALISATION${NC}"
echo -e "${YELLOW}└────────────────────────────────────────────────────────────────┘${NC}"

# Création des dossiers addons
mkdir -p "dist/LOMETA/addons"
mkdir -p "dist/LOMETA_DEBUG/addons"
echo "# Dossier des modules" > "dist/LOMETA/addons/README.txt"
echo "# Dossier des modules" > "dist/LOMETA_DEBUG/addons/README.txt"
echo -e "${GREEN}✓ Dossiers addons créés${NC}"

# Copie du fichier de log
cp "$LOG_FILE" "dist/LOMETA/$LOG_FILE" 2>/dev/null
cp "$LOG_FILE" "dist/LOMETA_DEBUG/$LOG_FILE" 2>/dev/null
echo -e "${GREEN}✓ Log copié dans les dossiers de sortie${NC}"

# Ajout des permissions d'exécution
if [ -f "dist/LOMETA/LOMETA" ]; then
    chmod +x "dist/LOMETA/LOMETA"
    echo -e "${GREEN}✓ Permissions ajoutées: dist/LOMETA/LOMETA${NC}"
fi

if [ -f "dist/LOMETA_DEBUG/LOMETA_DEBUG" ]; then
    chmod +x "dist/LOMETA_DEBUG/LOMETA_DEBUG"
    echo -e "${GREEN}✓ Permissions ajoutées: dist/LOMETA_DEBUG/LOMETA_DEBUG${NC}"
fi

# Taille des dossiers
SIZE_FINAL=$(du -sh dist/LOMETA 2>/dev/null | cut -f1)
SIZE_DEBUG=$(du -sh dist/LOMETA_DEBUG 2>/dev/null | cut -f1)

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${WHITE}                    COMPILATION TERMINÉE                     ${GREEN}║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${WHITE}📦 Exécutable FINAL :${NC} ${CYAN}dist/LOMETA/LOMETA${NC} ${WHITE}(${SIZE_FINAL})${NC}"
echo -e "${WHITE}🐛 Exécutable DEBUG :${NC} ${CYAN}dist/LOMETA_DEBUG/LOMETA_DEBUG${NC} ${WHITE}(${SIZE_DEBUG})${NC}"
echo -e "${WHITE}📋 Fichier log :${NC}      ${CYAN}$LOG_FILE${NC}"
echo ""
echo -e "${YELLOW}Pour diagnostiquer les erreurs :${NC}"
echo -e "  1. ${WHITE}./dist/LOMETA_DEBUG/LOMETA_DEBUG${NC} - Pour voir les erreurs en console"
echo -e "  2. ${WHITE}cat $LOG_FILE${NC} - Pour consulter le log complet"
echo ""

log "========================================"
log "Compilation terminee avec succes"
log "========================================"