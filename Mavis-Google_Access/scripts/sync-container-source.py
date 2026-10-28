#!/usr/bin/env python3
"""sync-container-source.py - copy the live container source into this repo.

The image content lives in ONE place at a time. This script copies the
authoritative source (the folder the image is built from) into ./container,
so the repository can rebuild the identical image.

Rules:
- secrets are NEVER copied (data/, logs/, and every *.json credential)
- the copy is byte-exact for the files it copies
- a file that is missing on the source side is reported, not silently kept

Usage: python scripts/sync-container-source.py [--source <dir>] [--check]
       --check  only report the difference, write nothing
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys

FILES = [
    "Dockerfile",
    ".dockerignore",
    "server.mjs",
    "provision-grant.cjs",
    "consent-watcher.mjs",
    "mcp-call.mjs",
    "probe.mjs",
    "probe-services.mjs",
    "extendlm-provision.mjs",
    "watch-reauth.ps1",
]

# Diagnostic tools that live in state/ on the live machine.
EXTRA = {
    "state/probe-token.mjs": "scripts/probe-token.mjs",
    "state/extendlm-register-probe.mjs": "scripts/extendlm-register-probe.mjs",
    "state/patch-api-hosts.py": "scripts/patch-api-hosts.py",
}

GITIGNORE = """# The credential never enters this repository.
data/
logs/
state/
*.tmp
*.log
__pycache__/

# Working clone of MAVIS-CLOUD - that repo has its own history. A copy of
# another repository inside a public repository would duplicate it.
.work/
"""


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=r"C:\Users\apviz\.minimax\google-access")
    ap.add_argument("--dest", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "container"))
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    os.makedirs(args.dest, exist_ok=True)
    problems = []
    copied = 0
    for name in FILES:
        src = os.path.join(args.source, name)
        dst = os.path.join(args.dest, name)
        if not os.path.isfile(src):
            problems.append("MISSING_SOURCE " + name)
            continue
        if os.path.isfile(dst) and sha(src) == sha(dst):
            continue
        if args.check:
            problems.append("DIFFERS " + name)
            continue
        shutil.copy2(src, dst)
        copied += 1
        print("COPIED %s sha256=%s" % (name, sha(dst)[:16]))

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for rel, dest_rel in EXTRA.items():
        src = os.path.join(args.source, rel)
        dst = os.path.join(repo_root, dest_rel)
        if not os.path.isfile(src):
            problems.append("MISSING_SOURCE " + rel)
            continue
        if os.path.isfile(dst) and sha(src) == sha(dst):
            continue
        if args.check:
            problems.append("DIFFERS " + dest_rel)
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1
        print("COPIED %s sha256=%s" % (dest_rel, sha(dst)[:16]))

    gi = os.path.join(repo_root, ".gitignore")
    if not args.check and (not os.path.isfile(gi) or open(gi, encoding="utf-8").read() != GITIGNORE):
        with open(gi, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(GITIGNORE)
        print("WROTE .gitignore")

    # The .gitignore is a safety device, so it is verified, not assumed.
    # Measured 2026-10-27: this script owned the file with a constant that did
    # not carry the .work/ rule, so a sync silently dropped it and the working
    # clone of MAVIS-CLOUD (418 files) became visible to "git add -A" inside a
    # PUBLIC repository. A rule that is only a constant can be dropped silently;
    # it has to be checked against the real git index.
    required_ignores = [
        ("data/credentials.json", "the credential must never be committable"),
        ("data/extendlm.json", "the ExtendLM token must never be committable"),
        (".work/MAVIS-CLOUD/README.md", "another repository's clone must stay out"),
    ]
    for rel, why in required_ignores:
        probe = os.path.join(repo_root, rel.replace("/", os.sep))
        r = subprocess.run(
            ["git", "-C", repo_root, "check-ignore", "-q", rel],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if r.returncode != 0:
            problems.append("NOT_IGNORED %s (%s)" % (rel, why))
        else:
            print("IGNORE_OK %s" % rel)
        if os.path.exists(probe):
            print("PRESENT_BUT_IGNORED %s" % rel)

    # The stronger property: nothing under the sensitive roots is TRACKED.
    # A .gitignore rule never untracks a file that is already in the index,
    # so the index itself has to be inspected.
    tracked = subprocess.run(
        ["git", "-C", repo_root, "ls-files"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    tracked_paths = [p for p in tracked.stdout.decode("utf-8", "replace").splitlines() if p]
    sensitive = [p for p in tracked_paths if p.startswith(("data/", "logs/", "state/", ".work/"))]
    if sensitive:
        problems.append("TRACKED_SENSITIVE_PATH count=%d sample=%s" % (len(sensitive), sensitive[0]))
    else:
        print("TRACKED_CHECK_OK files=%d sensitive=0" % len(tracked_paths))

    # A credential inside the repo would be a leak, not a copy.
    for root, _dirs, names in os.walk(args.dest):
        for n in names:
            if n.endswith(".json"):
                problems.append("JSON_IN_IMAGE_FOLDER " + os.path.join(root, n))

    print("COPIED_COUNT=%d PROBLEMS=%d" % (copied, len(problems)))
    for p in problems:
        print("  " + p)
    return 0 if not problems else 2


if __name__ == "__main__":
    sys.exit(main())
