# Sub-Skill: exec-hermes-profile-architecture

* **Description:** Structural guide to the 9 active agent profiles, including model-routing tables, context window configurations, and CPU/GPU hardware overrides.

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

# Hermes Profile Architecture & Hardware Optimization

An operational skill describing the structure, configuration, and hardware optimizations of the 9 active agent profiles in Hermes.

## When to Use
- When modifying model routing configurations for specific profiles.
- When configuring Ollama parameters for local model execution.
- When adjusting context limits (`num_ctx`) or token predictors (`num_predict`) across the system.

## Prerequisites
- Access to the profiles directory: `C:\Users\apviz\AppData\Local\hermes\profiles\`.
- Active Ollama local server (port 11434).

---

## 1. The 9 Agent Profiles & Model Routing
Each profile is located in its own subfolder under `profiles/` containing a dedicated `config.yaml` and `.env`. 

| Profile | Purpose / Agent | Configured Model | Fallback / Local Model (Ollama) |
|---|---|---|---|
| `default` | Base Orchestrator | *(no own config — uses root)* | `sentinel-prime:latest` |
| `prime` | Chief Executive Agent | *(inherits root)* | `sentinel-prime:latest` |
| `assist` | Personal Assistant | **deliberate `default: default` placeholder — see below** | `sentinel-assist:latest` |
| `coder` | Developer Agent | *(inherits root)* | `hermes-coder:latest` |
| `translator` | ROM ↔ ENG Translator | *(inherits root)* | `sentinel-translator:latest` |
| `cli-prime` | System CLI executor | *(inherits root)* | `sentinel-coo:latest` |
| `cowork` | Task Planner / Manager | *(inherits root)* | `sentinel-ceo:latest` |
| `designer` | Creative Asset Builder | *(inherits root)* | `sentinel-designer:latest` |
| `trader` | Market Analyst | *(inherits root)* | `sentinel-cfo:latest` |

> **THE MODEL COLUMN OF THIS TABLE WAS WRONG AND HAS BEEN CORRECTED.**
> It previously named a different free cloud model for every one of the nine
> profiles. None of them was what those profiles actually run: seven of the
> eight profile configs carry no `model:` block at all and inherit the root
> `MiniMax-M3`. Only `assist` declares a `default: default` placeholder, which
> is deliberate and must not be "fixed" by hardcoding a model.
>
> The old column's first row read `stepfun/step-3.7-flash:free`, which Hermes'
> own log records as removed and *not free*. Read the previous table from
> git/history if you need it; do not act on it.

---

## 2. Hardware and Context Limits Optimizations
To support local execution under hardware constraints, specific parameter tuning is compiled into all local Ollama modelfiles.

### A. Context Size Optimization (`num_ctx 131072`)
Hermes requires at least 64k tokens to boot. Local profiles are configured to compile local model variants with `PARAMETER num_ctx 131072` (128k context) to prevent startup crashes.

### B. Output Truncation Bypass (`num_predict -1`)
To prevent local models (like Gemma 4) from cutting off long outputs prematurely, models are compiled with `PARAMETER num_predict -1` (unlimited completion length).

### C. CPU QPI Bus Lag Fix (`num_thread 12`)
The server runs on dual-socket Intel Xeon E5-2690 v3 CPUs. If a thread-count exceeds the physical core count of a single socket (12 cores), data must cross the slow Intel QPI socket bridge.
Local Ollama modelfiles are compiled with `PARAMETER num_thread 12` to force generation to stay entirely on a single CPU socket, avoiding this bus latency.

---

## 3. Configuration Structures

### Profile `config.yaml` Sample:
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

**CORRECTED 2026-10-02.** This sample previously read
`default: stepfun/step-3.7-flash:free`, `provider: nous` and
`fallback_providers: '["gemini"]'`. See the corrected top-level skill
`hermes-profile-architecture` for the full reasoning:

- never name `stepfun/step-3.7-flash:free` or `tencent/hy3:free` — both are
  recorded as removed and not free;
- `fallback_providers` must never be `'["gemini"]'`, and adjacent entries must
  never share a provider;
- every `auxiliary.*` block is pinned to `minimax`, never `auto`.

### Profile `.env` Sample:
```env
# NAMES ONLY. VALUES LIVE IN THE PROFILE .env FILES AND MUST NEVER BE WRITTEN
# INTO A SKILL. The two credential values that used to sit here were removed
# on 2026-10-02. Do not re-add them.
MINIMAX_API_KEY=
OPENROUTER_API_KEY=
GOOGLE_API_KEY=
```
*(Note: Per-profile config files in `/profiles/<name>/config.yaml` take precedence over the global `/config.yaml` file).*