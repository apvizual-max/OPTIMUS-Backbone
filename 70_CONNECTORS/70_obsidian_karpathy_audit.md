# Obsidian Second Brain — Karpathy LLM-Wiki Audit

**Date**: 2026-10-02
**Author**: Mavis (MiniMax Code orchestrator)
**Status**: 🔴 Audit complete. Closes the investigation half of GAP-4.
**Vault**: `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\`

---

## 1. Headline: the pattern is SPECIFIED but not ENFORCED

Popy said the vault *"operates based on karpathy's LLM wiki concept but custom adapted."*

**He is right, and the spec exists.** `SF_MKVA - KARPATHY_LLM_WIKI_SETUP.md` (370 lines, `sacru: true`, `type: karpathy-setup`, dated 2026-05-12) documents the whole thing, including the source video (Nate Herk on Karpathy, `sboNwYmH3AY`, April 2026) and the original gist.

**The problem is enforcement, not design.**

---

## 2. The Karpathy spec, as documented in the vault

### 2.1 Canonical structure

```
vault/
├── raw/                        # source material
└── wiki/
    ├── analysis/               # (default folder)
    ├── concepts/               # (default folder)
    ├── entities/               # (default folder)
    ├── sources/                # (default folder)
    ├── tools/                  # discovered empirically
    ├── techniques/             # discovered empirically
    ├── people/                 # discovered empirically
    ├── index.md                # KEY: master navigation
    ├── log.md                  # operation history
    └── hot.md                  # HOT CACHE — 500 words most recent
└── claude.md                   # project schema
```

### 2.2 The HOT CACHE mechanism (`hot.md`)

From `SF_MKVA - HOT_CACHE_DOCUMENTATION.md` and the setup doc:

| Property | Value |
|---|---|
| Location | `wiki/hot.md` |
| Size cap | ~500 words / characters |
| Content | The proverb/axioms currently **converging** for this session |
| Read rule | Any agent queries `hot.md` **FIRST** → gets context without crawling |
| Write rule | Updated on **every prompt** with currently-relevant HOT items |
| Wake rule | SENTINEL at wake reads `hot.md` **FIRST** → has current convergence |
| OPTIMUS equivalent | `SOUL_*.md` with a HOT proverbs section |

### 2.3 The vault's own compliance verdict

`KARPATHY_LLM_WIKI_SETUP.md:315-345` contains a self-audit table:

| Karpathy concept | OPTIMUS equivalent | Status (per the doc) |
|---|---|---|
| `raw/` | INVENTAR_SISTEM + sources/ | EXISTS |
| `wiki/` | Vault Obsidian primary `E:\CLAUDE\` | DECISION PASS 9 |
| `index.md` | INTEGRATION_INDEX.md + 00_INDEX_MASTER | EXISTS |
| `log.md` | `reflex_archive\T3_ritual_final\` | EXISTS |
| **`hot.md`** | **SOUL_*.md with HOT proverbs section** | **DE CREAT FAZA D** ← *to be created, phase D* |
| `claude.md` | CLAUDE.md + BOOTSTRAP_PROTOCOL | EXISTS |
| Linting | `tools\health_check.sh` + Bundle C `index_knowledge_global` | EXISTS |
| Web clipper | Cowork R15.7 + Chrome MCP | EXISTS |

> **Verdict in the doc's own words:** *"OPTIMUS deja are majoritatea componentelor Karpathy — lipsa critică = `hot.md` HOT CACHE."*

**So the vault diagnosed its own gap 4 months ago (2026-05-12) and it is still open.**

---

## 3. Measured compliance (2026-10-02, live audit)

### 3.1 Index coverage — 25 of 399

| Metric | Value |
|---|---|
| Directories at depth ≤ 2 | 399 |
| **Have an index file** (`_?index*.md`) | **25** (6.3%) |
| **Missing an index** | **374** (93.7%) |

Including all 6 top-level operation folders:
- `- ORCHESTRATOR - Sys Folder - Hermes Default`
- `Skills and MCP Skill Bundles`
- `CLI_PRIME_OPPERATIONS - CPO`
- `CODER_OPPERATIOS - CO`
- `COWORK_OPPERATIONS - COW`
- `POPY_OPPERATIONS - PO`
- `SENTINEL_PRIME_OPPERATIONS - SPO`

### 3.2 No vault-root index

`E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\` contains **7 directories and 0 files.** There is no `index.md`, no `_INDEX.md`, nothing. A new agent (or Popy after 2 weeks away) has no single entry point.

### 3.3 The `MAIN SYSTEM KNOLEDGE INDEX` folder

Named like an index, but is a *folder* containing 5 files — not an index file:

| File | Size | Frontmatter? |
|---|---|---|
| `00_OP_KVMC - SECOND BRAIN - CLAUDE - WIKILINKS.md` | 29,983 B | ❌ no |
| `00_OP_KVMC - SECOND BRAIN - INDEX_KV_MASTER - Mod B.md` | 43,622 B | ✅ yes |
| `00_OP_KVMC - SECOND_BRAIN - INDEX_KV_MASTER - Mod A.md` | 39,701 B | ✅ yes |
| `00_OP_KVMC - SYSTEM_FOLDER - Base - Mod A.base` | 4,434 B | n/a (.base) |
| `00_OP_KVMC - SYSTEM_FOLDER - Base - Mod B.base` | 2,777 B | n/a (.base) |

**Mod A and Mod B** (39.7 KB + 43.6 KB) are the real master indexes — they have frontmatter and are substantial. But they live one level deep, are not named `index.md`, and a crawler won't find them automatically.

### 3.4 Frontmatter compliance — 76 of 400 (19%)

| Sample | With YAML frontmatter | Without |
|---|---|---|
| First 100 md @ depth ≤ 3 | 4 | 96 |
| First 400 md @ depth ≤ 3 | **76** (19%) | 324 (81%) |

**Frontmatter exists but is inconsistent.** Files that *do* have it follow a consistent SENTINEL schema:

```yaml
---
created: 2026-05-12
author: CODER_APP
session: CHAT-019
type: karpathy-setup
status: documented-from-transcript
sacru: true
tags: [karpathy, llm-wiki, obsidian, setup, hot-cache, claude-code, sf-mkva]
---
```

Fields: `created`, `author`, `session`, `type`, `status`, `sacru`, `tags`, plus `Keywords:`, `Cross-link la fișiere înrudite`, `Citește acest fișier când:` (a "read this when" trigger), and `SOUL` (the one-line essence).

**This IS a canonical header schema — it's just applied to 19% of files.** The 81% without it are the gap, not the absence of a spec.

### 3.5 Hot cache — absent

No `hot.md` anywhere in the vault (searched). The spec calls for `wiki/hot.md` at ~500 words, read-first by every agent, rewritten every prompt.

**The closest existing artifact** is `SOUL_*.md`:
- `SOUL_DEFAULT.md`
- `SOUL_PRIME.md`
- `SOUL_ASSIST.md`
- `SF_IA - SOUL_LEVEL_0.md`

These are profile-scoped (default / prime / assist) rather than a single session-scoped convergence cache. They cover the same intent differently.

---

## 4. Gap summary

| # | Gap | Severity | Fix effort | Who |
|---|---|---|---|---|
| **4.1** | **`hot.md` HOT CACHE does not exist** | 🔴 High | 30 min | R0 → me |
| **4.2** | **No vault-root `index.md`** | 🔴 High | 30 min | R0 → me |
| **4.3** | **374 of 399 dirs lack an index** (93.7%) | 🟡 Medium | 2–4 h (bulk) | R0 → me |
| **4.4** | **324 of 400 notes lack frontmatter** (81%) | 🟡 Medium | 4–8 h (bulk) | R0 → me |
| **4.5** | Mod A / Mod B master indexes not named/discoverable as `index.md` | 🟢 Low | 10 min | R0 → me |
| **4.6** | Mavis's `obsidian-second-brain-skill` doesn't enforce or verify the pattern | 🟡 Medium | 20 min | R0 → me |

**What is NOT a gap**: the design. It's documented, dated, marked `sacru: true`, and mapped to OPTIMUS equivalents. Someone did the thinking. What's missing is the build + enforcement.

---

## 5. Proposed build plan (R0 required)

### Stage 1 — Hot cache (highest value, smallest effort)

Create `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\wiki\hot.md` (or equivalent location Popy prefers):

```markdown
---
type: hot-cache
sacru: true
updated: <timestamp>
word_cap: 500
---
# HOT CACHE — current convergence

## HOT axioms this session
- <axiom 1> — source: <path:line>
- <axiom 2> — source: <path:line>

## HOT proverbs in play
- "<proverb>" — applies because <reason>

## Active task
- <one line>

## Do not
- <constraint>
```

Then: Mavis updates it on every session-open and every doctrine-relevant decision. `mavis-session-lifecycle-skill` gets a new step.

**Needs Popy's decision**: location + whether Mavis writes it autonomously or proposes.

### Stage 2 — Vault root index

Create `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\00_CANONICAL_INDEX.md`:

```markdown
| Folder | Role | Index file | Notes count | Entry point |
|---|---|---|---|---|
| - ORCHESTRATOR - Sys Folder - Hermes Default | Deep doctrine | MAIN SYSTEM KNOLEDGE INDEX/...Mod A.md | 6,000+ | ... |
| SENTINEL_PRIME_OPPERATIONS - SPO | Sentinel ops | (to be created) | ? | — |
| POPY_OPPERATIONS - PO | Popy's ops | (to be created) | ? | — |
| ... | | | | |
```

### Stage 3 — Frontmatter backfill (bulk, staged)

Priority order:
1. Files in the 13 `SF_*` manual folders (doctrine — highest value)
2. Files in the 6 operation folders
3. Everything else

Use the existing SENTINEL schema. Do not invent a new one.

### Stage 4 — Index backfill (bulk)

Generate an `INDEX.md` for every dir missing one, from its own contents. Auto-generated, human-reviewable.

### Stage 5 — Enforcement in Mavis

Update `mavis-obsidian-second-brain-skill` to:
- Refuse to write a note without the canonical frontmatter
- Warn when writing into a folder that has no index
- Offer to create the index

---

## 6. Why this matters for the OPTIMUS integration

The vault is Popy's **long-term memory** and the substrate SENTINEL reads at wake. Three concrete consequences of the current state:

1. **Cold-start cost.** No root index + 374 unindexed dirs means any agent (Mavis included) must crawl to find anything. The Karpathy `index.md` pattern exists precisely to eliminate this.
2. **No convergence memory.** Without `hot.md`, every session starts cold. SENTINEL must re-derive which axioms/proverbs are live rather than reading a 500-word convergence cache.
3. **Retrieval noise.** 81% of notes lack the `tags` + `Citește acest fișier când:` trigger that makes semantic recall work. The 19% that have it are effectively searchable; the rest are a haystack.

Fixing `hot.md` alone (Stage 1, 30 min) recovers the highest-leverage piece.

---

## 7. GAP-4 status

| Sub-item | Status |
|---|---|
| Karpathy pattern located in vault | ✅ `SF_MKVA - KARPATHY_LLM_WIKI_SETUP.md` (370 lines) |
| Canonical header schema identified | ✅ 8 fields: `created`, `author`, `session`, `type`, `status`, `sacru`, `tags` + Keywords/Cross-link/Citește/SOUL |
| Index coverage measured | ✅ 25/399 dirs (6.3%) |
| Frontmatter compliance measured | ✅ 76/400 notes (19%) |
| `hot.md` absence confirmed | ✅ No file found |
| Root index absence confirmed | ✅ 0 files at vault root |
| Build plan written | ✅ 5 stages |
| **Execution** | ❌ **R0 required** — writing to the vault is gated by doctrine §11 |

---

## Cross-references

- Master gap report: `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\OPTIMUS_MINIMAX_INTEGRATION_GAP_REPORT.md`
- Karpathy spec: `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\- ORCHESTRATOR - Sys Folder - Hermes Default\SF_MKVA - MEMORIE_KV_ARHIVE\SF_MKVA - KARPATHY_LLM_WIKI_SETUP.md`
- Hot cache spec: `...\SF_MKVA - HOT_CACHE_DOCUMENTATION.md`
- Obsidian bridge skill: `C:\Users\apviz\.minimax\agents\mavis\skills\mavis-obsidian-second-brain-skill\SKILL.md`
- Doctrine §11: propose before writing to the vault
