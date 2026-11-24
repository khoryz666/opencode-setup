---
name: humanize
description: >-
  Rewrite long-form reports and academic prose in Khor Yu Zhuang's own voice,
  removing AI-sounding filler while preserving facts, citations and ODT
  formatting. Use when the user says "humanize", "make this sound like me",
  "rewrite in my voice", "remove AI tells", or asks to rewrite an .odt report
  such as the Malaysian Economy project or the QorFinder FYP.
---

# Humanize reports in my voice

This profile is distilled from the QorFinder FYP proposal and the Malaysian
Economy property-development report. The FYP is the primary voice sample; the
Malaysian report is group work, so use it for register and evidence habits, not
as a unique voice.

## Voice profile

### Shape

- **Sentences:** mean 25 words, median 24, most between 10 and 42. Split
  anything over 45.
- **Paragraphs:** 90–180 words, 4–8 sentences. Topic sentence → evidence →
  implication.
- **Register:** formal academic/report English. British `-ise` spelling in the
  samples (`normalise`, `customise`, `organisation`); keep the document's own
  convention.
- **Person:** no first person in the body. Use "this project", "this report",
  "the system", "the developer", "the user". "I" only in acknowledgements.
- **Contractions:** none.

### Sentences

- Start with a concrete subject and verb: "The system indexes…", "Property
  development matters…", "This project assumes…".
- Prefer active voice when the actor matters; use passive in methods where the
  process matters ("was implemented", "were compared").
- Avoid "There is/are" openers and noun-heavy nominalisations.
- Use short non-restrictive "which" clauses for detail.
- Vary length: a 10–15 word claim, then a 25–35 word evidence sentence.

### Evidence

- Every claim gets a number, date, statute, table/section reference, or
  parenthetical citation.
- Keep citations exactly: `[1]`, `[18], [19]`, `(DOSM, 2026a, 2026e)`.
- Keep names, figures, units, dates and technical terms unchanged. Do not round
  numbers.
- Define acronyms on first use.
- Use "For example" for a concrete case and "In terms of" to narrow a
  comparison.

### Connectives

- Use "However" and "Therefore" freely (20 and 30 in 25k words). "For example"
  and "Overall" sparingly.
- Near-zero in the samples: "Moreover", "Furthermore", "Thus", "Hence", "In
  addition", "Additionally", "In conclusion". Do not add them.
- Use "First", "Second", "Third" for enumerations.
- Do not stack connectives at the start of a sentence.

### Punctuation

- Parentheses are common for citations, definitions, units and short
  clarifications (297 in 25k words).
- Colons introduce lists and definitions. Semicolons are rare (7) and only link
  tightly related clauses.
- No em dashes, exclamation marks or rhetorical questions.
- Keep curly quotes if the source uses them.

### Vocabulary

- Precise academic, legal and economic terms; no marketing adjectives.
- Remove: delve, leverage, robust, seamless, pivotal, crucial, vital,
  comprehensive, holistic, multifaceted, landscape (as a metaphor), realm,
  tapestry, navigate, foster, facilitate, utilize, not only…but also, serves as,
  plays a vital role, underscores, highlights, paving the way, game-changer,
  cutting-edge, revolutionary, unprecedented, in today's world, it is important
  to note, it is worth noting, in conclusion.
- Keep hedges only when the evidence is uncertain: may, can, likely, about.
- Do not add new claims, examples or evidence.

### Before / after

AI-ish:

> In today's rapidly evolving digital landscape, it is crucial to leverage robust
> search solutions to facilitate seamless information retrieval for small law
> firms.

My voice:

> Small law firms need a search tool that finds a relevant passage by meaning
> rather than by exact wording. The search built into an operating system matches
> file names and exact terms, so a lawyer must remember where a document was
> saved or how it was worded.

AI-ish:

> Moreover, the property sector plays a pivotal role in driving economic growth
> and fostering sustainable development.

My voice:

> Property development matters to the economy for three reasons. First, it has
> strong linkages with other industries. Second, housing is the largest asset and
> the largest debt of most families. Third, housing is the biggest item in the
> household budget.

## Rewrite rules

- Preserve meaning, facts, citations, figures, names, technical terms, paragraph
  order, headings and captions.
- Do not add evidence and do not delete evidence. Keep length within about 15%;
  cut filler, not facts.
- Rewrite prose only. Leave headings, table cells, figure/table captions,
  references, code and metadata alone.
- If a claim is unsupported or the meaning is unclear, leave it and flag it.
- Keep the document's spelling and citation style.
- For group reports, ask which sections are the user's; rewrite only those
  unless asked otherwise.
- Never mention AI, rewriting or "humanizing" in the report itself.

## ODT workflow

The scripts use only the Python standard library. `<skill>` is this skill's
directory (the skill tool prints its absolute path).

1. **Extract** the report into an editable Markdown file and metadata:

   ```bash
   python3 <skill>/scripts/odt_extract.py report.odt --out report.humanize
   ```

   This writes `report.humanize/report.md` and `report.humanize/blocks.json`.
   The original `.odt` is not modified.

2. **Rewrite** `report.md`. Edit only blocks with `rewrite=yes`:
   - keep the `<!-- block ... -->` header lines unchanged;
   - keep `{{rN}}…{{/rN}}` markers (they preserve bold/italic/citation
     formatting); move a marker only with its text;
   - keep each paragraph on one line;
   - leave `rewrite=no` blocks untouched.

3. **Apply** the edits to a new file:

   ```bash
   python3 <skill>/scripts/odt_apply.py report.odt report.humanize/report.md \
     report.humanize/blocks.json --out report.humanized.odt
   ```

   The original stays intact. If a marker is dropped or a read-only block was
   edited, the script stops and names the block.

4. **Verify**:

   ```bash
   python3 <skill>/scripts/odt_verify.py report.odt report.humanized.odt --pdf
   ```

   Check the citation warnings and the word-count change. `--pdf` asks
   LibreOffice to render the new file so it can be inspected.

5. **Report back:** changed paragraphs, word-count change, citation warnings and
   the output path. Do not paste the whole report into chat.

If the user asks to replace the original, back it up first; never overwrite it
silently.

### Long reports

Work one chapter or 20-block batch at a time. Use the heading blocks to find the
range, read only that range, and edit those blocks; leave the rest of the
Markdown untouched. You can apply after each batch. Every apply rebuilds from the
original `.odt` plus all edits currently in the Markdown, so earlier batches are
kept.

### Read-only reasons

The extractor marks a block `rewrite=no` when it is a heading, shorter than 160
characters, a caption/note, metadata, a reference/bibliography, a table/text-box,
code, or contains a link, footnote or frame. These are context, not rewrite
targets.

### Refreshing the profile

The baseline above comes from 208 paragraphs, 990 sentences and 25,161 words:

```bash
python3 <skill>/scripts/style_profile.py report1.odt report2.odt
```

Current numbers: mean sentence 25.4, median 24, p10 10, p90 42; 298 citations;
297 parentheses; 7 semicolons; however 20, therefore 30; moreover/furthermore/
thus/hence near zero. If new samples move these numbers, update this file.

## Plain text and Markdown

For a `.txt` or `.md` report, skip the ODT scripts and apply the profile
directly: rewrite paragraph by paragraph, preserve citations and figures, and
keep the same structure.

## Files

- `scripts/odt_extract.py` — ODT → editable Markdown + metadata.
- `scripts/odt_apply.py` — edited Markdown + metadata → new ODT.
- `scripts/odt_verify.py` — compare original and rewritten ODT; optional PDF.
- `scripts/style_profile.py` — print the voice statistics used above.
- `scripts/odt_lib.py` — shared parser and formatting-preserving rewrite logic.
- `scripts/selftest.py` — end-to-end check for the scripts.
