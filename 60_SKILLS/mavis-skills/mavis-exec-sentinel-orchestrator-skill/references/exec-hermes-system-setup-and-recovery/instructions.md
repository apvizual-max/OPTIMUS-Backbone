# Sub-Skill: exec-hermes-system-setup-and-recovery

* **Description:** Comprehensive system configuration, OpenRouter/Gemini settings, Qwen MCP bridge setup, and recovery from Hermes app update crashes or Skill Hub UI glitches.

---

> ## ⚠️ CORRECTED 2026-10-02 — READ BEFORE USING THIS FILE
>
> **This is a nested reference copy.** Its top-level parent skill has already
> been corrected. An earlier version of this file was still carrying the
> original corruption, and because `exec-sentinel-orchestrator` is an *active*
> skill, the nested copy is the one an agent actually loads. That is why the
> defect survived the first repair pass.
>
> **Removed from this file, in full:**
>
> - `stepfun/step-3.7-flash:free` as a default model — recorded by Hermes'
>   own log as *removed, not free*;
> - `provider: nous` with the NousResearch base URL as a default;
> - `fallback_providers: '["gemini"]'`;
> - **two live plaintext credentials.** Values are never written into a
>   skill; only the variable *names* belong here.
> - the "Confirmed Free OpenRouter Models" list, which is the direct cause of
>   the four config restores (see `findings.md`, root-cause section).
>
> **The authoritative statement of current state is
> `C:\Users\apviz\.minimax\skills\HERMES_CURRENT_STATE.md`.**
> Where this file and that document disagree, that document wins.
>
> **Do not restore any value named above.** If you believe one of them is
> correct, re-verify against the live system first — that check is what this
> file failed to do.

---

# Hermes System Setup and Recovery

A comprehensive operational guide and skill set for managing, configuring, and recovering the Hermes Desktop application environment on Windows.

## When to Use
- **Hermes App crashes after an update** (e.g., missing FastAPI/Uvicorn, backend exiting before ready).
- **Skill Hub (Browse Hub) displays incorrect installation statuses** (installed skills marked as 'Not Installed').
- **Setting up or restoring API credentials** for OpenRouter, Nous Research, and Google AI Studio.
- **Configuring the Qwen MCP Bridge System** and other MCP tools (Filesystem, Obsidian).
- **Verifying or repairing profile-specific settings** for persistent system administration.

## Prerequisites
- Hermes Desktop App installed in `C:\Users\apviz\AppData\Local\hermes`.
- Python virtual environment active at `C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv`.
- Node.js and npm/npx installed.

---

## 1. Crash Recovery after Application Update
If the Hermes backend exits with code `1` (usually due to missing web server packages like `fastapi` and `uvicorn` after an update):

### Repair Procedure:
1. Open PowerShell or Command Prompt.
2. Navigate to the `hermes-agent` root:
   ```cmd
   cd C:\Users\apviz\AppData\Local\hermes\hermes-agent
   ```
3. Re-install all dependencies into the local interpreter in editable mode:
   ```cmd
   .\venv\Scripts\python.exe -m pip install -e ".[all]"
   ```
4. Check if the backend dependencies are correct:
   ```cmd
   .\venv\Scripts\python.exe hermes_bootstrap.py --check-deps
   ```
5. Confirm it runs without module errors:
   ```cmd
   .\venv\Scripts\hermes.exe --version
   ```

---

## 2. Skill Hub UI Glitch Repair
If installed skills show up as "Not Installed" in the Browse Hub UI despite being active in the CLI:

### Root Cause:
Path separator mismatches between Windows-style backslashes (`\`) in local paths and POSIX-style forward slashes (`/`) used by the search index.

### Solution:
Verify that the following backend files are patched:
1. **`C:\Users\apviz\AppData\Local\hermes\hermes-agent\tools\skills_hub.py`**
   - Inside `OptionalSkillSource.fetch()`, ensure the `identifier` is converted to POSIX format:
     ```python
     identifier=f"official/{skill_dir.relative_to(self._optional_dir).as_posix()}"
     ```
   - In both `fetch()` and `inspect()`, normalize incoming `identifier` inputs:
     ```python
     normalized_ident = identifier.replace("\\", "/")
     ```
2. **`C:\Users\apviz\AppData\Local\hermes\hermes-agent\hermes_cli\web_server.py`**
   - Inside `_installed_hub_identifiers()`, normalize returning keys:
     ```python
     normalized_ident = ident.replace("\\", "/")
     ```

---

## 3. OpenRouter & Gemini AI Studio Settings
**This section no longer describes how to route to free models.** It
now records what was removed and why. Sub-section C explains the
consequence: the procedure that used to live here is what re-routed
the default model through a free tier on four separate occasions.
Do not restore that configuration.

### A. Environment Configuration (`.env`)
Located at `C:\Users\apviz\AppData\Local\hermes\.env`:
```env
# NAMES ONLY. VALUES LIVE IN THE .env FILES AND MUST NEVER BE WRITTEN INTO A SKILL.
# The two credential values that used to sit here were removed on 2026-10-02.
# Do not re-add them. Read the real value from .env when a live call is needed.
MINIMAX_API_KEY=
OPENROUTER_API_KEY=
GOOGLE_API_KEY=
```

### B. Configuration (`config.yaml`)
Located globally at `C:\Users\apviz\AppData\Local\hermes\config.yaml` or per-profile:
```yaml
model:
  default: MiniMax-M3
  provider: minimax
  base_url: https://api.minimax.io/anthropic
  context_length: 131072
  reasoning_effort: high
providers:
  ollama:
    api_key: ollama
    base_url: http://localhost:11434/v1
```

**CORRECTED 2026-10-02.** This block previously read
`default: stepfun/step-3.7-flash:free`, `provider: nous`,
`base_url: https://inference-api.nousresearch.com/v1`.

- `stepfun/step-3.7-flash:free` — Hermes' own log
  (`session-2026-08-10-free-limits-plugin.md`) records it **removed: not free,
  paid variants only**. Naming it as the default is wrong twice over.
- `tencent/hy3:free` — same log, same removal.
- `provider: nous` is a local-inference provider. It is not the configured
  default and setting it here reroutes every request away from the account.

**`fallback_providers: '["gemini"]'` is forbidden.** Gemini is not an
inference provider for this system. The real chain is an interleaved list
anchored on `minimax` / `MiniMax-M3`, and adjacent entries must never share a
provider.

### C. "Confirmed Free OpenRouter Models" — WITHDRAWN 2026-10-02

**This list is not a catalogue. It is a trap, and it has been removed as
guidance.**

The `update-openrouter-free-models` procedure ordered twice that you "confirm
the default model in `config.yaml` is present in the free models list". This
system runs the *direct* MiniMax endpoint, so `MiniMax-M3` can never appear in
an OpenRouter free list, so that check can never pass. Following it
necessarily reroutes the default model through a free tier. That procedure is
the documented cause of the four config restores.

- Do not treat a model as free because a stale list named it. Free tiers
  change without notice; the authoritative record is the live catalogue, not
  a document.
- If a free model must be *catalogued* rather than routed to, it lives in
  `mcp_servers` metadata only — never in `model.default`.

---

## 4. Qwen MCP Bridge & System MCPs
Set up model context protocol (MCP) servers to enable filesystem access, memory management, and external tools.

### Configuration Format (Inside `config.yaml`):
```yaml
mcp_servers:
  filesystem:
    command: mcp-server-filesystem.cmd
    args:
      - "C:/"
      - "E:/"
      - "D:/Alex - KV Obsidian"
      - "D:/Google Local Files - Personal Folder"
  obsidian:
    command: npx
    args:
      - -y
      - "@huangyihe/obsidian-mcp"
      - "--vault-path"
      - "D:\Alex - KV Obsidian\Alex - KV Obsidian"
  qwen:
    command: npx
    args:
      - -y
      - "@gy920/qwen-mcp-tool"
  sequential-thinking:
    command: npx
    args:
      - -y
      - "@modelcontextprotocol/server-sequential-thinking"
```

---

## Verification Checklist
- Run `hermes skills list` to confirm skills are active on CLI.
- Open Desktop Browse Hub to verify installed state badges match CLI list.
- Run `hermes mcp list` and `hermes mcp test qwen` to check MCP bridges.