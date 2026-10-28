#!/usr/bin/env node
/**
 * GOOGLE LINK FILE — genereaza linkul de autorizare si il scrie in repo.
 *
 *   node mavis-tools/google-link-file.js           # scrie fisierul
 *   node mavis-tools/google-link-file.js --print   # si il afiseaza (doar LOCAL)
 *
 * DE CE EXISTA (2026-10-22):
 *   Platforma mascheaza valorile din secret manager in mesajele mele.
 *   Un link de autorizare trimis prin chat ajunge in browser cu
 *   "{{ARCHON_SECRET:GOOGLE_CLIENT_ID...}}" in loc de client_id real ->
 *   "Error 401: invalid_client". Am pierdut doua runde pe asta.
 *
 *   Așa: linkul ajunge la tine prin REPO (fisier text, deschis in browser),
 *   unde nu poate fi mascat. Secretul nu se misca nici macar.
 *
 *   Client ID e un identificator, nu un secret — e in google-client.json,
 *   in repo, intentionat. Secretul (client_secret) sta in secret manager.
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const CLIENT_JSON = path.join(__dirname, 'google-client.json');
const OUT_REL = path.join('18-GOOGLE', 'AUTORIZARE-LINK.txt');

const C = {
  b: s => `\x1b[1m${s}\x1b[0m`, g: s => `\x1b[32m${s}\x1b[0m`,
  y: s => `\x1b[33m${s}\x1b[0m`, r: s => `\x1b[31m${s}\x1b[0m`, d: s => `\x1b[2m${s}\x1b[0m`,
};

function readClientConfig() {
  try { return JSON.parse(fs.readFileSync(CLIENT_JSON, 'utf8')); } catch { return null; }
}

function buildLink(cfg) {
  const clientId = process.env.GOOGLE_CLIENT_ID_MAVIS_CLOUD || process.env.GOOGLE_CLIENT_ID || cfg.client_id;
  const redirect = process.env.GOOGLE_REDIRECT_URI || cfg.redirect_uri || 'http://127.0.0.1:8976';
  const scopes = cfg.scope_uri && cfg.scope_uri.length ? cfg.scope_uri : require('./google-scopes.js').ALL;
  const p = new URLSearchParams({
    client_id: clientId,
    redirect_uri: redirect,
    response_type: 'code',
    scope: scopes.join(' '),
    access_type: 'offline',
    prompt: 'consent',
    include_granted_scopes: 'true',
  });
  return 'https://accounts.google.com/o/oauth2/v2/auth?' + p.toString();
}

const cfg = readClientConfig();
if (!cfg || !cfg.client_id) {
  console.error(C.r('\n[ROSU] Nu pot citi mavis-tools/google-client.json'));
  console.error('       (sau nu are client_id). Verifica fisierul.\n');
  process.exit(1);
}

const envId = process.env.GOOGLE_CLIENT_ID_MAVIS_CLOUD || process.env.GOOGLE_CLIENT_ID;
if (envId && envId !== cfg.client_id) {
  console.log(C.y('  [ATENTIE] DRIFT: client_id din secret manager != cel din google-client.json'));
  console.log(C.y('    env  : ' + envId));
  console.log(C.y('    repo : ' + cfg.client_id));
  console.log(C.y('    Folosesc pe cel din env. Daca env-ul e gresit, corecteaza-l.\n'));
}

const link = buildLink(cfg);
const stamp = new Date().toISOString().slice(0, 16).replace('T', ' ');

const body = [
  '=== GOOGLE — LINK DE AUTORIZARE ===',
  '',
  'Generat: ' + stamp,
  'Client: ' + cfg.nume_client + ' (' + cfg.tip + ')  |  proiect: ' + cfg.proiect,
  'Redirect: ' + (process.env.GOOGLE_REDIRECT_URI || cfg.redirect_uri),
  '',
  '--- LINK (copiaza tot cu tot) ---',
  '',
  link,
  '',
  '--- CE FACI CU EL ---',
  '',
  '1. Deschide linkul in browser.',
  '2. Alege contul apvizual@gmail.com -> Continue -> Allow.',
  '3. Browserul va incerca sa deschida http://127.0.0.1:8976 si va da un ecran gol',
  '   sau o eroare de conexiune. ASTA E NORMAL — nimic nu ruleaza acolo.',
  '4. Copiaza bara de adresa intreaga (contine ?code=...).',
  '5. Trimite-o inapoi la Mavis Cloud.',
  '',
  'IMPORTANT: acest link contine client_id, care e un identificator public, nu un secret.',
  'Nu trimite client_secret in chat.',
  '',
].join('\n');

const outPath = path.join(ROOT, OUT_REL);
fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, body, 'utf8');

console.log(C.g('\n  Link scris: ') + C.b(OUT_REL));
console.log(C.d('  Deschide-l in browser de pe GitHub (raw) sau din repo local.\n'));

if (process.argv.includes('--print')) {
  console.log(C.y('  --print: afisez si in terminal (util doar LOCAL, nu prin chat)\n'));
  console.log(link + '\n');
}
