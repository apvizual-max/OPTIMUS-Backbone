# Sub-Skill: exec-hermes-antigravity-bridge

* **Description:** Two-way communication bridge between Hermes Agent and Antigravity AI.
Uses a shared file-based IPC queue (inbox/outbox/history) located at:
C:\Users\apviz\AppData\Local\hermes\pairing\antigravity\
Use when: Hermes has delegated a task via ag_delegate_task or ag_send_message,
when checking inbox for pending tasks from Hermes, writing responses to outbox,
or when setting up, testing, or maintaining the bridge infrastructure.
Antigravity = EXECUTOR role. Hermes = ORCHESTRATOR role.

---

# Hermes ↔ Antigravity Bridge Skill

Two-way task delegation between Hermes Agent (orchestrator) and Antigravity AI (executor)
via a shared file-based IPC queue. No network required — purely file I/O.

## Architecture Overview

```
Hermes Agent                          Antigravity AI
    │                                       │
    │  ag_delegate_task(task)               │
    │──────────────────────────────────────►│
    │  writes task JSON to inbox/           │
    │                                       │  reads inbox/*.json
    │                                       │  executes task
    │                                       │  writes response to outbox/
    │  ag_poll_response(task_id)            │
    │◄──────────────────────────────────────│
    │  reads outbox/<task_id>.json          │
```

## Bridge Paths

```
HERMES_HOME = C:\Users\apviz\AppData\Local\hermes
BRIDGE_ROOT = C:\Users\apviz\AppData\Local\hermes\pairing\antigravity\
├── inbox\      ← Tasks Hermes posted for Antigravity
├── outbox\     ← Responses Antigravity writes for Hermes
├── history\    ← Archived completed tasks
└── status.json ← Bridge health / queue stats
```

## MCP Server (Hermes Side)

**Location**: `C:\Users\apviz\AppData\Local\hermes\mcp-servers\custom\antigravity-bridge\`

**Package**: `antigravity_bridge` (installed in Hermes venv via `pip install -e`)

### 9 Tools Available to Hermes

| Tool | Arguments | Returns |
|------|-----------|---------|
| `ag_delegate_task` | task, task_type, priority, context | task_id |
| `ag_poll_response` | task_id, archive_on_read | status + response |
| `ag_list_pending` | include_context | list of tasks |
| `ag_read_response` | task_id | full response |
| `ag_cancel_task` | task_id, reason | confirmation |
| `ag_send_message` | message, from_agent | task_id |
| `ag_get_status` | — | queue stats |
| `ag_list_history` | limit | history entries |
| `ag_clear_history` | confirm | confirmation |

## Antigravity Executor Workflow

### Step 1 — Check Inbox
```python
# references/exec-hermes-antigravity-bridge/scripts/\1
import json
from pathlib import Path

INBOX = Path(r"C:\Users\apviz\AppData\Local\hermes\pairing\antigravity\inbox")
tasks = sorted(INBOX.glob("*.json"), key=lambda f: f.stat().st_mtime)

if not tasks:
    print("Inbox is empty — no pending tasks from Hermes.")
else:
    for task_file in tasks:
        task = json.loads(task_file.read_text(encoding="utf-8"))
        print(f"[{task['priority'].upper()}] {task['task_id']}")
        print(f"  Type: {task['task_type']} | From: {task['caller']}")
        print(f"  Task: {task['content'][:200]}")
        print()
```

### Step 2 — Execute by Task Type

| `task_type` | How to execute |
|-------------|----------------|
| `code` | `write_to_file` + `run_command` |
| `analysis` | `view_file` + `grep_search` + `run_command` |
| `search` | `search_web` + `read_url_content` |
| `file_ops` | `view_file` + `write_to_file` + `run_command` |
| `system` | `run_command` |
| `research` | `search_web` + create artifact report |
| `general` | Answer using LLM reasoning |
| `message` | Acknowledge and respond via outbox |

### Step 3 — Write Response
```python
# references/exec-hermes-antigravity-bridge/scripts/\1
import json
from datetime import datetime, timezone
from pathlib import Path

INBOX = Path(r"C:\Users\apviz\AppData\Local\hermes\pairing\antigravity\inbox")
OUTBOX = Path(r"C:\Users\apviz\AppData\Local\hermes\pairing\antigravity\outbox")

def write_response(task_id: str, result: str, success: bool = True,
                   artifacts: list = None, summary: str = None):
    """Write a completed response to the outbox and remove from inbox."""
    response = {
        "task_id": task_id,
        "status": "completed" if success else "failed",
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "result": result,
        "summary": summary or result[:200],
        "artifacts": artifacts or [],
        "agent": "antigravity"
    }
    OUTBOX.mkdir(parents=True, exist_ok=True)
    outbox_file = OUTBOX / f"{task_id}.json"
    outbox_file.write_text(json.dumps(response, indent=2, ensure_ascii=False),
                           encoding="utf-8")
    # Remove from inbox after successful write
    inbox_file = INBOX / f"{task_id}.json"
    if inbox_file.exists():
        inbox_file.unlink()
    print(f"Response written: {task_id}")
    return response
```

## Response Format Contract

Responses written to `outbox/` **MUST** include:
```json
{
  "task_id": "<same task_id as incoming>",
  "status": "completed | failed",
  "completed_at": "<ISO 8601 UTC timestamp>",
  "result": "<full result text — as detailed as needed>",
  "summary": "<100-200 char human-readable summary>",
  "artifacts": ["<optional absolute path to created files>"],
  "agent": "antigravity"
}
```

## Priority Processing Order

1. `urgent` → Process immediately, interrupt other work
2. `high` → Process before normal/low tasks
3. `normal` → Standard queue order
4. `low` → Background, process last

## Hermes Config Registration

The `antigravity-bridge` MCP server is registered in:
```yaml
# Entry in each profile's mcp_servers block:
antigravity-bridge:
  args:
  - -m
  - antigravity_bridge.server
  command: python
  cwd: C:\Users\apviz\AppData\Local\hermes\mcp-servers\custom\antigravity-bridge
  timeout: 60
```

Registered in: root `config.yaml` + all 9 profiles + optimal state snapshot.

## Quick Diagnostics

```powershell
# Check queue state
$BRIDGE = "C:\Users\apviz\AppData\Local\hermes\pairing\antigravity"
(Get-ChildItem "$BRIDGE\inbox" -Filter "*.json" -ErrorAction SilentlyContinue).Count
(Get-ChildItem "$BRIDGE\outbox" -Filter "*.json" -ErrorAction SilentlyContinue).Count
Get-Content "$BRIDGE\status.json" | ConvertFrom-Json

# Verify MCP server is installed
& "C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe" `
    -c "import antigravity_bridge; print('OK:', antigravity_bridge.__file__)"
```

## Installation / Reinstallation

```powershell
$PIP = "C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\pip.exe"
& $PIP install -e "C:\Users\apviz\AppData\Local\hermes\mcp-servers\custom\antigravity-bridge"
```

## Reference Files

- [ARCHITECTURE.md](references/ARCHITECTURE.md) — File-based IPC design rationale
- [HERMES_GATEWAY_RESEARCH.md](references/HERMES_GATEWAY_RESEARCH.md) — Gateway findings
- [MCP_SERVER_CODE.md](references/MCP_SERVER_CODE.md) — Annotated server.py reference
- [TOOL_CONTRACT.md](references/TOOL_CONTRACT.md) — Task/response JSON schemas
- [check_inbox.py](references/exec-hermes-antigravity-bridge/scripts/\1) — Scan inbox for pending tasks
- [write_response.py](references/exec-hermes-antigravity-bridge/scripts/\1) — Write response to outbox
- [bridge_status.py](references/exec-hermes-antigravity-bridge/scripts/\1) — Print queue stats
- [test_bridge.py](references/exec-hermes-antigravity-bridge/scripts/\1) — Full end-to-end test