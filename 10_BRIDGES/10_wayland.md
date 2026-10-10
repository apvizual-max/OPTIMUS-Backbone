# Wayland Pillar — Inventory & Integration Design

**Date**: 2026-10-02
**Author**: Mavis (MiniMax Code orchestrator)
**Status**: 🔴 First deep inventory. Zero prior Mavis integration — this closes GAP-2.

---

## 1. What Wayland is (as installed on this machine)

Wayland is Popy's **agentic cowork + workflow platform**. Installed at:
- App: `C:\Program Files\Wayland\`
- Roaming data: `C:\Users\apviz\AppData\Roaming\Wayland\`
- Updater: `C:\Users\apviz\AppData\Local\wayland-updater\`

Its purpose in OPTIMUS: **agentic cowork** — the place where Popy and agents do structured, repeatable work together (launches, content batches, business ops cycles).

---

## 2. The workflow engine — 71 workflows (the headline)

`C:\Program Files\Wayland\resources\bundled-workflows\index.json` — **71 workflows**, all `type: workflow`, all `source: wayland-library`, all `author: wayland`.

| Category | Count | % |
|---|---|---|
| `content-creation` | 37 | 52.1% |
| `business-operations` | 34 | 47.9% |
| **Total** | **71** | 100% |

### 2.1 Business-operations (34)

| # | Workflow | Relevance to OPTIMUS |
|---|---|---|
| 1 | `business-ops-monthly-review` | Low — generic business review |
| 2 | `business-ops-operations-handbook` | Low |
| 3 | `business-ops-runbook-generator` | Medium — runbooks ≈ SOPs for the swarm |
| 4 | `business-ops-sop-generator` | Medium — SOPs for Sentinel role AIs |
| 5 | `business-ops-weekly-review` | Low |
| 6 | `wayland-budget-build` | Low |
| 7 | `wayland-budget-variance-check` | Low |
| 8 | `wayland-build-financial-model` | Low |
| 9 | `wayland-cashflow-batch-review` | Low |
| 10 | `wayland-cashflow-review` | Low |
| 11 | `wayland-contract-review` | **High** — Popy does B2B proposals; contract review is core |
| 12 | `wayland-deal-forensic` | Medium — deal post-mortems |
| 13 | `wayland-discovery-prep` | Low |
| 14 | `wayland-employment-package` | Low |
| 15 | `wayland-forecast-build` | Low |
| 16 | `wayland-hr-comp-band` | Low |
| 17 | `wayland-hr-handbook` | Low |
| 18 | `wayland-hr-hire-loop` | Low |
| 19 | `wayland-hr-onboard-package` | Low |
| 20 | `wayland-hr-performance-review` | Low |
| 21 | `wayland-icp-build` | **High** — ICP definition for B2B targeting |
| 22 | `wayland-morning-report` | Medium — daily ops digest |
| 23 | `wayland-nda-pack` | **High** — NDA generation for B2B |
| 24 | `wayland-objection-library-build` | **High** — sales objection handling |
| 25 | `wayland-outreach-build` | **High** — cold outreach sequences |
| 26 | `wayland-pipeline-batch-review` | Medium |
| 27 | `wayland-policy-stack` | Medium — policy generation |
| 28 | `wayland-pricing-stress-test` | Medium |
| 29 | `wayland-runway-projection` | Low |
| 30 | `wayland-support-churn-investigate` | Low |
| 31 | `wayland-support-kb-article` | Medium — KB article generation |
| 32 | `wayland-support-macro-library` | Low |
| 33 | `wayland-support-ticket-triage` | Low |
| 34 | `wayland-support-week-batch` | Low |

### 2.2 Content-creation (37)

| # | Workflow | Relevance to OPTIMUS |
|---|---|---|
| 1 | `wayland-abandoned-cart-recovery` | Low — e-commerce |
| 2 | `wayland-batch-investor-update` | Low |
| 3 | `wayland-blog-publish` | Medium |
| 4 | `wayland-brand-audit` | Medium |
| 5 | `wayland-build-investor-deck` | **High** — decks for B2B |
| 6 | `wayland-bullshit-clean` | **High** — strips filler; matches SOUL/CONSTINTA discipline |
| 7 | `wayland-bullshit-clean-batch` | **High** — batch version |
| 8 | `wayland-campaign-brief` | Medium |
| 9 | `wayland-case-study-build` | **High** — case studies for B2B |
| 10 | `wayland-channel-mix` | Low |
| 11 | `wayland-close-rebuild` | Low |
| 12 | `wayland-competitor-deep-research` | **High** — competitive intel |
| 13 | `wayland-competitor-watch` | Medium |
| 14 | `wayland-content-batch-process` | **High** — batch content processing |
| 15 | `wayland-content-calendar-build` | Medium |
| 16 | `wayland-conversion-audit` | Low |
| 17 | `wayland-course-build` | Medium |
| 18 | `wayland-draft-investor-update` | Low |
| 19 | `wayland-evergreen-conversion` | Low |
| 20 | `wayland-full-funnel-design` | Medium |
| 21 | `wayland-full-launch` | **High** — product launch orchestration |
| 22 | `wayland-full-sales-asset` | **High** — sales collateral |
| 23 | `wayland-funnel-audit` | Low |
| 24 | `wayland-headline-lab` | Medium — headline A/B testing |
| 25 | `wayland-launch-readiness-audit` | Medium |
| 26 | `wayland-launch-status-batch` | Medium — referenced by `daily-launch-status` routine |
| 27 | `wayland-listing-audit-pick` | Low — e-commerce |
| 28 | `wayland-listing-optimize` | Low — e-commerce |
| 29 | `wayland-offer-build` | **High** — offer construction for B2B |
| 30 | `wayland-positioning-sprint` | **High** — positioning work |
| 31 | `wayland-prep-due-diligence` | Medium |
| 32 | `wayland-re-launch` | Medium |
| 33 | `wayland-sku-launch` | Low |
| 34 | `wayland-voice-bootstrap` | **High** — voice/tone profile; maps to the second-brain voice layer |
| 35 | `wayland-vsl-build` | Medium — VSL scripts |
| 36 | `wayland-webinar-funnel` | Medium |
| 37 | `wayland-winback-campaign` | Low |

**12 high-relevance workflows identified** (marked **High** above) — these map directly to Popy's B2B proposal work, SENTINEL content, and the SOUL/CONSTINTA voice discipline.

---

## 3. The routine scheduler

`bundled-workflows/routines.json` — scheduled automations referencing `~/wayland/` paths.

### 3.1 Routines found (4 read)

| id | name | schedule | workflow | inputs |
|---|---|---|---|---|
| `daily-launch-status` | Daily launch status | `0 9 * * *` | `wayland-launch-status-batch` | `~/wayland/state/active-launch.yaml`, `~/wayland/inbox/{sales,ads,support}` |
| `weekly-listing-audit` | Weekly listing audit | `0 10 * * 3` | `wayland-listing-audit-pick` | `~/wayland/commerce/inventory.csv`, pick=`lowest_conversion` |
| `weekly-content-batch` | Weekly content batch | `0 18 * * 0` | `wayland-content-batch-process` | `~/wayland/inbox/content-briefs/`, `~/wayland/voice-notes.md` |
| `weekly-copy-review` | Weekly copy review | (truncated in read) | — | — |

### 3.2 The `~/wayland/` contract

Routines expect these paths to exist:

| Path | Purpose |
|---|---|
| `~/wayland/state/active-launch.yaml` | current launch state |
| `~/wayland/inbox/sales/` | sales input drop |
| `~/wayland/inbox/ads/` | ads input drop |
| `~/wayland/inbox/support/` | support input drop |
| `~/wayland/inbox/content-briefs/` | content brief drop |
| `~/wayland/commerce/inventory.csv` | inventory data |
| `~/wayland/voice-notes.md` | voice/tone profile |

**Gap**: none of these were verified to exist. Mavis has no read/write bridge to this tree.

---

## 4. CLI surface — the blocker

`bundled-workflows` has a working engine, but **there is no Wayland CLI on PATH**:

```
wayland      -> NOT FOUND
wl           -> NOT FOUND
wayland-cli  -> NOT FOUND
```

Only one managed shim exists:

| Path | Content |
|---|---|
| `resources/managed-cli-shims/officecli` | binary/shim |
| `resources/managed-cli-shims/officecli.cmd` | Windows wrapper |

### 4.1 Bundled binaries (discovered)

| Dir | Contents | Purpose |
|---|---|---|
| `bundled-officecli\win32-x64\` | native binary | Office document operations |
| `bundled-fuigo\win32-x64\` | native binary | **unknown** — "fuigo" is not a term I can verify |
| `bundled-tvcontrol\node_modules\` | node deps | TV/display control? unknown |
| `classic-recovery-tools\` | tools | recovery utilities |
| `pwa\` | PWA assets | progressive web app shell |

**Honest finding**: `officecli` is the only surface I can name with confidence. `fuigo`, `tvcontrol` are unverified — I will not guess their purpose.

---

## 5. `skills-library/` is EMPTY

`resources/skills-library\` → **0 directories**.

Either:
- The library populates on first launch of the Wayland app, or
- The install is incomplete

`bundled-workflows/skill-bodies.bin` + `skill-bodies.offsets.json` hold the actual workflow bodies (binary-encoded). `index.json` is the manifest. Format of `skill-bodies.bin` not inspected.

---

## 6. Workflow metadata schema (from index.json)

```json
{
  "name": "business-ops-monthly-review",
  "title": "Monthly Review",
  "description": "...",
  "type": "workflow",
  "source": "wayland-library",
  "path": "bodies/business-ops-monthly-review/SKILL.md",
  "metadata": {
    "author": "wayland",
    "version": "1.0.0",
    "tags": ["business-ops", "monthly-review", "metrics", "reporting", "deterministic"],
    "category": "business-operations",
    "depends": ["ops-report"]
  },
  "category": "business-operations",
  "tags": [...],
  "security": {
    "verdict": "clean",
    "findings": [],
    "scannedAt": 1788048000000,
    "scannerVersion": 1,
    "llmScanned": false
  }
}
```

Notable: workflows are **`SKILL.md` bodies** under `bodies/<name>/SKILL.md`, versioned, tagged, with a **dependency graph** (`depends`) and **automated security scanning** (`security.verdict`).

**This is a skill library structurally compatible with Mavis's own skill system.** A `mavis-wayland-bridge-skill` could index these and route to them the same way `mavis-skill-index` routes across the 1,159 personal skills.

---

## 7. Proposed integration design (needs Popy R0 to execute)

### 7.1 Bridge skill

Create `C:\Users\apviz\.minimax\agents\mavis\skills\mavis-wayland-bridge-skill\SKILL.md`:

| Field | Value |
|---|---|
| Purpose | Route content-creation / business-operations tasks to Wayland's 71 workflows |
| Trigger | "build a launch", "contract review", "case study", "investor deck", "positioning sprint", "outreach sequence" |
| Data source | `C:\Program Files\Wayland\resources\bundled-workflows\index.json` |
| Execution | **BLOCKED** — no CLI. Requires Wayland to expose an invocation surface, or Mavis to read `skill-bodies.bin` and execute the body directly. |

### 7.2 `~/wayland/` tree bridge

Verify / create the contract paths; wire `obsidian-mcp` or `mcp-server-filesystem` to read/write them. **R0 required** — writing to a new tree is a mutation.

### 7.3 Cron reconciliation

Two schedulers now exist:
- **Mavis crons**: classifier rebuild (Mon 04:00)
- **Wayland routines**: 4+ routines (daily 09:00, weekly Wed 10:00, weekly Sun 18:00, weekly copy review)

**They do not currently collide**, but there is no shared registry. Proposal: Wayland owns launch/content/commerce routines; Mavis owns skill-index and system-maintenance crons. **Popy decision required.**

### 7.4 Path to a working bridge

The honest blocker: **Wayland's invocation surface is not exposed.** Options:

| Option | Effort | Risk |
|---|---|---|
| A. Read `skill-bodies.bin`, parse, execute bodies in Mavis | Medium (format reverse-engineering) | Low — read-only |
| B. Ask Wayland vendor for CLI / API | Low effort, external dependency | None |
| C. Drive the Wayland desktop app via `chrome-devtools-mcp` / UI automation | High (brittle) | Medium — UI changes break it |
| D. Treat Wayland as human-only; Mavis reads its outputs | Low | None — but limits integration |

**My recommendation: A then B.** A gets Mavis read access immediately; B gets a stable surface.

---

## 8. Gap-2 status

| Sub-item | Status |
|---|---|
| Workflow count + catalog | ✅ 71 mapped, 12 high-relevance flagged |
| Category breakdown | ✅ 37 content / 34 business-ops |
| Routine scheduler | ✅ 4 routines read, `~/wayland/` contract identified |
| `~/wayland/` tree existence | ❌ Not verified |
| CLI surface | ❌ Not on PATH — blocker |
| `skills-library/` | ❌ Empty (0 dirs) |
| `bundled-fuigo` / `bundled-tvcontrol` purpose | ❌ Unverified — not guessing |
| Bridge skill | 🟡 Design written, execution blocked on CLI |
| Cron reconciliation | 🟡 Design written, Popy decision needed |

**GAP-2 is now documented rather than assumed.** The remaining work is a Popy decision on option A/B/C/D.

---

## Cross-references

- Master gap report: `C:\Users\apviz\.minimax-agent\projects\OPTIMUS_MINIMAX_INTEGRATION_GAP_REPORT.md`
- Mavis skill index: `C:\Users\apviz\.minimax\agents\mavis\skills\mavis-skill-index\SKILL.md`
- Wayland workflows: `C:\Program Files\Wayland\resources\bundled-workflows\index.json`
- Wayland routines: `C:\Program Files\Wayland\resources\bundled-workflows\routines.json`
- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md` §9 (bridges)
