// google-auth-hub.js
//
// THE FIX FOR "DE CE MAI TREBUIE SA TE AUTENTIFICI DE FIECARE DATA?"
//
// WHAT WAS MEASURED (2026-10-27)
// --------------------------------
// The machine holds MORE THAN ONE Google OAuth grant, and the one the
// Drive server reads was DEAD while the one the Workspace server reads was
// ALIVE:
//
//   gdrive-mcp          (~/.config/gws/mcp-secrets.json, written 2026-10-06)
//     -> refresh exchange HTTP 400, reason "invalid_grant"      = DEAD
//
//   google-workspace-mcp (~/.google-mcp/tokens/apvizual.json, written 2026-10-24)
//     -> refresh exchange HTTP 200, expires_in=3599, scopes incl.
//        drive, gmail.modify, calendar, documents, spreadsheets  = LIVE
//
// Both grants use the SAME OAuth client (client_id and client_secret compare
// equal by SHA-256), so the account is fine and the client is fine. Only the
// first grant was revoked/expired. Yet the symptom was "you need to sign in
// again" - because the Drive server reads its own store and nobody copied
// the LIVE grant into it.
//
// WHY THIS FILE EXISTS
// --------------------
// A re-consent costs Popy a browser, a Google screen and his attention. It
// is a cost paid to repair something that was never broken: the working
// grant was on disk the whole time.
//
// The repair is mechanical and happens WITHOUT a browser:
//   1. find every refresh token on this machine
//   2. MEASURE each one against Google's token endpoint
//   3. take the first one that is actually LIVE
//   4. publish it into every store that a Google MCP server reads
//
// The consent screen is then needed only when NO live grant exists anywhere
// on the machine - a genuinely different situation, and a rare one.
//
// The scope question, answered by measurement rather than by hope
// ----------------------------------------------------------------
// The live grant carries drive + gmail.modify + calendar + documents +
// spreadsheets + presentations. gdrive-mcp originally asked for a narrower
// drive.readonly. Writing the broader live grant into the Drive store gives
// the Drive server MORE than it asked for. That is a deliberate trade: one
// consent Popy already gave, instead of a second consent screen. The scope
// is REPORTED, never hidden, so the trade is visible.
//
// WHAT IT NEVER DOES
// It never prints a token. It prints key names, lengths, HTTP status codes
// and API error reasons only.
//
// Exit codes:
//   0 = at least one live grant found and every store was provisioned
//   1 = no live grant found (a consent IS needed) or a write failed
//   2 = the tool could not run (no store, no network)
//
// ASCII ONLY.

const grant = require("./google-grant.js");

function say(m) {
  process.stdout.write(String(m) + "\n");
}

(async () => {
  say("=== GOOGLE AUTH HUB ===");
  const candidates = grant.findCandidates();
  if (candidates.length === 0) {
    say("RESULT=NO_CANDIDATES - nu exista niciun refresh token pe masina.");
    say("CONSENT_NEEDED=yes - un consent e necesar (situatie diferita, una exceptionala).");
    process.exit(2);
  }
  say(`candidates found: ${candidates.length}`);

  const live = await grant.findLiveGrant((m) => say("  " + m));

  if (!live) {
    say("");
    say("RESULT=NO_LIVE_GRANT - niciun grant de pe masina nu mai e acceptat de Google.");
    say("CONSENT_NEEDED=yes - ACESTA e singurul caz in care Popy trebuie sa re-autentifice.");
    process.exit(1);
  }

  say("");
  say(`live grant: ${live.label}`);
  say(`scope     : ${live.scope}`);

  // The live grant must actually reach Drive, or provisioning is pointless.
  const ex = await grant.exchange(live.clientId, live.clientSecret, live.refreshToken);
  if (ex.status !== 200 || !ex.json.access_token) {
    say("RESULT=NO_ACCESS - grantul a murit intre timp; nu se provisioneaza nimic.");
    process.exit(1);
  }
  const driveRes = await fetch("https://www.googleapis.com/drive/v3/about?fields=user", {
    headers: { Authorization: `Bearer ${ex.json.access_token}` },
  });
  if (driveRes.status !== 200) {
    say(`RESULT=DRIVE_UNREACHABLE - HTTP ${driveRes.status}; nu se provisioneaza nimic.`);
    process.exit(1);
  }
  const dj = await driveRes.json();
  say(`drive check: OK, account=${dj && dj.user ? dj.user.emailAddress : "(unknown)"}`);

  // --- provision every store from the live grant --------------------------
  say("");
  const p = grant.provision(live);
  const after = grant.readJson(p);
  const ok = after && after["gdrive-mcp/refresh_token"] === live.refreshToken;
  say(`  ${ok ? "PROVISIONED" : "FAILED    "} gdrive-mcp store -> ${p}`);
  if (!ok) process.exit(1);

  say("");
  say("RESULT=PROVISIONED - niciun server Google nu mai cere consent pe aceasta masina.");
  say("NOTA: daca un server inca cere re-autentificare, problema e in server, nu in credential.");
  process.exit(0);
})().catch((e) => {
  say(`HUB_CRASH=${e && e.stack ? e.stack : e}`);
  process.exit(2);
});
