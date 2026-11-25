#!/usr/bin/env python3
"""Point at the voice-rule breaks in prose, block by block, to fix before applying.

Usage: tells.py report.odt | tells.py report.humanize/report.md
Checks the rewritable blocks for AI tells, banned connectives, em dashes,
exclamation marks, first person, contractions, "There is/are" openers and
sentences over 45 words. Exits 1 on findings.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from odt_lib import parse_block_markdown, prepare_blocks, read_odt, strip_markers
from style_profile import AI_TELLS, CONTRACTIONS, FIRST_PERSON, SENTENCE_SPLIT

BANNED = ["Moreover", "Furthermore", "Thus", "Hence", "In addition", "Additionally", "In conclusion"]
CHECKS = [(f"AI tell “{t}”", re.compile(rf"\b{re.escape(t)}\b", re.I)) for t in AI_TELLS] + [
    (f"connective “{c}”", re.compile(rf"\b{c}\b")) for c in BANNED] + [
    ("em dash", re.compile("—")), ("exclamation", re.compile(r"!(?!\[)")),
    ("first person", FIRST_PERSON), ("contraction", CONTRACTIONS),
    ("“There is/are” opener", re.compile(r"(?:^|(?<=[.!?]\s))There (?:is|are|was|were)\b"))]
LONG = 45


def blocks(path: Path) -> list[tuple[str, str, bool]]:
    """(id, text, rewritable) in document order, from the .odt or its extracted .md."""
    if path.suffix == ".odt":
        found, _ = prepare_blocks(*read_odt(path))
        return [(b.id, b.text, not b.readonly) for b in found if not b.hidden]
    md = path.read_text(encoding="utf-8")
    meta = {m.group(1): "rewrite=yes" in m.group(0) for m in re.finditer(r"<!-- block id=(\S+)[^>]*", md)}
    return [(i, strip_markers(t), meta.get(i, False)) for i, t in parse_block_markdown(path).items()]


def tells(path: Path) -> list[str]:
    found, heading = [], ""
    for block, text, rewritable in blocks(path):
        if block.startswith("h"):
            heading = text.lower()
        if not rewritable:
            continue
        for name, rx in CHECKS:
            if name == "first person" and "acknowledg" in heading:
                continue  # the one place "I" belongs
            for m in rx.finditer(text):
                found.append(f"{block}: {name}: …{text[max(0, m.start() - 40):m.end() + 40]}…")
        for sentence in SENTENCE_SPLIT.split(text):
            if (n := len(sentence.split())) > LONG:
                found.append(f"{block}: {n}-word sentence: {sentence[:80]}…")
    return found


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    hits = tells(Path(sys.argv[1]))
    print("\n".join(hits) or "no tells")
    sys.exit(1 if hits else 0)
