#!/usr/bin/env python3
"""Compare a report's Zotero citations with a collection subtree.

Usage: audit.py REPORT.odt COLLECTION [ZOTERO_DB]
Exits 1 if anything is missing, redundant, unrefreshed or duplicated.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

import zotlib


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def audit(odt: Path, root: str, db: Path = zotlib.DB) -> list[str]:
    items = zotlib.load(zotlib.connect(db))
    xml = zotlib.content(odt)
    cites = zotlib.citations(xml)
    cited = {k for c in cites for k in c.keys}
    filed = {k: it for k, it in items.items() if it.regular and not it.trashed and it.under(root)}
    label = lambda k: f"{k} {items[k].title if k in items else '(not in library)'}"
    problems = []

    for k in sorted(cited - filed.keys()):
        why = "not in library" if k not in items else "trashed" if items[k].trashed else \
            f"in {', '.join(items[k].collections) or 'no collection'}"
        problems.append(f"missing: {label(k)} [{why}]")
    problems += [f"redundant (uncited): {label(k)}" for k in sorted(filed.keys() - cited)]
    problems += [f"in root, not a subcollection: {label(k)}" for k, it in filed.items() if root in it.collections]
    problems += [f"unrefreshed citation: {c.visible!r} ({', '.join(c.keys)})"
                 for c in cites if c.visible != c.stored or "?" in c.visible]
    bib = zotlib.bibliography(xml)
    if bib is None:
        problems.append("no Zotero bibliography in the document")
    elif any(bib.get(k) for k in ("uncited", "custom")):
        problems.append(f"bibliography has manual entries: {bib}")

    groups = defaultdict(set)
    for k, it in filed.items():
        for name, value in (("title", norm(it.title)), ("DOI", it.fields.get("DOI", "").lower()),
                            ("ISBN", re.sub(r"\D", "", it.fields.get("ISBN", "")))):
            if value:
                groups[(name, value)].add(k)
    for (name, _), keys in groups.items():
        if len(keys) > 1:
            problems.append(f"duplicate {name}: " + " | ".join(label(k) for k in sorted(keys)))

    problems += [f"loose {it.type} (no parent): {label(k)}" for k, it in items.items()
                 if not it.regular and not it.parent and not it.trashed and it.under(root)]

    notes = [f"filed twice: {label(k)} in {', '.join(it.collections)}"
             for k, it in filed.items() if len(it.collections) > 1]
    print(f"{len(filed)} items under {root}, {len(cited)} cited, {len(cites)} citation fields")
    print("\n".join(problems + notes) or "no problems")
    return problems


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        sys.exit(__doc__)
    sys.exit(1 if audit(Path(sys.argv[1]), sys.argv[2], *map(Path, sys.argv[3:])) else 0)
