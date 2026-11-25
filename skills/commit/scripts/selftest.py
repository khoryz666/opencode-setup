#!/usr/bin/env python3
"""Self-test: stage one of two hunks in a throwaway repository."""

from __future__ import annotations

import contextlib
import io
import os
import subprocess
import tempfile
from pathlib import Path

import hunks


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        cwd = os.getcwd()
        os.chdir(tmp)
        try:
            run = lambda *a: subprocess.run(["git", *a], check=True, capture_output=True)
            run("init", "-q")
            run("config", "user.email", "t@example.com")
            run("config", "user.name", "t")
            lines = [f"line {i}" for i in range(1, 41)]
            Path("a.txt").write_text("\n".join(lines) + "\n")
            Path("b.txt").write_text("b\n")
            run("add", ".")
            run("commit", "-qm", "init")
            lines[1], lines[35] = "first change", "second change"
            Path("a.txt").write_text("\n".join(lines) + "\n")
            Path("b.txt").write_text("b changed\n")

            found = hunks.parse(hunks.git("diff"))
            assert [p for p, _, _ in found] == ["a.txt", "a.txt", "b.txt"], found
            with contextlib.redirect_stdout(io.StringIO()):
                hunks.main(["--stage", "2", "3"])
            staged = hunks.git("diff", "--cached")
            assert "+second change" in staged and "+b changed" in staged and "first change" not in staged
            assert "+first change" in hunks.git("diff")
            with contextlib.redirect_stdout(io.StringIO()) as out:
                hunks.main(["a.txt"])
            assert out.getvalue().count("a.txt") == 1
        finally:
            os.chdir(cwd)
    print("commit selftest ok")


if __name__ == "__main__":
    main()
