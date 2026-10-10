# Ralph Loop v2 — OPTIMUS Control Center: from dashboard to instrument
Started: 2026-10-03 01:40 | Status: ✅ Done

## Goal
Keep improving http://127.0.0.1:8900/ without losing functionality. The previous
loop was mostly cosmetic. This one adds REAL capability. 20 iterations.

## Non-negotiable
Do not break what works. Verified in a real browser after every phase.

## Completed — capability first
- [x] 01 Loop v2 init; v0.4 confirmed as the rollback floor
- [x] 02 Server-side history ring buffer (`state-history.jsonl`, change-gated)
- [x] 03 TREND ENGINE: real server-side sparklines, not 40 browser samples
- [x] 04 ANOMALY DETECTION against a MEDIAN baseline, not a mean
- [x] 05 INCIDENT CORRELATION: transitions, timestamped, co-changes listed
- [x] 06 SSE live push — BUILT, MEASURED, THEN REMOVED (see below)
- [x] 07 ALERT RULES — folded into anomaly detection rather than a second engine
- [x] 08 CONTAINER DRILL-DOWN: click any row for its full record
- [x] 09 JOURNAL VIEWER: reads the audit trail the bridges already write
- [x] 10 ASK SCOPED TO TAB: carried in the digest the model receives
- [x] 11 EXPORT: state JSON, container CSV, print, AI handover briefing
- [x] 12 DESIGN: 21 inline SVG icons, hero KPI band, spacing scale, motion
- [x] 13 RESPONSIVE + reduced-motion + focus-visible
- [x] 14 ACCESSIBILITY: focus rings, keyboard reachability, contrast
- [x] 15 Verified 13/13 tabs clean in a real browser
- [x] 16 Verified 15/15 actions execute with real output
- [x] 17 Verified every NEW function against real data
- [x] 18 Verified the new journal path (after fixing a deadlock)
- [x] 19 Regression check vs v0.4
- [x] 20 Snapshot v0.5; version cap now at 5/5 and refusing the sixth

## Bugs found and fixed during the loop
1. **History dedup was broken.** The comparison included the `ts` field, which
   is regenerated every run, so EVERY sample looked like a change and the
   history filled with false transitions. Excluded `ts` from the comparison.
2. **The journal action deadlocked the server.** It called
   `http://127.0.0.1:8900/api/journal` from inside `/api/action`. The request
   loop is serial, so the action waited on the very server running it — 30s
   timeout, HTTP 500. Fixed by shelling out to `docker exec` like every other
   action. Now 0.5s.
3. **SSE never opened.** Built `/api/stream`, wrote to `Response.OutputStream`
   (curl confirmed 22 KB of real frames), but `EventSource` never fired `onopen`
   even after 55 s: HttpListener does not flush response headers early. Removed
   both the route and the client code rather than ship a live feed that silently
   never activates.
4. Anomaly list serialised as a blank object; switched to `.ToArray()`.

## What is new versus v0.4
- **Trends & Incidents tab** — the answer to "when did it break", which a
  snapshot cannot give
- **History** recorded server-side, one sample per genuine change
- **Anomaly detection** on median baselines
- **Incident correlation** with timestamps and co-changes
- **Container drill-down** — click any row
- **Bridge journal** — 15th action, reads the real audit trail

## Current Work
Complete. Version store is at 5/5 and correctly refuses the sixth until Popy
says which baseline to drop.

## Progress Log
### Phase 2 — Substrate ✓
[01:50] Ring buffer landed. Testing immediately exposed the `ts` dedup bug.
### Phase 3 — Analysis ✓
[02:05] Trends, anomalies, incidents all verified with injected history.
### Phase 4 — Integration ✓
[02:20] Journal deadlock found and fixed. SSE built, measured, removed.
### Phase 5 — Verification ✓
[02:40] 13/13 tabs, 15/15 actions, AI verified. v0.5 snapshotted.

## Stalled / Blockers
- **Version store is full at 5/5.** v0.6 will be refused until Popy names the
  baseline to drop. That is the rule he set, not a fault.
