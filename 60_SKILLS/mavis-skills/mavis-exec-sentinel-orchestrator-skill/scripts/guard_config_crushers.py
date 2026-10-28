#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Guard the CONFIG-CRUSHER skills found by skill_guard.py.

Popy's stated risk, verbatim intent: "Ensure that skills don't crush the
config. You got it! That's the basic risk you need to eliminate because that's
what happened to us. That's why we spent another day out of frustration."

Three unguarded procedures were found that would each destroy the fallback
policy ratified today:

  1. hermes-gateway-restore  - "Copy `gateway_config.yaml` to root
     `config.yaml`. Restore all 8 profile `config.yaml` files". A whole-tree
     overwrite of exactly the files the policy lives in.
  2. optimus-prime-sentinel - an "escape hatch" that runs
     `hermes config set model.default ...` / `model.provider ollama` /
     `fallback_providers '["ollama"]'`. This is the single most dangerous line
     found: it re-points the whole system at a local backend.
  3. sentinel-self-setup-autonomy - `hermes config set model.default
     "MODEL_NAME_HERE"` with `provider: openrouter`, plus a pointer to the two
     free-model procedures that are already disabled.

Each gets a targeted banner naming the ratified policy. Nothing is deleted:
the procedures stay auditable, and each says what the correct action is now.
Guarded files are also synced where a byte-paired twin exists in the agent tree.
"""
import io
import os
import re
import shutil
import datetime

STAMP = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

POLICY = """# ---------------------------------------------------------------------------
# FALLBACK POLICY - ratified by Popy 2026-10-02, implemented and verified.
#
#   Tier 1 (on MiniMax), in this exact order:
#     1. minimax         / MiniMax-M3
#     2. minimax         / MiniMax-M2.7
#     3. minimax-oauth   / MiniMax-M2.7-highspeed      ("fast", last resort)
#
#   Tier 2 (not on MiniMax): the best available FREE model chosen by context
#   size, the size being set per profile in the Profile Definition role:
#     1M    default, prime, assist
#     500K  cowork, designer, trader
#     200K  coder, translator
#     small cli-prime   (may be local)
#
#   Root and every profile write the whole ordered chain into
#   `fallback_providers` and leave `fallback_model` empty. That is deliberate:
#   hermes_cli/fallback_config.py::get_fallback_chain consumes
#   `fallback_providers` FIRST and APPENDS `fallback_model` last, so a ladder
#   left in `fallback_model` would be tried after the other routes.
#
#   Verified through Hermes' own loader, not by reading the file.
# ---------------------------------------------------------------------------
"""

# (path, anchor line, banner to insert BEFORE that line)
GUARDS = [
    (
        r"C:\Users\apviz\.minimax\skills\hermes-gateway-restore\SKILL.md",
        "2. **Deploy Configuration State**:",
        "## ⛔ STEP 2 IS PROHIBITED WITHOUT AN EXPLICIT R0 — 2026-10-02\n\n"
        + POLICY + "\n"
        "**Step 2 below would overwrite the ratified policy.** It copies a\n"
        "`gateway_config.yaml` snapshot over the live root `config.yaml` and\n"
        "restores all 8 profile `config.yaml` files wholesale. That snapshot\n"
        "predates this policy, so running it silently reverts Tier 1 and the\n"
        "per-profile context tiers, and reintroduces whatever the live config\n"
        "had fixed since the backup was taken.\n\n"
        "**Do not run step 2 as part of a gateway restore.** If the gateway is\n"
        "down, restore the *runtime* (steps 1, 3, 4, 5, 6) and leave\n"
        "configuration alone. If configuration really must be redeployed, first\n"
        "run `scripts/skill_guard.py` and record the drift you are about to\n"
        "cause, then get Popy's explicit go.\n\n"
        "---\n\n",
    ),
    (
        r"C:\Users\apviz\.minimax\skills\behave-system_behavioral_protocols\references"
        r"\optimus-prime-sentinel\instructions.md",
        "## LOCAL-MODEL ESCAPE HATCH FOR CONTEXT-LOSS ON MODEL SWITCHES",
        "## ⛔ THE ESCAPE HATCH BELOW IS PROHIBITED — 2026-10-02\n\n"
        + POLICY + "\n"
        "**The procedure below is disabled.** Its step 2 runs\n"
        "`hermes config set model.default`, `model.provider ollama` and\n"
        "`fallback_providers '[\"ollama\"]'` — it re-points the entire system at\n"
        "a local backend and discards the MiniMax ladder. It was written for a\n"
        "different machine state and is the most destructive instruction found\n"
        "in the skill trees.\n\n"
        "**Context loss on a model switch is not fixed by re-pointing routing.**\n"
        "If the user asks for a local-only escape hatch:\n"
        "  1. Say plainly that this would drop the ratified Tier 1 and the\n"
        "     per-profile context tiers.\n"
        "  2. Ask for the explicit R0, quoting this banner.\n"
        "  3. Only then make the change, and re-run `scripts/skill_guard.py`\n"
        "     afterwards to record the new state.\n"
        "**Never do it autonomously.**\n\n"
        "---\n\n",
    ),
    (
        r"C:\Users\apviz\.minimax\skills\behave-system_behavioral_protocols\references"
        r"\sentinel-self-setup-autonomy\instructions.md",
        "**Changing active model:**",
        "## ⛔ MODEL-CHANGING COMMANDS ARE PROHIBITED WITHOUT R0 — 2026-10-02\n\n"
        + POLICY + "\n"
        "**The `hermes config set` block below is disabled.** It points\n"
        "`model.default` at a placeholder and `model.provider` at `openrouter`,\n"
        "which is how the default model got re-routed through a free tier in the\n"
        "first place. The `nvidia/nemotron-3-ultra-550b-a55b:free` default shown\n"
        "above it is also retired.\n\n"
        "**Both free-model procedures it points to are disabled as of 2026-10-02:**\n"
        "`update-openrouter-free-models` and `openrouter-free-models-healer`.\n"
        "The second one is a boot-time self-healer that rewrites `models.py` and\n"
        "deletes `provider_models_cache.json`; it is the proven root cause of\n"
        "four separate config restores. Do not install or re-run it.\n\n"
        "To change routing, edit the `fallback_providers` chain described above,\n"
        "then verify with `scripts/skill_guard.py`.\n\n"
        "---\n\n",
    ),
]

# Byte-paired twins: the same guard must exist in the agent's own tree.
TWIN_OF = {
    r"C:\Users\apviz\.minimax\skills\behave-system_behavioral_protocols\references"
    r"\optimus-prime-sentinel\instructions.md":
        r"C:\Users\apviz\.minimax\agents\mavis\skills\mavis-exec-sentinel-orchestrator-skill\references"
        r"\optimus-prime-sentinel\instructions.md",
    r"C:\Users\apviz\.minimax\skills\behave-system_behavioral_protocols\references"
    r"\sentinel-self-setup-autonomy\instructions.md":
        r"C:\Users\apviz\.minimax\agents\mavis\skills\mavis-exec-sentinel-orchestrator-skill\references"
        r"\sentinel-self-setup-autonomy\instructions.md",
}


def read(p):
    with io.open(p, "r", encoding="utf-8") as fh:
        return fh.read()


def write(p, t):
    with io.open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write(t)


def guard(path, anchor, banner):
    if not os.path.isfile(path):
        print("  [skip] not present: %s" % os.path.basename(os.path.dirname(path)))
        return None
    t = read(path)
    marker = banner.strip().splitlines()[0]
    if marker in t:
        print("  [skip] already guarded: %s" % os.path.basename(os.path.dirname(path)))
        return t
    if t.count(anchor) != 1:
        raise SystemExit("ABORT %s: anchor %r found %d times"
                         % (path, anchor, t.count(anchor)))
    t = t.replace(anchor, banner + anchor, 1)
    shutil.copy2(path, path + ".bak-guard-" + STAMP)
    write(path, t)
    print("  [guarded] %-46s %6dB" % (os.path.basename(os.path.dirname(path))[:46],
                                      len(t.encode("utf-8"))))
    return t


def main():
    print("=" * 74)
    print("CONFIG-CRUSHER GUARDS.  stamp:", STAMP)
    print("=" * 74)
    for path, anchor, banner in GUARDS:
        new = guard(path, anchor, banner)
        twin = TWIN_OF.get(path)
        if twin and new is not None:
            guard(twin, anchor, banner)
    print("\nEach guarded file keeps its original procedure below the banner.")


if __name__ == "__main__":
    main()
