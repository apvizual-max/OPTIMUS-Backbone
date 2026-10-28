/**
 * GOOGLE AUTH — rezolvarea unica a credentialelor Google.
 *
 * Ordinea (prima care exista castiga):
 *   1. ENV din secret manager (Cloud):
 *        GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET / GOOGLE_REFRESH_TOKEN
 *   2. FISIERE locale (Local):
 *        ~/.google-mcp/credentials.json  -> installed.client_id / installed.client_secret
 *        ~/.google-mcp/tokens/mavis.json  -> refresh_token
 *
 * REGULA: nu afiseaza NICIO secret. describe() intoarce doar DE UNDE a venit.
 *          niciun secret nu ajunge in repo, in chat, sau in log.
 */

const fs = require('fs');
const path = require('path');

const HOME = process.env.HOME || '/root';
const CREDS_FILE = path.join(HOME, '.google-mcp', 'credentials.json');
const TOKENS_FILE = path.join(HOME, '.google-mcp', 'tokens', 'mavis.json');

// POPY a adaugat cheile in secret manager cu sufixul _MAVIS_CLOUD, ca sa nu se
// confunde cu cele locale. Acceptam ambele forme — prima care exista castiga.
const ENV_KEYS = {
  client_id: ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_ID_MAVIS_CLOUD'],
  client_secret: ['GOOGLE_CLIENT_SECRET', 'GOOGLE_CLIENT_SECRET_MAVIS_CLOUD'],
  refresh_token: ['GOOGLE_REFRESH_TOKEN', 'GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD'],
  email: ['GOOGLE_EMAIL'],
  maps: ['GOOGLE_MAPS_API_KEY'],
};

function envVal(kind) {
  for (const n of (ENV_KEYS[kind] || [])) {
    if (process.env[n]) return { value: process.env[n], name: n };
  }
  return null;
}

function readJson(p) {
  try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch { return null; }
}

/**
 * JSON tolerant la erori de copiere manuala.
 * Caz real: fisierul avea un `"` la inceput si `}}` la final ->
 * JSON.parse arunca, iar credentialele dispareau silent.
 * Recuperam primul `{` ... ultimul `}` si re incercam.
 */
function readJsonTolerant(p) {
  const raw = (() => { try { return fs.readFileSync(p, 'utf8'); } catch { return null; } })();
  if (!raw) return null;
  try { return JSON.parse(raw); } catch { /* mai jos */ }
  // Extragem primul obiect JSON BALANSAT: de la primul '{' pana la paranteza
  // care ii corespunde. Asta repara si gunoi ramas dupa (ex: '}}' la final).
  const s = raw.indexOf('{');
  if (s === -1) return null;
  let depth = 0, inStr = false, esc = false, end = -1;
  for (let i = s; i < raw.length; i++) {
    const ch = raw[i];
    if (inStr) {
      if (esc) esc = false;
      else if (ch === '\\') esc = true;
      else if (ch === '"') inStr = false;
      continue;
    }
    if (ch === '"') inStr = true;
    else if (ch === '{') depth++;
    else if (ch === '}') { depth--; if (depth === 0) { end = i; break; } }
  }
  if (end === -1) return null;
  try { return JSON.parse(raw.slice(s, end + 1)); } catch { return null; }
}

function fromEnv() {
  // REGULA (masurat 2026-10-27): client_id, client_secret si refresh_token
  // trebuie sa vina din ACEEASI familie de variabile. Amestecarea (client din
  // GOOGLE_CLIENT_ID + token din GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD) trimite
  // catre Google o pereche care nu poate exista: tokenul apartine altui
  // client OAuth -> invalid_grant / unauthorized_client.
  const groups = [
    { suffix: '_MAVIS_CLOUD', label: 'env(_MAVIS_CLOUD)' },
    { suffix: '', label: 'env' },
  ];
  for (const g of groups) {
    const id = process.env['GOOGLE_CLIENT_ID' + g.suffix];
    const sec = process.env['GOOGLE_CLIENT_SECRET' + g.suffix];
    const tok = process.env['GOOGLE_REFRESH_TOKEN' + g.suffix];
    if (id && sec && tok) {
      return {
        client_id: id,
        client_secret: sec,
        refresh_token: tok,
        source: 'env',
        source_detail: [
          'GOOGLE_CLIENT_ID' + g.suffix,
          'GOOGLE_CLIENT_SECRET' + g.suffix,
          'GOOGLE_REFRESH_TOKEN' + g.suffix,
        ],
        client_source: g.label,
        mixed_sources: false,
      };
    }
  }
  // Variabile amestecate: un client dintr-o familie + un token din alta
  // familie = invalid_grant. NU se asambleaza o pereche care nu poate
  // exista — se refuza, iar describe() arata exact ce s-a gasit, ca
  // remedierea sa fie un pas, nu o vanatoare.
  return null;
}

/** Diagnostic al amestecului de familii de variabile env. Fara secrete. */
function mixedEnvNames() {
  const id = envVal('client_id');
  const sec = envVal('client_secret');
  const tok = envVal('refresh_token');
  if (!id || !sec || !tok) return null;
  const families = new Set(
    [id.name, sec.name, tok.name].map((n) => (n.endsWith('_MAVIS_CLOUD') ? '_MAVIS_CLOUD' : ''))
  );
  if (families.size <= 1) return null;
  return [id.name, sec.name, tok.name];
}

function fromFiles() {
  const c = readJsonTolerant(CREDS_FILE);
  const t = readJsonTolerant(TOKENS_FILE);
  if (!c || !t) return null;
  const inst = c.installed || c.web || c; // desktop client = installed, web = web
  const refresh_token = t.refresh_token;
  if (!refresh_token) return null;

  // REGULA (masurat 2026-10-27): tokenul apartine UNUI client. Daca fisierul
  // de token isi poarta propriul client_id + client_secret, acelea se folosesc
  // — nu cele din credentials.json, care pot apartine altui client.
  // Cazul masurat in cloud: tokenul era al clientului ...u773, iar
  // credentials.json tinea clientul ...5b7h17gt1c5hc4 -> invalid_grant.
  // NU se amesteca niciodata: fie perechea completa din fisierul de token,
  // fie perechea completa din credentials.json.
  const tokenHasClient = Boolean(t.client_id && t.client_secret);
  const credClientId = inst.client_id;
  if (tokenHasClient) {
    return {
      client_id: t.client_id,
      client_secret: t.client_secret,
      refresh_token,
      source: 'files',
      source_detail: [TOKENS_FILE],
      client_source: 'token-file',
      mixed_sources: false,
    };
  }
  // Tokenul nu are pereche completa. Daca are un client_id care DIFERA de
  // cel din credentials.json, atunci tokenul apartine altui client, iar
  // asamblarea secretului din credentials.json ar da invalid_grant. Se refuza.
  if (t.client_id && credClientId && t.client_id !== credClientId) return null;
  const client_id = credClientId;
  const client_secret = inst.client_secret;
  if (!client_id || !client_secret) return null;
  return {
    client_id,
    client_secret,
    refresh_token,
    source: 'files',
    source_detail: [CREDS_FILE, TOKENS_FILE],
    client_source: 'credentials-file',
    mixed_sources: false,
  };
}

/** Credentialele active, sau null daca nu exista niciun set complet. */
function resolve() {
  return fromEnv() || fromFiles() || null;
}

/** Diagnostic fara secreti. Spune EXACT ce lipseste. */
function describe() {
  const env = {
    client_id: envVal('client_id')?.name || null,
    client_secret: envVal('client_secret')?.name || null,
    refresh_token: envVal('refresh_token')?.name || null,
    email: envVal('email')?.name || null,
    maps_api_key: envVal('maps')?.name || null,
  };
  const files = {
    credentials_json: fs.existsSync(CREDS_FILE),
    tokens_mavis_json: fs.existsSync(TOKENS_FILE),
  };
  const r = resolve();
  const missing = [];
  if (!env.client_id && !files.credentials_json) missing.push('GOOGLE_CLIENT_ID');
  if (!env.client_secret && !files.credentials_json) missing.push('GOOGLE_CLIENT_SECRET');
  if (!env.refresh_token && !files.tokens_mavis_json) missing.push('GOOGLE_REFRESH_TOKEN');

  // Diagnostic al perechii client-token, fara secrete.
  // Daca fisierul de token are un client propriu, iar credentials.json are
  // ALT client, atunci perechea (credentials.json, token) ar da invalid_grant.
  // Se raporteaza explicit, nu se presupune ca e bine.
  let client_pairing = null;
  try {
    const c = readJsonTolerant(CREDS_FILE);
    const t = readJsonTolerant(TOKENS_FILE);
    const credClient = c ? (c.installed || c.web || c).client_id : null;
    const tokenClient = t ? t.client_id : null;
    if (tokenClient && credClient) {
      client_pairing = tokenClient === credClient ? 'same-client' : 'different-clients';
    } else if (tokenClient) {
      client_pairing = 'token-only';
    } else if (credClient) {
      client_pairing = 'credentials-only';
    }
  } catch { client_pairing = 'unreadable'; }

  return {
    resolved: !!r,
    source: r ? r.source : null,
    source_detail: r ? r.source_detail : null,
    client_source: r ? (r.client_source || null) : null,
    mixed_sources: r ? (r.mixed_sources === true) : false,
    mixed_env: mixedEnvNames(),
    client_pairing,
    env,
    files,
    missing,
    paths: { CREDS_FILE, TOKENS_FILE },
  };
}

/** Scope-urile pentru care se cere consimtamant. Un set complet, o singura cerere. */
const SCOPES = {
  drive: 'https://www.googleapis.com/auth/drive',
  gmail: 'https://www.googleapis.com/auth/gmail.modify',
  gmailReadonly: 'https://www.googleapis.com/auth/gmail.readonly',
  calendar: 'https://www.googleapis.com/auth/calendar',
  docs: 'https://www.googleapis.com/auth/documents',
  spreadsheets: 'https://www.googleapis.com/auth/spreadsheets',
  slides: 'https://www.googleapis.com/auth/presentations',
  photosReadonly: 'https://www.googleapis.com/auth/photoslibrary.readonly',
  photosReadwrite: 'https://www.googleapis.com/auth/photoslibrary.readwrite',
  driveFile: 'https://www.googleapis.com/auth/drive.file',
};

/**
 * Setul implicit (6 scope-uri) — cele care functioneaza fara API-uri suplimentare
 * activate in proiectul Cloud.
 *
 * DE CE NU PENTRU PHOTOS: scope-ul photoslibrary.* este respins de Google cu
 * `invalid_scope` daca Photos Library API nu e activata in proiect. Google
 * raporteaza scope-urile pentru API-uri neactivate drept "invalid" — vezi
 * raportul de eroare: valid=[...], invalid=[photoslibrary.readwrite].
 *
 * In plus, masurat 2026-10-21: `photoslibrary.googleapis.com` este blocat de
 * egress-ul sandboxului de cloud (0/6 conexiuni). Deci Photos se face de la
 * Local, oricum. Nu blocam restul setup-ului pentru el.
 */
const FULL_SCOPES = [
  SCOPES.drive,
  SCOPES.gmail,
  SCOPES.calendar,
  SCOPES.docs,
  SCOPES.spreadsheets,
  SCOPES.slides,
];

/** Scope-uri pentru Google Photos — doar daca Photos Library API e activata in proiect. */
const PHOTOS_SCOPES = [SCOPES.photosReadwrite];

/** Setul minim: ce trebuie ca Drive + Gmail sa mearga in cloud. */
const CORE_SCOPES = [SCOPES.drive, SCOPES.gmail, SCOPES.calendar];

module.exports = {
  resolve,
  describe,
  fromEnv,
  fromFiles,
  mixedEnvNames,
  readJson,
  readJsonTolerant,
  SCOPES,
  FULL_SCOPES,
  PHOTOS_SCOPES,
  CORE_SCOPES,
  CREDS_FILE,
  TOKENS_FILE,
};
