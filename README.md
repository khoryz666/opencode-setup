# opencode-setup

My global OpenCode configuration: custom skills, a tutor agent, and the
[ponytail](https://github.com/DietrichGebert/ponytail) plugin.

The repo root **is** the OpenCode config directory, so cloning it into place is
the whole install. There is no install script.

## Install

```bash
mkdir -p ~/.config
git clone git@github.com:khoryz666/opencode-setup.git ~/.config/opencode
```

That's it. OpenCode reads `opencode.json`, `agents/`, `commands/`, `skills/` and
`learned/` from `~/.config/opencode`. Start OpenCode, or press `/reload` if it is
already running.

Do **not** clone into `~/.opencode`: that is where the `opencode` binary lives,
not where OpenCode reads its configuration.

If `~/.config/opencode` already exists, move it aside first, then copy back any
personal settings you want to keep:

```bash
mv ~/.config/opencode ~/.config/opencode.backup
git clone git@github.com:khoryz666/opencode-setup.git ~/.config/opencode
```

Update later with:

```bash
git -C ~/.config/opencode pull
```

Credentials are not in git. On a fresh machine, connect a provider once with
`opencode auth login` (or the provider screen in the app).

## What's in here

| Path | What it is |
|------|------------|
| `opencode.json` | Global config: formatter, snapshots, compaction, permissions, instructions, ponytail. |
| `agents/tutor.md` | Tutor agent. Explains and reviews, never edits. |
| `commands/learn.md` | `/learn <task>` — deliberate-practice mode. |
| `skills/` | Custom skills. One directory per skill, each with a `SKILL.md`. |
| `learned/preferences.md` | Curated, public-safe preferences loaded into every session. |

OpenCode already ships `docx`, `pdf`, `pptx`, `xlsx`, `skill-creator` and the
other built-in skills, so this repo does not duplicate them. It only adds what
OpenCode does not have.

Memory, handoff and self-optimization plugins are intentionally not installed.
Add them when needed; keep memory private.

## Skills

**Git**
- **`commit`** — one-thing, one-line conventional commits gated on the project's
  checks, including applying review feedback one item at a time.

**Writing**
- **`write-docs`** — short, plain, purpose-first docs, plus keeping docs, plans
  and code aligned.
- **`humanize`** — rewrite reports and prose through a voice profile and an ODT
  workflow that preserves citations and formatting. The profile is provisional.

**Security**
- **`security-review`** — read-only review of secrets, data exposure, file
  handling, auth, dependencies and LLM-specific risks.

**Visuals**
- **`drawio`** — diagrams, flowcharts, architecture, mockups, plus print posters
  and infographics, exported to `.drawio`, PNG, SVG or PDF.

`drawio` is adapted from [jgraph/drawio-mcp](https://github.com/jgraph/drawio-mcp)
(Apache 2.0, © 2025 JGraph Ltd) for OpenCode, Linux/macOS and Python helpers.
See `skills/drawio/LICENSE.txt` and `skills/drawio/NOTICE`.

The `humanize` ODT scripts use only the Python standard library. Its voice
profile is still provisional until it is rebuilt from authentic writing samples.

## Learning by doing: `/learn`

`/learn <task>` switches to the `tutor` agent:

- gives you one small step at a time, not the full solution;
- waits while you write the code;
- reviews your diff and asks you to explain what changed;
- runs only the narrowest check, with approval;
- **cannot edit files** (`edit` is denied; `shell` asks first).

This is deliberate practice, not a self-optimizing loop. It is version-controlled
in `commands/learn.md` and `agents/tutor.md`.

## Safe config defaults

`opencode.json` enables:

- built-in formatters (`formatter: true`);
- snapshots, todos and compaction;
- update notifications;
- permission asks for external directories, `.env`, `git push`, `git reset
  --hard` and `rm -rf`, and a deny for `~/.ssh`;
- `watcher.ignore` for `.git`, `node_modules`, `target`, `dist`, `build` and
  `coverage`;
- `learned/preferences.md` as a global instruction file.

Private state is gitignored: `memory/`, `journal/`, `sessions/`,
`learned/usage.json`, `.env` and `service.json`.

## How to use it

Just ask in plain language. OpenCode loads a matching skill on its own. To force
one, mention it as `@skill-id` or by name.

Examples:

- "Commit this as one focused commit." → `commit`
- "Write a README for this project." → `write-docs`
- "Check whether the docs and code still agree." → `write-docs`
- "Humanize this report in my voice." → `humanize`
- "Rewrite `~/Desktop/qorfinder/doc/23ACB05662_FYP1.odt` in my voice." → `humanize`
- "Security-review the current diff." → `security-review`
- "Make an A1 conference poster about the project, portrait, and export a print PDF." → `drawio`
- "Turn these notes into a one-page infographic." → `drawio`
- "Draw the auth flow and export it as SVG." → `drawio`
- "`/learn` implement the login flow" → tutor mode

The ponytail plugin adds the `/ponytail`, `/ponytail-review`, `/ponytail-audit`,
`/ponytail-debt`, `/ponytail-gain` and `/ponytail-help` commands. It styles every
coding task, so use `/ponytail off` if you want it out of the way.

## Security review

`security-review` is a read-only review skill. Ask for it before a release, or
when a change touches parsing, storage, auth, networking, legal or client data.

It checks secrets and PII, data flow, malicious file input, local API exposure,
dependencies, LLM prompt injection, error/log leakage and data retention. For
QorFinder it also covers client-file confidentiality, local index and temp
storage, PDF parsing and model downloads.

Findings are reported as **must fix**, **should fix** and **notes**, with what,
where, impact, fix and the check that proves it. It does not edit files.

## drawio, posters and infographics

The `drawio` skill writes a native `.drawio` file first, then exports it.
Mermaid is the fastest path for flowcharts and standard diagrams; XML is used for
posters, infographics and precise layouts.

The draw.io **desktop CLI** is optional for authoring `.drawio` XML and browser
URLs. It is required for Mermaid conversion, ELK layouts and PNG/SVG/PDF export:

```bash
# macOS
brew install --cask drawio

# Ubuntu/Debian
sudo snap install drawio
```

The helper scripts need only `python3`:

```bash
python3 ~/.config/opencode/skills/drawio/scripts/repair_drawio.py poster.drawio
python3 ~/.config/opencode/skills/drawio/scripts/drawio_url.py poster.drawio
python3 ~/.config/opencode/skills/drawio/scripts/find_shapes.py "github" "slack"
```

Poster/infographic prompts work best with a format, orientation and audience:

> Make an A1 portrait conference poster for engineers. Sections: problem, method,
> results chart, conclusion, QR. Export a print PDF and keep the `.drawio`.

## Humanizing ODT reports

`humanize` edits a report through a Markdown intermediate so paragraph styles,
bold/italic spans and citations survive. The voice profile is provisional; the
ODT tooling is ready and the profile can be rebuilt from authentic samples.

```bash
# 1. Extract to an editable Markdown file
python3 ~/.config/opencode/skills/humanize/scripts/odt_extract.py \
  ~/Desktop/qorfinder/doc/23ACB05662_FYP1.odt --out /tmp/fyp.humanize

# 2. Ask the agent to rewrite /tmp/fyp.humanize/23ACB05662_FYP1.md,
#    or edit it yourself. Rewrite only blocks with rewrite=yes.

# 3. Apply to a new file; the original is untouched
python3 ~/.config/opencode/skills/humanize/scripts/odt_apply.py \
  ~/Desktop/qorfinder/doc/23ACB05662_FYP1.odt \
  /tmp/fyp.humanize/23ACB05662_FYP1.md \
  /tmp/fyp.humanize/blocks.json \
  --out ~/Desktop/qorfinder/doc/23ACB05662_FYP1.humanized.odt

# 4. Compare, check citations, optionally render a PDF
python3 ~/.config/opencode/skills/humanize/scripts/odt_verify.py \
  ~/Desktop/qorfinder/doc/23ACB05662_FYP1.odt \
  ~/Desktop/qorfinder/doc/23ACB05662_FYP1.humanized.odt --pdf
```

The extractor keeps headings and captions as read-only context and leaves
tables, references, code, metadata and short paragraphs out of the rewrite
targets. Formatting spans appear as `{{rN}}…{{/rN}}` markers; keep them when
rewriting. A dropped marker or an edit to a read-only block stops the apply step.

Refresh the profile with authentic writing samples:

```bash
python3 ~/.config/opencode/skills/humanize/scripts/style_profile.py \
  report1.odt report2.odt
```

## Add a skill

Drop in a `skills/<name>/SKILL.md` folder. There is no install step; OpenCode
picks it up automatically.

```markdown
---
name: my-skill
description: what it does and when to use it
---
# my-skill
…
```

Do not add a skill that OpenCode already ships. Check the available list in a
session first, or run `opencode` with an empty config and ask for the skill IDs.

## Prerequisites

- Linux or macOS.
- OpenCode installed and connected to a provider (`opencode auth login`).
- `git` and `python3`.
- Optional: draw.io Desktop for Mermaid conversion, layouts and image export.
- Optional: LibreOffice for `odt_verify.py --pdf` and for opening the results.

## License

MIT — see [LICENSE](LICENSE). The `drawio` skill is Apache 2.0; the rest is MIT.
Each skill keeps its own license file.
