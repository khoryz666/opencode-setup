#!/usr/bin/env python3
"""Compare an original ODT with a humanized copy.

Checks structure, read-only blocks and citation counts. Optional --pdf asks
LibreOffice to render the new file so it can be inspected visually.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path

from odt_lib import CITATION_RE, prepare_blocks, read_odt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("humanized", type=Path)
    parser.add_argument("--strict", action="store_true", help="exit non-zero on warnings")
    parser.add_argument("--pdf", action="store_true", help="render the new file to PDF with LibreOffice")
    args = parser.parse_args()

    original = args.original.expanduser().resolve()
    humanized = args.humanized.expanduser().resolve()
    original_root, original_styles = read_odt(original)
    humanized_root, humanized_styles = read_odt(humanized)
    original_blocks, _ = prepare_blocks(original_root, original_styles)
    humanized_blocks, _ = prepare_blocks(humanized_root, humanized_styles)

    original_by_id = {block.id: block for block in original_blocks}
    humanized_by_id = {block.id: block for block in humanized_blocks}
    errors: list[str] = []
    warnings: list[str] = []

    if set(original_by_id) != set(humanized_by_id):
        errors.append("the block structure changed (missing or extra paragraphs)")

    changed = 0
    unchanged = 0
    original_words = 0
    humanized_words = 0
    for block_id, before in original_by_id.items():
        after = humanized_by_id.get(block_id)
        if after is None:
            continue
        if before.hidden:
            if before.text != after.text:
                errors.append(f"{block_id}: hidden block changed")
            continue
        if before.readonly:
            if before.text != after.text:
                errors.append(f"{block_id}: read-only block changed")
            continue
        original_words += before.word_count
        humanized_words += after.word_count
        if before.text == after.text:
            unchanged += 1
            continue
        changed += 1
        before_citations = len(CITATION_RE.findall(before.text))
        after_citations = len(CITATION_RE.findall(after.text))
        if after_citations < before_citations:
            warnings.append(
                f"{block_id}: citations dropped ({before_citations} -> {after_citations})"
            )

    total_words = sum(block.word_count for block in original_blocks if not block.hidden)
    new_total_words = sum(block.word_count for block in humanized_blocks if not block.hidden)
    delta = 0.0 if total_words == 0 else (new_total_words - total_words) * 100 / total_words

    if args.pdf:
        soffice = shutil.which("soffice") or shutil.which("libreoffice")
        if soffice:
            subprocess.run(
                [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(humanized.parent), str(humanized)],
                check=False,
            )
        else:
            warnings.append("LibreOffice not found; PDF not rendered")

    print(f"blocks: {len(original_blocks)} total, {changed} changed, {unchanged} unchanged")
    print(f"words: {total_words} -> {new_total_words} ({delta:+.1f}%)")
    if warnings:
        print("warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    if errors:
        print("errors:")
        for error in errors:
            print(f"  - {error}")

    if errors or (args.strict and warnings):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
