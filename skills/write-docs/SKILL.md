---
name: write-docs
description: >-
  Write documentation and copy that is short, plain and purpose-first: READMEs,
  changelogs, plans, PR bodies, release notes, descriptions and page text. Use
  whenever you write or rewrite docs or copy, the user asks to "shorten",
  "simplify", "make it concise" or "use simple sentences", or docs/plans/code
  are "inconsistent", "out of sync" or "not aligned".
---

# write-docs

## Style
- Short, simple sentences and plain words. Cut what the reader won't use.
- **Purpose first.** Say what the thing is for, then how to use it, then how
  to build or change it.
- Follow the repo's existing format (headings, dates, section names) instead of
  inventing a new one.
- No author names, commit hashes or history inside doc items.
- No AI attribution.
- Diagrams should make sense on their own, with very little text.

## Decisions
When a finding is really a choice for the owner, write it as:

```markdown
**Decide:** the question
- Pick one: A) ... B) ...
- Either way: steps that apply to both
```

## Keep docs aligned
Cross-check every document against the others and against the code. Give each
fact one home: a plan owns *when*, a guide owns *how*, the README owns
*commands*. For every number, feature, status and process claim, find what backs
it: code, a recorded result, a commit, or a command you can rerun. Remove claims
nothing backs. When one doc changes, re-check every other doc that states the
same fact.

Back up binary documents (`.odt`, `.docx`) before editing, and use a tool that
preserves fields and citations instead of retyping them as text.

## Keep docs DRY
Each fact lives in one place and other docs link to it. Merge duplicate docs and
delete the extras.
