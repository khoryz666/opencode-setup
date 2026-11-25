#!/usr/bin/env python3
"""Insert one Zotero citation after an anchor in an ODT.

Usage: cite.py IN.odt OUT.odt ANCHOR KEY [KEY...]
ANCHOR is raw content.xml text that occurs exactly once; the citation goes right
after it as " [?]". Several keys make one citation. Then: Zotero > Refresh.
"""

from __future__ import annotations

import sys
from pathlib import Path

import zotlib


def cite(src: Path, dst: Path, anchor: str, keys: list[str], db: Path = zotlib.DB) -> None:
    con = zotlib.connect(db)
    items = zotlib.load(con)
    bad = [k for k in keys if k not in items or items[k].trashed or not items[k].regular]
    if bad:
        sys.exit(f"not citable (missing, trashed or not a regular item): {', '.join(bad)}")
    xml = zotlib.content(src)
    if (n := xml.count(anchor)) != 1:
        sys.exit(f"anchor occurs {n} times in content.xml; it must occur once")
    mark = zotlib.citation_mark([items[k] for k in keys], zotlib.user_key(con))
    zotlib.write_content(src, dst, xml.replace(anchor, f"{anchor} {mark}"))
    print(f"cited {', '.join(keys)} in {dst}")


if __name__ == "__main__":
    if len(sys.argv) < 5:
        sys.exit(__doc__)
    cite(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4:])
