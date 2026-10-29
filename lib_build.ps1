# ============================================================
#  LOMETA — Bibliothèque commune de compilation (Windows)
#  Sourcée par build_windows.ps1 et build_addons.ps1
#  Ne pas exécuter directement.
# ============================================================

# ─── Couleurs ───
function Write-Section {
    param([string]$Text)
    Write-Host ""
    Write-Host ("═" * 64) -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor White
    Write-Host ("═" * 64) -ForegroundColor Cyan
}

function Write-Ok     { param([string]$Text) Write-Host "✓ $Text" -ForegroundColor Green }
function Write-Warn   { param([string]$Text) Write-Host "⚠ $Text" -ForegroundColor Yellow }
function Write-Fail   { param([string]$Text) Write-Host "✗ $Text" -ForegroundColor Red }
function Write-Info   { param([string]$Text) Write-Host "ℹ $Text" -ForegroundColor Blue }

function Stop-WithError {
    param([string]$Message)
    Write-Fail $Message
    exit 1
}

# ─── Chemins ───
$Global:ProjectRoot = if ($env:PROJECT_ROOT) { $env:PROJECT_ROOT } else { Split-Path -Parent $PSCommandPath }
$Global:AddonsSrc   = Join-Path $ProjectRoot "addons"
$Global:AddonsBuild = Join-Path $ProjectRoot "addons_compiled"
$Global:DistRoot    = Join-Path $ProjectRoot "dist_secure"

# ─── Vérification des prérequis ───
function Test-Prerequisites {
    Write-Section "0 · Vérification de l'environnement"

    # Python
    if (-not $env:PYTHON) { $env:PYTHON = "python" }
    try {
        $pyVer = & $env:PYTHON --version 2>&1
    } catch {
        Stop-WithError "Python introuvable. Installez Python et ajoutez-le au PATH."
    }

    # Nuitka
    $nuitkaOk = $false
    try {
        $null = & $env:PYTHON -m nuitka --version 2>&1
        $nuitkaOk = $true
    } catch { $nuitkaOk = $false }

    if (-not $nuitkaOk) {
        Write-Warn "Nuitka manquant — installation…"
        & $env:PYTHON -m pip install --upgrade "nuitka>=2.7" ordered-set zstandard | Out-Null
        if ($LASTEXITCODE -ne 0) { Stop-WithError "Échec installation Nuitka" }
    }

    # Version Nuitka
    $nuitkaLine = (& $env:PYTHON -m nuitka --version 2>&1 | Select-Object -First 1)
    if ($nuitkaLine -match '(\d+)\.(\d+)') {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        if ($major -lt 2 -or ($major -eq 2 -and $minor -lt 7)) {
            Stop-WithError "Nuitka $major.$minor trop ancien (≥ 2.7 requis)"
        }
    }

    # Suffixe ABI
    $Global:PY_ABI_SUFFIX = (& $env:PYTHON -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))").Trim()
    if (-not $PY_ABI_SUFFIX) { $Global:PY_ABI_SUFFIX = ".pyd" }

    Write-Host "🐍 Python : $pyVer (ABI: $PY_ABI_SUFFIX)" -ForegroundColor Blue
    Write-Host "🔨 Nuitka : $nuitkaLine" -ForegroundColor Blue
    Write-Host "📂 Racine : $ProjectRoot" -ForegroundColor Blue
}

# ─── Détection récursive des inclusions ───
function Get-IncludeArgs {
    param([string]$Name, [string]$Pkg)

    $args = @()
    $args += "--include-package=addons.$Name"

    # Sous-packages
    Get-ChildItem -Path $Pkg -Filter "__init__.py" -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($Pkg.Length + 1).Replace("\", "/")
        $dir = Split-Path $rel -Parent
        if ($dir -and $dir -ne ".") {
            $dotted = $dir.Replace("/", ".")
            $args += "--include-package=addons.$Name.$dotted"
        }
    }

    # Modules .py isolés
    Get-ChildItem -Path $Pkg -Filter "*.py" -Recurse -File | ForEach-Object {
        $base = $_.BaseName
        if ($base -eq "__init__") { return }
        $rel = $_.FullName.Substring($Pkg.Length + 1).Replace("\", "/")
        $relNoExt = $rel -replace '\.py$', ''
        $dotted = $relNoExt.Replace("/", ".")
        $args += "--include-module=addons.$Name.$dotted"
    }

    # Namespace packages (dossiers sans __init__.py)
    Get-ChildItem -Path $Pkg -Directory -Recurse | ForEach-Object {
        $rel = $_.FullName.Substring($Pkg.Length + 1).Replace("\", "/")
        if ($rel -match '^(\.|_|tests?|migrations|__pycache__)') { return }
        if (Test-Path (Join-Path $_.FullName "__init__.py")) { return }
        $dotted = $rel.Replace("/", ".")
        $args += "--include-package=addons.$Name.$dotted"
    }

    return $args
}

# ─── Préparation des sources ───
function Initialize-AddonSource {
    param([string]$Name)

    $src = Join-Path $AddonsSrc $Name
    $dst = Join-Path $AddonsBuild $Name
    if (-not (Test-Path $src)) { Write-Warn "Addon introuvable : $Name"; return $false }

    if (Test-Path $dst) { Remove-Item -Recurse -Force $dst }
    New-Item -ItemType Directory -Path $dst -Force | Out-Null

    # Copie avec robocopy (plus robuste que Copy-Item pour les exclusions)
    $excludeDirs  = @(".history", "__pycache__", ".pytest_cache", "_build")
    $excludeFiles = @("*.pyc", "*.pyo", "*.db", "*.sqlite", "test_*.py")

    $robocopyArgs = @($src, $dst, "/E", "/NFL", "/NDL", "/NJH", "/NJS", "/nc", "/ns", "/np")
    $robocopyArgs += "/XD"
    $robocopyArgs += $excludeDirs
    $robocopyArgs += "/XF"
    $robocopyArgs += $excludeFiles

    & robocopy @robocopyArgs | Out-Null
    if ($LASTEXITCODE -ge 8) { Write-Warn "robocopy a échoué pour $Name"; return $false }

    # __init__.py obligatoire
    $initPath = Join-Path $dst "__init__.py"
    if (-not (Test-Path $initPath)) {
        Write-Warn "$Name/__init__.py absent — création minimale"
        Set-Content -Path $initPath -Value '"""Auto-generated."""' -Encoding UTF8
    }
    return $true
}

# ─── Compilation d'un addon ───
function Invoke-CompileAddon {
    param([string]$Name)

    $pkg = Join-Path $AddonsBuild $Name
    if (-not (Test-Path $pkg)) { Write-Warn "Source non préparée : $Name"; return $false }

    Write-Host ""
    Write-Host "──────────────────────────────────────────────────────────" -ForegroundColor Cyan
    Write-Host "  → Compilation : $Name" -ForegroundColor White
    Write-Host "──────────────────────────────────────────────────────────" -ForegroundColor Cyan

    $buildOut = Join-Path $pkg "_build"
    if (Test-Path $buildOut) { Remove-Item -Recurse -Force $buildOut }
    New-Item -ItemType Directory -Path $buildOut -Force | Out-Null

    $includeArgs = Get-IncludeArgs -Name $Name -Pkg $pkg
    Write-Host "  📦 $($includeArgs.Count) inclusions détectées" -ForegroundColor Blue

    $nuitkaLog = Join-Path $buildOut "nuitka.log"
    $start = Get-Date

    $nuitkaArgs = @(
        "-m", "nuitka",
        "--module", "--mode=module",
        "--assume-yes-for-downloads",
        "--enable-plugin=pyside6",
        "--nofollow-import-to=pytest",
        "--nofollow-import-to=tkinter",
        "--nofollow-import-to=PyQt5",
        "--nofollow-import-to=PyQt6",
        "--nofollow-import-to=matplotlib",
        "--output-dir=$buildOut"
    ) + $includeArgs + @($pkg)

    & $env:PYTHON @nuitkaArgs *> $nuitkaLog
    $exitCode = $LASTEXITCODE

    $elapsed = [int]((Get-Date) - $start).TotalSeconds
    Get-Content $nuitkaLog -Tail 20 | ForEach-Object { Write-Host "    $_" }

    if ($exitCode -ne 0) {
        Write-Fail "Nuitka exit $exitCode (voir $nuitkaLog)"
        return $false
    }

    # Localiser le .so/.pyd principal
    $mainSo = Get-ChildItem -Path $buildOut -Filter "$Name*.so" -File -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $mainSo) {
        $mainSo = Get-ChildItem -Path $buildOut -Filter "$Name*.pyd" -File -ErrorAction SilentlyContinue | Select-Object -First 1
    }
    if (-not $mainSo) {
        $mainSo = Get-ChildItem -Path $buildOut -Filter "*.so" -File -ErrorAction SilentlyContinue | Select-Object -First 1
    }
    if (-not $mainSo) {
        $mainSo = Get-ChildItem -Path $buildOut -Filter "*.pyd" -File -ErrorAction SilentlyContinue | Select-Object -First 1
    }
    if (-not $mainSo) {
        Write-Fail "Aucune .pyd/.so générée"
        return $false
    }

    $sizeMB = [math]::Round($mainSo.Length / 1MB, 2)
    Write-Ok "compilé en ${elapsed}s → $($mainSo.Name) ($sizeMB MB)"

    $Global:ADDON_SO_PATH = $mainSo.FullName
    $Global:ADDON_BUILD_OUT = $buildOut
    return $true
}

# ─── Installation dans le dist ───
function Install-Addon {
    param([string]$Name)

    $buildOut = $ADDON_BUILD_OUT
    $mainSo = $ADDON_SO_PATH
    if (-not (Test-Path $mainSo)) { Write-Warn "Pas de .so à installer pour $Name"; return $false }

    $dest = Join-Path (Join-Path $DistDir "addons") $Name
    if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
    New-Item -ItemType Directory -Path $dest -Force | Out-Null

    # Renommer avec le suffixe ABI
    Copy-Item -Path $mainSo -Destination (Join-Path $dest "__init$PY_ABI_SUFFIX") -Force

    # Autres .so/.pyd
    Get-ChildItem -Path $buildOut -Recurse -Include "*.so","*.pyd" -File |
        Where-Object { $_.FullName -ne $mainSo } |
        ForEach-Object { Copy-Item $_.FullName -Destination $dest -Force }

    # Données non-Python
    $srcAddon = Join-Path $AddonsBuild $Name
    $excludeDirs  = @(".history", "__pycache__", "_build")
    $excludeFiles = @("*.py", "*.pyc", "*.db", "*.sqlite", "*.so", "*.pyd")
    $robocopyArgs = @($srcAddon, $dest, "/E", "/NFL", "/NDL", "/NJH", "/NJS", "/nc", "/ns", "/np")
    $robocopyArgs += "/XD"
    $robocopyArgs += $excludeDirs
    $robocopyArgs += "/XF"
    $robocopyArgs += $excludeFiles
    & robocopy @robocopyArgs | Out-Null

    Write-Ok "installé → $dest"
    return $true
}

# ─── Vérification du .so/.pyd ───
function Test-SoFile {
    param([string]$SoPath, [string]$Name)

    if (-not (Test-Path $SoPath)) { Write-Warn "$SoPath n'existe pas"; return $false }

    $count = (Get-ChildItem -Path (Split-Path $SoPath -Parent) -Filter "*.so" -File).Count +
             (Get-ChildItem -Path (Split-Path $SoPath -Parent) -Filter "*.pyd" -File).Count
    $sizeMB = [math]::Round((Get-Item $SoPath).Length / 1MB, 2)

    Write-Ok "$Name : $sizeMB MB, $count fichier(s) natif(s)"
    return $true
}