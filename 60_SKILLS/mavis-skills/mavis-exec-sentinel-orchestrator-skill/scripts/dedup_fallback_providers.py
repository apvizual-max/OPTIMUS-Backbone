#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
De-duplicate `fallback_providers` against the new MiniMax ladder.

The previous script COMPUTED the dedup and printed "9 kept" but never wrote it.
The config still held 14 entries with 5 duplicate minimax/MiniMax-M3 routes.
A computed result that is not applied is a green log line and nothing more.

This one rebuilds the list, writes it, then re-reads the file from disk and
asserts against the parsed bytes. It does not trust its own arithmetic.
"""
import io
import re
import os
import shutil
import datetime

CONFIG = r"C:\Users\apviz\AppData\Local\hermes\config.yaml"
STAMP = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

LADDER = {("minimax", "MiniMax-M3"),
          ("minimax", "MiniMax-M2.7"),
          ("minimax-oauth", "MiniMax-M2.7-highspeed")}

# The free tier, in role-tier order. `default/prime/assist` want the largest
# window; `cli-prime` is last because the CLI tolerates the smallest.
FREE_TIER = [
    ("openrouter", "anthropic/claude-sonnet-4"),
    ("openrouter", "openai/gpt-4o"),
    ("nous", "Hermes-4-405B"),
    ("nous", "Hermes-4-70B"),
    ("minimax-oauth", "MiniMax-M3"),
]


def main():
    t = io.open(CONFIG, encoding="utf-8").read()

    m = re.search(r"(?ms)^fallback_providers:\n((?:  - provider: [^\n]*\n    model: [^\n]*\n)+)", t)
    if not m:
        raise SystemExit("ABORT: fallback_providers not in the expected shape")

    entries = re.findall(r"  - provider: (\S+)\n    model: (\S+)", m.group(1))
    before = len(entries)
    print("on disk before: %d entries" % before)

    # Drop exact duplicates of each other, and anything the ladder already covers.
    seen, kept, dropped = set(), [], []
    for prov, model in entries + FREE_TIER:
        key = (prov, model)
        if key in LADDER:
            dropped.append((prov, model, "covered by ladder"))
            continue
        if key in seen:
            dropped.append((prov, model, "duplicate"))
            continue
        seen.add(key)
        kept.append((prov, model))

    block = "fallback_providers:\n" + "".join(
        "  - provider: %s\n    model: %s\n" % (p, mo) for p, mo in kept)
    t = t[:m.start()] + block + t[m.end():]

    shutil.copy2(CONFIG, CONFIG + ".bak-dedup-" + STAMP)
    io.open(CONFIG, "w", encoding="utf-8", newline="").write(t)
    print("wrote %d entries" % len(kept))
    for p, mo, why in dropped:
        print("   dropped %-16s %-24s (%s)" % (p, mo, why))

    # ---- verify against the bytes actually on disk ----
    import yaml
    cfg = yaml.safe_load(io.open(CONFIG, encoding="utf-8").read())
    fb = cfg.get("fallback_providers") or []
    fm = cfg.get("fallback_model") or []
    print("\nre-read from disk:")
    print("  fallback_model      : %s" % [(e.get("provider"), e.get("model")) for e in fm])
    print("  fallback_providers  : %d entries" % len(fb))
    for e in fb:
        print("      %-16s %s" % (e.get("provider"), e.get("model")))

    pairs = [(e.get("provider"), e.get("model")) for e in fb]
    assert len(pairs) == len(set(pairs)), "duplicates still present!"
    assert not (set(pairs) & LADDER), "ladder routes still duplicated in the list!"
    md = cfg.get("model") or {}
    assert md.get("default") == "MiniMax-M3" and md.get("provider") == "minimax"
    print("\nASSERTIONS PASSED (no duplicates, no ladder overlap, primary intact)")
    print("backup: %s" % os.path.basename(CONFIG + ".bak-dedup-" + STAMP))


if __name__ == "__main__":
    main()
