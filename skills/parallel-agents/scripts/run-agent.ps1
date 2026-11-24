param(
    [Parameter(Mandatory)][string]$Repo,    # repo root (absolute)
    [Parameter(Mandatory)][string]$Brief,   # brief path, relative to repo
    [Parameter(Mandatory)][string]$Marker,  # completion marker path, relative to repo
    [Parameter(Mandatory)][string]$Log,     # log file path (absolute)
    [string]$Model = '',
    [string]$Title = 'parallel-agent'
)

# One implementation agent. Launched DETACHED by launch.ps1 so it survives terminal
# close / Ctrl-C. The agent may only read and write files; a reviewer runs tests and
# commits. Windows counterpart of run-agent.sh.

$ErrorActionPreference = 'Continue'
. (Join-Path $PSScriptRoot 'lib.ps1')

if ($host.UI.RawUI) { $host.UI.RawUI.WindowTitle = $Title }
$markerAbs = Join-Path $Repo $Marker

Remove-Item -LiteralPath $markerAbs -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $Log -ErrorAction SilentlyContinue
Set-Location -LiteralPath $Repo

if (-not $Model) { $Model = default_model }

$prompt = "Read the file $Brief in this repository and implement everything it " +
    "specifies, following it exactly. Only read and write files; do not run any " +
    "shell, package-manager, git, or test commands, and do not commit. Mirror the " +
    "existing modules and conventions already in this repo. When finished, print a " +
    "short list of files created and any TODOs, then print DONE on its own line."

Write-Host "=== $Title :: $Brief (model: $Model) ===" -ForegroundColor Cyan
Write-Host ''

# Always leave a marker, even on an early failure, so the orchestrator's wait loop
# never hangs on an agent that died before running.
$code = 1
try {
    $opencode = resolve_opencode
    if (-not $opencode) {
        Write-Host 'run-agent: opencode CLI not found' -ForegroundColor Red
    } else {
        & $opencode run $prompt --agent $OPENCODE_AGENT --model $Model --auto 2>&1 |
            Tee-Object -FilePath $Log
        $code = $LASTEXITCODE
    }
} finally {
    "RUN_DONE exit=$code at $(Get-Date -Format o)" | Out-File -LiteralPath $markerAbs -Encoding utf8
}

Write-Host ''
Write-Host "=== DONE: $Title (exit=$code). Files written; reviewer will test + commit. ===" -ForegroundColor Green
exit 0
