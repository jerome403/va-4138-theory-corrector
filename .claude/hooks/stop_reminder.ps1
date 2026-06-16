# Stop-hook reminder (handoff workflow — see CLAUDE.md).
# Non-blocking: if there are uncommitted changes to TRACKED files, or unpushed
# commits on the current branch, surface a one-line nudge. Silent (exit 0, no
# output) when the tree is clean and pushed. Never blocks the Stop -- it only
# emits a systemMessage -- so there is zero risk of a stop-hook loop. Ignores
# untracked files (scratch files won't trigger it). Relies on the hook's cwd
# being the repo root (don't hardcode a per-machine path; this file is committed).
$ErrorActionPreference = 'SilentlyContinue'

$dirty = git status --porcelain --untracked-files=no 2>$null

$ahead = $null
$upstream = git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>$null
if ($LASTEXITCODE -eq 0 -and $upstream) {
    $ahead = git rev-list '@{u}..HEAD' 2>$null
}

if (-not $dirty -and -not $ahead) { exit 0 }   # clean + pushed -> stay silent

$bits = @()
if ($dirty) { $bits += 'uncommitted changes to tracked files' }
if ($ahead) { $bits += 'unpushed commits' }
$msg = 'Heads up before ending: ' + ($bits -join ' and ') +
    '. If a change shipped: commit/push, run sync-to-desktop.ps1 to refresh the ' +
    'Desktop copy, and follow the handoff rule in CLAUDE.md.'

[Console]::Out.Write((@{ systemMessage = $msg } | ConvertTo-Json -Compress))
exit 0
