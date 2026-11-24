---
name: drawio
description: >-
  Create or edit draw.io diagrams, mockups, posters and infographics; export to
  .drawio, PNG, SVG or PDF. Use for draw.io/.drawio, flowcharts, architecture,
  ER/sequence/class, wireframes, posters, infographics or visual summaries.
---

# drawio

Produce a native `.drawio`, then export or open it. Helpers live in
`<skill>/scripts`.

| Author as | Best for | Needs Desktop? |
|-----------|----------|----------------|
| **Mermaid** | flowcharts, sequence, class, state, ER, gantt, mindmap, timeline, C4, pie | yes, to convert |
| **XML** | posters, infographics, precise layouts, mockups, custom shapes | no, layout/export optional |

Prefer Mermaid for standard diagrams; XML where position, typography or print
size matters.

## Pipeline
1. **Author**
   - Mermaid: `drawio -x -f xml -o diagram.drawio diagram.mmd`; delete `.mmd`.
   - XML: write `diagram.drawio`; then
     `python3 <skill>/scripts/repair_drawio.py diagram.drawio`.
2. **Deliver**
   - default: keep `.drawio`; open it.
   - png/svg/pdf: `drawio -x -f pdf -e -b 10 -o diagram.drawio.pdf diagram.drawio`;
     delete the source.
   - url: keep `.drawio`; print the URL (below).
3. Open with `xdg-open` (Linux) or `open` (macOS), else print the path.

Always convert Mermaid to `.drawio` first; direct Mermaid → PNG with `-e` is
broken.

## CLI
Linux: `command -v drawio`. macOS: `command -v drawio`, else
`/Applications/draw.io.app/Contents/MacOS/drawio` or the same under
`~/Applications`, or Spotlight (`mdfind "kMDItemCFBundleIdentifier == 'com.jgraph.drawio.desktop'"`).
If absent, keep authoring XML and deliver `.drawio`/`url`; tell the user Desktop
enables Mermaid, layouts and exports.

## Layout XML
`drawio -x -f xml --layout verticalFlow -o diagram.drawio diagram.drawio`

Presets: `verticalFlow`, `horizontalFlow`, `verticalTree`, `horizontalTree`,
`radialTree`, `organic`; edges only: `libavoid`; custom ELK: JSON array starting
`[`. Mermaid is already laid out; don't add `--layout`.

## Output
- Names: lowercase-hyphenated (`login-flow`, `a1-poster`); exports use
  `name.drawio.png|svg|pdf`.
- `-e` embeds editable XML; `-b 10` border; `-s 2` scale; `--width/--height` fit;
  `--disable-gpu` for VMs.

## URL
`URL=$(python3 <skill>/scripts/drawio_url.py diagram.drawio)`, then
`xdg-open "$URL"` or `open "$URL"`. No desktop needed to view; very large
diagrams may exceed URL limits.

## XML
```xml
<mxGraphModel page="1" pageWidth="3179" pageHeight="4494" background="#ffffff" adaptiveColors="auto">
  <root><mxCell id="0"/><mxCell id="1" parent="0"/></root>
</mxGraphModel>
```
- No XML comments. Escape `&amp; &lt; &gt; &quot;`. Use unique ids.
- Every edge needs `<mxGeometry relative="1" as="geometry" />`.
- Container cells use `parent="<container-id>"` and relative coordinates.
- Run `repair_drawio.py` after writing: strips surrounding text, escapes
  attributes, fixes `<mxCell id="1" parent="1"/>`.
- Complex XML: fetch
  `https://raw.githubusercontent.com/jgraph/drawio-mcp/main/shared/xml-essentials.md`.

## Shapes
Don't guess `mxgraph.*`. Run
`python3 <skill>/scripts/find_shapes.py "aws4 lambda" "github"`; each line is
`title wxh style`; paste the style. Needs network.

## Posters and infographics
Plan format (A0–A4, 16:9, social 1080×1080/1350/1920), orientation, viewing
distance, one takeaway, and print PDF vs screen PNG/SVG. At 96 DPI: A0
3179×4494, A1 2245×3179, A2 1587×2245, A3 1123×1587, A4 794×1123; swap for
landscape; set `pageWidth/pageHeight`.

Layout: poster 3 columns (2 for A2/A3), margins 5–8% of the short edge, gutters
24–40 px; infographic 12 columns. Reading order: title → main message → 3–5
sections → conclusion/source. One idea per block; cut text before shrinking
type. Body ≥24–28 px on A1/A0; titles 2–3×; max 2 fonts and 3 sizes. One accent,
neutral and background plus data colors; WCAG AA. Use icons and simple charts;
every chart needs title, units and source. Conference poster: title, authors,
intro, methods, results, conclusion, QR/footer, logos; title readable at 3 m.
Print: 3 mm bleed, safe area, PDF, embedded images; PNG at print size with
`-s 2`.

Build: absolute coordinates; `rounded=0` cards, text cells, image cells;
`whiteSpace=wrap;html=1;`; explicit align/verticalAlign; group sections; export
`-e -b 0`; keep the source.

QA: squint test; no overflow/overlap/clipping; consistent margins/type/colors;
numbers/units/sources correct; PDF physical size or PNG pixel size correct.

## Troubleshooting
CLI absent → XML + `.drawio`/url. Mermaid→PNG crash → convert first. Blank →
root ids `0`/`1` + repair. Layout no-op → preset/JSON array; update Desktop. GPU
error → `--disable-gpu`. URL empty → keep `.drawio`; use the `#R` URL.

## Attribution
Adapted from [jgraph/drawio-mcp](https://github.com/jgraph/drawio-mcp)
(Apache 2.0, © 2025 JGraph Ltd): OpenCode/Linux/macOS, Python helpers, no
Windows/WSL, added poster guidance. See `LICENSE.txt` and `NOTICE`.
