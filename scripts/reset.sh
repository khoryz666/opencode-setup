#!/usr/bin/env bash
set -euo pipefail

# Re-exec from /tmp so this script can delete the config repo it lives in.
if [[ ${OPENCODE_RESET_DETACHED:-0} != 1 ]]; then
  repo=$(cd -- "$(dirname -- "$(readlink -f -- "$0")")/.." && pwd)
  tmp=$(mktemp -d /tmp/opencode-reset.XXXXXX)
  cp -- "$(readlink -f -- "$0")" "$tmp/reset.sh"
  OPENCODE_RESET_DETACHED=1 OPENCODE_RESET_TMP="$tmp" OPENCODE_RESET_REPO="$repo" \
    exec bash "$tmp/reset.sh" "$@"
fi
trap 'rm -rf -- "${OPENCODE_RESET_TMP:?}"' EXIT

umask 077

REPO=${OPENCODE_RESET_REPO:?}
REMOTE=git@github.com:khoryz666/opencode-setup.git
DB=$HOME/.local/share/opencode/opencode.db
DRY_RUN=0
FORCE=0
OUT=""

die() { printf 'error: %s\n' "$*" >&2; exit 1; }
usage() {
  cat <<'EOF'
Usage: scripts/reset.sh [--dry-run] [--out DIR] [--force]

Exports every session, wipes OpenCode's binary, data, state, cache and local
config, reinstalls OpenCode, and clones the setup repo back into place.

  --dry-run   Show what would happen; change nothing.
  --out DIR   Session backup directory (default: ~/opencode-session-backup/<timestamp>).
  --force     Wipe even if some sessions fail to export.

Run from a normal terminal, not from inside OpenCode.
EOF
}

while (($#)); do
  case $1 in
    --dry-run) DRY_RUN=1; shift ;;
    --out) OUT=${2:?--out needs a directory}; shift 2 ;;
    --force) FORCE=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[[ -d $REPO/.git ]] || die "not a git repo: $REPO"
repo_remote=$(git -C "$REPO" remote get-url origin 2>/dev/null || true)
[[ $repo_remote == *khoryz666/opencode-setup* ]] || die "origin is not $REMOTE"
[[ -z ${OPENCODE_SESSION_ID:-} || $DRY_RUN == 1 ]] ||
  die "run this from a normal terminal, not from inside OpenCode"
if ((DRY_RUN == 0)) && pgrep -x opencode -a | grep -v 'serve --service' | grep -q .; then
  die "close the OpenCode TUI before running this"
fi

command -v git >/dev/null || die "git is required"
command -v python3 >/dev/null || die "python3 is required"
command -v curl >/dev/null || die "curl is required"
command -v opencode >/dev/null || die "opencode is not installed"

git -C "$REPO" fetch --quiet origin main || die "cannot fetch $REMOTE"
[[ -z $(git -C "$REPO" status --porcelain) ]] || die "config has uncommitted changes; commit and push first"
ahead=$(git -C "$REPO" rev-list --count origin/main..HEAD)
((ahead == 0)) || die "$ahead local commit(s) not pushed; push first"

SESSION_COUNT=0
[[ -f $DB ]] && SESSION_COUNT=$(python3 - "$DB" <<'PY'
import sqlite3, sys
con = sqlite3.connect(f"file:{sys.argv[1]}?mode=ro", uri=True)
print(con.execute("select count(*) from session_v2").fetchone()[0])
PY
)

out=${OUT:-$HOME/opencode-session-backup/$(date +%Y%m%d-%H%M%S)}
for p in "$HOME/.opencode" "$HOME/.local/share/opencode" "$HOME/.local/state/opencode" \
         "$HOME/.cache/opencode" "$HOME/.config/opencode"; do
  [[ $out == "$p" || $out == "$p"/* ]] && die "backup directory must be outside $p"
done

if ((DRY_RUN)); then
  cat <<EOF
repo:       $REPO (clean, pushed)
sessions:   $SESSION_COUNT
backup:     $out
would stop: opencode service, opencode-pty
would remove: ~/.opencode, ~/.local/share/opencode, ~/.local/state/opencode,
              ~/.cache/opencode, ~/.config/opencode, /tmp/opencode*
would install: curl -fsSL https://opencode.ai/v2/install | bash
would clone:   $REMOTE -> ~/.config/opencode
EOF
  exit 0
fi

mkdir -p "$out/sessions"
chmod 700 "$out" "$out/sessions"
python3 - "$DB" "$out" <<'PY'
import json, sqlite3, sys
db, out = sys.argv[1], sys.argv[2]
con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
rows = con.execute(
    "select id, directory, title, time_created from session_v2 order by time_created"
).fetchall()
with open(f"{out}/ids.txt", "w") as ids, open(f"{out}/manifest.jsonl", "w") as manifest:
    for sid, directory, title, created in rows:
        ids.write(sid + "\n")
        manifest.write(json.dumps({
            "id": sid, "directory": directory, "title": title, "created": created
        }) + "\n")
print(len(rows))
PY

total=$(wc -l < "$out/ids.txt")
done=0
failed=0
while IFS= read -r id; do
  if opencode session export "$id" > "$out/sessions/$id.json" 2>>"$out/export.log" \
     && [[ -s $out/sessions/$id.json ]]; then
    done=$((done + 1))
  else
    failed=$((failed + 1))
    rm -f -- "$out/sessions/$id.json"
  fi
  printf '\r%d/%d exported, %d failed' "$done" "$total" "$failed" >&2
done < "$out/ids.txt"
printf '\n' >&2

if ((failed > 0)); then
  echo "$failed session(s) failed; see $out/export.log" >&2
  ((FORCE == 1)) || die "rerun with --force to wipe anyway"
fi

cat > "$out/RESTORE.md" <<EOF
# OpenCode session backup

Full exports, including transcripts. Treat this directory as private (mode 700).

Restore after reinstalling and logging in:

    ~/.config/opencode/scripts/restore.sh "$out"

The restore script deletes this backup after every import succeeds.
Metadata is in \`manifest.jsonl\`.
EOF

printf 'stopping OpenCode...\n'
opencode service stop >/dev/null 2>&1 || true
pkill -f "$HOME/.opencode/bin/opencode serve --service" 2>/dev/null || true
pkill -f "$HOME/.cache/opencode/bin/opencode-pty" 2>/dev/null || true
sleep 1

printf 'removing traces...\n'
rm -rf -- "$HOME/.opencode" \
          "$HOME/.local/share/opencode" \
          "$HOME/.local/state/opencode" \
          "$HOME/.cache/opencode" \
          "$HOME/.config/opencode"
rm -rf -- /tmp/opencode "/tmp/opencode-pty-$(id -u)"

printf 'installing OpenCode...\n'
curl -fsSL https://opencode.ai/v2/install | bash
"$HOME/.opencode/bin/opencode" --version >/dev/null || die "install failed"

printf 'cloning config...\n'
git clone "$REMOTE" "$HOME/.config/opencode"

cat <<EOF

Done.

Sessions: $out
Config:   $HOME/.config/opencode

Next:
  opencode
  /connect        (log in to your provider)

Restore history (deletes the backup after import):
  ~/.config/opencode/scripts/restore.sh "$out"
EOF
