<!-- SOT-STATUS-BANNER
  Added 2026-10-02 10:46 by scripts\stamp-doc-status.ps1

  THIS IS A POINT-IN-TIME DOCUMENT: an assessment of the minimax-h3-skills plugin.

  It is deliberately NOT rewritten -- rewriting it would destroy the record of
  what was true when it was written. For the CURRENT system state read:

    POPY_MiniMax_OPTIMUS_Status_Report-10-02-2026.md   <- current state, for Popy
    mavis-minimax-optimus-system                        <- skill: restore + config SOT
    mavis-minimax-index-folder-update                   <- skill: how to index this folder
    optimus status   /  cc start   /  cc guard          <- live truth, measured
-->
# Assessment: `minimax-h3-skills` Plugin

**Date**: 2026-09-18
**Author**: Mavis (MiniMax Code orchestrator)
**Status**: Plugin staged, partially usable from this session
**Verdict**: Major expansion of the swarm's content-generation capability, but only **1 of 9 skills** is portable into Mavis's current MiniMax Code runtime. The other 8 require the **MiniMax Hub agent** which is **not installed** on this station.

---

## §1 What's actually here

**Plugin on disk**: `C:\Users\apviz\.minimax\v2\plugin-cache\official\sha256-tree-v1-c2d6874982eb435598007d287f288d6c1d8a92fa8c91550848c672dc9c567e67\` — **41 files, 665.5 KB**

**Skills delivered** (9 total):

| # | Skill | Portable to Mavis? | Capability |
|---|---|---|---|
| 1 | `h3-prompt-writing` | ✅ Yes (no API needed) | Foundational: rewrites multimodal requests into MiniMax H3 prompt format (T2VA / I2VA / FL2VA / L2VA / Ref2VA modes) |
| 2 | `3d-animation-short-generator` | ❌ Requires MiniMax Hub | End-to-end 3D animated short workflows with character/scene cards, shot planning, BGM |
| 3 | `brand-promo-video-generator` | ❌ Requires MiniMax Hub | Promotional videos from brand assets, logos, product images |
| 4 | `co-op-game-intro-generator` | ❌ Requires MiniMax Hub | 2-player co-op game menu/intro animations |
| 5 | `handdrawn-live-video-generator` | ❌ Requires MiniMax Hub | Hand-drawn glowing animation + live-action fusion, 15s 16:9 |
| 6 | `minimalist-product-ad-generator` | ❌ Requires MiniMax Hub | E-commerce minimalist product ad shorts |
| 7 | `music-video-subtitle-generator` | ❌ Requires MiniMax Hub | Beat-reactive spatial typography MVs, lyric-driven visuals |
| 8 | `paper-collage-explainer-generator` | ❌ Requires MiniMax Hub | Halftone paper-collage explainer videos with tactile stop-motion |
| 9 | `papercraft-stop-motion-explainer` | ❌ Requires MiniMax Hub | Papercraft / diorama / pop-up-book stop-motion explainers |

Each of the 8 generators has a `compatibility:` frontmatter field that says explicitly:

> "Requires the MiniMax Hub agent (canvas workspace and hub_* tools); not portable to generic agent harnesses."

`h3-prompt-writing` is the only one whose `compatibility:` field says:

> "Portable to any agent that can read local files — no external API calls, MiniMax Hub tools, or proprietary runtime required."

So this is **by design**, not a configuration issue.

## §2 What's missing: the MiniMax Hub agent

The 8 generator skills expect these tools to exist at runtime:

- `hub_canvas_get_node`
- `hub_canvas_group_recent_outputs`
- `hub_generate_image`
- `hub_generate_video`
- `hub_analyse_media`
- `hub_image_search`
- `webfetch` (one generator)

**None of these tools are present in the current Mavis runtime.**

I probed the standard install locations for the MiniMax Hub agent:

- `C:\Users\apviz\.minimax\.minimax-hub-agent` → not found
- `C:\Users\apviz\AppData\Local\MiniMax Hub` → not found
- `C:\Program Files\MiniMax Hub` → not found
- Hub CLI on PATH (`minimax-hub`, `hub`, `minimax-hub-cli`, `mhub`) → none found

The Hub agent is **not installed** on this station. Until it is, the 8 generator skills cannot run end-to-end.

## §3 What IS usable right now in Mavis's session

- `h3-prompt-writing` — fully functional. Mavis can load the skill, read `references/base-en.txt` (15.7 KB) and `references/ref-en.txt` (23.5 KB), and write MiniMax H3-compliant prompts that Popy pastes into the MiniMax Hub agent manually.
- The other 8 skills are discoverable by name (so Mavis can describe what they'd do) but their workflow bodies cannot execute in this session.

## §4 Natural integration points with OPTIMUS Prime

Popy already has rich SENTINEL Character assets at `D:\Alex_Knowlege_Vault\03_Resources\03_7-SENTINEL_Character\`:

| Folder | Contents | Natural plugin skill |
|---|---|---|
| `AUDIO/` | 4 Romanian-prose `.m4a` files (proverbs, Optimus logic, rituals, sovereign AI) | `music-video-subtitle-generator` (beat-reactive lyric typography) |
| `BRAIN/` | 6 numbered design docs + main PNG + image/video sub-folders | `handdrawn-live-video-generator` (SENTINEL Brain aesthetic) |
| `CHARACTER/` | 8 portrait files (Gemini + custom) | `minimalist-product-ad-generator` (SENTINEL character promo) |
| `Photo Seeds/` | 8 photo seeds | `brand-promo-video-generator` (asset provenance pattern matches) |
| `SCENES/` | 4 scene renders (AI command center, futuristic gateway, holographic grid) | `3d-animation-short-generator` (scene continuity source) |
| `VIDEO/` | 17+ cinematic clips | `papercraft-stop-motion-explainer` (compress into explainer package) |

Plus the doctrinal material at `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\- ORCHESTRATOR - Sys Folder - Hermes Default\SF_IA - IDENTITATE_AXIOMA\SF_IA - 963_PROVERBE_COMPLET.md` (25-axe decision matrix) is a natural target for `paper-collage-explainer-generator` and `papercraft-stop-motion-explainer`.

## §5 Two paths forward (R0)

**Option A — install the MiniMax Hub agent** (full pipeline)
- Pros: all 9 skills become end-to-end runnable from the Hub agent's canvas workspace.
- Cons: requires a separate install / setup of the Hub agent runtime on this station. Not currently on disk.

**Option B — keep using `h3-prompt-writing` from Mavis** (text-only)
- Pros: zero install. Mavis produces MiniMax H3-compliant prompts; Popy pastes them into the Hub agent (or wherever MiniMax H3 lives) by hand.
- Cons: Mavis doesn't get end-to-end video generation. The 8 generators stay dormant.

**My recommendation**: start with **Option B** (no install, Mavis is immediately productive on prompt generation), then evaluate **Option A** later when there's a concrete video project. The bottleneck is not prompt-writing — Mavis can produce H3 prompts now — but image/video model access, which depends on Hub agent setup.

## §6 JURNAL_OGLINDA entry

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | Plugin `minimax-h3-skills` staged + assessed | 41 files / 665.5 KB at `C:\Users\apviz\.minimax\v2\plugin-cache\official\sha256-tree-v1-c2d6874982eb435598007d287f288d6c1d8a92fa8c91550848c672dc9c567e67\`. 9 skills total; 1 portable (`h3-prompt-writing`), 8 require MiniMax Hub agent runtime (not installed). Compatibility: portable skill works in Mavis; Hub-required skills are dormant until Hub agent is wired. |

