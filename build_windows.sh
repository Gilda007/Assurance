#!/bin/bash

# ========================================
#  Compilation de LOMETA pour Linux
# ========================================

# Nettoyage 
echo "Nettoyage des anciens dossiers..."
rm -rf build dist
rm -f *.spec 

# Installation des dépendances
echo "Installation des dépendances..."
pip install -r requirements.txt --quiet 

# Compilation avec tous les modules importants
# Note : On remplace les ^ (Windows) par des \ (Linux) pour la continuité de ligne 
echo "Compilation en cours..."
pyinstaller --onedir \
    --name "LOMETA" \
    --windowed \
    --icon "icon.ico" \
    --add-data "addons:addons" \
    --collect-all PySide6 \
    --collect-all sqlalchemy \
    --collect-all psycopg2 \
    --collect-all pandas \
    --collect-all numpy \
    --collect-all openpyxl \
    --collect-all PIL \
    --collect-all flask \
    --collect-all requests \
    --collect-all urllib3 \
    --hidden-import=PySide6.QtCore \
    --hidden-import=PySide6.QtWidgets \
    --hidden-import=PySide6.QtGui \
    --hidden-import=PySide6.QtNetwork \
    --hidden-import=sqlalchemy.dialects.postgresql \
    --hidden-import=psycopg2._psycopg \
    --hidden-import=psycopg2.extensions \
    --hidden-import=psycopg2.extras \
    --hidden-import=PIL._imaging \
    --hidden-import=config \
    --hidden-import=version_manager \
    --hidden-import=update_manager \
    --hidden-import=requests \
    --hidden-import=urllib3 \
    --hidden-import=certifi \
    --hidden-import=idna \
    --hidden-import=charset_normalizer \
    --hidden-import=flask \
    --hidden-import=flask_cors \
    --runtime-tmpdir "." \
    --clean \
    main.py 

# Vérification des erreurs [cite: 5]
if [ $? -ne 0 ]; then
    echo "ERREUR lors de la compilation !"
    exit 1
fi

# Créer le dossier addons [cite: 5]
mkdir -p "dist/LOMETA/addons"
echo "# Dossier des modules" > dist/LOMETA/addons/README.txt 

echo ""
echo "========================================"
echo " Compilation terminée !"
echo " Exécutable : dist/LOMETA/LOMETA"
echo "========================================" 