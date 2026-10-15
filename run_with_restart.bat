@echo off
title LOMETA - Lanceur automatique
color 0A

echo ========================================
echo    LOMETA - Lanceur avec redémarrage
echo ========================================
echo.

set LOG_DIR=%USERPROFILE%\Documents\LOMETA\logs
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

set LOG_FILE=%LOG_DIR%\launcher_%date:~6,4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
set LOG_FILE=%LOG_FILE: =0%

:loop
echo [%date% %time%] Démarrage de l'application... >> "%LOG_FILE%"
echo Démarrage de LOMETA...

REM Lancer l'application
python main.py

REM Vérifier le code de sortie
if %errorlevel% equ 0 (
    echo [%date% %time%] Application fermée normalement >> "%LOG_FILE%"
    echo Application fermée normalement.
    exit /b 0
) else (
    echo [%date% %time%] Application crashée (code: %errorlevel%) >> "%LOG_FILE%"
    echo ATTENTION: L'application a crashé !
    echo Redémarrage dans 5 secondes...
    timeout /t 5 /nobreak
    goto loop
)