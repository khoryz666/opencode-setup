#!/usr/bin/env bash
# Install every skill in this repo for OpenCode.
# Idempotent: re-running is safe, and symlinks are used so `git pull` updates
# the skills in place. Add a skill by dropping a skills/<id>/SKILL.md directory.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENCODE_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/opencode"

info() { printf '\033[32m[install]\033[0m %s\n' "$*"; }
warn() { printf '\033[33m[install]\033[0m %s\n' "$*"; }

# Link <dst> -> <src> if absent. A mismatched symlink (e.g. from an earlier
# layout) is replaced; a real file/dir is never touched.
link_if_absent() {
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [ -L "$dst" ]; then
    if [ "$(readlink "$dst")" = "$src" ]; then
      info "already installed: $dst -> $src"
    else
      rm -f "$dst"
      ln -s "$src" "$dst"
      info "re-linked: $dst -> $src"
    fi
  elif [ -e "$dst" ]; then
    warn "exists (not a symlink), leaving untouched: $dst"
  else
    ln -s "$src" "$dst"
    info "linked: $dst -> $src"
  fi
}

# 1. Install every skill (skills/<id>/SKILL.md).
n=0
for skill_dir in "$REPO_DIR"/skills/*/; do
  [ -d "$skill_dir" ] || continue
  skill_dir="${skill_dir%/}"
  [ -f "$skill_dir/SKILL.md" ] || continue
  id="$(basename "$skill_dir")"
  link_if_absent "$skill_dir" "$OPENCODE_CONFIG/skills/$id"
  # OpenCode agents shipped with the skill.
  for agent in "$skill_dir"/opencode/agents/*.md; do
    [ -f "$agent" ] || continue
    link_if_absent "$agent" "$OPENCODE_CONFIG/agents/$(basename "$agent")"
  done
  n=$((n + 1))
done
info "installed $n skill(s)"

# 2. Install third-party OpenCode plugins (skipped if already present).
plugins=(@dietrichgebert/ponytail)
if command -v opencode >/dev/null 2>&1; then
  installed="$(opencode plugin list 2>/dev/null || true)"
  for p in "${plugins[@]}"; do
    if grep -qF -- "$p" <<<"$installed"; then
      info "plugin already installed: $p"
    else
      opencode plugin add "$p" && info "plugin added: $p" || warn "plugin add failed: $p"
    fi
  done
else
  warn "opencode not on PATH; skipped plugins: ${plugins[*]}"
fi

echo
info "Done. Verify with:"
for c in "$REPO_DIR"/skills/*/scripts/check-cli.sh; do
  [ -f "$c" ] && echo "  $c"
done
