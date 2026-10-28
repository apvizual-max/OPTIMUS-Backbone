// cli.mjs - punctul de intrare al motorului Mavis-Optimus-CI.
//
//   node cli.mjs doctor     - starea completa a sistemului (mounts, token, gate, Google, repo-uri)
//   node cli.mjs status     - starea repo-urilor: local vs server, dirty, divergenta
//   node cli.mjs plan       - PRE-FLIGHT: GitHub curat si unitar? READY sau BLOCKED cu motive
//   node cli.mjs sync       - sincronizare autonoma locala (ff-only / merge --no-ff / commit)
//   node cli.mjs push       - impingere, DOAR cu marker R0 si doar daca planul e READY
//   node cli.mjs evidence   - ultimele evenimente din ledger
//   node cli.mjs serve      - serverul HTTP (API pentru pluginul MCP)
//
// Tot ce afiseaza aici este MASURAT in momentul rularii.

import http from 'node:http';
import { CFG, REPOS } from './lib.mjs';
import {
  doctor,
  planAll,
  pushAll,
  armPush,
  statusAll,
  syncAll,
  evidenceTail,
} from './engine.mjs';

function print(obj) {
  console.log(JSON.stringify(obj, null, 2));
}

async function main() {
  const cmd = (process.argv[2] || 'serve').toLowerCase();
  switch (cmd) {
    case 'doctor': {
      const d = doctor();
      print(d);
      process.exit(d.green ? 0 : 1);
      break;
    }
    case 'status': {
      print({ ts: new Date().toISOString(), repos: statusAll() });
      break;
    }
    case 'plan': {
      const p = await planAll();
      print(p);
      process.exit(p.verdict === 'READY' ? 0 : 3);
      break;
    }
    case 'sync': {
      const s = await syncAll();
      print(s);
      process.exit(s.ok ? 0 : 1);
      break;
    }
    case 'push': {
      const p = await pushAll();
      print(p);
      process.exit(p.ok ? 0 : 1);
      break;
    }
    case 'arm-r0': {
      // Armeaza acordul R0. NU impinge. Un acord = o impingere: markerul
      // PUSH-ACORD e consumat de poarta comuna la primul push reusit.
      //   node cli.mjs arm-r0 [ci,cloud,ciclone] [cine acorda]
      const repos = process.argv[3]
        ? process.argv[3].split(',').map((s) => s.trim()).filter(Boolean)
        : null;
      const by = process.argv[4] || 'operator';
      print(armPush(repos, by));
      process.exit(0);
      break;
    }
    case 'evidence': {
      const n = Number(process.argv[3] || 50);
      print({ ts: new Date().toISOString(), events: evidenceTail(n) });
      break;
    }
    case 'ping': {
      // Verificare FARA retea: pentru HEALTHCHECK. Doctorul atinge reteaua
      // (ls-remote x 3 repo-uri) si nu incape intr-un healthcheck de 8s.
      print({ ok: true, container: 'Mavis-Optimus-CI', version: CFG.version });
      break;
    }
    case 'selftest': {
      // Autotestul motorului: ca o poarta care poate esua, nu doar semnalizeaza.
      const { spawnSync } = await import('node:child_process');
      const here = new URL('./selftest.mjs', import.meta.url).pathname;
      const r = spawnSync(process.execPath, [here], { stdio: 'inherit' });
      process.exit(r.status === null ? 1 : r.status);
      break;
    }
    case 'serve': {
      serve();
      break;
    }
    default: {
      console.error('comanda necunoscuta: ' + cmd);
      process.exit(2);
    }
  }
}

function send(res, code, obj) {
  const body = JSON.stringify(obj, null, 2);
  res.writeHead(code, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(body),
  });
  res.end(body);
}

function serve() {
  const server = http.createServer(async (req, res) => {
    const url = new URL(req.url, 'http://localhost');
    const route = url.pathname;
    try {
      if (route === '/health') {
        send(res, 200, {
          ok: true,
          container: 'Mavis-Optimus-CI',
          version: CFG.version,
          uptimeSec: Math.round(process.uptime()),
          repos: REPOS.length,
        });
        return;
      }
      if (route === '/doctor') {
        const d = doctor();
        send(res, d.green ? 200 : 503, d);
        return;
      }
      if (route === '/status') {
        send(res, 200, { ts: new Date().toISOString(), repos: statusAll() });
        return;
      }
      if (route === '/plan') {
        const p = await planAll();
        send(res, p.verdict === 'READY' ? 200 : 409, p);
        return;
      }
      if (route === '/sync' && req.method === 'POST') {
        const s = await syncAll();
        send(res, s.ok ? 200 : 500, s);
        return;
      }
      if (route === '/push' && req.method === 'POST') {
        const p = await pushAll();
        send(res, p.ok ? 200 : 409, p);
        return;
      }
      if (route === '/arm-r0' && req.method === 'POST') {
        // Instrumentul `ci_arm_push` al pluginului apeleaza EXACT ruta asta.
        // Fara ea, pluginul raspundea 404 si acordul R0 nu putea fi dat prin
        // interfata documentata (masurat 2026-10-28).
        let body = {};
        try {
          let raw = '';
          for await (const chunk of req) raw += chunk;
          if (raw.trim()) body = JSON.parse(raw);
        } catch {
          body = {};
        }
        const repos = Array.isArray(body.repos) && body.repos.length ? body.repos : null;
        const by = typeof body.by === 'string' && body.by.trim() ? body.by.trim() : 'operator';
        const a = armPush(repos, by);
        send(res, 200, a);
        return;
      }
      if (route === '/evidence') {
        const n = Number(url.searchParams.get('n') || 50);
        send(res, 200, { ts: new Date().toISOString(), events: evidenceTail(n) });
        return;
      }
      send(res, 404, { error: 'route necunoscuta: ' + route });
    } catch (e) {
      send(res, 500, { error: String(e && e.message ? e.message : e) });
    }
  });
  // Bind pe 0.0.0.0 in container: publicarea portului Docker ajunge la IP-ul
  // containerului, nu la loopback-ul lui. Expunerea pe host ramane limitata la
  // 127.0.0.1 (docker run -p 127.0.0.1:8790:8790), deci nimeni din afara
  // masinii nu atinge serverul.
  server.listen(CFG.apiPort, '0.0.0.0', () => {
    console.log(
      'Mavis-Optimus-CI ' + CFG.version + ' asculta pe 127.0.0.1:' + CFG.apiPort +
        ' | proiect=' + CFG.project + ' | gitdata=' + CFG.gitdata
    );
  });
}

main();
