# MCP DECISION BRIEF — the last FAIL, with the evidence attached

**For:** Popy · **Date:** 2026-10-05 · **Status:** awaiting your decision
**Checks:** `mcp_config_servers_exist` and `mcp_npx_packages_resolve` — the two reds in a 55-check monitor

> Corrected 2026-10-05: this line first read "the single remaining red in a 54-check
> monitor". Both figures were stale, and "single" was wrong from the moment the second
> check was added — the body of this brief described both reds while the header claimed
> one. Measured: 55 checks, 52 OK, 2 FAIL, 1 STALE.

---

## 1. The question, stated properly

`OPTIMUS_MCP_CONFIG.json` declares **9** servers. Four are `npx` packages. Five point at `.py`
files **that do not exist on disk**. The check is therefore not asking a question of taste — it is
reporting that a config advertises programs which cannot start.

**Correction, found while preparing this brief: the config carries 7 dead entries, not 5.** The
monitor only counted the five `.py` files, because it skipped every `npx` entry on a comment that
read *"npm package, resolved by npx at launch"*. That comment was the entire claim, it was never
checked, and it is false. Resolving each package against the npm registry:

| declared `npx` package | resolves? |
|---|---|
| `@modelcontextprotocol/server-filesystem` | **yes** — 2026.8.31 |
| `@playwright/mcp` | **yes** — 0.0.83 |
| `@modelcontextprotocol/server-fetch` | **NO — 404 Not Found** |
| `@modelcontextprotocol/server-git` | **NO — 404 Not Found** |

Not a flaky registry: a control package (`react`) resolved to 19.3.0 in the same run, and both
failures are hard `E404`s from `registry.npmjs.org`. `npx -y @modelcontextprotocol/server-fetch`
fails exactly the way the missing `.py` files do.

The monitor has been fixed to check these too (`mcp_npx_packages_resolve`), so this can no longer
happen silently.

## 2. What actually exists

Under `07_BACKBONE\mcp\` there is exactly one server:

```
sentinel_hub_server.py      33,469 B
OPTIMUS_MCP_CONFIG.json      4,565 B
```

It was verified by a **real MCP stdio handshake**, not by reading its source:

```
protocol version   : 2024-11-05
server name        : sentinel-hub
declared in source : 26
returned by wire   : 26
probe              : sentinel_confirm_identity -> ok, arguments arrived
record             : 09_LOGS\mcp_handshake.json
```

## 3. The mapping — what each absent server would have provided

Each of the five declares a concern. The hub's 26 tools were matched against those concerns from
the tool names **the wire returned**, not from a grep of the source.

| Declared server | Its stated concern | Already served by the hub? |
|---|---|---|
| `sentinel-state` | state, search, anti-mimicry | **COVERED** — `sentinel_get_state`, `sentinel_set_state`, `sentinel_check_mimicry`, `sentinel_extract_patterns`, `sentinel_workflow_state` |
| `rule-triggers` | R-2, R-9, R-10 trigger monitoring | **COVERED** — `sentinel_check_r_triggers` |
| `learning-loop` | auto-learning, feedback, metrics | **COVERED** — `sentinel_extract_patterns`, `sentinel_make_educated_guess`, `sentinel_universal_adapt_prompt` |
| `context-pressure` | context pressure, auto-compact | **COVERED** — `sentinel_check_context` |
| `prime-bridge` | filesystem + workspace bridge | **NOT COVERED — no filesystem tool exists in the hub** |

**Four of the five are stale duplicates of tools that already work over the wire.**

## 4. Why implementing them would be the wrong fix

The `sentinel-state`, `rule-triggers`, `learning-loop` and `context-pressure` servers would each
re-implement a concern a working tool already serves. Writing them produces **two sources of truth
for the same question** — and two will eventually disagree, silently.

That is the same reason `mavis-sentinel-bimodal-workflow-skill` was installed as a *child* of the
existing `mavis-r33-bimodal-skill` rather than beside it. **Two sources of truth become a silent
contradiction.** Four fresh ones would be a worse version of the same mistake.

## 5. The one that is genuinely missing — and its catch

`prime-bridge` is the only entry representing a capability nothing currently provides. The hub has
browser tools (`sentinel_browser_navigate`, `_scrape`, `_screenshot`) but **zero filesystem tools**;
the string "filesystem" does not appear in the server at all.

**But the config already declares a second, separate filesystem provider:**

```json
"filesystem": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem"],
  "env": { "ALLOWED_DIRECTORIES": "...\\SENTINEL_PRIME" }
}
```

So the config contains **two entries for one concern** — a local `.py` that does not exist, and an
`npx` package. That is very likely the same stale-claim shape as the other four, just pointing at a
different provider.

**This one is now verified:** `@modelcontextprotocol/server-filesystem` resolves at **2026.8.31**.
Filesystem access therefore already has a working provider, which makes `prime_bridge_server.py`
a duplicate claim rather than a missing capability. That removes the last argument for implementing
it.

## 5A. The other two 404s

- **`@modelcontextprotocol/server-fetch`** — does not exist. The fetch capability it declared for
  "R-2 verification" has no working provider in this config. Whether you want one is a capability
  question, not a repair.
- **`@modelcontextprotocol/server-git`** — does not exist. The nearest package,
  `mcp-server-git`, resolves to `0.0.1-security`, which is a placeholder, not a working server.
  The real git MCP server is distributed differently. So **git access for `/checkpoint` currently
  has no provider in this config either.**

Both of these are capability gaps, and both are yours to fill or accept.

## 6. The options, with consequences

Seven of nine entries are dead: 5 missing `.py` and 2 unresolvable packages.

| | What I would do | Result | Cost |
|---|---|---|---|
| **A — prune all seven** | Delete the 5 dead `.py` and the 2 dead `npx` entries. Filesystem stays on its working `npx` provider. | monitor **fully green**; config stops lying | you lose the *claimed* fetch and git capabilities — they were claims, not functions |
| **B — prune seven, add real providers** | As A, then add working fetch and git servers if you want those capabilities | green **and** honest capability coverage | needs a decision on which servers actually serve fetch and git |
| **C — implement the five `.py`** | Write all five local servers | green on the old check, still red on `mcp_npx_packages_resolve` | **creates four duplicate sources of truth.** Not recommended |

**My recommendation: A, then B if you want the capabilities.** Every one of the seven dead entries
is a promise with nothing behind it; four of them duplicate tools that already answer over the wire,
and three duplicate or replace providers that either work or are honestly missing. Pruning removes
false promises without removing a single working capability — and the check is already there to
confirm the result.

## 7. What I have not done, deliberately

I have not edited `OPTIMUS_MCP_CONFIG.json`. Pruning removes a declared capability and adding
provides one — both are decisions about what SENTINEL should be, and both are yours. The checks stay
**red and visible** in the meantime, which is the correct terminal state: a declared server that
cannot start should be loudly declared-unstartable, not quietly forgotten.

One word from you — "A" or "B" — and this becomes a single pass.
