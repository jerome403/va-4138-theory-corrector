# sync-to-desktop.ps1
# Copies the canonical 4138 tool from this git/APPS repo (the SOURCE OF TRUTH) to
# the Desktop working copies. Keeps BOTH the shell "Desktop" (which may be
# OneDrive-redirected) and the local profile Desktop (C:\Users\<you>\Desktop) in
# sync, so the tool survives turning OneDrive off.
#
# Workflow: edit + commit the HTML HERE, then run this. Never edit a Desktop copy
# directly -- it is a derivative and gets overwritten.
#
# Usage (from this folder):  .\sync-to-desktop.ps1

$ErrorActionPreference = 'Stop'

$fileName = '4138-theory-corrector.html'
$source   = Join-Path $PSScriptRoot $fileName

if (-not (Test-Path $source)) {
    Write-Error "Source not found: $source"
    exit 1
}

# Targets: the shell Desktop known folder + the literal local profile Desktop.
# When OneDrive redirection is OFF these resolve to the same path (deduped below).
$targets = @(
    [Environment]::GetFolderPath('Desktop'),
    (Join-Path $env:USERPROFILE 'Desktop')
) | Where-Object { $_ }

$seen = @{}
foreach ($dir in $targets) {
    $key = $dir.TrimEnd('\').ToLower()
    if ($seen.ContainsKey($key)) { continue }
    $seen[$key] = $true

    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    $dest = Join-Path $dir $fileName
    Copy-Item -Path $source -Destination $dest -Force
    Write-Host "Synced -> $dest" -ForegroundColor Green
}

Write-Host "Desktop copies are up to date with the repo (source of truth)."
