# build_windows.bat
@echo off
echo ========================================
echo  Compilation de LOMETA pour Windows
echo ========================================

REM Nettoyer les anciens builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Compiler avec --onedir (recommandé)
pyinstaller --onedir ^
    --name "LOMETA" ^
    --windowed ^
    --add-data "addons;addons" ^
    --hidden-import=config ^
    --hidden-import=version_manager ^
    --hidden-import=update_manager ^
    --runtime-tmpdir "." ^
    main.py

echo.
echo ========================================
echo  Compilation terminee !
echo  Executable : dist\LOMETA\LOMETA.exe
echo  Les modules seront dans : dist\LOMETA\addons\
echo ========================================

REM Créer le dossier addons vide dans dist
if not exist dist\LOMETA\addons mkdir dist\LOMETA\addons

REM Copier un README dans le dossier addons
echo # Dossier des modules > dist\LOMETA\addons\README.txt
echo Placez vos modules ici. >> dist\LOMETA\addons\README.txt

pause