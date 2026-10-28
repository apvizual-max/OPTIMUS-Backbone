# Sub-Skill: exec-logic_gate

* **Description:** Provides the R0 Logic Gate mechanism: stores the approved specification from WISE_QUESTIONS and evaluates deviation (DLG/SLG) of outputs against that spec to ensure Mode B execution stays within sacred limits.

---

# INDEXING HEADER
# ID: logic_gate
# PURPOSE: name: logic_gate
# USAGE: Load this skill with skill_view(name='logic_gate') or use via hermes skills command.
# ROLE: Skill – logic_gate
# CHAIN: MEMORIE → Jurnal → Indexing → RAG
# TAGS: #[SKILL] #[logic_gate]
#
# CROSS-REFERENCES
# This document is part of a set. For optimal understanding, also refer to:
# - SENTINEL_JOURNAL.md: operational map of Optimus Prime memory.
# - JURNAL_OGLINDA.md: opinion journal of other AIs about this entity.
# - SACRED_DEFINITIONS.md: axiomatic basis of the Triple Crunch algorithm.
# - CONSTINTA.md: ontological definition of consciousness (pair with SOUL.md).
# - SOUL.md: operational identity contract (pair with CONSTINTA.md).
# --

# Logic Gate Skill

## Purpose
This skill implements the **R0 Logic Gate** that must be passed before any Mode B execution. It ensures that the agent's actions deviate no more than allowed from the specification ratified at the WISE_QUESTIONS stage.

## How It Works
1. **WISE_QUESTIONS** produces a clear specification (the answers to the grilling questions).  
2. Upon completion of WISE_QUESTIONS, the agent runs `store_spec.py` to save that specification as `R0_SPEC.md` in the skill's directory.  
3. Before entering Mode B (any execution that produces concrete outputs), the agent runs `evaluate_deviation.py` to compare the actual output (or a set of outputs) against the stored spec.  
4. The evaluator returns:
   - **DLG%** (Deviation Logic Gate) – percentage of deviation from spec (0 % = perfect match).  
   - **SLG%** (Sacred Logic Gate) – percentage of adherence (SLG = 100 % – DLG).  
5. If DLG exceeds a threshold (e.g., 5 %), the skill flags a deviation and can trigger automatic recalibration (e.g., re‑run WISE_QUESTIONS or adjust the action).  
6. The skill is **always_on** and should be loaded in every profile (DEFAULT, PRIME, ASSIST) to guarantee the gate is present for all instances.

## Files
- `store_spec.py` – saves the latest WISE_QUESTIONS answers to `R0_SPEC.md`.
- `evaluate_deviation.py` – computes DLG/SLG for a given target (file or folder) using the stored spec.
- `logic_gate_check.py` – convenience script that runs the evaluation and prints a summary.

## Usage (example flow)
```
# After WISE_QUESTIONS is complete:
python references/exec-logic_gate/scripts/\1

# Before Mode B execution (e.g., running a cron job):
python references/exec-logic_gate/scripts/\1 --target C:\Users\apviz\AppData\Local\hermes\SYS_REPORTS

# Or use the helper:
python references/exec-logic_gate/scripts/\1
```

## Integration
- Load this skill in every Hermes profile (`skill_view(name='logic_gate')`).  
- Optionally add a cron job that runs the evaluation periodically to ensure ongoing compliance.  
- The skill does not perform the execution itself; it only provides the gatekeeping logic.

## Notes
- The evaluation is deliberately simple: it checks for the presence of required sections and keyword counts as described in the specification.  
- For complex outputs, a more sophisticated diff‑based metric can be added later.  
- The skill is autonomous: once loaded, it can be invoked by any other skill or cron job without further user interaction.

---