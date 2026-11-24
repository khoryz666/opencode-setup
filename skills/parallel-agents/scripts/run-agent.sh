#!/usr/bin/env bash
# One implementation agent. Launched DETACHED by launch.sh so it survives
# terminal close / Ctrl-C. The agent may only read and write files; a reviewer
# runs tests and commits.
set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1090,SC1091  # lib.sh is resolved via $here at runtime
source "$here/lib.sh"

repo=""; brief=""; marker=""; log=""; model=""; title="parallel-agent"
need_val() { [ $# -ge 2 ] || { echo "run-agent: $1 needs a value" >&2; exit 2; }; }
while [ $# -gt 0 ]; do
  case "$1" in
    --repo|--brief|--marker|--log|--model|--title) need_val "$@" ;;
  esac
  case "$1" in
    --repo)   repo="$2";   shift 2 ;;
    --brief)  brief="$2";  shift 2 ;;
    --marker) marker="$2"; shift 2 ;;
    --log)    log="$2";    shift 2 ;;
    --model)  model="$2";  shift 2 ;;
    --title)  title="$2";  shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

[ -n "$repo" ]   || { echo "run-agent: --repo is required" >&2; exit 2; }
[ -n "$brief" ]  || { echo "run-agent: --brief is required" >&2; exit 2; }
[ -n "$marker" ] || { echo "run-agent: --marker is required" >&2; exit 2; }
[ -n "$log" ]    || { echo "run-agent: --log is required" >&2; exit 2; }

marker_abs="$repo/$marker"
rm -f "$marker_abs" "$log"

# Always leave a marker, even on an early failure, so the orchestrator's wait
# loop never hangs on an agent that died before running.
code=1
trap 'echo "RUN_DONE exit=$code at $(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$marker_abs"' EXIT

command -v opencode >/dev/null 2>&1 || { echo "run-agent: opencode not found on PATH" >&2; exit 2; }
model="${model:-$(default_model)}"

cd "$repo" || { echo "run-agent: cannot cd to $repo" >&2; exit 1; }

prompt="Read the file $brief in this repository and implement everything it \
specifies, following it exactly. Only read and write files; do not run any \
shell, package-manager, git, or test commands, and do not commit. Mirror the \
existing modules and conventions already in this repo. When finished, print a \
short list of files created and any TODOs, then print DONE on its own line."

echo "=== $title :: $brief (model: $model) ==="

opencode run "$prompt" --agent "$OPENCODE_AGENT" --model "$model" --auto 2>&1 | tee "$log"
code=${PIPESTATUS[0]}

echo
echo "=== DONE: $title (exit=$code). Files written; reviewer will test + commit. ==="
exit 0
