"""Scan the repository for content that should not be published.

Run from the repository root:

    python scripts/check_publish_safety.py

It scans every file in the repository (generated folders such as data/raw, data/processed, models and outputs are skipped) and reports:

  * absolute local paths (home directories, temporary folders and drive paths of any operating system),
  * secrets or key-like strings (private keys, cloud and GitHub tokens, "password = '...'" style assignments),
  * e-mail addresses,
  * .env files, secrets files and key files,
  * any file over 25 MB.

It prints every scanned file with its size and every finding, and exits 1 on any finding, 0 otherwise. A pattern scan finds the common mistakes;
it cannot prove that a file holds nothing sensitive, and it does not read inside binary files.
"""

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"__pycache__", ".ipynb_checkpoints", ".git", ".venv", "venv", "env", "raw", "processed", "models", "outputs", "chembl_fetch"}
TEXT_SUFFIXES = {".py", ".md", ".txt", ".toml", ".csv", ".json", ".ipynb", ".yml", ".yaml", ".cfg", ""}
MAX_BYTES = 25 * 1024 * 1024

PATTERNS = {
    "absolute local path": re.compile(r"(?:/Users/[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+|[A-Za-z]:\\Users\\|/private/(?:tmp|var)|/var/folders/|/Volumes/[A-Za-z0-9._-]+)"),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "cloud or GitHub token": re.compile(r"\b(?:AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|gho_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{30,})\b"),
    "secret-like assignment": re.compile(r"(?i)\b(?:api[_-]?key|secret|token|passwd|password)\b\s*[:=]\s*['\"][^'\"\s]{8,}['\"]"),
    "e-mail address": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
}
FORBIDDEN_NAMES = [re.compile(p) for p in (r"^\.env(\..*)?$", r"^secrets\.toml$", r".*\.pem$", r".*\.key$", r"^id_rsa.*$", r"^credentials(\..*)?$")]


def repository_files():
    files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            if name != ".DS_Store" and not name.endswith(".pyc") and path.resolve() != Path(__file__).resolve():   # the scanner holds the patterns it looks for
                files.append(path)
    return sorted(files)


def main():
    files = repository_files()
    findings = []
    total = 0
    print(f"Scanned files ({len(files)}):")
    for f in files:
        size = f.stat().st_size
        total += size
        rel = f.relative_to(ROOT)
        print(f"  {size:>10,}  {rel}")
        if size > MAX_BYTES:
            findings.append(f"{rel}: {size / 1e6:.1f} MB is over 25 MB")
        if any(p.match(f.name) for p in FORBIDDEN_NAMES):
            findings.append(f"{rel}: a file that normally holds secrets or keys")
        if f.suffix.lower() in TEXT_SUFFIXES:
            try:
                text = f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                findings.append(f"{rel}: not readable as text (unexpected for this suffix)")
                continue
            for label, pattern in PATTERNS.items():
                for m in pattern.finditer(text):
                    line = text.count("\n", 0, m.start()) + 1
                    findings.append(f"{rel}:{line}: {label}: {m.group(0)[:60]}")
    print(f"\nTotal {total / 1e6:.2f} MB. Findings: {len(findings)}")
    for item in findings:
        print("  FINDING:", item)
    if not findings:
        print("  none")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
