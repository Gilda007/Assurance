
---

## 🪟 Script Windows : `compile_and_zip.bat`

```batch
@echo off
setlocal enabledelayedexpansion

REM ========================================
REM  Compilation et Archivage des Modules .pyc
REM  Version 1.0 - Windows
REM ========================================

set VERSION=1.0.0
set DATE=%DATE:/=_%
set TIME=%TIME::=_%
set TIMESTAMP=%DATE%_%TIME%
set TIMESTAMP=%TIMESTAMP: =0%
set LOG_FILE=compile_modules_%TIMESTAMP%.log
set OUTPUT_DIR=dist_compiled
set MODULES_DIR=%OUTPUT_DIR%\modules
set ARCHIVE_NAME=modules_compiled_%VERSION%_%TIMESTAMP%.zip

echo ============================================================
echo      COMPILATION & ARCHIVAGE MODULES .PYC - WINDOWS
echo ============================================================
echo.
echo [%DATE% %TIME%] Démarrage du script > %LOG_FILE%

REM Vérification de Python
echo 🔍 Vérification de Python...
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python non trouvé !
    echo ❌ Python non trouvé ! >> %LOG_FILE%
    pause
    exit /b 1
)

for /f "delims=" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python trouvé: %PYTHON_VERSION%
echo ✅ Python trouvé: %PYTHON_VERSION% >> %LOG_FILE%

REM Nettoyage
echo 🧹 Nettoyage des dossiers existants...
if exist "%OUTPUT_DIR%" rd /s /q "%OUTPUT_DIR%"
mkdir "%MODULES_DIR%" 2>nul

echo ✅ Dossiers préparés >> %LOG_FILE%

REM ========================================
REM  ÉTAPE 1: Compilation
REM ========================================
echo.
echo ════════════════════════════════════════════════════════════════
echo 🔒 ÉTAPE 1/3 : Compilation des modules en .pyc
echo ════════════════════════════════════════════════════════════════

echo 📝 Compilation des fichiers Python...
echo 📝 Compilation des fichiers Python... >> %LOG_FILE%

python -O -m compileall -b -f -q . ^
    --exclude="venv" ^
    --exclude=".git" ^
    --exclude="__pycache__" ^
    --exclude="dist" ^
    --exclude="build" ^
    --exclude="dist_compiled" ^
    >> %LOG_FILE% 2>&1

if errorlevel 1 (
    echo ❌ Erreur lors de la compilation
    echo ❌ Erreur lors de la compilation >> %LOG_FILE%
    pause
    exit /b 1
)

echo 📦 Organisation des modules compilés...
echo 📦 Organisation des modules compilés... >> %LOG_FILE%

set COUNT=0
for /r . %%F in (*.pyc) do (
    set "FILE=%%F"
    set "FILE=!FILE:%CD%\=!"
    
    REM Vérifier les exclusions
    echo !FILE! | findstr /i "venv .git __pycache__ dist build dist_compiled" > nul
    if errorlevel 1 (
        set "REL_PATH=!FILE:.pyc=.py!"
        set "DEST_FILE=%MODULES_DIR%\!REL_PATH!"
        set "DEST_DIR=!DEST_FILE!\.."
        
        mkdir "!DEST_DIR!" 2>nul
        
        REM Copier le .pyc
        copy "%%F" "!DEST_FILE!c" > nul
        
        REM Créer le loader .py
        (
            echo # -*- coding: utf-8 -*-
            echo # ⚠️  MODULE COMPILE - Code source non disponible
            echo import os, sys, importlib.util
            echo.
            echo __all__ = []
            echo.
            echo def __load_module():
            echo     module_name = __name__
            echo     pyc_path = __file__ + 'c'
            echo     if not os.path.isfile(pyc_path):
            echo         raise ImportError(f"Fichier compile manquant: {pyc_path}")
            echo     try:
            echo         spec = importlib.util.spec_from_file_location(module_name, pyc_path)
            echo         module = importlib.util.module_from_spec(spec)
            echo         spec.loader.exec_module(module)
            echo         sys.modules[module_name] = module
            echo         for attr_name in dir(module):
            echo             if not attr_name.startswith('_'):
            echo                 globals()[attr_name] = getattr(module, attr_name)
            echo         if hasattr(module, '__all__'):
            echo             globals()['__all__'] = module.__all__
            echo         return module
            echo     except Exception as e:
            echo         raise ImportError(f"Erreur de chargement: {e}")
            echo.
            echo __load_module()
        ) > "!DEST_FILE!"
        
        REM Supprimer le .pyc original
        del "%%F" 2>nul
        
        set /a COUNT+=1
    )
)

echo ✅ %COUNT% modules compilés
echo ✅ %COUNT% modules compilés >> %LOG_FILE%

REM ========================================
REM  ÉTAPE 2: Création de l'archive
REM ========================================
echo.
echo ════════════════════════════════════════════════════════════════
echo 📦 ÉTAPE 2/3 : Création de l'archive ZIP
echo ════════════════════════════════════════════════════════════════

echo 📦 Compression des modules...
echo 📦 Compression des modules... >> %LOG_FILE%

REM Utiliser PowerShell pour créer le zip
powershell -command ^
    "$zipPath = '%OUTPUT_DIR%\%ARCHIVE_NAME%'; ^
     if (Test-Path $zipPath) { Remove-Item $zipPath }; ^
     $moduleDir = '%OUTPUT_DIR%\modules'; ^
     if (Test-Path $moduleDir) { ^
         Add-Type -AssemblyName System.IO.Compression.FileSystem; ^
         [System.IO.Compression.ZipFile]::CreateFromDirectory($moduleDir, $zipPath) ^
     }"

if exist "%OUTPUT_DIR%\%ARCHIVE_NAME%" (
    for %%i in ("%OUTPUT_DIR%\%ARCHIVE_NAME%") do set "ARCHIVE_SIZE=%%~zi"
    set /a ARCHIVE_SIZE_MB=!ARCHIVE_SIZE! / 1048576
    echo ✅ Archive créée: %ARCHIVE_NAME% (!ARCHIVE_SIZE_MB! MB)
    echo ✅ Archive créée: %ARCHIVE_NAME% >> %LOG_FILE%
) else (
    echo ❌ Erreur lors de la création de l'archive
    echo ❌ Erreur lors de la création de l'archive >> %LOG_FILE%
    pause
    exit /b 1
)

REM ========================================
REM  ÉTAPE 3: Métadonnées
REM ========================================
echo.
echo ════════════════════════════════════════════════════════════════
echo 📋 ÉTAPE 3/3 : Création des métadonnées
echo ════════════════════════════════════════════════════════════════

REM Créer metadata.json
(
    echo {
    echo     "version": "%VERSION%",
    echo     "build_date": "%DATE%_%TIME%",
    echo     "python_version": "%PYTHON_VERSION%",
    echo     "modules_count": %COUNT%,
    echo     "compilation_level": "optimized",
    echo     "compiler": "python",
    echo     "archive": "%ARCHIVE_NAME%"
    echo }
) > "%OUTPUT_DIR%\metadata.json"

REM Créer README.md
(
    echo # Modules Python Compiles
    echo.
    echo ## 📦 Description
    echo Ce package contient des modules Python pre-compiles en bytecode (.pyc).
    echo.
    echo ## 🔒 Protection
    echo - Le code source original n'est pas inclus
    echo - Les modules sont compiles avec optimisation (-O)
    echo - Chargement automatique via import
    echo.
    echo ## 📁 Structure
    echo ```
    echo modules/
    echo   └── [structure complete des modules]
    echo metadata.json
    echo README.md
    echo ```
    echo.
    echo ## 🚀 Installation
    echo ```bash
    echo # Decompresser l'archive
    echo # Extraire le ZIP dans le dossier de votre projet
    echo.
    echo # Ajouter le dossier aux chemins Python
    echo set PYTHONPATH=%%PYTHONPATH%%;%CD%\modules
    echo.
    echo # Importer normalement
    echo import votre_module
    echo ```
) > "%OUTPUT_DIR%\README.md"

echo ✅ Métadonnées créées
echo ✅ Métadonnées créées >> %LOG_FILE%

REM ========================================
REM  RÉSUMÉ FINAL
REM ========================================
echo.
echo ============================================================
echo              🎉 OPERATION TERMINEE
echo ============================================================
echo.
echo 📦 Archive: %OUTPUT_DIR%\%ARCHIVE_NAME%
echo 📁 Modules: %MODULES_DIR%\
echo 📋 Log:     %LOG_FILE%
echo.
echo 📝 Pour utiliser les modules:
echo    set PYTHONPATH=%%PYTHONPATH%%;%CD%\%MODULES_DIR%
echo    python -c "import votre_module"
echo.
echo Log: %LOG_FILE%

echo ✅ Script termine avec succes >> %LOG_FILE%
pause