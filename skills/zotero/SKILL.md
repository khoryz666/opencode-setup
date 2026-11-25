---
name: zotero
description: >-
  Inspect a local Zotero library and its citations in an ODT report, and write
  Zotero JavaScript for the user to run when items must change. Use for Zotero
  items, collections, duplicates, uncited or missing references, or citation
  fields in a LibreOffice report.
---

# zotero

Read the library yourself; let the user change it. Zotero keeps
`~/Zotero/zotero.sqlite` open, so writing to it corrupts its caches. The scripts
in `<skill>/scripts` read a copy, WAL included. Refer to items by their
8-character key.

| Task | Command |
|------|---------|
| report vs collection | `audit.py report.odt "Collection"` (exits 1 on problems) |
| inspect items | `show.py KEY...` |
| what the user just changed | `show.py --recent [MINUTES]` |
| add a citation | `cite.py in.odt out.odt "ANCHOR" KEY...` |
| change the library | copy `template.js`, write calls under `// --- changes` |

For anything else, use `zotlib.load(zotlib.connect())`, which returns every
item by key with its fields, creators, collection paths, parent, children and
trash flag.

## Audit
`audit.py` reports these problems:
- missing: cited but not filed;
- redundant: filed but not cited;
- filed in the root instead of a subcollection;
- duplicates by title, DOI or ISBN;
- attachments with no parent;
- `[?]` or stale citation text, which means a refresh is due;
- manual bibliography entries.

"Filed twice" is a note, not a problem. Rerun the audit after every change the
user makes.

## Citing
- Read the source's attachment first and confirm that it states the claim.
- Back up the `.odt`, then run `cite.py` from the backup into the original.
  The anchor is raw `content.xml` text that occurs once, and the citation is
  inserted right after it as ` [?]`.
- Check that LibreOffice opens the result. Then the user runs **Zotero >
  Refresh**, and you rerun `audit.py`.

## Editing: JavaScript for the user
- The user runs it in Zotero: **Tools > Developer > Run JavaScript**, with
  **Run as async function** ticked.
- The `template.js` helpers are `item`, `collection("A/B")`, `person`, `org`,
  `create`, `update`, `attach` (gives a lone PDF its parent) and `move`.
- Each helper throws on a missing key, skips work already done and logs one line.
- Save the script to a file and run `node --check` on it, wrapped in
  `(async()=>{…})`. Give the user its path and say what it changes.
- Afterwards, run `show.py --recent`.
- Merging and trashing stay manual in Zotero: select both items, then **Merge
  Items**. This keeps their attachments.
