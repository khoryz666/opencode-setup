"""Shared ODT parsing and rewriting helpers for the humanize skill.

Standard library only. Paragraph IDs are document-order counters, so the
extract and apply scripts assign the same IDs as long as the document structure
is unchanged.
"""

from __future__ import annotations

import io
import json
import re
import zipfile
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
import xml.etree.ElementTree as ET

OFFICE = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
TEXT = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
STYLE = "urn:oasis:names:tc:opendocument:xmlns:style:1.0"
FO = "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
TABLE = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
XML = "http://www.w3.org/XML/1998/namespace"

NS = {"office": OFFICE, "text": TEXT, "style": STYLE, "fo": FO, "table": TABLE}
XML_SPACE = f"{{{XML}}}space"

UNSAFE = {
    "a",
    "note",
    "annotation",
    "bookmark-ref",
    "reference-ref",
    "sequence-ref",
    "frame",
    "image",
    "text-box",
}
HIDDEN_STYLES = ("reference", "bibliography", "contents", "cover", "header", "footer", "index")
MARKER_RE = re.compile(r"\{\{(/?)(r\d+|lb|rb)\}\}")
CITATION_RE = re.compile(r"\[\d+(?:\s*,\s*\d+)*\]|\([A-Z][^()]{0,80}?\d{4}[a-z]?\)")


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def q(namespace: str, name: str) -> str:
    return f"{{{NS[namespace]}}}{name}"


def style_name(element: ET.Element, attribute: str = "style-name") -> str:
    return element.get(q("text", attribute)) or ""


@dataclass
class Segment:
    text: str
    style: str | None


@dataclass
class Block:
    id: str
    kind: str
    style: str
    element: ET.Element
    in_table: bool = False
    in_toc: bool = False
    in_textbox: bool = False
    segments: list[Segment] = field(default_factory=list)
    text: str = ""
    runs: dict[str, dict[str, str]] = field(default_factory=dict)
    markdown: str = ""
    wrap_style: str | None = None
    line_breaks: int = 0
    tabs: int = 0
    readonly: bool = False
    hidden: bool = False
    reason: str = ""

    @property
    def word_count(self) -> int:
        return len(self.text.split())


def parse_xml(data: bytes) -> ET.Element:
    prefixes: list[tuple[str, str]] = []
    for _, pair in ET.iterparse(io.BytesIO(data), events=("start-ns",)):
        prefixes.append(pair)
    for prefix, uri in prefixes:
        try:
            ET.register_namespace(prefix, uri)
        except ValueError:
            pass
    return ET.fromstring(data)


def read_odt(path: Path) -> tuple[ET.Element, dict[str, dict[str, str]]]:
    with zipfile.ZipFile(path) as archive:
        content = parse_xml(archive.read("content.xml"))
        style_info = extract_style_info(content)
        try:
            styles = parse_xml(archive.read("styles.xml"))
        except KeyError:
            styles = None
        if styles is not None:
            style_info.update(extract_style_info(styles))
    return content, style_info


def extract_style_info(root: ET.Element) -> dict[str, dict[str, str]]:
    info: dict[str, dict[str, str]] = {}
    for style in root.iter(q("style", "style")):
        if style.get(q("style", "family")) != "text":
            continue
        name = style.get(q("style", "name"))
        if not name:
            continue
        props = style.find(q("style", "text-properties"))
        values: dict[str, str] = {}
        if props is not None:
            for key, namespace in (
                ("font-weight", "fo"),
                ("font-style", "fo"),
                ("color", "fo"),
                ("background-color", "fo"),
                ("text-underline-style", "style"),
            ):
                value = props.get(q(namespace, key))
                if value is not None:
                    values[key] = value
        info[name] = values
    return info


def is_emphasis(style: str, style_info: dict[str, dict[str, str]]) -> bool:
    """True when a text style changes more than the document's base font."""
    props = style_info.get(style)
    if props is None:
        return True
    bold = props.get("font-weight", "").lower() in {"bold", "600", "700", "800", "900"}
    italic = props.get("font-style", "").lower() == "italic"
    underline = props.get("text-underline-style", "") not in {"", "none"}
    color = props.get("color", "") not in {"", "#000000"}
    background = props.get("background-color", "") not in {"", "transparent"}
    return bold or italic or underline or color or background


def font_family(name: str) -> str:
    return re.sub(r"\d+$", "", name.strip().lower())


def same_style(
    style: str,
    base_style: str | None,
    style_info: dict[str, dict[str, str]],
) -> bool:
    if base_style is None or style == base_style:
        return style == base_style
    left = style_info.get(style)
    right = style_info.get(base_style)
    if left is None or right is None:
        return False
    left_font, right_font = font_family(left.get("font-name", "")), font_family(right.get("font-name", ""))
    if left_font and right_font and left_font != right_font:
        return False
    left_size, right_size = left.get("font-size", ""), right.get("font-size", "")
    if left_size and right_size and left_size != right_size:
        return False
    for key, default in (("font-weight", "normal"), ("font-style", "normal"), ("text-underline-style", "none")):
        if (left.get(key) or default).lower() != (right.get(key) or default).lower():
            return False
    for key, default in (("color", "#000000"), ("background-color", "transparent")):
        if (left.get(key) or default).lower() != (right.get(key) or default).lower():
            return False
    return True


def write_odt(source: Path, destination: Path, content: bytes) -> None:
    with zipfile.ZipFile(source) as archive_in, zipfile.ZipFile(destination, "w") as archive_out:
        for info in archive_in.infolist():
            data = content if info.filename == "content.xml" else archive_in.read(info.filename)
            entry = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            entry.compress_type = zipfile.ZIP_STORED if info.filename == "mimetype" else info.compress_type
            entry.external_attr = info.external_attr
            archive_out.writestr(entry, data)


def iter_block_elements(root: ET.Element) -> Iterable[tuple[ET.Element, bool, bool, bool]]:
    body = root.find(f".//{q('office', 'text')}")
    if body is None:
        return
    yield from _walk(body, False, False, False)


def _walk(element: ET.Element, in_table: bool, in_toc: bool, in_textbox: bool):
    for child in list(element):
        tag = local(child.tag)
        if tag in {"tracked-changes", "deletion", "format-change"}:
            continue
        if tag in {"p", "h"}:
            yield child, in_table, in_toc, in_textbox
        elif tag == "table":
            yield from _walk(child, True, in_toc, in_textbox)
        elif tag in {"table-of-content", "illustration-index", "table-index", "alphabetical-index", "user-index"}:
            yield from _walk(child, in_table, True, in_textbox)
        elif tag == "text-box":
            yield from _walk(child, in_table, in_toc, True)
        else:
            yield from _walk(child, in_table, in_toc, in_textbox)


def render_segments(element: ET.Element) -> tuple[list[Segment], list[str], int, int]:
    segments: list[Segment] = []
    unsafe: list[str] = []
    line_breaks = 0
    tabs = 0

    def add(text: str | None, style: str | None) -> None:
        if not text:
            return
        if segments and segments[-1].style == style:
            segments[-1].text += text
        else:
            segments.append(Segment(text, style))

    def walk(node: ET.Element, inherited: str | None) -> None:
        nonlocal line_breaks, tabs
        tag = local(node.tag)
        if tag in {"tracked-changes", "deletion", "format-change"}:
            return
        if tag == "span":
            style = node.get(q("text", "style-name")) or inherited
            add(node.text, style)
            for child in node:
                walk(child, style)
                add(child.tail, style)
            return
        if tag == "s":
            count = int(node.get(q("text", "c")) or 1)
            add(" " * count, inherited)
            return
        if tag == "tab":
            tabs += 1
            add(" ", inherited)
            return
        if tag == "line-break":
            line_breaks += 1
            add(" ", inherited)
            return
        if tag == "soft-page-break":
            return
        if tag == "note":
            unsafe.append(tag)
            return
        if tag in UNSAFE:
            unsafe.append(tag)
            add(node.text, inherited)
            for child in node:
                walk(child, inherited)
                add(child.tail, inherited)
            return
        add(node.text, inherited)
        for child in node:
            walk(child, inherited)
            add(child.tail, inherited)

    walk(element, None)
    return segments, unsafe, line_breaks, tabs


def looks_like_code(text: str, line_breaks: int) -> bool:
    signals = sum(text.count(char) for char in "{};")
    signals += text.count("=>") + text.count("pub fn") + text.count("let mut") + text.count("fn ")
    return line_breaks >= 3 or signals >= 4


def readonly_reason(block: Block) -> str:
    if block.hidden:
        return "hidden container"
    if block.kind == "h":
        return "heading"
    if block.in_textbox:
        return "text box"
    if block.element.find(f".//{q('text', 'note')}") is not None:
        return "footnote"
    if any(local(node.tag) in UNSAFE for node in block.element.iter()):
        return "link/frame/field"
    style = block.style.lower()
    if any(token in style for token in HIDDEN_STYLES):
        return "non-prose style"
    if len(block.text) < 160:
        return "too short"
    if re.match(r"^(Figure|Table|Note\.|Source:|Adapted from|List of)\b", block.text):
        return "caption/note"
    if re.match(r"^(Keywords?|Area of Study|Supervisor|Student ID|Course|Faculty)\b", block.text):
        return "metadata"
    if looks_like_code(block.text, block.line_breaks):
        return "code"
    return ""


def prepare_blocks(root: ET.Element, style_info: dict[str, dict[str, str]]) -> tuple[list[Block], str | None]:
    blocks: list[Block] = []
    counters = {"p": 0, "h": 0}
    for element, in_table, in_toc, in_textbox in iter_block_elements(root):
        kind = local(element.tag)
        counters[kind] += 1
        segments, unsafe, line_breaks, tabs = render_segments(element)
        raw_text = "".join(segment.text for segment in segments)
        text = re.sub(r"\s+", " ", raw_text).strip()
        block = Block(
            id=f"{kind}{counters[kind]:04d}",
            kind=kind,
            style=style_name(element),
            element=element,
            in_table=in_table,
            in_toc=in_toc,
            in_textbox=in_textbox,
            segments=segments,
            text=text,
            line_breaks=line_breaks,
            tabs=tabs,
        )
        block.hidden = in_table or in_toc or in_textbox or not text
        if unsafe:
            block.reason = "link/frame/field"
        blocks.append(block)

    style_chars: Counter[str | None] = Counter()
    for block in blocks:
        if block.hidden or block.reason:
            continue
        for segment in block.segments:
            if segment.style and not is_emphasis(segment.style, style_info):
                style_chars[segment.style] += len(segment.text)
    base_style = style_chars.most_common(1)[0][0] if style_chars else None

    for block in blocks:
        block.reason = readonly_reason(block)
        block.readonly = bool(block.reason)
        build_markdown(block, base_style, style_info)

    return blocks, base_style


def build_markdown(
    block: Block,
    base_style: str | None,
    style_info: dict[str, dict[str, str]],
) -> None:
    if block.readonly:
        block.markdown = block.text
        return

    nonempty = [(segment.text, segment.style) for segment in block.segments if segment.text.strip()]
    styles = {style for _, style in nonempty if style}
    if len(styles) == 1:
        style = next(iter(styles))
        if (
            not same_style(style, base_style, style_info)
            and all(style == segment_style for _, segment_style in nonempty)
        ):
            block.wrap_style = style
            block.markdown = escape_markers(block.text)
            return

    parts: list[str] = []
    runs: dict[str, dict[str, str]] = {}
    for segment in block.segments:
        if not segment.text:
            continue
        style = segment.style
        if not style or same_style(style, base_style, style_info) or not segment.text.strip():
            parts.append(escape_markers(segment.text))
            continue
        run_id = f"r{len(runs) + 1}"
        runs[run_id] = {"style": style, "text": segment.text}
        parts.append("{{" + run_id + "}}" + escape_markers(segment.text) + "{{/" + run_id + "}}")
    block.runs = runs
    block.markdown = re.sub(r"\s+", " ", "".join(parts)).strip()


def escape_markers(text: str) -> str:
    return text.replace("{{", "{{lb}}").replace("}}", "{{rb}}")


def unescape_markers(text: str) -> str:
    return text.replace("{{lb}}", "{").replace("{{rb}}", "}")


def strip_markers(text: str) -> str:
    return unescape_markers(MARKER_RE.sub("", text))


def parse_markers(text: str, runs: dict[str, dict[str, str]]) -> tuple[list[tuple[str, str | None]], list[str]]:
    segments: list[tuple[str, str | None]] = []
    used: list[str] = []
    stack: list[str] = []
    position = 0

    def add(value: str, run_id: str | None) -> None:
        if not value:
            return
        if segments and segments[-1][1] == run_id:
            segments[-1] = (segments[-1][0] + value, run_id)
        else:
            segments.append((value, run_id))

    for match in MARKER_RE.finditer(text):
        if match.start() > position:
            add(text[position : match.start()], stack[-1] if stack else None)
        closing, name = match.group(1), match.group(2)
        if name == "lb":
            add("{", stack[-1] if stack else None)
        elif name == "rb":
            add("}", stack[-1] if stack else None)
        elif closing:
            if not stack or stack[-1] != name:
                raise ValueError(f"unbalanced marker {{{{/{name}}}}}")
            stack.pop()
        else:
            if stack:
                raise ValueError(f"nested marker {{{{/{stack[-1]}}}}} / {{{{{name}}}}}")
            if name not in runs:
                raise ValueError(f"unknown marker {{{{{name}}}}}")
            stack.append(name)
            used.append(name)
        position = match.end()
    if position < len(text):
        add(text[position:], stack[-1] if stack else None)
    if stack:
        raise ValueError(f"unclosed marker {{{{{stack[-1]}}}}}")
    return segments, used


def replace_block_text(block: Block, text: str) -> None:
    if not text.strip():
        raise ValueError(f"{block.id}: rewritten paragraph is empty")
    segments, used = parse_markers(text, block.runs)
    element = block.element
    for child in list(element):
        element.remove(child)
    element.text = None
    element.set(XML_SPACE, "preserve")

    def append_text(value: str) -> None:
        if len(element):
            last = element[-1]
            last.tail = (last.tail or "") + value
        else:
            element.text = (element.text or "") + value

    if block.wrap_style:
        span = ET.SubElement(element, q("text", "span"))
        span.set(q("text", "style-name"), block.wrap_style)
        span.set(XML_SPACE, "preserve")
        span.text = text
        return

    for value, run_id in segments:
        if run_id:
            span = ET.SubElement(element, q("text", "span"))
            span.set(q("text", "style-name"), block.runs[run_id]["style"])
            span.set(XML_SPACE, "preserve")
            span.text = value
        else:
            append_text(value)

    missing = [run_id for run_id in block.runs if run_id not in used]
    if missing:
        details = ", ".join(
            f"{run_id}={block.runs[run_id]['text']!r}" for run_id in missing
        )
        raise ValueError(f"{block.id}: formatted text was dropped: {details}")


def serialize_content(root: ET.Element) -> bytes:
    return ET.tostring(root, encoding="UTF-8", xml_declaration=True)


def parse_block_markdown(path: Path) -> dict[str, str]:
    blocks: dict[str, str] = {}
    current: str | None = None
    lines: list[str] = []
    header = re.compile(r"^<!-- block (.*?) -->$")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = header.match(line)
        if match:
            if current is not None:
                blocks[current] = re.sub(r"\s+", " ", " ".join(lines)).strip()
            meta = dict(re.findall(r"(\w+)=(\S+)", match.group(1)))
            current = meta.get("id")
            if current is None:
                raise ValueError(f"block header without id: {line}")
            lines = []
        elif current is not None:
            lines.append(line)
    if current is not None:
        blocks[current] = re.sub(r"\s+", " ", " ".join(lines)).strip()
    return blocks


def load_metadata(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_metadata(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
