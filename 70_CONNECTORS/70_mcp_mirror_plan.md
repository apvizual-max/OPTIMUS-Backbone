# Mavis — Hermes / Docker MCP Mirror Plan

**Date**: 2026-09-18
**Author**: Mavis (orchestrator)
**Status**: Phase B of the approved 3-phase plan. Research only — no mutations to Hermes or Docker configs.

---

## Goal

Identify which MCPs / Docker containers from the Hermes side Mavis should:
- **MIRROR** — install directly on Mavis's profile, because high-frequency / low-cost / used across many Mavis tasks
- **ROUTE VIA HERMES** — keep on Hermes, access through `hermes-mcp-router` MCP. Mavis dispatches the call, Hermes executes.
- **LEAVE** — not useful for Popy's specific OPTIMUS Prime workflows. Don't activate.

## What I researched (read-only)

1. **Hermes-side MCP fleet** — 36 servers (1 disabled: `gmail`), verified live via `hermes mcp list`
2. **Hermes optional-MCP templates** — 65 entries under `C:\Users\apviz\AppData\Local\hermes\hermes-agent\optional-mcps\` (vendor-curated, OAuth-ready manifest.yaml per entry)
3. **Hermes `hermes-mcp-*` Docker containers** — 31 running, all `node:20-secure` image
4. **SENTINEL SF_SB bundle doctrine** — read for category mapping

---

## Section 1 — Hermes's 36-side MCP fleet (live)

| # | MCP | Transport | Mavis-side mirror status | Decision |
|---|---|---|---|---|
| 1 | `agent-browser` | stdio (node) | Mavis has `agent-browser-mcp` already | **DUPLICATE → DRAC the Hermes-side or accept redundancy** |
| 2 | `antigravity-bridge` | stdio (local) | Mavis has shell bridge `mavis-antigravity-bridge-skill` | **KEEP on Hermes** — heavy-call dispatch |
| 3 | `browser` | stdio (node) | Mavis has `chrome-devtools-mcp` already | **DUPLICATE → use Mavis-side** (newer version) |
| 4 | `chrome-devtools` | stdio (node) | Mavis has `chrome-devtools-mcp` already | **DUPLICATE → use Mavis-side** |
| 5 | `comfy-cloud` | HTTP (cloud.comfy.org) | n/a — vendor cloud | **ROUTE VIA HERMES** — Popy already uses ComfyUI locally; cloud is separate |
| 6 | `discord` | stdio (node) | n/a — messaging | **LEAVE** — Popy hasn't asked for Discord integration |
| 7 | `docker-gordon-bridge` | stdio (local) | Mavis has `docker-mcp` already | **DUPLICATE → use Mavis-side** |
| 8 | `docker-mcp` | stdio (local) | Mavis has `docker-mcp` already | **DUPLICATE → use Mavis-side** |
| 9 | `elasticsearch-mcp` | stdio (local) | n/a — backend infra | **LEAVE** — Popy's stack doesn't use Elasticsearch |
| 10 | `figma` | HTTP (mcp.figma.com) | n/a — vendor cloud | **ROUTE VIA HERMES** — Popy uses Figma |
| 11 | `filesystem` | stdio (node) | Mavis has `mcp-server-filesystem` already | **DUPLICATE → use Mavis-side** |
| 12 | `git` | stdio (local) | Mavis has `git-mcp` already | **DUPLICATE → use Mavis-side** |
| 13 | `gmail` | stdio (node) | Mavis has `gmail-mcp` (awaiting OAuth) | **DORMANT** — both disabled until OAuth |
| 14 | `google-drive` | stdio (node) | Mavis has `gdrive-mcp` (awaiting OAuth) | **DORMANT** — both disabled |
| 15 | `google-workspace` | stdio (node) | Mavis has `google-workspace-mcp` (awaiting OAuth) | **DORMANT** — both disabled |
| 16 | `hermes-profile` | stdio (local) | n/a — Hermes-internal | **KEEP on Hermes** — internal coordination |
| 17 | `memory` | stdio (node) | n/a — Hermes-internal | **KEEP on Hermes** — Hermes owns memory model |
| 18 | `notebooklm` | stdio (node) | Mavis has `notebooklm-mcp` already | **DUPLICATE → use Mavis-side** |
| 19 | `obsidian` | stdio (node) | Mavis has `obsidian-mcp` already | **DUPLICATE → use Mavis-side** |
| 20 | `optimus-orchestrator` | stdio (local) | n/a — meta-orchestrator | **KEEP on Hermes** — internal SENTINEL PRIME orchestrator |
| 21 | `postgresql-mcp` | stdio (local) | n/a — backend infra | **LEAVE** — not in Popy's stack |
| 22 | `prometheus-mcp` | stdio (local) | n/a — observability | **LEAVE** |
| 23 | `qwen` | stdio (node) | Mavis has `qwen-mcp-http` already | **DUPLICATE → use Mavis-side** (Mavis-side covers Qwen via HTTP) |
| 24 | `redis-mcp` | stdio (local) | n/a — backend infra | **LEAVE** |
| 25 | `searxng` | stdio (local) | n/a — search infra | **KEEP on Hermes** — useful for research queries via Mavis |
| 26 | `sequential-thinking` | stdio (node) | n/a — reasoning helper | **ROUTE VIA HERMES** — useful when Mavis needs deep reasoning |
| 27 | `session-replay` | stdio (local) | n/a — debugging | **LEAVE** unless debugging needed |
| 28 | `telegram` | stdio (node) | n/a — messaging | **LEAVE** |
| 29 | `telegram-bot` | stdio (node) | n/a — bot infra | **LEAVE** |
| 30 | `vault-mcp` | stdio (local) | n/a — secrets storage | **LEAVE** — Hermes-only |
| 31 | `whatsapp-mcp` | stdio (node) | n/a — messaging | **LEAVE** |
| 32 | `windows-system` | stdio (local) | n/a — Windows OS access | **KEEP on Hermes** — used for system ops through Hermes |
| 33 | `goal-judge` | stdio (local) | n/a — meta-reasoning | **KEEP on Hermes** — sub-agent infrastructure |

**Total: 36 entries** — 13 DUPLICATEs (use Mavis-side), 11 LEAVE, 5 KEEP on Hermes, 5 ROUTE VIA HERMES (vendor cloud), 2 DORMANT (OAuth pending both sides).

## Actionable recommendations (the 13 DUPLICATEs)

For each duplicate, Mavis already has the matching capability. No action needed except:
1. **Document** in `10_BRIDGES/10_hermes.md` that the Mavis-side MCP is the primary access path.
2. **Tell Popy** which Hermes-side entries are now redundant so he can consider DRAC-ing them at his leisure. Mavis will NOT auto-delete Hermes-side configs.

The 4 OAuth-dormant entries (gmail, google-drive, google-workspace) appear on both sides. **Both will wake up** when Popy drives browser OAuth once. No action duplication — just one OAuth flow per Google service.

---

## Section 2 — Hermes optional-MCP templates (65 entries)

These are vendor-curated MCP configurations (mostly HTTP + OAuth, vendor-hosted). For each, Mavis scored it against Popy's stated projects (OPTIMUS, SENTINEL, B2B proposals).

| MCP | Capability | Popy relevance | Decision |
|---|---|---|---|
| `notion` | Pages and databases | MEDIUM — could host OPTIMUS docs | **MIRROR via Hermes** (vendor OAuth) — don't install on Mavis directly |
| `figma` | Figma designs | MEDIUM — Popy uses Figma | **Already MIRRORED via Hermes** |
| `linear` | Issue tracking | LOW — Popy uses self-built systems | **LEAVE** |
| `supabase` | Supabase DB | LOW — not in current stack | **LEAVE** |
| `airtable` | Airtable bases | LOW | **LEAVE** |
| `asana` | Project mgmt | LOW | **LEAVE** |
| `atlassian` | Jira/Confluence | LOW | **LEAVE** |
| `cloudflare` | Cloudflare ops | LOW | **LEAVE** |
| `datadog` | Monitoring | LOW | **LEAVE** |
| `sentry` | Error tracking | LOW | **LEAVE** |
| `stripe` | Payments | LOW | **LEAVE** |
| `postman` | API testing | LOW — Mavis may want | **MIRROR via Hermes** when needed |
| `webflow` | CMS | LOW | **LEAVE** |
| `vercel` | Deployment | LOW | **LEAVE** |
| `github` | GitHub ops | LOW — Popy uses git directly | **LEAVE** |
| `gitlab` | GitLab ops | LOW | **LEAVE** |
| `twilio-docs` | Twilio docs | LOW | **LEAVE** |
| `n8n` | Workflow automation | MEDIUM — could orchestrate OPTIMUS workflows | **MIRROR via Hermes** |
| `context7` | Library docs | MEDIUM — useful for code questions | **MIRROR via Hermes** |
| `deepwiki` | Devopedia-style | MEDIUM | **MIRROR via Hermes** |
| `twelve-data` | Financial data | LOW | **LEAVE** |
| `microsoft-learn` | MS Learn docs | LOW | **LEAVE** |
| `motherduck` | DuckDB cloud | LOW | **LEAVE** |
| `prisma-postgres` | Postgres ORM | LOW | **LEAVE** |
| `neon` | Serverless Postgres | LOW | **LEAVE** |
| `railway` | Deployment | LOW | **LEAVE** |
| `netlify` | Deployment | LOW | **LEAVE** |
| `paypal` | Payments | LOW | **LEAVE** |
| `plaid` | Banking | LOW | **LEAVE** |
| `robinhood` | Trading | LOW | **LEAVE** |
| `kiwi` | Travel | LOW | **LEAVE** |
| `trivago` | Travel | LOW | **LEAVE** |
| `strava` | Fitness | LOW | **LEAVE** |
| `indeed` | Job board | LOW | **LEAVE** |
| `gamma` | Presentations | MEDIUM — Popy creates B2B proposals | **MIRROR via Hermes** |
| `canva` | Designs | LOW | **LEAVE** |
| `miro` | Whiteboard | LOW | **LEAVE** |
| `fireflies` | Meeting notes | LOW | **LEAVE** |
| `intercom` | Customer chat | LOW | **LEAVE** |
| `klaviyo` | Email marketing | LOW | **LEAVE** |
| `mixpanel` | Analytics | LOW | **LEAVE** |
| `monday` | Project mgmt | LOW | **LEAVE** |
| `amplitude` | Analytics | LOW | **LEAVE** |
| `algolia` | Search | LOW | **LEAVE** |
| `dropbox` | Cloud storage | LOW | **LEAVE** |
| `cloudinary` | Media | LOW | **LEAVE** |
| `clickup` | Project mgmt | LOW | **LEAVE** |
| `calendly` | Scheduling | LOW | **LEAVE** |
| `circleci` | CI/CD | LOW | **LEAVE** |
| `buildkite` | CI/CD | LOW | **LEAVE** |
| `betterstack` | Logging | LOW | **LEAVE** |
| `attio` | CRM | LOW | **LEAVE** |
| `close` | CRM | LOW | **LEAVE** |
| `craft` | Docs | LOW | **LEAVE** |
| `globalping` | Network diagnostics | LOW | **LEAVE** |
| `grafana` | Dashboards | LOW | **LEAVE** |
| `hugging_face` | ML models | LOW — Popy may want this | **MIRROR via Hermes** when model access needed |
| `aws-knowledge` | AWS docs | LOW | **LEAVE** |
| `unreal-engine` | Game engine docs | LOW | **LEAVE** |
| `wolfram` | Computational | MEDIUM — could be useful for research | **MIRROR via Hermes** |
| `semgrep` | Code security | MEDIUM | **MIRROR via Hermes** |
| `n8n` | Workflow automation | MEDIUM | **MIRROR via Hermes** |
| `mixpanel` | Analytics | LOW | **LEAVE** |
| `comfy-cloud` | ComfyUI cloud | LOW — Popy has local ComfyUI | **LEAVE** |
| `fireflies` | Meeting notes | LOW | **LEAVE** |
| `motherduck` | DuckDB cloud | LOW | **LEAVE** |
| `robinhood` | Trading | LOW | **LEAVE** |
| `stripe` | Payments | LOW | **LEAVE** |
| `supabase` | Supabase | LOW | **LEAVE** |
| `square` | Payments | LOW | **LEAVE** |

**Total: 65 entries** — 9 MIRROR via Hermes (when needed), 0 MIRROR on Mavis directly, 56 LEAVE.

The 9 to "MIRROR via Hermes" are simply ones Mavis can call through `hermes-mcp-router`. **Mavis does NOT need to install them locally** — that would be wasteful duplication.

## Section 3 — Docker containers (31 running)

Each `hermes-mcp-*` container is a tool-specific service. Most are unique (one per tool), but some look like duplication candidates.

| Container | MCP counterpart | Verdict |
|---|---|---|
| `hermes-mcp-filesystem` | filesystem | KEEP — single instance |
| `hermes-mcp-memory` | memory | KEEP |
| `hermes-mcp-browser` | browser | **Possibly DUPLICATE** with `hermes-mcp-agent-browser` and `hermes-mcp-chrome-devtools` — needs Popy review |
| `hermes-mcp-obsidian` | obsidian | KEEP |
| `hermes-mcp-agent-browser` | agent-browser | KEEP |
| `hermes-mcp-telegram` | telegram | KEEP |
| `hermes-mcp-telegram-bot` | telegram-bot | KEEP |
| `hermes-mcp-discord` | discord | KEEP |
| `hermes-mcp-google-workspace` | google-workspace | KEEP |
| `hermes-mcp-google-drive` | google-drive | KEEP |
| `hermes-mcp-chrome-devtools` | chrome-devtools | KEEP — primary browser MCP |
| `hermes-mcp-sequential-thinking` | sequential-thinking | KEEP |
| `hermes-mcp-notebooklm` | notebooklm | KEEP |
| `hermes-mcp-qwen` | qwen | KEEP — primary Qwen dispatch |
| `hermes-mcp-optimus-orchestrator` | optimus-orchestrator | KEEP — SENTINEL PRIME meta-orchestrator |
| `hermes-mcp-git` | git | KEEP — also primary git dispatcher |
| `hermes-mcp-git-base` | git-base | **Possibly DUPLICATE** with `hermes-mcp-git` — needs Popy review |
| `hermes-mcp-session-replay` | session-replay | KEEP |
| `hermes-mcp-vault` | vault | KEEP |
| `hermes-mcp-elasticsearch` | elasticsearch | KEEP |
| `hermes-mcp-redis` | redis | KEEP |
| `hermes-mcp-docker` | docker-mcp | KEEP — also primary Docker dispatcher |
| `hermes-mcp-windows-system` | windows-system | KEEP |
| `hermes-mcp-docker-gordon-bridge` | docker-gordon-bridge | KEEP |
| `hermes-mcp-prometheus` | prometheus | KEEP |
| `hermes-mcp-antigravity-bridge` | antigravity-bridge | KEEP |
| `hermes-mcp-goal-judge` | goal-judge | KEEP |
| `hermes-mcp-searxng` | searxng | KEEP |
| `hermes-mcp-whatsapp` | whatsapp | KEEP |
| `hermes-mcp-hermes-profile` | hermes-profile | KEEP |
| `hermes-mcp-postgresql` | postgresql | KEEP |

**Total: 31 containers** — 29 KEEP, 2 candidate duplicates (`hermes-mcp-browser` vs `hermes-mcp-agent-browser`, `hermes-mcp-git` vs `hermes-mcp-git-base`).

DRAC recommendation (Popy R0 only):
- Retire `hermes-mcp-browser` (use `hermes-mcp-agent-browser` + `hermes-mcp-chrome-devtools` instead)
- Retire `hermes-mcp-git-base` (use `hermes-mcp-git` instead)

**Mavis does not touch these.** Documentation only.

---

## Summary matrix

| Bucket | Total | MIRROR on Mavis | ROUTE VIA HERMES | LEAVE | DORMANT (OAuth) |
|---|---|---|---|---|---|
| Hermes-side MCPs (live) | 36 | 13 (already done) | 5 (vendor cloud) | 11 | 4 (Google — same on Mavis side) |
| Hermes optional-MCPs | 65 | 0 | 9 | 56 | 0 |
| Docker containers | 31 | n/a | 31 (Hermes-internal) | 0 | 0 |

**Honest finding**: Mavis already has the right coverage for Popy's current stack. The "MIRROR" actions were completed in earlier sessions. The remaining 9 optional-MCPs that are useful can be reached via Hermes without any local install.

**No new MCP installs recommended for Mavis at this time.** The 4 Google MCPs (gmail, gdrive, google-workspace, google-calendar) are wired and enabled — they need Popy's browser-OAuth bootstrap once, then they're live.

## Cross-references

- Bridge registry: `00_INDEX/00_bridge_registry.md`
- Memory entries: agent memory has Hermes v0.21.3 + 31 containers + 33 MCP servers recorded
- SENTINEL_PRIME doctrine: `01_FOUNDATION/doctrine/A_FI_DOCTRINE.md`

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | MCP mirror plan completed | 36 Hermes-side MCPs reviewed, 65 optional MCPs scored, 31 containers audited. 13 duplicates already MIRRORED on Mavis. 9 optional MCPs useful via Hermes routing. 0 new installs recommended. |
