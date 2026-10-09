# Sub-Skill: exec-qwen-mcp-sse-bridge

* **Description:** Technical guide to run the Qwen Desktop MCP Filesystem Server over an HTTP SSE Bridge to bypass space-containing Windows paths and avoid spawn errors (-32000).

---

# Qwen MCP SSE Bridge Setup

A technical guide and skill description explaining the architecture and maintenance of the Qwen Desktop Filesystem MCP bypass bridge on Windows.

## When to Use
- When Qwen Desktop App throws a `-32000: Connection closed` or `ENOENT` spawn error when trying to configure local directories with spaces in their paths (e.g. `D:\Alex - KV Obsidian`).
- When the Qwen Desktop App config gets reset on startup by IPC command default overrides.
- When you need to establish secure local HTTP (Server-Sent Events) communication for MCP servers.

## Prerequisites
- Node.js installed.
- `@modelcontextprotocol/server-filesystem` installed locally or available via npx.
- Access to the tools directory: `C:\Users\apviz\AI_Tools`.

---

## 1. The Space-Splitting Path Bug
In Qwen Desktop (which is an Electron webview wrapper), MCP commands configured via JSON are spawned using Bun (`bun.exe x -y [args...]`) with `shell: true`. 
On Windows, when a shell parses paths containing spaces (like `D:\Alex - KV Obsidian`), it splits the path on spaces into separate arguments (e.g. `D:\Alex`, `-`, `KV`, `Obsidian`), causing initialization to crash with `ENOENT` (error code `-32000`).

---

## 2. SSE Bridge Architecture
To solve this, we bypass stdio execution by routing the MCP requests through an HTTP Server-Sent Events (SSE) server running locally. Bun is instructed to only run a clean command with no spaces (`mcp-remote http://127.0.0.1:3010/sse`), while our local Node.js bridge spawns the actual filesystem server with `{ shell: false }`, ensuring path strings are passed intact.

### Component 1: Node.js Bridge Server
**File Location**: `C:\Users\apviz\AI_Tools\mcp-filesystem-sse-bridge.js`
This script starts an HTTP server on port 3010, listens to SSE connections on `/sse`, spawns the filesystem script with `{ shell: false }`, and translates stdin/stdout to HTTP posts and EventStreams.

### Component 2: Background Startup Launcher
**File Location**: `C:\Users\apviz\AI_Tools\start_mcp_bridge.vbs`
Launches the Node server silently without displaying a console window:
```vbscript
Option Explicit
Dim sh
Set sh = CreateObject("WScript.Shell")
sh.Run "node.exe ""C:\Users\apviz\AI_Tools\mcp-filesystem-sse-bridge.js""", 0, False
```

### Component 3: Permanent Scheduled Task
A Windows Scheduled Task named `QwenMcpFilesystemBridge` is configured to run at user login, launching the `.vbs` script silently.

---

## 3. Qwen Configuration
To wire up the Qwen Desktop App to the bridge:
1. Open Qwen Desktop settings.
2. Go to **Add using JSON** (or configure MCP Servers JSON).
3. Paste the following configuration under a unique name (e.g., `filesystem-full`):
   ```json
   {
     "mcpServers": {
       "filesystem-full": {
         "command": "npx",
         "args": [
           "-y",
           "mcp-remote",
           "http://127.0.0.1:3010/sse"
         ]
       }
     }
   }
   ```
*Note: Do not name the server `Filesystem` because the remote Qwen webapp overrides the `Filesystem` configuration on every boot. Custom names like `filesystem-full` are preserved.*

---

## 4. Maintenance and Validation

### Verify Bridge is Running:
```powershell
netstat -ano | findstr ":3010"
# Expected: TCP  127.0.0.1:3010  0.0.0.0:0  LISTENING
```

### Manually Start the Bridge:
```powershell
Start-ScheduledTask -TaskName "QwenMcpFilesystemBridge"
```