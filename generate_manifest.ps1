# ============================================================
#  LOMETA — Génération du manifeste de distribution (Windows)
# ============================================================

param(
    [Parameter(Mandatory=$true)][string]$DistPath,
    [Parameter(Mandatory=$true)][string]$Version,
    [string]$Output = ""
)

$ErrorActionPreference = "Stop"

if (-not $Output) { $Output = Join-Path $DistPath "manifest.json" }
if (-not (Test-Path $DistPath)) { Write-Error "$DistPath n'existe pas" }

$distAbs = (Resolve-Path $DistPath).Path
$distName = Split-Path $distAbs -Leaf

Write-Host "🔍 Génération du manifeste…" -ForegroundColor Blue
Write-Host "   Dist    : $distAbs"
Write-Host "   Version : $Version"
Write-Host "   Sortie  : $Output"

# Binaire principal
$binary = $null
foreach ($c in @("LOMETA.exe", "LOMETA", "LOMETA.bin")) {
    $candidate = Join-Path $distAbs $c
    if (Test-Path $candidate) { $binary = $c; break }
}
if (-not $binary) { Write-Error "Binaire LOMETA introuvable" }

$binaryPath = Join-Path $distAbs $binary
$binaryHash = (Get-FileHash $binaryPath -Algorithm SHA256).Hash.ToLower()
$binarySize = (Get-Item $binaryPath).Length

# Suffixe ABI
$pyAbi = ""
try { $pyAbi = (& $env:PYTHON -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX') or '')").Trim() } catch {}

# Fichiers
Push-Location $distAbs
try {
    $files = Get-ChildItem -Path $distAbs -Recurse -File |
        Where-Object {
            $_.Name -notin @("manifest.json", "manifest.json.sig") -and
            $_.Extension -ne ".log" -and
            $_.FullName -notmatch "\\__pycache__\\" -and
            $_.FullName -notmatch "\\data\\"
        } |
        Sort-Object FullName

    $fileEntries = @()
    foreach ($f in $files) {
        $rel = $f.FullName.Substring($distAbs.Length + 1).Replace("\", "/")
        $hash = (Get-FileHash $f.FullName -Algorithm SHA256).Hash.ToLower()
        $fileEntries += [PSCustomObject]@{
            path   = $rel
            size   = $f.Length
            sha256 = $hash
        }
    }

    $manifest = [PSCustomObject]@{
        schema_version    = 1
        app_name          = "LOMETA"
        version           = $Version
        generated_at      = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        platform          = "windows"
        arch              = $env:PROCESSOR_ARCHITECTURE.ToLower()
        python_abi        = $pyAbi
        binaire           = $binary
        binaire_sha256    = $binaryHash
        binaire_taille    = $binarySize
        fichiers          = $fileEntries
        requirements      = [PSCustomObject]@{
            python_min   = "3.10"
            os           = @("windows", "linux")
            libs_systeme = @("vcruntime140", "msvcp140")
        }
        total_fichiers    = $fileEntries.Count
        total_taille      = ($files | Measure-Object -Property Length -Sum).Sum
    }

    $manifest | ConvertTo-Json -Depth 10 | Set-Content -Path $Output -Encoding UTF8

    Write-Host ""
    Write-Host "✅ Manifeste généré : $Output" -ForegroundColor Green
    Write-Host "   Taille : $((Get-Item $Output).Length) octets"
    Write-Host "   Fichiers : $($fileEntries.Count)"
} finally {
    Pop-Location
}