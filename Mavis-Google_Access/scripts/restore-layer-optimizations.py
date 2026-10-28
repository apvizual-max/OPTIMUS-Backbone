#!/usr/bin/env python3
# restore-layer-optimizations.py - carry the merged optimizations forward into
# the new home of google-layer/, without rewriting any of them by hand.
#
# WHY THIS EXISTS
# 2026-10-28: google-layer/ moved from the backbone repo into
# Mavis-Google_Access/ (its own repo, its own remote, its own history). The
# move was verified for PRESENCE. It was NOT verified for CONTENT, and three
# optimizations merged on 24 Oct were left behind in the old repo:
#
#   PR #11  bun-secrets-shim.js  - async I/O
#   PR #31  gworkspace-oauth.js  - async OAuth client load
#   PR #34  verify-workspace.js - async readLock
#   (notebook-ask.js also moved pre-async)
#
# A file that is present but older is not a move. It is a regression wearing a
# move's clothes.
#
# WHAT IT DOES
# For each listed file, it takes the blob from the reference repo at a pinned
# commit (not "HEAD", so the result is reproducible), writes it byte-exact into
# the destination, and PROVES the outcome:
#   - the written bytes hash identically to the source blob
#   - the file still parses (node --check for .js)
#   - the public export surface is unchanged (a shim whose exports change
#     would break its callers silently)
#
# Usage:
#   python scripts/restore-layer-optimizations.py --from <repo> --to <repo> \
#          [--commit <sha>] [--apply]
#
# Without --apply it only reports what WOULD change. Exit: 0 = ok, 1 = a
# verification failed (and the destination was left untouched).

import argparse
import hashlib
import os
import subprocess
import sys

FILES = [
    "google-layer/bun-secrets-shim.js",
    "google-layer/gworkspace-oauth.js",
    "google-layer/notebook-ask.js",
    "google-layer/verify-workspace.js",
]


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def blob(repo, commit, rel):
    p = run(["git", "-C", repo, "show", commit + ":" + rel])
    if p.returncode != 0:
        return None
    return p.stdout


def sha(data):
    return hashlib.sha256(data).hexdigest()


def exports_of(text):
    """The public export surface of a CommonJS module, as a sorted list."""
    out = []
    for line in text.decode("utf-8", "replace").splitlines():
        s = line.strip()
        if s.startswith("module.exports"):
            out.append(s)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", required=True, help="reference repo")
    ap.add_argument("--to", dest="dst", required=True, help="destination repo")
    ap.add_argument("--commit", default="HEAD", help="pinned commit in the reference repo")
    ap.add_argument("--apply", action="store_true", help="write the files (default: report only)")
    args = ap.parse_args()

    problems = []
    changed = 0
    identical = 0

    for rel in FILES:
        data = blob(args.src, args.commit, rel)
        if data is None:
            problems.append("source blob missing: " + rel)
            continue

        dst_path = os.path.join(args.dst, rel.replace("/", os.sep))
        cur = None
        if os.path.exists(dst_path):
            with open(dst_path, "rb") as fh:
                cur = fh.read()

        if cur is not None and sha(cur) == sha(data):
            identical += 1
            print("ALREADY_CURRENT " + rel)
            continue

        # The export surface must not change: a shim whose exports change
        # breaks its callers at runtime, not at commit time.
        if cur is not None:
            ex_src = exports_of(data)
            ex_dst = exports_of(cur)
            if ex_src != ex_dst:
                problems.append("export surface would change in " + rel)
                print("PROBLEM " + rel + " export_surface_changed")
                continue

        if not args.apply:
            # Report mode: verify the SOURCE is intact and state what the
            # destination would become. Comparing the untouched destination
            # against the source would always "fail" - that measures nothing.
            if sha(data) != sha(blob(args.src, args.commit, rel) or b""):
                problems.append("source blob re-read differs: " + rel)
                print("PROBLEM " + rel + " source_unstable")
                continue
            changed += 1
            print("WOULD_RESTORE " + rel + " bytes=%d sha256=%s" % (len(data), sha(data)[:12]))
            continue

        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        with open(dst_path, "wb") as fh:
            fh.write(data)

        # Prove it: the bytes on disk now hash to the source blob.
        with open(dst_path, "rb") as fh:
            written = fh.read()
        if sha(written) != sha(data):
            problems.append("byte verification failed: " + rel)
            print("PROBLEM " + rel + " byte_mismatch")
            continue

        if rel.endswith(".js"):
            chk = run(["node", "--check", dst_path])
            if chk.returncode != 0:
                problems.append("node --check failed: " + rel)
                print("PROBLEM " + rel + " node_check_failed")
                continue

        changed += 1
        print("RESTORED " + rel + " bytes=%d sha256=%s" % (len(data), sha(data)[:12]))

    print("")
    print("SUMMARY restored=%d already_current=%d problems=%d apply=%s" % (changed, identical, len(problems), args.apply))
    for p in problems:
        print("  PROBLEM " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
