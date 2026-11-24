#!/usr/bin/env python3
"""Extract ODT paragraphs into an editable Markdown file plus metadata JSON.

Only blocks marked rewrite=yes should be rewritten. Formatting that differs
from the document's body style is represented as {{rN}}...{{/rN}} markers.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from odt_lib import prepare_blocks, read_odt, save_metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="source .odt")
    parser.add_argument("--out", type=Path, help="output directory (default: <name>.humanize)")
    args = parser.parse_args()

    source = args.input.expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"odt_extract: not a file: {source}")
    out_dir = (args.out or source.with_name(source.stem + ".humanize")).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    root, style_info = read_odt(source)
    blocks, base_style = prepare_blocks(root, style_info)

    markdown_path = out_dir / (source.stem + ".md")
    metadata_path = out_dir / "blocks.json"

    rewriteable = sum(1 for block in blocks if not block.readonly and not block.hidden)
    visible = [block for block in blocks if not block.hidden]
    hidden = len(blocks) - len(visible)

    lines = [
        "<!-- odt-humanize v1",
        f"source: {source}",
        f"base_style: {base_style or '(none)'}",
        "Rewrite only blocks with rewrite=yes. Keep block headers unchanged,",
        "keep {{rN}}...{{/rN}} markers, and keep each paragraph on one line.",
        "Do not edit rewrite=no blocks.",
        "-->",
        "",
    ]
    for block in visible:
        header = (
            f"<!-- block id={block.id} kind={block.kind} style={block.style or '-'} "
            f"rewrite={'no' if block.readonly else 'yes'} words={block.word_count} runs={len(block.runs)}"
        )
        if block.reason:
            header += f" reason={block.reason}"
        lines.append(header + " -->")
        lines.append(block.markdown)
        lines.append("")

    markdown_path.write_text("\n".join(lines), encoding="utf-8")
    save_metadata(
        metadata_path,
        {
            "source": str(source),
            "base_style": base_style,
            "blocks": [
                {
                    "id": block.id,
                    "kind": block.kind,
                    "style": block.style,
                    "text": block.text,
                    "markdown": block.markdown,
                    "runs": block.runs,
                    "wrap_style": block.wrap_style,
                    "readonly": block.readonly,
                    "hidden": block.hidden,
                    "reason": block.reason,
                    "word_count": block.word_count,
                    "in_table": block.in_table,
                    "in_toc": block.in_toc,
                    "in_textbox": block.in_textbox,
                }
                for block in blocks
            ],
        },
    )

    print(f"blocks: {len(blocks)} total, {rewriteable} rewriteable, {len(visible) - rewriteable} read-only, {hidden} hidden")
    print(f"base style: {base_style or '(none)'}")
    print(f"markdown: {markdown_path}")
    print(f"metadata: {metadata_path}")


if __name__ == "__main__":
    main()
