---
name: zotero
description: >-
  Inspect a local Zotero library and its citations in an ODT report, and write
  Zotero JavaScript for the user to run when items must change. Use for Zotero
  items, collections, duplicates, uncited or missing references, or citation
  fields in a LibreOffice report.
---

# zotero

Read the database yourself; let the user change it. Zotero holds
`~/Zotero/zotero.sqlite` open, so writing to it corrupts caches.

## Read
Copy first, WAL included, then query the copy with Python `sqlite3`
(the `sqlite3` CLI may be absent):

```bash
cp ~/Zotero/zotero.sqlite ~/Zotero/zotero.sqlite-wal "$TMP/"
```

| Need | Tables |
|------|--------|
| field value | `itemData` ⋈ `itemDataValues` ⋈ `fields` (`fieldName`: `title`, `nameOfAct`, `date`, `url`, `DOI`) |
| type | `items` ⋈ `itemTypes`; skip `attachment`, `note`, `annotation` |
| authors | `itemCreators` ⋈ `creators` (`fieldMode=1` = one-field name) |
| collections | `collections` (`parentCollectionID`), `collectionItems`; subtree via `WITH RECURSIVE` |
| trash | `deletedItems` — exclude it everywhere |
| child files | `itemAttachments.parentItemID`; files in `~/Zotero/storage/<key>/` |

Refer to items by their 8-character `key`, not `itemID`. Re-copy after every
user change, then report what changed (`dateModified`).

## Citations in ODT
`content.xml` holds each citation as a reference mark
`ZOTERO_ITEM CSL_CITATION {json} RND<id>`; the JSON `citationItems[].uris` ends
in the item key. The bibliography is the section `ZOTERO_BIBL {...}`; check its
`uncited`/`custom` are empty.

Audit: cited keys vs non-trashed regular items under the collection. Report
missing (cited, not filed), redundant (filed, uncited), items filed twice,
duplicates (normalised title, DOI, URL, ISBN), and loose attachments with no
parent. Visible text ≠ `plainCitation`, or `[?]`, means a refresh is due.

To add a citation, back up the `.odt`, insert a reference mark
(`formattedCitation` `[?]`, `uris`, `itemData`) in `content.xml`, rezip with
`mimetype` first and stored, check that LibreOffice opens it, then ask the user
to run Zotero > Refresh.

Before citing a source, read its attachment and confirm that it states the claim.

## Edit: JavaScript for the user
Zotero: **Tools > Developer > Run JavaScript**, tick **Run as async function**.
Save the script to a file, give its path, and say what it changes.

```js
const lib = Zotero.Libraries.userLibraryID;
const col = Zotero.Collections.getByLibrary(lib, true)
  .find(c => c.name === 'Target');            // match parentID too if names repeat
if (!col) throw new Error('collection not found');
const item = await Zotero.Items.getByLibraryAndKeyAsync(lib, 'ABCD1234');
if (!item) throw new Error('ABCD1234 not found');
item.setField('title', '...');                // setCreators([{firstName,lastName,creatorType}])
item.addToCollection(col.id);                 // removeFromCollection(id)
await item.saveTx();
return 'done';                                // shown to the user
```

- New item: `new Zotero.Item('webpage')`, set `libraryID`, fields, `saveTx()`.
- Institutional author: `{lastName: 'Org', fieldMode: 1, creatorType: 'author'}`.
- Parent for a lone PDF: save the parent, then `pdf.setCollections([])`,
  `pdf.parentID = parent.id`, `pdf.saveTx()`. Children can't sit in collections.
- Make it idempotent (skip what is already done), throw on missing keys, and
  return a log line for each change.
- Check syntax with `node --check` (wrap it in `(async()=>{…})`), then
  re-read the database once the user has run it.
- Let the user merge duplicates in Zotero (select both > **Merge Items**) so
  attachments are kept, and delete or trash items there too.
