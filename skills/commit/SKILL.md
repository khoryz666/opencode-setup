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
`git add -p` may be unavailable. Stage one concern's hunks by number:

```bash
python3 <skill>/scripts/hunks.py [PATH...]            # list hunks, numbered
python3 <skill>/scripts/hunks.py --stage 2 5 [-- PATH...]
git diff --cached && git commit -m "fix(x): ..."
```

Relist after each stage; numbers shift. Untracked files: `git add` whole. If a
hunk mixes concerns, reset and replay one concern at a time.

Report `git log --oneline`.
