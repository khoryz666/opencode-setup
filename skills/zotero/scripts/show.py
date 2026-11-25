#!/usr/bin/env python3
"""Show Zotero items in full.

Usage: show.py KEY... | show.py --recent [MINUTES=60]
--recent lists what the user changed in the last MINUTES (Zotero stores UTC).
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone

import zotlib


def main(args: list[str], db=zotlib.DB) -> None:
    items = zotlib.load(zotlib.connect(db))
    if args[:1] == ["--recent"]:
        since = datetime.now(timezone.utc) - timedelta(minutes=float(args[1]) if len(args) > 1 else 60)
        keys = sorted((k for k, it in items.items() if it.modified >= since.strftime("%Y-%m-%d %H:%M:%S")),
                      key=lambda k: items[k].modified, reverse=True)
    else:
        keys = args
    for k in keys:
        print(zotlib.describe(items[k], items) if k in items else f"{k} not found", end="\n\n")
    if not keys:
        print("nothing")


if __name__ == "__main__":
    if not sys.argv[1:]:
        sys.exit(__doc__)
    main(sys.argv[1:])
