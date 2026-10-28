#!/usr/bin/env python3
# append-busola.py - append rows to BUSOLA.md ON PLACE, never replace.
#
# The busola is Popy's compass through the project. The rule: the list is
# NEVER rewritten - rows are added, and a row that no longer fits is closed
# with "completed"/"cancelled" plus a reason, never deleted. This script can
# therefore only APPEND. It refuses to truncate, and it reports the row count
# before and after so the change is measurable on the object.
#
# It also verifies, after writing, that no row was lost and no character was
# corrupted in transit (the U+FFFD defect measured on 2026-10-27).
#
# Usage: python append-busola.py --file <path> --block <file>

import argparse
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--block", required=True, help="file with the text to append")
    args = ap.parse_args()

    with open(args.file, "rb") as fh:
        before = fh.read()
    before_text = before.decode("utf-8")
    before_rows = len([l for l in before_text.splitlines() if l.strip()])

    with open(args.block, "rb") as fh:
        block = fh.read().decode("utf-8")

    if "\ufffd" in block:
        print("ERROR: the block contains a corrupted character (U+FFFD)")
        return 1

    if not before_text.endswith("\n"):
        block = "\n" + block

    with open(args.file, "ab") as fh:
        fh.write(block.encode("utf-8"))

    with open(args.file, "rb") as fh:
        after = fh.read()
    after_text = after.decode("utf-8")

    if not after_text.startswith(before_text):
        print("ERROR: the previous content is not intact")
        return 1
    if "\ufffd" in after_text:
        print("ERROR: a corrupted character (U+FFFD) is present after the write")
        return 1

    after_rows = len([l for l in after_text.splitlines() if l.strip()])
    print("BUSOLA_ROWS_BEFORE=%d" % before_rows)
    print("BUSOLA_ROWS_AFTER=%d" % after_rows)
    print("BUSOLA_ROWS_ADDED=%d" % (after_rows - before_rows))
    print("BUSOLA_BYTES_BEFORE=%d" % len(before))
    print("BUSOLA_BYTES_AFTER=%d" % len(after))
    print("PREVIOUS_CONTENT_INTACT=1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
