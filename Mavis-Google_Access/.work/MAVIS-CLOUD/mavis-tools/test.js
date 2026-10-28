const fs = require('fs');
const path = require('path');
const https = require('https');
const querystring = require('querystring');

const CREDS = JSON.parse(fs.readFileSync(path.join(process.env.HOME, '.google-mcp', 'credentials.json'))).installed;
const TOK = JSON.parse(fs.readFileSync(path.join(process.env.HOME, '.google-mcp', 'tokens', 'mavis.json')));

function refresh() {
  return new Promise((res, rej) => {
    const body = querystring.stringify({
      client_id: CREDS.client_id, client_secret: CREDS.client_secret,
      refresh_token: TOK.refresh_token, grant_type: 'refresh_token',
    });
    const req = https.request({ hostname: 'oauth2.googleapis.com', path: '/token', method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': Buffer.byteLength(body) } },
      r => { let d = ''; r.on('data', c => d += c); r.on('end', () => { const j = JSON.parse(d); j.error ? rej(new Error(j.error)) : res(j.access_token); }); });
    req.on('error', rej); req.write(body); req.end();
  });
}

function api(token, url) {
  return new Promise((res, rej) => {
    https.get(url, { headers: { Authorization: 'Bearer ' + token } }, r => {
      let d = ''; r.on('data', c => d += c); r.on('end', () => { try { res(JSON.parse(d)); } catch { res(d); } });
    }).on('error', rej);
  });
}

(async () => {
  const token = await refresh();
  console.log('TOKEN REFRESHAT: ok\n');

  console.log('=== GOOGLE DRIVE: primele 12 fișiere ===');
  const dr = await api(token, 'https://www.googleapis.com/drive/v3/files?pageSize=12&fields=files(name,mimeType,modifiedTime,owners(emailAddress))&orderBy=modifiedTime desc');
  if (dr.files) { dr.files.forEach(f => console.log(`  - ${f.name}  [${(f.mimeType||'').split('.').pop()}]`)); console.log(`  total primite: ${dr.files.length}`); }
  else console.log('  EROARE:', JSON.stringify(dr).slice(0,300));

  console.log('\n=== GMAIL: ultimele 8 mesaje ===');
  const gm = await api(token, 'https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=8');
  if (gm.messages) {
    for (const m of gm.messages) {
      const d = await api(token, `https://gmail.googleapis.com/gmail/v1/users/me/messages/${m.id}?format=metadata&metadataHeaders=Subject&metadataHeaders=From`);
      const h = {};
      (d.payload.headers || []).forEach(x => h[x.name] = x.value);
      console.log(`  - ${(h.Subject||'(fără subiect)').slice(0,60)}`);
      console.log(`    de la: ${(h.From||'?').slice(0,55)}`);
    }
  } else console.log('  EROARE:', JSON.stringify(gm).slice(0,300));
})().catch(e => console.error('E:', e.message));
