---
name: drawio
description: >-
  Create or edit draw.io diagrams and print/screen layouts: flowcharts,
  architecture and network diagrams, ER/sequence/class diagrams, mockups,
  wireframes, one-pagers, posters, infographics and flyers. Use when the user
  mentions draw.io/drawio/.drawio, asks for a diagram exported to PNG/SVG/PDF,
  or wants a poster, conference poster, infographic or visual summary laid out
  in draw.io.
---

# Draw.io diagrams, posters and infographics

Produce a native `.drawio` file, then export it to PNG/SVG/PDF or open it in the
draw.io editor. Helper scripts live in this skill's `scripts/` directory;
`<skill>` below is that directory (the skill tool prints its absolute path).

## 1. Pick the authoring format

| Author as | Best for | Needs draw.io Desktop? |
|-----------|----------|------------------------|
| **Mermaid** | Flowcharts, sequence, class, state, ER, gantt, mindmap, timeline, C4, pie | Yes, to convert to `.drawio` |
| **XML** | Posters, infographics, precise layouts, mockups, custom shapes, no desktop app | No (optional layout/export needs it) |

Prefer Mermaid for standard diagrams. Use XML for anything where position,
typography or print size matters: posters, infographics, dashboards, wireframes.

## 2. The pipeline

1. **Author**
   - Mermaid: write `diagram.mmd`, then
     ```bash
     drawio -x -f xml -o diagram.drawio diagram.mmd
     ```
     Delete the `.mmd`; the `.drawio` is the artifact.
   - XML: write `diagram.drawio` directly, then repair it:
     ```bash
     python3 <skill>/scripts/repair_drawio.py diagram.drawio
     ```
2. **Deliver**
   - No format asked: keep `diagram.drawio` and open it.
   - `png` / `svg` / `pdf`: export with embedded XML, then delete the source:
     ```bash
     drawio -x -f pdf -e -b 10 -o diagram.drawio.pdf diagram.drawio
     ```
   - `url`: keep the `.drawio` and open a browser link (see §6).
3. **Open the result** with `xdg-open` (Linux) or `open` (macOS), or print the
   absolute path if no opener works.

Always convert Mermaid to `.drawio` first, then export. Direct Mermaid → PNG
with `-e` is broken in current draw.io Desktop.

## 3. Find the CLI

Linux:

```bash
command -v drawio
```

macOS:

```bash
{ command -v drawio; ls /Applications/draw.io.app/Contents/MacOS/drawio \
    ~/Applications/draw.io.app/Contents/MacOS/drawio 2>/dev/null
  mdfind "kMDItemCFBundleIdentifier == 'com.jgraph.drawio.desktop'" \
    | sed 's|$|/Contents/MacOS/drawio|'; } 2>/dev/null | head -1
```

If the CLI is absent, keep authoring XML and deliver `.drawio` or `url`. Tell the
user that installing the draw.io desktop app enables Mermaid conversion, layouts
and image export.

## 4. Layout XML diagrams

Generate approximate positions and let the CLI lay them out:

```bash
drawio -x -f xml --layout verticalFlow -o diagram.drawio diagram.drawio
```

Presets: `verticalFlow`, `horizontalFlow`, `verticalTree`, `horizontalTree`,
`radialTree`, `organic`. For edge-only orthogonal routing use
`--layout libavoid`. For a custom ELK layout pass a JSON array starting with `[`:

```bash
drawio -x -f xml --layout '[{"layout":"elkLayered","config":{"elk.direction":"RIGHT"}}]' \
  -o diagram.drawio diagram.drawio
```

Mermaid output is already laid out; do not add `--layout` to it.

## 5. Output, naming and export flags

- Names: lowercase, hyphenated, content-based (`login-flow`, `a1-poster`).
- Exports use double extensions: `name.drawio.png`, `name.drawio.svg`,
  `name.drawio.pdf`.
- Use `-e` (`--embed-diagram`) for PNG/SVG/PDF so the file stays editable.
- `-b 10` adds a 10 px border.
- `-s 2` scales; `--width` / `--height` fit a target size.
- `--disable-gpu` fixes `GPU process isn't usable` on VMs and remote desktops.

## 6. Browser URL

Keep the `.drawio` file and print a URL that opens it in draw.io:

```bash
URL=$(python3 <skill>/scripts/drawio_url.py diagram.drawio)
xdg-open "$URL"      # Linux
open "$URL"          # macOS
```

No desktop app is needed to view the URL. Very large diagrams can exceed the
browser URL limit; open the `.drawio` locally instead.

## 7. XML rules and repair

Minimum structure:

```xml
<mxGraphModel page="1" pageWidth="3179" pageHeight="4494" background="#ffffff" adaptiveColors="auto">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
  </root>
</mxGraphModel>
```

- Never emit XML comments (`<!-- -->`).
- Escape `&amp;`, `&lt;`, `&gt;`, `&quot;` in attribute values.
- Every cell needs a unique `id`; every edge needs a child
  `<mxGeometry relative="1" as="geometry" />`.
- Cells inside a container use `parent="<container-id>"` and relative coordinates.
- Run `repair_drawio.py` after writing; it strips text around the diagram,
  escapes attributes and fixes `<mxCell id="1" parent="1"/>`.

The condensed upstream reference is useful before a complex XML diagram:
<https://raw.githubusercontent.com/jgraph/drawio-mcp/main/shared/xml-essentials.md>.

## 8. Shapes and icons

Do not guess `mxgraph.*` names. Look up cloud, network, brand and concept icons:

```bash
python3 <skill>/scripts/find_shapes.py "aws4 lambda" "github" "slack"
```

Each line is `title widthxheight style`; paste the style into a cell. The script
searches draw.io's shape libraries and icon service and needs network access.

## 9. Posters and infographics

Treat these as designed print/screen layouts, not enlarged diagrams.

### Plan first
Confirm or infer:
- **Format**: A0/A1/A2/A3/A4, 16:9 slide, or social (1080×1080, 1080×1350,
  1080×1920).
- **Orientation** and **viewing distance** (conference poster: 1–3 m; phone:
  30 cm).
- **One main takeaway** the viewer should remember.
- **Output**: print PDF (vector) or screen PNG/SVG.

At 96 DPI use: A0 3179×4494, A1 2245×3179, A2 1587×2245, A3 1123×1587,
A4 794×1123. Swap width/height for landscape. Put the size in `pageWidth` and
`pageHeight`.

### Layout
- Poster: 3-column grid (or 2 for A2/A3), margins 5–8% of the short edge,
  gutters 24–40 px, generous whitespace.
- Infographic: 12-column grid; one section per row; align every block.
- Reading order: title → main message → 3–5 sections → conclusion/source. On a
  poster, left-to-right, top-to-bottom.
- One idea per block. Use 3–5 sections maximum; cut text before shrinking type.
- Body text at least 24–28 px on A1/A0 (about 9–11 pt at print size); titles
  2–3× body. Use at most two font families and three sizes.
- Palette: one accent, one dark neutral, one light background, plus data colors.
  Check contrast (WCAG AA for screen).
- Use icons and simple charts instead of paragraphs. Every chart needs a title,
  units and a source line.
- Conference poster: title, authors/affiliation, intro, methods, results
  (chart/table), conclusion, QR/footer, logos. Keep the title readable from 3 m.
- Print: 3 mm bleed, all text inside the safe area, PDF export, embedded images.
  For PNG at print size use `-s 2` and check the pixel dimensions.

### Build in drawio XML
- Use absolute coordinates on the page; drawio does not auto-layout poster text.
- Use `rounded=0` rectangles for section cards, `text` cells for headings, and
  `shape=image` cells for icons and logos.
- Set `whiteSpace=wrap;html=1;` on text; set `align`/`verticalAlign` explicitly.
- Group each section (container) so moving it moves its children.
- Export PDF with `-e -b 0`; keep the `.drawio` source.

### QA checklist
- Squint test: the title and main message still read at a glance.
- No text overflow, overlap or clipped icons.
- Consistent margins, gutters, type sizes and colors.
- Numbers, units, dates and sources are correct.
- Print PDF is the requested physical size; screen export is the requested
  pixel size.

## 10. Troubleshooting

| Problem | Fix |
|---------|-----|
| CLI not found | Work through §3; keep XML authoring and deliver `.drawio`/`url` |
| Mermaid → PNG crashes | Convert to `.drawio` first (`-f xml`), then export |
| Blank diagram | Check root cells `id="0"` and `id="1"`; run the repair script |
| Layout does nothing | Use a preset or a JSON array starting with `[`; update Desktop |
| `GPU process isn't usable` | Add `--disable-gpu` |
| URL opens empty | Keep the `.drawio` local and use the printed `#R...` URL |

## Attribution

Adapted from [jgraph/drawio-mcp](https://github.com/jgraph/drawio-mcp)
(Apache 2.0, Copyright 2025 JGraph Ltd). Changes: OpenCode/Linux/macOS focused,
Node.js helpers replaced with Python, Windows/WSL instructions removed, and
poster/infographic guidance added. See `LICENSE.txt` and `NOTICE`.
