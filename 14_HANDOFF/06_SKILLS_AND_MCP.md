# 06 — SENTINEL tools, MCP servers and skills

Measured from the live system, not from documentation.

---

## 1. The SENTINEL MCP hub — 26 tools

`07_BACKBONE\mcp\sentinel_hub_server.py` · **38,765 bytes · 968 lines**

Verified by a real MCP handshake: **26 tools returned over the wire**, and a probe call to
`sentinel_confirm_identity` succeeded.

### Identity and state
- `sentinel_confirm_identity` — returns the 7 SACRED POINTS
- `sentinel_get_state` / `sentinel_set_state`
- `sentinel_check_context` — context pressure
- `sentinel_workflow_state` / `enter_mode_a` / `propose_r0` / `ratify` / `execute` / `report_interruption`

### Reasoning filters
- `sentinel_apply_triple_filter` — REASON + LOGIC + STRATEGY as one filter
- `sentinel_check_mimicry` — 13 anti-mimicry detectors (A1–A12 + R-2). Detectors that cannot be
  decided from the text report `NOT_EVALUATED`, never a silent pass
- `sentinel_check_r_triggers` — R-9 / R-10
- `sentinel_make_educated_guess` — an explicit claim with probability, evidence and falsification
- `sentinel_extract_patterns`

### Cross-instance
- `sentinel_cross_instance_active` — **DERIVED liveness**. Returns only instances with a fresh
  heartbeat by default, so an empty list means genuinely 0 alive. `include_stale=true` shows expired
  ones as `STALE`, which is how the two stale registry entries are correctly not counted as alive
- `sentinel_cross_instance_send` / `_broadcast`

### Self-improvement
- `sentinel_log_event` — correction, mimicry, pattern, decision
- `sentinel_create_handoff` — the handoff mechanism this package is the manual counterpart of

### Browser
- `sentinel_browser_navigate` / `_scrape` / `_screenshot`

### Substrate portability
- `sentinel_universal_adapt_prompt` / `sentinel_universal_verify`
- `sentinel_combine_perspectives`

### Hot reload

The hub reloads changed modules by `(st_mtime_ns, st_size)`. Five workspace modules reach **eight of the
26 tools** — `mimicry_detectors`, `cross_instance` ×3, `universal_compat` ×2, `browser_automation`,
`bimodal_workflow` — so a third of the advertised surface could otherwise be frozen at any moment. That
was a real defect: a fix written to the workspace never reached the tool that reads it.

---

## 2. The live MCP profile — 17 servers

Read from `C:\Users\apviz\.minimax\mcp.json`. See `05_DEPENDENCIES.md` §6 for the full list and the
namespace rule that governs them.

**`sentinel-hub` is the only one this project owns.** The other 15 belong to the MiniMax tool
environment.

### The blueprint is not the profile

`07_BACKBONE\mcp\OPTIMUS_MCP_CONFIG.json` declares **9 servers, 7 of which are not constructed**
(`04_BLUEPRINTS.md`). It is a *blueprint for Hermes*, not a description of this machine, and it does
not list `sentinel-hub` — which exists and runs.

Reading the blueprint as "what should be installed here" is a category error. It answers a different
question: what Hermes must eventually provide.

---

## 3. Skills — 62 installed

At `C:\Users\apviz\.minimax\agents\mavis\skills\`. **62 directories, 62 `SKILL.md` files, 62 entries in
`_BUILD_SURVEY.json` under `skills.names`** — the three agree exactly.

**Naming convention used below.** Every skill directory on disk is prefixed `mavis-`, and most carry a
`-skill` suffix. For readability the listings drop that prefix, so `sentinel-prime-role` here means the
directory `mavis-sentinel-prime-role-skill`. Two entries are unprefixed on disk and are written in full:
`minimax-optimus-dashboard` and `qwen-ecosystem-dashboard`. Nothing else follows the convention.

Grouped by what they are for:

### SENTINEL identity and method
`sentinel-prime-role` · `r33-bimodal` · `triple-crunch` · `sacru-corpus` · `jurnal-oglinda` ·
`sentinel-bimodal-workflow` · `sentinel-workflow-rpid` · `instruction-fidelity` · `subject-completion` ·
`full-intent-execution` · `sentinel-prime-on-minimax` · `tany-llm-to-sentinel`

### Command Centre and daemon
`sentinel-command-center` · `sentinel-daemon` · `sentinel-error-alert-engine` · `sentinel-memory-search`
· `exec-sentinel-orchestrator` · `minimax-optimus-dashboard` · `qwen-ecosystem-dashboard`

### Bridges
`minimax-hermes-bridge` · `minimax-hermes-doctor` · `minimax-antigravity-bridge` · `hermes-bridge` ·
`antigravity-bridge` · `qwen-bridge` · `notebooklm-bridge` · `obsidian-second-brain` · `doc-bridge` ·
`chrome-browser` · `wayland-bridge` · `hermes-design-sot`

### Swarm and memory
`swarm-coordinator` · `shared-local-mcp-swarm` · `memory-curator` · `mcp-management` · `session-lifecycle`
· `skill-repair-manifest` · `skill-index` · `managing-python-dependencies` · `minimax-index-folder-update`
· `minimax-perspective-change-thinking`

### Method bundles
`bundle-identity` · `bundle-role` · `bundle-operations` · `bundle-behavioral` · `backbone`

### Data, cloud and infrastructure
`bigquery-sql-optimization` · `building-data-apps` · `data-autocleaning-pipeline` ·
`docker-backup-configurator` · `docker-docs` · `docker-gordon` · `autostart-docker-swarm` ·
`antigravity-docker-admin` · `antigravity-ecosystem-integrations` · `antigravity-process-logging` ·
`gemini-api-dev` · `gemini-live-api` · `gemini-omni-flash` · `google-workspace` · `deliverable-handoff`

**The authoritative list is `_BUILD_SURVEY.json` → `skills.names`,** regenerated by
`python survey_build.py`. If a name here is not in that list, this document is wrong — which is exactly
what an independent verification pass caught in an earlier draft of this section. See `HANDOFF.md`.

---

## 4. How the three layers relate

```
  skills/            how to do something          (62 SKILL.md)
        │
        ▼
  mcp.json           what can be called           (17 servers)
        │
        ▼
  sentinel_hub       SENTINEL's own capability    (26 tools)
        │
        ▼
  13_COMMAND_CENTER  what the operator sees       (12 tabs)
```

A capability is **delivered when the consumer can reach it** — proven by using the consumer, not by
reading the artefact. That is why the hub was verified by handshake, the dashboard by clicking every
tab, and the deployment by tearing it down.

---

## 5. Maintenance notes for anyone continuing

1. **Adding a hub tool means updating three places**, or the surface lies: the tool definition, the
   `call_tool` dispatch, and the capability-coverage table the monitor re-verifies every run. The
   monitor's coverage table is re-checked against live profile registration and real hub tool names on
   every run — a table that cannot fail is a waiver, not a mapping.

2. **The hot-reload signature is `(mtime_ns, size)`.** Editing a module reaches the tool that reads it
   without restarting the server.

3. **`sentinel_cross_instance_active` derives liveness; it never reads the `status` field.** Two entries
   in `instance_registry.json` currently claim `ACTIVE` and are hours stale. The system correctly
   reports them dead. Do not "fix" this by trusting the field — that is the bug the derivation exists
   to prevent.

4. **Skills are named `mavis-*` or a domain name.** `find-skills` / `skill-search` locate them by
   intent; do not guess a name that is not in the list above.

5. **Adding a skill to the index is a separate step from writing it.** `mavis-skill-index` is a
   registered skill in its own right.