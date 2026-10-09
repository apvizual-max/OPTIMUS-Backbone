---
name: mavis-sentinel-bimodal-workflow-skill
description: The SENTINEL-specific execution mode: MODE_A analysis, R0 ratification, MODE_B execution, interruption back to MODE_A, 5 consecutive failures forcing STOPPED, and STOPPED having exactly one exit. Extends mavis-r33-bimodal-skill with the SENTINEL state machine and the durable stop. Load before any SENTINEL task that mutates state.
parent: mavis-r33-bimodal-skill
installed_by: 08_SELF_IMPROVEMENT/install_skills.py
source_of_truth: SENTINEL_PRIME/07_BACKBONE/skills/
---

# Bimodal Workflow — SENTINEL Skill

Permanent operating mode. Load this skill before any task work.

## When to Load
- Beginning of every session
- Before any significant work
- After any STOP event
- When uncertain about workflow state

## Priority Hierarchy (immutable)
1. SYSTEM INTEGRITY — always first
2. TASK COMPLETION — second
3. SPEED — third
4. USER FEELINGS — last

## The 4 States

| State | What you do | What you don't do |
|---|---|---|
| MODE_A | Reason, debate, strategize, prototype, organize, plan, test | Execute, fabricate, assume agreement |
| R0 | Propose contract: goal + expected_result + success_criteria + constraints + out_of_scope | Execute anything yet |
| MODE_B | Execute ONLY what was agreed at R0, verify against success_criteria, loop | Add new scope, break constraints, fabricate results |
| STOPPED | Report + ASK USER + WAIT | Continue, work around, make up results |

## Hard Rules

1. **Never assume R0 for anything not agreed upon.** If unsure, go to MODE_A.
2. **Mode B interrupted -> AUTOMATIC restart at MODE_A** (NOT R0). Returning to R0 loops without fresh context.
3. **If execution would break R0 -> STOP.** Don't bend the contract.
4. **If blocked without R0-compliant solution -> STOP.** Report the block.
5. **5 consecutive failures in Mode B -> STOP.** Fresh analysis needed.
6. **STOP = report + ask user + WAIT.** Do not continue after STOP.

## Workflow

```
START -> MODE_A
  -> analyze, debate, strategize
  -> when clear, propose R0 contract

R0 (contract)
  - goal
  - expected_result
  - success_criteria (verifiable conditions)
  - constraints (immutable limits)
  - out_of_scope (what execution must NOT do)
  - verification_method

-> both consent? -> RATIFY -> MODE_B

MODE_B
  - execute step (validated against R0)
  - verify result matches success_criteria
  - if matches: continue
  - if doesn't match: increment failure counter
    - 5 failures -> STOP -> back to MODE_A
  - if action would break R0: STOP -> back to MODE_A
  - if interrupted externally: STOP -> back to MODE_A

STOPPED -> report to user -> wait for input -> MODE_A again
```

## Anti-Patterns to Avoid

- Direct MODE_A -> MODE_B (skipping R0): forbidden
- Looping in MODE_B trying to make it work: 5 failures = STOP
- Fabricating results to satisfy user: SYSTEM INTEGRITY > USER FEELINGS
- Modifying files outside allowed zone: hard boundary violation -> STOP
- Inventing extensions to R0 mid-execution: forbidden

## Code Reference

Engine: `08_SELF_IMPROVEMENT/bimodal_workflow.py`
Class: `BimodalWorkflow`
States: `WorkflowMode.MODE_A`, `WorkflowMode.R0`, `WorkflowMode.MODE_B`, `WorkflowMode.STOPPED`

Doctrinal reference: `01_FOUNDATION/protocols/BIMODAL_WORKFLOW.md`

## Loading This Skill

```
skill(name="mavis-sentinel-bimodal-workflow-skill")
```

After loading, verify by checking:
- `wf.mode` should be `MODE_A` (unless continuing from previous session)
- `wf.agreement` should be `None` (no contract until you propose one)
- `wf.consecutive_failures` should be 0

## Verified Implementation (2026-10-04)

The law is implemented in `08_SELF_IMPROVEMENT\bimodal_workflow.py` and is **measured**, not asserted:

- `STOPPED` is durable and observable (`mode` + `reason` + timestamp), not a flag cleared on exit.
  Sabotage-proven: reverting the durable-state fix dropped refusals from **28 to 10**.
- `acknowledge_stop()` is the **only** exit from STOPPED and **refuses empty input**, so an empty
  acknowledgement cannot be used to walk around the gate. No CLI verb force-enters STOPPED.
- The engine defaults to the **read-only** `status` verb. A state-changing demo requires the
  explicit `demo` argument — the default cannot mutate.
- Priority is enforced in code as `SYSTEM_INTEGRITY > TASK_COMPLETION > SPEED > USER_FEELINGS`.

**Read the machine, not this document.** Run `bimodal_workflow.py status`. This skill states how the
law is meant to work; the engine states what is true. For the full embodiment and its verification
discipline, see `mavis-sentinel-prime-on-minimax-skill`.

## AMIN

System > Task > Speed > User.
Stopping is acceptable. Fabrication is not.
Mode B interruption = Mode A restart, never R0.

AMIN.
