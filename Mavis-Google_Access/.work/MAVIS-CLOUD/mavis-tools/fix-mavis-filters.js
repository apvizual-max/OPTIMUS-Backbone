#!/usr/bin/env node
/**
 * REPARATIA FILTRELOR Gmail MAVIS/* — pregătită 2026-10-25, neaplicată din cloud.
 *
 * DE CE NU S-A APLICAT DIN CLOUD: tokenul din cloud are `gmail.modify`, dar NU
 * `gmail.settings.basic`. Fara acest scope, `filters PATCH` raspunde 403
 * "insufficient scopes". Deci se ruleaza de pe masina lui Alex, unde scope-ul exista.
 *
 * CE REPARA (doua defecte, masurate la 2026-10-25):
 *   1) CRITERII: in cautarea Gmail, `()` = SI, `{}` = SAU. Cele 5 filtre scriau
 *      `from:(jooble bestjobs hipo indeed jobleads linkedin)`, deci cereau un
 *      expeditor cu TOATE cuvintele simultan -> 0 mesaje lovite in 30 de zile.
 *      Cu `{}` ar fi prins 2967 mesaje in 30 de zile.
 *   2) ACTIUNE: `addLabelIds` era vid -> chiar daca filtrul ar fi lovit ceva,
 *      nu ar fi pus eticheta MAVIS/*.
 *
 * SIGURANTA:
 *   - starea curenta a celor 5 filtre se salveaza in
 *     `mavis-tools/filters-state-before-repair.json` -> rollback exact.
 *   - se atinge DOAR cele 5 filtre MAVIS/*; celelalte 13 raman neatinse.
 *   - NICIO stergere, NICIO trimitere. Orice PATCH se poate anula cu
 *     `--rollback`.
 *   - etichetele MAVIS/* se pot reface pe orice mesaj, oricand.
 *
 * UTILIZARE:
 *   node fix-mavis-filters.js --dry-run     # arata ce ar face, nu scrie nimic
 *   node fix-mavis-filters.js               # aplica reparatia
 *   node fix-mavis-filters.js --rollback    # readuce starea salvata
 */
const fs = require('fs');
const path = require('path');
const k = require('./kit.js');
const taxonomy = require('./taxonomy.js');

const DIR = __dirname;
const STATE_FILE = path.join(DIR, 'filters-state-before-repair.json');
const DRY = process.argv.includes('--dry-run');
const ROLLBACK = process.argv.includes('--rollback');

/** Criteriile celor 5 filtre, cum sunt scrise acum in Gmail (masurate live, nu ghicite). */
const MAVIS_CRITERIA = [
  'from:(jooble bestjobs hipo indeed jobleads linkedin) OR subject:(job angajare vacanta oportunitate)',
  'from:(substack goatacademy aiautomationsociety sadhguru beehiiv twine) OR subject:(AI artificial intelligence)',
  'from:(skool facebook instagram pinterest tiktok polibrawl)',
  'from:(noreply no-reply newsletter digest mail@ info@ news@ updates@)',
  'from:(kraken tradingview bitunix coinbase binance) OR subject:(factura investitie trading)',
];

/**
 * Categoria pe care o eticheteaza fiecare filtru.
 *
 * AICI stau doar CHEILE, nu numele etichetelor. Numele se rezolva LIVE,
 * prin taxonomy.js - sursa unica de adevar.
 *
 * MASURAT 2026-10-27: etichetele au fost rearanjate in noaptea, iar
 * scriptul cu numele hardcodate sartea 4 filtre din 5 ("eticheta nu
 * exista"), desi filtrele erau prezente. Filtrele ramasesc reparamabile:
 * se repara adevarul lor, nu numele de acum al etichetei.
 */
const CATEGORY_KEY = {
  'from:(jooble bestjobs hipo indeed jobleads linkedin) OR subject:(job angajare vacanta oportunitate)': 'joburi',
  'from:(substack goatacademy aiautomationsociety sadhguru beehiiv twine) OR subject:(AI artificial intelligence)': 'ai',
  'from:(skool facebook instagram pinterest tiktok polibrawl)': 'social',
  'from:(noreply no-reply newsletter digest mail@ info@ news@ updates@)': 'newsletter',
  'from:(kraken tradingview bitunix coinbase binance) OR subject:(factura investitie trading)': 'finante',
};

/**
 * `from:(a b c)` -> `from:{a b c}`.
 * In cautarea Gmail: parantezele = SI, acoladele = SAU.
 * Grupele vide se elimina, ca sa nu lase un criteriu gol.
 */
function toOrGroups(query) {
  return query.replace(/\(([^()]*)\)/g, (m, inner) => {
    const parts = inner.trim().split(/\s+/).filter(Boolean);
    return parts.length ? '{' + parts.join(' ') + '}' : '';
  });
}

async function loadFilters() {
  const fl = await k.req('GET', 'https://gmail.googleapis.com/gmail/v1/users/me/settings/filters');
  return fl.filter || [];
}

(async () => {
  const labels = await k.gmail.labels();
  const name2id = {};
  (labels.labels || []).forEach(l => { name2id[l.name] = l.id; });
  // Numele etichetelor se rezolva pe etichetele VII, prin taxonomy.js.
  const tax = taxonomy.resolve(labels.labels || []);
  if (tax.missing.length) {
    console.log('  (categorii nerezolvate pe etichetele vii: ' + tax.missing.map(m => m.key).join(', ') + ')');
  }

  // ---- ROLLBACK ----
  if (ROLLBACK) {
    if (!fs.existsSync(STATE_FILE)) {
      console.log('Nu exista ' + STATE_FILE + ' — nu am ce readuce.');
      process.exit(1);
    }
    const saved = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
    const live = await loadFilters();
    for (const f of saved.filters) {
      // API-ul Gmail NU are PATCH pe filtre. Singurele cai de mutatie sunt
      // DELETE si CREATE, deci rollback-ul recunoaste filtrul viu prin
      // CRITERIUL lui (cel reparat), nu prin id - id-ul se schimba la
      // recreare.
      const repairedQuery = toOrGroups((f.criteria && f.criteria.query) || '');
      const liveFilter = (live || []).find(z => (z.criteria && z.criteria.query) === repairedQuery);
      if (!liveFilter) {
        console.log(`  rollback ${f.name}: filtrul viu cu criteriul reparat nu a fost gasit - nimic de readus`);
        continue;
      }
      await k.req('DELETE', `https://gmail.googleapis.com/gmail/v1/users/me/settings/filters/${liveFilter.id}`);
      const r = await k.req('POST', 'https://gmail.googleapis.com/gmail/v1/users/me/settings/filters', {
        criteria: { query: (f.criteria && f.criteria.query) || '' },
        action: f.action || { removeLabelIds: ['UNREAD', 'INBOX'] },
      });
      console.log(`  rollback ${f.name}: readus cu criteriu=${r.criteria?.query} add=${JSON.stringify(r.action?.addLabelIds || [])}`);
    }
    console.log('Starea de dinainte a fost readusa. Filtrele celelalte nu au fost atinse.');
    return;
  }

  const all = await loadFilters();
  const byQuery = {};
  for (const f of all) if (f.criteria && f.criteria.query) byQuery[f.criteria.query] = f;

  const targets = MAVIS_CRITERIA
    .map(q => ({ q, f: byQuery[q] }))
    .filter(x => x.f);

  console.log('Filtre MAVIS gasite: ' + targets.length + ' / ' + MAVIS_CRITERIA.length);
  if (targets.length < MAVIS_CRITERIA.length) {
    console.log('ATENTIE: un criteriu nu mai exista in Gmail — filtrul a fost modificat manual sau sters.');
    MAVIS_CRITERIA.filter(q => !byQuery[q]).forEach(q => console.log('  lipseste: ' + q));
  }

  // ---- salveaza starea de dinainte (o singura data) ----
  const before = targets.map(x => {
    const row = tax.byKey[CATEGORY_KEY[x.q]];
    return {
      id: x.f.id, name: row ? row.name : 'necunoscut (' + (CATEGORY_KEY[x.q] || '?') + ')',
      criteria: x.f.criteria, action: x.f.action,
    };
  });
  if (!fs.existsSync(STATE_FILE)) {
    fs.writeFileSync(STATE_FILE, JSON.stringify({ savedAt: new Date().toISOString(), note: 'starea filtrelor MAVIS/* inainte de reparatie — pentru rollback', filters: before }, null, 2));
    console.log('Starea de dinainte salvata -> ' + STATE_FILE);
  } else {
    console.log('Starea de dinainte exista deja, nu o suprascriu.');
  }

  for (const x of targets) {
    const row = tax.byKey[CATEGORY_KEY[x.q]];
    const labelName = row ? row.name : null;
    const labelId = row ? row.id : null;
    if (!labelId) { console.log('  !! categoria "' + (CATEGORY_KEY[x.q] || '?') + '" nu se rezolva pe etichetele vii — sarit'); continue; }
    const fixedQuery = toOrGroups(x.q);
    const action = {
      addLabelIds: [labelId],
      removeLabelIds: (x.f.action && x.f.action.removeLabelIds) ? x.f.action.removeLabelIds : ['UNREAD', 'INBOX'],
    };
    if (DRY) {
      console.log(`  [DRY] ${labelName.padEnd(24)} criteriu: ${x.q}`);
      console.log(`        ->             criteriu: ${fixedQuery}`);
      console.log(`        actiune acum: ${JSON.stringify(x.f.action)}`);
      console.log(`        actiune noua: ${JSON.stringify({ addLabelIds: [labelId], removeLabelIds: action.removeLabelIds })}`);
      continue;
    }
    // API-ul Gmail NU are PATCH pe filtre. Masurat 2026-10-27 din
    // discovery document (gmail v1): pe gmail.users.settings.filters exista
    // doar DELETE, GET, LIST si CREATE. PATCH intoarce 404 "Method not
    // found" - de aceea scriptul nu a fost aplicat niciodata.
    //
    // ORDINEA: CREATE intai, DELETE abia dupa. Daca CREATE picte, filtrul
    // vechi e intact; daca DELETE pica, ramane o dublura cu aceeasi actiune
    // (eticheta se aplica o data, nu de doua ori) - si e raportata.
    const created = await k.req('POST', 'https://gmail.googleapis.com/gmail/v1/users/me/settings/filters', {
      criteria: { query: fixedQuery },
      action,
    });
    let deleted = 'nu';
    try {
      await k.req('DELETE', `https://gmail.googleapis.com/gmail/v1/users/me/settings/filters/${x.f.id}`);
      deleted = 'da';
    } catch (e) {
      console.log(`  !! vechiul filtru ${x.f.id} nu a putut fi sters: ${e.message.slice(0, 120)}`);
    }
    console.log(`  REPARAT ${labelName.padEnd(28)} criteriu=${created.criteria?.query} | add=${JSON.stringify(created.action?.addLabelIds || [])} | vechi_sters=${deleted}`);
  }

  if (!DRY) {
    const v = await loadFilters();
    console.log('\n=== VERIFICARE ===');
    for (const x of targets) {
      const fixedQuery = toOrGroups(x.q);
      const y = (v || []).find(z => (z.criteria && z.criteria.query) === fixedQuery);
      const row = tax.byKey[CATEGORY_KEY[x.q]];
      console.log(`  ${(row ? row.name : '').padEnd(28)} gasit=${Boolean(y)} criteriu=${y?.criteria?.query} add=${JSON.stringify(y?.action?.addLabelIds || [])} remove=${JSON.stringify(y?.action?.removeLabelIds || [])}`);
    }
    console.log(`  celelalte ${(v || []).length - targets.length} filtre: neatinse`);
  }
})().catch((e) => { console.error('ERR:', e.message); process.exit(1); });
