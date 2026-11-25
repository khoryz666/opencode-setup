"""Read-only access to a local Zotero library and the Zotero citations in an ODT."""

from __future__ import annotations

import html
import json
import random
import re
import shutil
import sqlite3
import string
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

DB = Path.home() / "Zotero" / "zotero.sqlite"
TITLE_FIELDS = ("title", "nameOfAct", "caseName", "subject")
NOT_REGULAR = {"attachment", "note", "annotation"}
CSL_TYPE = {  # Zotero refreshes itemData from the library; this is only a fallback
    "journalArticle": "article-journal", "conferencePaper": "paper-conference", "book": "book",
    "bookSection": "chapter", "webpage": "webpage", "report": "report", "thesis": "thesis",
    "statute": "legislation", "computerProgram": "software", "preprint": "article", "dataset": "dataset",
}
MARK = re.compile(r'<text:reference-mark-start text:name="(ZOTERO_ITEM [^"]*)"/>(.*?)'
                  r'<text:reference-mark-end text:name="ZOTERO_ITEM [^"]*"/>', re.S)


@dataclass
class Item:
    id: int
    key: str
    type: str
    modified: str
    trashed: bool
    fields: dict[str, str] = field(default_factory=dict)
    creators: list[str] = field(default_factory=list)
    collections: list[str] = field(default_factory=list)  # paths, "Parent/Child"
    parent: str | None = None
    children: list[str] = field(default_factory=list)

    @property
    def title(self) -> str:
        return next((self.fields[f] for f in TITLE_FIELDS if f in self.fields), "")

    @property
    def regular(self) -> bool:
        return self.type not in NOT_REGULAR

    def under(self, root: str) -> bool:
        return any(c == root or c.startswith(root + "/") for c in self.collections)


def connect(db: Path = DB) -> sqlite3.Connection:
    """Open a copy (with its WAL), so the running Zotero is never touched."""
    tmp = Path(tempfile.mkdtemp(prefix="zotero-"))
    for suffix in ("", "-wal"):
        src = Path(str(db) + suffix)
        if src.exists():
            shutil.copy2(src, tmp / src.name)
    return sqlite3.connect(tmp / db.name)


def collection_paths(con: sqlite3.Connection) -> dict[int, str]:
    rows = {i: (n, p) for i, n, p in con.execute(
        "select collectionID, collectionName, parentCollectionID from collections")}

    def path(i: int) -> str:
        name, parent = rows[i]
        return f"{path(parent)}/{name}" if parent else name
    return {i: path(i) for i in rows}


def load(con: sqlite3.Connection) -> dict[str, Item]:
    """Every item by key, trashed ones included (check Item.trashed)."""
    items = {i: Item(i, k, t, m, bool(d)) for i, k, t, m, d in con.execute(
        "select itemID, key, typeName, dateModified, itemID in (select itemID from deletedItems)"
        " from items join itemTypes using(itemTypeID)")}
    for i, name, value in con.execute(
            "select itemID, fieldName, value from itemData join itemDataValues using(valueID)"
            " join fields using(fieldID)"):
        items[i].fields[name] = value
    for i, last, first, mode in con.execute(
            "select itemID, lastName, firstName, fieldMode from itemCreators"
            " join creators using(creatorID) order by itemID, orderIndex"):
        items[i].creators.append(last if mode == 1 or not first else f"{last}, {first}")
    paths = collection_paths(con)
    for c, i in con.execute("select collectionID, itemID from collectionItems"):
        items[i].collections.append(paths[c])
    for i, parent in con.execute("select itemID, parentItemID from itemAttachments where parentItemID is not null"):
        items[i].parent = items[parent].key
        items[parent].children.append(items[i].key)
    return {it.key: it for it in items.values()}


def user_key(con: sqlite3.Connection) -> str:
    return con.execute("select value from settings where setting='account' and key='localUserKey'").fetchone()[0]


def describe(it: Item, items: dict[str, Item]) -> str:
    lines = [f"{it.key} {it.type}{' TRASHED' if it.trashed else ''}  modified {it.modified}",
             *(f"  {k} = {v[:150]}" for k, v in it.fields.items() if k != "abstractNote"),
             f"  creators: {'; '.join(it.creators) or '-'}",
             f"  collections: {', '.join(it.collections) or '-'}"]
    if it.parent:
        lines.append(f"  parent: {it.parent} {items[it.parent].title}")
    lines += [f"  child: {c} {items[c].fields.get('title', '')}" for c in it.children]
    return "\n".join(lines)


# --- ODT citations -------------------------------------------------------

@dataclass
class Citation:
    keys: list[str]
    stored: str   # plainCitation Zotero last wrote
    visible: str  # text currently in the document


def _payload(name: str) -> dict:
    return json.loads(html.unescape(name).removeprefix("ZOTERO_ITEM CSL_CITATION ").rsplit(" RND", 1)[0])


def content(odt: Path) -> str:
    with zipfile.ZipFile(odt) as z:
        return z.read("content.xml").decode("utf-8")


def citations(xml: str) -> list[Citation]:
    out = []
    for name, body in MARK.findall(xml):
        p = _payload(name)
        out.append(Citation([c["uris"][0].rsplit("/", 1)[1] for c in p["citationItems"]],
                            p["properties"]["plainCitation"], html.unescape(re.sub(r"<[^>]+>", "", body))))
    return out


def bibliography(xml: str) -> dict | None:
    m = re.search(r'text:name="ZOTERO_BIBL ([^"]*) CSL_BIBLIOGRAPHY', xml)
    return json.loads(html.unescape(m.group(1))) if m else None


def citation_mark(items: list[Item], user: str) -> str:
    """A Zotero citation field showing [?] until Zotero > Refresh."""
    rnd = lambda n: "".join(random.choices(string.ascii_letters + string.digits, k=n))
    payload = {"citationID": rnd(8),
               "properties": {"formattedCitation": "[?]", "plainCitation": "[?]", "noteIndex": 0},
               "citationItems": [{"id": it.id, "uris": [f"http://zotero.org/users/local/{user}/items/{it.key}"],
                                  "itemData": {"id": it.id, "type": CSL_TYPE.get(it.type, "document"),
                                               "title": it.title}} for it in items],
               "schema": "https://github.com/citation-style-language/schema/raw/master/csl-citation.json"}
    name = html.escape(f"ZOTERO_ITEM CSL_CITATION {json.dumps(payload, ensure_ascii=False)} RND{rnd(10)}", quote=True)
    return f'<text:reference-mark-start text:name="{name}"/>[?]<text:reference-mark-end text:name="{name}"/>'


def write_content(src: Path, dst: Path, xml: str) -> None:
    """Copy src to dst with a new content.xml; entry order and compression kept (mimetype first, stored)."""
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, "w") as zout:
        for info in zin.infolist():
            data = xml.encode("utf-8") if info.filename == "content.xml" else zin.read(info.filename)
            zout.writestr(info, data, compress_type=info.compress_type)
