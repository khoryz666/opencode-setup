#!/usr/bin/env python3
"""List numbers in docs that no backing file contains, to trace or remove.

Usage: facts.py BACKING DOC...
BACKING is a file or directory of recorded results (text files are searched).
Skips citations, reference entries, URLs, DOIs, headings, section/table/figure
numbers, single digits and years. Decimals in BACKING also back their roundings.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from doctext import paragraphs

NUMBER = re.compile(r"(?<![\w.§@-])(\d{1,3}(?:,\d{3})+|\d+)((?:\.\d+)*)(?![\w.]*\w)%?")
LABEL = re.compile(r"(§|\b(?:Section|Sections|Table|Tables|Figure|Figures|Chapter|Equation|Appendix|"
                   r"FR|NFR|T|Q|A|v)\s*)$", re.I)
YEAR = re.compile(r"(19|20)\d\d")


def backing_numbers(root: Path) -> set[str]:
    """Every number in the backing files, also rounded to 0-4 decimals ("0.10436" backs "0.104")."""
    files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file()]
    out = set()
    for p in files:
        data = p.read_bytes() if p.stat().st_size < 20_000_000 else b"\0"
        if b"\0" in data[:4096]:
            continue
        for m in re.finditer(r"\d+(?:\.\d+)?", data.decode("utf-8", "replace").replace(",", "")):
            out.add(m.group(0))
            if "." in m.group(0):
                out.update(f"{float(m.group(0)):.{d}f}" for d in range(5))
    return out


def unbacked(backing: set[str], docs: list[Path]) -> list[str]:
    found = []
    for doc in docs:
        for loc, text in paragraphs(doc):
            if re.match(r"\[\d+\]", text):
                continue  # reference-list entry
            bare = re.sub(r"\[[\d,\s–-]+\]|\S*(?:://|doi:\s*|10\.\d{4,}/)\S*", " ", text)  # citations, URLs, DOIs
            for m in NUMBER.finditer(bare):
                whole, decimals = m.group(1).replace(",", ""), m.group(2)
                if decimals.count(".") > 1 or not bare[: m.start()].strip("# ") or LABEL.search(bare[: m.start()]):
                    continue  # section number, heading or label
                if not decimals and (int(whole) < 10 or YEAR.fullmatch(whole)):
                    continue
                if whole + decimals not in backing:
                    found.append(f"{loc}: {m.group(0)}  …{bare[max(0, m.start() - 50):m.end() + 30]}…")
    return found


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    hits = unbacked(backing_numbers(Path(sys.argv[1])), [Path(a) for a in sys.argv[2:]])
    print("\n".join(hits) or "every number is backed")
    sys.exit(1 if hits else 0)
