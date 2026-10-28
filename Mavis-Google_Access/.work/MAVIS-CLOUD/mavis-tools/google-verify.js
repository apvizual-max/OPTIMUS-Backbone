#!/usr/bin/env node
/**
 * GOOGLE VERIFY — ruleaza in CLOUD, dupa ce cheile sunt in secret manager.
 *
 * Doar citire. Nu scrie, nu muta, nu sterge nimic din Drive sau Gmail.
 * Nicio valoare inventata: fiecare rand vine dintr-un HTTP real.
 *
 *   node mavis-tools/google-verify.js
 *   node mavis-tools/google-verify.js --json     (output machine-readable)
 */
const AUTH = require('./google-auth.js');

const C = {
  b: (s) => `\x1b[1m${s}\x1b[0m`, g: (s) => `\x1b[32m${s}\x1b[0m`,
  y: (s) => `\x1b[33m${s}\x1b[0m`, r: (s) => `\x1b[31m${s}\x1b[0m`, d: (s) => `\x1b[2m${s}\x1b[0m`,
};
const JSON_OUT = process.argv.includes('--json');
const results = [];

function rec(service, status, detail) {
  results.push({ service, status, detail });
  if (!JSON_OUT) {
    const mark = status === 'OK' ? C.g('OK  ') : status === 'BLOCKED' ? C.y('BLOC') : C.r('FAIL ');
    console.log(`  ${mark} ${service.padEnd(22)} ${C.d(detail)}`);
  }
}

(async () => {
  const d = AUTH.describe();

  if (!JSON_OUT) {
    console.log(C.b('\n=== GOOGLE VERIFY ===\n'));
    console.log(C.d('credentiale: ') + (d.resolved ? C.g(d.source) : C.r('nu exista')) +
      (d.source_detail ? C.d(' (' + d.source_detail.join(', ') + ')') : ''));
    if (d.missing.length) console.log(C.d('lipsesc: ') + d.missing.join(', '));
    console.log('');
  }

  if (!d.resolved) {
    rec('credentiale', 'FAIL', 'lipsesc: ' + d.missing.join(', '));
    if (JSON_OUT) console.log(JSON.stringify(results, null, 2));
    else console.log(C.r('\nAdauga cheile in secret manager, apoi reia.\n'));
    process.exit(1);
  }

  let k;
  try { k = require('./kit.js'); }
  catch (e) { rec('kit', 'FAIL', e.message); process.exit(1); }

  // ---- token ----
  let info = null;
  try {
    info = await k.tokeninfo();
    rec('token', 'OK', `email=${info.email} expira_in=${info.expires_in}s`);
  } catch (e) {
    rec('token', 'FAIL', e.message.slice(0, 160));
    if (JSON_OUT) console.log(JSON.stringify(results, null, 2));
    else {
      console.log(C.r('\nTokenul nu se poate reface. Daca primeste "invalid_grant", vezi docs/GOOGLE-INTEGRARE.md sectiunea "7 zile".\n'));
    }
    process.exit(1);
  }

  const granted = String(info.scope || '').split(/\s+/).filter(Boolean);
  const has = (s) => granted.includes(s);
  if (!JSON_OUT) {
    console.log(C.d('\nscope-uri acordate:'));
    for (const s of granted) console.log(C.d('  · ' + s));
    console.log('');
  }

  // ---- DRIVE ----
  try {
    const a = await k.drive.about();
    rec('drive:about', 'OK', `${a.user.emailAddress} | folosit ${a.storageQuota.usage} / ${a.storageQuota.limit} bytes`);
  } catch (e) { rec('drive:about', 'FAIL', e.message.slice(0, 160)); }

  // Structura reala din Drive = PKM-ul lui POPY (folderul "Alex Work" a fost
  // desfiintat in 2026-10-22). Verificam folderele de la radacina.
  try {
    const r = await k.drive.list("mimeType='application/vnd.google-apps.folder' and 'root' in parents and trashed=false", 50);
    const names = r.files.map(f => f.name).slice(0, 12);
    rec('drive:structura', 'OK', `${r.files.length} foldere la radacina: ${names.join(', ')}${r.files.length > 12 ? ' …' : ''}`);
  } catch (e) { rec('drive:structura', 'FAIL', e.message.slice(0, 160)); }

  // ---- GMAIL ----
  try {
    const p = await k.gmail.profile();
    rec('gmail:profile', 'OK', `${p.emailAddress} | ${p.messagesTotal} mesaje | ${p.threadsTotal} thread-uri`);
  } catch (e) { rec('gmail:profile', 'FAIL', e.message.slice(0, 160)); }

  try {
    const l = await k.gmail.labels();
    const mavis = l.labels.filter(x => x.name.startsWith('MAVIS/'));
    rec('gmail:etichete', 'OK', `${l.labels.length} etichete total, ${mavis.length} din seria MAVIS/*`);
  } catch (e) { rec('gmail:etichete', 'FAIL', e.message.slice(0, 160)); }

  // ---- CALENDAR ----
  try {
    const c = await k.calendar.list();
    rec('calendar', 'OK', `${c.items.length} calendare: ${c.items.slice(0, 4).map(x => x.summary).join(', ')}`);
  } catch (e) { rec('calendar', 'FAIL', e.message.slice(0, 160)); }

  // ---- DOCS / SHEETS / SLIDES (prin gasirea unui fisier real) ----
  async function findNative(mime, label, probe) {
    try {
      const r = await k.drive.list(`mimeType='${mime}' and trashed=false`, 5);
      if (!r.files.length) { rec(label, 'BLOCKED', 'scope ok, dar nu exista niciun fisier de acest tip in Drive'); return; }
      const f = r.files[0];
      const out = await probe(f.id);
      rec(label, 'OK', `"${f.name}" — ${out}`);
    } catch (e) { rec(label, 'FAIL', e.message.slice(0, 160)); }
  }

  // DOCS: docs.googleapis.com e BLOCAT din cloud (HTTP 400, pagina anti-bot
  // reCAPTCHA — nu JSON de eroare). Credentialele sunt corecte. Workaround
  // masurat: exportul prin Drive, care merge si intoarce continut real.
  await findNative('application/vnd.google-apps.document', 'docs',
    async (id) => {
      try {
        const d = await k.docs.get(id);
        return `${d.title} | ${(d.body?.content || []).length} blocuri`;
      } catch (e) {
        const txt = await k.docs.text(id);
        const head = txt.replace(/\s+/g, ' ').trim().slice(0, 60);
        return `API Docs blocat din cloud (anti-bot) — continutul prin Drive export: ${txt.length} caractere | "${head}..."`;
      }
    });

  await findNative('application/vnd.google-apps.spreadsheet', 'sheets',
    async (id) => { const v = await k.sheets.values(id, 'A1:Z50'); return `${v.range} = ${(v.values || []).length} randuri`; });

  await findNative('application/vnd.google-apps.presentation', 'slides',
    async (id) => { const s = await k.slides.get(id); return `${s.title} | ${(s.slides || []).length} slide-uri`; });

  // ---- PHOTOS ----
  try {
    const a = await k.photos.albums(20);
    rec('photos:albums', 'OK', `${(a.albums || []).length} albume`);
  } catch (e) { rec('photos:albums', 'FAIL', e.message.slice(0, 160)); }

  // ---- MAPS (are nevoie de API key, nu de OAuth) ----
  const mk = process.env.GOOGLE_MAPS_API_KEY;
  if (!mk) {
    rec('maps', 'BLOCKED', 'needs GOOGLE_MAPS_API_KEY (API key, nu OAuth) + proiect Cloud cu billing');
  } else {
    try {
      const r = await fetch('https://maps.googleapis.com/maps/api/geocode/json?address=Bucharest&key=' + encodeURIComponent(mk));
      const j = await r.json();
      rec('maps', j.status === 'OK' ? 'OK' : 'BLOCKED', `status=${j.status} ${j.error_message || ''}`.slice(0, 140));
    } catch (e) { rec('maps', 'FAIL', e.message.slice(0, 120)); }
  }

  // ---- verdict ----
  const ok = results.filter(r => r.status === 'OK').length;
  const blocked = results.filter(r => r.status === 'BLOCKED').length;
  const failed = results.filter(r => r.status === 'FAIL').length;

  if (JSON_OUT) {
    console.log(JSON.stringify({ results, grantedScopes: granted, summary: { ok, blocked, failed } }, null, 2));
  } else {
    console.log(C.b(`\nrezultat: ${ok} ok, ${blocked} blocate, ${failed} esuate\n`));
    if (failed) console.log(C.y('Cele cu FAIL sunt probleme reale de credential sau scope.\n'));
  }
  process.exit(failed ? 1 : 0);
})();
