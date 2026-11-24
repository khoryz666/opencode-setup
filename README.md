# opencode-setup

My global OpenCode config. The repo root is the config directory, so cloning it
into place is the install.

## Install

```bash
mkdir -p ~/.config
git clone git@github.com:khoryz666/opencode-setup.git ~/.config/opencode
```

OpenCode reads `opencode.json`, `cli.json`, `agents/`, `commands/`, `skills/` and
`learned/` from `~/.config/opencode`. Press `/reload` if it is already running.

Do **not** clone into `~/.opencode`; that is the binary directory.

If `~/.config/opencode` exists, back it up first:

```bash
mv ~/.config/opencode ~/.config/opencode.backup
git clone git@github.com:khoryz666/opencode-setup.git ~/.config/opencode
```

Update with `git -C ~/.config/opencode pull`. Credentials are not in git; run
`opencode auth login` once.

## Contents

| Path | What |
|------|------|
| `opencode.json` | Formatter, snapshots, compaction, permissions, ponytail. |
| `cli.json` | Terminal theme: GitHub. |
| `agents/tutor.md` | Tutor agent: explains and reviews, never edits. |
| `commands/learn.md` | `/learn <task>` — one step at a time. |
| `skills/` | Custom skills. |
| `learned/preferences.md` | Curated preferences loaded every session. |

OpenCode's built-in skills are not duplicated.

## Skills

- **`commit`** — small conventional commits; apply review feedback one item at a time.
- **`write-docs`** — concise docs; keep docs, plans and code aligned.
- **`humanize`** — rewrite ODT reports; preserve citations and formatting.
- **`security-review`** — read-only security review before releases.
- **`drawio`** — diagrams, mockups, posters and infographics.

## Use

Ask naturally, or force a skill with `@skill-id`.

- `/learn implement the login flow` — tutor mode.
- "Commit this as one focused commit."
- "Security-review the current diff."
- "Humanize this ODT report."
- "Make an A1 poster and export a PDF."

Ponytail adds `/ponytail`, `/ponytail-review`, `/ponytail-audit`,
`/ponytail-debt`, `/ponytail-gain` and `/ponytail-help`.

Each skill's `SKILL.md` has the detailed workflow.

## Add a skill

Add `skills/<name>/SKILL.md`; there is no install step. Do not duplicate an
OpenCode built-in.

## Prerequisites

Linux or macOS, OpenCode with a connected provider, `git` and `python3`.
Optional: draw.io Desktop for exports; LibreOffice for PDF checks.

## License

MIT. The `drawio` skill is Apache 2.0; see `skills/drawio/LICENSE.txt`.
