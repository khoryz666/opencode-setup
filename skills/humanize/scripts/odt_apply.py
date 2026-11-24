#!/usr/bin/env python3
"""Apply an edited humanize Markdown file back into a new ODT.

The original file is never modified. Formatting spans referenced by
{{rN}}...{{/rN}} markers are rebuilt with their original character styles.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from odt_lib import (
    load_metadata,
    parse_block_markdown,
    prepare_blocks,
    read_odt,
    replace_block_text,
    serialize_content,
    strip_markers,
    write_odt,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="original .odt")
    parser.add_argument("markdown", type=Path, help="edited Markdown from odt_extract.py")
    parser.add_argument("metadata", type=Path, help="blocks.json from odt_extract.py")
    parser.add_argument("--out", type=Path, help="output .odt (default: <name>.humanized.odt)")
    args = parser.parse_args()

    source = args.input.expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"odt_apply: not a file: {source}")
    if args.out is None:
        destination = source.with_name(source.stem + ".humanized.odt")
    else:
        destination = args.out.expanduser().resolve()
        if destination.is_dir():
            destination = destination / (source.stem + ".humanized.odt")
    if destination == source:
        raise SystemExit("odt_apply: refusing to overwrite the original file")

    metadata = load_metadata(args.metadata.expanduser().resolve())
    edited_blocks = parse_block_markdown(args.markdown.expanduser().resolve())
    meta_by_id = {block["id"]: block for block in metadata["blocks"]}

    root, style_info = read_odt(source)
    blocks, _ = prepare_blocks(root, style_info)
    block_by_id = {block.id: block for block in blocks}

    unknown = sorted(set(edited_blocks) - set(meta_by_id))
    if unknown:
        raise SystemExit(f"odt_apply: unknown block id(s) in Markdown: {', '.join(unknown)}")

    changed = 0
    unchanged = 0
    skipped = 0
    for block_id, meta in meta_by_id.items():
        block = block_by_id.get(block_id)
        if block is None:
            raise SystemExit(f"odt_apply: block {block_id} is missing from the ODT")
        if meta["hidden"]:
            continue
        if block_id not in edited_blocks:
            if meta["readonly"]:
                continue
            raise SystemExit(f"odt_apply: rewrite block {block_id} is missing from the Markdown")
        edited = edited_blocks[block_id]
        if meta["readonly"]:
            original = re.sub(r"\s+", " ", strip_markers(edited)).strip()
            if original != meta["text"]:
                raise SystemExit(f"odt_apply: read-only block {block_id} was edited")
            skipped += 1
            continue
        if edited == meta["markdown"]:
            unchanged += 1
            continue
        block.runs = meta["runs"]
        block.wrap_style = meta["wrap_style"]
        try:
            replace_block_text(block, edited)
        except ValueError as error:
            raise SystemExit(f"odt_apply: {error}") from error
        changed += 1

    write_odt(source, destination, serialize_content(root))
    print(f"changed: {changed}, unchanged: {unchanged}, read-only: {skipped}")
    print(f"output: {destination}")


if __name__ == "__main__":
    main()
