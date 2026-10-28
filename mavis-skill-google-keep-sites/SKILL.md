---
name: mavis-skill-google-keep-sites
description: Keep and Sites - the two Google services that stay refused, by decision and by Google's design. Load this when a workflow needs Keep notes or Sites content, when a probe reports them as REFUSED, when someone asks why they are not working, or when the plan to automate them is picked up again. Owns the measured reason for each refusal, the fact that both scope names are invalid and would invalidate the whole consent request, and the deferred automation plan under user management.
role: functional
bot: mavis-google-access-bot
---

# mavis-skill-google-keep-sites

**Role.** The two services that do not work, recorded so that nobody spends
another hour diagnosing them, and so that the decision to leave them out stays
a decision rather than an oversight.

---

## 1. The decision (Popy, 28 oct 2026)

> *„ok. putem sa ne descurcam momentan fara keep si sites. le voi importa eu
> prin gemini sau alte unelte to google drive. ok. DAR ASTEA SA FIE SINGURELE
> CARE NU MERG!"*

So: **Keep** and **Sites** are skipped for now, under user management — Popy
imports that content into Drive himself, through Gemini or other tools. The
automation for them is **deferred**, not abandoned (§5).

Every other service must work, in full, permanently.

---

## 2. Why they are refused — measured, not assumed

| Service | Measured answer | Reason |
|---|---|---|
| **Keep** | `403` | Google publishes **no grantable OAuth scope** for Keep. `keep` is not in the scope registry; the console said *"not added because they are invalid"*. |
| **Sites** | `404` | The Google Sites API was **retired**. `sites.googleapis.com` is no longer in the official directory; only `siteverification` remains, which is not the Sites API. |

### The trap that cost a day

Both scope names are **invalid**. An invalid scope invalidates the **entire**
consent request — so while they were in `FULL_SCOPES`, the other 28 (later 30,
later 32) valid scopes could not be granted either. The symptom was "Google
asks for consent again and again".

They were removed from `FULL_SCOPES`, **with the reason written into the
source** (lines 24 and 27). The tools `gkeep_list` and `gsites_list` **still
exist** in the server: they have no scope, so they report `MISSING_SCOPE` and
send the caller to `google_scope_upgrade`. **They never go silent.**

---

## 3. How they appear in the system

```
CHECK C3.services OK  OK=14 REFUSED=2[keep,sites] ERROR=0
```

The control point **expects** exactly these two refusals. A missing refusal is
also a finding (`missing_expected_refused=...`), because it would mean the
measurement no longer describes reality.

**A refusal is a measured answer, not a failure.** `REFUSED` (Google answered
with a refusal), `ERROR` (nothing answered) and `OK` are three different
things and are never collapsed.

---

## 4. What is in place for them

- The tools exist and report the reason (`MISSING_SCOPE` + the upgrade path).
- The probe classifies them as `REFUSED`, and the control point expects them.
- The Cloud runner sees the same two refusals (measured in the run that ended
  `notebooklm OK`).

---

## 5. The deferred automation plan (to be picked up later)

| Step | What it would take | Why it is deferred |
|---|---|---|
| 1. Keep, read-only | find out whether a **scope exists at all** for read-only Keep in the current Google directory; if it does, it goes through the normal consent route — one click — and the tool starts answering | until Popy says so; and the content he wants can be imported through Gemini meanwhile |
| 2. Keep, write | a project-scoped API or a Workspace-admin route (Keep is a Workspace product; personal accounts have no API surface) | the same |
| 3. Sites | nothing to automate: the API is **retired**. The content is static HTML; it can be migrated to Drive, not re-read through an API | the API is gone; only a migration remains |
| 4. The import automation Popy described | a repeatable Gemini/other-tools → Drive import, which belongs to the Drive side, not to this container | it is Popy's manual step today |

**When any of these is picked up, it goes through the normal route** — scope
verified against Google's registry first, consent once, then the tools start
answering and the control point's expectation is updated.

---

## 6. What it guarantees

- Nobody re-diagnoses Keep and Sites as a broken setup.
- Nobody re-adds the two invalid scopes and breaks the consent request again.
- The deferral is visible as a **decision**, with the reason and the plan.

---

## 7. Known limits, stated out loud

- **Keep content is not in Drive** until Popy imports it. A workflow that
  assumed otherwise would read an empty library.
- **Sites cannot be re-read by an API at all.** Any plan that needs Sites
  content must migrate it.
- **This skill describes a plan, not a built thing.** The automation does not
  exist yet, by Popy's decision.

---

## 8. Cross-references

- `mavis-skill-google-access-control-point` — `C3`, which expects these two refusals
- `mavis-google-access-bot` — the hub that owns this skill
- Docs: `Mavis-Google_Access/docs/TINERE-API-GOOGLE.md`, `docs/STARE-MASURATA.md`
