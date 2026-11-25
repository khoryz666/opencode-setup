#!/usr/bin/env python3
"""Self-test: audit and cite against a fake Zotero library and report."""

from __future__ import annotations

import contextlib
import io
import re
import sqlite3
import tempfile
import zipfile
from pathlib import Path

import audit
import cite
import zotlib

SCHEMA = """
create table itemTypes (itemTypeID integer primary key, typeName text);
create table items (itemID integer primary key, itemTypeID int, dateModified text, key text);
create table fields (fieldID integer primary key, fieldName text);
create table itemDataValues (valueID integer primary key, value);
create table itemData (itemID int, fieldID int, valueID int);
create table creators (creatorID integer primary key, firstName text, lastName text, fieldMode int);
create table itemCreators (itemID int, creatorID int, orderIndex int);
create table collections (collectionID integer primary key, collectionName text, parentCollectionID int);
create table collectionItems (collectionID int, itemID int);
create table deletedItems (itemID integer primary key);
create table itemAttachments (itemID integer primary key, parentItemID int);
create table settings (setting text, key text, value);
insert into settings values ('account', 'localUserKey', 'USER');
insert into itemTypes values (1, 'book'), (2, 'webpage'), (3, 'attachment');
insert into fields values (1, 'title');
insert into collections values (1, 'Thesis', null), (2, 'Ch2', 1), (3, 'Other', null);
"""
# key, type, title, collection, trashed, parent
ITEMS = [("CITED001", 1, "Cited Book", 2, 0, None),
         ("UNCITED1", 2, "Uncited Page", 2, 0, None),
         ("DUPE0001", 1, "Cited  book!", 2, 0, None),   # same normalised title as CITED001
         ("ROOT0001", 2, "Root Page", 1, 0, None),
         ("TRASHED1", 1, "Trashed Book", 2, 1, None),
         ("ELSEWHR1", 1, "Elsewhere", 3, 0, None),
         ("PDF00001", 3, "file.pdf", None, 0, "CITED001")]

CONTENT = ('<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
           'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"><office:body><office:text>'
           '<text:p>Claim one{c1}. Claim two{c2}. Anchor here.</text:p>'
           '<text:section text:name="ZOTERO_BIBL {{&quot;uncited&quot;:[],&quot;omitted&quot;:[],&quot;custom&quot;:[]}}'
           ' CSL_BIBLIOGRAPHY RNDx"/></office:text></office:body></office:document-content>')


def make_db(path: Path) -> None:
    con = sqlite3.connect(path)
    con.executescript(SCHEMA)
    ids = {}
    for n, (key, type_, title, col, trashed, parent) in enumerate(ITEMS, 1):
        ids[key] = n
        con.execute("insert into items values (?, ?, '2026-01-01 00:00:00', ?)", (n, type_, key))
        con.execute("insert into itemDataValues values (?, ?)", (n, title))
        con.execute("insert into itemData values (?, 1, ?)", (n, n))
        if col:
            con.execute("insert into collectionItems values (?, ?)", (col, n))
        if trashed:
            con.execute("insert into deletedItems values (?)", (n,))
        if type_ == 3:
            con.execute("insert into itemAttachments values (?, ?)", (n, ids.get(parent)))
    con.execute("insert into creators values (1, null, 'Some Org', 1)")
    con.execute("insert into itemCreators values (1, 1, 0)")
    con.commit()


def make_odt(path: Path, items: dict) -> None:
    mark = lambda k: " " + zotlib.citation_mark([items[k]], "USER").replace("[?]", "[1]").replace(
        "&quot;[?]&quot;", "&quot;[1]&quot;")
    with zipfile.ZipFile(path, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/vnd.oasis.opendocument.text")
        z.writestr("content.xml", CONTENT.format(c1=mark("CITED001"), c2=mark("ROOT0001")))


def quiet(fn, *args):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        db, odt, out = tmp / "zotero.sqlite", tmp / "r.odt", tmp / "out.odt"
        make_db(db)
        items = zotlib.load(zotlib.connect(db))
        assert items["CITED001"].creators == ["Some Org"] and items["CITED001"].children == ["PDF00001"]
        assert items["DUPE0001"].collections == ["Thesis/Ch2"] and items["TRASHED1"].trashed
        make_odt(odt, items)

        problems = quiet(audit.audit, odt, "Thesis", db)
        joined = "\n".join(problems)
        for expect in ("redundant (uncited): UNCITED1", "redundant (uncited): DUPE0001",
                       "in root, not a subcollection: ROOT0001", "duplicate title: CITED001"):
            assert expect in joined, (expect, joined)
        assert "TRASHED1" not in joined and "ELSEWHR1" not in joined and "unrefreshed" not in joined
        assert "loose" not in joined  # the PDF has a parent

        quiet(cite.cite, odt, out, "Anchor here", ["UNCITED1", "ELSEWHR1"], db)
        with zipfile.ZipFile(out) as z:
            assert z.infolist()[0].filename == "mimetype"
        xml = zotlib.content(out)
        c = zotlib.citations(xml)[-1]
        assert c.keys == ["UNCITED1", "ELSEWHR1"] and c.visible == "[?]", c
        assert "Anchor here [?]" in re.sub(r"<[^>]+>", "", xml)
        joined = "\n".join(quiet(audit.audit, out, "Thesis", db))
        assert "missing: ELSEWHR1 Elsewhere [in Other]" in joined and "unrefreshed citation" in joined
        assert "redundant (uncited): UNCITED1" not in joined

        for bad in (("Claim", ["UNCITED1"]), ("Anchor here", ["TRASHED1"])):
            try:
                quiet(cite.cite, odt, out, bad[0], bad[1], db)
            except SystemExit:
                continue
            raise AssertionError(f"cite accepted {bad}")
    print("zotero selftest ok")


if __name__ == "__main__":
    main()
