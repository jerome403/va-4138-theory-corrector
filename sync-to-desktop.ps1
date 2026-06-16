# sync-to-desktop.ps1
# Copies the canonical 4138 tool from this git/APPS repo (the SOURCE OF TRUTH)
# to the Desktop working copy, so the Desktop copy survives moving off OneDrive.
#
# Workflow: edit + commit the HTML HERE, then run this script to refresh the Desktop.
# Never edit the Desktop copy directly -- it is a derivative and will be overwritten.
#
# Usage (from this folder):  .\sync-to-desktop.ps1

$ErrorActionPreference = 'Stop'

$fileName = '4138-theory-corrector.html'
$source   = Join-Path $PSScriptRoot $fileName
$desktop  = [Environment]::GetFolderPath('Desktop')
$dest     = Join-Path $desktop $fileName

if (-not (Test-Path $source)) {
    Write-Error "Source not found: $source"
    exit 1
}

Copy-Item -Path $source -Destination $dest -Force
Write-Host "Synced:" -ForegroundColor Green
Write-Host "  from  $source"
Write-Host "  to    $dest"
Write-Host "Desktop copy is now up to date with the repo (source of truth)."
