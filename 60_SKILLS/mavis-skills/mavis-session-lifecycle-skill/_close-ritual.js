#!/usr/bin/env node
/**
 * RITUAL DE INCHIDERE DE SESIUNE — C6
 * C:\Users\apviz\QWEN_BACKUP\_close-ritual.js
 *
 * Nu citeste din note. Masoara. Daca un fapt nu poate fi masurat, verdictul este
 * NU GATA — nu GATA CU REZERVE. Un ritual care nu poate spune "nu" e decor.
 *
 * Regula: nicio stare nu este raportata ca rezolvata pe baza unei supozitii.
 */
'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');

const QS   = process.env.RITUAL_QS   || 'C:\\Users\\apviz\\AI_Tools\\qwen-system';
const HB   = process.env.RITUAL_ROOT || 'C:\\Users\\apviz\\QWEN_BACKUP';

const out = [];
const say = (s) => { out.push(s); console.log(s); };
const checks = [];
const record = (id, ok, verdict, why) => checks.push({ id, ok, verdict, why });

// ── helper: citeste un log de certificare si cere verdictul din el ───────────
function readCert(dir) {
  const files = fs.readdirSync(dir)
    .filter(f => /^tcv_cert_.*\.log$/.test(f))
    .map(f => ({ f, m: fs.statSync(path.join(dir, f)).mtimeMs }))
    .sort((a, b) => b.m - a.m);
  if (!files.length) return null;
  const p = path.join(dir, files[0].f);
  const txt = fs.readFileSync(p, 'utf8');
  // \D* nu \s+ : masurat, logul scrie "CERTIFIED — 11/11" cu o linie de em-dash
  // intre cuvant si cifre. Un regex prea strict a citit un log CERTIFIED drept
  // "NU certificat". Un fals pozitiv e cel mai scump defect al unei masuratori —
  // opreste munca pe ceva care e gata, si pare zel.
  const cert = /CERTIFIED\D*(\d+)\s*\/\s*(\d+)/.exec(txt);
  const pass = /pass\s*=\s*(\d+)/i.exec(txt);
  const fail = /fail\s*=\s*(\d+)/i.exec(txt);
  const unk  = /unknown\s*=\s*(\d+)/i.exec(txt);
  return {
    file: files[0].f,
    certified: !!cert,
    ratio: cert ? `${cert[1]}/${cert[2]}` : null,
    pass: pass ? +pass[1] : null,
    fail: fail ? +fail[1] : null,
    unknown: unk ? +unk[1] : null,
  };
}

// ── 1. CERTIFICAREA ─────────────────────────────────────────────────────────
const cert = readCert(HB);
if (!cert) {
  record('C1', false, 'UNKNOWN', 'niciun log de certificare in QWEN_BACKUP');
  say('[ ] C1 certificare : UNKNOWN — niciun log gasit');
} else if (!cert.certified) {
  record('C1', false, 'FAIL', `${cert.file} — NU certificat`);
  say(`[ ] C1 certificare : FAIL — ${cert.file}`);
} else if (cert.unknown !== 0) {
  record('C1', false, 'UNKNOWN', `unknown=${cert.unknown} blocheaza certificarea`);
  say(`[ ] C1 certificare : UNKNOWN=${cert.unknown} — blocant`);
} else if (cert.fail !== 0) {
  record('C1', false, 'FAIL', `fail=${cert.fail}`);
  say(`[ ] C1 certificare : FAIL=${cert.fail} — blocant`);
} else {
  record('C1', true, 'PASS', `${cert.ratio}, fail=0 unknown=0 — ${cert.file}`);
  say(`[x] C1 certificare : ${cert.ratio}  fail=0 unknown=0`);
}

// ── 2. UN SINGUR GUARDRAIL ─────────────────────────────────────────────────
function nodeProcs(filter) {
  let outp = '';
  try {
    outp = execFileSync('powershell.exe', ['-NoProfile', '-Command',
      "Get-CimInstance Win32_Process -Filter \"Name='node.exe'\" | ForEach-Object { \"$($_.ProcessId)|$($_.CommandLine)\" }"
    ], { encoding: 'utf8' });
  } catch { return null; }
  return outp.split(/\r?\n/).filter(Boolean)
    .map(l => { const i = l.indexOf('|'); return { pid: l.slice(0, i), cmd: l.slice(i + 1) }; })
    .filter(p => filter.test(p.cmd));
}
const guards = nodeProcs(/guardrail\.js/i) || [];
const sups   = nodeProcs(/supervisor\.js/i) || [];
if (guards.length === 1) {
  record('C2', true, 'PASS', `un singur guardrail, pid ${guards[0].pid}`);
  say(`[x] C2 guardrail  : UN SINGUR (pid ${guards[0].pid})`);
} else {
  record('C2', false, 'FAIL', `${guards.length} guardrail`);
  say(`[ ] C2 guardrail  : ${guards.length} procese — ${guards.length === 0 ? 'nu ruleaza' : 'split-brain'}`);
}
say(`    supervizori  : ${sups.length}`);

// ── 3. VERSIONARE — nimic necomitat ────────────────────────────────────────
function gitDirty(dir) {
  try {
    const o = execFileSync('git', ['-C', dir, 'status', '--porcelain'],
      { encoding: 'utf8' });
    return o.split(/\r?\n/).filter(Boolean);
  } catch { return null; }
}
for (const [name, dir] of [['qwen-system', QS], ['QWEN_BACKUP', HB]]) {
  const d = gitDirty(dir);
  if (d === null) { record(`C3.${name}`, false, 'UNKNOWN', 'git indisponibil'); say(`[ ] C3 ${name}: UNKNOWN`); }
  else if (d.length === 0) { record(`C3.${name}`, true, 'PASS', 'curat'); say(`[x] C3 ${name}: curat`); }
  else { record(`C3.${name}`, false, 'DIRTY', `${d.length} necomitate`); say(`[ ] C3 ${name}: ${d.length} necomitate`); }
}

// ── 4. POARTA DE COMMIT (LiveReview) ───────────────────────────────────────
for (const [name, dir] of [['qwen-system', QS], ['QWEN_BACKUP', HB]]) {
  const sentinel = path.join(dir, '.git', 'lrc', 'disabled');
  if (fs.existsSync(sentinel)) {
    record(`C4.${name}`, false, 'DEGRADED', 'poarta LiveReview e scoasa de pe acest repo');
    say(`[ ] C4 poarta ${name}: DEGRADAT — lrc dezactivat`);
  } else {
    record(`C4.${name}`, true, 'PASS', 'poarta activa');
    say(`[x] C4 poarta ${name}: activa`);
  }
}

// ── 5. JURALE — trunchiere exacta sau rupta ────────────────────────────────
for (const f of ['guardrail.jsonl', 'supervisor.jsonl']) {
  const p = path.join(QS, 'logs', f);
  if (!fs.existsSync(p)) { record(`C5.${f}`, false, 'MISSING', 'jurnal absent'); say(`[ ] C5 ${f}: LIPSA`); continue; }
  const lines = fs.readFileSync(p, 'utf8').split(/\r?\n/).filter(Boolean);
  let broken = 0;
  for (const l of lines) { try { JSON.parse(l); } catch { broken++; } }
  if (broken === 0) {
    record(`C5.${f}`, true, 'PASS', `${lines.length} linii, toate JSON valide`);
    say(`[x] C5 ${f}: ${lines.length} linii, zero rupturi`);
  } else {
    record(`C5.${f}`, false, 'FAIL', `${broken} linii JSON rupte`);
    say(`[ ] C5 ${f}: ${broken} linii RUPTE`);
  }
}

// ── VERDICT ────────────────────────────────────────────────────────────────
const blocking = checks.filter(c => !c.ok);
say('');
say('='.repeat(72));
if (blocking.length === 0) {
  say('VERDICT: GATA — toate verificarile au trecut, fiecare masurat.');
} else {
  say(`VERDICT: NU GATA — ${blocking.length} verificari blocate:`);
  for (const b of blocking) say(`        - ${b.id}: ${b.verdict} (${b.why})`);
}
say('='.repeat(72));
say('');
say('NOTA: GATA inseamna "poate fi predat". NU inseamna "nu mai exista nimic');
say('de facut". Un item poate fi inchis ca "nu e o problema" — caz in care');
say('ritualul il trateaza la fel de bine, pentru ca masura, nu presupune.');

// Raportul NU se scrie in arborele repo-urilor. Masurat: scriindu-l in QWEN_BACKUP,
// procedura isi face propriul repo dirty si nu poate raporta NICIODATA "curat" dupa
// prima rulare. O masuratorie care se modifica singura nu masoara nimic.
const REPORT = process.env.RITUAL_REPORT
  || path.join(os.tmpdir(), 'qwen-close-ritual-last.txt');

try {
  fs.mkdirSync(path.dirname(REPORT), { recursive: true });
  fs.writeFileSync(REPORT, out.join('\n') + '\n', 'utf8');
  say('');
  say(`raport: ${REPORT}`);
} catch (e) {
  say('');
  say(`raport NESCris (${e.message}) — verdictul de mai sus este valabil oricum`);
}
process.exit(blocking.length === 0 ? 0 : 2);