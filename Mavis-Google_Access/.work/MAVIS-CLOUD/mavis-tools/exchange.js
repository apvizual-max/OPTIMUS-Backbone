const fs = require('fs');
const path = require('path');
const https = require('https');
const querystring = require('querystring');

const CREDS = JSON.parse(fs.readFileSync(path.join(process.env.HOME, '.google-mcp', 'credentials.json'))).installed;
const code = process.argv[2];
if (!code) { console.error('usage: node exchange.js <code>'); process.exit(1); }

const body = querystring.stringify({
  code,
  client_id: CREDS.client_id,
  client_secret: CREDS.client_secret,
  redirect_uri: 'http://localhost:8765',
  grant_type: 'authorization_code',
});

const req = https.request({
  hostname: 'oauth2.googleapis.com',
  path: '/token',
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Content-Length': Buffer.byteLength(body),
  },
}, (res) => {
  let data = '';
  res.on('data', c => data += c);
  res.on('end', () => {
    const j = JSON.parse(data);
    if (j.error) {
      console.error('EROARE:', j.error, '-', j.error_description || '');
      process.exit(1);
    }
    const out = path.join(process.env.HOME, '.google-mcp', 'tokens');
    fs.mkdirSync(out, { recursive: true });
    const file = path.join(out, 'mavis.json');
    fs.writeFileSync(file, JSON.stringify(j, null, 2));
    console.log('TOKEN SALVAT:', file);
    console.log('scope:', j.scope);
    console.log('refresh_token:', j.refresh_token ? 'prezent' : 'LIPSA');
  });
});
req.on('error', e => { console.error('eroare rețea:', e.message); process.exit(1); });
req.write(body);
req.end();
