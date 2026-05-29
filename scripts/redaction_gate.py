#!/usr/bin/env python3
"""Redaction gate for the public ThesisOS repo.

Fails (exit 1) if any tracked file looks like it leaks a secret, a private
credential, or owner/organization PII. This is the automatable half of the
private/public boundary policy defined in the Research OS registry
(tobe/migrations/M-20260529-03-thesisos-public-oss-skeleton.md §9).

Dependency-free. Scans `git ls-files` so only tracked content is checked.
Run locally before pushing, and in CI on every push / pull_request.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# This file legitimately contains the forbidden patterns below, so exclude it.
SELF = "scripts/redaction_gate.py"

# Tracked paths that must never exist in the public repo.
FORBIDDEN_PATH_RE = re.compile(
    r"(^|/)\.env($|\.)"            # .env / .env.*
    r"|(^|/)(secrets|private|local)/"  # secret/private/local dirs
    r"|\.(pem|key|p12|pfx|db|sqlite3?|sqlite)$"  # key material / local DBs
    r"|(^|/)[^/]*(credential|cookie)s?[^/]*$",  # credentials / cookies files
    re.IGNORECASE,
)

# Value-shaped secret / PII patterns (target VALUES, not the generic words,
# so an OSS boundary statement like "no bot tokens" does not trip the gate).
CONTENT_PATTERNS = {
    "owner/org PII": re.compile(r"intervest|mailplug|shin영성|신영성|ys\.shin", re.IGNORECASE),
    "known telegram chat id": re.compile(r"\b373040444\b"),
    "telegram bot token": re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b"),
    "openai-style api key": re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    "aws access key id": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private key block": re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"),
}


def tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True, check=True
    ).stdout
    return [line for line in out.splitlines() if line and line != SELF]


def main() -> int:
    violations: list[str] = []
    for rel in tracked_files():
        if FORBIDDEN_PATH_RE.search(rel):
            violations.append(f"[path] forbidden tracked file: {rel}")
        p = Path(rel)
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue  # binary / asset / gone — skip
        for label, pat in CONTENT_PATTERNS.items():
            for m in pat.finditer(text):
                line_no = text.count("\n", 0, m.start()) + 1
                violations.append(f"[content] {label}: {rel}:{line_no}")

    if violations:
        print("REDACTION GATE FAILED — public boundary violation(s):", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        print(
            "\nThis repo is PUBLIC. Remove the leak, scrub git history if it was "
            "ever committed, and rotate any exposed credential before re-pushing.",
            file=sys.stderr,
        )
        return 1

    print(f"Redaction gate OK — {len(tracked_files())} tracked files clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
