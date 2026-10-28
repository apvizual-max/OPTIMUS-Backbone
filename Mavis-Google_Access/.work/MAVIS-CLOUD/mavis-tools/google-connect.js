#!/usr/bin/env node
/**
 * GOOGLE CONNECT — one-paste finisher.
 *
 *   node mavis-tools/google-connect.js <cod sau URL de callback>
 *
 * 1. schimba codul de autorizare in refresh_token
 * 2. scrie tokenul local
 * 3. ruleaza verificarea completa (Drive, Gmail, Calendar, Docs, Sheets, Slides)
 * 4. afiseaza cele 3 chei de pus in secret manager
 *
 * Daca o sa dai codul in chat, cheile ies aici, nu in repo.
 */
const { execFileSync } = require('child_process');
const path = require('path');
const AUTH = require('./google-auth.js');

const C = {
  b: (s) => `\x1b[1m${s}\x1b[0m`, g: (s) => `\x1b[32m${s}\x1b[0m`,
  y: (s) => `\x1b[33m${s}\x1b[0m`, r: (s) => `\x1b[31m${s}\x1b[0m`, d: (s) => `\x1b[2m${s}\x1b[0m`,
};

const REDIRECT_PORT = Number(process.env.GOOGLE_REDIRECT_PORT || 8976);
const REDIRECT_URI = `http://127.0.0.1:${REDIRECT_PORT}`;

function extractCode(input) {
  const s = String(input || '').trim();
  if (!s) return null;
  const m = s.match(/[?&]code=([^&\s]+)/);
  if (m) return decodeURIComponent(m[1]);
  if (/^[A-Za-z0-9._\-/]+$/.test(s)) return s;
  return null;
}

function client() {
  const eid = process.env.GOOGLE_CLIENT_ID || process.env.GOOGLE_CLIENT_ID_MAVIS_CLOUD;
  const esec = process.env.GOOGLE_CLIENT_SECRET || process.env.GOOGLE_CLIENT_SECRET_MAVIS_CLOUD;
  if (eid && esec) return { client_id: eid, client_secret: esec };
  const c = AUTH.readJsonTolerant(AUTH.CREDS_FILE);
  if (c) {
    const inst = c.installed || c.web || c;
    if (inst.client_id && inst.client_secret) return { client_id: inst.client_id, client_secret: inst.client_secret };
  }
  return null;
}

if (require.main === module) {
  (async () => {
    const code = extractCode(process.argv.slice(2).filter(a => a !== '--url')[0]);
    if (!code) {
      console.log(C.r('\nNu am primit un cod. Trimite-l pe intreg, cu tot cu adresa:'));
      console.log(C.d('  node mavis-tools/google-connect.js "http://127.0.0.1:8976/callback?code=..."\n'));
      process.exit(1);
    }
    const c = client();
    if (!c) { console.log(C.r('Nu am client OAuth.')); process.exit(1); }

    console.log(C.d('Schimb codul...'));
    // Retei: din sandboxul de cloud, conexiunea la oauth2.googleapis.com pica
    // intermitent (masurat 2026-10-22: ~1 din 5 requesturi = connect timeout).
    // Un cod de autorizare e de unica folosinta, deci o pica de retea NU
    // trebuie sa consume codul — de aici retries.
    const payload = new URLSearchParams({
      client_id: c.client_id, client_secret: c.client_secret,
      code, grant_type: 'authorization_code', redirect_uri: REDIRECT_URI,
    }).toString();
    let j = null, lastErr = null;
    for (let i = 0; i < 8; i++) {
      if (i) {
        const wait = Math.min(2000 * i, 8000);
        console.log(C.y('  retea instabila — reiau in ' + wait + 'ms (incep ' + (i + 1) + '/8)'));
        await new Promise(z => setTimeout(z, wait));
      }
      try {
        const r = await fetch('https://oauth2.googleapis.com/token', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: payload,
          signal: AbortSignal.timeout(20000),
        });
        j = await r.json();
        lastErr = null;
        break;
      } catch (e) { lastErr = e; j = null; }
    }
    if (!j) {
      console.log(C.r('\nNu am putut contacta Google: ' + (lastErr?.cause?.code || lastErr?.message)));
      console.log(C.y('Codul de autorizare NU s-a consumat (nu a ajuns la Google). Reia cu acelasi cod.'));
      console.log(C.y('Daca persista, ruleaza din nou google-connect.js cu acelasi cod.\n'));
      process.exit(1);
    }
    if (j.error) {
      console.log(C.r('\nSchimbul a esuat: ' + j.error + ' — ' + (j.error_description || '') + '\n'));
      if (j.error === 'redirect_uri_mismatch') {
        console.log(C.y('Portul asteptat: ' + REDIRECT_PORT + '. Reia cu GOOGLE_REDIRECT_PORT=<port> ...\n'));
      }
      if (j.error === 'invalid_grant') {
        console.log(C.y('Codul a fost consumat sau a expirat. Deschide linkul de autorizare din nou, ia un cod nou.\n'));
      }
      process.exit(1);
    }

    console.log(C.g('Token primit. Scope-uri: ' + String(j.scope || '').split(/\s+/).join(', ')));

    try {
      const fs = require('fs');
      fs.mkdirSync(path.dirname(AUTH.TOKENS_FILE), { recursive: true });
      fs.writeFileSync(AUTH.TOKENS_FILE, JSON.stringify({
        access_token: j.access_token, refresh_token: j.refresh_token, scope: j.scope,
        token_type: j.token_type, expires_in: j.expires_in, obtained_at: new Date().toISOString(),
      }, null, 2), { mode: 0o600 });
      console.log(C.g('Token salvat in ' + AUTH.TOKENS_FILE));
    } catch (e) { console.log(C.d('Nu am putut salva local: ' + e.message)); }

    console.log(C.b('\n=== VERIFICARE LIVE ===\n'));
    const env = {
      ...process.env,
      GOOGLE_CLIENT_ID: c.client_id,
      GOOGLE_CLIENT_SECRET: c.client_secret,
      GOOGLE_REFRESH_TOKEN: j.refresh_token,
    };
    try {
      execFileSync(process.execPath, [path.join(__dirname, 'google-verify.js')], { env, stdio: 'inherit' });
    } catch (e) { /* verify printeaza propriul verdict */ }

    console.log(C.b('\n=== CHEI PENTRU SECRET MANAGER ===\n'));
    console.log('GOOGLE_CLIENT_ID_MAVIS_CLOUD     = ' + c.client_id);
    console.log('GOOGLE_CLIENT_SECRET_MAVIS_CLOUD = ' + c.client_secret);
    console.log('GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD = ' + j.refresh_token);
    console.log('');
  })();
}
module.exports = { extractCode };
