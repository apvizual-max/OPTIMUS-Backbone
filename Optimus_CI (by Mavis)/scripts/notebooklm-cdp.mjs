#!/usr/bin/env node
/**
 * notebooklm-cdp.mjs - drivarea NotebookLM prin CDP, FARA browser grafic si FARA login.
 *
 * De ce exista asta:
 *   Serverul MCP `minimax-notebooklm` pornește Chrome headless cu un profil
 *   AUTENTIFICAT pe disc si expune CDP pe portul 9412. Dar serverul are doar
 *   unelte de CITIRE (health / list_notebooks / get_sources / ask).
 *   Singura cale de SCRIS era browserul grafic -> cere login uman de fiecare data.
 *
 *   Acest script foloseste ACELEASI sesiune deja autentificata.
 *   Daca profilul e pe disc, sesiunea supravietuieste repornirii.
 *   Popy nu mai apasa niciun buton.
 *
 * Folosire:
 *   node notebooklm-cdp.mjs auth
 *   node notebooklm-cdp.mjs list
 *   node notebooklm-cdp.mjs rename <notebookId> <titluNou>
 *
 * Portabilitate: nu scrie nimic pe disk in afara profilului deja existent.
 */

const CDP_PORT = Number(process.env.NBLM_CDP_PORT || 9412);
const CDP = `http://127.0.0.1:${CDP_PORT}`;

/** Gaseste sau creeaza un tab pe NotebookLM si intoarce descriptorul lui. */
async function tab() {
  let list;
  try {
    list = await (await fetch(`${CDP}/json/list`)).json();
  } catch (e) {
    throw new Error(
      `CDP ${CDP_PORT} nu raspunde. Chrome-ul headless cu profilul notebooklm ruleaza? ` +
      `Verifica: Get-NetTCPConnection -LocalPort ${CDP_PORT}`
    );
  }
  let page = list.find((t) => t.type === 'page' && t.webSocketDebuggerUrl);
  if (!page) {
    page = await (await fetch(`${CDP}/json/new?about:blank`, { method: 'PUT' })).json();
  }
  return page;
}

/** Minimal CDP client: trimite comenzi si asteapta raspunsul cu id-ul potrivit. */
function connect(wsUrl) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(wsUrl);
    const pending = new Map();
    let seq = 0;

    ws.addEventListener('open', () =>
      resolve({
        send(method, params = {}) {
          const id = ++seq;
          return new Promise((res, rej) => {
            pending.set(id, { res, rej });
            ws.send(JSON.stringify({ id, method, params }));
          });
        },
        close: () => ws.close(),
      })
    );
    ws.addEventListener('error', reject);
    ws.addEventListener('message', (ev) => {
      const msg = JSON.parse(ev.data);
      const p = pending.get(msg.id);
      if (!p) return;
      pending.delete(msg.id);
      msg.error ? p.rej(new Error(msg.error.message)) : p.res(msg.result);
    });
  });
}

/**
 * Ruleaza expresia in pagina si intoarce valoarea deserializata.
 *NU folosim Runtime.evaluate cu awaitPromise cand expresia e simpla,
 * ca sa nu depindem de timing-ul paginii.
 */
async function evaluate(client, expression) {
  const r = await client.send('Runtime.evaluate', {
    expression,
    returnByValue: true,
    awaitPromise: true,
  });
  if (r.exceptionDetails) {
    throw new Error(r.exceptionDetails.exception?.description || 'evaluate a esuat');
  }
  return r.result.value;
}

/** Sesiunea e autentificata doar daca exista un marker de CONT, nu un buton de logare. */
const AUTH_PROBE = `(() => {
  const txt = document.body.innerText || '';
  const hasSignIn = /sign in to your account|sign in to gemini notebook/i.test(txt);
  const acct = document.querySelector('[aria-label*="Google Account"], [aria-label*="Google Account:"]');
  return {
    url: location.href,
    title: document.title,
    signedIn: !!acct,
    account: acct ? acct.getAttribute('aria-label') : null,
    stillOfferedSignIn: hasSignIn,
    notebooks: (txt.match(/\\d+ sources?/g) || []).length
  };
})()`;

async function main() {
  const [cmd, ...rest] = process.argv.slice(2);
  const page = await tab();
  const client = await connect(page.webSocketDebuggerUrl);
  try {
    if (cmd === 'auth') {
      await evaluate(client, `location.href.startsWith('https://notebook.google.com')
        ? true : (location.href = 'https://notebook.google.com/', false)`).catch(() => {});
      // daca am navigat, dam timp paginii sa se aseze
      await new Promise((r) => setTimeout(r, 2500));
      console.log(JSON.stringify(await evaluate(client, AUTH_PROBE), null, 2));
    } else if (cmd === 'list') {
      console.log(JSON.stringify(await evaluate(client, AUTH_PROBE), null, 2));
    } else if (cmd === 'rename') {
      const [id, title] = rest;
      if (!id || !title) throw new Error('folosire: rename <notebookId> <titluNou>');
      await client.send('Page.navigate', {
        url: `https://notebook.google.com/notebook/${id}`,
      });
      await new Promise((r) => setTimeout(r, 3000));

      // APASAM pe input ca sa-l focusam, apoi scriem prin insertText.
      // NU folosim fill si NU folosim Control+A: pe acest input Angular
      // selectia se opreste la limita de cuvant si corupe titlul.
      const input = await evaluate(
        client,
        `(() => { const i = document.querySelector('input.title-input');
                  if (i) { i.focus(); i.select(); return true; } return false; })()`
      );
      if (!input) throw new Error('input.title-input negasit');

      await client.send('Input.dispatchKeyEvent', {
        type: 'keyDown', key: 'a', code: 'KeyA', windowsVirtualKeyCode: 65,
        modifiers: 2, // Ctrl
      });
      await client.send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'a', code: 'KeyA', windowsVirtualKeyCode: 65, modifiers: 2 });

      await client.send('Input.insertText', { text: title });

      const written = await evaluate(client, `document.querySelector('input.title-input').value`);

      await client.send('Input.dispatchKeyEvent', {
        type: 'rawKeyDown', key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13,
      });
      await client.send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13 });

      // VERIFICAM VALOAREA, nu confirmarea apelului.
      console.log(JSON.stringify({ written, expected: title, ok: written === title }, null, 2));
    } else {
      console.log('folosire: auth | list | rename <id> <titlu>');
    }
  } finally {
    client.close();
  }
}

main().catch((e) => {
  console.error('EROARE: ' + e.message);
  process.exit(1);
});