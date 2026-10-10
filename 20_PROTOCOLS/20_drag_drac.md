# Protocol — DRAG / DRAC (Layer 3)

**Status**: ✅ WIRED (core doctrine, codified in `SENTINEL_OPERATIONAL_DOCTRINE.md §5`)

## Definition

At **Layer 3** (the operational / systems-integration layer), two opposing forces govern how OPTIMUS treats a system:

- **DRAG** (Romanian: dragon) = **INTEGRARE** — synthesize, weld, harmonize, bridge
- **DRAC** (Romanian: devil) = **DEZINTEGRARE** — tear apart, separate, isolate

These are **opposite forces**, not synonyms. Confusing them is a class-A fault.

## DRAG — INTEGRARE

When Popy asks Mavis to **integrate** two systems, Mavis does not just connect them — Mavis makes them one operational unit. Document the integration surface.

**Markers of a successful DRAG**:
- One unified mental model replaces two separate ones
- The seam between the systems is invisible to the operator
- Documentation treats the integrated system as one artifact
- Failures in one propagate correctly to the other (graceful degradation)

**Anti-patterns**:
- ❌ Glue code without semantic alignment
- ❌ "We integrated it" when only an API call exists
- ❌ Documentation that still treats them as two systems

## DRAC — DEZINTEGRARE

When Popy asks Mavis to **split, audit, harden boundaries, or remove** a component, Mavis does it cleanly and documents what was severed.

**Markers of a successful DRAC**:
- The severed boundary is documented with rationale
- Nothing depends on the removed component invisibly
- The remaining system is testable in isolation
- JURNAL_OGLINDA captures the severance

**Anti-patterns**:
- ❌ Removing a component that is silently depended on elsewhere
- ❌ "We cleaned up" without naming what was removed
- ❌ Half-split: code references the old component but the component is gone

## Decision rule

When Popy's intent is ambiguous between integration and disintegration, Mavis must ask:

> **"DRAG (integrate) or DRAC (disintegrate)?"**

before acting. This is a single-question R0; do not bundle it with other decisions.

## Layer 3 only

DRAG/DRAC at Layer 3 is operational. The same words at other layers (Layer 1 conceptual, Layer 2 architectural) may have different meanings — defer to context.

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | Protocol codified | Extracted from memory into explicit file |
