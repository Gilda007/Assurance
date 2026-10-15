@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: ============================================================================
:: SCRIPT INTERACTIF DE CRÉATION DE BASE DE DONNÉES POSTGRESQL POUR LOMETA
:: ============================================================================

:: Défaut des couleurs (si supporté)
set "GREEN="
set "RED="
set "YELLOW="
set "BLUE="
set "BOLD="
set "RESET="

:: Vérifier si les couleurs sont supportées
call :init_colors

:: ============================================================================
:: FONCTIONS
:: ============================================================================

:init_colors
:: Activer les couleurs si supportées
for /f "tokens=2 delims=:" %%a in ('chcp') do set "code_page=%%a"
if "%code_page%"=="65001" (
    set "GREEN=[92m"
    set "RED=[91m"
    set "YELLOW=[93m"
    set "BLUE=[94m"
    set "BOLD=[1m"
    set "RESET=[0m"
) else (
    set "GREEN="
    set "RED="
    set "YELLOW="
    set "BLUE="
    set "BOLD="
    set "RESET="
)
exit /b

:print_header
echo.
echo %BOLD%%BLUE%============================================================%RESET%
echo %BOLD%%BLUE%      CRÉATION DE LA BASE DE DONNÉES LOMETA%RESET%
echo %BOLD%%BLUE%============================================================%RESET%
echo.
exit /b

:print_success
echo %GREEN%[OK]%RESET% %~1
exit /b

:print_error
echo %RED%[ERREUR]%RESET% %~1
exit /b

:print_info
echo %BLUE%[INFO]%RESET% %~1
exit /b

:print_warning
echo %YELLOW%[ATTENTION]%RESET% %~1
exit /b

:print_separator
echo.
echo %BOLD%----------------------------------------------------------------%RESET%
echo.
exit /b

:: ============================================================================
:: SAISIE DES INFORMATIONS
:: ============================================================================

:get_config
call :print_header

echo %BOLD%📋 Configuration de la connexion PostgreSQL%RESET%
echo.
echo Veuillez renseigner les informations suivantes :
echo.

:: Hôte PostgreSQL
set /p PG_HOST="Hôte PostgreSQL [localhost] : "
if "!PG_HOST!"=="" set PG_HOST=localhost

:: Port PostgreSQL
set /p PG_PORT="Port PostgreSQL [5432] : "
if "!PG_PORT!"=="" set PG_PORT=5432

:: Utilisateur administrateur
set /p PG_ADMIN="Utilisateur administrateur PostgreSQL [postgres] : "
if "!PG_ADMIN!"=="" set PG_ADMIN=postgres

:: Mot de passe administrateur (masqué)
echo.
echo ⚠️  Entrez le mot de passe de l'administrateur PostgreSQL
set /p PG_PASSWORD="Mot de passe (masqué) : "

:: Vérifier que le mot de passe n'est pas vide
if "!PG_PASSWORD!"=="" (
    call :print_error "Le mot de passe est requis."
    pause
    exit /b 1
)

echo.
call :print_separator

:: ============================================================================
:: SAISIE DES INFORMATIONS DE LA BASE
:: ============================================================================

echo %BOLD%📋 Configuration de la base de données%RESET%
echo.

:: Nom de la base de données
set /p DB_NAME="Nom de la base de données [lometa_db] : "
if "!DB_NAME!"=="" set DB_NAME=lometa_db

:: Nom de l'utilisateur
set /p DB_USER="Nom d'utilisateur [lometa_user] : "
if "!DB_USER!"=="" set DB_USER=lometa_user

:: Mot de passe de l'utilisateur
set /p DB_PASSWORD="Mot de passe de l'utilisateur (masqué) : "
if "!DB_PASSWORD!"=="" set DB_PASSWORD=Lom3t@2024#Secure!

echo.
call :print_separator

:: ============================================================================
:: CONFIRMATION
:: ============================================================================

echo %BOLD%📋 RÉCAPITULATIF DE LA CONFIGURATION%RESET%
echo.
echo    %BOLD%Connexion PostgreSQL :%RESET%
echo       Hôte     : %PG_HOST%
echo       Port     : %PG_PORT%
echo       Admin    : %PG_ADMIN%
echo.
echo    %BOLD%Base de données :%RESET%
echo       Nom       : %DB_NAME%
echo       Utilisateur : %DB_USER%
echo.
echo %YELLOW%⚠️  ATTENTION : Ce script va créer :%RESET%
echo    - Base de données '%DB_NAME%'
echo    - Utilisateur '%DB_USER%' avec le mot de passe défini
echo    - Droits complets sur la base
echo.
set /p CONFIRM="Continuer ? (O/N) : "
if /i not "!CONFIRM!"=="O" (
    echo Annulé.
    pause
    exit /b 0
)

echo.
call :print_separator
exit /b

:: ============================================================================
:: VÉRIFICATION DE POSTGRESQL
:: ============================================================================

:check_postgres
call :print_info "Vérification de PostgreSQL..."

:: Vérifier si psql est disponible
where psql > nul 2>&1
if errorlevel 1 (
    call :print_error "PostgreSQL n'est pas installé ou psql n'est pas dans le PATH."
    echo.
    echo Veuillez installer PostgreSQL ou ajouter le dossier bin au PATH.
    echo Chemin typique : C:\Program Files\PostgreSQL\15\bin
    echo.
    echo Pour ajouter au PATH temporairement :
    echo    set PATH=C:\Program Files\PostgreSQL\15\bin;%%PATH%%
    pause
    exit /b 1
)

:: Vérifier la version de PostgreSQL
for /f "tokens=*" %%a in ('psql --version 2^>^&1') do set PG_VERSION=%%a
call :print_success "PostgreSQL trouvé : !PG_VERSION!"
echo.
exit /b 0

:: ============================================================================
:: TEST DE CONNEXION
:: ============================================================================

:test_connection
call :print_info "Test de connexion à PostgreSQL..."

:: Créer un fichier temporaire pour la commande
set PGPASSWORD=%PG_PASSWORD%

:: Tester la connexion
echo exit | psql -h %PG_HOST% -p %PG_PORT% -U %PG_ADMIN% -d postgres > nul 2>&1

if errorlevel 1 (
    call :print_error "Échec de la connexion à PostgreSQL."
    echo.
    echo Vérifiez :
    echo    - PostgreSQL est en cours d'exécution
    echo    - Le mot de passe est correct
    echo    - L'utilisateur '%PG_ADMIN%' existe
    echo    - Le port %PG_PORT% est ouvert
    echo.
    pause
    exit /b 1
)

call :print_success "Connexion établie avec succès."
echo.
exit /b 0

:: ============================================================================
:: CRÉATION DE LA BASE DE DONNÉES ET DE L'UTILISATEUR
:: ============================================================================

:create_database
call :print_info "Création de la base de données et de l'utilisateur..."

set PGPASSWORD=%PG_PASSWORD%

:: 1. Créer l'utilisateur
call :print_info "Création de l'utilisateur '%DB_USER%'..."
psql -h %PG_HOST% -p %PG_PORT% -U %PG_ADMIN% -d postgres -c "CREATE USER %DB_USER% WITH PASSWORD '%DB_PASSWORD%';" > nul 2>&1
if errorlevel 1 (
    call :print_warning "L'utilisateur '%DB_USER%' existe peut-être déjà (ou erreur)."
) else (
    call :print_success "Utilisateur '%DB_USER%' créé."
)

:: 2. Créer la base de données
call :print_info "Création de la base de données '%DB_NAME%'..."
psql -h %PG_HOST% -p %PG_PORT% -U %PG_ADMIN% -d postgres -c "CREATE DATABASE %DB_NAME% OWNER %DB_USER%;" > nul 2>&1
if errorlevel 1 (
    call :print_warning "La base de données '%DB_NAME%' existe peut-être déjà (ou erreur)."
) else (
    call :print_success "Base de données '%DB_NAME%' créée."
)

:: 3. Donner les droits sur la base
call :print_info "Attribution des droits..."
psql -h %PG_HOST% -p %PG_PORT% -U %PG_ADMIN% -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE %DB_NAME% TO %DB_USER%;" > nul 2>&1
if errorlevel 1 (
    call :print_error "Erreur lors de l'attribution des droits sur la base."
) else (
    call :print_success "Droits sur la base '%DB_NAME%' attribués."
)

:: 4. Donner les droits sur le schéma public
psql -h %PG_HOST% -p %PG_PORT% -U %PG_ADMIN% -d %DB_NAME% -c "GRANT ALL PRIVILEGES ON SCHEMA public TO %DB_USER%;" > nul 2>&1
if errorlevel 1 (
    call :print_warning "Erreur lors de l'attribution des droits sur le schéma public."
) else (
    call :print_success "Droits sur le schéma public attribués."
)

:: 5. Donner les droits par défaut
psql -h %PG_HOST% -p %PG_PORT% -U %PG_ADMIN% -d %DB_NAME% -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO %DB_USER%;" > nul 2>&1
if errorlevel 1 (
    call :print_warning "Erreur lors de l'attribution des droits par défaut (non bloquante)."
) else (
    call :print_success "Droits par défaut sur les tables attribués."
)

:: 6. Donner les droits sur les séquences
psql -h %PG_HOST% -p %PG_PORT% -U %PG_ADMIN% -d %DB_NAME% -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO %DB_USER%;" > nul 2>&1
if errorlevel 1 (
    call :print_warning "Erreur lors de l'attribution des droits sur les séquences."
) else (
    call :print_success "Droits par défaut sur les séquences attribués."
)

echo.
exit /b 0

:: ============================================================================
:: INSTALLATION DES EXTENSIONS
:: ============================================================================

:create_extensions
call :print_info "Installation des extensions PostgreSQL..."

set PGPASSWORD=%PG_PASSWORD%

:: Extension UUID
psql -h %PG_HOST% -p %PG_PORT% -U %PG_ADMIN% -d %DB_NAME% -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";" > nul 2>&1
if errorlevel 1 (
    call :print_warning "Extension 'uuid-ossp' : échec (non bloquant)."
) else (
    call :print_success "Extension 'uuid-ossp' installée."
)

:: Extension pgcrypto
psql -h %PG_HOST% -p %PG_PORT% -U %PG_ADMIN% -d %DB_NAME% -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;" > nul 2>&1
if errorlevel 1 (
    call :print_warning "Extension 'pgcrypto' : échec (non bloquant)."
) else (
    call :print_success "Extension 'pgcrypto' installée."
)

echo.
exit /b 0

:: ============================================================================
:: AFFICHAGE DES INFORMATIONS FINALES
:: ============================================================================

:show_info
echo.
echo %BOLD%%GREEN%============================================================%RESET%
echo %BOLD%%GREEN%      INSTALLATION TERMINÉE AVEC SUCCÈS !%RESET%
echo %BOLD%%GREEN%============================================================%RESET%
echo.
echo %BOLD%📋 Informations de connexion :%RESET%
echo.
echo    %BOLD%Connexion PostgreSQL :%RESET%
echo       Hôte     : %PG_HOST%
echo       Port     : %PG_PORT%
echo.
echo    %BOLD%Base de données :%RESET%
echo       Nom       : %DB_NAME%
echo       Utilisateur : %DB_USER%
echo       Mot de passe : %DB_PASSWORD%
echo.
echo %BOLD%🔗 Chaîne de connexion (DSN) :%RESET%
echo    postgresql://%DB_USER%:%DB_PASSWORD%@%PG_HOST%:%PG_PORT%/%DB_NAME%
echo.
echo %BOLD%📝 Fichier config.ini :%RESET%
echo.
echo [DATABASE]
echo host = %PG_HOST%
echo port = %PG_PORT%
echo database = %DB_NAME%
echo user = %DB_USER%
echo password = %DB_PASSWORD%
echo.
echo %BOLD%🔄 Pour tester la connexion :%RESET%
echo    psql -h %PG_HOST% -p %PG_PORT% -U %DB_USER% -d %DB_NAME%
echo.
echo %YELLOW%⚠️  Conservez ces informations en lieu sûr !%RESET%
echo.
pause
exit /b 0

:: ============================================================================
:: FONCTION PRINCIPALE
:: ============================================================================

:main
:: Récupérer les informations
call :get_config

:: Vérifier PostgreSQL
call :check_postgres
if errorlevel 1 exit /b 1

:: Tester la connexion
call :test_connection
if errorlevel 1 exit /b 1

:: Créer la base de données
call :create_database

:: Créer les extensions
call :create_extensions

:: Afficher les informations
call :show_info

exit /b 0

:: ============================================================================
:: LANCEMENT
:: ============================================================================

call :main