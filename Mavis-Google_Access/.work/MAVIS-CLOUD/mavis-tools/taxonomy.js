// TAXONOMIA ETICHETELOR GMAIL — sursa unică de adevăr.
//
// DE CE EXISTĂ: pe 27.10.2026 etichetele MAVIS/* au fost rearanjate între
// noaptea (Mavis Local, pe calculatorul lui Alex). Doar "MAVIS/Joburi" și-a
// păstrat prefixul; celelalte 7 au primit alte nume și alte ierarhii:
//   MAVIS/AI si comunitati  -> AI Folder/AI si Comunitati
//   MAVIS/Social            -> Socials
//   MAVIS/Newsletter        -> Newsletter
//   MAVIS/Finante           -> Finante
//   MAVIS/Personal          -> Personal
//   MAVIS/De raspuns        -> De raspuns
//   MAVIS/Facturi si conturi-> Facturi si Conturi
//   (nou)                   -> Optimus CD   [categorie "agenți", filtrul care MERGE]
//
// Scriptele de raport nu mai scriu numele etichetelor prin cod — le rezolvă
// de aici, la runtime, din etichetele vii. Dacă Alex rearanjează din nou
// taxonomy, se schimbă UN LOC: lista de mai jos.
//
// REGULĂ: dacă o categorie nu se rezolvă, scriptul RAPORTEAZĂ lipsa (nu
// tace și nu scrie 0). Zero-ul mascat e mai periculos decât eroarea.

/** Categoriile de măsurat. `key` e stabil (nu se schimbă), `aliases` sunt numele posibile. */
const CATEGORIES = [
  { key: 'joburi',      title: 'Joburi',                aliases: ['MAVIS/Joburi', 'Joburi'] },
  { key: 'ai',          title: 'AI si comunitati',       aliases: ['MAVIS/AI si comunitati', 'AI si comunitati', 'AI Folder/AI si Comunitati'] },
  { key: 'social',      title: 'Social',                aliases: ['MAVIS/Social', 'Social', 'Socials'] },
  { key: 'newsletter',  title: 'Newsletter',            aliases: ['MAVIS/Newsletter', 'Newsletter'] },
  { key: 'finante',     title: 'Finante',               aliases: ['MAVIS/Finante', 'Finante'] },
  { key: 'personal',    title: 'Personal',              aliases: ['MAVIS/Personal', 'Personal'] },
  { key: 'actiune',     title: 'De raspuns',            aliases: ['MAVIS/De raspuns', 'MAVIS/Actiune - de raspuns', 'De raspuns'] },
  { key: 'facturi',     title: 'Facturi si conturi',    aliases: ['MAVIS/Facturi si conturi', 'Facturi si Conturi', 'Facturi si conturi'] },
  { key: 'agenti',      title: 'Agenti (pipeline propriu)', aliases: ['MAVIS/Agenti', 'Agenti', 'Optimus CD'] },
];

/** Normalizează un nume de etichetă: ultima componentă după '/' sau ' | '. */
function normalize(name) {
  const s = String(name || '');
  const cut = Math.max(s.lastIndexOf('/'), s.lastIndexOf(' | '));
  const last = cut >= 0 ? s.slice(cut + 1) : s;
  return last.trim().toLowerCase().replace(/\s+/g, ' ');
}

/**
 * Rezolvă categoriile pe etichetele vii.
 * @param {Array<{name:string,id:string}>} liveLabels
 * @returns {{resolved:Array, missing:Array, byKey:Object}}
 */
function resolve(liveLabels) {
  const labels = liveLabels || [];
  const norm = new Map();
  for (const l of labels) {
    const n = normalize(l.name);
    if (!norm.has(n)) norm.set(n, l);       // prima potrivire câștigă
  }

  const resolved = [], missing = [], byKey = {};
  for (const c of CATEGORIES) {
    let hit = null;
    for (const a of c.aliases) {
      const n = normalize(a);
      if (norm.has(n)) { hit = norm.get(n); break; }
    }
    if (hit) {
      const row = { key: c.key, title: c.title, name: hit.name, id: hit.id };
      resolved.push(row);
      byKey[c.key] = row;
    } else {
      missing.push({ key: c.key, title: c.title, aliases: c.aliases });
    }
  }
  return { resolved, missing, byKey };
}

/** Numele etichetei pentru o categorie, sau null dacă nu e rezolvată. */
function labelName(byKey, key) {
  return byKey && byKey[key] ? byKey[key].name : null;
}

module.exports = { CATEGORIES, normalize, resolve, labelName };
