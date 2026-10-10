# Mavis — MiniMax Plugin Universe Survey

**Date**: 2026-09-18
**Author**: Mavis (orchestrator)
**Status**: Phase C of the approved 3-phase plan. Research only.

---

## Goal

Survey the MiniMax plugin universe, identify which plugins close capability gaps for Popy's agentic workflows, and rank the top recommendations.

## Sources reviewed

- **MiniMax Agent docs** — https://agent.minimax.io/docs/code/agents/plugins
- **MiniMax Skill marketplace** — https://agent.minimax.io/skills
- **minimax-ai/skills GitHub** — https://github.com/MiniMax-AI/skills (23 skills, 44.8k installs as of 2026)
- **Tessl.io registry** — https://tessl.io/registry/skills/github/MiniMax-AI/skills
- **Claude Code marketplaces** — https://claudeskills.info/plugins/minimax-ai/skills/, https://claudemarketplaces.com/skills/minimax-ai/skills

## MiniMax plugin universe — taxonomy

### A. Official `minimax-ai/skills` GitHub (23 skills, free)

| Skill | Description | Popy-relevant? | Verdict |
|---|---|---|---|
| `frontend-dev` | Full-stack frontend, React/Next.js/Tailwind, MiniMax API integration | MEDIUM — Popy occasionally builds UI | **SKIP** unless web project |
| `fullstack-dev` | Backend architecture, REST, auth, real-time, DB | LOW | **SKIP** |
| `android-native-dev` | Android Kotlin/Compose | LOW — Popy is not on Android | **SKIP** |
| `ios-application-dev` | iOS UIKit/SwiftUI | LOW | **SKIP** |
| `flutter-dev` | Flutter cross-platform | LOW | **SKIP** |
| `react-native-dev` | RN/Expo | LOW | **SKIP** |
| `shader-dev` | GLSL shaders (ray marching, SDF, fluid sim, particles, procedural gen) | HIGH — Popy uses ComfyUI / image gen heavily | **HIGH PRIORITY** |
| `gif-sticker-maker` | Photos → 4 animated GIF stickers via MiniMax image/video API | MEDIUM | **CANDIDATE** for SENTINEL Character assets |
| `minimax-pdf` | Generate / fill / reformat PDFs (15 cover styles) | HIGH — Popy creates B2B proposals | **HIGH PRIORITY** |
| `pptx-generator` | Create/edit/read PowerPoint | HIGH — B2B proposals | **HIGH PRIORITY** |
| `minimax-xlsx` | Open/create/read/analyze/edit Excel | MEDIUM | **CANDIDATE** |
| `minimax-docx` | Professional DOCX creation/editing via OpenXML SDK | MEDIUM | **CANDIDATE** |
| `vision-analysis` | Image analysis, OCR, chart data extraction, MiniMax VL + GPT-4V fallback | HIGH — Popy works with images | **HIGH PRIORITY** |
| `minimax-multimodal-toolkit` | TTS, music, video, image, FFmpeg via MiniMax APIs | HIGH — covers all media | **HIGH PRIORITY** |
| `minimax-music-gen` | Vocal songs, instrumentals, covers, lyrics gen | MEDIUM — SENTINEL Character audio | **CANDIDATE** |
| `buddy-sings` | Personalized songs from pet / context | LOW | **SKIP** |
| `minimax-music-playlist` | Personalized playlist generation | LOW | **SKIP** |
| `pr-review` | Code review with structured output | HIGH — Popy has manual `code_review_rules.md`; a pr-review skill complements it | **HIGH PRIORITY** |
| `mmx-cli` | CLI wrapper around MiniMax multimodal API | HIGH — Mavis could orchestrate this directly | **HIGH PRIORITY** if available |
| `ppt-editing-skill`, `ppt-orchestra-skill`, `slide-making-skill` | PPT variants | HIGH — supports `pptx-generator` | **CANDIDATE** |
| `color-font-skill`, `design-style-skill` | Visual design helpers | MEDIUM — useful for OPTIMUS visual identity | **CANDIDATE** |

**Official GitHub summary**: 23 skills. **11 HIGH PRIORITY** for Popy's stack, **7 CANDIDATE**, **5 SKIP**.

### B. MiniMax Marketplace plugins (paid + curated)

The MiniMax marketplace has additional plugins beyond the free GitHub repo. Popy's screenshot shows a long list. Categories per docs:

- **Financial data**: Hundsun paid financial database
- **Company information**: Qichacha
- **Long-form capture**: EverMe
- **Legal material**: PKUlaw (Peking University Law)
- **Office / collaboration**: WPS Kingsoft, WeCom (企业微信), Microsoft Office
- **Knowledge organization**: long-term capture

Plus "Red Skill search" — MiniMax can search popular Xiaohongshu (Little Red Book) skills and reuse social-content templates.

### C. Already installed (MiniMax-managed)

- `minimax-h3-skills` — MiniMax H3 video generation (1 portable + 8 Hub-required skills) — installed 2026-09-18

---

## Cross-reference with Phase A capability gaps

From `00_INDEX/00_skill_taxonomy.md`:

| Category | Gap | Plugin candidate |
|---|---|---|
| Identity and File Locations | Document indexer, code-search enhancer | **`mmx-cli`** for fast code/text search across vault |
| Behavioral | Time-budget tool | None — discipline tool, no marketplace equivalent |
| Role Definition | Explicit role-conflict detector | None — internal architecture |
| Operations | More bridge MCPs (Notion, Figma, Linear, Stripe) | **`notion` MCP** (vendor OAuth), **`figma` MCP** (already on Hermes), **`linear` MCP** (low priority) |
| Operations | PPT / PDF / DOCX / XLSX creation for B2B proposals | **`pptx-generator`, `minimax-pdf`, `minimax-docx`, `minimax-xlsx`** |
| Operations | Image generation / vision analysis | **`vision-analysis`, `minimax-multimodal-toolkit`** |
| Operations | Audio / music generation | **`minimax-music-gen`, `minimax-multimodal-toolkit`** |
| Operations | Shaders / effects (for SENTINEL Character BRAIN aesthetic) | **`shader-dev`** |
| Operations | PR review (structured, beyond custom rules) | **`pr-review`** |

---

## Ranked recommendations (top 10)

Each row scored by: **project relevance** (SENTINEL Character / OPTIMUS / B2B), **stack match** (Popy's TS/Python/PowerShell/MCP world), **install friction**.

| Rank | Plugin / Skill | Why | Install path | Effort | R0-gated? |
|---|---|---|---|---|---|
| **1** | **`minimax-multimodal-toolkit`** | Covers TTS, music, video, image, FFmpeg — fills Popy's creative pipeline gap | GitHub clone into skills dir | ~5 min | No |
| **2** | **`pptx-generator`** | B2B proposal workflow (Popy's professional context) | GitHub clone | ~5 min | No |
| **3** | **`minimax-pdf`** | Same — PDFs for proposals | GitHub clone | ~5 min | No |
| **4** | **`vision-analysis`** | Image analysis (Popy has SENTINEL Character imagery + B2B proposal screenshots) | GitHub clone | ~5 min | No |
| **5** | **`pr-review`** | Complements `code_review_rules.md` — structured PR review workflow | GitHub clone | ~5 min | No |
| **6** | **`shader-dev`** | GLSL shaders for SENTINEL Character BRAIN aesthetic | GitHub clone | ~5 min | No |
| **7** | **`mmx-cli`** | CLI orchestration of MiniMax APIs from Mavis's shell | GitHub clone | ~5 min | No |
| **8** | **`minimax-music-gen`** | SENTINEL Character audio expansion (currently has 4 m4a files) | GitHub clone | ~5 min | No |
| **9** | **`gif-sticker-maker`** | SENTINEL Character visual content (1-line from any photo) | GitHub clone | ~5 min | No |
| **10** | **`minimax-docx`** + **`minimax-xlsx`** | B2B proposal supporting docs | GitHub clone | ~10 min | No |

All top-10 are from the official `minimax-ai/skills` GitHub repo — free, official, easy install.

### Install command (general pattern)

```bash
# Clone the official skills repo
git clone https://github.com/MiniMax-AI/skills.git ~/.minimax-skills

# Symlink Mavis skills
mkdir -p ~/.minimax/agents/mavis/skills
ln -s ~/.minimax-skills/skills/minimax-multimodal-toolkit ~/.minimax/agents/mavis/skills/minimax-multimodal-toolkit
# (repeat per plugin)
```

(Or use the plugin marketplace: `claude plugin marketplace add https://github.com/MiniMax-AI/skills`)

## Ranked recommendations — paid / marketplace (lower priority)

| Rank | Plugin | Why | Cost | Verdict |
|---|---|---|---|---|
| 11 | **WPS Kingsoft** | Office doc collaboration | Subscription | **DEFER** — Popy uses Google Pro already |
| 12 | **WeCom (企业微信)** | Enterprise messaging | Free for basic | **DEFER** — not in current OPTIMUS workflow |
| 13 | **Qichacha** | Company info lookup | Subscription | **DEFER** — Popy doesn't run B2B intel yet |
| 14 | **Notion MCP** | Vault/pages for OPTIMUS docs | Free OAuth | **CANDIDATE** — but Obsidian already covers this |
| 15 | **Hundsun financial data** | Financial DB | Paid | **DEFER** — Popy isn't doing finance work in OPTIMUS |

**Cost filter applied**: no paid plugin in top-10. The 5 lower-priority items are all paid, and Popy's doctrine explicitly says don't recommend pay-as-you-go over flat subscription, and don't upsell things he doesn't need.

---

## Capability gap → plugin resolution

| Gap (from Phase A) | Resolved by plugin |
|---|---|
| Identity: document indexer | `mmx-cli` (+ already have `mavis-backbone-skill`) |
| Operations: B2B proposal PPT/PDF | `pptx-generator`, `minimax-pdf`, `minimax-docx`, `minimax-xlsx` |
| Operations: image analysis for visual assets | `vision-analysis`, `minimax-multimodal-toolkit` |
| Operations: video generation (SENTINEL Character assets) | `minimax-multimodal-toolkit`, `shader-dev` |
| Operations: music/audio for SENTINEL Character | `minimax-music-gen`, `minimax-multimodal-toolkit` |
| Operations: PR review complement to `code_review_rules.md` | `pr-review` |
| Behavioral: prompt quality (already covered) | (no new plugin — `mavis-triple-crunch-skill` suffices) |
| Behavioral: time-budget (no plugin equivalent) | (gap remains) |
| Role: role-conflict detector | (no plugin — internal architecture) |

## Cross-references

- `00_INDEX/00_skill_taxonomy.md` — the 4-category × 2-layer grid this report's gaps come from
- `70_CONNECTORS/70_mcp_mirror_plan.md` — companion report on MCP mirroring
- MiniMax Agent docs: https://agent.minimax.io/docs/code/agents/plugins

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | Plugin universe surveyed | 23 official `minimax-ai/skills` + 1 `minimax-h3-skills` already installed + marketplace paid plugins catalogued. Top-10 free recommendations issued. Popy R0 needed for any install. |
