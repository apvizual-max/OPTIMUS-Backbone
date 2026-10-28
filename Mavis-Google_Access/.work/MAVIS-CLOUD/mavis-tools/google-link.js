#!/usr/bin/env node
/**
 * GOOGLE LINK — genereaza linkul de autorizare. Corect, de fiecare data.
 *
 *   node mavis-tools/google-link.js
 *
 * De ce exista: linkul a fost transcris de mana si s-a stricat
 * ("preadsheets" in loc de "spreadsheets" -> invalid_scope).
 * Scope-urile vin din lista canonica, nu din tastare.
 *
 * Redirect-ul e pe 127.0.0.1:8976 — port fix, ca portul sa fie
 * IDENTIC in cererea de autorizare si in schimbul de token.
 */
const AUTH = require('./google-auth.js');

// FARA FALLBACK HARDCODAT. 2026-10-22: un client_id hardcodat a ramas
// in repo si a fost folosit cand secretul avea alt client (cel pentru
// Hermes CLI) -> "Error 401: invalid_client" in browser, fara explicatie.
// Daca lipseste client_id, se opreste. Nu se mai inventeaza nimic.
const CLIENT_ID = process.env.GOOGLE_CLIENT_ID
  || process.env.GOOGLE_CLIENT_ID_MAVIS_CLOUD;
if (!CLIENT_ID) {
  console.error('\n[ROSU] Nu exista GOOGLE_CLIENT_ID / GOOGLE_CLIENT_ID_MAVIS_CLOUD.');
  console.error('       Fara client_id, linkul de autorizare ar fi invalid.');
  console.error('       Pune client_id-ul in secret manager (Mavis Cloud) sau in env.\n');
  process.exit(1);
}

const PORT = Number(process.env.GOOGLE_REDIRECT_PORT || 8976);
const REDIRECT_URI = `http://127.0.0.1:${PORT}`;

const WITH_PHOTOS = process.argv.includes('--with-photos');
const SCOPES = WITH_PHOTOS
  ? [...AUTH.FULL_SCOPES, ...AUTH.PHOTOS_SCOPES]
  : AUTH.FULL_SCOPES;

const p = new URLSearchParams({
  client_id: CLIENT_ID,
  redirect_uri: REDIRECT_URI,
  response_type: 'code',
  scope: SCOPES.join(' '),
  access_type: 'offline',
  prompt: 'consent',
  include_granted_scopes: 'true',
});
const url = 'https://accounts.google.com/o/oauth2/v2/auth?' + p.toString();

// verificare: scope-urile din link trebuie sa fie EXACT lista canonica
const back = new URL(url).searchParams.get('scope').split(' ').sort();
const want = SCOPES.slice().sort();
if (JSON.stringify(back) !== JSON.stringify(want)) {
  console.error('EROARE: scope-urile din link nu corespund listei canonice.');
  process.exit(1);
}

console.log(url);
console.error('\nScope-uri (' + back.length + '):');
for (const s of back) console.error('  - ' + s);
console.error('\nDupa ce consimti: browserul va muri pe ' + REDIRECT_URI);
console.error('Copieaza bara de adresa (contine ?code=...) si trimite-mi codul.\n');
