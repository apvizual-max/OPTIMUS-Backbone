#!/usr/bin/env node
/**
 * GOOGLE EXCHANGE — transforma codul de autorizare in refresh_token.
 *
 * Se foloseste cand browserul a fost directionat pe un 127.0.0.1 care nu asculta
 * (ex: flow-ul pornit din cloud). Codul se ia din bara de adresa a browserului
 * si se paseaza aici.
 *
 *   node mavis-tools/google-exchange.js <cod sau URL complet>
 *   node mavis-tools/google-exchange.js --url "http://127.0.0.1:8976/callback?code=..."
 *
 * Iese: cheile gata de introdus in secret manager.
 * NU scrie nimic in repo. Nu afiseaza nimic pana nu reuseste schimbul.
 */
const fs = require('fs');
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
  // accepta si URL complet cu ?code=... sau &code=...
  const m = s.match(/[?&]code=([^&\s]+)/);
  if (m) return decodeURIComponent(m[1]);
  if (/^[A-Za-z0-9._\-]+$/.test(s)) return s; // cod brut
  return null;
}

function client() {
  // 1. env vars (cloud sau local)
  const eid = process.env.GOOGLE_CLIENT_ID || process.env.GOOGLE_CLIENT_ID_MAVIS_CLOUD;
  const esec = process.env.GOOGLE_CLIENT_SECRET || process.env.GOOGLE_CLIENT_SECRET_MAVIS_CLOUD;
  if (eid && esec) return { client_id: eid, client_secret: esec, from: 'env' };
  // 2. fisier local
  const c = AUTH.readJson(AUTH.CREDS_FILE);
  if (c) {
    const inst = c.installed || c.web || c;
    if (inst.client_id && inst.client_secret) {
      return { client_id: inst.client_id, client_secret: inst.client_secret, from: AUTH.CREDS_FILE };
    }
  }
  return null;
}

(async () => {
  const args = process.argv.slice(2).filter(a => a !== '--url');
  const raw = args[0] || '';
  const code = extractCode(raw);

  if (!code) {
    console.log(C.r('\nNu am primit un cod de autorizare.\n'));
    console.log('Foloseste una din forme:\n');
    console.log('  node mavis-tools/google-exchange.js 4/0Ad...\n');
    console.log('  node mavis-tools/google-exchange.js "http://127.0.0.1:8976/callback?code=4/0Ad..."\n');
    process.exit(1);
  }

  const c = client();
  if (!c) {
    console.log(C.r('Nu am client OAuth. Seteaza GOOGLE_CLIENT_ID si GOOGLE_CLIENT_SECRET,\n' +
      'sau pune credentials.json in ' + AUTH.CREDS_FILE + '\n'));
    process.exit(1);
  }

  console.log(C.d('Schimb codul de autorizare...'));
  const r = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: c.client_id,
      client_secret: c.client_secret,
      code,
      grant_type: 'authorization_code',
      redirect_uri: REDIRECT_URI,
    }).toString(),
  });
  const j = await r.json();

  if (j.error) {
    console.log(C.r('\nSchimbul a esuat: ' + j.error + ' — ' + (j.error_description || '') + '\n'));
    if (j.error === 'redirect_uri_mismatch') {
      console.log(C.y('redirect_uri nu se potriveste cu cel din cererea de autorizare.'));
      console.log(C.y('Portul asteptat aici: ' + REDIRECT_PORT + '. Daca linkul avea alt port, reia cu:\n'));
      console.log('  GOOGLE_REDIRECT_PORT=<port> node mavis-tools/google-exchange.js <cod>\n');
    }
    if (j.error === 'invalid_grant') {
      console.log(C.y('Codul a expirat (10 min) sau a fost deja folosit. Generaza un link nou.\n'));
    }
    process.exit(1);
  }

  // salveaza local, daca e posibil
  try {
    fs.mkdirSync(path.dirname(AUTH.TOKENS_FILE), { recursive: true });
    fs.writeFileSync(AUTH.TOKENS_FILE, JSON.stringify({
      access_token: j.access_token,
      refresh_token: j.refresh_token,
      scope: j.scope,
      token_type: j.token_type,
      expires_in: j.expires_in,
      obtained_at: new Date().toISOString(),
    }, null, 2), { mode: 0o600 });
    fs.chmodSync(AUTH.TOKENS_FILE, 0o600);
    console.log(C.g('Token salvat in ' + AUTH.TOKENS_FILE));
  } catch (e) { console.log(C.d('Nu am putut salva local: ' + e.message)); }

  console.log(C.b('\n=== CHEI PENTRU SECRET MANAGER ===\n'));
  console.log('GOOGLE_CLIENT_ID=' + c.client_id);
  console.log('GOOGLE_CLIENT_SECRET=' + c.client_secret);
  console.log('GOOGLE_REFRESH_TOKEN=' + j.refresh_token);
  console.log('GOOGLE_EMAIL=' + (process.env.GOOGLE_EMAIL || 'apvizual@gmail.com'));
  console.log(C.d('\nscope-uri acordate:\n  ' + String(j.scope || '').split(/\s+/).join('\n  ')));
  console.log('');
})();
