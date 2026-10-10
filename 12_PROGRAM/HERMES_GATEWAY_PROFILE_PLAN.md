# Hermes Gateway Profile Plan

**Status:** scaffolding. Recorded 2026-10-06 at the operator's instruction. Nothing here is a defect.
**Owner:** Popy. **Not an optimisation target.**

---

## The design

The Hermes gateway is to carry **one server per Hermes profile** — nine profiles, nine servers.
`07_BACKBONE\mcp\OPTIMUS_MCP_CONFIG.json` already declares all nine. Each declared server is
infrastructure that has to be created in Hermes.

Four of the nine are npm-backed (`web-tools`, `filesystem`, `browser`, `git`); five are Python
(`prime-bridge`, `sentinel-state`, `rule-triggers`, `learning-loop`, `context-pressure`). As of this
note, **1 of 9 is constructed** and **8 of 9 are not**. That ratio is the work, not a fault report.

The four Hermes profile mailboxes already exist as scaffolding under
`09_LOGS\cross_instance\mailbox\`: `SENTINEL-DESKTOP`, `SENTINEL-COWORK`, `SENTINEL-CHAT`, `CODER-APP`.

This concerns Hermes, not MiniMax. SENTINEL manages and holds relations with all of it.

---

## The principle, in the operator's words

> These are blueprints for what we need to construct. The point here is you do not delete the plan
> to fit your work and say your work is according to needs or expectations or the plan. In this
> case, these are the plan.
>
> Gaps — these are called gaps. We do not solve them by removing the gap; we solve them by
> upgrading the system. This is the principle of building. If you want to build something, you play
> scaffolding and then raise the building. **You do not take the scaffolding down if the building is
> not finished.**

Operationally:

1. **A declared-but-unbuilt server is a gap, not an error.** It is tracked in
   `12_PROGRAM\GAP_REGISTER.json` as `HPROF_<name>` with status `OPEN`.
2. **The blueprint is never pruned to match what exists.** Writing the config down so it agrees
   with today is the failure mode, not the fix.
3. **Empty profile mailboxes are scaffolding and stay.** Removing them because they are empty
   removes the place the work will land.
4. **A gap closes by construction, never by deletion.** The nine entries disappear when the servers
   exist — not before.
5. **Nothing is merged.** A separate profile is a separate profile.

---

## What was almost done wrong

On 2026-10-06 the monitor reported `mcp_config_servers_exist` as FAIL and I recommended rewriting the
blueprint to match reality, and separately recommended declaring single-instance operation and
removing the empty profile directories. **Both recommendations were wrong in the same way:** they
resolved a measurement by deleting the thing the measurement was about. The check was accurate; the
proposed response was not.

The check itself remains FAIL on purpose. It is a true reading of "8 of 9 declared servers do not
exist on disk", and it is the correct signal for work outstanding. Its evidence already states that
rewriting or pruning the config is an operator decision.

---

## To close a gap

Construct the server in the Hermes gateway, point the blueprint entry at the file that now exists,
then set that `HPROF_` entry's status to `CLOSED-BUILT`. Do not delete the entry and do not delete the
declaration.

## To be addressed later

The full multi-profile swarm, and the Design cloud gate (`HILO_USER_TOKEN` still unprovisioned).
Noted for a later session, not scheduled here.
