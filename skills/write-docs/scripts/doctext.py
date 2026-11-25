"""Paragraphs of a Markdown, text or ODT document, each with a location to cite."""

from __future__ import annotations

import html
import re
import zipfile
from pathlib import Path

PARA = re.compile(r"<text:(p|h)\b[^>]*>(.*?)</text:\1>", re.S)


def paragraphs(path: Path) -> list[tuple[str, str]]:
    """[(location, text)]: `file:line` for text files, `file#pN` (Nth paragraph) for .odt."""
    if path.suffix == ".odt":
        with zipfile.ZipFile(path) as z:
            xml = z.read("content.xml").decode("utf-8")
        xml = re.sub(r"<text:(s|tab)\b[^>]*/>", " ", xml)
        out = [(f"{path}#p{n}", " ".join(html.unescape(re.sub(r"<[^>]+>", "", body)).split()))
               for n, (_, body) in enumerate(PARA.findall(xml), 1)]
    else:
        out = [(f"{path}:{n}", line.strip())
               for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1)]
    return [(loc, text) for loc, text in out if text]
