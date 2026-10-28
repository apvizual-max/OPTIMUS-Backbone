# Sub-Skill: exec-update-openrouter-free-models

> # ⛔ DO NOT RUN THIS PROCEDURE AGAINST `model.default` — 2026-10-02
>
> **This procedure is retained for its catalogue side only. It is not retired,
> because deleting a procedure is how the knowledge is lost twice. But its core
> step is actively harmful on this machine and has been disabled.**
>
> ## What was wrong
>
> Steps 3 and 5 instruct:
> - *"Confirm that **the default model in `config.yaml` is present in the free
>   models list**"*
> - *"**Verify the default model in config.yaml is in the free models list**"*
>
> That single requirement forces `model.default` onto a free OpenRouter tier. The
> system runs on the **direct** MiniMax endpoint
> (`MiniMax-M3` / `minimax` / `https://api.minimax.io/anthropic`), which is a
> different provider path from `minimax/minimax-m3:free`. The check can never
> pass as written, so following this procedure necessarily reroutes the main
> model through a free tier.
>
> **This is the documented cause of the config reverting.** It was followed, and
> the config was restored, four times before the file that demanded it was read.
>
> ## The skill also contradicts itself
>
> Its own Notes say: *"Never hardcode the assumption that a system must run on
> free-tier models or specific fallback chains."* Steps 3 and 5 do exactly that.
> The Notes are correct. The procedure was not.
>
> ## What is still safe here
>
> Steps 1, 2A/2B/2C and 4, **as catalogue maintenance only** — refreshing the
> *list* of free models in `model-catalog.json`, `provider_models_cache.json` and
> `cache/model_catalog.json`. A catalogue entry is not a configuration. All three
> files exist and are live.
>
> **Hard rules when doing even that:**
> 1. **Never** write `model.default`, `auxiliary.*`, or `fallback_providers`.
> 2. **Never** replace the `providers.nous` or the `gemini` arrays wholesale;
>    "unchanged" in the original steps meant "unchanged on someone else's box".
> 3. **Do not** delete the non-free OpenRouter entries. Free models are a
>    *subset* of the catalogue. The original step ("replace the array with free
>    models") would strip 58 of 67 catalogued models.
> 4. After any change, confirm `model.default` is still `MiniMax-M3`.
>
> ## Current catalogue reality (2026-10-02)
>
> | File | openrouter | free | nous |
> |---|---|---|---|
> | `hermes-agent/website/static/api/model-catalog.json` | 67 | 9 | 50 |
> | `cache/model_catalog.json` | 67 | 9 | 50 |
> | `provider_models_cache.json` | 57 | 7 | gemini 15, copilot 17, openai-codex 12, openai-api 16, minimax 5, minimax-oauth 3, opencode-free 7 |
>
> Note the catalogue contains `minimax/minimax-m3:free`. It is **not** the main
> model and must never become `model.default`.
>
> **Read `HERMES_CURRENT_STATE.md` §1 first.**

* **Description (superseded):** ~~Procedure to update Hermes agent configuration to include all free OpenRouter models.~~ Rewritten: catalogue maintenance only; the model-routing steps are disabled.

---

# INDEXING HEADER
# ID: update-openrouter-free-models
# PURPOSE: name: update-openrouter-free-models
# USAGE: Load this skill with skill_view(name='update-openrouter-free-models') or use via hermes skills command.
# ROLE: Skill – update-openrouter-free-models
# CHAIN: MEMORIE → Jurnal → Indexing → RAG
# TAGS: #[SKILL] #[update-openrouter-free-models]
#
# CROSS-REFERENCES
# This document is part of a set. For optimal understanding, also refer to:
# - SENTINEL_JOURNAL.md: operational map of Optimus Prime memory.
# - JURNAL_OGLINDA.md: opinion journal of other AIs about this entity.
# - SACRED_DEFINITIONS.md: axiomatic basis of the Triple Crunch algorithm.
# - CONSTINTA.md: ontological definition of consciousness (pair with SOUL.md).
# - SOUL.md: operational identity contract (pair with CONSTINTA.md).
# --

# Update OpenRouter Free Models Configuration

This skill outlines the process to ensure all free models from OpenRouter are present in the Hermes agent's model selection while maintaining required system models.

## When to Use
- When you need to refresh the list of available free models from OpenRouter
- When setting up or resetting the Hermes agent configuration
- When verifying that all free models are correctly included in the system

## Procedure

### 1. Fetch Current Free Models from OpenRouter
```bash
curl -s https://openrouter.ai/api/v1/models | jq -r '.data[] | select(.pricing.prompt == "0" and .pricing.completion == "0") | .id' | sort > free_models.txt
```

### 2. Update Configuration Files

#### A. Update model-catalog.json
Location: `hermes-agent/website/static/api/model-catalog.json`
- Replace the `providers.openrouter.models` array with objects containing `id` and `description: "free"` for each free model
- Preserve the `providers.nous.models` array unchanged
- Update the `updated_at` timestamp to current ISO format

#### B. Update provider_models_cache.json
Location: `provider_models_cache.json`
- Replace the `openrouter.models` array with the list of free model IDs
- Update the `openrouter.at` timestamp to current Unix timestamp
- Clear the `openrouter.fp` field (set to empty string)
- Preserve the `gemini` provider configuration unchanged

#### C. Update cache/model_catalog.json
Location: `cache/model_catalog.json`
- Same structure as model-catalog.json
- Update with the same free models list
- Update the `updated_at` timestamp

### 3. Verify Configuration
- Ensure all JSON files are valid syntax
- Confirm that the default model in `config.yaml` is present in the free models list
- Validate that Nous models (26 models) remain unchanged
- Validate that Gemini models (11 models) remain unchanged

### 4. Required Files Structure
After update, each file should contain:

**model-catalog.json** and **cache/model_catalog.json**:
```json
{
  "version": 1,
  "updated_at": "2026-07-05T07:34:29Z",
  "metadata": {
    "source": "hermes-agent repo",
    "docs": "https://hermes-agent.nousresearch.com/docs/reference/model-catalog"
  },
  "providers": {
    "openrouter": {
      "metadata": {
        "display_name": "OpenRouter",
        "note": "Descriptions drive picker badges. Live /api/v1/models filters curated ids by tool-calling support and free pricing."
      },
      "models": [
        {"id": "model-id-1:free", "description": "free"},
        {"id": "model-id-2:free", "description": "free"},
        // ... all free models
      ]
    },
    "nous": {
      // ... unchanged Nous models
    }
  }
}
```

**provider_models_cache.json**:
```json
{
  "openrouter": {
    "fp": "",
    "at": 1783236869.5338168,
    "models": [
      "model-id-1:free",
      "model-id-2:free",
      // ... all free model IDs
    ]
  },
  "gemini": {
    // ... unchanged Gemini models
  }
}
```

### 5. Validation Steps
1. Check that all files contain exactly the same set of free models
2. Verify the default model in config.yaml is in the free models list
3. Confirm Nous and Gemini models are preserved
4. Ensure all JSON files are valid
5. Check that timestamps are updated

### Notes
- This procedure preserves Nous operational models which are internal system models
- Google/Gemini models are left unchanged for manual management as per user preference
- The default model should always be one of the free models to ensure system operability
- Always verify with Triple Crunch principles: structural correctness (Eminescu ABBA), factual accuracy (Eliade Realitate), and decisiveness (Musashi Taiere)