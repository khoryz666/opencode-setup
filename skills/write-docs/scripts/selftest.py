#!/usr/bin/env python3
"""Self-test for facts.py and repeats.py on small Markdown and ODT files."""

from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path

from facts import backing_numbers, unbacked
from repeats import repeats

DOC = """# 3.1 Results
nDCG@10 rose to 0.419 on 34 queries, and 6,771 pairs were used (Table 4.2, Section 3.7.4) [12].
Latency was 87 ms in 2026, see https://example.org/records/4595826 and 2 runs.
The fine-tuned model is the default for every new index in the app.
[3] A. Author, “Paper,” 2020, pp. 1234–1240.
"""
ODT = ('<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
       'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"><office:body><office:text>'
       '<text:p>The fine-tuned model is the <text:span>default</text:span> for every new index in the app.</text:p>'
       '</office:text></office:body></office:document-content>')


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "results").mkdir()
        (tmp / "results" / "scores.tsv").write_text("ndcg\t0.41893\nqueries\t34\npairs\t6771\n")
        doc, odt = tmp / "README.md", tmp / "report.odt"
        doc.write_text(DOC)
        with zipfile.ZipFile(odt, "w") as z:
            z.writestr("content.xml", ODT)

        hits = unbacked(backing_numbers(tmp / "results"), [doc])
        assert len(hits) == 1 and ": 87 " in hits[0], hits  # 0.419 rounds from 0.41893; the rest are skipped

        groups = repeats([doc, odt])
        assert len(groups) == 1 and [loc for loc, _ in groups[0]] == [f"{doc}:4", f"{odt}#p1"], groups
    print("write-docs selftest ok")


if __name__ == "__main__":
    main()
