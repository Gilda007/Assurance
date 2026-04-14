@echo off
setlocal enabledelayedexpansion

TITLE AMS_Project - Configuration Environnement Dev
echo ======================================================
echo    INSTALLATION DE L'ENVIRONNEMENT DEV (AMS_Project)
echo ======================================================

:: 1. Vérification de Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python n'est pas installe ou n'est pas dans le PATH.
    pause
    exit /b
)

:: 2. Clonage du projet (si pas deja fait)
if not exist "Assurance" (
    echo [INFO] Clonage du depot GitHub...
    git clone https://github.com/Gilda007/Assurance.git
    cd Assurance
) else (
    echo [INFO] Le dossier Assurance existe deja.
    cd Assurance
)

:: 3. Creation de l'environnement virtuel
if not exist "venv" (
    echo [INFO] Creation de l'environnement virtuel (venv)...
    python -m venv venv
)

:: 4. Activation et Installation des dependances
echo [INFO] Activation de venv et installation des packages...
call venv\Scripts\activate.bat

:: Mise a jour de pip
python -m pip install --upgrade pip

:: Installation des dependances essentielles
echo [INFO] Installation de PySide6, SQLAlchemy et psycopg2...
pip install PySide6 sqlalchemy psycopg2-binary qrcode

:: Verification du fichier requirements.txt
if exist "requirements.txt" (
    echo [INFO] Installation des dependances depuis requirements.txt...
    pip install -r requirements.txt
)

:: 5. Creation de la structure des dossiers manquants
echo [INFO] Verification de la structure des dossiers...
if not exist "addons" mkdir addons
if not exist "core" mkdir core
if not exist "logs" mkdir logs

:: 6. Fin de l'installation
echo ======================================================
echo [SUCCESS] Environnement configure avec succes !
echo.
echo Pour lancer l'application :
echo 1. Tapez 'call venv\Scripts\activate'
echo 2. Tapez 'python main.py'
echo ======================================================
pause