#!/usr/bin/env python3
"""Scan a git repository for committed secrets and sensitive files.

Usage: find_secrets.py [history]
Default: the tracked files now. `history`: every line ever added on any branch.
Matches are redacted. Exits 1 on findings.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import PurePath

PATTERNS = {
    "private key": r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----",
    "AWS access key": r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b",
    "GitHub token": r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{60,})\b",
    "Anthropic key": r"\bsk-ant-[A-Za-z0-9_-]{20,}",
    "OpenAI key": r"\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}",
    "Google API key": r"\bAIza[0-9A-Za-z_-]{35}\b",
    "Slack token": r"\bxox[abprs]-[A-Za-z0-9-]{10,}",
    "JWT": r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",
    "URL with password": r"\b[a-z][a-z0-9+.-]*://[^/\s:@]+:[^/\s@]{3,}@",
    "assigned secret": r"(?i)\b(?:password|passwd|secret|api_?key|token)\b\s*[:=]\s*['\"][^'\"\s]{8,}['\"]",
}
SENSITIVE_FILES = re.compile(
    r"(^|/)(\.env(\..+)?|id_(rsa|dsa|ecdsa|ed25519)|.+\.(pem|key|p12|pfx|keystore)|credentials\.json|"
    r"service-account.*\.json|\.netrc|\.pgpass)$")
SAFE_FILES = re.compile(r"\.env\.(example|sample|template)$|\.pub$")
RX = {name: re.compile(p) for name, p in PATTERNS.items()}


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, errors="replace", check=True).stdout


def redact(s: str) -> str:
    return s[:6] + "…" if len(s) > 6 else "…"


def scan_line(where: str, line: str) -> list[str]:
    return [f"{where}: {name}: {redact(m.group(0))}" for name, rx in RX.items() for m in rx.finditer(line)]


def scan_tracked() -> list[str]:
    found = []
    for path in git("ls-files", "-z").split("\0"):
        if not path:
            continue
        if SENSITIVE_FILES.search(path) and not SAFE_FILES.search(path):
            found.append(f"{path}: sensitive file is tracked")
        try:
            data = open(path, "rb").read(5_000_000)
        except OSError:
            continue
        if b"\0" not in data[:4096]:
            for n, line in enumerate(data.decode("utf-8", "replace").splitlines(), 1):
                found += scan_line(f"{path}:{n}", line)
    return found


def scan_history() -> list[str]:
    found, commit, path = [], "", ""
    for line in git("log", "-p", "--all", "--no-color", "--no-ext-diff", "--format=commit %h").splitlines():
        if line.startswith("commit "):
            commit = line.split()[1]
        elif line.startswith("+++ b/"):
            path = line[6:]
            if SENSITIVE_FILES.search(path) and not SAFE_FILES.search(path):
                found.append(f"{commit} {path}: sensitive file was committed")
        elif line.startswith("+") and not line.startswith("+++"):
            found += scan_line(f"{commit} {path}", line[1:])
    return list(dict.fromkeys(found))


if __name__ == "__main__":
    if sys.argv[1:] not in ([], ["history"]):
        sys.exit(__doc__)
    hits = scan_history() if sys.argv[1:] else scan_tracked()
    print("\n".join(hits) or "no secrets found")
    sys.exit(1 if hits else 0)
