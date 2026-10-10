# Workflow — Bridge Dispatch

**Purpose**: Step-by-step for handing a task to another AI in the swarm.

## Pre-flight

Before dispatching, confirm:
- [ ] The bridge is ✅ WIRED (not 🟡 blueprint) in `00_INDEX/00_bridge_registry.md`
- [ ] The bridge file's `Open questions for Popy` section is empty (no unresolved blockers)
- [ ] Popy has R0-ratified the dispatch (per R33 Mod B)

## Steps

1. **Declare** the bridge (which AI, which model/version if applicable, why this bridge).
2. **Construct the task contract** — see `20_PROTOCOLS/20_bridge_protocol.md` for the contract shape.
3. **Hand off** the contract. Capture the request ID if the bridge returns one.
4. **Wait** for the response. If the bridge has a timeout, set it explicitly.
5. **Verify** the response against acceptance criteria.
6. **Integrate** the result into Mavis's output with explicit attribution.
7. **Log** to the bridge file's JURNAL_OGLINDA table.

## Failure handling

If the bridge fails:
- Surface the failure to Popy immediately.
- Do NOT silently fall back to Mavis doing the task itself unless pre-authorized.
- Append the failure to JURNAL_OGLINDA with the error verbatim.

## Pre-authorization (R33 exception)

Popy may pre-authorize a class of dispatches (e.g., "you may dispatch to Gemini for vision tasks without asking each time"). In that case:
- The pre-authorization must be explicit and time-bounded (or revocable).
- Mavis still logs every dispatch.
- Mavis still surfaces the result.

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | Workflow codified | First backbone session |
