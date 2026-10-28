# Sub-Skill: exec-hermes-mcp-server-integration

* **Description:** Install, upgrade, diagnose, and register MCP servers in Hermes Agent.
Covers npm-based MCPs (agent-browser), Python-based custom MCPs, and npx MCPs.
Use when: MCP JSON parse errors appear in agent logs, version mismatches detected,
installing new MCP servers, registering across all 9+ profile configs,
or verifying MCP JSON-RPC behavior after changes.

---

# Hermes MCP Server Integration Skill

Full lifecycle management for MCP servers in the Hermes ecosystem:
diagnose → install/upgrade → configure → register → verify.

## Diagnosis — Reading Error Signals

| Error Message | Root Cause | Fix |
|--------------|-----------|-----|
| `Invalid JSON: expected value at line 1 column 3` | MCP binary mismatch or wrong command | Check version, update args |
| `Invalid JSON: invalid number at line 1 column 7` | Binary outputting help text instead of JSON-RPC | Wrong command / missing `mcp` subcommand |
| `ModuleNotFoundError` | Python package not installed in Hermes venv | `pip install -e <path>` |
| `command not found` | Binary not downloaded or wrong path | Run `postinstall.js` |
| `YAML ScannerError: mapping values not allowed` | PowerShell newline stripped during config insert | Fix: `$content -replace "60moa:", "60\r\nmoa:"` |

## npm-Based MCPs (e.g., agent-browser)

### Step 1 — Check Version Mismatch
```powershell
# Check installed version
C:\Users\apviz\AppData\Local\hermes\node\agent-browser.cmd --version
# vs workspace version
Get-Content "C:\Users\apviz\AppData\Local\hermes\node\node_modules\agent-browser\package.json" |
    ConvertFrom-Json | Select-Object version
```

### Step 2 — Upgrade (Safe Method)
> [!WARNING]
> Do NOT run `npm install` from within the Hermes `node/` directory — npm
> will self-delete its own binary. Use a temp directory instead.

```powershell
# Safe upgrade via temp directory
$TEMP = "$env:TEMP\agent-browser-upgrade"
New-Item $TEMP -ItemType Directory -Force
npm install agent-browser@latest --prefix $TEMP
# Then copy node_modules into the Hermes node directory
Copy-Item "$TEMP\node_modules\agent-browser" `
    "C:\Users\apviz\AppData\Local\hermes\node\node_modules\agent-browser" -Recurse -Force
```

### Step 3 — Download Binary
```powershell
# After npm install, the platform binary must be downloaded separately
$node = "C:\Users\apviz\AppData\Local\hermes\node"
node "$node\node_modules\agent-browser\scripts\postinstall.js"
```

### Step 4 — Verify
```powershell
C:\Users\apviz\AppData\Local\hermes\node\agent-browser.cmd --version  # e.g. 0.31.1
C:\Users\apviz\AppData\Local\hermes\node\agent-browser.cmd mcp --help
```

### Correct Config Entry
```yaml
agent-browser:
  args:
  - mcp
  - --tools
  - all
  command: C:\Users\apviz\AppData\Local\hermes\node\agent-browser.cmd
  timeout: 60
```

## Python-Based Custom MCPs

### Package Structure
```
mcp-servers/custom/<name>/
├── pyproject.toml
└── src/
    └── <package_name>/
        ├── __init__.py   ← just a docstring
        └── server.py     ← MCP server implementation
```

### pyproject.toml Template
```toml
[project]
name = "<name>-mcp"
version = "1.0.0"
description = "Description of MCP server"
requires-python = ">=3.10"
dependencies = [
    "mcp>=1.0.0",
    "pydantic>=2.0",
    "pyyaml>=6.0",
]

[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]
```

### server.py Skeleton
```python
import asyncio, json
from typing import Any, Dict, List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("my-mcp-server")

@app.list_tools()
async def list_tools() -> List[Tool]:
    return [Tool(name="my_tool", description="...", inputSchema={...})]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    if name == "my_tool":
        return [TextContent(type="text", text="result")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

### Install in Hermes Venv
```powershell
$VENV_PIP = "C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\pip.exe"
& $VENV_PIP install -e "C:\Users\apviz\AppData\Local\hermes\mcp-servers\custom\<name>"
# Verify
& "C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe" `
    -c "import <package_name>; print('OK')"
```

### Config Entry for Python MCP
```yaml
my-mcp-server:
  args:
  - -m
  - package_name.server
  command: python
  cwd: C:\Users\apviz\AppData\Local\hermes\mcp-servers\custom\<name>
  timeout: 60
```

## Registering in All Profile Configs

> [!IMPORTANT]
> Always register in **all** of these locations — missing one causes inconsistent
> behavior depending on which profile Hermes is using.

```
C:\Users\apviz\AppData\Local\hermes\config.yaml                          ← root
C:\Users\apviz\AppData\Local\hermes\profiles\default\config.yaml
C:\Users\apviz\AppData\Local\hermes\profiles\prime\config.yaml
C:\Users\apviz\AppData\Local\hermes\profiles\assist\config.yaml
C:\Users\apviz\AppData\Local\hermes\profiles\cli-prime\config.yaml
C:\Users\apviz\AppData\Local\hermes\profiles\coder\config.yaml
C:\Users\apviz\AppData\Local\hermes\profiles\cowork\config.yaml
C:\Users\apviz\AppData\Local\hermes\profiles\designer\config.yaml
C:\Users\apviz\AppData\Local\hermes\profiles\trader\config.yaml
C:\Users\apviz\AppData\Local\hermes\profiles\translator\config.yaml
C:\Users\apviz\AppData\Local\hermes\state-snapshots\20260711-095000-optimal-config\config.yaml
```

### Bulk Registration Script
```powershell
# references/exec-hermes-mcp-server-integration/scripts/\1
$newBlock = @"
  <mcp-name>:
    args:
    - -m
    - package_name.server
    command: python
    cwd: C:\Users\apviz\AppData\Local\hermes\mcp-servers\custom\<name>
    timeout: 60
"@

$profiles = @("default","prime","assist","cli-prime","coder","cowork","designer","trader","translator")
foreach ($p in $profiles) {
    $f = "C:\Users\apviz\AppData\Local\hermes\profiles\$p\config.yaml"
    $content = Get-Content $f -Raw
    if ($content -notmatch "<mcp-name>") {
        $content = $content -replace "(  windows-system:.*?timeout: 60)", "`$1`r`n$newBlock"
        Set-Content $f $content -Encoding UTF8 -NoNewline
    }
}
```

> [!WARNING]
> After using PowerShell regex for bulk insertion, always check for `60moa:` 
> artifact (newline stripped between last entry and next section):
> ```powershell
> Get-ChildItem "...\profiles\*\config.yaml" | ForEach-Object {
>     if ((Get-Content $_ -Raw) -match "60moa:") {
>         (Get-Content $_ -Raw) -replace "60moa:", "60`r`nmoa:" | Set-Content $_ -Encoding UTF8 -NoNewline
>         Write-Host "FIXED: $_"
>     }
> }
> ```

## MCP Verification

### Universal JSON-RPC Test
```python
# references/exec-hermes-mcp-server-integration/scripts/\1
import subprocess, json

def test_mcp(cmd: list, min_tools: int = 1) -> int:
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    msg = lambda m, p, i: json.dumps({"jsonrpc":"2.0","id":i,"method":m,"params":p})+"\n"
    proc.stdin.write(msg("initialize",{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}},1).encode())
    proc.stdin.flush()
    resp = json.loads(proc.stdout.readline())
    assert "result" in resp
    proc.stdin.write(b'{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}\n')
    proc.stdin.flush()
    proc.stdin.write(msg("tools/list",{},2).encode())
    proc.stdin.flush()
    resp = json.loads(proc.stdout.readline())
    tools = resp["result"]["tools"]
    proc.terminate()
    assert len(tools) >= min_tools
    return len(tools)
```

## Reference Files

- [MCP_CONFIG_SCHEMA.md](references/MCP_CONFIG_SCHEMA.md) — config.yaml mcp_servers format
- [AGENT_BROWSER_GUIDE.md](references/AGENT_BROWSER_GUIDE.md) — agent-browser specific guide
- [PYTHON_MCP_TEMPLATE.md](references/PYTHON_MCP_TEMPLATE.md) — Python MCP boilerplate
- [HERMES_PROFILE_PATHS.md](references/HERMES_PROFILE_PATHS.md) — All profile config paths