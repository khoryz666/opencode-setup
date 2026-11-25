#!/usr/bin/env python3
"""Check a .drawio file before export.

Usage: lint_drawio.py FILE.drawio [MIN_FONT]
Reports duplicate ids, edges without geometry or with missing ends, cells
outside the page, and text below MIN_FONT px (default: 24 on A1 or larger, else
off). Exits 1 on findings.
"""

from __future__ import annotations

import base64
import html
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

A1_AREA = 2245 * 3179


def models(path: Path) -> list[tuple[str, ET.Element]]:
    root = ET.fromstring(path.read_text(encoding="utf-8"))
    if root.tag == "mxGraphModel":
        return [("page 1", root)]
    out = []
    for n, diagram in enumerate(root.iter("diagram"), 1):
        model = diagram.find("mxGraphModel")
        if model is None and (diagram.text or "").strip():  # compressed page
            raw = zlib.decompress(base64.b64decode(diagram.text.strip()), -15).decode()
            model = ET.fromstring(urllib.parse.unquote(raw))
        if model is not None:
            out.append((diagram.get("name") or f"page {n}", model))
    return out


def style(cell: ET.Element) -> dict[str, str]:
    return dict(p.split("=", 1) for p in (cell.get("style") or "").split(";") if "=" in p)


def lint(path: Path, min_font: float | None = None) -> list[str]:
    problems = []
    for page, model in models(path):
        width, height = float(model.get("pageWidth", 0)), float(model.get("pageHeight", 0))
        floor = min_font if min_font is not None else 24 if width * height >= A1_AREA else 0
        cells = list(model.iter("mxCell"))
        ids = [c.get("id") for c in cells]
        problems += [f"{page}: duplicate id {i}" for i in sorted({i for i in ids if ids.count(i) > 1})]
        known = set(ids)
        for c in cells:
            cid, geo = c.get("id"), c.find("mxGeometry")
            if c.get("edge") == "1":
                if geo is None:
                    problems.append(f"{page}: edge {cid} has no mxGeometry")
                for end in ("source", "target"):
                    if c.get(end) and c.get(end) not in known:
                        problems.append(f"{page}: edge {cid} {end} {c.get(end)} does not exist")
            if c.get("vertex") != "1" or geo is None or c.get("parent") not in ("1", None):
                continue  # children of containers use relative coordinates
            x, y = float(geo.get("x", 0)), float(geo.get("y", 0))
            w, h = float(geo.get("width", 0)), float(geo.get("height", 0))
            if width and height and (x < 0 or y < 0 or x + w > width or y + h > height):
                problems.append(f"{page}: {cid} at ({x:g}, {y:g}, {w:g}×{h:g}) is outside the {width:g}×{height:g} page")
            text = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", c.get("value") or "")).split())
            size = float(style(c).get("fontSize", 12))
            if text and size < floor:
                problems.append(f"{page}: {cid} font {size:g}px < {floor:g}px: {text[:40]!r}")
    return problems


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    found = lint(Path(sys.argv[1]), float(sys.argv[2]) if len(sys.argv) == 3 else None)
    print("\n".join(found) or "ok")
    sys.exit(1 if found else 0)
