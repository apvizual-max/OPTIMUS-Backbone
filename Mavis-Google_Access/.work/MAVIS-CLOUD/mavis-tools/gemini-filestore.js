#!/usr/bin/env node
/**
 * GEMINI FILE SEARCH — RAG cu citare peste surse reale.
 *
 * Calea (a) aleasă de POPY pe 2026-10-28: pentru un cont Google normal
 * NotebookLM n-are API oficial, dar Gemini API + File Search dă același
 * rezultat: întrebări cu citare peste documente.
 *
 * FLUX (măsurat, 28 oct 2026):
 *   1. create store   POST /v1beta/fileSearchStores            {"displayName","embeddingModel"}
 *   2. upload         POST /upload/v1beta/{store}:uploadToFileSearchStore   (resumable, 2 pasi)
 *   3. poll           GET  /v1beta/{store}/upload/operations/{op}
 *   4. intreaba       POST /v1beta/models/{model}:generateContent  tools:[{file_search:{...}}]
 *
 * CHEIA: GOOGLE_AI_STUDIO_FREE_TIER_KEY (free tier AI Studio).
 *
 *   node mavis-tools/gemini-filestore.js list
 *   node mavis-tools/gemini-filestore.js init "Nume Store"
 *   node mavis-tools/gemini-filestore.js add <store> <fisierLocal> ["nume vizibil"]
 *   node mavis-tools/gemini-filestore.js fromdrive <store> <driveFileId> ["nume vizibil"]
 *   node mavis-tools/gemini-filestore.js ask <store> "intrebare"
 *   node mavis-tools/gemini-filestore.js delete <store>
 */

const fs = require('fs');
const path = require('path');
const kit = require('./kit.js');

const KEY = process.env.GOOGLE_AI_STUDIO_FREE_TIER_KEY || process.env.GEMINI_API_KEY;
const BASE = 'https://generativelanguage.googleapis.com/v1beta';
const UPLOAD = 'https://generativelanguage.googleapis.com/upload/v1beta';
// Lant de fallback: pe free tier, primul model poate da "quota exceeded".
const MODELS = (process.env.GEMINI_MODELS || 'gemini-3.8-flash,gemini-3-flash-preview,gemini-flash-latest').split(',');
const EMB = 'models/gemini-embedding-2';

const G = (s) => `\x1b[32m${s}\x1b[0m`, D = (s) => `\x1b[2m${s}\x1b[0m`;
const B = (s) => `\x1b[1m${s}\x1b[0m`, R = (s) => `\x1b[31m${s}\x1b[0m`;

async function api(method, url, body, headers) {
  if (!KEY) throw new Error('lipseste GOOGLE_AI_STUDIO_FREE_TIER_KEY (sau GEMINI_API_KEY)');
  const u = url + (url.includes('?') ? '&' : '?') + 'key=' + encodeURIComponent(KEY);
  const opts = { method, signal: AbortSignal.timeout(120000), headers: headers || {} };
  if (body !== undefined && !Buffer.isBuffer(body)) {
    opts.body = JSON.stringify(body);
    opts.headers['Content-Type'] = 'application/json';
  } else if (Buffer.isBuffer(body)) {
    opts.body = body;
  }
  let last;
  for (let i = 0; i < 4; i++) {
    try {
      const r = await fetch(u, opts);
      const t = await r.text();
      let j; try { j = JSON.parse(t); } catch (e) { j = { raw: t.slice(0, 200) }; }
      if (r.ok) return j;
      last = new Error(`HTTP ${r.status}: ${JSON.stringify(j).slice(0, 300)}`);
      if (r.status < 500) throw last;
    } catch (e) { last = e; }
    await new Promise((z) => setTimeout(z, 1500 * (i + 1)));
  }
  throw last;
}

/** Upload resumabil in 2 pasi, exact cum cere API-ul. */
async function uploadToStore(storeName, content, displayName, mime) {
  // Pas 1: cere URL-ul de upload
  const start = await fetch(`${UPLOAD}/${storeName}:uploadToFileSearchStore?key=${encodeURIComponent(KEY)}`, {
    method: 'POST',
    headers: {
      'X-Goog-Upload-Protocol': 'resumable',
      'X-Goog-Upload-Command': 'start',
      'X-Goog-Upload-Header-Content-Length': String(content.length),
      'X-Goog-Upload-Header-Content-Type': mime || 'text/plain',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ displayName }),
    signal: AbortSignal.timeout(60000),
  });
  const uploadUrl = start.headers.get('x-goog-upload-url');
  if (!uploadUrl) {
    const t = await start.text();
    throw new Error(`start upload a esuat: HTTP ${start.status} ${t.slice(0, 200)}`);
  }
  // Pas 2: trimite continutul
  const up = await fetch(uploadUrl, {
    method: 'POST',
    headers: {
      'X-Goog-Upload-Offset': '0',
      'X-Goog-Upload-Command': 'upload, finalize',
      'Content-Type': mime || 'text/plain',
    },
    body: content,
    signal: AbortSignal.timeout(180000),
  });
  const t = await up.text();
  if (!up.ok) throw new Error(`upload a esuat: HTTP ${up.status} ${t.slice(0, 250)}`);
  let j; try { j = JSON.parse(t); } catch (e) { j = {}; }
  return j;
}

async function waitOp(opName, maxMs = 180000) {
  const t0 = Date.now();
  while (Date.now() - t0 < maxMs) {
    const r = await api('GET', `${BASE}/${opName}`);
    if (r.done) {
      if (r.error) throw new Error('operatie esuata: ' + JSON.stringify(r.error).slice(0, 250));
      return r.response || {};
    }
    await new Promise((z) => setTimeout(z, 3000));
  }
  return null;
}

async function initStore(displayName) {
  // Corpul = obiectul store DIRECT (nu infasurat). embeddingModel explicit.
  const r = await api('POST', `${BASE}/fileSearchStores`, { displayName, embeddingModel: EMB });
  console.log(G(`  store creat: ${r.name}`));
  console.log(D(`  displayName: ${r.displayName} · embeddingModel: ${r.embeddingModel || EMB}`));
  return r.name;
}

async function listStores() {
  const r = await api('GET', `${BASE}/fileSearchStores?pageSize=20`);
  const list = r.fileSearchStores || [];
  console.log(B(`\n=== FILE SEARCH STORES (${list.length}) ===`));
  for (const s of list) {
    console.log(`  ${s.name}`);
    console.log(D(`    displayName: ${s.displayName} · createTime: ${s.createTime}`));
  }
  if (!list.length) console.log(D('  (niciun store)'));
  console.log();
  return list;
}

async function addBuffer(storeName, content, displayName, mime) {
  const op = await uploadToStore(storeName, content, displayName, mime);
  const opName = op.name;
  if (!opName) { console.log(G('  upload acceptat')); return op; }
  console.log(D(`  operatie: ${opName}`));
  const res = await waitOp(opName);
  const name = (res && (res.name || (res.document && res.document.name))) || opName;
  console.log(G(`  gata: ${name}`));
  return res || op;
}

async function addLocalFile(storeName, filePath, displayName) {
  const content = fs.readFileSync(filePath);
  const mime = /\.md$/i.test(filePath) ? 'text/markdown' : /\.csv$/i.test(filePath) ? 'text/csv' : 'text/plain';
  return addBuffer(storeName, content, displayName || path.basename(filePath), mime);
}

async function addDriveFile(storeName, driveFileId, displayName) {
  const meta = await kit.req('GET', `https://www.googleapis.com/drive/v3/files/${driveFileId}?fields=id,name,mimeType,size`);
  console.log(D(`  sursa Drive: ${meta.name} (${meta.mimeType}, ${meta.size}B)`));
  let content, mime = 'text/plain';
  if (meta.mimeType === 'application/vnd.google-apps.document') {
    content = Buffer.from(String(await kit.docs.text(driveFileId)), 'utf8');
  } else if (meta.mimeType === 'application/vnd.google-apps.spreadsheet') {
    const v = await kit.sheets.values(driveFileId, 'A1:Z200');
    content = Buffer.from((v.values || []).map((r) => r.join('\t')).join('\n'), 'utf8');
    mime = 'text/tab-separated-values';
  } else if (meta.mimeType === 'application/vnd.google-apps.presentation') {
    const p = await kit.slides.get(driveFileId);
    const texts = [];
    for (const s of p.slides || []) for (const e of s.pageElements || []) {
      const te = e.shape && e.shape.text && e.shape.text.textElements;
      if (te) for (const t of te) if (t.textRun) texts.push(t.textRun.content);
    }
    content = Buffer.from(texts.join('\n'), 'utf8');
  } else {
    const c = await kit.drive.download(driveFileId);
    content = Buffer.isBuffer(c) ? c : Buffer.from(String(c), 'utf8');
  }
  return addBuffer(storeName, content, displayName || meta.name, mime);
}

async function ask(storeName, question) {
  // Matarie: primul model poate da "quota exceeded" pe free tier.
  // Se incearca pe rand, pana cand unul raspunde.
  let lastErr = null;
  for (const model of MODELS) {
    try {
      const r = await api('POST', `${BASE}/models/${model}:generateContent`, {
        contents: [{ role: 'user', parts: [{ text: question }] }],
        tools: [{ file_search: { file_search_store_names: [storeName] } }],
      });
      const cands = r.candidates || [];
      const parts = (cands[0] && cands[0].content && cands[0].content.parts) || [];
      const text = parts.map((p) => p.text || '').join('\n').trim();
      const gm = cands[0] && cands[0].groundingMetadata;
      const chunks = (gm && gm.groundingChunks) || [];
      const cites = chunks.map((c) => ({
        sursa: (c.retrievedContext && c.retrievedContext.title) || (c.web && c.web.title) || '(fără titlu)',
        text: (c.retrievedContext && c.retrievedContext.text) || '',
        uri: c.web && c.web.uri,
      }));
      return { text, cites, usage: r.usageMetadata, model };
    } catch (e) { lastErr = e; }
  }
  throw lastErr;
}

(async () => {
  const [cmd, ...rest] = process.argv.slice(2);
  if (!KEY) { console.error(R('\nLIPSA GOOGLE_AI_STUDIO_FREE_TIER_KEY. Adaug-o in secret manager.\n')); process.exit(2); }

  if (cmd === 'init') {
    console.log(B('\n=== CREARE FILE SEARCH STORE ===\n'));
    const s = await initStore(rest[0] || 'MavisCloud-Store');
    console.log(D(`\n  next: node mavis-tools/gemini-filestore.js add ${s} <fisier>\n`));
  } else if (cmd === 'list') {
    await listStores();
  } else if (cmd === 'add') {
    console.log(B('\n=== INCARCARE SURSA (local) ===\n'));
    await addLocalFile(rest[0], rest[1], rest[2]);
  } else if (cmd === 'fromdrive') {
    console.log(B('\n=== INCARCARE SURSA (Drive) ===\n'));
    await addDriveFile(rest[0], rest[1], rest[2]);
  } else if (cmd === 'fromfolder') {
    const [store, folderId, ...opts] = rest;
    const recursive = !opts.includes('--flat');   // recursiv implicit
    console.log(B(`\n=== INGESTIE FOLDER DRIVE → FILE SEARCH ===\n`));
    // Aduna recursiv folderele (implicit), ca memoria sa fie completa.
    const collected = [];
    const walk = async (id, depth) => {
      const files = await kit.req('GET',
        `https://www.googleapis.com/drive/v3/files?q=${encodeURIComponent(`'${id}' in parents and trashed=false`)}` +
        `&fields=files(id,name,mimeType,size)&pageSize=200`);
      for (const f of files.files || []) {
        if (f.mimeType === 'application/vnd.google-apps.folder') {
          if (recursive || depth === 0) await walk(f.id, depth + 1);
        } else collected.push(f);
      }
    };
    await walk(folderId, 0);
    const seen = new Set();
    const docs = collected.filter((f) => { if (seen.has(f.id)) return false; seen.add(f.id); return true; });
    console.log(D(`  ${docs.length} documente de ingestat`));
    let n = 0;
    for (const f of docs) {
      try {
        await addDriveFile(store, f.id, f.name);
        n++;
      } catch (e) { console.log(R(`  FAIL ${f.name}: ${String(e.message).slice(0, 90)}`)); }
    }
    console.log(G(`\n  ${n}/${docs.length} documente ingestate`));
  } else if (cmd === 'ask') {
    const [store, ...q] = rest;
    console.log(B('\n=== ÎNTREBARE (File Search + citări) ===\n'));
    const r = await ask(store, q.join(' '));
    console.log(r.text);
    console.log(D(`\n  model: ${r.model}`));
    if (r.cites.length) {
      console.log(B(`\n  SURSE CITATE (${r.cites.length}):`));
      const seen = new Set();
      r.cites.forEach((c, i) => {
        const k = c.sursa + '|' + c.text.slice(0, 40);
        if (seen.has(k)) return; seen.add(k);
        console.log(`   ${i + 1}. ${c.sursa}`);
        if (c.text) console.log(D(`      „${c.text.slice(0, 220).replace(/\r?\n/g, ' ')}"`));
      });
    } else console.log(D('\n  (fără citări)'));
    if (r.usage) console.log(D(`\n  tokens: ${r.usage.totalTokenCount || '?'}`));
    console.log();
  } else if (cmd === 'delete') {
    await api('DELETE', `${BASE}/${rest[0]}`);
    console.log(G(`  store sters: ${rest[0]}`));
  } else {
    console.log(B('\n Uzura:\n  list | init "Nume" | add <store> <fisier> [nume] | fromdrive <store> <driveId> [nume]\n  fromfolder <store> <folderId> [--flat] | ask <store> "<intrebare>" | delete <store>\n'));
  }
  process.exit(0);
})().catch((e) => { console.error(R('\nFAIL: ' + e.message + '\n')); process.exit(1); });
