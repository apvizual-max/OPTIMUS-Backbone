#!/usr/bin/env node
/**
 * GOOGLE PREFLIGHT — un singur verdict, inainte de orice alta operatiune.
 *
 *   node mavis-tools/google-preflight.js
 *
 * De ce exista: pe 2026-10-22 am pierdut timp diagnosticand de ce Google
 * "nu merge". Cauza: secretul manager avea client_id-ul de la ALT client
 * (cel pentru Hermes CLI). Token endpointul accepta perechea (invalid_grant),
 * dar authorize endpointul dadea "Error 401: invalid_client" in browser.
 *
 * Acest script verifica TOATE cele 4 lucruri care conteaza, in ordine:
 *   1. credentialele exista
 *   2. clientul e recunoscut de TOKEN endpoint  (client_id + secret)
 *   3. clientul rezolva la AUTHORIZE endpoint   (linkul de browser merge)
 *   4. refresh_token-ul e viu                    (exchange cu token real)
 *
 * Daca 1-3 sunt OK dar 4 pica, inseamna ca trebuie un consimtamant nou.
 * Daca 2 sau 3 pica, inseamna ca secretul manager are clientul gresit.
 *
 * READ-ONLY. Nu scrie, nu trimite, nu modifica nimic.
 */
const CID = process.env.GOOGLE_CLIENT_ID_MAVIS_CLOUD || process.env.GOOGLE_CLIENT_ID;
const CSEC = process.env.GOOGLE_CLIENT_SECRET_MAVIS_CLOUD || process.env.GOOGLE_CLIENT_SECRET;
const RT = process.env.GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD || process.env.GOOGLE_REFRESH_TOKEN;
const REDIRECT = process.env.GOOGLE_REDIRECT_URI || 'http://127.0.0.1:8976';
const fs = require('fs');
const path = require('path');
const REPO_CLIENT_JSON = path.join(__dirname, 'google-client.json');
// Sursa unica de adevar: mavis-tools/google-scopes.js
// (a existat o lista hardcodata aici — exact anti-pattern-ul care a degradat
//  tokenul pe 28 oct 2026. Flag-at de evalul skill-ului central.)
const SCOPES = require('./google-scopes.js').ALL;

const G = s => `\x1b[32m${s}\x1b[0m`, R = s => `\x1b[31m${s}\x1b[0m`;
const Y = s => `\x1b[33m${s}\x1b[0m`, D = s => `\x1b[2m${s}\x1b[0m`, B = s => `\x1b[1m${s}\x1b[0m`;

/** fetch cu retry — reteaua din cloud pica ~1 din 5 cereri. */
async function fr(url, opts = {}, tries = 5) {
  let last = null;
  for (let i = 0; i < tries; i++) {
    if (i) await new Promise(r => setTimeout(r, 1200 * i));
    try { return await fetch(url, { ...opts, signal: AbortSignal.timeout(20000) }); }
    catch (e) { last = e; }
  }
  throw last;
}

(async () => {
  console.log(B('\n=== GOOGLE PREFLIGHT ===\n'));

  // 0. drift: secret manager vs repo (google-client.json)
  let drift = null;
  try {
    const cfg = JSON.parse(fs.readFileSync(REPO_CLIENT_JSON, 'utf8'));
    if (cfg.client_id && CID && cfg.client_id !== CID) drift = { env: CID, repo: cfg.client_id };
  } catch { /* fisierul nu exista — ok */ }
  if (drift) {
    console.log(R('  [0] drift client_id  secret manager != google-client.json'));
    console.log(D(`      env  : ${drift.env}`));
    console.log(D(`      repo : ${drift.repo}`));
    console.log(Y('      Unul din ele e clientul vechi. Verifica in Cloud Console -> Clients.'));
  } else {
    console.log(G('  [0] drift client_id  OK') + D('  (env si repo coincid)'));
  }

  // 1. credentiale
  const miss = [];
  if (!CID) miss.push('GOOGLE_CLIENT_ID');
  if (!CSEC) miss.push('GOOGLE_CLIENT_SECRET');
  if (!RT) miss.push('GOOGLE_REFRESH_TOKEN');
  const noToken = !RT;
  if (miss.filter(m => m !== 'GOOGLE_REFRESH_TOKEN').length) {
    console.log(R(`  [1] credentiale      LIPSA: ${miss.join(', ')}`));
    console.log(Y(`      Pune-le in secret manager (Mavis Cloud -> Environmental Information -> Secrets).`));
    process.exit(1);
  }
  if (noToken) console.log(Y('  [1] credentiale      TOKEN LIPSA (ok daca n-ai consimtamit inca)'));
  else console.log(G('  [1] credentiale      OK') + D(`  (${CID.split('-')[0]}…${CID.split('-')[1].slice(-6)})`));

  // 2. token endpoint: clientul + secretul sunt recunoscute?
  //    invalid_grant  = client gasit, secret bun    -> OK
  //    invalid_client = client sau secret gresit    -> FAIL
  let ok2 = false, e2 = '', net2 = false;
  try {
    const r = await fr('https://oauth2.googleapis.com/token', {
      method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ client_id: CID, client_secret: CSEC, grant_type: 'authorization_code', code: 'PREFLIGHT_FAKE', redirect_uri: REDIRECT }),
    }, 8);
    const j = await r.json().catch(() => ({}));
    ok2 = j.error === 'invalid_grant';
    e2 = `${j.error}${j.error_description ? ' — ' + j.error_description : ''}`;
  } catch (e) { net2 = true; e2 = 'RETEA: ' + (e.cause?.code || e.message); }
  if (net2) {
    console.log(Y(`  [2] client la token   INDETERMINAT (retea)  ${e2}`));
    console.log(Y('      Nu pot afirma nimic despre client. Mai incearca mai tarziu.'));
    console.log(Y('      Daca persista, testeaza cu: curl -s -o /dev/null -w "%{http_code}" https://oauth2.googleapis.com/token\n'));
    process.exit(3);
  }
  console.log(ok2 ? G('  [2] client la token   OK') : R(`  [2] client la token   FAIL  ${e2}`));
  if (!ok2) {
    console.log(Y('      -> client_id sau client_secret din secret manager nu se potrivesc.'));
    console.log(Y('      -> verifica in Cloud Console -> Google Auth Platform -> Clients.'));
    process.exit(1);
  }

  // 3. authorize endpoint: linkul de browser va functiona?
  //    Clientul rezolvat -> redirect cu opparams + dsh. Nu rezolvat -> fara ele.
  let ok3 = false, e3 = '', net3 = false;
  try {
    const p = new URLSearchParams({
      client_id: CID, redirect_uri: REDIRECT, response_type: 'code',
      scope: SCOPES.join(' '), access_type: 'offline', prompt: 'consent',
    });
    const r = await fr('https://accounts.google.com/o/oauth2/v2/auth?' + p, {
      redirect: 'manual', headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120' },
    }, 8);
    const loc = r.headers.get('location') || '';
    ok3 = loc.includes('opparams=') && loc.includes('dsh=');
    e3 = ok3 ? '' : 'clientul NU rezolva la authorize endpoint';
  } catch (e) { net3 = true; e3 = 'RETEA: ' + (e.cause?.code || e.message); }
  if (net3) {
    console.log(Y(`  [3] client la auth    INDETERMINAT (retea)  ${e3}`));
    console.log(Y('      Nu pot afirma nimic despre client. Mai incearca mai tarziu.\n'));
    process.exit(3);
  }
  console.log(ok3 ? G('  [3] client la auth    OK') : R(`  [3] client la auth    FAIL  ${e3}`));
  if (!ok3) {
    console.log(Y('      -> linkul de autorizare va da "Error 401: invalid_client" in browser.'));
    console.log(Y('      -> clientul din secret manager nu e cel potrivit. Verifica Clients in Cloud Console.'));
    process.exit(1);
  }

  // 4. refresh token viu?
  if (noToken) {
    console.log(Y('  [4] refresh token    LIPSA — nu se poate verifica'));
    console.log(Y('\n  VERDICT: clientul e CORECT. Trebuie doar un consimtamant nou.'));
    console.log(Y('  -> node mavis-tools/google-link.js   (da linkul, deschide in browser)'));
    console.log(Y('  -> node mavis-tools/google-connect.js "<url>"   (schimba codul in token)\n'));
    process.exit(2);
  }
  let ok4 = false, e4 = '';
  let expiresIn, grantedScopes = [];
  try {
    const r = await fr('https://oauth2.googleapis.com/token', {
      method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ client_id: CID, client_secret: CSEC, refresh_token: RT, grant_type: 'refresh_token' }),
    });
    const j = await r.json().catch(() => ({}));
    ok4 = !!j.access_token;
    expiresIn = j.refresh_token_expires_in;
    grantedScopes = (j.scope || '').split(/\s+/).filter(Boolean);
    e4 = j.error ? `${j.error} — ${j.error_description || ''}` : '';
  } catch (e) { e4 = 'RETEA: ' + (e.cause?.code || e.message); }
  console.log(ok4 ? G('  [4] refresh token    OK') : R(`  [4] refresh token    FAIL  ${e4}`));
  if (!ok4) {
    console.log(Y('\n  VERDICT: clientul e corect, dar tokenul nu mai e viu.'));
    console.log(Y('  -> trebuie un consimtamant nou: node mavis-tools/google-refresh.js link'));
    console.log(Y('  -> apoi: node mavis-tools/google-refresh.js code "<url>"\n'));
    process.exit(2);
  }

  // 5. CAT TIMP MAI AI TOKENUL? + appul e publicat sau nu?
  //    refresh_token_expires_in e prezent DOAR cand consent screen-ul e in
  //    "Testing" (limita de 7 zile). Daca ABSENT -> appul e In production
  //    si tokenul nu mai expira in 7 zile.
  if (expiresIn === undefined) {
    console.log(G('  [5] expirare         fara limita de 7 zile') + D('  (appul e IN PRODUCTION)'));
  } else {
    const h = expiresIn / 3600;
    const exp = new Date(Date.now() + expiresIn * 1000).toISOString().replace('.000Z', 'Z');
    const paint = h < 48 ? R : Y;
    console.log(paint(`  [5] expirare         ${h.toFixed(1)} ore  (${exp})`));
    console.log(Y('      appul e INCA IN "Testing" -> tokenul moare in 7 zile de la consimtamant.'));
    console.log(D('      Fix: Cloud Console -> OAuth consent screen -> Publish app -> In production.'));
    console.log(D('      Dupa publicare: node mavis-tools/google-refresh.js link'));
  }

  // 6. DRIFT SCOPE-URI: tokenul are exact scope-urile canonice?
  //    Daca un re-consimtamant a fost facut cu o lista mai scurta, tokenul
  //    pierde capacitati (ex. gmail.settings.basic -> filtrele nu se repara
  //    din cloud). Se vede aici, inainte sa te treaca.
  try {
    const canon = require('./google-scopes.js').ALL;
    const lipsa = canon.filter((x) => !grantedScopes.includes(x));
    const extra = grantedScopes.filter((x) => !canon.includes(x));
    if (!grantedScopes.length) {
      console.log(Y('  [6] scope-uri         INDETERMINAT (raspunsul nu contine scope)'));
    } else if (!lipsa.length) {
      console.log(G(`  [6] scope-uri         OK  (${grantedScopes.length}, identice cu lista canonica)`));
    } else {
      console.log(R(`  [6] scope-uri         DRIFT  (lipsesc ${lipsa.length})`));
      lipsa.forEach((x) => console.log(R('      lipseste: ' + x.replace('https://www.googleapis.com/auth/', ''))));
      if (extra.length) extra.forEach((x) => console.log(D('      in plus: ' + x.replace('https://www.googleapis.com/auth/', ''))));
      console.log(Y('      -> re-consimtamant cu lista completa: node mavis-tools/google-refresh.js link'));
    }
  } catch (e) {
    console.log(Y('  [6] scope-uri         INDETERMINAT (' + e.message.slice(0, 60) + ')'));
  }

  console.log(G(B('\n  VERDICT: Google e conectat. Poate rula google-verify.js.\n')));
  process.exit(0);
})();
