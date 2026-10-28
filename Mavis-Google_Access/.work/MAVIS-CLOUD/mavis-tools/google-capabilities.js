#!/usr/bin/env node
/**
 * PROBE DE CAPABILITATE GOOGLE — Mavis Cloud
 *
 * Măsoară, nu presupune. Fiecare test face un apel real la API și raportează
 * rezultatul real. Dovezile (fisierele create) raman pe Drive, in folderul
 * `_PROOF`; artefactele tranzitorii (draft, eveniment, filtru throwaway) sunt
 * curatate la final, pentru ca nu polueze contul lui POPY.
 *
 *   node mavis-tools/google-capabilities.js
 *   node mavis-tools/google-capabilities.js --parent <folderId>   # alt folder
 *   node mavis-tools/google-capabilities.js --json rezultat.json
 *
 * REGULI:
 *  - nu trimite mail (doar draft)
 *  - nu sterge definitiv nimic (doar trash pe artefactele proprii)
 *  - filtrele throwaway: criteriu care nu poate potrivi nimic
 */

const fs = require('fs');
const path = require('path');
const kit = require('./kit.js');

const G = (s) => `\x1b[32m${s}\x1b[0m`, R = (s) => `\x1b[31m${s}\x1b[0m`;
const Y = (s) => `\x1b[33m${s}\x1b[0m`, D = (s) => `\x1b[2m${s}\x1b[0m`;
const B = (s) => `\x1b[1m${s}\x1b[0m`;

const args = process.argv.slice(2);
const argOf = (f, dflt) => { const i = args.indexOf(f); return i >= 0 ? args[i + 1] : dflt; };

const BOT_FOLDER = argOf('--parent', '1UQIxhctyJxBXIIFnpxSc5Jd0wvFxEylu');
const JSON_OUT = argOf('--json', path.join(__dirname, '.capabilities.json'));
const PROOF_NAME = '_PROOF';
const STAMP = new Date().toISOString().slice(0, 16).replace(/[:T]/g, '-');

const results = [];
let proofFolder = null;
const transient = { drafts: [], events: [], filters: [], calIds: [] };

async function test(nume, serviciu, fn) {
  const t0 = Date.now();
  try {
    const detail = await fn();
    results.push({ nume, serviciu, status: 'OK', detail: detail || '', ms: Date.now() - t0 });
    console.log(`  ${G('OK  ')} ${nume.padEnd(46)} ${D(detail || '')}`);
  } catch (e) {
    const msg = String(e.message || e).replace(/\s+/g, ' ').slice(0, 150);
    const blocked = /insufficient|403|PERMISSION|has not been used|not enabled|403 Forbidden/i.test(msg);
    results.push({ nume, serviciu, status: blocked ? 'BLOCKED' : 'FAIL', detail: msg, ms: Date.now() - t0 });
    console.log(`  ${blocked ? Y('BLOC') : R('FAIL')} ${nume.padEnd(46)} ${D(msg)}`);
  }
}

const cleanup = async () => {
  for (const d of transient.drafts) {
    try { await kit.req('DELETE', `https://gmail.googleapis.com/gmail/v1/users/me/drafts/${d}`); console.log(D(`  curatat draft ${d}`)); } catch (e) {}
  }
  for (const [cal, ev] of transient.events) {
    try { await kit.req('DELETE', `https://www.googleapis.com/calendar/v3/calendars/${encodeURIComponent(cal)}/events/${ev}`); console.log(D(`  curatat eveniment ${ev}`)); } catch (e) {}
  }
  for (const f of transient.filters) {
    try { await kit.req('DELETE', `https://gmail.googleapis.com/gmail/v1/users/me/settings/filters/${f}`); console.log(D(`  curatat filtru throwaway ${f}`)); } catch (e) {}
  }
};

(async () => {
  console.log(B('\n=== PROBE DE CAPABILITATE GOOGLE — Mavis Cloud ===\n'));
  console.log(D(`  folder tinta: ${BOT_FOLDER}\n`));

  // ---------- DRIVE ----------
  console.log(B('  DRIVE'));
  await test('drive: listare (children)', 'Drive', async () => {
    const r = await kit.req('GET', `https://www.googleapis.com/drive/v3/files?q=${encodeURIComponent(`'${BOT_FOLDER}' in parents`)}&fields=files(id,name,mimeType)&pageSize=50`);
    return `${(r.files || []).length} elemente`;
  });

  await test('drive: about (cota)', 'Drive', async () => {
    const a = await kit.drive.about();
    return `${(Number(a.storageQuota.usage) / 1e9).toFixed(2)} GB folositi`;
  });

  await test('drive: search (q pe nume)', 'Drive', async () => {
    const r = await kit.req('GET', `https://www.googleapis.com/drive/v3/files?q=${encodeURIComponent(`name contains 'Mavis' and trashed=false`)}&fields=files(id,name)&pageSize=5`);
    return `${(r.files || []).length} rezultate`;
  });

  await test('drive: create folder', 'Drive', async () => {
    const f = await kit.drive.mkdir(`${PROOF_NAME} ${STAMP}`, BOT_FOLDER);
    proofFolder = f.id;
    return `id ${f.id}`;
  });

  await test('drive: upload fisier text', 'Drive', async () => {
    const f = await kit.drive.upload(`PROBE-${STAMP}.md`,
      `# Probe Mavis Cloud ${STAMP}\n\nCreat de google-capabilities.js. Acesta este un artefact de test.\n`,
      'text/markdown', proofFolder);
    return `id ${f.id} · ${f.size}B`;
  });

  await test('drive: read back continut', 'Drive', async () => {
    const r = await kit.req('GET', `https://www.googleapis.com/drive/v3/files?q=${encodeURIComponent(`name contains 'PROBE-${STAMP}.md'`)}&fields=files(id,name,size)`);
    const f = (r.files || [])[0];
    if (!f) throw new Error('fisierul creat nu apare in cautare');
    const c = await kit.drive.download(f.id);
    return `${String(c).length} caractere citite`;
  });

  await test('drive: rename', 'Drive', async () => {
    const r = await kit.req('GET', `https://www.googleapis.com/drive/v3/files?q=${encodeURIComponent(`name contains 'PROBE-${STAMP}.md'`)}&fields=files(id,name)`);
    const f = (r.files || [])[0];
    const n = await kit.drive.rename(f.id, `PROBE-RENUMIT-${STAMP}.md`);
    return `nume nou: ${n.name}`;
  });

  await test('drive: move intre foldere', 'Drive', async () => {
    const r = await kit.req('GET', `https://www.googleapis.com/drive/v3/files?q=${encodeURIComponent(`name contains 'PROBE-RENUMIT-${STAMP}.md'`)}&fields=files(id,parents)`);
    const f = (r.files || [])[0];
    const sub = await kit.drive.mkdir(`_sub ${STAMP}`, proofFolder);
    await kit.drive.move(f.id, sub.id, f.parents[0]);
    const chk = await kit.req('GET', `https://www.googleapis.com/drive/v3/files/${f.id}?fields=parents`);
    return `parinte nou: ${chk.parents[0] === sub.id ? 'corect' : 'GRESIT'}`;
  });

  await test('drive: create Google Doc NATIV (workaround)', 'Drive', async () => {
    const f = await kit.req('POST', 'https://www.googleapis.com/drive/v3/files', {
      name: `PROBE-Doc-Nativ-${STAMP}`,
      mimeType: 'application/vnd.google-apps.document',
      parents: [proofFolder],
    });
    const t = await kit.docs.text(f.id);
    return `id ${f.id} · export: ${String(t).length} caractere`;
  });

  await test('drive: write in Google Doc (batchUpdate)', 'Drive', async () => {
    const r = await kit.req('GET', `https://www.googleapis.com/drive/v3/files?q=${encodeURIComponent(`name contains 'PROBE-Doc-Nativ-${STAMP}'`)}&fields=files(id)`);
    const id = (r.files || [])[0].id;
    const res = await kit.req('POST', `https://docs.googleapis.com/document/v1/documents/${id}:batchUpdate`, {
      requests: [{ insertText: { location: { index: 1 }, text: 'Text scris de Mavis Cloud via Docs API.\n' } }],
    });
    return `batchUpdate: ${res.replies ? res.replies.length : 0} raspunsuri`;
  });

  await test('drive: permissions.list', 'Drive', async () => {
    const r = await kit.req('GET', `https://www.googleapis.com/drive/v3/files/${proofFolder}/permissions?fields=permissions(id,role,type)`);
    return `${(r.permissions || []).length} permisiuni`;
  });

  await test('drive: share (create permission)', 'Drive', async () => {
    const r = await kit.req('POST', `https://www.googleapis.com/drive/v3/files/${proofFolder}/permissions`, {
      role: 'reader', type: 'anyone', allowFileDiscovery: false,
    });
    transient.permissions = transient.permissions || [];
    transient.permissions.push(r.id);
    return `permission id ${r.id}`;
  });

  await test('drive: trash + untrash (reversibil)', 'Drive', async () => {
    const r = await kit.req('GET', `https://www.googleapis.com/drive/v3/files?q=${encodeURIComponent(`name contains 'PROBE-RENUMIT-${STAMP}.md'`)}&fields=files(id)`);
    const id = (r.files || [])[0].id;
    await kit.drive.trashed(id, true);
    const t1 = await kit.drive.get(id);
    await kit.drive.trashed(id, false);
    const t2 = await kit.drive.get(id);
    return `trashed=${t1.trashed} -> recuperat=${!t2.trashed}`;
  });

  await test('drive: copy', 'Drive', async () => {
    const r = await kit.req('GET', `https://www.googleapis.com/drive/v3/files?q=${encodeURIComponent(`name contains 'PROBE-RENUMIT-${STAMP}.md'`)}&fields=files(id)`);
    const c = await kit.drive.copy((r.files || [])[0].id, `PROBE-COPY-${STAMP}.md`, proofFolder);
    return `copie id ${c.id}`;
  });

  // ---------- GMAIL ----------
  console.log(B('\n  GMAIL'));
  await test('gmail: profile', 'Gmail', async () => {
    const p = await kit.gmail.profile();
    return `${p.emailAddress} · ${p.messagesTotal} mesaje`;
  });

  await test('gmail: list mesaje', 'Gmail', async () => {
    const r = await kit.gmail.list('in:inbox', 5);
    return `${(r.messages || []).length} returnate`;
  });

  await test('gmail: read mesaj', 'Gmail', async () => {
    const r = await kit.gmail.list('in:inbox', 1);
    const id = (r.messages || [])[0].id;
    const m = await kit.gmail.get(id);
    return `id ${id} · ${(m.snippet || '').slice(0, 40)}`;
  });

  await test('gmail: labels (read)', 'Gmail', async () => {
    const l = await kit.gmail.labels();
    return `${l.labels.length} etichete`;
  });

  await test('gmail: create DRAFT (nu trimite)', 'Gmail', async () => {
    const d = await kit.req('POST', 'https://gmail.googleapis.com/gmail/v1/users/me/drafts', {
      message: { raw: Buffer.from(`To: ${process.env.GOOGLE_EMAIL}\r\nSubject: [PROBE Mavis Cloud] test draft\r\n\r\nArtefact de test. Se sterge automat.`).toString('base64') },
    });
    transient.drafts.push(d.id);
    return `draft id ${d.id}`;
  });

  await test('gmail: modify mesaj (add label) — pe draft-ul propriu', 'Gmail', async () => {
    // ATENTIE: endpointul users.drafts.modify da 404 in aceasta versiune de API.
    // Calea functionala: messages.modify pe id-ul mesajului din draft.
    const d = await kit.req('GET', `https://gmail.googleapis.com/gmail/v1/users/me/drafts/${transient.drafts[0]}`);
    await kit.req('POST', `https://gmail.googleapis.com/gmail/v1/users/me/messages/${d.message.id}/modify`, {
      addLabelIds: ['IMPORTANT'], removeLabelIds: ['UNREAD'],
    });
    const m = await kit.gmail.get(d.message.id);
    return `labels: ${(m.labelIds || []).join(',')}`;
  });

  await test('gmail: batchModify', 'Gmail', async () => {
    const d = await kit.req('GET', `https://gmail.googleapis.com/gmail/v1/users/me/drafts/${transient.drafts[0]}`);
    const r = await kit.req('POST', 'https://gmail.googleapis.com/gmail/v1/users/me/messages/batchModify', {
      ids: [d.message.id], addLabelIds: ['IMPORTANT'],
    });
    return `status: ${r.status || 'ok'}`;
  });

  await test('gmail: filters.list (read)', 'Gmail', async () => {
    const f = await kit.req('GET', 'https://gmail.googleapis.com/gmail/v1/users/me/settings/filters?maxResults=200');
    return `${f.filter.length} filtre`;
  });

  await test('gmail: filter CREATE+DELETE (throwaway) → dovedeste write', 'Gmail', async () => {
    // Actiunea NU poate fi goala ("Filter doesn't have any actions").
    // Criteriul nu poate potrivi nimic, deci efectul e zero chiar daca s-ar aplica.
    const f = await kit.req('POST', 'https://gmail.googleapis.com/gmail/v1/users/me/settings/filters', {
      criteria: { query: 'subject:"maviscloud-proof-9x8y7z-never-matches-anything"' },
      action: { addLabelIds: ['IMPORTANT'], removeLabelIds: [] },
    });
    transient.filters.push(f.id);
    return `filtru id ${f.id}`;
  });

  // ---------- CALENDAR ----------
  console.log(B('\n  CALENDAR'));
  let calId = null;
  await test('calendar: list calendars', 'Calendar', async () => {
    const c = await kit.calendar.list();
    calId = (c.items || [])[0].id;
    transient.calIds.push(calId);
    return `${(c.items || []).length} calendare · tinta: ${calId}`;
  });

  await test('calendar: list events', 'Calendar', async () => {
    const e = await kit.calendar.events(calId, 5);
    return `${(e.items || []).length} evenimente`;
  });

  await test('calendar: create event', 'Calendar', async () => {
    const ev = await kit.calendar.insert(calId, {
      summary: `[PROBE Mavis Cloud] test ${STAMP}`,
      start: { dateTime: '2026-10-28T10:00:00Z' },
      end: { dateTime: '2026-10-28T10:30:00Z' },
      description: 'Artefact de test. Se sterge automat.',
    });
    transient.events.push([calId, ev.id]);
    return `event id ${ev.id}`;
  });

  await test('calendar: read event back', 'Calendar', async () => {
    const ev = await kit.req('GET', `https://www.googleapis.com/calendar/v3/calendars/${encodeURIComponent(calId)}/events/${transient.events[0][1]}`);
    return ev.summary;
  });

  await test('calendar: update event', 'Calendar', async () => {
    const ev = await kit.req('PATCH', `https://www.googleapis.com/calendar/v3/calendars/${encodeURIComponent(calId)}/events/${transient.events[0][1]}`, {
      summary: `[PROBE Mavis Cloud] EDITAT ${STAMP}`,
    });
    return ev.summary;
  });

  // ---------- SHEETS ----------
  console.log(B('\n  SHEETS'));
  let sheetId = null;
  await test('sheets: create spreadsheet', 'Sheets', async () => {
    const s = await kit.req('POST', 'https://sheets.googleapis.com/v4/spreadsheets', {
      properties: { title: `PROBE-Sheet-${STAMP}` },
      sheets: [{ properties: { title: 'Probe' } }],
    });
    sheetId = s.spreadsheetId;
    return `id ${sheetId}`;
  });

  await test('sheets: write values', 'Sheets', async () => {
    const r = await kit.sheets.update(sheetId, 'Probe!A1:C2', [['Mavis Cloud', 'probe', STAMP], ['ok', 1, 2]]);
    return `updatedRange: ${r.updatedRange}`;
  });

  await test('sheets: read values', 'Sheets', async () => {
    const v = await kit.sheets.values(sheetId, 'Probe!A1:C2');
    return `${(v.values || []).length} randuri · A1=${v.values?.[0]?.[0]}`;
  });

  await test('sheets: append', 'Sheets', async () => {
    const r = await kit.sheets.append(sheetId, 'Probe!A1', [['rand nou', 'probe', STAMP]]);
    return `updatedRange: ${r.updatedRange}`;
  });

  await test('sheets: move spreadsheet in proof folder', 'Sheets', async () => {
    const f = await kit.req('GET', `https://www.googleapis.com/drive/v3/files/${sheetId}?fields=parents`);
    await kit.drive.move(sheetId, proofFolder, f.parents[0]);
    const chk = await kit.req('GET', `https://www.googleapis.com/drive/v3/files/${sheetId}?fields=parents`);
    return chk.parents[0] === proofFolder ? 'corect' : 'GRESIT';
  });

  // ---------- SLIDES ----------
  console.log(B('\n  SLIDES'));
  let presId = null;
  await test('slides: create presentation', 'Slides', async () => {
    const p = await kit.req('POST', 'https://slides.googleapis.com/v1/presentations', { title: `PROBE-Slides-${STAMP}` });
    presId = p.presentationId;
    return `id ${presId} · ${(p.slides || []).length} slide-uri`;
  });

  await test('slides: read presentation', 'Slides', async () => {
    const p = await kit.slides.get(presId);
    return `${(p.slides || []).length} slide-uri · titlu: ${p.title}`;
  });

  await test('slides: batchUpdate (add slide cu text)', 'Slides', async () => {
    // REGULI API: objectId >= 5 caractere; placeholder-ul se afla la
    // element.shape.placeholder (nu element.placeholder); insertText merge in
    // placeholder-ele layout-ului, nu intr-un slide gol.
    await kit.req('POST', `https://slides.googleapis.com/v1/presentations/${presId}:batchUpdate`, {
      requests: [{ createSlide: { objectId: 'probeSlide2', slideLayoutReference: { predefinedLayout: 'TITLE_AND_BODY' } } }],
    });
    const g = await kit.slides.get(presId);
    const sl = g.slides.find((s) => s.objectId === 'probeSlide2');
    const ph = sl.pageElements.filter((e) => e.shape && e.shape.placeholder);
    if (!ph.length) throw new Error('niciun placeholder in slide-ul creat');
    await kit.req('POST', `https://slides.googleapis.com/v1/presentations/${presId}:batchUpdate`, {
      requests: ph.map((e, i) => ({ insertText: { objectId: e.objectId, text: i === 0 ? 'Titlu scris de Mavis Cloud.' : 'Corp scris de Mavis Cloud.' } })),
    });
    const g2 = await kit.slides.get(presId);
    const sl2 = g2.slides.find((s) => s.objectId === 'probeSlide2');
    // Textul real e la textElements[].textRun.content — NU la index fix 1.
    const tx = sl2.pageElements
      .filter((e) => e.shape && e.shape.text && e.shape.text.textElements)
      .flatMap((e) => e.shape.text.textElements.map((te) => te.textRun && te.textRun.content).filter(Boolean));
    return `${g2.slides.length} slide-uri · text scris: ${JSON.stringify(tx)}`;
  });

  // ---------- DOCS (API direct — se stie ca e blocat, se testeaza oricum) ----------
  console.log(B('\n  DOCS (direct, fara workaround)'));
  await test('docs: API direct (asteptat BLOCAT din cloud)', 'Docs', async () => {
    const d = await kit.docs.create(`PROBE-Docs-API-${STAMP}`);
    return `id ${d.documentId}`;
  });

  await test('docs: WORKAROUND (upload -> copy nativ -> export)', 'Docs', async () => {
    // Asta e calea care MERGE din cloud: Docs API direct e blocat de anti-bot,
    // dar Drive API converteste fisierul intr-un Google Doc nativ.
    const tmp = await kit.drive.upload(`PROBE-doc-src-${STAMP}.md`, `# Probe Docs\n\nPrag scris de Mavis Cloud prin Drive API.\n`, 'text/markdown', proofFolder);
    const conv = await kit.req('POST', `https://www.googleapis.com/drive/v3/files/${tmp.id}/copy`, {
      name: `PROBE-Doc-Convertit-${STAMP}.md`, mimeType: 'application/vnd.google-apps.document',
    });
    const t = String(await kit.docs.text(conv.id));
    return `doc nativ id ${conv.id} · export ${t.length} char · continut ${t.includes('Prag scris') ? 'CORECT' : 'LIPSA'}`;
  });

  // ---------- CURATENIE ----------
  console.log(B('\n  CURATENIE (doar artefacte tranzitorii proprii)'));
  await cleanup();
  for (const p of (transient.permissions || [])) {
    try { await kit.req('DELETE', `https://www.googleapis.com/drive/v3/files/${proofFolder}/permissions/${p}`); console.log(D(`  curatat permission ${p}`)); } catch (e) {}
  }

  // ---------- SUMAR ----------
  const ok = results.filter((r) => r.status === 'OK').length;
  const blocked = results.filter((r) => r.status === 'BLOCKED').length;
  const fail = results.filter((r) => r.status === 'FAIL').length;
  console.log(B('\n=== REZULTAT ==='));
  console.log(`  ${G(ok + ' OK')} · ${Y(blocked + ' blocate')} · ${R(fail + ' esuate')}  (din ${results.length} teste)`);
  console.log(D(`  dovezi pastrate in Drive: ${proofFolder}`));

  fs.writeFileSync(JSON_OUT, JSON.stringify({ stamp: STAMP, proofFolder, results }, null, 2));
  console.log(D(`  JSON: ${JSON_OUT}\n`));
  process.exit(fail ? 1 : 0);
})().catch((e) => { console.error(R('\nPROBE CRASH: ' + e.message + '\n')); process.exit(3); });
