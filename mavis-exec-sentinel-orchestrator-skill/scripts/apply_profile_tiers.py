#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Per-profile fallback tiers - Popy's context-size policy, expressed durably.

Popy: "IF not on minimax, then use the best available free model based on
CONTEXT SIZE for each Hermes profile defined separately in the Profile
Definition ROLE. Orchestrator Default means 1M context window, for sure,
Prime and Assist the same... coder and CLI can use smaller context model,
especially CLI, Translator, again it can be small and local... define it
broadly as we will be adding routers for free quota aggregation."

Honest constraint, stated once and encoded in the files: Hermes screens a
fallback candidate by context window only for the `compression` task
(agent/auxiliary_client.py::_task_minimum_context_length returns None for every
other task). There is no per-profile context field to set. So the tier is
expressed as CHAIN ORDER inside each profile's own config.yaml, which is the
durable lever available until Omnirouter aggregates free quota.

Root already has the Tier-1 MiniMax ladder. Each profile gets:
  * the MiniMax ladder first (it is the preferred tier, always)
  * then its own free tier, ordered large-window -> small-window

The role -> tier mapping is written into each profile's config as
`_context_tier` (unknown keys are ignored by the loader; this is
documentation-as-configuration, and it is verified below).

Idempotent: re-running replaces the block rather than appending.
"""
import io
import os
import re
import shutil
import datetime
import yaml

HERMES = r"C:\Users\apviz\AppData\Local\hermes"
PROFILES = os.path.join(HERMES, "profiles")
STAMP = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

LADDER = [("minimax", "MiniMax-M3"),
          ("minimax", "MiniMax-M2.7"),
          ("minimax-oauth", "MiniMax-M2.7-highspeed")]

# Free tier, ordered by context window: largest first.
FREE = {
    "1M":    [("openrouter", "anthropic/claude-sonnet-4"),
              ("nous", "Hermes-4-405B")],
    "500K":  [("nous", "Hermes-4-405B"),
              ("openrouter", "openai/gpt-4o"),
              ("nous", "Hermes-4-70B")],
    "200K":  [("openrouter", "openai/gpt-4o"),
              ("nous", "Hermes-4-70B")],
    "small": [("nous", "Hermes-4-70B")],
}

# Popy's role definition.
ROLE = {
    "default":    ("1M",    "Orchestrator - full window, this is the brain"),
    "prime":      ("1M",    "Chief executive - full window"),
    "assist":     ("1M",    "Personal assistant - full window"),
    "cowork":     ("500K",  "Task planning / management"),
    "designer":   ("500K",  "Creative asset work, large prompts"),
    "trader":     ("500K",  "Market analysis, long data"),
    "coder":      ("200K",  "Code editing, smaller window is sufficient"),
    "translator": ("200K",  "Translation, short-ish segments; may go local"),
    "cli-prime":  ("small", "CLI executor - smallest window, may be local"),
}

NOTE_TMPL = """
# ---------------------------------------------------------------------------
# PER-PROFILE FALLBACK TIER - ratified by Popy 2026-10-02, written by Mavis.
#
# ROLE      : {role}
# CONTEXT   : {tier}   (1M = 1,000,000+ window; small = may be local)
# TIER 1    : MiniMax ladder, always first - {ladder}
# TIER 2    : best available FREE model by context size, this profile's tier:
{free}
#
# WHY ORDER AND NOT A FIELD: Hermes screens a fallback by context window only
# for the `compression` task (agent/auxiliary_client.py::_task_minimum_context_
# length returns None for all other tasks). There is no per-profile context
# field. Ordering is the only durable lever until Omnirouter aggregates free
# quota, and it lives in this file so it survives restarts and app updates.
# ---------------------------------------------------------------------------
"""

BEGIN = "# BEGIN MANAGED FALLBACK TIER - Mavis 2026-10-02"
END = "# END MANAGED FALLBACK TIER"


def read(p):
    with io.open(p, "r", encoding="utf-8") as fh:
        return fh.read()


def write(p, t):
    with io.open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write(t)


def build_block(tier, role):
    lines = [BEGIN, "# ROLE: %s" % role, "# CONTEXT TIER: %s" % tier,
             NOTE_TMPL.format(role=role, tier=tier,
                              ladder=" -> ".join(m for _, m in LADDER),
                              free="\n".join("#   %-16s %s" % (p, m) for p, m in FREE[tier])).strip("\n"),
             "fallback_model:"]
    for prov, model in LADDER + FREE[tier]:
        lines.append("  - provider: %s" % prov)
        lines.append("    model: %s" % model)
    lines.append("_context_tier: %s" % tier)
    lines.append(END)
    return "\n".join(lines) + "\n"


def apply(path, tier, role):
    t = read(path)
    if BEGIN in t:
        pre = t.split(BEGIN)[0]
        post = t.split(END, 1)[1]
        t = pre.rstrip("\n") + "\n\n" + build_block(tier, role) + post.lstrip("\n")
    else:
        t = t.rstrip("\n") + "\n\n" + build_block(tier, role)
    shutil.copy2(path, path + ".bak-tier-" + STAMP)
    write(path, t)
    cfg = yaml.safe_load(read(path))
    fm = cfg.get("fallback_model") or []
    pairs = [(e.get("provider"), e.get("model")) for e in fm]
    assert pairs[:3] == LADDER, "%s: ladder not first" % os.path.basename(path)
    assert cfg.get("_context_tier") == tier, "%s: tier not set" % os.path.basename(path)
    assert len(pairs) == len(set(pairs)), "%s: duplicates" % os.path.basename(path)
    return len(pairs)


def main():
    print("=" * 74)
    print("PER-PROFILE FALLBACK TIERS.  stamp:", STAMP)
    print("=" * 74)
    total = 0
    for name in sorted(ROLE):
        d = os.path.join(PROFILES, name)
        cfg = os.path.join(d, "config.yaml")
        if not os.path.isfile(cfg):
            print("  %-11s no config.yaml (inherits root) - root ladder applies" % name)
            continue
        tier, role = ROLE[name]
        n = apply(cfg, tier, role)
        total += 1
        print("  %-11s tier=%-6s %d fallback entries, verified" % (name, tier, n))
    print("\nprofiles written: %d" % total)
    print("Each file re-parsed and asserted after the write.")


if __name__ == "__main__":
    main()
