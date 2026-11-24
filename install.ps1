# Install every skill in this repo for OpenCode, on Windows.
# Idempotent: re-running is safe. Links are used so `git pull` updates the skills in
# place; where symlinks are unavailable (they need admin rights or Developer Mode) a
# directory junction or a file copy is used instead.
# Windows counterpart of install.sh. Run from PowerShell:
#   powershell -ExecutionPolicy Bypass -File .\install.ps1

$ErrorActionPreference = 'Stop'

$REPO_DIR = $PSScriptRoot
$XDG = if ($env:XDG_CONFIG_HOME) { $env:XDG_CONFIG_HOME } else { Join-Path $HOME '.config' }
$OPENCODE_CONFIG = Join-Path $XDG 'opencode'

function Write-Info { Write-Host "[install] $($args -join ' ')" -ForegroundColor Green }
function Write-Warn { Write-Host "[install] $($args -join ' ')" -ForegroundColor Yellow }

# Link <Destination> -> <Source> if absent. An existing link (symlink or junction) is
# replaced; a real file/dir is never touched.
function Install-Link {
    param([string]$Source, [string]$Destination)

    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Destination) | Out-Null

    if (Test-Path -LiteralPath $Destination) {
        $item = Get-Item -LiteralPath $Destination -Force
        if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
            # Some kind of link already; replace it so it points at $Source.
            Remove-Item -LiteralPath $Destination -Force
        } else {
            Write-Warn "exists (not a link), leaving untouched: $Destination"
            return
        }
    }

    try {
        New-Item -ItemType SymbolicLink -Path $Destination -Target $Source -ErrorAction Stop | Out-Null
        Write-Info "linked: $Destination -> $Source"
    } catch {
        # Symlinks need admin rights or Developer Mode. Fall back to a junction for
        # directories (no admin needed on NTFS) or a copy for files.
        if (Test-Path -LiteralPath $Source -PathType Container) {
            New-Item -ItemType Junction -Path $Destination -Target $Source -ErrorAction Stop | Out-Null
            Write-Info "linked (junction): $Destination -> $Source"
        } else {
            Copy-Item -LiteralPath $Source -Destination $Destination -Force
            Write-Info "copied (no symlink support): $Destination <- $Source"
        }
    }
}

# 1. Install every skill (skills/<id>/SKILL.md).
$n = 0
foreach ($skill in (Get-ChildItem -LiteralPath (Join-Path $REPO_DIR 'skills') -Directory)) {
    $skillDir = $skill.FullName
    $id = $skill.Name
    if (-not (Test-Path -LiteralPath (Join-Path $skillDir 'SKILL.md'))) { continue }

    Install-Link $skillDir (Join-Path $OPENCODE_CONFIG ("skills\$id"))

    # OpenCode agents shipped with the skill.
    $agentsDir = Join-Path $skillDir 'opencode\agents'
    if (Test-Path -LiteralPath $agentsDir -PathType Container) {
        foreach ($agent in (Get-ChildItem -LiteralPath $agentsDir -Filter '*.md')) {
            Install-Link $agent.FullName (Join-Path $OPENCODE_CONFIG ("agents\$($agent.Name)"))
        }
    }
    $n++
}
Write-Info "installed $n skill(s)"

Write-Host ''
Write-Info 'Done.'
