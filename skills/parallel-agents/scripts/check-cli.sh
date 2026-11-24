#!/usr/bin/env bash
# Prerequisite check: is the opencode CLI installed on this host?
# (Login can't be checked non-interactively; see the hint printed at the end.)
set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1090,SC1091  # lib.sh is resolved via $here at runtime
source "$here/lib.sh"

status=0
if command -v opencode >/dev/null 2>&1; then
  printf 'opencode: %s\n' "$(command -v opencode)"
  opencode --version 2>&1 | sed 's/^/          /' || true
else
  color_yellow "opencode: not found on PATH"
  echo "  install: curl -fsSL https://opencode.ai/install | bash"
  status=1
fi

agent_file="${XDG_CONFIG_HOME:-$HOME/.config}/opencode/agents/${OPENCODE_AGENT}.md"
if [ -f "$agent_file" ]; then
  echo "opencode agent: $agent_file"
else
  color_yellow "opencode agent '$OPENCODE_AGENT' not installed (run $REPO_ROOT/install.sh)"
fi

echo
if [ -f "$CONFIG_FILE" ]; then
  echo "config: $CONFIG_FILE"
  echo "  agent model: $(default_model)"
else
  color_yellow "config.json not found (expected at $CONFIG_FILE)"
fi

echo
color_cyan "If a run prints 'Not logged in', run the CLI once interactively and complete login."
exit "$status"
