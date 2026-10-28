// lib.mjs - primitive si logica comuna a motorului Mavis-Optimus-CI.
//
// Fara dependinte: doar stdlib Node. Containerul ramane mic, iar motorul
// continua sa functioneze peste ani, fara npm install.
//
// REGULA DE AUR A MECHANISMULUI: instrumentul masoara, nu presupune.
// Un check care nu poate rula se raporteaza SKIPPED/UNKNOWN, niciodata GREEN.

import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

const gitdata = process.env.CI_GITDATA_DIR || '/workspace/gitdata';
const project = process.env.CI_PROJECT_DIR || '/workspace/project';
const secrets = process.env.CI_SECRETS_DIR || '/secrets';

export const CFG = {
  project,
  gitdata,
  secrets,
  gaData: process.env.CI_GA_DATA_DIR || '/ga-data',
  gateDir: process.env.CI_GATE_DIR || '/workspace/gate',
  evidence: process.env.CI_EVIDENCE_DIR || path.join(gitdata, 'evidence'),
  apiPort: Number(process.env.CI_API_PORT || 8790),
  owner: process.env.CI_GH_OWNER || 'apvizual-max',
  tokenFile: process.env.CI_TOKEN_FILE || path.join(secrets, 'github-token-apvizual-max.txt'),
  version: '1.0.0',
};

// Cele doua repo-uri administrate de Popy la nivel de arhitectura, plus
// clona din cloud-ingest. Fiecare are: gitdir (in folderul de gitdata) si
// worktree (in proiect).
export const REPOS = [
  {
    id: 'ci',
    label: 'MAVIS-OPTIMUS-CI',
    remote: 'MAVIS-OPTIMUS-CI',
    gitdir: 'repo',
    worktree: project,
    hooks: 'repo/hooks',
    role: 'repo-ul sistemului',
  },
  {
    id: 'cloud',
    label: 'MAVIS-CLOUD',
    remote: 'MAVIS-CLOUD',
    gitdir: 'clone-MAVIS-CLOUD',
    worktree: path.join(project, 'cloud-ingest', 'MAVIS-CLOUD'),
    hooks: 'clone-MAVIS-CLOUD/hooks',
    role: 'instanta Mavis Cloud',
  },
  {
    id: 'ciclone',
    label: 'MAVIS-OPTIMUS-CI (cloud-ingest)',
    remote: 'MAVIS-OPTIMUS-CI',
    gitdir: 'clone-MAVIS-OPTIMUS-CI',
    worktree: path.join(project, 'cloud-ingest', 'MAVIS-OPTIMUS-CI'),
    hooks: 'clone-MAVIS-OPTIMUS-CI/hooks',
    role: 'clona canalului secundar',
  },
];

export function repoById(id) {
  const r = REPOS.find((x) => x.id === id);
  if (!r) throw new Error('repo necunoscut: ' + id);
  return r;
}

// --- primitivele -----------------------------------------------------------

export function run(cmd, args, opts = {}) {
  const r = spawnSync(cmd, args, {
    encoding: 'utf8',
    cwd: opts.cwd,
    env: { ...process.env, ...(opts.env || {}) },
    maxBuffer: 64 * 1024 * 1024,
    timeout: opts.timeout || 300000,
  });
  return {
    code: r.status === null ? -1 : r.status,
    out: (r.stdout || '').trim(),
    err: (r.stderr || '').trim(),
  };
}

// Git cu --git-dir/--work-tree explicite: in container pointerul .git din
// proiect contine o cale Windows (E:/...), pe care git linux nu o poate
// rezolva. Disciplina asta face ca motorul sa nu depinda de pointer.
export function git(repo, args, opts = {}) {
  const gitdir = path.join(CFG.gitdata, repo.gitdir);
  const hooks = path.join(CFG.gitdata, repo.hooks);
  const base = ['--git-dir', gitdir, '--work-tree', repo.worktree];
  const cfg = fs.existsSync(hooks) ? ['-c', 'core.hooksPath=' + hooks] : [];
  const env = {
    GIT_DIR: gitdir,
    GIT_WORK_TREE: repo.worktree,
    GIT_AUTHOR_NAME: process.env.CI_GIT_NAME || 'Mavis Optimus CI',
    GIT_AUTHOR_EMAIL: process.env.CI_GIT_EMAIL || 'mavis-ci@local',
    GIT_COMMITTER_NAME: process.env.CI_GIT_NAME || 'Mavis Optimus CI',
    GIT_COMMITTER_EMAIL: process.env.CI_GIT_EMAIL || 'mavis-ci@local',
    ...(opts.env || {}),
  };
  // Tokenul GitHub intra prin header, nu prin URL si nu in loguri.
  const auth = gitAuthArgs();
  return run('git', [...base, ...cfg, ...auth, ...args], { ...opts, env });
}

// -c http.extraheader pentru acces la GitHub: tokenul nu ajunge nici in
// URL, nici in reflog, nici in logurile motorului.
export function gitAuthArgs() {
  const t = readToken();
  if (!t) return [];
  const basic = Buffer.from('x-access-token:' + t, 'utf8').toString('base64');
  return ['-c', 'http.extraheader=Authorization: Basic ' + basic];
}

export function gitLines(repo, args, opts = {}) {
  const r = git(repo, args, opts);
  return r.out.split('\n').map((s) => s.trim()).filter(Boolean);
}

// Valoarea unei chei din configul gitdir-ului. O cheie ABSENTA inseamna ''
// (git config --get iese cu cod 1), nu o valoare inventata: un instrument
// care masoara trebuie sa distinga "absent" de "setat pe false".
export function gitConfigValue(repo, key) {
  const r = git(repo, ['config', '--get', key]);
  if (r.code !== 0) return '';
  return r.out.trim();
}

export function readToken() {
  try {
    const t = fs.readFileSync(CFG.tokenFile, 'utf8').trim();
    return t.length > 0 ? t : null;
  } catch {
    return null;
  }
}

export function hasToken() {
  return readToken() !== null;
}

// Tokenul GitHub ca header pentru git: nu se scrie in niciun fisier,
// nu apare in loguri, nu se tipareste.
export function gitAuthEnv() {
  const t = readToken();
  if (!t) return {};
  const basic = Buffer.from('x-access-token:' + t, 'utf8').toString('base64');
  return {
    GIT_TERMINAL_PROMPT: '0',
    GIT_CONFIG_COUNT: '1',
    GIT_CONFIG_KEY_0: 'http.extraheader',
    GIT_CONFIG_VALUE_0: 'Authorization: Basic ' + basic,
  };
}

// --- GitHub API -------------------------------------------------------------

export async function gh(pathname) {
  const token = readToken();
  if (!token) return { ok: false, status: 0, error: 'NO_TOKEN', body: [] };
  try {
    const res = await fetch('https://api.github.com' + pathname, {
      headers: {
        Authorization: 'Bearer ' + token,
        Accept: 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'User-Agent': 'Mavis-Optimus-CI',
      },
    });
    if (res.status === 404) return { ok: true, status: 404, body: [] };
    const body = await res.json();
    if (!res.ok) {
      return { ok: false, status: res.status, error: 'HTTP_' + res.status, body: [] };
    }
    return { ok: true, status: res.status, body: Array.isArray(body) ? body : [body] };
  } catch (e) {
    return { ok: false, status: 0, error: String(e && e.message ? e.message : e), body: [] };
  }
}

// --- evidenta ---------------------------------------------------------------

export function evidence(action, detail) {
  const rec = { ts: new Date().toISOString(), action, detail: detail || {} };
  try {
    fs.mkdirSync(CFG.evidence, { recursive: true });
    fs.appendFileSync(
      path.join(CFG.evidence, 'ci-ledger.jsonl'),
      JSON.stringify(rec) + '\n'
    );
    fs.appendFileSync(
      path.join(CFG.evidence, 'ci-ledger.log'),
      '[' + rec.ts + '] ' + action + ' ' + JSON.stringify(detail || {}) + '\n'
    );
  } catch {
    // Evidenta nu poate bloca munca: daca discul nu scrie, munca merge,
    // dar raportul o spune explicit.
    rec.evidence_write_failed = true;
  }
  return rec;
}

export function evidenceTail(n = 50) {
  const f = path.join(CFG.evidence, 'ci-ledger.jsonl');
  try {
    const lines = fs.readFileSync(f, 'utf8').split('\n').filter(Boolean);
    return lines.slice(-n).map((l) => {
      try {
        return JSON.parse(l);
      } catch {
        return { raw: l };
      }
    });
  } catch {
    return [];
  }
}

// --- utilitare --------------------------------------------------------------

export function exists(p) {
  try {
    fs.accessSync(p);
    return true;
  } catch {
    return false;
  }
}

export function isDir(p) {
  try {
    return fs.statSync(p).isDirectory();
  } catch {
    return false;
  }
}

export function sha256File(p) {
  try {
    return createHash('sha256').update(fs.readFileSync(p)).digest('hex');
  } catch {
    return null;
  }
}
