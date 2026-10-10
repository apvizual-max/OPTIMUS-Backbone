#!/usr/bin/env python3
"""
extract_wayland_workflows.py — materialize Wayland's bundled workflows to disk.

Wayland ships its 71 workflow SKILL.md bodies as a single packed blob
(`skill-bodies.bin`) plus an offset map (`skill-bodies.offsets.json`).
This script unpacks them into a readable tree and writes an index, so Mavis
can search and read Wayland workflows directly.

Read-only against the Wayland install; writes only under the output dir.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

DEFAULT_SRC = Path(r"C:\Program Files\Wayland\resources\bundled-workflows")
DEFAULT_OUT = Path(
    r"C:\Users\apviz\.minimax-agent\projects\20_BRIDGES\wayland\workflows"
)


def load_index(src: Path) -> dict:
    return json.loads((src / "skill-bodies.offsets.json").read_text(encoding="utf-8"))


def extract(src: Path, out: Path) -> dict:
    blob = (src / "skill-bodies.bin").read_bytes()
    index = load_index(src)
    entries = index.get("entries", {})

    out.mkdir(parents=True, exist_ok=True)
    written, failed = [], []

    for rel, (offset, length) in sorted(entries.items()):
        chunk = blob[offset:offset + length]
        try:
            text = chunk.decode("utf-8")
        except UnicodeDecodeError as e:
            failed.append({"path": rel, "error": f"utf-8 decode: {e}"})
            continue
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8", newline="\n")
        written.append({
            "path": rel,
            "bytes": length,
            "sha256": hashlib.sha256(chunk).hexdigest()[:16],
            "first_line": text.splitlines()[0] if text.splitlines() else "",
        })

    manifest = {
        "source": str(src),
        "output": str(out),
        "blob_bytes": len(blob),
        "index_version": index.get("version"),
        "extracted": len(written),
        "failed": len(failed),
        "failures": failed,
        "workflows": written,
    }
    (out / "_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return manifest


def render_index(m: dict) -> str:
    lines = [
        "# Wayland Workflows — Extracted Index",
        "",
        f"**Source**: `{m['source']}`",
        f"**Output**: `{m['output']}`",
        f"**Extracted**: {m['extracted']} workflows from a {m['blob_bytes']:,}-byte packed blob",
        f"**Failed**: {m['failed']}",
        "",
        "These are Wayland's bundled agentic-cowork workflows, unpacked from",
        "`skill-bodies.bin` + `skill-bodies.offsets.json`. Each is a real `SKILL.md`.",
        "",
        "| # | Workflow | Bytes | SHA256 |",
        "|---|---|---|---|",
    ]
    for i, w in enumerate(m["workflows"], 1):
        name = w["path"].split("/")[-2] if "/" in w["path"] else w["path"]
        lines.append(f"| {i} | `{name}` | {w['bytes']:,} | `{w['sha256']}` |")
    lines += [
        "",
        "## How Mavis uses these",
        "",
        "1. Search `bodies/**/SKILL.md` for the task shape (contract review, deck build, ICP).",
        "2. Read the matching SKILL.md for the full procedure.",
        "3. Execute the procedure inline, following the doctrine gates in",
        "   `SENTINEL_OPERATIONAL_DOCTRINE.md` (R33, Triple Crunch, SOUL/CONSTINTA).",
        "",
        "These are workflow *bodies*, not tools. Wayland still has no CLI, so Mavis",
        "executes the procedure itself rather than dispatching to a Wayland binary.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(DEFAULT_SRC))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    m = extract(Path(args.src), Path(args.out))
    (Path(args.out) / "README.md").write_text(
        render_index(m), encoding="utf-8", newline="\n"
    )
    print(f"extracted {m['extracted']} workflows, {m['failed']} failed")
    print(f"-> {args.out}")
    for f in m["failures"]:
        print("  FAIL", f["path"], f["error"])
    return 0 if m["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
