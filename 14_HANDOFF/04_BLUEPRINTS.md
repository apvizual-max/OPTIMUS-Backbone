# 04 — Blueprints

Declared designs that are **not yet built**. This is the plan, and the plan is not edited to match
what exists.

Enforced by `test_the_plan_is_never_pruned` (see `08_CONSTRUCTION_SCHEMA.md`).
Master detail: `12_PROGRAM\HERMES_GATEWAY_PROFILE_PLAN.md`.

---

## Blueprint 1 — Nine Hermes gateway profile servers

**The design, stated by the operator:**

> The idea is that nine of them — nine profiles — each has a server in the gateway of Hermes.

`07_BACKBONE\mcp\OPTIMUS_MCP_CONFIG.json` declares all nine. It is **4,565 bytes, SHA256 `86989B62…`,
mtime 2026-09-12** — unmodified through this entire stage of work.

### Per-server build target

| Declared name | Target | Current measured state | To build |
|---|---|---|---|
| `filesystem` | `@modelcontextprotocol/server-filesystem` | **resolves — 2026.8.31** | available now |
| `browser` | `@playwright/mcp` | **resolves — 0.0.83** | available now |
| `prime-bridge` | `07_BACKBONE\mcp\prime_bridge_server.py` | absent | the server |
| `sentinel-state` | `…\sentinel_state_server.py` | absent | the server |
| `rule-triggers` | `…\rule_triggers_server.py` | absent | the server |
| `learning-loop` | `…\learning_loop_server.py` | absent | the server |
| `context-pressure` | `…\context_pressure_server.py` | absent | the server |
| `web-tools` | `@modelcontextprotocol/server-fetch` | **does not resolve** | a real package, or the server written |
| `git` | `@modelcontextprotocol/server-git` | **does not resolve** | a real package, or the server written |

**7 of 9 to build.** Each is a separate registered gap (`HPROF_<name>`) so it can be built and closed
independently.

### Where each profile gets its identity

Four profile mailboxes exist at
`09_LOGS\cross_instance\mailbox\{SENTINEL-DESKTOP, SENTINEL-COWORK, SENTINEL-CHAT, CODER-APP}`.

They are **not empty** — they hold 138 / 138 / 138 / 276 historical messages, all sent by `PRIME-CLI`
between `2026-09-12` and `2026-10-06`. Mostly `type:"test"` residue from an older, pre-fix version of the
unit suite, plus one `alert` each and a `state_share`. No **new** profile traffic has been written since
`2026-10-06T15:56:28`, and repeated suite runs since then have added nothing — the suite is sandboxed.
Full detail in `02_GAPS.md` A2.

An instance becomes **alive** by writing a heartbeat under its own name. Liveness is derived from
heartbeat age — never from the `status` field a writer leaves behind, which is why two stale entries in
`instance_registry.json` claiming `ACTIVE` do not fool the system into reporting them live.

---

## Blueprint 2 — MiniMax Design integration

**What is built:** a measured description of the Design cloud seam, from the files on disk.

Measured at `%LOCALAPPDATA%\Programs\MiniMax Design\current\resources`:

| Surface | Measured |
|---|---|
| `gateway/dist/main.js` | **17,090,864 bytes** |
| `conf/external_api_conf.yaml` | **2,867 bytes** (79 lines) |
| `mcp-tools/@hilo/mcp-tools` | 0.1.0 |
| `gateway/package.json` | `@hilo/gateway-bundle` 0.1.0, 13 SQL migrations |
| Cloud categories | 6 — video, image, speech, music, media, super_resolution |
| Vendors × routed operations | 13 × 47 |
| Cloud hosts | 2 regions × 4 channels = 8 URLs |
| Reachable hosts | **2 of 4 probed** — `design.minimax.cn`, `design.minimax.io` |
| Unreachable hosts | 2, both resolving to RFC1918 — `hilo-test.xaminim.com`, `hub-pre.xaminim.com` |

**What is NOT built:** the app has **never been launched**, so no runtime surface is claimed. The
collector measures files and never launches what it measures.

**The cloud gate is measured closed, not broken.** The application carries its own verbatim warning:
`no HILO_USER_TOKEN / HILO_USER_TOKEN_FILE set; cloud-bound MCP tool calls will 401`. No token is
provisioned. Cloud-bound calls would authenticate-and-fail, and the ecosystem snapshot reports the
credential state as booleans — never as a fabricated token or an assumed success.

**To open this gate:** provision a `HILO_USER_TOKEN`, then launch the app. Deferred by the operator.

---

## Blueprint 3 — The MultiMax Control Center as a whole

The stage goal: bring this project to the level of the total build in Hermes and everything around it,
so the two sit side by side and development can proceed piece by piece.

**Achieved:** a loopback-only, dual-anchored, self-measuring control centre that runs unattended and
reports honestly on itself.

**Not yet achieved:** the Hermes integration itself — the nine gateway servers, the four configured
profiles, and the cross-profile coordination that follows from them. That is `09_ROADMAP.md`.

---

## Blueprint 4 — Documentation-only concepts

Five concepts are designed and deliberately not implemented. Each is registered with its reason, and
each reason is that documentation-only is the **correct** form for it — not an excuse.

| ID | Concept | Why it stays documentation-only |
|---|---|---|
| `CONCEPT_C18` | Partnership protocol (two blind men) | A doctrine meant to be read, not run |
| `CONCEPT_C19` | 3-Propozitii ritual | Described; wiring it to a command would make it appear runnable when it is not yet |
| `CONCEPT_C21` | Context pressure monitor | Partially implemented; not yet surfaced in the hub |
| `CONCEPT_C23` | Historical cultures corpus | It is a corpus. A corpus is not a program |
| `CONCEPT_C24` | 963 Hz / SACRU proverbs | Doctrine only — and it carries an honest correction, below |

### The honest finding inside `CONCEPT_C24`

The file is described in the project as "963 Romanian proverbs". Measured and recorded: **it is a
25-axis decision matrix, not a 963-proverb enumeration**, and its per-proverb attributions are flagged
**inside the file itself** as fabricated by an earlier agent.

The gap register carries this verbatim rather than repeating the claim. Anything built on that file
must not quote it as a corpus of 963 attributed proverbs.

---

## The governing principle

> **We do not solve a gap by removing the gap; we solve it by upgrading the system. If you want to
> build something, you play scaffolding and then raise the building. You do not take the scaffolding
> down if the building is not finished.**

Applied concretely to these blueprints:

1. A blueprint is never edited to match the disk. It is the target.
2. A profile mailbox is left standing, contents and all. It is where the work lands.
3. A declaration that 404s upstream stays declared — the *requirement* is real even when the package
   name is wrong. Fix the package when building it; do not delete the requirement.
4. Nothing is merged. Nine profiles stay nine profiles.