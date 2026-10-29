# ============================================================
#  LOMETA — Compilation sécurisée complète (Windows)
#  Cœur (--standalone) + addons (--module)
# ============================================================
#  Usage :
#    .\build_windows.ps1                # build complet
#    .\build_windows.ps1 -Clean         # nettoyage + build
#    .\build_windows.ps1 -NoZip         # sans ZIP
#    .\build_windows.ps1 -Verbose       # logs détaillés
# ============================================================

param(
    [switch]$Clean,
    [switch]$NoZip,
    [switch]$VerboseOutput
)

$ErrorActionPreference = "Stop"

# Sourcer la bibliothèque
. (Join-Path $PSScriptRoot "lib_build.ps1")

$LogFile = Join-Path $ProjectRoot ("build_secure_{0}.log" -f (Get-Date -Format "yyyyMMdd_HHmmss"))
function Write-Log { param([string]$Text) $Text | Tee-Object -FilePath $LogFile -Append | Out-Null }

# ─── 0. Prérequis ───
Test-Prerequisites
Write-Host "📋 Log : $LogFile" -ForegroundColor Blue

# ─── 1. Nettoyage ───
Write-Section "1 · Nettoyage"

if ($Clean) {
    Remove-Item -Recurse -Force (Join-Path $ProjectRoot "build")        -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force (Join-Path $ProjectRoot "dist")         -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force $DistRoot                                -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force $AddonsBuild                             -ErrorAction SilentlyContinue
}

$srcClean = Join-Path $ProjectRoot "src_clean"
Remove-Item -Recurse -Force $srcClean -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $srcClean -Force | Out-Null

Write-Ok "Espace de travail prêt"

# ─── 2. Préparation du cœur ───
Write-Section "2 · Préparation de la source cœur"

foreach ($pkg in @("core", "server", "icons")) {
    $src = Join-Path $ProjectRoot $pkg
    if (-not (Test-Path $src)) { Write-Warn "$pkg/ absent, ignoré"; continue }
    $dst = Join-Path $srcClean $pkg
    $excludeDirs  = @(".history", "__pycache__", ".venv", "node_modules", ".pytest_cache")
    $excludeFiles = @("*.pyc", "*.pyo", "test_*.py")
    $robocopyArgs = @($src, $dst, "/E", "/NFL", "/NDL", "/NJH", "/NJS", "/nc", "/ns", "/np", "/XD") +
                    $excludeDirs + @("/XF") + $excludeFiles
    & robocopy @robocopyArgs | Out-Null
}

foreach ($f in @("version_manager.py", "update_manager.py", "update_dialog.py",
                 "update_client.py", "update_widget.py", "module_detector.py", "main.py")) {
    $src = Join-Path $ProjectRoot $f
    if (Test-Path $src) { Copy-Item $src -Destination $srcClean -Force }
}

Write-Ok "Source cœur prête"

# ─── 3. Compilation du cœur ───
Write-Section "3 · Compilation Nuitka du cœur (20–40 min la 1ère fois)"

$dataArgs = @()
if (Test-Path (Join-Path $ProjectRoot "icons")) {
    $dataArgs += "--include-data-dir=$(Join-Path $ProjectRoot 'icons')=icons"
}
if (Test-Path (Join-Path $ProjectRoot "module_registry.json")) {
    $dataArgs += "--include-data-file=$(Join-Path $ProjectRoot 'module_registry.json')=."
}

$coreArgs = @(
    "-m", "nuitka",
    "--standalone",
    "--assume-yes-for-downloads",
    "--enable-plugin=pyside6",
    "--include-package=core",
    "--include-package=server",
    "--include-package=icons",
    "--include-package-data=PySide6",
    "--include-package-data=qtawesome",
    "--include-package-data=sqlalchemy",
    "--include-package-data=pandas",
    "--include-package-data=numpy",
    "--include-package-data=PIL",
    "--include-package-data=requests",
    "--include-package-data=qrcode",
    "--include-package-data=reportlab",
    "--include-package-data=openpyxl",
    "--include-package-data=bcrypt",
    "--include-package-data=flask",
    "--include-package-data=flask_cors",
    "--include-package-data=pymysql",
    "--include-package-data=pyqtgraph",
    "--include-package-data=dateutil",
    "--include-package-data=dotenv",
    "--include-module=cv2",
    "--include-module=numpy",
    "--include-module=PySide6.QtCharts",
    "--include-module=PySide6.QtMultimedia",
    "--include-module=PySide6.QtMultimediaWidgets",
    "--include-module=PySide6.QtPrintSupport",
    "--include-module=PySide6.QtSvg",
    "--include-module=PySide6.QtSql",
    "--include-module=PySide6.QtNetwork",
    "--include-module=PySide6.QtOpenGL",
    "--include-module=PySide6.QtOpenGLWidgets",
    "--nofollow-import-to=pytest",
    "--nofollow-import-to=tkinter",
    "--nofollow-import-to=PyQt5",
    "--nofollow-import-to=PyQt6",
    "--nofollow-import-to=matplotlib",
    "--nofollow-import-to=IPython",
    "--nofollow-import-to=jupyter",
    "--nofollow-import-to=notebook",
    "--output-dir=$DistRoot",
    "--output-filename=LOMETA",
    "--report=$LogFile.nuitka.xml"
) + $dataArgs + @((Join-Path $srcClean "main.py"))

& $env:PYTHON @coreArgs 2>&1 | Tee-Object -FilePath $LogFile -Append
if ($LASTEXITCODE -ne 0) { Stop-WithError "Compilation du cœur échouée" }

# Localiser le .dist
$distDir = Get-ChildItem -Path $DistRoot -Directory -Filter "*.dist" | Select-Object -First 1
if (-not $distDir) { Stop-WithError "Dossier .dist introuvable dans $DistRoot" }
$Global:DistDir = $distDir.FullName
$binary = Join-Path $DistDir "LOMETA.exe"
if (-not (Test-Path $binary)) {
    $binary = Join-Path $DistDir "LOMETA"
}
if (-not (Test-Path $binary)) { Stop-WithError "Binaire LOMETA introuvable dans $DistDir" }

Write-Ok "Cœur compilé : $binary"

# ─── 4. Compilation des addons ───
Write-Section "4 · Compilation des addons en modules natifs"

New-Item -ItemType Directory -Path $AddonsBuild -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $DistDir "addons") -Force | Out-Null

$addonsToBuild = Get-ChildItem -Path $AddonsSrc -Directory | Select-Object -ExpandProperty Name
if (-not $addonsToBuild) { Write-Warn "Aucun addon à compiler" }

Write-Host "🎯 Addons à compiler : $($addonsToBuild -join ', ')" -ForegroundColor White

$failed = @()
$success = @()

foreach ($name in $addonsToBuild) {
    $prepared = Initialize-AddonSource -Name $name
    if ($prepared -and (Invoke-CompileAddon -Name $name) -and (Install-Addon -Name $name)) {
        $success += $name
    } else {
        $failed += $name
    }
}

# Métadonnées racine
$registry = Join-Path $ProjectRoot "module_registry.json"
if (Test-Path $registry) { Copy-Item $registry -Destination $DistDir -Force }
$envFile = Join-Path $ProjectRoot ".env"
if (Test-Path $envFile) { Copy-Item $envFile -Destination $DistDir -Force -ErrorAction SilentlyContinue }

# Dossier data/
New-Item -ItemType Directory -Path (Join-Path $DistDir "data/evaluations") -Force | Out-Null

if ($success) { Write-Ok "Addons compilés : $($success.Count) → $($success -join ', ')" }
if ($failed) {
    foreach ($f in $failed) { Write-Fail $f }
    Stop-WithError "Certains addons n'ont pas été compilés"
}

# ─── 5. Vérifications ───
Write-Section "5 · Vérification de la protection"

# Aucun .py du cœur
$leakedCore = Get-ChildItem -Path $DistDir -Filter "*.py" -Recurse |
    Where-Object { $_.FullName -match "\\(core|server|icons)\\" }
if ($leakedCore) { Stop-WithError "$($leakedCore.Count) fichiers .py du cœur exposés" }
Write-Ok "Aucun .py du cœur dans le dist"

# Aucun .py dans addons
$leakedAddons = Get-ChildItem -Path (Join-Path $DistDir "addons") -Filter "*.py" -Recurse -ErrorAction SilentlyContinue
if ($leakedAddons) { Stop-WithError "$($leakedAddons.Count) fichiers .py exposés dans addons/" }
Write-Ok "Aucun .py dans addons/"

# Chaque addon a son .so/.pyd
foreach ($d in Get-ChildItem -Path (Join-Path $DistDir "addons") -Directory) {
    $soFiles = Get-ChildItem -Path $d.FullName -Filter "__init*" -File | Where-Object { $_.Extension -in @(".pyd", ".so") }
    if (-not $soFiles) { Stop-WithError "$($d.Name)/__init*.pyd manquant" }
    Test-SoFile -SoPath $soFiles[0].FullName -Name $d.Name
}
Write-Ok "Tous les addons ont un .pyd/.so valide"

# Code métier lisible
$strings = & "cmd" "/c" "findstr /C:`"VehicleController`" `"$binary`"" 2>$null
if ($strings) { Stop-WithError "Code source Python lisible dans le binaire" }
Write-Ok "Aucun code métier lisible dans le binaire"

$distSize = (Get-ChildItem -Path $DistDir -Recurse -File | Measure-Object -Property Length -Sum).Sum
Write-Host ("📊 Taille totale : {0:N1} MB" -f ($distSize / 1MB)) -ForegroundColor Blue

# ─── 6. Packaging ───
if (-not $NoZip) {
    Write-Section "6 · Packaging de la distribution"

    $zipName = Join-Path $ProjectRoot ("LOMETA_windows_{0}.zip" -f (Get-Date -Format "yyyyMMdd_HHmmss"))
    Compress-Archive -Path (Join-Path $DistRoot "*") -DestinationPath $zipName -CompressionLevel Optimal -Force
    if (-not (Test-Path $zipName)) { Stop-WithError "Échec création du ZIP" }
    Write-Ok "Archive : $zipName"
}

# Nettoyage
Remove-Item -Recurse -Force $AddonsBuild -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force $srcClean     -ErrorAction SilentlyContinue

# ─── 7. Résumé ───
Write-Section "7 · Compilation terminée"

Write-Host ""
Write-Host "✅ COMPILATION SÉCURISÉE RÉUSSIE" -ForegroundColor Green
Write-Host ""
Write-Host "📦 Binaire  : $binary" -ForegroundColor Cyan
Write-Host "📂 Dist     : $DistDir" -ForegroundColor Cyan
if (-not $NoZip) { Write-Host "🗜  Archive  : $zipName" -ForegroundColor Cyan }
Write-Host "📋 Log      : $LogFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "🧪 Tester :" -ForegroundColor Yellow
Write-Host "   cd `"$DistDir`"; .\LOMETA.exe" -ForegroundColor Cyan
Write-Host ""

Write-Log "Compilation terminée avec succès"