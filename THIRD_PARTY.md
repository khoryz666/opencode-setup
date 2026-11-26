# Third-party skills

Vendored so a fresh install needs nothing outside this repository.

| Skill | Source | Licence |
|-------|--------|---------|
| `docx` | Anthropic skills, synced Claude Code copy | Apache-2.0, `skills/docx/LICENSE.txt` |
| `pdf` | Anthropic skills, synced Claude Code copy | Apache-2.0, `skills/pdf/LICENSE.txt` |
| `pptx` | Anthropic skills, synced Claude Code copy | Apache-2.0, `skills/pptx/LICENSE.txt` |
| `xlsx` | Anthropic skills, synced Claude Code copy | Apache-2.0, `skills/xlsx/LICENSE.txt` |
| `skill-creator` | Anthropic skills, synced Claude Code copy | Apache-2.0, `skills/skill-creator/LICENSE.txt` |

Vendored 2026-11-26. Files are unmodified; each skill keeps its own `LICENSE.txt`.
Runtime packages (`docx`, `pptxgenjs`, `openpyxl`, `pypdf`, LibreOffice) are not
vendored and are installed on demand by the skills.

Deliberately not vendored:

- `docs`, `google-workspace`, `morning`, `import-memory`: depend on Claude
  connectors or MCP servers, and carry no redistribution licence.
- `built-in-browser`, `chrome-browser`, `computer-use`: need Claude desktop
  tools and are marked all rights reserved.
- `deep-research`: no licence; write an original skill if it is needed.

OpenCode's own skills (`opencode`, `report`, `browser`) ship with OpenCode and
are not copied here.
