/**
 * QUOTA MANAGER — limite oficiale Google Gmail API (documentatie 01.05.2026)
 *   per minut per proiect      : 1.200.000 unitati
 *   per minut per utilizator   : 6.000 unitati
 *   prag zilnic de facturare   : 80.000.000 unitati
 *
 * COST PE METODA:
 *   history.list      2 | messages.list  5 | messages.modify 5
 *   messages.get     20 | messages.trash 20 | messages.delete 10
 *   messages.insert  25 | messages.import 25 | threads.get 40 | messages.send 100
 *
 * REGULA: NU folosi messages.get cand poti folosi messages.list.
 * 34.000 mesaje * 20 unitati = 680.000 -> arde cotă in 2 minute.
 * 34.000 mesaje *  5 unitati = 170.000 -> incape in 28 de minute.
 */
const QUOTA = {
  perMinutePerUser: 6000,
  units: {
    'history.list': 2, 'messages.list': 5, 'messages.modify': 5,
    'messages.get': 20, 'messages.trash': 20, 'messages.delete': 10,
    'messages.insert': 25, 'messages.import': 25,
    'threads.get': 40, 'threads.list': 5, 'threads.trash': 20,
    'messages.send': 100, 'labels.create': 5, 'labels.list': 5,
    'filters.create': 10, 'filters.list': 5, 'messages.batchModify': 5,
  },
};

const state = { used: 0, windowStart: Date.now(), waited: 0, requests: 0 };

function costOf(method) { return QUOTA.units[method] || 10; }

function budgetLeft() {
  const el = Date.now() - state.windowStart;
  if (el >= 60000) { state.used = 0; state.windowStart = Date.now(); return QUOTA.perMinutePerUser; }
  return QUOTA.perMinutePerUser - state.used;
}

let promiseQueue = Promise.resolve();

/** Asteapta pana cand bugetul permite apelul. Returneaza cand se poate. */
async function reserve(method) {
  const cost = costOf(method);

  const p = promiseQueue.then(async () => {
    while (budgetLeft() < cost) {
      const waitMs = 60000 - (Date.now() - state.windowStart) + 250;
      state.waited += waitMs;
      await new Promise(r => setTimeout(r, waitMs));
    }
    state.used += cost;
    state.requests++;
  });

  promiseQueue = p.catch(() => {});
  return p;
}

/** Backoff exponenial pentru 429 / rateLimitExceeded */
function backoffMs(attempt) {
  return Math.min(32000, 1000 * Math.pow(2, attempt)) + Math.floor(Math.random() * 500);
}

module.exports = { QUOTA, state, costOf, budgetLeft, reserve, backoffMs };
