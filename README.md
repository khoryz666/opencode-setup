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

If `~/.config/opencode` exists, back it up first:

```bash
mv ~/.config/opencode ~/.config/opencode.backup
git clone git@github.com:khoryz666/opencode-setup.git ~/.config/opencode
```

Update with `git -C ~/.config/opencode pull`. Credentials are not in git; run
`opencode auth login` once.

A fresh install needs nothing outside this repo. OpenCode supplies its own
skills (`opencode`, `report`, `browser`); ponytail is fetched from npm;
`~/.claude` and `~/.agents` are not needed.

## Contents

| Path | What |
|------|------|
| `opencode.json` | Formatter, snapshots, compaction, permissions, ponytail. |
| `cli.json` | Terminal theme: GitHub. |
| `agents/tutor.md` | Tutor agent: explains and reviews, never edits. |
| `commands/learn.md` | `/learn <task>` — one step at a time. |
| `skills/` | Custom and vendored skills. |
| `learned/preferences.md` | Curated preferences loaded every session. |
| `scripts/reset.sh` | Export sessions, wipe local state, reinstall and re-clone. |
| `scripts/restore.sh` | Import a session backup, then delete it. |
| `THIRD_PARTY.md` | Vendored skill sources and licences. |

## Skills

- **`commit`** — small conventional commits; apply review feedback one item at a time.
- **`write-docs`** — concise docs; keep docs, plans and code aligned.
- **`humanize`** — rewrite ODT reports; preserve citations and formatting.
- **`security-review`** — read-only security review before releases.
- **`drawio`** — diagrams, mockups, posters and infographics.
- **`zotero`** — audit a Zotero library against a report's citations; write JS for edits.

Vendored from Anthropic's Apache-2.0 skills, adapted for OpenCode; see `THIRD_PARTY.md`.

- **`docx`** — create, read, edit and template Word documents.
- **`pdf`** — extract, merge, split, watermark, fill and OCR PDFs.
- **`pptx`** — create, read, edit and template PowerPoint decks.
- **`xlsx`** — create, read, edit and recalculate spreadsheets.
- **`skill-creator`** — draft, evaluate and improve skills.

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

## Reset

`scripts/reset.sh` exports every session to
`~/opencode-session-backup/<timestamp>/` (full transcripts, mode 700), then
removes the binary, data, state, cache, temp files and local config, reinstalls
OpenCode and clones this repo back.

It refuses to run with uncommitted or unpushed config. Run it from a normal
terminal, not from inside OpenCode.

- `--dry-run` — print the plan, change nothing.
- `--out DIR` — choose the backup directory.
- `--force` — wipe even if some sessions fail to export.

Restore after logging in:

```bash
~/.config/opencode/scripts/restore.sh ~/opencode-session-backup/<timestamp>
```

`restore.sh` imports every session, then deletes the backup directory and the
empty parent. If any import fails, it keeps the backup and exits non-zero.

## Add a skill

Add `skills/<name>/SKILL.md`; there is no install step. Do not duplicate an
OpenCode built-in.

## Prerequisites

Linux or macOS, OpenCode with a connected provider, `git`, `python3` and Node.js
(npm). Document skills install their Python/npm packages on demand.
Optional: draw.io Desktop for exports; LibreOffice for PDF and spreadsheet checks.

## License

MIT. The `drawio`, `docx`, `pdf`, `pptx`, `xlsx` and `skill-creator` skills are
Apache 2.0; see each skill's `LICENSE.txt` and `THIRD_PARTY.md`.
