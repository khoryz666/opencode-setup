#!/usr/bin/env bash
# Shared helpers for the parallel-agents skill. Sourced by the other scripts.

# Resolve locations relative to this file. `pwd -P` follows the install symlink,
# so REPO_ROOT is the real clone directory even when invoked via ~/.config/opencode/skills.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd -P)"
REPO_ROOT="$(cd "$SKILL_DIR/../.." && pwd -P)"
CONFIG_FILE="$REPO_ROOT/config.json"

# Fallback default, used only if config.json / python3 are unavailable.
DEFAULT_MODEL="opencode/deepseek-v4.1-flash-free"

# The file-only OpenCode agent each run selects (installed by install.sh).
# Exported because run-agent.sh and check-cli.sh read it after sourcing this file.
export OPENCODE_AGENT="parallel-agent"

color_yellow() { printf '\033[33m%s\033[0m\n' "$*"; }
color_cyan()   { printf '\033[36m%s\033[0m\n' "$*"; }

# Print the value at a dotted path in $CONFIG_FILE (e.g. "model").
# Returns non-zero (and prints nothing) if unavailable.
config_get() {
  local path="$1"
  [ -f "$CONFIG_FILE" ] || return 1
  command -v python3 >/dev/null 2>&1 || return 1
  python3 - "$CONFIG_FILE" "$path" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(1)
for part in sys.argv[2].split("."):
    if isinstance(d, dict) and part in d:
        d = d[part]
    else:
        sys.exit(1)
print(d if not isinstance(d, (dict, list)) else json.dumps(d))
PY
}

# Default agent (coding) model, from config with a hardcoded fallback.
default_model() {
  local v
  v="$(config_get model 2>/dev/null || true)"
  printf '%s\n' "${v:-$DEFAULT_MODEL}"
}
