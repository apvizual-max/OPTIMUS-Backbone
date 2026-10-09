# Sub-Skill: exec-openrouter-free-models-healer

* **Description:** Technical instructions on the self-healing startup mechanism that injects all 26 free OpenRouter models into the Hermes model selector, surviving system updates.

---

> ## ⚠️ CORRECTED 2026-10-02 — THIS MECHANISM IS THE ROOT CAUSE, NOT A FIX
>
> **This is a nested reference copy** of a procedure that is *documented here as
> a feature but is proven to be the direct cause of four separate config
> restores*. It is preserved so the mechanism stays auditable. It is NOT
> guidance, and it must not be installed, re-installed, or re-run.
>
> **What this procedure does, and why it breaks the system:**
>
> 1. It patches `hermes_cli/models.py` at boot, appending every free OpenRouter
>    model to the curated list.
> 2. It deletes `provider_models_cache.json`, forcing a refetch of that
>    expanded list.
> 3. Its companion procedure, `update-openrouter-free-models`, then ordered
>    twice that you "confirm the default model in `config.yaml` is present in
>    the free models list".
>
> **Step 3 can never succeed here.** This system runs the *direct* MiniMax
> endpoint (`model.provider: minimax`, `model.default: MiniMax-M3`). `MiniMax-M3`
> is not an OpenRouter model and can never appear in an OpenRouter free list, so
> the check fails by construction. Acting on that failure is what re-routed the
> default model through a free tier — four times.
>
> **Corroboration, on this machine:**
> - `session-2026-08-10-free-limits-plugin.md` records both
>   `stepfun/step-3.7-flash:free` and `tencent/hy3:free` as **removed — not
>   free, paid variants only**.
> - `.curator_backups\2026-07-10T03-41-01Z\cron-jobs.json` shows real cron
>   jobs silently skipped by free-model drift.
>
> **A free tier may legitimately be *catalogued* for choice. It must never be
> the configured default, and it must never be injected at boot.** Catalogue
> entries belong in `mcp_servers` metadata, not in `model.default` and not in a
> startup task that rewrites the model registry.
>
> **Authoritative current state:
> `C:\Users\apviz\.minimax\skills\HERMES_CURRENT_STATE.md`.**
> Where this file and that document disagree, that document wins.

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