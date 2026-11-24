---
name: humanize
description: >-
  Rewrite long-form reports and academic prose in a personal voice, removing
  AI-sounding filler while preserving facts, citations and ODT formatting. Use
  for "humanize", "sound like me", "rewrite in my voice", "remove AI tells", or
  an .odt report. Profile is provisional until authentic samples replace it.
---

# humanize

> **Provisional profile:** distilled from AI-generated reports, so treat it as an
> AI-text baseline, not the user's voice. Replace after authentic samples and
> before/after edits.

## Voice
- Formal academic/report English; British `-ise` as in the source; keep the
  document's convention.
- Sentences: mean 25, median 24, most 10–42; split over ~45. Paragraphs 90–180
  words, 4–8 sentences: claim → evidence → implication.
- No first person in the body: use "this project/report/system/developer/user";
  "I" only in acknowledgements. No contractions.
- Start with a concrete subject and verb. Active where the actor matters;
  passive in methods. Avoid "There is/are" and nominalisations; keep "which"
  clauses short.
- Every claim gets a number, date, statute, section/table reference or citation.
  Keep citations exactly (`[1]`, `[18], [19]`, `(DOSM, 2026a)`); keep names,
  figures, units, dates and terms; define acronyms once; never round numbers.
- Use "However"/"Therefore" freely; "For example"/"Overall" sparingly. Avoid
  "Moreover", "Furthermore", "Thus", "Hence", "In addition", "Additionally",
  "In conclusion". Use First/Second/Third.
- Parentheses for citations, definitions and units; colons for lists and
  definitions; semicolons rare. No em dashes, exclamation marks or rhetorical
  questions. Keep curly quotes.
- Precise technical/legal/economic terms; no marketing adjectives. Remove:
  delve, leverage, robust, seamless, pivotal, crucial, vital, comprehensive,
  holistic, multifaceted, landscape (metaphor), realm, tapestry, navigate,
  foster, facilitate, utilize, not only…but also, serves as, plays a vital role,
  underscores, highlights, paving the way, game-changer, cutting-edge,
  revolutionary, unprecedented, in today's world, it is important to note, it
  is worth noting, in conclusion.
- Hedges only for uncertain evidence: may, can, likely, about. Add no claims,
  examples or evidence.

## Rewrite rules
- Preserve meaning, facts, citations, figures, names, terms, paragraph order,
  headings and captions.
- Cut filler, not facts; keep length within ~15%.
- Rewrite prose only. Leave headings, table cells, captions, references, code
  and metadata.
- If a claim is unsupported or unclear, leave it and flag it.
- Keep the document's spelling and citation style.
- For group reports, ask which sections are the user's.
- Never mention AI, rewriting or "humanizing" in the report.

## ODT workflow
Scripts use only the Python standard library; `<skill>` is this skill's directory.

1. Extract: `python3 <skill>/scripts/odt_extract.py report.odt --out report.humanize`
   → `report.md` + `blocks.json`; original untouched.
2. Rewrite `report.md`: edit only `rewrite=yes` blocks; keep block headers,
   `{{rN}}…{{/rN}}` markers and one paragraph per line; leave `rewrite=no` alone.
3. Apply:
   `python3 <skill>/scripts/odt_apply.py report.odt report.humanize/report.md report.humanize/blocks.json --out report.humanized.odt`
   The original stays intact; a dropped marker or edited read-only block stops it.
4. Verify: `python3 <skill>/scripts/odt_verify.py report.odt report.humanized.odt --pdf`
   Check citation warnings and the word-count change.
5. Report changed paragraphs, word delta, citation warnings and output path; do
   not paste the report.

Long reports: work one chapter or 20 blocks at a time; apply after each batch.
Every apply rebuilds from the original plus all current Markdown edits.

Read-only: headings, <160 chars, captions, metadata, references, tables/text
boxes, code, links/footnotes/frames.

Refresh profile: `python3 <skill>/scripts/style_profile.py report1.odt report2.odt`;
update this file if the numbers move.

Plain text/Markdown: apply the same voice rules directly.

Files: `odt_extract.py`, `odt_apply.py`, `odt_verify.py`, `style_profile.py`,
`odt_lib.py`, `selftest.py`.
