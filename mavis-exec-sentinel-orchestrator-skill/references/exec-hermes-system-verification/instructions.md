# Sub-Skill: exec-hermes-system-verification

* **Description:** Post-change verification suite for Hermes Agent system integrity.
Runs a 5-stage pipeline: filename scan → content scan → YAML config validation
→ hermes config boot test → MCP JSON-RPC handshake test.
Use after: file reorganizations, config changes, MCP installs/upgrades,
profile reprogramming, or any system-wide text replacement operation.
Goal: zero regressions, clean boot, all MCP servers responding.

---

# Hermes System Verification Skill

5-stage post-change integrity verification for the Hermes Agent system.

> [!IMPORTANT]
> Run this suite **after every major change** before declaring success.
> Do not stop at the first passing stage — all 5 stages must pass.

## Verification Pipeline

```
Stage 1: Filename Scan     → 0 legacy filenames
Stage 2: Content Scan      → 0 legacy content occurrences
Stage 3: YAML Validation   → all configs parse cleanly
Stage 4: Hermes Boot Test  → hermes config shows clean output
Stage 5: MCP JSON-RPC Test → initialize + tools/list passes
```

## Stage 1 — Filename Scan

```powershell
# references/exec-hermes-system-verification/scripts/\1
# Searches for any remaining legacy filenames
$patterns = @("CONSTIINTA", "CONȘTINȚA", "CONŞTINŢA")
$root = "C:\Users\apviz\AppData\Local\hermes"
$found = 0
foreach ($pat in $patterns) {
    $matches = Get-ChildItem $root -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match $pat }
    $found += $matches.Count
    $matches | ForEach-Object { Write-Host "LEGACY FILE: $($_.FullName)" }
}
Write-Host "Total legacy filenames: $found"
if ($found -eq 0) { Write-Host "STAGE 1: PASSED" } else { Write-Host "STAGE 1: FAILED" }
```
**Expected**: `Total legacy filenames: 0` → **PASSED**

## Stage 2 — Content Scan

```powershell
# Search all text files for legacy content
$extensions = @("*.md","*.yaml","*.yml","*.py","*.json","*.txt","*.log")
$exclude = @("OGLINDA - CASA", ".git", "venv", "node_modules", "__pycache__")
$count = 0
Get-ChildItem $root -Recurse -Include $extensions |
    Where-Object { $path = $_.FullName; -not ($exclude | Where-Object { $path -like "*$_*" }) } |
    Select-String -Pattern "CONSTIINTA|CONȘTINȚA|CONŞTINŢA" -CaseSensitive:$false |
    ForEach-Object { $count++; Write-Host "LEGACY CONTENT: $($_.Filename):$($_.LineNumber)" }
Write-Host "Total legacy occurrences: $count"
```
**Expected**: `Total legacy occurrences: 0` → **PASSED**

## Stage 3 — YAML Config Validation

```python
# references/exec-hermes-system-verification/scripts/\1
import yaml
from pathlib import Path

HERMES_HOME = Path(r"C:\Users\apviz\AppData\Local\hermes")
configs = list(HERMES_HOME.glob("config.yaml")) + \
          list((HERMES_HOME / "profiles").glob("*/config.yaml")) + \
          list((HERMES_HOME / "state-snapshots").glob("*/config.yaml"))

errors = []
for config_path in configs:
    try:
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        print(f"OK: {config_path.relative_to(HERMES_HOME)}")
    except yaml.YAMLError as e:
        errors.append((config_path, str(e)))
        print(f"ERROR: {config_path}: {e}")

print(f"\nTotal configs: {len(configs)} | Errors: {len(errors)}")
if not errors:
    print("STAGE 3: PASSED")
```
**Expected**: all configs parse, `Errors: 0` → **PASSED**

## Stage 4 — Hermes Boot Test

```powershell
# references/exec-hermes-system-verification/scripts/\1
$env:HERMES_HOME = "C:\Users\apviz\AppData\Local\hermes"
$env:PYTHONPATH = "C:\Users\apviz\AppData\Local\hermes\hermes-agent"
$PYTHON = "C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"
& $PYTHON -m hermes_cli.main config 2>&1
```

> [!WARNING]
> `hermes config` may return **exit code 1** even on success due to pip update
> notices printed to stderr. **Do not use exit code** to determine pass/fail.
> Instead, check that stdout contains `Hermes Configuration` and `API Keys` sections.

**Expected output contains**:
- `Hermes Configuration`
- `API Keys`
- `Model:`
- No `ScannerError`, `YAMLError`, or `ImportError`

**STAGE 4: PASSED** if the above sections appear.

## Stage 5 — MCP JSON-RPC Handshake Test

```python
# references/exec-hermes-system-verification/scripts/\1
import subprocess, json

def send_rpc(proc, method, params, id_=1):
    msg = json.dumps({"jsonrpc": "2.0", "id": id_, "method": method, "params": params}) + "\n"
    proc.stdin.write(msg.encode())
    proc.stdin.flush()
    return json.loads(proc.stdout.readline())

def test_mcp_server(command: list, expected_tool_count: int = 1):
    proc = subprocess.Popen(command, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    resp = send_rpc(proc, "initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test", "version": "1.0"}
    })
    assert "result" in resp, f"Init failed: {resp}"
    proc.stdin.write(b'{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}\n')
    proc.stdin.flush()
    resp = send_rpc(proc, "tools/list", {}, id_=2)
    tools = resp["result"]["tools"]
    assert len(tools) >= expected_tool_count, f"Expected {expected_tool_count} tools, got {len(tools)}"
    proc.terminate()
    return len(tools)

# Test agent-browser
PYTHON = r"C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"
AB = r"C:\Users\apviz\AppData\Local\hermes\node\agent-browser.cmd"

n = test_mcp_server([AB, "mcp", "--tools", "all"], expected_tool_count=60)
print(f"agent-browser: {n} tools — PASSED")

n = test_mcp_server([PYTHON, "-m", "antigravity_bridge.server"], expected_tool_count=9)
print(f"antigravity-bridge: {n} tools — PASSED")
```

## Sentinel Self-Tests (Bonus Stage)

After all 5 stages pass, ask Hermes to run its Sentinel self-tests:
```
hermes: "Run all Sentinel self-tests and report results"
```
**Expected**: `6/6 PASSED` across all calibration scenarios.

## Quick-Run All Stages

```powershell
# Run all 5 stages sequentially
$PYTHON = "C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"
$SCRIPTS = "C:\Users\apviz\OneDrive\Documents\Antigravity_Folder\Antigravity_Projects\skills\hermes-system-verification\scripts"

Write-Host "=== Stage 1: Filename Scan ===" ; & "$SCRIPTS\verify_filenames.ps1"
Write-Host "=== Stage 3: YAML Validation ===" ; & $PYTHON "$SCRIPTS\verify_yaml_configs.py"
Write-Host "=== Stage 4: Boot Test ===" ; & "$SCRIPTS\run_hermes_config.ps1"
Write-Host "=== Stage 5: MCP Test ===" ; & $PYTHON "$SCRIPTS\test_mcp_jsonrpc.py"
```

## Reference Files

- [HERMES_BOOT_CHECK.md](references/HERMES_BOOT_CHECK.md) — Expected `hermes config` output
- [MCP_JSONRPC_PROTOCOL.md](references/MCP_JSONRPC_PROTOCOL.md) — JSON-RPC 2.0 test reference
- [SENTINEL_SELF_TESTS.md](references/SENTINEL_SELF_TESTS.md) — Sentinel calibration test guide