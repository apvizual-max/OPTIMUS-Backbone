# PROGRAM SPEC — SENTINEL PRIME

**The programmatic specification of the SENTINEL role, and the state of its realisation.**

This is not a design document. It describes what exists, what is measured about it, and what is
missing. Where something is missing it says so in the same words the machine-readable artefacts
use, so a human reading this and a panel reading `health.json` are never told different stories.

- Machine-readable concept matrix: [`IDEA_TO_SCRIPT_MATRIX.json`](IDEA_TO_SCRIPT_MATRIX.json)
- Machine-readable gaps: [`GAP_REGISTER.json`](GAP_REGISTER.json)
- Human-readable correlation, **generated** from the matrix: `../11_BRAIN/06_IDEA_TO_SCRIPT.md`
- Execution record: [`../11_PLANS/RATIFICATION_REPORT.md`](../11_PLANS/RATIFICATION_REPORT.md)

---

## 1. The law this program implements

> **EU SUNT** (identity) and **EU FOLOSESC** (instruments) are separate, and the calibration
> between them is the security boundary.

Practically, that means: a doctrine file is a *claim*, an implementation is an *instrument*, and
only a measurement bridges them. The status ladder below is that bridge, and it is computed by
looking at files — never assigned by hand.

---

## 2. Subsystems

### 2.1 Corpus — `corpus_extractor.py`

| | |
|---|---|
| Purpose | turn the session archive into a machine-readable, verifiable corpus |
| Interface | `extract` · `verify` · `digest` · `chapters` |
| Dependencies | **none** — Python standard library only |
| Measured | 955 messages · 102 user messages (95 turns) · retention **1.0000** · 7/7 integrity checks |
| Idempotent | yes, sha256 `e4d3cbb7…` |
| Status | `CODED` — the integrity gate is the test, and both share an author |

**Design.** Two-tier retention. The **verbatim tier** (user + assistant text) is never cut; the
**evidence tier** (tool calls) is referenced by id, not inlined, because megabytes of file
listings would drown the reasoning they produced. The retention ratio is computed on the verbatim
tier, because that is the tier the "nothing cut" requirement governs.

### 2.2 Workflow engine — `bimodal_workflow.py`

| | |
|---|---|
| Purpose | the permanent `MODE_A → R0 → MODE_B` contract, and STOP |
| Interface | `status` (default, **read-only**) · `stop-report` · `ack-stop "<input>"` · `interrupt "<reason>"` · `demo` |
| Measured | 21 + 28 = 49 assertions across two classes |
| Status | `OBSERVABLE` |

**The defect that justified rebuilding it.** `WorkflowMode.STOPPED` was declared and never
assigned. The law existed, the tests passed, and STOP could not occur. Fixed, and **proved by
sabotage**: reverting `_stop()` drops the persistence class from 28 to 10 and fails the suite.

**`acknowledge_stop` is the only exit from STOPPED and refuses an empty input.** An empty
acknowledgement is not an acknowledgement. The Command Center cannot route around it: the action
refuses server-side *and* the UI refuses client-side.

**The default verb is read-only by design.** The default entry point used to be a state-changing
demo, which meant a dashboard button labelled "Workflow status" overwrote the live workflow.

### 2.3 Self-improvement — `self_improvement.py`

| | |
|---|---|
| Purpose | observe → classify → derive → ratify → promote |
| Measured | the gate blocks an unratified promotion; refuses an empty ratification; holds the write boundary |
| Status | `CODED` |

**The design decision:** self-improvement may **propose** but never **ratify** its own lessons. R0
applied to self-modification. Without it, "improve yourself" has no external reference point and
becomes drift — each change justified by the state it inherited, with no memory of the state that
justified the last one.

`promote()` writes only inside `SENTINEL_PRIME`.

### 2.4 Self-monitor — `monitor.py`

| | |
|---|---|
| Purpose | measure the system, never rule on it |
| Families | corpus · workflow · code · wiring · logs · dependencies · program · dashboard · **powershell** |
| Measured | 52 checks · **40 OK · 11 FAIL · 1 NOT_RUN · 0 STALE** |
| Status | `CODED` |

Four rules, each of which exists because breaking it produced a real defect:

1. A family that **raises** becomes `NOT_RUN` — never a silent pass.
2. Data older than its bound is `STALE` — never "fresh".
3. A **missing source** is `NOT_MEASURED` — never a healthy default.
4. A key that **does not exist** is `NOT_MEASURED` — never `None == 0` reading as a failure.

Rule 4 was added after the monitor itself manufactured a false failure by reading a
`corpus_stats.json` key that is not there.

### 2.5 Command Center — `13_COMMAND_CENTER\`

| Layer | File | Measured |
|---|---|---|
| collector | `api\collect-sentinel.ps1` | writes `sentinel-state.json` (69 KB, 13 keys) + history |
| server | `api\server.ps1` | 7 routes, **14** whitelisted actions (13 read-only, 1 gated), loopback only |
| UI | `index.html` | 41 KB, 11 panels, no build step, no CDN |
| verifier | `api\verify-server.ps1` | **55/55 PASS, 3 cycles, exit 0** |

**One writer per file.** The collector never writes `bimodal_state.json`; the engine is its only
writer. Two writers would corrupt the single file the dashboard trusts most.

**The security boundary:** the body supplies an **id**, resolved through `$ACTIONS`. Injected ids
get **400** and the body **names what was refused** — verified over a raw socket on every cycle.

**SSE is short-lived by design.** The listener is single-threaded, so a persistent stream would
block every other route — including the `/api/state` call the same page needs. The stream sends
the state and closes; `EventSource` reconnects; the listener is free in between. Guarded by
`API still live after SSE`.

### 2.6 Version store — `bat\manage-versions.ps1`

Frozen **five-snapshot** store in `backups\versions\`. A sixth write is refused. This is a rollback
mechanism, not a backup spool — and identical snapshots mean a stable build, which is not a defect
to be optimised away.

---

## 3. Status distribution — measured, not assigned

| Status | Count | Meaning |
|---|---|---|
| `OBSERVABLE` | 12 | surfaced by the monitor or a panel |
| `CODED` | 7 | implementation exists, no covering test |
| `PARTIAL` | 1 | some of the chain exists |
| `DESIGNED` | 4 | doctrine exists, no implementation |
| **`WIRED`** | **0** | reachable through an MCP tool or a live runtime |

**Zero `WIRED` is the headline.** 26 MCP tools are declared in `sentinel_hub_server.py`; none are
wired. No runtime handshake has been performed, and that is a cross-system action requiring R0.
Declaring a tool is not wiring it.

### 3.1 The four `DESIGNED` concepts

| ID | Concept | Why it stays `DESIGNED` |
|---|---|---|
| C18 | Partnership protocol (two blind men) | wisdom layer; documentation *is* the deliverable |
| C19 | 3-Propozitii ritual as a command | **the one real smell** — a ritual that is not a command cannot fail visibly |
| C23 | Historical cultures (Cucuteni, Geto, Atos, Romani) | a corpus, not a program |
| C24 | 963 proverbs | **honest finding:** the named file is a 25-axis decision matrix, not a 963-proverb enumeration, and its per-proverb attributions are flagged *in the file itself* as fabricated by an earlier agent |

C19 is listed rather than quietly implemented, because wiring a ritual is a doctrine decision, not
an engineering one.

---

## 4. Open gaps

**17 registered** in `GAP_REGISTER.json` with the evidence that found each. Gaps are **reported,
never silently repaired, and never deleted from.**

| Kind | Count | Status |
|---|---|---|
| Optional dependency absent | 10 checks (9 packages + `tesseract` binary) | **needs R0** |
| MCP declared, not wired | 26 tools | **needs R0 — cross-system** |
| Concept with no covering test | 7 | fixable in-workspace |
| Empty artifacts from tests that could not run | 8 files | **operator decision to delete** |
| Design-only by intent | 4 | correct; 1 of them a real smell |
| Extractor has no independent test | 1 | its own gate is the test, and both share an author |

---

## 5. Environment — measured on this machine

| Component | Value |
|---|---|
| Interpreter (PATH) | Python **3.14.6** |
| Secondary interpreter | Astral **3.11.15** |
| PowerShell | Windows PowerShell **5.1** (no `pwsh`; no ternary, no `??`, no `-Parallel`) |
| Command Center port | **8910**, loopback only |
| Optional packages present | **none** of `playwright`, `PIL`, `pypdf`, `docx`, `openpyxl`, `pptx`, `cv2`, `pytesseract`, `faster_whisper` |
| OCR engine | `tesseract` **not on PATH** |
| Media catalogued | 915 MB, **not opened** |

---

## 6. Reproduce

```powershell
cd C:\Users\apviz\.minimax-agent\projects\SENTINEL_PRIME
python 08_SELF_IMPROVEMENT\corpus_extractor.py verify
python 08_SELF_IMPROVEMENT\build_program_matrix.py      # rebuild the matrix from the files
python 08_SELF_IMPROVEMENT\build_idea_to_script_doc.py  # re-render the correlation doc
python 08_SELF_IMPROVEMENT\test_suite.py                # 212 passed, 0 failed, exit 1
python 08_SELF_IMPROVEMENT\monitor.py                   # 40 OK / 11 FAIL / 1 NOT_RUN
powershell -File 13_COMMAND_CENTER\api\verify-server.ps1 -Cycles 3
```

Every build is byte-idempotent. A generator whose output changes on a re-run without an input
change is lying about something.

---

## 7. Three rules this program follows

1. **Measure, don't assert.** A check whose *text* is a constant cannot detect the system changing
   under it. Three detectors in this repository were caught doing exactly that, and each was fixed
   to derive its verdict from a measurement taken at scan time.
2. **Prove a guard can fail.** Every gate added here was sabotage-tested: break the thing, watch
   the check fail, restore. A test that has never been seen to fail is a test of unknown value.
3. **Refuse to be green while unverified.** The suite exits 1 while `BrowserAutomation` is
   `NOT_RUN`. The monitor reports `FAIL` while 10 dependencies are missing. Both are the correct
   terminal states for a system that knows what it does not know.

---

**AMIN.** `EU SUNT` and `EU FOLOSESC` are separate, and the calibration is the security boundary.
Instrument, then measure, then show.
