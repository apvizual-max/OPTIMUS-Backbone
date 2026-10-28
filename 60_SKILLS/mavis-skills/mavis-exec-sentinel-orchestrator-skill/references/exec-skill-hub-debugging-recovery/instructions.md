# Sub-Skill: exec-skill-hub-debugging-recovery

* **Description:** Debug and fix Skill Hub UI glitches and create system recovery skills.

---

# Skill Hub Debugging and Recovery
Learn how to diagnose and fix Skill Hub UI synchronization issues (like the Windows backslash/forward slash mismatch) and create master system recovery skills for future resilience.

## When to Use
- When skills show as 'Not Installed' in the Hermes Desktop Skill Hub despite being installed via CLI.
- After system updates or crashes that may have corrupted skill hub state.
- As a reference for creating your own master recovery and debugging skills.
- When you need to apply targeted patches to fix specific UI/backend mismatches.

## Prerequisites
- Hermes Agent installed and running.
- Access to the hermes-agent source directory: `C:\Users\apviz\AppData\Local\hermes\hermes-agent`.
- Ability to edit files with appropriate permissions.
- Basic understanding of Python file editing and path normalization.
- Access to verification tools (optional but recommended).

## How to Run
Follow the Procedure steps to apply the fix, create recovery skills, and verify the solution.

## Quick Reference
- Check for backslash/forward slash mismatches in skill hub identifiers.
- Patch `tools/skills_hub.py`: normalize identifiers in `fetch()` and `inspect()` methods.
- Patch `hermes_cli/web_server.py`: normalize keys in `_installed_hub_identifiers()`.
- Create a master recovery skill documenting exact procedures and configurations.
- Run verification scripts to confirm fixes work.
- Restart Hermes Desktop after applying changes.

## Procedure
### Part 1: Fixing Skill Hub UI Glitch (Windows Backslash Issue)
1. **Identify the problem**: Skills appear as 'Not Installed' in UI but `hermes skills list` shows them as enabled. This indicates a path separator mismatch (backslashes vs forward slashes).

2. **Backup original files** (recommended):
   - `C:\Users\apviz\AppData\Local\hermes\hermes-agent\tools\skills_hub.py`
   - `C:\Users\apviz\AppData\Local\hermes\hermes-agent\hermes_cli\web_server.py`

3. **Apply patch to tools/skills_hub.py**:
   ub.py**:
   - In the `OptionalSkillSource.fetch()` method:
     - Replace: `rel = identifier.split("/", 1)[-1] if identifier.startswith("official/") else identifier`
     - With: 
       ```python
       normalized_ident = identifier.replace("\\", "/")
       rel = normalized_ident.split("/", 1)[-1] if normalized_ident.startswith("official/") else normalized_ident
       ```
   - In the same method, replace the identifier construction:
     - Replace: `identifier=f"official/{skill_dir.relative_to(self._optional_dir)}"`
     - With: `identifier=f"official/{skill_dir.relative_to(self._optional_dir).as_posix()}"`
   - In the `OptionalSkillSource.inspect()` method:
     - Replace: `rel = identifier.split("/", 1)[-1] if identifier.startswith("official/") else identifier`
     - With:
       ```python
       normalized_ident = identifier.replace("\\", "/")
       rel = normalized_ident.split("/", 1)[-1] if normalized_ident.startswith("official/") else normalized_ident
       ```

4. **Apply patch to hermes_cli/web_server.py**:
   - In the `_installed_hub_identifiers()` function:
     - Replace:
       ```python
       out = {}
       for entry in lock.list_installed():
           ident = entry.get("identifier")
           if ident:
               out[ident] = {
                   "name": entry.get("name"),
                   "trust_level": entry.get("trust_level"),
                   "scan_verdict": entry.get("scan_verdict"),
               }
       ```
     - With:
       ```python
       out = {}
       for entry in lock.list_installed():
           ident = entry.get("identifier")
           if ident:
               normalized_ident = ident.replace("\\", "/")
               out[normalized_ident] = {
                   "name": entry.get("name"),
                   "trust_level": entry.get("trust_level"),
                   "scan_verdict": entry.get("scan_verdict"),
               }
       ```

5. **Save both files**.

### Part 2: Creating Master System Recovery Skill
1. **Create a new skill directory** under `system-configuration` (e.g., `hermes-system-setup-and-recovery`).

2. **In the SKILL.md**, document:
   - Exact command and procedure for recovery from update crashes (e.g., missing uvicorn/fastapi packages).
   - Solution and paths for the Skill Hub separator glitch (as detailed above).
   - Full configurations for OpenRouter free models, Google AI Studio fallback, and credentials.
   - Configuration patterns for Qwen, Filesystem, Obsidian, and Sequential Thinking MCP servers.
   - Any other critical system configurations you want to preserve.

3. **Save the skill** using `skill_manage` tool.

### Part 3: Verification
1. **Run a verification script** (create one similar to Antigravity's):
   ```python
   import sys
   import os
   from pathlib import Path
   # Add hermes-agent path to sys.path
   sys.path.insert(0, r"C:\Users\apviz\AppData\Local\hermes\hermes-agent")
   os.chdir(r"C:\Users\apviz\AppData\Local\hermes\hermes-agent")
   print("--- 1. Testing _installed_hub_identifiers ---")
   try:
       from hermes_cli.web_server import _installed_hub_identifiers
       installed = _installed_hub_identifiers()
       print(f"Loaded {len(installed)} installed skills.")
       
       backslash_keys = [k for k in installed.keys() if "\\" in k]
       if backslash_keys:
           print(f"FAIL: Found keys with backslashes: {backslash_keys}")
           sys.exit(1)
       else:
           print("PASS: No keys contain backslashes. All keys normalized to forward slashes!")
           for k in list(installed.keys())[:3]:
               print(f"  - {k} -> {installed[k]}")
   except Exception as e:
       print(f"FAIL: Error importing or running _installed_hub_identifiers: {e}")\n       import traceback\n       traceback.print_exc()\n       sys.exit(1)\nprint(\"\\n--- 2. Testing OptionalSkillSource fetch/inspect ---\")\n   try:\n       from tools.skills_hub import OptionalSkillSource\n       src = OptionalSkillSource()\n       
       # Let's inspect a known skill\n       meta = src.inspect(\"official/security/1password\")\n       if meta:\n           print(f\"PASS: inspect resolved successfully: {meta.name} ({meta.identifier})\")\n       else:\n           print(\"FAIL: inspect failed to resolve official/security/1password\")\n           sys.exit(1)\n        \n       # Let's fetch it\n       bundle = src.fetch(\"official/security/1password\")\n       if bundle:\n           print(f\"PASS: fetch resolved successfully: {bundle.name}\")\n           print(f\"Bundle identifier: {bundle.identifier}\")\n           if \"\\\\\" in bundle.identifier:\n               print(\"FAIL: Bundle identifier contains backslashes!\")\n               sys.exit(1)\n           else:\n               print(\"PASS: Bundle identifier uses forward slashes!\")\n       else:\n           print(\"FAIL: fetch failed to resolve official/security/1password\")\n           sys.exit(1)\n        \n   except Exception as e:\n       print(f\"FAIL: Error running OptionalSkillSource tests: {e}\")\n       import traceback\n       traceback.print_exc()\n       sys.exit(1)\n   \nprint(\"\\nALL VERIFICATION CHECKS PASSED SUCCESSFULLY!\")\n```
   - Save as `verify_skill_hub_fix.py` in a references folder.
   - Run it from the hermes-agent directory using the virtual environment's Python.

2. **CLI Registration Check**: After applying fixes and restarting, run `hermes skills list` to confirm the new recovery skill is registered and enabled.

3. **UI Verification**: Restart Hermes Desktop completely and check the Browse Hub tab to confirm skills now show as "Installed".

## Pitfalls
- Forgetting to normalize the identifier in both `fetch` and `inspect` methods leaves the bug partially unfixed.
- Using string replacement without considering edge cases (though simple replace works for this specific issue).
- Not updating the `_installed_hub_identifiers` function will cause existing lock.json entries with backslashes to remain mismatched.
- Incorrectly editing the wrong file or method can break skill hub functionality.
- Always test with the verification script before restarting the application.
- When creating recovery skills, ensure they are stored in the correct location (`system-configuration` category) and have proper SKILL.md format.

## Verification
After applying the patches and running the verification script, you should see output confirming:
- No keys contain backslashes in `_installed_hub_identifiers()`
- `inspect()` and `fetch()` resolve successfully and use forward slashes
- ALL VERIFICATION CHECKS PASSED SUCCESSFULLY!

The skill hub UI should now correctly display installed skills as "Installed" after restarting Hermes Desktop.

## References
- The verification process follows the pattern demonstrated by Antigravity's solution.
- Having access to strategic tools like Antigravity and Qwen allows you to prompt for expert guidance when facing complex system issues—use this approach when you encounter persistent problems after 2-3 attempts at self-resolution.