// engine.mjs - motorul Mavis-Optimus-CI.
//
// CE FACE, IN ORDINE (regulile lui Popy, 2026-10-27):
//
//   1. PRE-FLIGHT (plan): GitHub trebuie sa fie CURAT si UNITAR. Exact o
//      ramura (main), zero pull request-uri deschise. Daca nu e asa, motorul
//      NU sincronizeaza si NU impinge: raporteaza BLOCKED cu motivele exacte.
//      ("DACA pe github sunt mai multe branchuri ... NU FACI PROCESUL DELOC
//      si raportezi: TREBUIE CURATAT GITHUB si adus la NUMITOR COMUN".)
//
//   2. SYNC (autonom, local): fetch, fast-forward sau merge --no-ff (niciodata
//      rebase, niciodata reset, niciodata discard), commit automat, totul pe
//      main. Nimic nu se taie: ramurile locale ale altor agenti se INTEGREAZA
//      in main, nu se sterg.
//
//   3. PUSH (doar cu R0): se intampla doar daca planul este READY si exista
//      markerul PUSH-ACORD in gitdir. Markerul e singurul acord al lui Popy.
//
//   4. EVIDENTA: tot ce s-a facut se scrie in ledger, ca orice AI sa poata
//      prelua containerul dupa un an fara sa cunoasca istoricul.

import {
  CFG,
  REPOS,
  repoById,
  git,
  gitLines,
  gitConfigValue,
  gh,
  evidence,
  evidenceTail,
  exists,
  isDir,
  run,
  sha256File,
} from './lib.mjs';
import path from 'node:path';
import fs from 'node:fs';

// --- starea unui repo -------------------------------------------------------

export function statusRepo(repo) {
  const head = git(repo, ['rev-parse', 'HEAD']);
  const server = git(repo, ['ls-remote', 'origin', 'refs/heads/main']);
  const serverSha = server.out ? server.out.split(/\s+/)[0] : null;
  const div = git(repo, ['rev-list', '--left-right', '--count', 'origin/main...main']);
  const parts = div.out.split(/\s+/);
  const dirty = gitLines(repo, ['status', '--porcelain']);
  const localBranches = gitLines(repo, ['branch', '--format=%(refname:short)']);
  const remoteHeads = gitLines(repo, ['ls-remote', '--heads', 'origin']).map((l) => {
    const [sha, ref] = l.split(/\s+/);
    return { sha, name: ref.replace('refs/heads/', '') };
  });
  const marker = path.join(CFG.gitdata, repo.gitdir, 'PUSH-ACORD');
  return {
    id: repo.id,
    label: repo.label,
    role: repo.role,
    gitdir: path.join(CFG.gitdata, repo.gitdir),
    worktree: repo.worktree,
    head: head.out || null,
    server: serverSha,
    inSync: Boolean(head.out) && head.out === serverSha,
    behind: Number(parts[0] || 0),
    ahead: Number(parts[1] || 0),
    dirtyCount: dirty.length,
    dirtySample: dirty.slice(0, 8),
    localBranches,
    remoteBranches: remoteHeads.map((h) => h.name),
    r0MarkerPresent: exists(marker),
  };
}

export function statusAll() {
  return REPOS.map(statusRepo);
}

// --- 1. PRE-FLIGHT ----------------------------------------------------------

export async function planRepo(repo) {
  const blockers = [];
  const notes = [];

  // a) Remote: exact o ramura, main.
  const ls = git(repo, ['ls-remote', '--heads', 'origin']);
  if (ls.code !== 0) {
    blockers.push({
      code: 'REMOTE_UNREACHABLE',
      detail: (ls.err || ls.out || 'git ls-remote a esuat').slice(0, 300),
    });
  }
  const heads = ls.out
    .split('\n')
    .map((l) => l.trim())
    .filter(Boolean)
    .map((l) => {
      const [sha, ref] = l.split(/\s+/);
      return { sha, name: ref.replace('refs/heads/', '') };
    });
  const extra = heads.filter((h) => h.name !== 'main');
  if (!heads.some((h) => h.name === 'main')) {
    blockers.push({ code: 'REMOTE_NO_MAIN', detail: heads.map((h) => h.name).join(', ') || 'niciuna' });
  }
  if (extra.length) {
    blockers.push({
      code: 'REMOTE_EXTRA_BRANCHES',
      detail: extra.map((h) => h.name).join(', '),
      hint: 'GitHub trebuie adus la un singur branch (main) inainte de orice proces.',
    });
  }

  // b) Pull request-uri deschise: trebuie zero.
  const prs = await gh('/repos/' + CFG.owner + '/' + repo.remote + '/pulls?state=open&per_page=100');
  if (!prs.ok) {
    blockers.push({
      code: 'PR_CHECK_UNKNOWN',
      detail: prs.error,
      hint: 'Un check care nu poate rula nu e verde: e necunoscut. Nu se presupune.',
    });
  } else if (prs.body.length) {
    blockers.push({
      code: 'OPEN_PULL_REQUESTS',
      detail: prs.body.map((p) => '#' + p.number).join(', '),
      hint: 'PR-urile trebuie rezolvate si aduse la main inainte de orice proces.',
    });
  }

  // c) Divergenta local/server (dupa fetch, ca sa fie reala).
  const fetch = git(repo, ['fetch', 'origin', 'main']);
  if (fetch.code !== 0) {
    blockers.push({ code: 'FETCH_FAILED', detail: (fetch.err || '').slice(0, 300) });
  }
  const div = git(repo, ['rev-list', '--left-right', '--count', 'origin/main...main']);
  const parts = div.out.split(/\s+/);
  const behind = Number(parts[0] || 0);
  const ahead = Number(parts[1] || 0);
  if (behind > 0 && ahead > 0) {
    notes.push({
      code: 'DIVERGED',
      detail: 'behind=' + behind + ' ahead=' + ahead,
      hint: 'Se rezolva prin merge --no-ff (ambele istorice pastrate), niciodata rebase.',
    });
  }

  // d) Ramuri locale in afara de main: se integraza, nu se sterg.
  const localBranches = gitLines(repo, ['branch', '--format=%(refname:short)']);
  const extraLocal = localBranches.filter((b) => b !== 'main');
  if (extraLocal.length) {
    notes.push({
      code: 'LOCAL_EXTRA_BRANCHES',
      detail: extraLocal.join(', '),
      hint: 'Se integraza in main la sync. Stergerea e distructiva: cere R0.',
    });
  }

  // e) Worktree murdar: se comite autonom, nu e blocaj.
  const dirty = gitLines(repo, ['status', '--porcelain']);
  if (dirty.length) {
    notes.push({ code: 'DIRTY_WORKTREE', detail: dirty.length + ' intrari', hint: 'Se comite autonom la sync.' });
  }

  return {
    repo: repo.id,
    label: repo.label,
    remote: repo.remote,
    remoteBranches: heads.map((h) => h.name),
    localBranches,
    behind,
    ahead,
    dirtyCount: dirty.length,
    openPullRequests: prs.ok ? prs.body.map((p) => ({ number: p.number, title: p.title })) : null,
    blockers,
    notes,
    verdict: blockers.length ? 'BLOCKED' : 'READY',
  };
}

export async function planAll() {
  const repos = [];
  for (const r of REPOS) repos.push(await planRepo(r));
  const blocked = repos.filter((r) => r.verdict === 'BLOCKED');
  const result = {
    ts: new Date().toISOString(),
    verdict: blocked.length ? 'BLOCKED' : 'READY',
    rule: 'Un singur branch (main), zero PR-uri deschise, repo-uri la numitor comun. Altfel: NU se face procesul.',
    repos,
    blockedRepos: blocked.map((r) => r.repo),
  };
  evidence('plan', { verdict: result.verdict, blocked: result.blockedRepos });
  return result;
}

// --- 2. SYNC (autonom, local) ------------------------------------------------

export function syncRepo(repo, opts = {}) {
  const steps = [];
  const before = git(repo, ['rev-parse', 'HEAD']).out;

  const fetch = git(repo, ['fetch', 'origin', 'main']);
  steps.push({ step: 'fetch', code: fetch.code, detail: fetch.err || 'ok' });
  if (fetch.code !== 0) {
    return { repo: repo.id, ok: false, steps, error: 'FETCH_FAILED' };
  }

  // a) Integrarea serverului: ff-only daca se poate, merge --no-ff daca nu.
  const div = git(repo, ['rev-list', '--left-right', '--count', 'origin/main...main']);
  const [behind, ahead] = div.out.split(/\s+/).map((n) => Number(n || 0));
  if (behind > 0 && ahead === 0) {
    const m = git(repo, ['merge', '--ff-only', 'origin/main']);
    steps.push({ step: 'merge-ff-only', code: m.code, detail: m.err || m.out });
    if (m.code !== 0) return { repo: repo.id, ok: false, steps, error: 'MERGE_FAILED' };
  } else if (behind > 0 && ahead > 0) {
    const m = git(repo, [
      'merge',
      '--no-ff',
      '-m',
      'ci: integra origin/main in main (autonom; ambele istorice pastrate)',
      'origin/main',
    ]);
    steps.push({ step: 'merge-no-ff', code: m.code, detail: m.err || m.out });
    if (m.code !== 0) {
      // Conflict: NU se rezolva automat, ca nimic sa nu se taie.
      git(repo, ['merge', '--abort']);
      return { repo: repo.id, ok: false, steps, error: 'MERGE_CONFLICT_ABORTED' };
    }
  } else {
    steps.push({ step: 'merge', code: 0, detail: 'nimic de integrat' });
  }

  // b) Ramuri locale ale altor agenti: se integraza in main. Nu se sterg.
  const localBranches = gitLines(repo, ['branch', '--format=%(refname:short)']);
  for (const b of localBranches) {
    if (b === 'main') continue;
    const m = git(repo, ['merge', '--no-ff', '-m', 'ci: integra ramura locala ' + b + ' in main', b]);
    steps.push({ step: 'merge-local:' + b, code: m.code, detail: m.err || 'ok' });
    if (m.code !== 0) {
      git(repo, ['merge', '--abort']);
      return { repo: repo.id, ok: false, steps, error: 'LOCAL_BRANCH_CONFLICT_ABORTED:' + b };
    }
  }

  // c) Commit autonom al lucrarii locale (poarta de secrete ruleaza prin hook).
  git(repo, ['add', '-A']);
  const staged = git(repo, ['diff', '--cached', '--name-only']);
  const stagedList = staged.out.split('\n').filter(Boolean);
  if (stagedList.length) {
    const msg =
      'ci: actualizare autonoma (' +
      stagedList.length +
      ' fisiere' +
      (stagedList[0] ? '; primul: ' + stagedList[0] : '') +
      ')';
    const c = git(repo, ['commit', '-m', msg]);
    steps.push({ step: 'commit', code: c.code, detail: c.err || c.out.slice(0, 400) });
    if (c.code !== 0) {
      // Poarta a refuzat commitul: NU se forteaza, se raporteaza.
      return { repo: repo.id, ok: false, steps, error: 'COMMIT_REFUSED_BY_GATE' };
    }
  } else {
    steps.push({ step: 'commit', code: 0, detail: 'nimic de comitat' });
  }

  const after = git(repo, ['rev-parse', 'HEAD']).out;
  const result = {
    repo: repo.id,
    label: repo.label,
    ok: true,
    before,
    after,
    changed: before !== after,
    steps,
  };
  evidence('sync:' + repo.id, { before, after, changed: before !== after });
  return result;
}

export async function syncAll(opts = {}) {
  const p = await planAll();
  if (p.verdict === 'BLOCKED') {
    evidence('sync:blocked', { blocked: p.blockedRepos });
    return { ok: false, verdict: 'BLOCKED', plan: p, repos: [] };
  }
  const repos = [];
  for (const r of REPOS) repos.push(syncRepo(r, opts));
  const failed = repos.filter((r) => !r.ok);
  return {
    ok: failed.length === 0,
    verdict: failed.length ? 'PARTIAL' : 'SYNCED',
    plan: p,
    repos,
    failed: failed.map((r) => ({ repo: r.repo, error: r.error })),
  };
}

// --- 3. PUSH (doar cu R0) ----------------------------------------------------

// Armarea acordului R0. Se apeleaza DOAR la cererea explicita a operatorului:
// un accord = o impingere, iar markerul e consumat de poarta comuna la push.
export function armPush(repoIds, by = 'operator') {
  const wanted = Array.isArray(repoIds) && repoIds.length ? repoIds : null;
  const targets = wanted ? wanted.map(repoById) : REPOS;
  const armed = [];
  for (const r of targets) {
    const marker = path.join(CFG.gitdata, r.gitdir, 'PUSH-ACORD');
    fs.writeFileSync(marker, new Date().toISOString() + ' ' + by + '\n');
    armed.push({ repo: r.id, marker });
  }
  evidence('arm-r0', { repos: armed.map((a) => a.repo), by });
  return { ok: true, armed, note: 'Un accord = o impingere. Poarta comuna consuma markerul la push.' };
}

export function pushRepo(repo) {
  const marker = path.join(CFG.gitdata, repo.gitdir, 'PUSH-ACORD');
  if (!exists(marker)) {
    evidence('push:refused-no-r0:' + repo.id, {});
    return {
      repo: repo.id,
      ok: false,
      code: 'NO_R0',
      detail: 'Fara marker PUSH-ACORD nu se impinge. Acordul se da din poarta sanitizata.',
    };
  }
  const before = git(repo, ['rev-parse', 'HEAD']).out;
  // Hookul pre-push (poarta comuna) consuma markerul: un acord = o impingere.
  const r = git(repo, ['push', 'origin', 'main']);
  const server = git(repo, ['ls-remote', 'origin', 'refs/heads/main']);
  const serverSha = server.out ? server.out.split(/\s+/)[0] : null;
  const ok = r.code === 0 && serverSha === before;
  evidence('push:' + repo.id, { ok, local: before, server: serverSha, code: r.code });
  return {
    repo: repo.id,
    label: repo.label,
    ok,
    code: ok ? 'PUSHED' : 'PUSH_NOT_CONFIRMED',
    local: before,
    server: serverSha,
    output: (r.out + '\n' + r.err).slice(0, 1200),
    note: ok ? '' : 'Daca pushul a picat, markerul a fost consumat: re-armaza-l (acord nou).',
  };
}

export async function pushAll() {
  const p = await planAll();
  if (p.verdict === 'BLOCKED') {
    evidence('push:blocked', { blocked: p.blockedRepos });
    return {
      ok: false,
      code: 'BLOCKED',
      detail: 'GitHub nu e curat si unitar. Nu se face procesul. Curata mai intai.',
      plan: p,
      repos: [],
    };
  }
  const repos = [];
  for (const r of REPOS) repos.push(pushRepo(r));
  const pushed = repos.filter((x) => x.ok);
  return {
    ok: repos.every((x) => x.ok),
    code: pushed.length ? 'PUSHED' : 'NOTHING_PUSHED',
    plan: p,
    repos,
  };
}

// --- 4. DOCTOR ---------------------------------------------------------------

export function doctor() {
  const checks = [];
  const add = (name, ok, detail) => checks.push({ name, ok: Boolean(ok), detail: String(detail) });

  add('mount:project', isDir(CFG.project), CFG.project);
  add('mount:gitdata', isDir(CFG.gitdata), CFG.gitdata);
  add('mount:secrets', isDir(CFG.secrets), CFG.secrets);
  add('mount:ga-data', isDir(CFG.gaData), CFG.gaData);
  add('mount:gate', isDir(CFG.gateDir), CFG.gateDir);

  const gitv = run('git', ['--version']);
  add('git', gitv.code === 0, gitv.out || gitv.err);
  const nodev = process.version;
  add('node', true, nodev);
  const pwsh = run('sh', ['-lc', 'command -v powershell || command -v pwsh || echo MISSING']);
  add('powershell', !/MISSING/.test(pwsh.out), pwsh.out || 'MISSING');

  add('token:github', exists(CFG.tokenFile), exists(CFG.tokenFile) ? 'prezent (nu se afiseaza)' : 'LIPSA');

  const gate = path.join(CFG.gateDir, 'pre-push');
  add('gate:pre-push', exists(gate), gate);
  const mirror = path.join(CFG.project, 'ci-server', 'gate', 'pre-push');
  if (exists(gate) && exists(mirror)) {
    const a = sha256File(gate);
    const b = sha256File(mirror);
    add('gate:mirror-equal', a === b, a === b ? 'identic' : 'DIFFER: shared=' + a + ' mirror=' + b);
  } else {
    add('gate:mirror-equal', false, 'una din cele doua lipsesc');
  }

  // Google: grantul viu, masurat din volumul montat (read-only).
  let grant = null;
  const consent = path.join(CFG.gaData, 'consent-result.json');
  if (exists(consent)) {
    try {
      const j = JSON.parse(fs.readFileSync(consent, 'utf8'));
      grant = {
        scopeCount: j.scope_count ?? (Array.isArray(j.scopes) ? j.scopes.length : null),
        permanent: j.PERMANENT ?? j.permanent ?? null,
        tokenEndpoint: j.TOKEN_ENDPOINT_HTTP ?? null,
        refreshProbe: j.REFRESH_PROBE_HTTP ?? null,
      };
      add('google:consent-file', true, 'scope_count=' + grant.scopeCount);
    } catch (e) {
      add('google:consent-file', false, 'JSON ilizibil: ' + e.message);
    }
  } else {
    add('google:consent-file', false, 'consent-result.json lipseste din ' + CFG.gaData);
  }

  const repos = REPOS.map((r) => {
    const s = statusRepo(r);
    add('repo:' + r.id, s.head !== null, 'HEAD=' + (s.head || 'n/a') + ' inSync=' + s.inSync);
    return s;
  });

  // --- Anomalii: igiena configului gitdir-ului si autorii commiturilor -----
  // Doua clase de accident, ambele masurate pe 2026-10-27:
  //   1. `git init` pe un gitdir real rescrie configul lui (core.worktree,
  //      core.filemode, user.*) - si apoi un commit ajunge in main cu
  //      identitatea celui care a rulat comanda.
  //   2. Un self-check care rezolva drumul gresit scrie fixture-ul in
  //      repository-ul de productie.
  // Doctorul nu repara nimic: face anomaliile VISIBILE. Istoricul nu se
  // rescrie niciodata, deci o anomalie din trecut ramane in trecut - dar una
  // noua nu mai poate trece neobservata.
  const anomalies = [];
  const knownAuthors = ['sentinel.prime@optimus.local', 'mavis-ci@local'];
  for (const r of REPOS) {
    const wt = gitConfigValue(r, 'core.worktree');
    const fm = gitConfigValue(r, 'core.filemode');
    const un = gitConfigValue(r, 'user.name');
    const ue = gitConfigValue(r, 'user.email');
    if (wt) anomalies.push({ code: 'GITDIR_WORKTREE_SET', repo: r.id, detail: wt });
    if (fm !== 'false') anomalies.push({ code: 'GITDIR_FILEMODE_NOT_FALSE', repo: r.id, detail: fm || '(unset)' });
    if (un || ue) anomalies.push({ code: 'GITDIR_IDENTITY_SET', repo: r.id, detail: (un + ' <' + ue + '>').trim() });
    // Conteaza doar commiturile NEPUBLICATE: ce e deja pe origin/main e
    // istoricul publicat al celorlalti agenti, nu o anomalie.
    const hasOrigin = gitLines(r, ['rev-parse', '--verify', 'origin/main']).length > 0;
    const unpublished = hasOrigin
      ? gitLines(r, ['log', '--format=%an|%ae', 'origin/main..main', '-n', '50'])
      : gitLines(r, ['log', '--format=%an|%ae', '-n', '20']);
    const foreign = [];
    for (const a of unpublished) {
      const parts = a.split('|');
      const email = (parts[1] || '').toLowerCase();
      if (email && knownAuthors.indexOf(email) === -1) foreign.push((parts[0] || '?') + ' <' + email + '>');
    }
    if (foreign.length) {
      anomalies.push({
        code: 'FOREIGN_AUTHORS',
        repo: r.id,
        detail:
          foreign.slice(0, 5).join(', ') + (foreign.length > 5 ? ' (+' + (foreign.length - 5) + ' mai multe)' : ''),
      });
    }
  }

  return {
    ts: new Date().toISOString(),
    container: 'Mavis-Optimus-CI',
    version: CFG.version,
    checks,
    green: checks.every((c) => c.ok),
    anomalyCount: anomalies.length,
    anomalies,
    grant,
    repos,
  };
}

export { evidenceTail };
