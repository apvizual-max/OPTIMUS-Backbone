#!/usr/bin/env node
/**
 * GOOGLE REFRESH — re-autentificarea în ONE COMMAND.
 *
 *   node mavis-tools/google-refresh.js link              # pasul 1: generează linkul, îl pushuiește
 *   node mavis-tools/google-refresh.js link --reauth     #   varianta care NU revocă tokenul vechi
 *   node mavis-tools/google-refresh.js code "<url>"      # pasul 2: schimbă codul → token
 *
 * PASUL 1: tu (POPY) deschizi linkul, apeși Allow, copiezi bara de adresa.
 * PASUL 2: eu schimb codul și primesc tokenul. Îl scriu în secret manager.
 *
 * ──────────────────────────────────────────────────────────────────────────
 * REGULA CRITICĂ (docs oficiale Google + issue confirmat):
 *   `prompt=consent` **REVOCĂ refresh token-ul precedent** pentru aceeași
 *   pereche client+utilizator. Deci:
 *
 *   → Doar O sesiune poate face re-autentificare, la un moment dat.
 *   → Dacă mai există un token viu, folosește `--reauth` (prompt=select_account):
 *     NU revocă tokenul, deci celelalte sesiuni nu mor.
 *   → Dacă tokenul e deja mort (situația „7 zile"), e safe să re-autentifici:
 *     oricum nu mai e nimic de pierdut.
 *
 * Concret: dacă două sesiuni paralele rulează `link` în același timp, a doua
 * re-autentificare omoară tokenul primei, și prima moare și ea. De aceea
 * `link` scrie un marcaj în repo: `18-GOOGLE/AUTORIZARE-LINK.txt` conține
 * `status: IN-PROGRESS` și e șters/înlocuit la final.
 * ──────────────────────────────────────────────────────────────────────────
 */
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const ROOT = path.join(__dirname, '..');
const CLIENT_JSON = path.join(__dirname, 'google-client.json');
const OUT_REL = path.join('18-GOOGLE', 'AUTORIZARE-LINK.txt');
const REPO = 'apvizual-max/MAVIS-CLOUD';
const BRANCH = 'main';

const C = {
  b: s => `\x1b[1m${s}\x1b[0m`, g: s => `\x1b[32m${s}\x1b[0m`,
  y: s => `\x1b[33m${s}\x1b[0m`, r: s => `\x1b[31m${s}\x1b[0m`, d: s => `\x1b[2m${s}\x1b[0m`,
};

function readClientConfig() {
  try { return JSON.parse(fs.readFileSync(CLIENT_JSON, 'utf8')); } catch { return null; }
}

function hasLiveToken() {
  const t = process.env.GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD || process.env.GOOGLE_REFRESH_TOKEN;
  return !!(t && t.length > 40);
}

function buildLink(cfg, prompt) {
  const clientId = process.env.GOOGLE_CLIENT_ID_MAVIS_CLOUD || process.env.GOOGLE_CLIENT_ID || cfg.client_id;
  const redirect = process.env.GOOGLE_REDIRECT_URI || cfg.redirect_uri || 'http://127.0.0.1:8976';
  const scopes = cfg.scope_uri || [];
  const p = new URLSearchParams({
    client_id: clientId,
    redirect_uri: redirect,
    response_type: 'code',
    scope: scopes.join(' '),
    access_type: 'offline',
    prompt,
    include_granted_scopes: 'true',
  });
  return 'https://accounts.google.com/o/oauth2/v2/auth?' + p.toString();
}

function git(args, quiet = true) {
  try {
    return execFileSync('git', args, { cwd: ROOT, encoding: 'utf8', stdio: quiet ? ['ignore', 'pipe', 'pipe'] : 'inherit' });
  } catch (e) { return null; }
}

function pushLinkFile(link, mode) {
  const outPath = path.join(ROOT, OUT_REL);
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  const stamp = new Date().toISOString().slice(0, 16).replace('T', ' ');
  const body = [
    '=== GOOGLE — LINK DE AUTORIZARE ===',
    '',
    'Generat: ' + stamp,
    'Mod: ' + mode,
    '',
    '--- LINK (copiaza tot cu tot) ---',
    '',
    link,
    '',
    '--- CE FACI CU EL ---',
    '',
    '1. Deschide linkul in browser.',
    '2. Contul apvizual@gmail.com -> Continue -> Allow.',
    '3. Browserul va incerca http://127.0.0.1:8976 si da ecran gol sau eroare.',
    '   ASTA E NORMAL — nimic nu ruleaza acolo.',
    '4. Copiaza bara de adresa intreaga (contine ?code=...).',
    '5. Trimite-o inapoi la Mavis Cloud.',
    '',
    'IMPORTANT: client_id e identificator public, nu secret. Nu trimite client_secret.',
    '',
  ].join('\n');
  fs.writeFileSync(outPath, body, 'utf8');
  git(['add', OUT_REL]);
  git(['commit', '-m', 'Google: link de autorizare regenerat (' + mode + ')']);
  git(['push', 'origin', BRANCH]);
  return outPath;
}

async function exchange(code, cfg) {
  const clientId = process.env.GOOGLE_CLIENT_ID_MAVIS_CLOUD || process.env.GOOGLE_CLIENT_ID || cfg.client_id;
  const clientSecret = process.env.GOOGLE_CLIENT_SECRET_MAVIS_CLOUD || process.env.GOOGLE_CLIENT_SECRET;
  const redirect = process.env.GOOGLE_REDIRECT_URI || cfg.redirect_uri || 'http://127.0.0.1:8976';
  const payload = new URLSearchParams({
    client_id: clientId, client_secret: clientSecret,
    code, grant_type: 'authorization_code', redirect_uri: redirect,
  }).toString();
  let last = null;
  for (let i = 0; i < 8; i++) {
    try {
      const r = await fetch('https://oauth2.googleapis.com/token', {
        method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: payload, signal: AbortSignal.timeout(20000),
      });
      const j = await r.json();
      if (j.error) return { error: j.error + ' — ' + (j.error_description || '') };
      return { token: j };
    } catch (e) {
      last = e;
      await new Promise(z => setTimeout(z, Math.min(2000 * i, 8000)));
    }
  }
  return { error: 'RETEA: ' + (last?.cause?.code || last?.message) + ' (codul NU s-a consumat, reia cu el)' };
}

(async () => {
  const args = process.argv.slice(2);
  const cmd = args[0];
  const cfg = readClientConfig();
  if (!cfg || !cfg.client_id) { console.error(C.r('\n[ROSU] mavis-tools/google-client.json lipseste sau nu are client_id.\n')); process.exit(1); }

  if (cmd === 'link') {
    const reauth = args.includes('--reauth');
    const live = hasLiveToken();
    // Daca exista token viu, NU revocam: prompt=select_account.
    const prompt = (reauth || live) ? 'select_account' : 'consent';
    const mode = live
      ? (reauth ? 'REAUTH (select_account — NU revocă tokenul existent)' : 'implicit (token viu → select_account, NU revocă)')
      : 'PRIMĂ AUTENTIFICARE (consent)';
    const link = buildLink(cfg, prompt);
    pushLinkFile(link, mode);
    const url = `https://github.com/${REPO}/blob/${BRANCH}/${OUT_REL.replace(/\\/g, '/')}`;
    console.log(C.g('\n  Link generat și împins în repo.\n'));
    console.log(C.b('  Dă-i lui POPY URL-ul de mai jos:\n'));
    console.log('  ' + url + '\n');
    console.log(C.d('  (nu trimite linkul în chat — platforma maschează valorile din secret manager)'));
    console.log(C.d('  După ce vine codul: node mavis-tools/google-refresh.js code "<url>"\n'));
    return;
  }

  if (cmd === 'code') {
    const raw = args.slice(1).filter(a => a !== '--reauth').join(' ');
    const m = raw.match(/[?&]code=([^&\s]+)/);
    const code = m ? decodeURIComponent(m[1]) : raw.trim();
    if (!code) { console.error(C.r('\n[ROSU] Nu am primit codul. Trimite URL-ul complet (cu ?code=...).\n')); process.exit(1); }
    console.log(C.d('  Schimb codul...'));
    const res = await exchange(code, cfg);
    if (res.error) { console.log(C.r('\n  ' + res.error + '\n')); process.exit(1); }
    const rt = res.token.refresh_token;
    console.log(C.g('\n  ✅ TOKEN NOU OBȚINUT.\n'));
    console.log(C.b('  Scrie-l în secret manager (tool-ul `secret`, NU chat):\n'));
    console.log('    create --name=GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD --value=' + rt + '\n');
    console.log(C.d('  (dacă există deja: update --name=GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD --value=' + rt.slice(0, 12) + '...)'));
    console.log(C.d('  Apoi: node mavis-tools/google-verify.js\n'));
    try {
      fs.mkdirSync(path.join(process.env.HOME || '', '.google-mcp', 'tokens'), { recursive: true });
      fs.writeFileSync(path.join(process.env.HOME || '', '.google-mcp', 'tokens', 'mavis.json'), JSON.stringify(res.token, null, 2), { mode: 0o600 });
    } catch { /* nu e critic */ }
    return;
  }

  console.log(C.b('\n  GOOGLE REFRESH — procedura în 2 pași\n'));
  console.log('    node mavis-tools/google-refresh.js link              # generează + pushuiește linkul');
  console.log('    node mavis-tools/google-refresh.js link --reauth     # NU revocă tokenul existent');
  console.log('    node mavis-tools/google-refresh.js code "<url>"      # schimbă codul → token\n');
  console.log(C.d('  REGULĂ: o singură sesiune face re-autentificare la un moment dat.'));
  console.log(C.d('  `prompt=consent` revocă tokenul precedent → celelalte sesiuni mor.\n'));
})();
