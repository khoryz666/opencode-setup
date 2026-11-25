#!/usr/bin/env python3
"""Self-test: find_secrets.py finds planted fakes in a throwaway repository."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

import find_secrets as scan

FAKE_AWS = "AKIA" + "ABCDEFGHIJKLMNOP"  # split so this file does not match itself
FAKE_GH = "ghp_" + "a" * 36


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        cwd = os.getcwd()
        os.chdir(tmp)
        try:
            run = lambda *a: subprocess.run(["git", *a], check=True, capture_output=True)
            run("init", "-q")
            run("config", "user.email", "t@example.com")
            run("config", "user.name", "t")
            Path("config.py").write_text(f'key = "{FAKE_AWS}"\nname = "ok"\n')
            Path(".env").write_text("X=1\n")
            Path(".env.example").write_text("X=\n")
            Path("old.txt").write_text(f"token {FAKE_GH}\n")
            run("add", "-A")
            run("commit", "-qm", "add")
            run("rm", "-q", "old.txt")
            run("commit", "-qm", "remove")

            now = "\n".join(scan.scan_tracked())
            assert "config.py:1: AWS access key: AKIAAB…" in now and FAKE_AWS not in now, now
            assert ".env: sensitive file is tracked" in now and ".env.example" not in now and "old.txt" not in now
            past = "\n".join(scan.scan_history())
            assert "old.txt: GitHub token" in past and FAKE_GH not in past, past
        finally:
            os.chdir(cwd)
    print("security-review selftest ok")


if __name__ == "__main__":
    main()
