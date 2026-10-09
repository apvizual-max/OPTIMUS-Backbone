# Sub-Skill: exec-skill-hub-windows-backslash-fix

* **Description:** Fix Windows backslash in skill hub UI.

---

# Skill Hub Windows Backslash Fix
Fix the UI glitch where installed skills appear as 'Not Installed' due to Windows backslashes in skill identifiers.

## When to Use
- After noticing skills show as 'Not Installed' in the Hermes Desktop Skill Hub despite being installed via CLI.
- When `hermes skills list` shows skills as enabled but the UI does not reflect this.
- Before redeploying or updating the Hermes agent to prevent recurrence.

## Prerequisites
- Hermes Agent installed and running.
- Access to the hermes-agent source directory: `C:\Users\apviz\AppData\Local\hermes\hermes-agent`.
- Ability to edit files with appropriate permissions.
- Python 3.x available (for running verification script).

## How to Run
Follow the Procedure steps to apply the patches, then run the verification script to confirm the fix.

## Quick Reference
- Edit `skills_hub.py`: normalize identifiers to forward slashes in `fetch` and `inspect`.
- Edit `web_server.py`: normalize keys in `_installed_hub_identifiers` to forward slashes.
- Run verification script provided in references/ to test the fix.
- Restart Hermes Desktop after changes.

## Procedure
1. **Backup the original files** (optional but recommended):
   - Copy `C:\Users\apviz\AppData\Local\hermes\hermes-agent\tools\skills_hub.py` to a backup location.
   - Copy `C:\Users\apviz\AppData\Local\hermes\hermes-agent\hermes_cli\web_server.py` to a backup location.

2. **Apply patch to skills_hub.py**:
   - Open the file and locate the `fetch` method in the `OptionalSkillSource` class.
   - Replace the block:
     ```python
     rel = identifier.split("/", 1)[-1] if identifier.startswith("official/") else identifier
     ```
     with:
     ```python
     normalized_ident = identifier.replace("\\", "/")
     rel = normalized_ident.split("/", 1)[-1] if normalized_ident.startswith("official/") else normalized_ident
     ```
   - Locate the line constructing the identifier for the returned `SkillBundle`:
     ```python
     identifier=f"official/{skill_dir.relative_to(self._optional_dir)}"
     ```
     replace with:
     ```python
     identifier=f"official/{skill_dir.relative_to(self._optional_dir).as_posix()}"
     ```
   - Locate the `inspect` method and apply the same normalization to the identifier parameter:
     ```python
     rel = identifier.split("/", 1)[-1] if identifier.startswith("official/") else identifier
     ```
     replace with:
     ```python
     normalized_ident = identifier.replace("\\", "/")
     rel = normalized_ident.split("/", 1)[-1] if normalized_ident.startswith("official/") else normalized_ident
     ```

3. **Apply patch to web_server.py**:
   - Open the file and locate the `_installed_hub_identifiers` function.
   - Replace the block:
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
     with:
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

4. **Save both files**.

5. **Run the verification script** (provided in references/verify_skill_hub_fix.py) to ensure the fix works:
   ```powershell
   cd C:\Users\apviz\AppData\Local\hermes\hermes-agent
   .\venv\Scripts\python.exe references\verify_skill_hub_fix.py
   ```
   The script should output "PASS" messages and exit with code 0.

6. **Restart Hermes Desktop** completely (quit from system tray, then relaunch) to load the updated code.

7. **Verify in UI**: Open the Hermes Desktop app, go to Browse Hub, and confirm that previously missing skills now show as "Installed".

## Pitfalls
- Forgetting to normalize the identifier in both `fetch` and `inspect` methods will leave the bug partially unfixed.
- Using `.as_posix()` ensures the identifier uses forward slashes regardless of OS; omitting it may still produce backslashes on Windows.
- Not updating the `_installed_hub_identifiers` function will cause existing lock.json entries with backslashes to remain mismatched.
- Incorrectly editing the wrong file (e.g., modifying the wrong class or method) can break skill hub functionality.
- Always test with the verification script before restarting the application.

## Verification
After applying the patches and running the verification script, you should see output similar to:
```
--- 1. Testing _installed_hub_identifiers ---
PASS: No keys contain backslashes. All keys normalized to forward slashes!
--- 2. Testing OptionalSkillSource fetch/inspect ---
PASS: inspect resolved successfully: 1password (official/security/1password)
PASS: fetch resolved successfully: 1password
PASS: Bundle identifier uses forward slashes!
ALL VERIFICATION CHECKS PASSED SUCCESSFULLY!
```
If any step fails, re‑check the applied changes and ensure they match the diffs exactly.

## References
- The verification script is available at `references/verify_skill_hub_fix.py` (see attached).