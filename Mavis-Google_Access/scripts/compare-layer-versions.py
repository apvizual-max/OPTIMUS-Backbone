#!/usr/bin/env python3
# compare-layer-versions.py - measure the difference between two copies of a
# file set, line by line, with no assumptions about which one is "right".
#
# WHY THIS EXISTS
# 2026-10-28: google-layer/ was moved from the backbone repo into
# Mavis-Google_Access/. The move was measured for PRESENCE (every file was
# present) but not for CONTENT: three merged optimizations from 24 Oct
# (PR #11 async shim, PR #31 async OAuth client load, PR #34 async readLock)
# were already in the backbone and were NOT in the moved copy. A file that is
# present but older is not a move - it is a regression wearing a move's
# clothes.
#
# This tool reports, per file: identical / differs, the number of added and
# removed lines, and the unified diff itself. It does NOT judge which side is
# correct; it makes the difference visible so a decision can be made on
# evidence.
#
# Usage:
#   python scripts/compare-layer-versions.py --a <repoA> --b <repoB> \
#          [--dir google-layer] [--diff]
#
# Exit: 0 = comparison ran, 1 = a usage error.

import argparse
import difflib
import subprocess
import sys


def git_show(repo, rel):
    """Return the blob text of rel at HEAD in repo, or None if absent."""
    p = subprocess.run(
        ["git", "-C", repo, "show", "HEAD:" + rel],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if p.returncode != 0:
        return None
    return p.stdout.decode("utf-8", "replace")


def git_ls(repo, prefix):
    p = subprocess.run(
        ["git", "-C", repo, "ls-files", "--", prefix],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if p.returncode != 0:
        return []
    return [line.strip() for line in p.stdout.decode("utf-8", "replace").splitlines() if line.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True, help="repo A (reference)")
    ap.add_argument("--b", required=True, help="repo B (copy under test)")
    ap.add_argument("--dir", default="google-layer", help="directory prefix inside both repos")
    ap.add_argument("--diff", action="store_true", help="print the unified diff for differing files")
    args = ap.parse_args()

    files_a = git_ls(args.a, args.dir)
    files_b = set(git_ls(args.b, args.dir))

    if not files_a:
        print("ERROR=no files under %s in %s" % (args.dir, args.a))
        return 1

    same = 0
    diff = 0
    only_a = []
    only_b = []

    for rel in files_a:
        if rel not in files_b:
            only_a.append(rel)
            continue
        ta = git_show(args.a, rel)
        tb = git_show(args.b, rel)
        if ta is None or tb is None:
            only_a.append(rel)
            continue
        la = ta.replace("\r\n", "\n").splitlines()
        lb = tb.replace("\r\n", "\n").splitlines()
        if la == lb:
            same += 1
            continue
        diff += 1
        added = sum(1 for x in difflib.ndiff(la, lb) if x.startswith("+ "))
        removed = sum(1 for x in difflib.ndiff(la, lb) if x.startswith("- "))
        print("DIFFERS %s lines_a=%d lines_b=%d added=%d removed=%d" % (rel, len(la), len(lb), added, removed))
        if args.diff:
            for line in difflib.unified_diff(la, lb, fromfile="A/" + rel, tofile="B/" + rel, lineterm="", n=1):
                print("    " + line)

    for rel in sorted(files_b - set(files_a)):
        only_b.append(rel)

    print("")
    print("SUMMARY identical=%d differs=%d only_in_a=%d only_in_b=%d" % (same, diff, len(only_a), len(only_b)))
    for rel in only_a:
        print("  ONLY_IN_A " + rel)
    for rel in only_b:
        print("  ONLY_IN_B " + rel)
    return 0


if __name__ == "__main__":
    sys.exit(main())
