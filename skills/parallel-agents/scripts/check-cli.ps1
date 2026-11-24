# Prerequisite check: is the opencode CLI installed on this host? (Login can't be
# checked non-interactively; see the hint printed at the end.)
# Windows counterpart of check-cli.sh.

$ErrorActionPreference = 'Continue'
. (Join-Path $PSScriptRoot 'lib.ps1')

$status = 0
$cmd = Get-Command opencode -ErrorAction SilentlyContinue
if ($cmd) {
    Write-Host "opencode: $($cmd.Source)"
    & opencode --version 2>&1 | ForEach-Object { Write-Host ("          {0}" -f $_) }
} else {
    color_yellow 'opencode: not found on PATH'
    Write-Host '  install: irm https://opencode.ai/install.ps1 | iex'
    $status = 1
}

$xdg = if ($env:XDG_CONFIG_HOME) { $env:XDG_CONFIG_HOME } else { Join-Path $HOME '.config' }
$agentFile = Join-Path (Join-Path $xdg 'opencode') ("agents\$OPENCODE_AGENT.md")
if (Test-Path -LiteralPath $agentFile) {
    Write-Host "opencode agent: $agentFile"
} else {
    color_yellow "opencode agent '$OPENCODE_AGENT' not installed (run $REPO_ROOT\install.ps1)"
}

Write-Host ''
if (Test-Path -LiteralPath $CONFIG_FILE) {
    Write-Host "config: $CONFIG_FILE"
    Write-Host "  agent model: $(default_model)"
} else {
    color_yellow "config.json not found (expected at $CONFIG_FILE)"
}

Write-Host ''
color_cyan "If a run prints 'Not logged in', run the CLI once interactively and complete login."
exit $status
