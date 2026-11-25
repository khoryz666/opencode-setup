#!/usr/bin/env python3
"""List or stage hunks of the unstaged diff, for when `git add -p` is unavailable.

Usage: hunks.py [PATH...]          list hunks, numbered
       hunks.py --stage N... [--] [PATH...]  stage only hunks N...
Numbers come from the listing with the same PATHs; relist after each stage.
Untracked files are not in the diff: `git add` them whole.
"""

from __future__ import annotations

import subprocess
import sys


def git(*args: str, stdin: str | None = None) -> str:
    return subprocess.run(["git", *args], input=stdin, capture_output=True, text=True, check=True).stdout


def parse(diff: str) -> list[tuple[str, str, str]]:
    """(path, file header, hunk) for every text hunk."""
    out = []
    for chunk in diff.split("\ndiff --git "):
        if not chunk.strip():
            continue
        chunk = chunk if chunk.startswith("diff --git ") else "diff --git " + chunk
        head, _, rest = chunk.partition("\n@@")
        if not rest:
            continue  # binary, mode-only or rename-only change
        path = head.split("\n", 1)[0].split(" b/", 1)[-1]
        for hunk in ("@@" + rest).split("\n@@"):
            hunk = hunk if hunk.startswith("@@") else "@@" + hunk
            out.append((path, head + "\n", hunk.rstrip("\n") + "\n"))
    return out


def summary(hunk: str) -> str:
    header, *lines = hunk.splitlines()
    changed = next((l for l in lines if l[:1] in "+-"), "")
    return f"{header.split(' @@')[0]} @@  {changed[:70]}"


def main(argv: list[str]) -> None:
    stage = argv[:1] == ["--stage"]
    paths, nums = argv[1:] if stage else argv, []
    while stage and paths and paths[0].isdigit():
        nums.append(int(paths.pop(0)))
    paths = paths[1:] if paths[:1] == ["--"] else paths
    hunks = parse(git("diff", "--no-color", "--no-ext-diff", "--", *paths))
    if not stage:
        for n, (path, _, hunk) in enumerate(hunks, 1):
            print(f"{n:3} {path} {summary(hunk)}")
        if not hunks:
            print("no unstaged hunks")
        return
    if not nums or any(not 1 <= n <= len(hunks) for n in nums):
        sys.exit(f"pick hunk numbers from 1 to {len(hunks)}")
    patch, last = "", None
    for n in sorted(set(nums)):
        path, head, hunk = hunks[n - 1]
        patch += (head if path != last else "") + hunk
        last = path
    git("apply", "--cached", "--recount", "-", stdin=patch)
    print(f"staged hunks {', '.join(map(str, sorted(set(nums))))}")


if __name__ == "__main__":
    main(sys.argv[1:])
