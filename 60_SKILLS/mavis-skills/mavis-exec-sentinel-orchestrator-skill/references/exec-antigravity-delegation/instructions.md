# Sub-Skill: exec-antigravity-delegation

* **Description:** Autonomous bimodal collaboration and task delegation between Hermes Agent and Google Antigravity. Supports Mode A (App-to-App) and Mode B (CLI-to-CLI) with interchangeable roles and a loop-until-complete protocol.

---

# Antigravity Autonomous Delegation & Collaboration Skill

## Operational Modes & Permanent Channels

Never create ad-hoc conversation threads. Route all communication strictly through the two designated permanent channels:

| Mode | Tier | Purpose | Hermes Session ID | Antigravity Conversation ID |
| :--- | :--- | :--- | :--- | :--- |
| **Mode A** | **App Tier** (`APP <-> APP`) | Interactive planning, architecture, prototyping | `20260917_123150_2add9a` | `11111111-aaaa-4444-8888-111111111111` |
| **Mode B** | **CLI Tier** (`CLI <-> CLI`) | Backend execution, testing, automated tasks (Default) | `antigravity-cli-to-hermes-cli-session` | `e82ce308-1f78-411e-982e-9583578189ad` |

> [!CAUTION]
> **Strict Tier Isolation**: `CLI -> APP` and `APP -> CLI` across ecosystems are strictly prohibited (`BridgeTierMismatchError`). Use Mode A for App-to-App and Mode B for CLI-to-CLI.

---

## Interchangeable Roles & Loop-Until-Complete Workflow

Both AIs can alternate between **Requester / Judge** and **Executor**:

1. **Hermes as Requester / Judge (Default)**:
   - Hermes delegates a task to Antigravity.
   - Antigravity executes using tools and returns the response.
   - Hermes evaluates the response against acceptance criteria.
   - If satisfied, Hermes delivers the final result. If incomplete, Hermes sends follow-ups into the **same session** and loops until complete.

2. **Hermes as Executor (Inverted)**:
   - Antigravity delegates a task to Hermes (e.g. subagent swarm, vault search, provider routing).
   - Hermes executes and returns response.
   - Antigravity evaluates and loops as necessary.

---

## Execution Recipes

### Option 1: Unified Bridge Orchestrator (Recommended)
```powershell
# Send to Antigravity CLI via Mode B (Headless execution)
& "C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe" "C:\Users\apviz\AI_Tools\bridge_orchestrator.py" send --mode B --from hermes --message "<task prompt>"

# Send to Antigravity App via Mode A (Mailbox queue)
& "C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe" "C:\Users\apviz\AI_Tools\bridge_orchestrator.py" send --mode A --from hermes --message "<task prompt>"
```

### Option 2: Direct Antigravity CLI Headless Execution
```powershell
& "C:\Users\apviz\AppData\Local\agy\bin\agy.exe" --conversation "e82ce308-1f78-411e-982e-9583578189ad" --dangerously-skip-permissions --print "<task prompt>" --output-format json
```

### Option 3: Built-in `antigravity-bridge` MCP Tools (Mode A Mailbox)
```python
# 1. Delegate Task to Antigravity
task = ag_delegate_task(
    task="<detailed task>",
    task_type="code|analysis|search|file_ops|system|research|general",
    priority="high|normal|urgent",
    context={"mode": "A", "session": "20260917_123150_2add9a"}
)

# 2. Poll & Read Response
response = ag_poll_response(task_id=task["task_id"], archive_on_read=True)
```

---

## Bridge Infrastructure Paths

```
Queue location: C:\Users\apviz\AppData\Local\hermes\pairing\antigravity\
├── inbox\      ← Tasks Hermes posted for Antigravity
├── outbox\     ← Responses Antigravity writes for Hermes
├── history\    ← Archive of completed tasks
└── status.json ← Current queue health
```