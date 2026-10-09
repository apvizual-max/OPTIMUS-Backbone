# Sub-Skill: exec-openrouter-free-models-healer

* **Description:** Technical instructions on the self-healing startup mechanism that injects all 26 free OpenRouter models into the Hermes model selector, surviving system updates.

---

# OpenRouter Free Models Config Healer

An operational skill detailing the background self-healing mechanism that dynamically keeps all free OpenRouter models available in the Hermes Desktop App.

## When to Use
- When new free models are added to OpenRouter and need to be refreshed.
- When an app update overwrites `models.py`, causing the free models to disappear from the selector.
- When verifying the system boot self-healer health.

## Prerequisites
- Access to the Python script: `C:\Users\apviz\AppData\Local\hermes\Hermes Local Configuration Engine\server.py`.
- Windows startup folder write access.

---

## 1. How the Healer Works
To prevent app updates from permanently reverting model definitions, a script is placed in the Windows Startup folder:
- **File**: `C:\Users\apviz\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Hermes_Model_Config_Healer.vbs`
- **Action**: Runs silently at user login using `pythonw.exe`.
- **Target Script**: `C:\Users\apviz\AppData\Local\hermes\Hermes Local Configuration Engine\server.py --silent`

Every time the computer boots, the script:
1. Opens `hermes_cli/models.py`.
2. Inspects if the free models patch block is present.
3. If missing, it inserts the code that appends all free models from OpenRouter's live API to the curated list.
4. Compiles the modified `models.py` file to check for Python syntax errors.
5. Deletes `provider_models_cache.json` under `$HERMES_HOME` to force the app to fetch the newly expanded model list.

---

## 2. Interactive Setup Dashboard
If you want to trigger the healer immediately without rebooting:
1. Run `C:\Users\apviz\AppData\Local\hermes\Hermes Local Configuration Engine\launch.bat`.
2. A local server starts on port `8998` and automatically opens Google Chrome to the config dashboard page.
3. Click the **Free Open-Routers Models Setup** button.
4. Close the server by clicking **Close Dashboard & Exit**.

---

## 3. The Code Patch logic
The self-healer locates the following target line inside `hermes_cli/models.py`:
```python
curated.append((preferred_id, desc))
```
And replaces it with:
```python
curated.append((preferred_id, desc))

    # Append all other free models from OpenRouter (without filtering)
    added_ids = {mid for mid, _ in curated}
    for mid, live_item in live_by_id.items():
        if mid in added_ids:
            continue
        if _openrouter_model_is_free(live_item.get("pricing")):
            curated.append((mid, "free"))
```

## 4. Manual Diagnostics and Triggers
You can trigger the healing process manually from PowerShell:
```powershell
cd "C:\Users\apviz\AppData\Local\hermes\Hermes Local Configuration Engine"
..\hermes-agent\venv\Scripts\python.exe server.py --silent
```
Expected console output:
`Running silent models setup/self-heal...`
`Result: {'status': 'success', 'already_done': True, 'syntax_ok': True, 'cache_cleared': True, 'free_count': 26}`