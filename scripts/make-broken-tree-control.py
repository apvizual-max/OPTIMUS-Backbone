"""Builds a control repository whose main tree carries an invalid path entry.

Purpose: a verification script that cannot fail is not a check. This script
produces the exact defect class that broke SENTINEL_PRIME on 2026-10-28 - a root
tree entry whose name contains ':', which git refuses to check out on Windows -
so a verifier can be shown to BLOCK it, not only shown to pass.

Usage:
    python scripts/make-broken-tree-control.py [target_dir]

Prints the path of the control repository on stdout. Deletes nothing.

The tree is built with plumbing on purpose (mktree -> commit-tree -> update-ref),
the same way the real repair was built, because a normal `git add` with an
absolute path is the accident that creates such an entry in the first place.
"""
import os
import subprocess
import sys

# The literal directory name that broke the real repository, backslash by backslash.
BOGUS_NAME = b"C:\\Users\\apviz\\.minimax-agent\\projects\\SENTINEL_PRIME"


def git(cwd, *args, **kw):
    return subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True, **kw)


def main():
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        temp = os.environ.get("TEMP") or os.environ.get("TMP") or "."
        target = os.path.join(temp, "sentinel-broken-tree-control")
    os.makedirs(target, exist_ok=True)
    git(target, "init", "-q")
    git(target, "symbolic-ref", "HEAD", "refs/heads/main")

    blob = git(target, "hash-object", "-w", "--stdin", input=b"control payload\n")
    if blob.returncode != 0:
        sys.stderr.write("hash-object failed: " + blob.stderr.decode("utf-8", "replace"))
        return 1
    blob_sha = blob.stdout.strip().decode()

    # a subtree with one ordinary file, to be filed under the invalid name
    subtree = git(target, "mktree",
                  input=b"100644 blob " + blob_sha.encode() + b"\tfile.txt\n")
    if subtree.returncode != 0:
        sys.stderr.write("mktree (subtree) failed: " + subtree.stderr.decode("utf-8", "replace"))
        return 1
    subtree_sha = subtree.stdout.strip().decode()

    # the root tree: that subtree under a name that contains ':'
    root = git(target, "mktree",
               input=b"040000 tree " + subtree_sha.encode() + b"\t" + BOGUS_NAME + b"\n")
    if root.returncode != 0:
        sys.stderr.write("mktree (root) failed: " + root.stderr.decode("utf-8", "replace"))
        return 1
    root_sha = root.stdout.strip().decode()

    commit = git(target, "commit-tree", root_sha, "-m",
                 "control: root tree with an invalid path entry")
    if commit.returncode != 0:
        sys.stderr.write("commit-tree failed: " + commit.stderr.decode("utf-8", "replace"))
        return 1
    commit_sha = commit.stdout.strip().decode()
    git(target, "update-ref", "refs/heads/main", commit_sha)

    # the verifier needs a remote to query and to clone from: point it at the
    # control repository itself.
    git(target, "remote", "remove", "origin")
    git(target, "remote", "add", "origin", target)

    print("control_repo=" + target)
    print("commit=" + commit_sha)
    print("invalid_entry=" + BOGUS_NAME.decode("utf-8", "replace"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
