# Shared helpers for the parallel-agents skill. Dot-sourced by the other scripts.
# Windows counterpart of scripts/lib.sh: same default and config lookup.

# Resolve locations relative to this file. `$PSScriptRoot` is the directory of this
# file even when the skill is linked into ~/.config/opencode/skills.
$SCRIPT_DIR  = $PSScriptRoot
$SKILL_DIR   = Split-Path -Parent $SCRIPT_DIR
$REPO_ROOT   = Split-Path -Parent (Split-Path -Parent $SKILL_DIR)
$CONFIG_FILE = Join-Path $REPO_ROOT 'config.json'

# Fallback default, used only if config.json / JSON parsing are unavailable.
$DEFAULT_MODEL = 'opencode/deepseek-v4.1-flash-free'

# The file-only OpenCode agent each run selects (installed by install.ps1).
$OPENCODE_AGENT = 'parallel-agent'

function color_yellow { Write-Host ($args -join ' ') -ForegroundColor Yellow }
function color_cyan   { Write-Host ($args -join ' ') -ForegroundColor Cyan }

# Print the value at a dotted path in $CONFIG_FILE (e.g. "model").
# Returns $null (and prints nothing) if the file, the path, or JSON parsing fails.
function config_get {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $CONFIG_FILE -PathType Leaf)) { return $null }
    try {
        $data = Get-Content -LiteralPath $CONFIG_FILE -Raw | ConvertFrom-Json
    } catch {
        return $null
    }
    $current = $data
    foreach ($part in ($Path -split '\.')) {
        if ($null -eq $current) { return $null }
        $current = $current.$part
    }
    if ($current -is [string]) { return $current }
    return ($current | ConvertTo-Json -Compress)
}

# Default agent (coding) model, from config with a hardcoded fallback.
function default_model {
    $v = config_get 'model'
    if ($v) { return $v }
    return $DEFAULT_MODEL
}

# Resolve the opencode executable.
function resolve_opencode {
    $cmd = Get-Command opencode -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    return $null
}
