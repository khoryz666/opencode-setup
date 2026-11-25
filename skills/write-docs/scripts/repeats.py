#!/usr/bin/env python3
"""Find sentences stated more than once across docs (keep one home, link the rest).

Usage: repeats.py DOC...
Compares sentences of 8+ words after lower-casing and dropping punctuation.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

from doctext import paragraphs

SENTENCE = re.compile(r"(?<=[.!?])\s+")


def repeats(docs: list[Path], min_words: int = 8) -> list[list[tuple[str, str]]]:
    seen = defaultdict(list)
    for doc in docs:
        for loc, text in paragraphs(doc):
            for s in SENTENCE.split(text):
                key = " ".join(re.sub(r"[^\w\s]", " ", s.lower()).split())
                if len(key.split()) >= min_words:
                    seen[key].append((loc, s))
    return [hits for hits in seen.values() if len(hits) > 1]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    groups = repeats([Path(a) for a in sys.argv[1:]])
    for hits in groups:
        print(hits[0][1][:120])
        print("".join(f"  {loc}\n" for loc, _ in hits))
    print(f"{len(groups)} repeated sentences" if groups else "no repeats")
