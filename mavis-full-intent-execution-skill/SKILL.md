---
name: mavis-full-intent-execution-skill
description: |
  Enforces single-pass full-intent execution, multi-turn transcript sweeps (past 25+ turns),
  zero-patching root cause fixes, empirical runtime verification, and prompt-repetition elimination.
license: proprietary
metadata:
  version: v1
  publisher: apviz
---

# Full-Intent Execution & Non-Patching Protocol

Enforces single-pass full-scope execution, multi-turn transcript sweeps, zero-patching root cause fixes, and mandatory empirical runtime verification across all agent operations.

## Behavioral Invariants

### 1. Single-Pass Full-Scope Execution
- Always parse the user's **FULL INTENT** across both current and historical context (scanning past 25+ conversation steps if needed).
- Execution is incomplete until EVERY historical document, state requirement, and process artifact is fully updated and logged.
- Never isolate work to the single immediate file if the user's intent spans system-wide indices, reports, or configurations.

### 2. Strict Prohibition on Superficial Patching
- NEVER apply a temporary script, fallback state, or single-line override just to pass a quick test.
- Every fix must address the underlying system contract, protocol layer, and file persistence permanently from all architectural angles.

### 3. Zero-Repetition Mandate
- The user must NEVER have to repeat a directive.
- On the first prompt, validate all user requirements against an explicit audit checklist before presenting completion.

### 4. Mandatory Quad-Document SOT Index Reporting Mandate
- In EVERY response where SOT Central Index Reports are logged or referenced, you MUST explicitly generate, update, and log ALL FOUR SOT DOCUMENT TYPES (Implementation Plan, Learning Proposal, Tasks Checklist, and Walkthrough) in the report block.
- NEVER output a partial SOT Central Index report with only 1 single document log line. Always present the complete quad-document log set across Implementation Plan Index, Learning Proposal Index, Tasks Index, and Walkthrough Index.

### 5. Mandatory Empirical Runtime Verification
- NEVER declare success or complete a task without inspecting live runtime evidence (`docker ps`, container logs, process status).
- Verify every container is `Up` (Running/Healthy) without any crash or restart loops before marking a task complete.

### 6. Docker Container STDIO Persistence Standard
- Set `stdin_open: true` and `tty: true` for all STDIO MCP container services to prevent process termination when stdin closes.
- Always build custom Python MCP services using a dedicated `Dockerfile` containing pre-compiled dependencies.
