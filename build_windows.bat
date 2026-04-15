@echo off
chcp 65001 >nul
echo ========================================
echo  Compilation de LOMETA pour Windows
echo ========================================
echo.

REM Nettoyage
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
del /q *.spec 2>nul

REM Installation des dépendances
echo Installation des dependances...
pip install -r requirements.txt --quiet

REM Compilation avec tous les modules importants
echo Compilation en cours...
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
    --collect-all requests ^
    --collect-all urllib3 ^
    --hidden-import=PySide6.QtCore ^
    --hidden-import=PySide6.QtWidgets ^
    --hidden-import=PySide6.QtGui ^
    --hidden-import=PySide6.QtNetwork ^
    --hidden-import=sqlalchemy.dialects.postgresql ^
    --hidden-import=psycopg2._psycopg ^
    --hidden-import=psycopg2.extensions ^
    --hidden-import=psycopg2.extras ^
    --hidden-import=PIL._imaging ^
    --hidden-import=config ^
    --hidden-import=version_manager ^
    --hidden-import=update_manager ^
    --hidden-import=requests ^
    --hidden-import=urllib3 ^
    --hidden-import=certifi ^
    --hidden-import=idna ^
    --hidden-import=charset_normalizer ^
    --hidden-import=flask ^
    --hidden-import=flask_cors ^
    --runtime-tmpdir "." ^
    --clean ^
    main.py

if errorlevel 1 (
    echo ERREUR lors de la compilation !
    pause
    exit /b 1
)

REM Créer le dossier addons
if not exist "dist\LOMETA\addons" mkdir "dist\LOMETA\addons"
echo # Dossier des modules > dist\LOMETA\addons\README.txt

echo.
echo ========================================
echo  Compilation terminee !
echo  Executable : dist\LOMETA\LOMETA.exe
echo ========================================
pause