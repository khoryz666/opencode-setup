#!/usr/bin/env bash
set -euo pipefail

# Imports a reset.sh session backup, then removes it. The backup is kept if any
# import fails, so a failed restore never loses history.

die() { printf 'error: %s\n' "$*" >&2; exit 1; }

usage() {
  cat <<'EOF'
Usage: scripts/restore.sh [BACKUP_DIR]

Imports every session in BACKUP_DIR/sessions, then deletes BACKUP_DIR.
Defaults to the newest ~/opencode-session-backup/* directory.

Log in first (`opencode`, then /connect). On any import failure the backup is
kept and the script exits non-zero.
EOF
}

case ${1:-} in
  -h|--help) usage; exit 0 ;;
esac
(($# <= 1)) || die "too many arguments"

backup=${1:-}
if [[ -z $backup ]]; then
  backup=$(ls -1dt "$HOME"/opencode-session-backup/*/ 2>/dev/null | head -1 || true)
  [[ -n $backup ]] || die "no backup under ~/opencode-session-backup"
fi
backup=${backup%/}
backup=${backup/#\~/$HOME}

command -v opencode >/dev/null || die "opencode is not installed"
[[ -d $backup/sessions ]] || die "not a session backup: $backup"

shopt -s nullglob
files=("$backup"/sessions/*.json)
shopt -u nullglob
((${#files[@]} > 0)) || die "no session files in $backup/sessions"

# Import defaults to the current directory, so look the original one up. Order
# parents before children: a child cannot be imported before its parent.
command -v python3 >/dev/null || die "python3 is required"
map=$(mktemp)
trap 'rm -f -- "$map"' EXIT
python3 - "$backup" > "$map" <<'PY'
import json, os, sys

backup = sys.argv[1]
sessions = os.path.join(backup, "sessions")
dirs = {}
manifest = os.path.join(backup, "manifest.jsonl")
if os.path.exists(manifest):
    for line in open(manifest):
        row = json.loads(line)
        dirs[row["id"]] = row["directory"]

paths = [os.path.join(sessions, f) for f in os.listdir(sessions) if f.endswith(".json")]
parents = {}
for path in paths:
    info = json.load(open(path))["info"]
    parents[info["id"]] = info.get("parentID")

def depth(sid):
    d, seen = 0, set()
    while parents.get(sid) and sid not in seen:
        seen.add(sid)
        sid = parents[sid]
        d += 1
    return d

for path in sorted(paths, key=lambda p: depth(os.path.basename(p)[:-5])):
    print(path, dirs.get(os.path.basename(path)[:-5], ""), sep="\t")
PY

while IFS=$'\t' read -r f dir; do
  printf 'importing %s\n' "$(basename "$f")"
  if [[ -n $dir && -d $dir ]]; then
    opencode session import "$f" --directory "$dir" || die "import failed: $f (backup kept)"
  else
    opencode session import "$f" || die "import failed: $f (backup kept)"
  fi
done < "$map"

rm -rf -- "$backup"
parent=$(dirname -- "$backup")
[[ $parent == "$HOME/opencode-session-backup" ]] && rmdir -- "$parent" 2>/dev/null || true

printf 'restored %d session(s); removed %s\n' "${#files[@]}" "$backup"
