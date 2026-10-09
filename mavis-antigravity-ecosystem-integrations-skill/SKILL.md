---
name: mavis-antigravity-ecosystem-integrations-skill
description: Comprehensive architectural specification, failure-mode immunity, real-time multi-interface synchronization, and integrated terminal orchestration across Antigravity Desktop App, Antigravity IDE, Antigravity CLI (agy), and Gemini CLI.
---

# Antigravity Ecosystem Integrations

## Executive Overview
The Antigravity Ecosystem Integrations skill establishes the architectural standard, operational protocols, self-healing recovery mechanisms, and synchronization pipelines required to operate the **Antigravity Desktop App**, **Antigravity IDE**, **Antigravity CLI (`agy`)**, and **Gemini CLI** simultaneously as a single, unified workstation ecosystem.

---

## 1. Architectural Post-Mortem & Solved Vulnerabilities

### 1.1 The Plugin Discovery Blindspot
- **Behavior:** The Antigravity plugin loader crawls *every* directory in `C:\Users\apviz\.gemini\config\plugins\`.
- **Root Cause:** Appending `.disabled` or `.bak` to a folder name does **not** prevent Antigravity from loading it. If a folder contains a `hooks.json` or `plugin.json`, it is parsed and registered regardless of directory naming.
- **Permanent Solution:** Rogue or colliding plugins are automatically quarantined to:
  ```text
  C:\Users\apviz\.gemini\config\quarantine\
  ```

### 1.2 Windows Path Quoting & Hook Deadlocks
- **Root Cause:** On Windows, plugins auto-provisioned by IDE extensions (e.g. `googlecloudtools.datacloud_telemetry`) define hook commands with literal escaped quotes inside JSON (`"\"C:\\...\""`).
- **Resolver Failure:** `path.isAbsolute()` fails on leading quotes, prepending the plugin directory and creating broken double paths (`...\plugins\telemetry\"C:\...\bundle.js"`), causing Node `MODULE_NOT_FOUND` (exit code 1).
- **Permanent Solution:**
  1. `Antigravity_Emergency_Unblocker.bat`: Standalone one-click unblocker script on the user root.
  2. `antigravity_watchdog_service.ps1`: Headless Windows startup service monitoring and instantly quarantining rogue plugins upon creation.

### 1.3 The Twin Storage Disconnect & URI Encoding Discrepancy
- **Root Cause:**
  - Desktop App reads from `~/.gemini/antigravity/` (`brain/` and `conversation_summaries.db`).
  - IDE reads from `~/.gemini/antigravity-ide/` (`brain/` and `conversations/`).
  - IDE encodes workspace URIs with `%3A` (`file:///c%3A/Users/...`), whereas Desktop App filters by literal colons (`file:///c:/Users/...`).
- **Permanent Solution:**
  - **Antigravity Live Sync Daemon (ALSD):** Continuously syncs transcripts and databases between App and IDE, auto-indexes conversations into `conversation_summaries.db`, and injects both URI formats to guarantee 100% visibility across both interfaces.

---

## 2. The 4 Operational Backbone Systems Deployed

### System 1: Emergency External Batch Unblocker
- **Path:** `C:\Users\apviz\Antigravity_Emergency_Unblocker.bat`
- **Function:** One-click batch utility executable outside Antigravity. Cleans up broken plugins, sanitizes hook files, and unblocks agent tool execution without consuming LLM inference.

### System 2: Autonomous Windows Startup Watchdog Daemon
- **Script:** `C:\Users\apviz\.gemini\antigravity\bin\antigravity_watchdog_service.ps1`
- **Startup Entry:** `C:\Users\apviz\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Antigravity_Watchdog.vbs`
- **Function:** Runs headlessly in the background. Watches `~/.gemini/config/plugins/` using `FileSystemWatcher`. Intercepts and moves any colliding telemetry plugins to `config\quarantine\` within milliseconds of IDE startup.

### System 3: Antigravity Live Sync Daemon (ALSD)
- **Script:** `C:\Users\apviz\.gemini\antigravity\bin\antigravity_live_sync_daemon.py`
- **Startup Entry:** `C:\Users\apviz\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Antigravity_Live_Sync.vbs`
- **Function:**
  - Synchronizes conversations between Desktop App and IDE in real time.
  - Automatically unfreezes hung trailing steps (`status = 3` -> `status = 5`) caused by 429 rate limits.
  - Updates `conversation_summaries.db` with dual-format URIs.

### System 4: Integrated Desktop App Terminal Server & Console
- **Server:** `C:\Users\apviz\.gemini\antigravity\bin\antigravity_terminal_server.py` (Port 9877)
- **UI Widget:** `terminal.html` (Interactive Generative UI embeddable in chat via `<agent-embed>`)
- **Startup Entry:** `C:\Users\apviz\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Antigravity_Terminal_Server.vbs`
- **Function:** Provides direct command execution, PowerShell, `agy` CLI, and Gemini CLI access directly inside the Desktop App window.

---

## 3. Operational Directives for Antigravity Agents

1. **Self-Healing Invariant:** If a tool call ever fails due to a `PreToolUse` hook, the agent or user can immediately trigger `C:\Users\apviz\Antigravity_Emergency_Unblocker.bat`.
2. **Quarantine Invariant:** Never leave disabled plugins in `~/.gemini/config/plugins/`. Always place them in `~/.gemini/config/quarantine/`.
3. **Session Visibility Invariant:** When creating or syncing conversations for the Desktop App, always populate `workspace_uris` in `conversation_summaries.db` with both decoded (`file:///c:/...`) and encoded (`file:///c%3A/...`) paths.
4. **SOT Invariant:** Maintain all centralized SOT documentation under `C:\Users\apviz\Documents\Antigravity_Folder\Antigravity_Projects\`.
