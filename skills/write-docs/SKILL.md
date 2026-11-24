---
name: write-docs
description: >-
  Short, plain, purpose-first docs and copy; keep docs, plans and code aligned.
  Use for READMEs, changelogs, plans, PR bodies, release notes, page text, or
  "shorten/simplify/align these docs".
---

# write-docs

## Style
- Short sentences, plain words. Cut what the reader won't use.
- Purpose first: what it is for → how to use → how to build/change.
- Follow the repo's format; no author names, hashes, history or AI attribution.
- Diagrams must stand alone.

## Decisions
For a choice for the owner:

```markdown
**Decide:** the question
- Pick one: A) ... B) ...
- Either way: shared steps
```

## Keep docs aligned
One fact, one home: a plan owns *when*, a guide owns *how*, the README owns
*commands*. For every number, feature, status and process claim, find its
backing: code, a recorded result, a commit, or a rerunnable command. Remove
claims nothing backs. When one doc changes, re-check every doc that repeats the
fact. Back up `.odt`/`.docx` before editing and preserve fields and citations.

## Keep docs DRY
Each fact lives once; other docs link to it. Merge duplicates and delete extras.
