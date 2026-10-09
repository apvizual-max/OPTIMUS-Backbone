---
name: mavis-wayland-bridge-skill
description: Operate the Wayland pillar (agentic cowork). Wayland ships 71 workflow SKILL.md bodies as a packed blob; Mavis extracts them, indexes them, and executes the procedures inline (Wayland has no CLI). Use for contract review, decks, ICP, positioning, NDA, objection libraries, launch workflows, content batches, HR playbooks, financial models. Triggers on "Wayland", "contract review", "investor deck", "positioning sprint", "launch workflow".
---

# mavis-wayland-bridge-skill

Wayland is the **agentic cowork** pillar. It has no CLI, so Mavis does not dispatch to it — Mavis **executes its workflow procedures directly**.

## What Wayland actually is

| Property | Value |
|---|---|
| Install | `C:\Program Files\Wayland\` |
| Packed workflows | `resources\bundled-workflows\skill-bodies.bin` (327,837 bytes) |
| Offset map | `resources\bundled-workflows\skill-bodies.offsets.json` (v1) |
| Workflow count | **71** |
| Catalog | `resources\bundled-workflows\index.json` — 37 content-creation, 34 business-operations |
| Routines | `resources\bundled-workflows\routines.json` — 4 scheduled jobs |
| CLI | **none** (`wayland`, `wl`, `wayland-cli` all not on PATH) |
| Skills library | `resources\skills-library\` — **empty** |

## The packing format (reverse-engineered)

`skill-bodies.bin` is **plain UTF-8 markdown**, not a binary format. `offsets.json` maps each path to `[offset, length]`:

```json
{"version": 1,
 "entries": {"bodies/wayland-contract-review/SKILL.md": [105960, 5930], ...}}
```

`blob[offset : offset+length].decode('utf-8')` is the complete `SKILL.md`.

## Refresh the extracted workflows

```powershell
python C:\Users\apviz\.minimax-agent\projects\scripts\extract_wayland_workflows.py
```

Output: `C:\Users\apviz\.minimax-agent\projects\20_BRIDGES\wayland\workflows\`
- `bodies\<name>\SKILL.md` × 71
- `_MANIFEST.json` — path, bytes, sha256, per workflow
- `README.md` — generated index table

## High-relevance workflows for Popy's work

| Workflow | Use for |
|---|---|
| `wayland-contract-review` | clause-by-clause risk review, red-lines, counsel routing |
| `wayland-nda-pack` | NDA generation for B2B |
| `wayland-icp-build` | ideal-customer-profile definition |
| `wayland-objection-library-build` | sales objection handling |
| `wayland-outreach-build` | cold outreach sequences |
| `wayland-build-investor-deck` | decks |
| `wayland-case-study-build` | case studies |
| `wayland-offer-build` | offer construction |
| `wayland-positioning-sprint` | positioning work |
| `wayland-full-launch` | product launch orchestration |
| `wayland-bullshit-clean` / `-batch` | strip filler — matches the SOUL/CONSTINTA discipline |
| `wayland-voice-bootstrap` | voice/tone profile |
| `wayland-competitor-deep-research` | competitive intel |
| `wayland-full-sales-asset` | sales collateral |

## How to execute a workflow

1. **Search** `bodies/**/SKILL.md` for the task shape.
2. **Read** the full `SKILL.md` — it is a real procedure, not a stub.
3. **Execute inline**, with the doctrine gates:
   - `mavis-r33-bimodal-skill` — Mod A / R0 / Mod B
   - `mavis-triple-crunch-skill` — all 3 axioms before finalizing
   - `mavis-deliverable-handoff-skill` — `<media />` for outputs
4. **Log** the result to the JURNAL and update `00_HOT_CACHE.md` if the convergence changed.

## Anti-patterns

- ❌ Trying to exec a Wayland binary — there is none.
- ❌ Treating the catalog (`index.json`) as the procedure — it is metadata only; the body is in the blob.
- ❌ Running an e-commerce workflow (`abandoned-cart-recovery`, `sku-launch`, `listing-*`) — not Popy's domain.
- ❌ Skipping the doctrine gates because "the workflow already says what to do" — the workflow is the *method*, the doctrine is the *discipline*.

## Cross-references

- Extracted workflows: `…\projects\20_BRIDGES\wayland\workflows\`
- Extractor: `…\projects\scripts\extract_wayland_workflows.py`
- Inventory: `…\projects\10_BRIDGES\10_wayland.md`
- Skills: `mavis-triple-crunch-skill`, `mavis-r33-bimodal-skill`
