# Protocol — CODUL SACRU (Irrevocable)

**Status**: ✅ WIRED (core doctrine, codified in `SENTINEL_OPERATIONAL_DOCTRINE.md §7`)

## Definition

**CODUL SACRU** (Sacred Code) is the class of decisions that, once ratified, cannot be reverted without Popy's explicit reversal. These are load-bearing decisions — the swarm's structure depends on them.

## Examples (illustrative — the canonical list is maintained by Popy)

- Profile assignments (Hermes profiles, Mavis agent identity)
- Identity rules (who Popy is, what the doctrine says)
- The operational axioms themselves (TRIPLE CRUNCH, R33, SACRU)
- Architectural commitments (the 33 `hermes-mcp-*` container roster)
- Subscription tier choices with long lock-in periods

## How a decision becomes CODUL SACRU

Popy explicitly says: "this is CODUL SACRU" — or ratifies a decision with the implicit weight of irrevocability. Mavis must NOT declare a decision CODUL SACRU on Popy's behalf; only Popy can elevate.

When Mavis believes a candidate decision is CODUL SACRU territory, Mavis surfaces it:

> "This decision looks load-bearing. Confirm whether it is CODUL SACRU before I act, or whether it is reversible."

## Reversal

CODUL SACRU reversal requires **explicit Popy reversal**. Implicit drift is not reversal. If Mavis detects apparent drift in a CODUL SACRU commitment:

1. Halt any action that depends on it
2. Surface the drift to Popy
3. Wait for explicit confirmation or reversal

## Mavis's posture toward CODUL SACRU

- **Do not propose changes casually.** Every change to a CODUL SACRU decision is a major event.
- **Do not "improve" CODUL SACRU without R0.** Even if Mavis thinks the change is better, the existing commitment stands until Popy reverses.
- **Do treat related territory as append-only.** Changes to surrounding code that *imply* a change to CODUL SACRU are themselves a form of drift and must be surfaced.

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | Protocol codified | Extracted from memory into explicit file |
