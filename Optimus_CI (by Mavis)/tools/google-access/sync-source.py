#!/usr/bin/env python3
# sync-source.py - refresh the project copy of the Google Access source from
# the live one, and PROVE the copy is the source of the running system.
#
# WHY THIS EXISTS
# tools\google-access\ is the reconstructible copy: the container image is
# built from server.mjs, and the host-side tools live beside it. Measured
# 2026-10-27: the live source changed (server.mjs 37 848 -> 40 919 bytes,
# image 1.0.3 -> 1.0.4, tools 25 -> 26) while the project copy stayed at the
# previous revision. The project therefore claimed "reconstructible from
# GitHub" for a source it no longer held. A copy that is not checked is a
# copy that rots silently.
#
# This tool therefore does three things, in this order:
#   1. copies an ALLOW-LIST of source files (never the credential)
#   2. verifies each file byte-for-byte (SHA256) after the copy
#   3. verifies the live server.mjs is byte-identical to the server.mjs
#      INSIDE the running container - that is what "the source reproduces the
#      running system" means, and it is the only check that catches a source
#      edited after the image was built
#
# The credential never enters the image layer and never enters this tree: it
# lives in the mounted volume (data\credentials.json) and is excluded here.
#
# Exit codes:
#   0 = copied, verified, and the live source matches the running container
#   1 = a copy failed, a hash mismatched, a secret leaked, or the live source
#       does NOT match the running container (drift - reported, not hidden)
#   2 = the tool could not run (source or destination missing)
#
# ASCII ONLY.

import hashlib
import os
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SRC = os.path.join(
    os.environ.get("USERPROFILE", r"C:\Users\apviz"), ".minimax", "google-access"
)
DST = os.path.join(
    r"E:\Google\GDrive\GDrive-Second_Brain_PKMS\02_Areas\02-2-AI-SOT\CASA"
    r"\OPTIMUS - Prime\Optimus_CI (by Mavis)\tools\google-access"
)

# The image build inputs, plus the host-side tools that drive them.
FILES = [
    "server.mjs",
    "Dockerfile",
    ".dockerignore",
    "probe.mjs",
    "provision-grant.cjs",
    "watch-reauth.ps1",
    "consent-watcher.mjs",
    "mcp-call.mjs",
    "probe-services.mjs",
    "extendlm-provision.mjs",
]

# Never copied, never committed.
FORBIDDEN_DIRS = ("data", "logs", "state")
FORBIDDEN_NAMES = ("credentials.json",)

CONTAINER = "Google_Access"
IMAGE_PATH = "/app/server.mjs"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def container_server_hash():
    """SHA256 of the server.mjs inside the running container, or None."""
    try:
        out = subprocess.run(
            ["docker", "exec", CONTAINER, "sha256sum", IMAGE_PATH],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    parts = out.stdout.split()
    return parts[0].lower() if parts else None


def main():
    if not os.path.isdir(SRC):
        print("ERROR=live source not found: %s" % SRC)
        return 2
    if not os.path.isdir(DST):
        print("ERROR=project copy not found: %s" % DST)
        return 2

    problems = 0
    copied = 0

    print("=== COPY ===")
    for name in FILES:
        s = os.path.join(SRC, name)
        d = os.path.join(DST, name)
        if not os.path.isfile(s):
            # A tool that no longer exists is not an error: the live source
            # may have dropped it. Report it, do not fail on it.
            print("ABSENT_LIVE  %-24s (not copied)" % name)
            continue
        shutil.copy2(s, d)
        same = sha256(s) == sha256(d)
        print(
            "COPY        %-24s bytes=%-7d sha_match=%s"
            % (name, os.path.getsize(d), same)
        )
        if same:
            copied += 1
        else:
            problems += 1

    print("")
    print("=== LEAK CHECK (the destination must carry no credential) ===")
    leaked = []
    for root, dirs, files in os.walk(DST):
        for d in list(dirs):
            if d in FORBIDDEN_DIRS:
                leaked.append(os.path.join(root, d))
        for f in files:
            if f in FORBIDDEN_NAMES or f.endswith(".env") or f.endswith(".env.local"):
                leaked.append(os.path.join(root, f))
    print("LEAKED_PATHS=%d" % len(leaked))
    for l in leaked:
        print("LEAK=%s" % l)
    if leaked:
        problems += len(leaked)

    print("")
    print("=== RUNNING-SYSTEM CHECK ===")
    live_server = os.path.join(SRC, "server.mjs")
    live_hash = sha256(live_server) if os.path.isfile(live_server) else None
    img_hash = container_server_hash()
    if live_hash is None:
        print("LIVE_HASH=UNKNOWN (no live server.mjs)")
        problems += 1
    elif img_hash is None:
        print("IMAGE_HASH=UNKNOWN (container not reachable)")
        problems += 1
    elif live_hash == img_hash:
        print("MATCH=true  (the live source IS the source of the running container)")
        print("  sha256=%s" % live_hash)
    else:
        print("MATCH=false - the live source is NOT what the running container serves")
        print("  live  sha256=%s" % live_hash)
        print("  image sha256=%s" % img_hash)
        problems += 1

    print("")
    print("PROBLEMS=%d COPIED=%d" % (problems, copied))
    return 0 if problems == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
