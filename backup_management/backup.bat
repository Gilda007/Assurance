@echo off
REM backup.bat - Script de backup pour Windows

setlocal enabledelayedexpansion

REM Configuration
set DB_HOST=212.47.73.151
set DB_PORT=5432
set DB_NAME=ams_db
set DB_USER=ams_admin
set DB_PASSWORD=votre_mot_de_passe
set BACKUP_DIR=C:\backups\lometa
set LOG_FILE=C:\logs\lometa_backup.log
set PG_PATH=C:\Program Files\PostgreSQL\16\bin

REM Ajouter PostgreSQL au PATH
set PATH=%PG_PATH%;%PATH%

REM Créer les dossiers
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
if not exist "C:\logs" mkdir "C:\logs"

REM Horodatage
set TIMESTAMP=%date:~6,4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

set BACKUP_FILE=%BACKUP_DIR%\backup_%DB_NAME%_%TIMESTAMP%.sql
set COMPRESSED_FILE=%BACKUP_FILE%.gz

echo %date% %time% - Démarrage du backup >> %LOG_FILE%

REM Backup
set PGPASSWORD=%DB_PASSWORD%
pg_dump -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% > "%BACKUP_FILE%"

if %errorlevel% equ 0 (
    echo %date% %time% - Backup réussi >> %LOG_FILE%
    
    REM Compression
    powershell -Command "Compress-Archive -Path '%BACKUP_FILE%' -DestinationPath '%COMPRESSED_FILE%'"
    del "%BACKUP_FILE%"
    
    echo %date% %time% - Compression terminée >> %LOG_FILE%
    
    REM Supprimer les backups de plus de 30 jours
    forfiles /p "%BACKUP_DIR%" /m "*.gz" /d -30 /c "cmd /c del @file" 2>nul
    
    echo %date% %time% - Backup terminé avec succès >> %LOG_FILE%
) else (
    echo %date% %time% - ERREUR lors du backup >> %LOG_FILE%
)

set PGPASSWORD=