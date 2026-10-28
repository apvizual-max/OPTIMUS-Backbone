#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix the fallback ORDER as Hermes actually applies it.

THE DEFECT THIS CORRECTS
`hermes_cli/fallback_config.py::get_fallback_chain` merges the two keys in a
fixed order:

    for key in ("fallback_providers", "fallback_model"):

So `fallback_providers` is consumed FIRST and `fallback_model` is APPENDED
LAST, regardless of how either is written in the file. The policy Popy
ratified is:

    Tier 1 (on MiniMax): M3 -> M2.7 -> M2.7-highspeed
    Tier 2 (not on MiniMax): best free model by that profile's context tier

With the ladder in `fallback_model`, Hermes tried `minimax-oauth/MiniMax-M3`
(position 0) before the ladder ever started at position 5. The file looked
correct; the runtime order was not the policy. That is precisely the
"green log line is not a working product" failure.

THE FIX
Put the ENTIRE ordered chain in `fallback_providers`, which is the primary
source of truth and keeps its order. Leave `fallback_model` EMPTY (an empty
list) so it contributes nothing and cannot append. One source of truth, one
order, no merge surprise.

Verified afterwards by calling Hermes' own `get_fallback_chain`, not by reading
the file back.
"""
import io
import os
import re
import shutil
import datetime
import sys

sys.path.insert(0, r"C:\Users\apviz\AppData\Local\hermes\hermes-agent")
from hermes_cli.config import load_config_readonly          # noqa: E402
from hermes_cli.fallback_config import get_fallback_chain   # noqa: E402

HERMES = r"C:\Users\apviz\AppData\Local\hermes"
ROOT = os.path.join(HERMES, "config.yaml")
STAMP = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

LADDER = [("minimax", "MiniMax-M3"),
          ("minimax", "MiniMax-M2.7"),
          ("minimax-oauth", "MiniMax-M2.7-highspeed")]

ROLE = {  # profile -> (tier, free tier entries, largest window first)
    "prime":      ("1M",    [("openrouter", "anthropic/claude-sonnet-4"),
                            ("nous", "Hermes-4-405B")]),
    "assist":     ("1M",    [("openrouter", "anthropic/claude-sonnet-4"),
                            ("nous", "Hermes-4-405B")]),
    "cowork":     ("500K",  [("nous", "Hermes-4-405B"),
                            ("openrouter", "openai/gpt-4o"),
                            ("nous", "Hermes-4-70B")]),
    "designer":   ("500K",  [("nous", "Hermes-4-405B"),
                            ("openrouter", "openai/gpt-4o"),
                            ("nous", "Hermes-4-70B")]),
    "trader":     ("500K",  [("nous", "Hermes-4-405B"),
                            ("openrouter", "openai/gpt-4o"),
                            ("nous", "Hermes-4-70B")]),
    "coder":      ("200K",  [("openrouter", "openai/gpt-4o"),
                            ("nous", "Hermes-4-70B")]),
    "translator": ("200K",  [("openrouter", "openai/gpt-4o"),
                            ("nous", "Hermes-4-70B")]),
    "cli-prime":  ("small", [("nous", "Hermes-4-70B")]),
}

ROOT_FREE = [("minimax-oauth", "MiniMax-M3"),
             ("openrouter", "anthropic/claude-sonnet-4"),
             ("openrouter", "openai/gpt-4o"),
             ("nous", "Hermes-4-405B"),
             ("nous", "Hermes-4-70B")]


def read(p):
    with io.open(p, "r", encoding="utf-8") as fh:
        return fh.read()


def write(p, t):
    with io.open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write(t)


def chain_block(entries):
    out = ["fallback_providers:"]
    for prov, model in entries:
        out.append("  - provider: %s" % prov)
        out.append("    model: %s" % model)
    return "\n".join(out) + "\n"


def replace_block(text, key, block):
    """Replace `key:` through the end of its list, tolerating a comment block."""
    pat = re.compile(r"(?ms)^%s:\n(?:[^\n]*\n)*?(?=^[A-Za-z_][A-Za-z0-9_]*:|\Z)" % key)
    if not pat.search(text):
        raise SystemExit("ABORT: %s not found" % key)
    return pat.sub(block, text, count=1)


def main():
    print("=" * 74)
    print("FALLBACK ORDER CORRECTION.  stamp:", STAMP)
    print("=" * 74)

    # ---------------- root ----------------
    t = read(ROOT)
    root_chain = LADDER + [e for e in ROOT_FREE
                           if e not in LADDER and e != ("minimax", "MiniMax-M3")]
    t = replace_block(t, "fallback_providers", chain_block(root_chain))
    t = replace_block(t, "fallback_model",
                      "fallback_model: []   # superseded: folded into "
                      "fallback_providers so the order is the policy\n")
    shutil.copy2(ROOT, ROOT + ".bak-order-" + STAMP)
    write(ROOT, t)
    print("  root: %d entries in fallback_providers, fallback_model emptied"
          % len(root_chain))

    # ---------------- profiles ----------------
    for name, (tier, free) in sorted(ROLE.items()):
        p = os.path.join(HERMES, "profiles", name, "config.yaml")
        if not os.path.isfile(p):
            print("  %-11s skipped (no config.yaml)" % name)
            continue
        pt = read(p)
        chain = LADDER + [e for e in free if e not in LADDER]
        pt = replace_block(pt, "fallback_model", chain_block(chain))
        pt = re.sub(r"(?m)^_context_tier:.*$", "_context_tier: %s" % tier, pt)
        shutil.copy2(p, p + ".bak-order-" + STAMP)
        write(p, pt)
        print("  %-11s tier=%-6s %d entries" % (name, tier, len(chain)))

    # ---------------- verify with Hermes' own code ----------------
    print("\nVERIFY via hermes_cli.get_fallback_chain() on the ROOT config:")
    cfg = load_config_readonly()
    chain = get_fallback_chain(cfg)
    for i, e in enumerate(chain):
        print("   %2d. %-16s %s" % (i, e.get("provider"), e.get("model")))
    pairs = [(e.get("provider"), e.get("model")) for e in chain]
    assert pairs[:3] == LADDER, "TIER 1 IS NOT FIRST: %s" % pairs[:3]
    assert (cfg.get("model") or {}).get("default") == "MiniMax-M3"
    assert not any("llama-3.3-70b" in m for _, m in pairs), "old free scalar live"
    assert len(pairs) == len(set(pairs)), "duplicates in the chain"
    print("\nASSERTIONS PASSED - the runtime chain now starts with the MiniMax ladder")


if __name__ == "__main__":
    main()
