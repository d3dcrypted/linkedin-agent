#!/usr/bin/env python3
"""Small dependency-free hygiene check before publishing a repository.

Fails on forbidden filenames (credential files) and on suspicious content in the
working tree: private keys, assigned secret values, private IP ranges and
machine-local home paths. Identity review stays manual on purpose: hardcoding a
person's name in a public script would leak the very thing it checks for.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", ".venv", "__pycache__"}
PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?:api[_-]?key|password|token|secret)\s*[:=]\s*['\"]?(?!\$\{)[^\s'\"]{8,}", re.I),
    re.compile(r"\b(?:10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+)\b"),
    re.compile(r"/home/[A-Za-z0-9_.-]+"),
]
FORBIDDEN_NAMES = {".env", ".env.local", "credentials.json", "id_rsa", "id_ed25519"}

failures = []
for path in ROOT.rglob("*"):
    if not path.is_file() or any(part in SKIP for part in path.parts):
        continue
    if path.name in FORBIDDEN_NAMES:
        failures.append(f"forbidden filename: {path.relative_to(ROOT)}")
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    for number, line in enumerate(text.splitlines(), 1):
        for pattern in PATTERNS:
            if pattern.search(line):
                failures.append(f"suspicious content: {path.relative_to(ROOT)}:{number}")
                break

if failures:
    print("Publication hygiene check failed:")
    print("\n".join(f"- {item}" for item in failures))
    sys.exit(1)
print("Publication hygiene check passed: no forbidden filenames or suspicious patterns found.")
