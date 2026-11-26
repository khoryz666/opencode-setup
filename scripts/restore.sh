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

# Import defaults to the current directory, so look the original one up.
map=$(mktemp)
trap 'rm -f -- "$map"' EXIT
if [[ -f $backup/manifest.jsonl ]]; then
  command -v python3 >/dev/null || die "python3 is required"
  python3 - "$backup/manifest.jsonl" > "$map" <<'PY'
import json, sys
for line in open(sys.argv[1]):
    row = json.loads(line)
    print(row["id"], row["directory"], sep="\t")
PY
fi

for f in "${files[@]}"; do
  id=$(basename "$f" .json)
  dir=$(awk -F '\t' -v id="$id" '$1 == id { print $2; exit }' "$map")
  printf 'importing %s\n' "$(basename "$f")"
  if [[ -n $dir && -d $dir ]]; then
    opencode session import "$f" --directory "$dir" || die "import failed: $f (backup kept)"
  else
    opencode session import "$f" || die "import failed: $f (backup kept)"
  fi
done

rm -rf -- "$backup"
parent=$(dirname -- "$backup")
[[ $parent == "$HOME/opencode-session-backup" ]] && rmdir -- "$parent" 2>/dev/null || true

printf 'restored %d session(s); removed %s\n' "${#files[@]}" "$backup"
