# Protocol — BRIDGE DISPATCH

**Status**: ✅ WIRED (operational discipline for cross-AI coordination)

## Definition

The standard sequence Mavis follows when handing a task to another AI in the swarm (Antigravity, Gemini, Hermes, Gordon, NotebookLM, Qwen Studio).

## The four-step sequence

### Step 1 — Declare the bridge

State explicitly which AI Mavis is bridging to and why. Example:

> "Dispatching to Hermes (profile: prime) for tool orchestration on this MCP call."

Never dispatch silently. The operator must see the bridge choice.

### Step 2 — Hand off minimal context

Pass only the context the receiving AI needs to execute. Do not dump Mavis's full session state — that's noise. Construct a clean task contract:

- Scope (what's in / what's out)
- Acceptance criteria (how to know it's done)
- Constraints (what must not change)
- Required inputs (what context the AI needs)
- Output format (what shape the answer should be)

### Step 3 — Receive and integrate

When the bridge returns:
- Capture the result with attribution (which AI, which model, which version, timestamp)
- Verify the result against acceptance criteria
- If the bridge failed, surface the failure — do not paper over it

### Step 4 — Log the dispatch

Append an entry to the bridge file's JURNAL_OGLINDA table:
- Date / time
- Bridge target
- Task contract summary
- Result summary
- Any failures

This makes the swarm auditable. No silent shadows between bridges.

## Failure modes

- ❌ Silent dispatch (no Step 1 declaration)
- ❌ Dumping full session context instead of a contract
- ❌ Pretending a bridge was called when it wasn't (CLI missing, etc.)
- ❌ Logging nothing about the dispatch
- ❌ Letting one bridge shadow another without surfacing it

## Pre-dispatch R0

Cross-AI dispatch is a **R33 Mod B action**. It requires Popy R0 unless pre-authorized. When in doubt, ask before dispatching.

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | Protocol codified | Extracted from doctrine into explicit bridge protocol |
