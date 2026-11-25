"""Write a .drawio file from Python with absolute coordinates (posters, infographics).

    d = Diagram("poster", 2245, 3179, font="Inter")
    title = d.text(80, 60, 2085, 160, "<b>Title</b>", size=96)
    a = d.box(80, 300, 600, 300, "Method", fill="#F5F5F5")
    b = d.box(760, 300, 600, 300, "Result")
    d.arrow(a, b, label="feeds")
    d.save("poster.drawio")

Every method returns the cell id; labels are HTML.
"""

from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from xml.sax.saxutils import quoteattr


class Diagram:
    def __init__(self, name: str, width: int, height: int, *, font: str = "Helvetica", color: str = "#000000"):
        self.name, self.width, self.height, self.font, self.color = name, width, height, font, color
        self.cells: list[str] = []

    def _add(self, attrs: str, geometry: str) -> str:
        cid = f"c{len(self.cells) + 2}"  # 0 and 1 are the root cells
        self.cells.append(f'<mxCell id="{cid}" {attrs}>{geometry}</mxCell>')
        return cid

    def _vertex(self, x, y, w, h, value: str, style: str) -> str:
        return self._add(f'value={quoteattr(value)} style={quoteattr(style)} vertex="1" parent="1"',
                         f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>')

    def box(self, x, y, w, h, html: str = "", *, fill="#ffffff", stroke="#000000", size=16, bold=False,
            align="center", valign="middle", rounded=True, dashed=False, color=None, font=None, extra="") -> str:
        return self._vertex(x, y, w, h, html,
                            f"rounded={int(rounded)};whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};"
                            f"fontFamily={font or self.font};fontSize={size};fontColor={color or self.color};"
                            f"fontStyle={int(bold)};align={align};verticalAlign={valign};dashed={int(dashed)};{extra}")

    def text(self, x, y, w, h, html: str, **kw) -> str:
        return self.box(x, y, w, h, html, **{"fill": "none", "stroke": "none", "rounded": False, **kw})

    def image(self, x, y, w, h, path: str | Path) -> str:
        """Embed a PNG/JPEG/SVG so the file stays self-contained."""
        mime = mimetypes.guess_type(str(path))[0] or "image/png"
        data = base64.b64encode(Path(path).read_bytes()).decode()
        return self._vertex(x, y, w, h, "", f"shape=image;aspect=fixed;imageAspect=0;image=data:{mime},{data};")

    def line(self, x1, y1, x2, y2, *, color="#cccccc", width=2, arrow=False) -> str:
        end = "block;endFill=1" if arrow else "none"
        return self._add(f'value="" style="endArrow={end};html=1;strokeColor={color};strokeWidth={width};" '
                         'edge="1" parent="1"',
                         f'<mxGeometry relative="1" as="geometry"><mxPoint x="{x1}" y="{y1}" as="sourcePoint"/>'
                         f'<mxPoint x="{x2}" y="{y2}" as="targetPoint"/></mxGeometry>')

    def arrow(self, source: str, target: str, *, label="", color="#000000", width=2, dashed=False,
              exit=None, entry=None) -> str:
        """Orthogonal connector; exit/entry are (x, y) fractions of the box, e.g. (1, 0.5) = right middle."""
        ports = (f"exitX={exit[0]};exitY={exit[1]};" if exit else "") + \
                (f"entryX={entry[0]};entryY={entry[1]};" if entry else "")
        style = (f"edgeStyle=orthogonalEdgeStyle;html=1;endArrow=block;endFill=1;strokeColor={color};"
                 f"strokeWidth={width};dashed={int(dashed)};fontFamily={self.font};fontColor={color};{ports}")
        return self._add(f'value={quoteattr(label)} style={quoteattr(style)} edge="1" parent="1" '
                         f'source="{source}" target="{target}"', '<mxGeometry relative="1" as="geometry"/>')

    def xml(self) -> str:
        return (f'<mxfile host="drawio"><diagram id={quoteattr(self.name)} name={quoteattr(self.name)}>'
                f'<mxGraphModel page="1" pageWidth="{self.width}" pageHeight="{self.height}" grid="1" gridSize="5">'
                f'<root><mxCell id="0"/><mxCell id="1" parent="0"/>{"".join(self.cells)}</root>'
                '</mxGraphModel></diagram></mxfile>')

    def save(self, path: str | Path) -> None:
        Path(path).write_text(self.xml(), encoding="utf-8")
