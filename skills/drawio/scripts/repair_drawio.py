#!/usr/bin/env python3
"""Repair the mechanical slips that make draw.io reject a .drawio file.

Strips text around the diagram, escapes unescaped < and & in attribute values,
and fixes a default layer written as its own parent.
"""

import re
import sys
from pathlib import Path

DIAGRAM_RE = re.compile(r"<mxfile[\s\S]*?</mxfile>|<mxGraphModel[\s\S]*?</mxGraphModel>")
ATTR_RE = re.compile(r'="([^"]*)"')
BAD_AMP_RE = re.compile(r"&(?!(?:amp|lt|gt|quot|apos|#[0-9]+|#x[0-9a-fA-F]+);)")
SELF_PARENT_RE = re.compile(r'<mxCell id="([^"]+)" parent="\1"\s*/>')


def repair(xml: str) -> str:
    match = DIAGRAM_RE.search(xml)
    if match and xml.strip() != match.group(0):
        xml = match.group(0)

    def escape(match: re.Match) -> str:
        value = match.group(1).replace("<", "&lt;")
        value = BAD_AMP_RE.sub("&amp;", value)
        return f'="{value}"'

    xml = ATTR_RE.sub(escape, xml)
    return SELF_PARENT_RE.sub(r'<mxCell id="\1" parent="0"/>', xml)


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: repair_drawio.py FILE.drawio")
    path = Path(sys.argv[1])
    try:
        xml = path.read_text(encoding="utf-8")
    except OSError as error:
        sys.exit(f"repair_drawio: {error}")
    path.write_text(repair(xml), encoding="utf-8")


if __name__ == "__main__":
    main()
