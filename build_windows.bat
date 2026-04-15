@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================================
echo   Compilation de LOMETA pour Windows
echo   Inclusion de TOUTES les dependances
echo ============================================================
echo.

REM Nettoyage
echo [1/6] Nettoyage des anciens builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
del /q *.spec 2>nul
echo OK
echo.

REM Installation des dépendances
echo [2/6] Installation de TOUTES les dependances...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ATTENTION: Certains paquets n'ont pas pu etre installes
    echo Continuons quand meme...
)
echo OK
echo.

REM Génération de la liste complète des modules
echo [3/6] Analyse des modules a inclure...

python -c "
import pkgutil
import sys
import re

# Modules de base a inclure
base_modules = [
    'PySide6', 'sqlalchemy', 'psycopg2', 'qrcode', 'PIL',
    'requests', 'urllib3', 'certifi', 'idna', 'charset_normalizer',
    'flask', 'flask_cors', 'pandas', 'numpy', 'openpyxl',
    'mysqlclient', 'PyMySQL', 'pyqtgraph', 'reportlab',
    'python_dotenv', 'dotenv', 'bcrypt', 'xlrd', 'et_xmlfile',
    'greenlet', 'six', 'typing_extensions', 'packaging',
    'colorama', 'altgraph', 'setuptools', 'shiboken6',
    'pyinstaller', 'pyinstaller_hooks_contrib',
    'opencv_python', 'cv2', 'numpy', 'dateutil',
    'config', 'version_manager', 'update_manager'
]

# Ajouter les sous-modules pour les paquets complexes
complex_packages = ['PySide6', 'sqlalchemy', 'psycopg2', 'PIL', 'numpy', 'pandas']

# Générer les flags --hidden-import
hidden_imports = set()

# Ajouter les modules de base
for m in base_modules:
    if m:
        hidden_imports.add(m)

# Ajouter les sous-modules pour les paquets complexes
for package in complex_packages:
    try:
        mod = __import__(package)
        if hasattr(mod, '__path__'):
            for submod in pkgutil.iter_modules(mod.__path__):
                if submod.name:
                    hidden_imports.add(f'{package}.{submod.name}')
    except ImportError:
        pass

# Ajouter les modules specifiques SQLAlchemy
hidden_imports.add('sqlalchemy.dialects.postgresql')
hidden_imports.add('sqlalchemy.dialects.mysql')
hidden_imports.add('sqlalchemy.dialects.sqlite')
hidden_imports.add('sqlalchemy.ext.declarative')
hidden_imports.add('sqlalchemy.orm')

# Ajouter les modules specifiques psycopg2
hidden_imports.add('psycopg2._psycopg')
hidden_imports.add('psycopg2.extensions')
hidden_imports.add('psycopg2.extras')
hidden_imports.add('psycopg2.pool')
hidden_imports.add('psycopg2.sql')

# Ajouter les modules specifiques PIL
hidden_imports.add('PIL._imaging')
hidden_imports.add('PIL._imagingft')
hidden_imports.add('PIL._imagingtk')
hidden_imports.add('PIL._webp')
hidden_imports.add('PIL.ImageDraw')
hidden_imports.add('PIL.ImageFilter')
hidden_imports.add('PIL.ImageFont')

# Ajouter les modules specifiques PySide6
pyside6_modules = [
    'PySide6.QtCore', 'PySide6.QtWidgets', 'PySide6.QtGui',
    'PySide6.QtNetwork', 'PySide6.QtSvg', 'PySide6.QtPrintSupport',
    'PySide6.QtMultimedia', 'PySide6.QtMultimediaWidgets',
    'PySide6.QtSql', 'PySide6.QtXml', 'PySide6.QtOpenGL',
    'PySide6.QtOpenGLWidgets', 'PySide6.QtCharts', 'PySide6.QtWebEngine',
    'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets',
    'PySide6.QtWebSockets', 'PySide6.QtDBus', 'PySide6.QtTest'
]
for m in pyside6_modules:
    hidden_imports.add(m)

# Generer la ligne de commande
result = ' '.join([f'--hidden-import={h}' for h in sorted(hidden_imports)])
print(result)

# Sauvegarder
with open('hidden_imports_temp.txt', 'w', encoding='utf-8') as f:
    f.write(result)
"

REM Lire les hidden-imports générés
set /p HIDDEN_IMPORTS=<hidden_imports_temp.txt
del hidden_imports_temp.txt
echo OK
echo.

REM Compilation avec TOUS les paquets
echo [4/6] Compilation en cours (cela peut prendre plusieurs minutes)...
echo.

pyinstaller --onedir ^
    --name "LOMETA" ^
    --windowed ^
    --icon "icon.ico" ^
    --add-data "addons;addons" ^
    --collect-all PySide6 ^
    --collect-all sqlalchemy ^
    --collect-all psycopg2 ^
    --collect-all pandas ^
    --collect-all numpy ^
    --collect-all openpyxl ^
    --collect-all PIL ^
    --collect-all flask ^
    --collect-all flask_cors ^
    --collect-all requests ^
    --collect-all urllib3 ^
    --collect-all qrcode ^
    --collect-all reportlab ^
    --collect-all pyqtgraph ^
    --collect-all mysqlclient ^
    --collect-all PyMySQL ^
    --collect-all bcrypt ^
    --collect-all python_dotenv ^
    --collect-all opencv_python ^
    --collect-all dateutil ^
    %HIDDEN_IMPORTS% ^
    --runtime-tmpdir "." ^
    --clean ^
    --noconfirm ^
    --log-level WARN ^
    main.py

if errorlevel 1 (
    echo.
    echo ERREUR lors de la compilation !
    echo.
    echo Tentative de compilation avec options minimales...
    echo.
    
    REM Compilation de secours avec options minimales
    pyinstaller --onedir ^
        --name "LOMETA" ^
        --windowed ^
        --add-data "addons;addons" ^
        --collect-all PySide6 ^
        --collect-all sqlalchemy ^
        --collect-all psycopg2 ^
        --hidden-import=requests ^
        --hidden-import=flask ^
        --hidden-import=pandas ^
        --hidden-import=numpy ^
        main.py
)
echo OK
echo.

REM Créer la structure de sortie
echo [5/6] Preparation du dossier de sortie...
if not exist "dist\LOMETA\addons" mkdir "dist\LOMETA\addons"

REM Copier les dossiers addons existants
if exist "addons\Automobiles" (
    echo Copie du module Automobiles...
    xcopy /E /I /Y /Q "addons\Automobiles" "dist\LOMETA\addons\Automobiles"
)
if exist "addons\Paramètres" (
    echo Copie du module Parametres...
    xcopy /E /I /Y /Q "addons\Paramètres" "dist\LOMETA\addons\Paramètres"
)
if exist "addons\Finances" (
    echo Copie du module Finances...
    xcopy /E /I /Y /Q "addons\Finances" "dist\LOMETA\addons\Finances"
)
if exist "addons\versions.json" (
    copy /Y "addons\versions.json" "dist\LOMETA\addons\" >nul
)

REM Copier le README
echo # Dossier des modules > dist\LOMETA\addons\README.txt
echo Placez vos modules ici. >> dist\LOMETA\addons\README.txt
echo OK
echo.

REM Informations finales
echo [6/6] Compilation terminee !
echo.
echo ============================================================
echo                    RAPPORT DE COMPILATION
echo ============================================================
echo.
echo Executable : dist\LOMETA\LOMETA.exe
echo.
if exist "dist\LOMETA\LOMETA.exe" (
    for %%A in ("dist\LOMETA\LOMETA.exe") do (
        set /a size=%%~zA/1048576
        echo Taille     : !size! MB
    )
) else (
    echo Taille     : Fichier non trouve
)
echo.
echo Dossier addons : dist\LOMETA\addons\
echo.
echo ============================================================
echo.
echo Pour tester :
echo   cd dist\LOMETA
echo   LOMETA.exe
echo.
echo ============================================================
pause