---
name: commit
description: >-
  Commit work as small, single-purpose commits with one-line Conventional Commit
  messages, each gated on the project's own checks. Use whenever you are about to
  commit, split changes into commits, amend or reorder history, apply review
  feedback one item at a time, or the user says "commit", "one commit one
  thing", "logically isolated commits", "apply the review" or "conventional
  commit".
---

# commit

## Rules
- **One commit does one thing.** Never bundle two concerns. Plan commit
  boundaries before editing, and commit after each change instead of splitting
  at the end.
- **Message = one line, no body.** Conventional Commits: `feat:`, `fix:`,
  `refactor:`, `docs:`, `test:`, `build:`, `ci:`, `chore:`, optional scope
  (`fix(parser): ...`). Imperative, lower case, no trailing period.
- **Describe the change, not the process.** No mention of AI, rewrites,
  rebuilt history or how the change was produced.
- **No AI in authorship.** No co-author trailer or "with <assistant>" unless the
  harness or the user requires one. Use the user's name where a name is needed.
- **Every commit passes.** Find the project's checks (CI config, Makefile,
  package scripts, README) and chain them with `&&`, never `;`, so a broken
  commit never lands.
- **Don't push, tag or merge unless asked.**

## Applying review feedback
When the user points at a review, feedback file or fix plan:

1. Read it all, number every item, and triage into **apply now**, **defer**,
   **decide** or **no change**. Record deferred work where the project tracks
   open work.
2. Apply one item at a time: fix it, run the project's checks, commit it alone.
   Never batch items.
3. If a fix claims an improvement (speed, size, accuracy), measure before and
   after with the same command and inputs. Keep it only if it improves;
   otherwise revert and note "tried, no gain".
4. Report three short lists: applied (with commit hashes), deferred (and where),
   not applied (and why).

## Splitting existing changes
Interactive `git add -p` may be unavailable. Stage part of a file by applying a
trimmed patch to the index:

```bash
git diff -U0 file > all.patch       # keep only this commit's hunks in part.patch
git apply --cached --unidiff-zero part.patch
git commit -m "fix(x): ..."
```

If one hunk mixes two concerns, reset the file and replay the edits one concern
at a time, committing after each.

## Before reporting
Show `git log --oneline` for the new commits.
