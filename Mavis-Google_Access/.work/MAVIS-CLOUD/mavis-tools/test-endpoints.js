#!/usr/bin/env node
/**
 * TEST ENDPOINTS — verifica ca URL-urile din kit.js sunt corecte.
 *
 * Ideea: trimitem un token FALS intentionat. Un endpoint care EXISTA raspunde
 * 401 (sau 400/403). Un endpoint cu URL gresit raspunde 404 sau 000.
 * Diferenta dintre 404 si 401 este exact diferenta dintre "host gresit" si "merge".
 *
 * Asta a prins o eroare reala: www.googleapis.com/docs/v1 -> 404.
 * API-urile Google au fiecare propriul host:
 *   drive      -> www.googleapis.com/drive/v3
 *   gmail      -> gmail.googleapis.com/gmail/v1
 *   calendar   -> www.googleapis.com/calendar/v3
 *   docs       -> docs.googleapis.com/document/v1
 *   sheets     -> sheets.googleapis.com/v4
 *   slides     -> slides.googleapis.com/v1
 *   photos     -> photoslibrary.googleapis.com/v1
 *
 *   node mavis-tools/test-endpoints.js
 */
const https = require('https');

const FAKE = 'ya29.intentional_invalid_token_endpoint_probe';
const TRIES = 4;

const ENDPOINTS = [
  ['drive:about', 'GET', 'https://www.googleapis.com/drive/v3/about?fields=user,storageQuota'],
  ['drive:files', 'GET', 'https://www.googleapis.com/drive/v3/files?q=trashed%3Dfalse&pageSize=1'],
  ['gmail:labels', 'GET', 'https://gmail.googleapis.com/gmail/v1/users/me/labels'],
  ['gmail:profile', 'GET', 'https://gmail.googleapis.com/gmail/v1/users/me/profile'],
  ['gmail:threads', 'GET', 'https://gmail.googleapis.com/gmail/v1/users/me/threads?q=in%3Ainbox&maxResults=1'],
  ['calendar:list', 'GET', 'https://www.googleapis.com/calendar/v3/users/me/calendarList'],
  ['docs:get', 'GET', 'https://docs.googleapis.com/document/v1/documents/invalid-id'],
  ['sheets:values', 'GET', 'https://sheets.googleapis.com/v4/spreadsheets/invalid-id/values/A1%3AZ50'],
  ['slides:get', 'GET', 'https://slides.googleapis.com/v1/presentations/invalid-id'],
  ['photos:albums', 'GET', 'https://photoslibrary.googleapis.com/v1/albums?pageSize=5'],
  ['tokeninfo', 'GET', 'https://oauth2.googleapis.com/tokeninfo?access_token=' + FAKE],
];

function once(method, url) {
  return new Promise(res => {
    const req = https.request(url, { method, headers: { Authorization: 'Bearer ' + FAKE } }, resp => {
      let d = ''; resp.on('data', c => d += c); resp.on('end', () => res({ code: resp.statusCode, body: d }));
    });
    req.on('error', e => res({ code: 0, body: e.message }));
    req.setTimeout(12000, () => { req.destroy(); res({ code: 0, body: 'timeout' }); });
    req.end();
  });
}

async function probe(name, method, url) {
  let last;
  for (let i = 0; i < TRIES; i++) {
    last = await once(method, url);
    if (last.code !== 0) return last;
    await new Promise(r => setTimeout(r, 700));
  }
  return last;
}

(async () => {
  console.log('\n=== TEST ENDPOINTS (token fals intentionat) ===\n');
  let broken = 0, unreachable = 0;
  for (const [name, method, url] of ENDPOINTS) {
    const r = await probe(name, method, url);
    // 401/403/400 = endpointul exista. 404 = URL gresit. 0 = retea blocata.
    const exists = [400, 401, 403].includes(r.code);
    if (r.code === 404) broken++;
    else if (r.code === 0) unreachable++;
    const mark = exists ? '\x1b[32mOK  \x1b[0m' : r.code === 0 ? '\x1b[33mBLOC\x1b[0m' : '\x1b[31mFAIL\x1b[0m';
    const hint = r.code === 404 ? '  <- URL GRESIT (404)'
      : r.code === 0 ? '  <- host inaccesibil din reteaua curenta (nu e vina URL-ului)'
        : '';
    console.log(`  ${mark} ${name.padEnd(16)} http=${String(r.code).padEnd(4)}${hint}`);
  }
  if (broken) console.log(`\n\x1b[31m${broken} endpoint(uri) cu URL GRESIT (404).\x1b[0m`);
  if (unreachable) console.log(`\x1b[33m${unreachable} endpoint(uri) inaccesibile din reteaua curenta.\x1b[0m`);
  if (!broken) console.log('\n\x1b[32mNiciun URL gresit. Corecte.\x1b[0m');
  console.log('');
  // esueaza DOAR la 404 (regresie reala de URL). 0 = retea, nu stricam CI-ul pentru asta.
  process.exit(broken ? 1 : 0);
})();
