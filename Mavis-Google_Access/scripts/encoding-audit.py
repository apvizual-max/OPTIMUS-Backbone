#!/usr/bin/env python3
"""encoding-audit.py - the encoding gate for this repository.

Why it exists: Windows PowerShell 5.1 writes UTF-8 WITH a BOM by default, and
a BOM in front of a YAML or shell file is not invisible - it is the first byte
the parser sees. A BOM in a committed script has already broken a workflow
here ("base64: invalid input"), and a BOM in a PowerShell script kills the
parser outright.

The gate reads the files that git reports as changed (or every tracked file
with --all) and fails when:
  - the file starts with a UTF-8 BOM,
  - the file is not valid UTF-8,
  - a .ps1 file contains non-ASCII bytes (Windows PowerShell 5.1 reads a
    .ps1 file as ANSI unless it carries a BOM, so non-ASCII in a .ps1 is
    corruption, not style).

Usage: python scripts/encoding-audit.py [--all]
"""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PS_ONLY_ASCII = (".ps1",)


def changed_files(all_files):
    if all_files:
        out = subprocess.run(["git", "-C", REPO, "ls-files"], capture_output=True, text=True).stdout
        return [p for p in out.splitlines() if p]
    out = subprocess.run(
        ["git", "-C", REPO, "status", "--porcelain"], capture_output=True, text=True
    ).stdout
    paths = []
    for line in out.splitlines():
        if len(line) > 3:
            paths.append(line[3:].strip().strip('"'))
    return paths


def main():
    all_files = "--all" in sys.argv
    paths = changed_files(all_files)
    problems = []
    checked = 0
    for rel in paths:
        p = os.path.join(REPO, rel.replace("/", os.sep))
        if not os.path.isfile(p):
            continue
        checked += 1
        raw = open(p, "rb").read()
        if raw[:3] == b"\xef\xbb\xbf":
            problems.append("BOM %s" % rel)
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError:
            problems.append("NOT_UTF8 %s" % rel)
            continue
        if os.path.splitext(rel)[1].lower() in PS_ONLY_ASCII:
            bad = [i for i, b in enumerate(raw) if b > 127]
            if bad:
                problems.append("NON_ASCII_IN_PS1 %s count=%d" % (rel, len(bad)))
    print("FILES_CHECKED=%d PROBLEMS=%d" % (checked, len(problems)))
    for p in problems:
        print("  " + p)
    return 0 if not problems else 2


if __name__ == "__main__":
    sys.exit(main())
