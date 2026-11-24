#!/usr/bin/env python3
"""Print a writing-style profile from ODT reports.

Run it on your own reports to refresh the voice profile in SKILL.md. It only
reads prose blocks that the ODT extractor would be willing to rewrite.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import statistics
from pathlib import Path

from odt_lib import CITATION_RE, prepare_blocks, read_odt

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z“\"(])")
FIRST_PERSON = re.compile(r"\b(I|we|our|us|my)\b")
CONTRACTIONS = re.compile(r"\b\w+'(?:t|re|ve|ll|d|m)\b", re.IGNORECASE)
CONNECTIVES = {
    "however": r"\bHowever\b",
    "therefore": r"\bTherefore\b",
    "moreover": r"\bMoreover\b",
    "furthermore": r"\bFurthermore\b",
    "thus": r"\bThus\b",
    "hence": r"\bHence\b",
    "in addition": r"\bIn addition\b",
    "overall": r"\bOverall\b",
    "for example": r"\bFor example\b",
    "first": r"\bFirst\b",
    "second": r"\bSecond\b",
    "third": r"\bThird\b",
}
AI_TELLS = [
    "delve", "leverage", "robust", "seamless", "pivotal", "crucial", "vital",
    "comprehensive", "holistic", "multifaceted", "landscape", "realm", "tapestry",
    "navigate", "foster", "facilitate", "utilize", "not only", "serves as",
    "plays a", "underscores", "highlights", "paving the way", "game-changer",
    "cutting-edge", "revolutionary", "unprecedented", "in today's",
    "it is important to note", "it is worth noting", "in conclusion",
]


def profile(paths: list[Path], min_words: int) -> dict:
    paragraphs: list[str] = []
    for path in paths:
        root, styles = read_odt(path)
        blocks, _ = prepare_blocks(root, styles)
        paragraphs.extend(
            block.text
            for block in blocks
            if not block.hidden and not block.readonly and block.word_count >= min_words
        )

    text = " ".join(paragraphs)
    sentences = [
        sentence.strip()
        for paragraph in paragraphs
        for sentence in SENTENCE_SPLIT.split(paragraph)
        if len(sentence.split()) >= 4
    ]
    lengths = [len(sentence.split()) for sentence in sentences]
    starters = collections.Counter(" ".join(sentence.split()[:2]) for sentence in sentences)

    def count(pattern: str) -> int:
        return len(re.findall(pattern, text, flags=re.IGNORECASE))

    return {
        "files": [str(path) for path in paths],
        "paragraphs": len(paragraphs),
        "sentences": len(sentences),
        "words": len(text.split()),
        "sentence_length": {
            "mean": round(statistics.mean(lengths), 1) if lengths else 0,
            "median": statistics.median(lengths) if lengths else 0,
            "p10": round(statistics.quantiles(lengths, n=10)[0], 1) if len(lengths) >= 10 else 0,
            "p90": round(statistics.quantiles(lengths, n=10)[8], 1) if len(lengths) >= 10 else 0,
        },
        "first_person": count(FIRST_PERSON.pattern),
        "contractions": count(CONTRACTIONS.pattern),
        "punctuation": {
            "semicolons": text.count(";"),
            "colons": text.count(":"),
            "parentheses": text.count("("),
            "em_dashes": text.count("—"),
            "en_dashes": text.count("–"),
        },
        "connectives": {name: count(pattern) for name, pattern in CONNECTIVES.items()},
        "ai_tells": {
            tell: len(re.findall(re.escape(tell), text, flags=re.IGNORECASE))
            for tell in AI_TELLS
        },
        "citations": len(CITATION_RE.findall(text)),
        "common_starters": starters.most_common(10),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path, help="one or more .odt reports")
    parser.add_argument("--min-words", type=int, default=20, help="ignore shorter paragraphs")
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    args = parser.parse_args()

    data = profile([path.expanduser().resolve() for path in args.files], args.min_words)
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    print(f"paragraphs: {data['paragraphs']}, sentences: {data['sentences']}, words: {data['words']}")
    lengths = data["sentence_length"]
    print(f"sentence length: mean {lengths['mean']}, median {lengths['median']}, p10 {lengths['p10']}, p90 {lengths['p90']}")
    print(f"first person: {data['first_person']}, contractions: {data['contractions']}, citations: {data['citations']}")
    punctuation = ", ".join(f"{key} {value}" for key, value in data["punctuation"].items())
    print(f"punctuation: {punctuation}")
    connectives = ", ".join(f"{key} {value}" for key, value in data["connectives"].items())
    print(f"connectives: {connectives}")
    tells = ", ".join(f"{key} {value}" for key, value in data["ai_tells"].items() if value)
    print(f"AI tells: {tells or 'none'}")
    starters = ", ".join(f"{phrase} ({count})" for phrase, count in data["common_starters"])
    print(f"common starters: {starters}")


if __name__ == "__main__":
    main()
