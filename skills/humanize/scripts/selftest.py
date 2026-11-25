#!/usr/bin/env python3
"""End-to-end self-test for the ODT humanizer scripts."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

from tells import tells

HERE = Path(__file__).resolve().parent
TEXT_NS = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"

CONTENT = """<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
 xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
 xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
 xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
 xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
 office:version="1.3">
 <office:body><office:text>
  <text:h text:style-name="H1">Test heading</text:h>
  <text:p text:style-name="P1">This paragraph explains how the system indexes a folder of legal documents and why that matters to a small firm that searches its own files every day and reviews the result.</text:p>
  <text:p text:style-name="P1">It keeps <text:span text:style-name="T1">bold text</text:span> and a citation [1] inside a paragraph that is deliberately long enough to be treated as prose by the extractor and the checker, and then verifies that the rebuilt document still contains both of them.</text:p>
  <table:table table:name="Table1"><table:table-row><table:table-cell><text:p>table cell text</text:p></table:table-cell></table:table-row></table:table>
  <text:p text:style-name="P1">pub fn main() { let mut x = 1; x += 1; x += 2; x += 3; }</text:p>
 </office:text></office:body>
</office:document-content>
"""

STYLES = """<?xml version="1.0" encoding="UTF-8"?>
<office:document-styles
 xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
 xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
 xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
 office:version="1.3">
 <office:styles>
  <style:style style:name="P1" style:family="paragraph"/>
  <style:style style:name="H1" style:family="paragraph"/>
  <style:style style:name="T1" style:family="text">
   <style:text-properties fo:font-weight="bold"/>
  </style:style>
 </office:styles>
</office:document-styles>
"""

MANIFEST = """<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" manifest:version="1.3">
 <manifest:file-entry manifest:full-path="/" manifest:media-type="application/vnd.oasis.opendocument.text"/>
 <manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/>
 <manifest:file-entry manifest:full-path="styles.xml" manifest:media-type="text/xml"/>
</manifest:manifest>
"""


def make_odt(path: Path) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        mimetype = zipfile.ZipInfo("mimetype")
        mimetype.compress_type = zipfile.ZIP_STORED
        archive.writestr(mimetype, "application/vnd.oasis.opendocument.text")
        archive.writestr("content.xml", CONTENT)
        archive.writestr("styles.xml", STYLES)
        archive.writestr("META-INF/manifest.xml", MANIFEST)


def run(script: str, *args: str) -> None:
    subprocess.run([sys.executable, str(HERE / script), *args], check=True)


def text_of(element: ET.Element) -> str:
    return "".join(element.itertext())


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        original = root / "original.odt"
        make_odt(original)
        work = root / "work"
        run("odt_extract.py", str(original), "--out", str(work))

        markdown_path = work / "original.md"
        markdown = markdown_path.read_text(encoding="utf-8")
        assert "{{r1}}bold text{{/r1}}" in markdown
        assert "rewrite=no" in markdown
        assert "table cell text" not in markdown
        assert "This paragraph explains" in markdown

        markdown = markdown.replace(
            "This paragraph explains how the system indexes a folder of legal documents and why that matters to a small firm that searches its own files every day and reviews the result.",
            "The system indexes every legal document in the folder and returns the passage that matches the query, which matters to a small firm that searches its own files every day.",
        ).replace("It keeps", "It preserves")
        markdown_path.write_text(markdown, encoding="utf-8")
        assert tells(markdown_path) == []
        markdown_path.write_text(markdown.replace("It preserves", "Moreover, it preserves"), encoding="utf-8")
        assert [t.split(": ")[1] for t in tells(markdown_path)] == ["connective “Moreover”"], tells(markdown_path)
        markdown_path.write_text(markdown, encoding="utf-8")

        humanized = root / "humanized.odt"
        run(
            "odt_apply.py",
            str(original),
            str(markdown_path),
            str(work / "blocks.json"),
            "--out",
            str(humanized),
        )
        run("odt_verify.py", str(original), str(humanized))

        with zipfile.ZipFile(humanized) as archive:
            content = ET.fromstring(archive.read("content.xml"))
        paragraphs = [
            text_of(element)
            for element in content.iter(f"{TEXT_NS}p")
        ]
        assert any("The system indexes every legal document" in paragraph for paragraph in paragraphs)
        spans = [element for element in content.iter(f"{TEXT_NS}span")]
        assert any(
            text_of(span) == "bold text"
            and span.get(f"{TEXT_NS}style-name") == "T1"
            for span in spans
        )

        print("odt humanizer: ok")


if __name__ == "__main__":
    main()
