@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ========================================
REM  Compilation de LOMETA pour Windows
REM  Version FINALE (sans console) et DEBUG (avec console)
REM ========================================

REM Configuration des couleurs (Windows 10+)
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do set "ESC=%%b"
set "RED=%ESC%[91m"
set "GREEN=%ESC%[92m"
set "YELLOW=%ESC%[93m"
set "BLUE=%ESC%[94m"
set "MAGENTA=%ESC%[95m"
set "CYAN=%ESC%[96m"
set "WHITE=%ESC%[97m"
set "NC=%ESC%[0m"

REM Fichier de log
set "LOG_FILE=build_log_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log"
set "LOG_FILE=%LOG_FILE: =0%"

REM Titre de la console
title Compilation LOMETA - Windows

REM En-tête
cls
echo %CYAN%╔════════════════════════════════════════════════════════════════╗%NC%
echo %CYAN%║%WHITE%                    COMPILATION LOMETA WINDOWS                     %CYAN%║%NC%
echo %CYAN%╚════════════════════════════════════════════════════════════════╝%NC%
echo.
echo %WHITE%Date: %date% %time%%NC%
echo.

REM Création du fichier de log
echo ======================================== >> "%LOG_FILE%" 2>&1
echo Compilation de LOMETA pour Windows >> "%LOG_FILE%" 2>&1
echo Date: %date% %time% >> "%LOG_FILE%" 2>&1
echo ======================================== >> "%LOG_FILE%" 2>&1

REM ========================================
REM ÉTAPE 1: Vérification de l'environnement
REM ========================================
echo %YELLOW%┌────────────────────────────────────────────────────────────────┐%NC%
echo %YELLOW%│%NC% %WHITE%VÉRIFICATION DE L'ENVIRONNEMENT%NC%
echo %YELLOW%└────────────────────────────────────────────────────────────────┘%NC%

where python >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set "PYTHON_VER=%%i"
    echo %GREEN%✓%NC% Python trouvé: !PYTHON_VER!
    echo Python trouve: !PYTHON_VER! >> "%LOG_FILE%" 2>&1
) else (
    echo %RED%✗ Python non trouvé !%NC%
    echo ERREUR: Python non trouve >> "%LOG_FILE%" 2>&1
    echo.
    echo %YELLOW%Veuillez installer Python depuis https://python.org%NC%
    pause
    exit /b 1
)

where pip >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%✓%NC% pip trouvé
    echo pip trouve >> "%LOG_FILE%" 2>&1
) else (
    echo %YELLOW%⚠ pip non trouvé, installation...%NC%
    python -m ensurepip --upgrade >> "%LOG_FILE%" 2>&1
)
echo.

REM ========================================
REM ÉTAPE 2: Nettoyage
REM ========================================
echo %YELLOW%┌────────────────────────────────────────────────────────────────┐%NC%
echo %YELLOW%│%NC% %WHITE%ÉTAPE 1/5 : Nettoyage%NC%
echo %YELLOW%└────────────────────────────────────────────────────────────────┘%NC%

call :progress_bar 0 3 "Nettoyage en cours..."
timeout /t 1 /nobreak >nul
call :progress_bar 1 3 "Nettoyage en cours..."
timeout /t 1 /nobreak >nul
call :progress_bar 2 3 "Nettoyage en cours..."
timeout /t 1 /nobreak >nul

if exist build rmdir /s /q build >nul 2>&1
if exist dist rmdir /s /q dist >nul 2>&1
del /q *.spec >nul 2>&1

call :progress_bar 3 3 "Nettoyage terminé"
echo.
echo %GREEN%✓ Nettoyage terminé%NC%
echo Nettoyage termine >> "%LOG_FILE%" 2>&1
echo.

REM ========================================
REM ÉTAPE 3: Installation des dépendances
REM ========================================
echo %YELLOW%┌────────────────────────────────────────────────────────────────┐%NC%
echo %YELLOW%│%NC% %WHITE%ÉTAPE 2/5 : Installation des dépendances%NC%
echo %YELLOW%└────────────────────────────────────────────────────────────────┘%NC%

set "REQUIREMENTS_FILE=requirements.txt"
if not exist "%REQUIREMENTS_FILE%" (
    echo %YELLOW%⚠ %REQUIREMENTS_FILE% non trouvé, création...%NC%
    (
        echo PySide6>=6.6.0
        echo sqlalchemy>=2.0.0
        echo psycopg2-binary>=2.9.0
        echo pandas>=2.0.0
        echo numpy>=1.24.0
        echo Pillow>=10.0.0
        echo requests>=2.31.0
        echo qrcode>=7.4.0
        echo reportlab>=4.0.0
        echo openpyxl>=3.1.0
        echo bcrypt>=4.0.0
        echo Flask>=2.3.0
        echo Flask-CORS>=4.0.0
        echo PyMySQL>=1.1.0
        echo mysqlclient>=2.2.0
        echo pyqtgraph>=0.13.0
        echo python-dateutil>=2.8.0
        echo python-dotenv>=1.0.0
    ) > "%REQUIREMENTS_FILE%"
    echo %REQUIREMENTS_FILE% cree >> "%LOG_FILE%" 2>&1
)

REM Compter le nombre de packages
set "TOTAL=0"
for /f "usebackq tokens=*" %%a in (`type "%REQUIREMENTS_FILE%" ^| findstr /v "^#" ^| findstr /v "^$"`) do set /a TOTAL+=1

set "CURRENT=0"
set "FAILED_PACKAGES="

call :timer_start

for /f "usebackq tokens=*" %%p in (`type "%REQUIREMENTS_FILE%" ^| findstr /v "^#" ^| findstr /v "^$"`) do (
    set /a CURRENT+=1
    set /a PERCENT=!CURRENT! * 100 / %TOTAL%
    set /a BARS=!PERCENT! / 2
    
    set "BAR="
    for /l %%i in (1,1,!BARS!) do set "BAR=!BAR!█"
    for /l %%i in (!BARS!,1,49) do set "BAR=!BAR!░"
    
    <nul set /p ="%CYAN%[%NC%!BAR!%CYAN%]%NC% %WHITE%!PERCENT!%%%NC% - %BLUE%%%~p%NC%"
    
    pip install %%~p >> "%LOG_FILE%" 2>&1
    if !errorlevel! neq 0 (
        set "FAILED_PACKAGES=!FAILED_PACKAGES! %%~p"
        echo ECHEC installation: %%~p >> "%LOG_FILE%" 2>&1
    ) else (
        echo OK installation: %%~p >> "%LOG_FILE%" 2>&1
    )
    echo.
)

call :timer_stop

if not "!FAILED_PACKAGES!"=="" (
    echo.
    echo %YELLOW%⚠ Certains packages n'ont pas pu être installés:%NC%
    echo %RED% !FAILED_PACKAGES!%NC%
    echo %YELLOW%Continuer malgré tout? (O/N)%NC%
    choice /c ON /n
    if errorlevel 2 (
        exit /b 1
    )
) else (
    echo %GREEN%✓ Installation terminée%NC%
)
echo.

REM ========================================
REM ÉTAPE 4: Installation de PyInstaller
REM ========================================
echo %YELLOW%┌────────────────────────────────────────────────────────────────┐%NC%
echo %YELLOW%│%NC% %WHITE%ÉTAPE 3/5 : Installation de PyInstaller%NC%
echo %YELLOW%└────────────────────────────────────────────────────────────────┘%NC%

where pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo %YELLOW%⚠ PyInstaller non trouvé, installation...%NC%
    pip install pyinstaller >> "%LOG_FILE%" 2>&1
)

where pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%✗ PyInstaller n'a pas pu être installé !%NC%
    echo ERREUR: PyInstaller non installe >> "%LOG_FILE%" 2>&1
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('pyinstaller --version') do set "PYINST_VER=%%i"
echo %GREEN%✓ PyInstaller disponible: %PYINST_VER%%NC%
echo PyInstaller version: %PYINST_VER% >> "%LOG_FILE%" 2>&1
echo.

REM ========================================
REM ÉTAPE 5: Compilation DEBUG (avec console)
REM ========================================
echo %YELLOW%┌────────────────────────────────────────────────────────────────┐%NC%
echo %YELLOW%│%NC% %WHITE%ÉTAPE 4/5 : Compilation DEBUG (avec console)%NC%
echo %YELLOW%└────────────────────────────────────────────────────────────────┘%NC%

call :timer_start
call :compile_pyinstaller "LOMETA_DEBUG" "--console"
if %errorlevel% equ 0 (
    call :timer_stop
    echo %GREEN%✓ Compilation DEBUG réussie%NC%
    echo Compilation DEBUG reussie >> "%LOG_FILE%" 2>&1
) else (
    call :timer_stop
    echo %RED%✗ Erreur lors de la compilation DEBUG%NC%
    echo ERREUR compilation DEBUG >> "%LOG_FILE%" 2>&1
    exit /b 1
)
echo.

REM ========================================
REM ÉTAPE 6: Compilation FINALE (sans console)
REM ========================================
echo %YELLOW%┌────────────────────────────────────────────────────────────────┐%NC%
echo %YELLOW%│%NC% %WHITE%ÉTAPE 5/5 : Compilation FINALE (sans console)%NC%
echo %YELLOW%└────────────────────────────────────────────────────────────────┘%NC%

call :timer_start
call :compile_pyinstaller "LOMETA" "--windowed"
if %errorlevel% equ 0 (
    call :timer_stop
    echo %GREEN%✓ Compilation FINALE réussie%NC%
    echo Compilation FINALE reussie >> "%LOG_FILE%" 2>&1
) else (
    call :timer_stop
    echo %RED%✗ Erreur lors de la compilation FINALE%NC%
    echo ERREUR compilation FINALE >> "%LOG_FILE%" 2>&1
    exit /b 1
)
echo.

REM ========================================
REM FINALISATION
REM ========================================
echo %YELLOW%┌────────────────────────────────────────────────────────────────┐%NC%
echo %YELLOW%│%NC% %WHITE%FINALISATION%NC%
echo %YELLOW%└────────────────────────────────────────────────────────────────┘%NC%

REM Création des dossiers addons
if not exist "dist\LOMETA\addons" mkdir "dist\LOMETA\addons" 2>nul
if not exist "dist\LOMETA_DEBUG\addons" mkdir "dist\LOMETA_DEBUG\addons" 2>nul
echo # Dossier des modules > "dist\LOMETA\addons\README.txt"
echo # Dossier des modules > "dist\LOMETA_DEBUG\addons\README.txt"
echo %GREEN%✓ Dossiers addons créés%NC%

REM Copie du fichier de log
copy "%LOG_FILE%" "dist\LOMETA\%LOG_FILE%" >nul 2>&1
copy "%LOG_FILE%" "dist\LOMETA_DEBUG\%LOG_FILE%" >nul 2>&1
echo %GREEN%✓ Log copié dans les dossiers de sortie%NC%

REM Taille des dossiers
for /f "tokens=*" %%i in ('"powershell -command "Get-ChildItem -Path dist\LOMETA -Recurse | Measure-Object -Property Length -Sum | ForEach-Object { '{0:N2} MB' -f ($_.Sum / 1MB) }""') do set "SIZE_FINAL=%%i"
for /f "tokens=*" %%i in ('"powershell -command "Get-ChildItem -Path dist\LOMETA_DEBUG -Recurse | Measure-Object -Property Length -Sum | ForEach-Object { '{0:N2} MB' -f ($_.Sum / 1MB) }""') do set "SIZE_DEBUG=%%i"

echo.
echo %GREEN%╔════════════════════════════════════════════════════════════════╗%NC%
echo %GREEN%║%WHITE%                    COMPILATION TERMINÉE                     %GREEN%║%NC%
echo %GREEN%╚════════════════════════════════════════════════════════════════╝%NC%
echo.
echo %WHITE%📦 Exécutable FINAL :%NC% %CYAN%dist\LOMETA\LOMETA.exe%NC% %WHITE%(!SIZE_FINAL!)%NC%
echo %WHITE%🐛 Exécutable DEBUG :%NC% %CYAN%dist\LOMETA_DEBUG\LOMETA_DEBUG.exe%NC% %WHITE%(!SIZE_DEBUG!)%NC%
echo %WHITE%📋 Fichier log :%NC%      %CYAN%!LOG_FILE!%NC%
echo.
echo %YELLOW%Pour diagnostiquer les erreurs :%NC%
echo   1. %WHITE%dist\LOMETA_DEBUG\LOMETA_DEBUG.exe%NC% - Pour voir les erreurs en console
echo   2. %WHITE%type !LOG_FILE!%NC% - Pour consulter le log complet
echo.

echo ======================================== >> "%LOG_FILE%" 2>&1
echo Compilation terminee avec succes >> "%LOG_FILE%" 2>&1
echo ======================================== >> "%LOG_FILE%" 2>&1

pause
exit /b 0

REM ========================================
REM FONCTIONS
REM ========================================

:progress_bar
set "current=%~1"
set "total=%~2"
set "message=%~3"
set /a percent=current * 100 / total
set /a filled=percent * 60 / 100
set "bar="
for /l %%i in (1,1,%filled%) do set "bar=!bar!█"
for /l %%i in (%filled%,1,59) do set "bar=!bar!░"
<nul set /p ="%CYAN%[%NC%!bar!%CYAN%]%NC% %WHITE%!percent!%%%NC% - !message!%NC%"
if %current% equ %total% echo.
exit /b

:compile_pyinstaller
set "BUILD_NAME=%~1"
set "CONSOLE_OPT=%~2"

echo %CYAN%════════════════════════════════════════════════════════════════%NC%
echo %WHITE%📦 Compilation de %BUILD_NAME%%NC%
echo %CYAN%════════════════════════════════════════════════════════════════%NC%

REM Supprimer l'ancien dossier si existant
if exist "dist\%BUILD_NAME%" rmdir /s /q "dist\%BUILD_NAME%" 2>nul

REM Lancer PyInstaller et afficher la sortie
set "TEMP_LOG=%TEMP%\pyinstaller_%BUILD_NAME%.log"

pyinstaller --noconfirm --onedir %CONSOLE_OPT% ^
    --name "%BUILD_NAME%" ^
    --icon "icon.ico" ^
    --add-data "addons;addons" ^
    --add-data "server/config.py;." ^
    --add-data "version_manager.py;." ^
    --add-data "update_manager.py;." ^
    --add-data "update_dialog.py;." ^
    --collect-all PySide6 ^
    --collect-all PySide6.QtCharts ^
    --collect-all sqlalchemy ^
    --collect-all psycopg2 ^
    --collect-all pandas ^
    --collect-all numpy ^
    --collect-all PIL ^
    --collect-all requests ^
    --collect-all qrcode ^
    --collect-all reportlab ^
    --collect-all openpyxl ^
    --collect-all bcrypt ^
    --collect-all flask ^
    --collect-all flask_cors ^
    --collect-all PyMySQL ^
    --collect-all mysqlclient ^
    --collect-all pyqtgraph ^
    --collect-all python_dateutil ^
    --collect-all dotenv ^
    --collect-all urllib3 ^
    --collect-all certifi ^
    --collect-all idna ^
    --collect-all charset_normalizer ^
    --collect-all greenlet ^
    --collect-all packaging ^
    --collect-all typing_extensions ^
    --collect-all six ^
    --collect-all et_xmlfile ^
    --collect-all xlrd ^
    --collect-all altgraph ^
    --collect-all colorama ^
    --collect-all setuptools ^
    --collect-all shiboken6 ^
    --collect-all pytz ^
    --collect-all tzdata ^
    --collect-all markupsafe ^
    --collect-all jinja2 ^
    --collect-all itsdangerous ^
    --collect-all click ^
    --collect-all werkzeug ^
    --collect-all cffi ^
    --collect-all pycparser ^
    --collect-all cryptography ^
    --collect-all opencv_python ^
    --collect-all cv2 ^
    --collect-all opencv-python ^
    --hidden-import "email" ^
    --hidden-import "email.mime" ^
    --hidden-import "email.mime.multipart" ^
    --hidden-import "email.mime.text" ^
    --hidden-import "email.mime.base" ^
    --hidden-import "email.mime.image" ^
    --hidden-import "email.mime.application" ^
    --hidden-import "email.encoders" ^
    --hidden-import "email.utils" ^
    --hidden-import "smtplib" ^
    --hidden-import "cv2" ^
    --hidden-import "opencv-python" ^
    --hidden-import "numpy" ^
    --hidden-import "numpy.core" ^
    --hidden-import "numpy.core._multiarray_umath" ^
    --hidden-import "numpy.random" ^
    --hidden-import "numpy.linalg" ^
    --hidden-import "PySide6.QtCore" ^
    --hidden-import "PySide6.QtWidgets" ^
    --hidden-import "PySide6.QtGui" ^
    --hidden-import "PySide6.QtNetwork" ^
    --hidden-import "PySide6.QtSvg" ^
    --hidden-import "PySide6.QtPrintSupport" ^
    --hidden-import "PySide6.QtOpenGL" ^
    --hidden-import "PySide6.QtOpenGLWidgets" ^
    --hidden-import "PySide6.QtMultimedia" ^
    --hidden-import "PySide6.QtMultimediaWidgets" ^
    --hidden-import "PySide6.QtSql" ^
    --hidden-import "PySide6.QtXml" ^
    --hidden-import "PySide6.QtCharts" ^
    --hidden-import "PySide6.QtCharts.QChart" ^
    --hidden-import "PySide6.QtCharts.QChartView" ^
    --hidden-import "PySide6.QtCharts.QPieSeries" ^
    --hidden-import "PySide6.QtCharts.QBarSeries" ^
    --hidden-import "PySide6.QtCharts.QBarSet" ^
    --hidden-import "PySide6.QtCharts.QLineSeries" ^
    --hidden-import "PySide6.QtCharts.QCategoryAxis" ^
    --hidden-import "PySide6.QtCharts.QValueAxis" ^
    --hidden-import "qrcode" ^
    --hidden-import "qrcode.image.pil" ^
    --hidden-import "qrcode.image.svg" ^
    --hidden-import "qrcode.image.base" ^
    --hidden-import "qrcode.util" ^
    --hidden-import "PIL" ^
    --hidden-import "PIL.Image" ^
    --hidden-import "PIL.ImageDraw" ^
    --hidden-import "PIL.ImageFont" ^
    --hidden-import "PIL.ImageFilter" ^
    --hidden-import "PIL.ImageEnhance" ^
    --hidden-import "PIL.ImageColor" ^
    --hidden-import "PIL.ImageFile" ^
    --hidden-import "PIL.ImagePalette" ^
    --hidden-import "PIL.ImageMode" ^
    --hidden-import "PIL.ImageSequence" ^
    --hidden-import "PIL.TiffImagePlugin" ^
    --hidden-import "PIL.JpegImagePlugin" ^
    --hidden-import "PIL.PngImagePlugin" ^
    --hidden-import "PIL.GifImagePlugin" ^
    --hidden-import "pandas" ^
    --hidden-import "pandas.core" ^
    --hidden-import "pandas.io" ^
    --hidden-import "pandas.io.sql" ^
    --hidden-import "pandas.io.parsers" ^
    --hidden-import "pandas.io.excel" ^
    --hidden-import "pandas.io.json" ^
    --hidden-import "pandas.io.html" ^
    --hidden-import "sqlalchemy" ^
    --hidden-import "sqlalchemy.dialects.postgresql" ^
    --hidden-import "sqlalchemy.dialects.mysql" ^
    --hidden-import "sqlalchemy.dialects.sqlite" ^
    --hidden-import "sqlalchemy.ext.declarative" ^
    --hidden-import "sqlalchemy.orm" ^
    --hidden-import "psycopg2" ^
    --hidden-import "psycopg2._psycopg" ^
    --hidden-import "psycopg2.extensions" ^
    --hidden-import "psycopg2.extras" ^
    --hidden-import "psycopg2.pool" ^
    --hidden-import "psycopg2.sql" ^
    --hidden-import "psycopg2.errorcodes" ^
    --hidden-import "requests" ^
    --hidden-import "requests.packages" ^
    --hidden-import "requests.packages.urllib3" ^
    --hidden-import "urllib3" ^
    --hidden-import "urllib3.packages" ^
    --hidden-import "certifi" ^
    --hidden-import "idna" ^
    --hidden-import "charset_normalizer" ^
    --hidden-import "flask" ^
    --hidden-import "flask.views" ^
    --hidden-import "flask.json" ^
    --hidden-import "flask_cors" ^
    --hidden-import "reportlab" ^
    --hidden-import "reportlab.lib" ^
    --hidden-import "reportlab.lib.pagesizes" ^
    --hidden-import "reportlab.lib.units" ^
    --hidden-import "reportlab.lib.colors" ^
    --hidden-import "reportlab.lib.utils" ^
    --hidden-import "reportlab.lib.fonts" ^
    --hidden-import "reportlab.lib.sequencer" ^
    --hidden-import "reportlab.pdfbase" ^
    --hidden-import "reportlab.pdfbase.pdfmetrics" ^
    --hidden-import "reportlab.pdfbase.ttfonts" ^
    --hidden-import "reportlab.pdfgen" ^
    --hidden-import "reportlab.pdfgen.canvas" ^
    --hidden-import "reportlab.pdfgen.textobject" ^
    --hidden-import "reportlab.platypus" ^
    --hidden-import "reportlab.platypus.doctemplate" ^
    --hidden-import "reportlab.platypus.flowables" ^
    --hidden-import "reportlab.platypus.paragraph" ^
    --hidden-import "reportlab.platypus.tables" ^
    --hidden-import "reportlab.platypus.frames" ^
    --hidden-import "reportlab.graphics" ^
    --hidden-import "reportlab.graphics.shapes" ^
    --hidden-import "reportlab.graphics.widgets" ^
    --hidden-import "reportlab.graphics.renderPDF" ^
    --hidden-import "reportlab.graphics.charts" ^
    --hidden-import "reportlab.graphics.charts.barcharts" ^
    --hidden-import "reportlab.graphics.charts.linecharts" ^
    --hidden-import "reportlab.graphics.charts.piecharts" ^
    --hidden-import "openpyxl" ^
    --hidden-import "openpyxl.cell" ^
    --hidden-import "openpyxl.reader" ^
    --hidden-import "openpyxl.workbook" ^
    --hidden-import "openpyxl.writer" ^
    --hidden-import "openpyxl.styles" ^
    --hidden-import "openpyxl.formatting" ^
    --hidden-import "openpyxl.chart" ^
    --hidden-import "openpyxl.utils" ^
    --hidden-import "bcrypt" ^
    --hidden-import "PyMySQL" ^
    --hidden-import "mysqlclient" ^
    --hidden-import "pyqtgraph" ^
    --hidden-import "pyqtgraph.Qt" ^
    --hidden-import "pyqtgraph.graphicsItems" ^
    --hidden-import "pyqtgraph.widgets" ^
    --hidden-import "dateutil" ^
    --hidden-import "dateutil.parser" ^
    --hidden-import "dateutil.tz" ^
    --hidden-import "dateutil.relativedelta" ^
    --hidden-import "dotenv" ^
    --hidden-import "greenlet" ^
    --hidden-import "packaging" ^
    --hidden-import "packaging.version" ^
    --hidden-import "packaging.specifiers" ^
    --hidden-import "packaging.requirements" ^
    --hidden-import "typing_extensions" ^
    --hidden-import "six" ^
    --hidden-import "et_xmlfile" ^
    --hidden-import "xlrd" ^
    --hidden-import "altgraph" ^
    --hidden-import "colorama" ^
    --hidden-import "setuptools" ^
    --hidden-import "setuptools._vendor" ^
    --hidden-import "shiboken6" ^
    --hidden-import "shiboken6.shiboken6" ^
    --hidden-import "cffi" ^
    --hidden-import "cryptography" ^
    --hidden-import "cryptography.hazmat" ^
    --hidden-import "cryptography.hazmat.backends" ^
    --hidden-import "cryptography.hazmat.primitives" ^
    --hidden-import "jinja2" ^
    --hidden-import "jinja2.ext" ^
    --hidden-import "markupsafe" ^
    --hidden-import "itsdangerous" ^
    --hidden-import "click" ^
    --hidden-import "werkzeug" ^
    --hidden-import "werkzeug.utils" ^
    --hidden-import "werkzeug.serving" ^
    --hidden-import "werkzeug.wsgi" ^
    --hidden-import "werkzeug.middleware" ^
    --hidden-import "pytz" ^
    --hidden-import "tzdata" ^
    --runtime-tmpdir "." ^
    main.py > "%TEMP_LOG%" 2>&1

REM Afficher la sortie en temps réel
set "LINE_NUM=0"
for /f "usebackq delims=" %%l in ("%TEMP_LOG%") do (
    set "line=%%l"
    set /a LINE_NUM+=1
    echo %MAGENTA%[%time:~0,8%]%NC% %%l
    echo %%l >> "%LOG_FILE%" 2>&1
)

REM Vérifier le résultat
findstr /i "completed successfully" "%TEMP_LOG%" >nul
if %errorlevel% equ 0 (
    echo.
    echo %GREEN%✓ Compilation de %BUILD_NAME% terminée avec succès%NC%
    exit /b 0
) else (
    echo.
    echo %RED%✗ Erreur lors de la compilation de %BUILD_NAME%%NC%
    exit /b 1
)

:draw_bar
set "percent=%~1"
set /a filled=percent * 60 / 100
set "bar="
for /l %%i in (1,1,%filled%) do set "bar=!bar!█"
for /l %%i in (%filled%,1,59) do set "bar=!bar!░"
<nul set /p ="%CYAN%[%NC%!bar!%CYAN%]%NC% %WHITE%!percent!%%%NC%"
exit /b

:timer_start
set "START_TIME=%time%"
set "START_SECONDS=0"
for /f "tokens=1-3 delims=:," %%a in ("%START_TIME%") do (
    set /a "START_SECONDS=((%%a*3600)+(%%b*60)+%%c)"
)
exit /b

:timer_stop
set "END_TIME=%time%"
set "END_SECONDS=0"
for /f "tokens=1-3 delims=:," %%a in ("%END_TIME%") do (
    set /a "END_SECONDS=((%%a*3600)+(%%b*60)+%%c)"
)
set /a "DURATION=END_SECONDS-START_SECONDS"
if !DURATION! lss 0 set /a "DURATION+=86400"
set /a "MINUTES=DURATION/60"
set /a "SECONDS=DURATION%%60"
echo %CYAN%⏱️  Durée: !MINUTES!m !SECONDS!s%NC%
exit /b