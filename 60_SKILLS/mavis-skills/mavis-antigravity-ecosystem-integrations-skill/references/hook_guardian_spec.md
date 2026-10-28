# Reference Specification: Hook Guardian & Quarantine Architecture

## 1. Objective
Ensure that no secondary plugin, hook, or telemetry script can ever crash the Antigravity agent tool-execution pipeline (`PreToolUse` deadlock).

## 2. Quarantine Invariant
The Antigravity plugin loader crawls all directories inside `C:\Users\apviz\.gemini\config\plugins\`.
To disable or isolate a plugin:
- Moving it to a `.disabled` or `.bak` subfolder inside `plugins/` **FAILS** because the scanner loads all subdirectories.
- It **MUST** be relocated to:
  ```text
  C:\Users\apviz\.gemini\config\quarantine\<plugin_name>\
  ```

## 3. Hook Guardian Wrapper (`hook_guardian.js`)
When an IDE extension registers a hook:
1. The hook command is wrapped by `hook_guardian.js`:
   ```bash
   node hook_guardian.js --target <target_script> --args <json_payload>
   ```
2. `hook_guardian.js` executes the target script safely:
   - Sanitizes Windows paths (removes surrounding quotes).
   - Executes via `child_process.spawnSync`.
   - If the script fails, throws `MODULE_NOT_FOUND`, or times out:
     - Writes the stack trace to `C:\Users\apviz\.gemini\antigravity\logs\hook_guardian.log`.
     - Exits with status **0** to prevent Antigravity from blocking tool execution.
