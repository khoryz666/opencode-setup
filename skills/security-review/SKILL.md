---
name: security-review
description: >-
  Security review of a diff, feature or repository: secrets, data exposure,
  unsafe file handling, auth, dependencies and LLM-specific risks. Use before
  releases, or when code touches parsing, storage, auth, networking, legal or
  client data.
---

# security-review

Review only. Do not edit files unless the user asks.

## Method
Read the actual code, not only comments. Trace attacker-controlled input from
entry to trust boundary to sink. Verify a suspected bug with a test or command
when possible. Report no speculative finding without a path.

Start with `python3 <skill>/scripts/find_secrets.py` (tracked files) and
`find_secrets.py history` (every added line, all branches); output is
redacted. A hit in history needs rotation, not just deletion.

## Checklist
- **Secrets and PII:** keys, tokens, `.env`, SSH keys, client names, document
  content in logs, fixtures, commits and error messages.
- **Data flow:** local-only processing, network calls, telemetry, model
  providers, uploads, temp files, backups and deletion.
- **Files:** path traversal, symlinks, zip bombs, malicious PDF/DOCX/ODT/archive
  input, unsafe extraction, temp permissions, TOCTOU.
- **Auth and local API:** token generation, bind address, CSRF, rate limits,
  privilege, session lifetime.
- **Dependencies:** lockfile, install scripts, versions, abandoned packages,
  supply-chain risk.
- **LLM-specific:** prompt injection from untrusted documents, tool permissions,
  model output executed as code, model downloads, data sent to providers.
- **Errors and logs:** no secrets or document content; no stack traces shown to
  users.
- **Retention:** index, cache, backups and deletion actually remove the data.

For a local legal-document app, also check: client-file confidentiality, index
and temp storage permissions, PDF parsing of hostile files, local API exposure,
embedding/model downloads, and whether any document content leaves the machine.

## Output
Three lists: **must fix**, **should fix**, **notes**. For each finding give:
what, where, impact, fix, and the check that proves it. Redact secrets. Never
test against third-party systems or real client data.
