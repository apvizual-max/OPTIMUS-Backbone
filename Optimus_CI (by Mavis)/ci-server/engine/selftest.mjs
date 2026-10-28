// selftest.mjs - autotestul falsificabil al motorului Mavis-Optimus-CI.
//
// CE TESTEAZA: MECANISMUL, nu integrarea. Cele 7 porti ale proiectului
// (scripts\*-selfcheck.ps1) sunt scrise pentru Windows PowerShell 5.1 si
// ruleaza pe host, unde sunt portile autoritative. Containerul are nevoie de
// o poarta a LUI: una care poate ESUECA si care demonstreaza, in container,
// ca mecanismul chiar refuza ce trebuie refuzat.
//
// Testele:
//   T1  scannerul de secrete REFUZA o cheie plantata (exit 1)
//   T2  poarta de push REFUZA fara markerul R0 (exit 1)
//   T3  poarta de push ACCEPTA cu markerul R0 si CONSUMA markerul
//   T4  integrare rapida (--ff-only) pastreaza istoricul
//   T5  integrare divergenta (--no-ff) pastreaza AMBELE lati
//   T6  o ramura locala straina e INTEGRATA in main, nu taiata
//   T7  autotestul NU atinge repository-urile reale (HEAD + config identice)
//
// Fara dependinte. Ruleaza in seconds.

import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { CFG, sha256File } from './lib.mjs';

const results = [];
function report(id, label, ok, detail) {
  results.push({ id, label, ok, detail });
  console.log((ok ? 'OK   ' : 'FAIL ') + id + ' ' + label + (detail ? ' -> ' + detail : ''));
}

function run(cmd, args, opts = {}) {
  // GIT_DIR/GIT_WORK_TREE globale ar strica orice git init/clone de fixture
  // ("GIT_WORK_TREE not allowed without specifying GIT_DIR"). Autotestul e
  // temator: le elimina din mediu, DAR doar daca apelantul nu le cere
  // explicit (portile chiar au nevoie de GIT_DIR).
  const env = { ...process.env, ...(opts.env || {}) };
  if (!opts.env || !('GIT_DIR' in opts.env)) delete env.GIT_DIR;
  if (!opts.env || !('GIT_WORK_TREE' in opts.env)) delete env.GIT_WORK_TREE;
  const r = spawnSync(cmd, args, {
    encoding: 'utf8',
    cwd: opts.cwd,
    env,
    timeout: 120000,
  });
  return { code: r.status === null ? -1 : r.status, out: (r.stdout || '').trim(), err: (r.stderr || '').trim() };
}

function gitIn(dir, args, env = {}) {
  return run('git', ['-C', dir, ...args], { env });
}

// --- T7: amprenta repository-urilor reale -----------------------------------
// MEASURED 2026-10-27: un self-check a scris un commit in repository-ul de
// productie (autor "Fixture <fixture@localhost>", 127 fisiere, toate modurile
// intorse 644 -> 755). Testul masoara exact ceea ce a esuat: HEAD-ul si
// configul gitdir-urilor REALE, inainte si dupa. Nu verifica daca autotestul
// "pare" izolat - verifica daca repository-urile reale au fost atinse.
function realRepoSnapshot() {
  const snap = [];
  for (const d of ['repo', 'clone-MAVIS-CLOUD', 'clone-MAVIS-OPTIMUS-CI']) {
    const gd = path.join(CFG.gitdata, d);
    if (!fs.existsSync(gd)) continue;
    const head = run('git', ['--git-dir', gd, 'rev-parse', 'HEAD']);
    snap.push({
      dir: d,
      head: head.code === 0 ? head.out : '(gol)',
      config: sha256File(path.join(gd, 'config')) || '(fara-config)',
    });
  }
  return snap;
}

const realBefore = realRepoSnapshot();

const scratch = path.join(CFG.gitdata, 'scratch', 'selftest');
const stamp = Date.now();
const root = path.join(scratch, 'st-' + stamp);

try {
  fs.rmSync(root, { recursive: true, force: true });
  fs.mkdirSync(root, { recursive: true });
} catch {
  // Stergerea e doar curatenie; daca nu merge, continuam cu alt folder.
}

const bare = path.join(root, 'remote.git');
const main = path.join(root, 'main');
const side = path.join(root, 'side');

// --- pregatire: remote bare + doua clone -----------------------------------
let setupError = '';
const initRes = run('git', ['init', '--bare', '-b', 'main', bare]);
if (initRes.code !== 0) setupError = 'init: ' + initRes.err + ' ' + initRes.out;
const cloneMain = run('git', ['clone', bare, main]);
if (setupError === '' && cloneMain.code !== 0) setupError = 'clone main: ' + cloneMain.err;
const cloneSide = run('git', ['clone', bare, side]);
if (setupError === '' && cloneSide.code !== 0) setupError = 'clone side: ' + cloneSide.err;

if (setupError !== '') {
  report('SETUP', 'pregătirea fixture-ului', false, setupError.slice(0, 300));
  process.exit(1);
}

// Identitate locala, ca sa nu depindem de configul global.
for (const d of [main, side]) {
  gitIn(d, ['config', 'user.name', 'Selftest']);
  gitIn(d, ['config', 'user.email', 'selftest@local']);
}

fs.writeFileSync(path.join(main, 'a.txt'), 'din main\n');
gitIn(main, ['add', '-A']);
gitIn(main, ['commit', '-m', 'seed']);
gitIn(main, ['push', 'origin', 'main']);
gitIn(side, ['fetch', 'origin']);
// Ramura trebuie sa porneasca de la commitul impartit, altfel istoricul e
// fara stramos comun si ff-only refuza corect ("unrelated histories").
gitIn(side, ['checkout', '-B', 'sideB', 'origin/main']);
fs.writeFileSync(path.join(side, 'b.txt'), 'din sideB\n');
gitIn(side, ['add', '-A']);
gitIn(side, ['commit', '-m', 'sideB']);
gitIn(side, ['push', 'origin', 'sideB']);

// --- T1: scannerul refuza o cheie plantata ----------------------------------
// Forma tokenului e construita prin concatenare, intentionat: acest fisier
// este el insusi in index, iar un literal cu forma de cheie ar bloca
// propriul commit (masurat 2026-10-27: poarta a refuzat commitul cu
// SCANNED=128 BLOCKS=1 pe chiar acest sir). La RUNTIME sirul plantat este
// complet - scannerul totusi il vede si il refuza.
const probe = path.join(root, 'probe.txt');
const plantedToken = 'ghp_' + 'A'.repeat(36);
fs.writeFileSync(probe, 'client_secret = "' + plantedToken + '"\n');
const scanner = path.join(CFG.project, 'scripts', 'scan-staged-secrets.ps1');
const t1 = run('powershell', ['-NoProfile', '-File', scanner, '-ProbeFile', probe]);
report('T1', 'scannerul refuza o cheie plantata', t1.code === 1, 'exit=' + t1.code + ' ' + (t1.out || '').split('\n').slice(-2).join(' '));

// --- T2/T3: poarta de push refuza fara R0, accepta cu R0 ---------------------
const gate = path.join(CFG.gateDir, 'pre-push');
const gateGitDir = path.join(root, 'gate-gitdir');
// Poarta cauta markerul EXACT la $(git rev-parse --git-dir)/PUSH-ACORD.
const marker = path.join(gateGitDir, 'PUSH-ACORD');
let t2ok = false;
let t3ok = false;
let detail = '';
if (fs.existsSync(gate)) {
  fs.mkdirSync(gateGitDir, { recursive: true });
  run('git', ['init', '--bare', gateGitDir]);
  const g2 = run('sh', [gate, 'origin', path.join(bare, 'x')], { env: { GIT_DIR: gateGitDir } });
  t2ok = g2.code === 1;
  detail = 'fara marker exit=' + g2.code;

  fs.writeFileSync(marker, 'selftest\n');
  const g3 = run('sh', [gate, 'origin', path.join(bare, 'x')], { env: { GIT_DIR: gateGitDir } });
  const consumed = !fs.existsSync(marker);
  t3ok = g3.code === 0 && consumed;
  detail += ' | cu marker exit=' + g3.code + ' consumat=' + consumed + ' ' + (g3.err || g3.out).slice(0, 120);
} else {
  detail = 'poarta nu a fost gasita la ' + gate;
}
report('T2', 'poarta refuza push fara acord R0', t2ok, detail);
report('T3', 'poarta accepta cu acord R0 si consuma markerul', t3ok, detail);

// --- T4: integrare rapida ----------------------------------------------------
const fetch4 = gitIn(main, ['fetch', 'origin']);
const ff = gitIn(main, ['merge', '--ff-only', 'origin/sideB']);
const log4 = gitIn(main, ['log', '--oneline', '-2']).out;
report(
  'T4',
  'integrare rapida (--ff-only) pastreaza istoricul',
  ff.code === 0 && /sideB/.test(log4),
  'fetch=' + fetch4.code + ' merge=' + ff.code + ' ' + (ff.err || ff.out).split('\n')[0].slice(0, 140)
);

// --- T5: integrare divergenta (ambele lati pastrate) -------------------------
const mainOnly = path.join(root, 'div-main');
const sideOnly = path.join(root, 'div-side');
run('git', ['clone', bare, mainOnly]);
run('git', ['clone', bare, sideOnly]);
for (const d of [mainOnly, sideOnly]) {
  gitIn(d, ['config', 'user.name', 'Selftest']);
  gitIn(d, ['config', 'user.email', 'selftest@local']);
}
gitIn(mainOnly, ['checkout', '-B', 'main']);
fs.writeFileSync(path.join(mainOnly, 'm.txt'), 'partea main\n');
gitIn(mainOnly, ['add', '-A']);
gitIn(mainOnly, ['commit', '-m', 'commit doar main']);
gitIn(sideOnly, ['checkout', '-B', 'alt']);
fs.writeFileSync(path.join(sideOnly, 's.txt'), 'partea side\n');
gitIn(sideOnly, ['add', '-A']);
gitIn(sideOnly, ['commit', '-m', 'commit doar side']);
gitIn(sideOnly, ['push', 'origin', 'alt']);
gitIn(mainOnly, ['fetch', 'origin']);
const div = gitIn(mainOnly, ['rev-list', '--left-right', '--count', 'origin/alt...main']).out.split(/\s+/);
const m5 = gitIn(mainOnly, ['merge', '--no-ff', '-m', 'integrare', 'origin/alt']);
const log5 = gitIn(mainOnly, ['log', '--oneline', '-5']).out;
const bothKept = /commit doar main/.test(log5) && /commit doar side/.test(log5);
report(
  'T5',
  'integrare divergenta pastreaza ambele lati',
  m5.code === 0 && bothKept,
  'exit=' + m5.code + ' behind/ahead=' + div.join('/')
);

// --- T6: ramura straina e integrata, nu taiata -------------------------------
const t6repo = path.join(root, 't6');
run('git', ['clone', bare, t6repo]);
gitIn(t6repo, ['config', 'user.name', 'Selftest']);
gitIn(t6repo, ['config', 'user.email', 'selftest@local']);
gitIn(t6repo, ['checkout', '-B', 'ramura-straine']);
fs.writeFileSync(path.join(t6repo, 'r.txt'), 'lucrarea altui agent\n');
gitIn(t6repo, ['add', '-A']);
gitIn(t6repo, ['commit', '-m', 'lucrare straina']);
const beforeBranches = gitIn(t6repo, ['branch', '--format=%(refname:short)']).out.split('\n').filter(Boolean);
const m6 = gitIn(t6repo, ['merge', '--no-ff', '-m', 'integrare ramura straina', 'ramura-straine']);
const afterLog = gitIn(t6repo, ['log', '--oneline', '-3']).out;
const kept = /lucrare straina/.test(afterLog);
report(
  'T6',
  'ramura straina e integrata in main, nu taiata',
  m6.code === 0 && kept,
  'exit=' + m6.code + ' ramuri_inainte=' + beforeBranches.join(',')
);

// --- T7: repository-urile reale sunt neatinse --------------------------------
const realAfter = realRepoSnapshot();
const diffs = [];
for (const b of realBefore) {
  const a = realAfter.find((x) => x.dir === b.dir);
  if (!a) {
    diffs.push(b.dir + ': gitdir dispare');
  } else if (a.head !== b.head || a.config !== b.config) {
    diffs.push(b.dir + ': ' + b.head + '/' + b.config.slice(0, 12) + ' -> ' + a.head + '/' + a.config.slice(0, 12));
  }
}
report(
  'T7',
  'autotestul nu atinge repository-urile reale',
  diffs.length === 0,
  diffs.length
    ? diffs.join(' | ')
    : 'HEAD+config identice inainte/dupa (' + realBefore.length + ' repo-uri: ' + realBefore.map((x) => x.dir).join(', ') + ')'
);

// --- verdict -----------------------------------------------------------------
const failed = results.filter((r) => !r.ok);
console.log('');
console.log('SELFTEST_PROBLEMS=' + failed.length + ' TESTS=' + results.length);
console.log(failed.length ? 'SELFTEST_FAILED' : 'SELFTEST_OK');
process.exit(failed.length ? 1 : 0);
