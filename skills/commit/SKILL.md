---
name: commit
description: >-
  Small, single-purpose commits with one-line Conventional Commit messages,
  gated on project checks; also apply review feedback one item at a time. Use
  for commits, splitting changes, history edits, or "apply the review".
---

# commit

- One commit, one concern. Plan boundaries before editing; commit after each
  change.
- One-line Conventional Commit: `feat|fix|refactor|docs|test|build|ci|chore(scope): imperative`,
  lower case, no period, no body. Describe the change, not the process or AI.
- No AI co-author or trailer unless required.
- Run the project's checks with `&&` before every commit. Never commit red.
- Don't push, tag or merge unless asked.

## Review feedback
Read the whole review, number every item, and triage: apply / defer / decide / no
change. Apply one at a time: fix, check, commit alone. Measure claimed
improvements before and after with the same command; keep only if better. Report
applied (with hashes), deferred (and where), and rejected (and why).

## Splitting an existing change
`git add -p` may be unavailable. Stage only one concern's hunks:

```bash
git diff -U0 file > all.patch       # keep only this commit's hunks in part.patch
git apply --cached --unidiff-zero part.patch
git commit -m "fix(x): ..."
```

If a hunk mixes concerns, reset and replay one concern at a time.

Report `git log --oneline`.
