# opencode-setup

My global OpenCode configuration: custom skills, one file-only agent, and the
[ponytail](https://github.com/DietrichGebert/ponytail) plugin.

The repo root **is** the OpenCode config directory, so cloning it into place is
the whole install. There is no install script.

## Install

```bash
mkdir -p ~/.config
git clone git@github.com:khoryz666/opencode-setup.git ~/.config/opencode
```

That's it. OpenCode reads `opencode.json`, `agents/` and `skills/` from
`~/.config/opencode`. Start OpenCode, or press `/reload` if it is already
running.

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
| `opencode.json` | Global config. Declares the ponytail plugin. |
| `agents/parallel-agent.md` | File-only agent used by `parallel-agents`. |
| `skills/` | Custom skills. One directory per skill, each with a `SKILL.md`. |
| `skills/parallel-agents/config.json` | Default cheap model for parallel runs. Not the global model. |

OpenCode already ships `docx`, `pdf`, `pptx`, `xlsx`, `skill-creator` and the
other built-in skills, so this repo does not duplicate them. It only adds what
OpenCode does not have.

## Skills

**Workflow**
- **`commit`** — one-thing, one-line conventional commits gated on the project's
  checks, including applying review feedback one item at a time.
- **`release`** — push, watch CI until green, write release notes.
- **`ui-polish`** — make a UI clean and obvious.

**Writing**
- **`write-docs`** — short, plain, purpose-first docs, plus keeping docs, plans
  and code aligned.
- **`explain-plainly`** — explain anything simply, with talking points and a
  learning path.
- **`humanize`** — rewrite reports and prose in my academic voice, with an ODT
  workflow that preserves citations and formatting.

**Delegation**
- **`parallel-agents`** — fan out cheap coding agents in parallel while you review.

**Visuals**
- **`drawio`** — diagrams, flowcharts, architecture, mockups, plus print posters
  and infographics, exported to `.drawio`, PNG, SVG or PDF.

`humanize` is distilled from the QorFinder FYP proposal and the Malaysian Economy
property-development report. The ODT scripts use only the Python standard
library.

`drawio` is adapted from [jgraph/drawio-mcp](https://github.com/jgraph/drawio-mcp)
(Apache 2.0, © 2025 JGraph Ltd) for OpenCode, Linux/macOS and Python helpers.
See `skills/drawio/LICENSE.txt` and `skills/drawio/NOTICE`.

## How to use it

Just ask in plain language. OpenCode loads a matching skill on its own. To force
one, mention it as `@skill-id` or by name.

Examples:

- "Commit this as one focused commit." → `commit`
- "Make an A1 conference poster about the project, portrait, and export a print PDF." → `drawio`
- "Turn these notes into a one-page infographic." → `drawio`
- "Draw the auth flow and export it as SVG." → `drawio`
- "Fan out these three independent tasks to the cheap model." → `parallel-agents`
- "Humanize this report in my voice." → `humanize`
- "Rewrite `~/Desktop/qorfinder/doc/23ACB05662_FYP1.odt` in my voice." → `humanize`

The ponytail plugin adds the `/ponytail`, `/ponytail-review`, `/ponytail-audit`,
`/ponytail-debt`, `/ponytail-gain` and `/ponytail-help` commands. It styles every
coding task, so use `/ponytail off` if you want it out of the way.

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

`humanize` rewrites in the voice distilled from the QorFinder FYP and the
Malaysian Economy report. It edits the report through a Markdown intermediate so
paragraph styles, bold/italic spans and citations survive.

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

Refresh the voice profile with more of your writing:

```bash
python3 ~/.config/opencode/skills/humanize/scripts/style_profile.py \
  report1.odt report2.odt
```

## parallel-agents (the big one)

You plan and review; cheap models write the code in parallel, so their output
never fills your context window. Write one brief per task, then launch:

```bash
~/.config/opencode/skills/parallel-agents/scripts/launch.sh \
  --repo /abs/path/to/repo --names topics,questions,import
```

Each agent writes its files and a `.agents/runs/<name>.done` marker. You review
the diffs, test, and commit. The default model is set in
`skills/parallel-agents/config.json`.

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
- `git`, `bash` and `python3`.
- Optional: draw.io Desktop for Mermaid conversion, layouts and image export.
- Optional: LibreOffice for `odt_verify.py --pdf` and for opening the results.

## License

MIT — see [LICENSE](LICENSE). The `drawio` skill is Apache 2.0; the rest is MIT.
Each skill keeps its own license file.
