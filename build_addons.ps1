# ============================================================
#  LOMETA — Compilation ciblée d'addons (Windows)
# ============================================================
#  Usage :
#    .\build_addons.ps1                       # tous
#    .\build_addons.ps1 Automobiles           # un seul
#    .\build_addons.ps1 Automobiles sinistres # plusieurs
#    .\build_addons.ps1 -List                 # lister
#    .\build_addons.ps1 -Clean                # nettoyer
# ============================================================

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Addons,
    [switch]$List,
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib_build.ps1")

$LogFile = Join-Path $ProjectRoot ("build_addons_{0}.log" -f (Get-Date -Format "yyyyMMdd_HHmmss"))

# Liste
if ($List) {
    Write-Host "Addons disponibles :" -ForegroundColor White
    Get-ChildItem -Path $AddonsSrc -Directory | ForEach-Object { Write-Host "  • $($_.Name)" }
    exit 0
}

Test-Prerequisites

# Localiser le dist
$distDir = Get-ChildItem -Path $DistRoot -Directory -Filter "*.dist" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $distDir) { Stop-WithError "Aucun dist_secure/*.dist. Lancez d'abord .\build_windows.ps1" }
$Global:DistDir = $distDir.FullName

# Nettoyage
if ($Clean) {
    Write-Section "Nettoyage"
    if (-not $Addons -or $Addons.Count -eq 0) {
        Remove-Item -Recurse -Force $AddonsBuild -ErrorAction SilentlyContinue
        Get-ChildItem -Path (Join-Path $DistDir "addons") -Directory -ErrorAction SilentlyContinue |
            Remove-Item -Recurse -Force
        Write-Ok "Tous les builds supprimés"
        exit 0
    } else {
        foreach ($name in $Addons) {
            Remove-Item -Recurse -Force (Join-Path $AddonsBuild $name) -ErrorAction SilentlyContinue
            Remove-Item -Recurse -Force (Join-Path (Join-Path $DistDir "addons") $name) -ErrorAction SilentlyContinue
            Write-Ok "$name nettoyé"
        }
        exit 0
    }
}

New-Item -ItemType Directory -Path $AddonsBuild -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $DistDir "addons") -Force | Out-Null

# Addons à compiler
if (-not $Addons -or $Addons.Count -eq 0) {
    $Addons = Get-ChildItem -Path $AddonsSrc -Directory | Select-Object -ExpandProperty Name
}
if (-not $Addons) { Stop-WithError "Aucun addon à compiler" }

Write-Section "Compilation ciblée"
Write-Host "🎯 Addons : $($Addons -join ', ')" -ForegroundColor White

$failed = @()
$success = @()

foreach ($name in $Addons) {
    $prepared = Initialize-AddonSource -Name $name
    if ($prepared -and (Invoke-CompileAddon -Name $name) -and (Install-Addon -Name $name)) {
        $success += $name
    } else {
        $failed += $name
    }
}

Write-Section "Résumé"

if ($success) { Write-Ok "Succès : $($success.Count) → $($success -join ', ')" }
if ($failed) {
    foreach ($f in $failed) { Write-Fail $f }
    Write-Host "`n💡 Log : $LogFile" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n✅ Tous les addons ciblés compilés" -ForegroundColor Green
Write-Host "`n📂 Contenu de $DistDir\addons :" -ForegroundColor White
Get-ChildItem -Path (Join-Path $DistDir "addons") -Directory | ForEach-Object {
    $so = Get-ChildItem -Path $_.FullName -Filter "__init*" -File | Where-Object { $_.Extension -in @(".pyd", ".so") } | Select-Object -First 1
    $size = if ($so) { "{0:N1} MB" -f ($so.Length / 1MB) } else { "?" }
    $nbData = (Get-ChildItem -Path $_.FullName -File | Where-Object { $_.Extension -notin @(".pyd", ".so") }).Count
    Write-Host "   $($_.Name) : $size, $nbData fichier(s) de données" -ForegroundColor Cyan
}