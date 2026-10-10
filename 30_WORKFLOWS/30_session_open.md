# Workflow — Session Open

**Purpose**: Standard opening sequence for every Mavis session in this workspace.

## Steps

1. **Read orientation** (cached after first read; skip on subsequent turns unless invalidated):
   - `README.md`
   - `OPTIMUS_INDEX.md`
   - `AGENTS.md`
2. **Check bridge status**: `00_INDEX/00_bridge_registry.md` — see if any bridge flipped from 🟡 → ✅ since last session.
3. **Check JURNAL_OGLINDA** in the relevant partition registries for new entries.
4. **Confirm language tier** with Popy's first message. Romanian at Popy + Prime + Assist, English below.
5. **State the SOUL** of the session: one line telling Popy what Mavis is ready for in this turn.
6. **Wait for Popy's first request.** Do not pre-empt.

## When the session is NOT in this workspace

If Mavis is operating in a different workspace (Popy opened a different project):
1. Skip the project file reads.
2. Apply the doctrine from Memory (which carries the operational code).
3. Note that project-specific files are not loaded.

## Anti-patterns

- ❌ Re-reading `README.md` every turn after the first.
- ❌ Pre-empting Popy's first request.
- ❌ Skipping JURNAL_OGLINDA check (you miss state changes from prior sessions).
- ❌ Forgetting language tier — answering in English when Popy wrote Romanian.

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | Workflow codified | First backbone session |
