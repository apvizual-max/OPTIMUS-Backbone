#!/usr/bin/env node
/**
 * CLASIFICATOR DE MESAJE — ce cere cu adevărat răspuns de la om.
 *
 * READ-ONLY: nu atinge Gmail. Lucrează doar pe rândurile deja aduse de
 * report-simulate-sort.js (care are snippet + subject + from + date).
 *
 * PATRUL: 4 clase, derivate din DATE, nu din hardcoding.
 *   A. needs-reply  — cer un răspuns explicit (de la o persoană, nu de la un robot)
 *   B. needs-action — cer o decizie (alerte de job care chiar bat cu profilul)
 *   C. fyi           — newsletter / promoție / noutate, fără acțiune
 *   D. noise        — zgomot din pipeline-ul propriu (bot-uri de pe repo-uri)
 *
 * Semnalele sunt scrise ca reguli, ca să funcționeze și mâine, pe alte mesaje.
 */
const fs = require('fs');

// ---- profilul de căutare al lui Alex (rol + piață) ----
const DESIGN_KW = [
  'art director', 'creative director', 'creative lead', 'art mid', 'head of creative',
  'graphic design', 'graphic designer', 'senior graphic', 'visual design', 'visual designer',
  'brand designer', 'product designer', 'ui/ux', 'ux/ui', 'ux designer', 'ui designer',
  'content designer', 'creative designer', 'design', 'creativ',
];
const LOC_KW = ['bucuresti', 'bucharest', 'ilfov', 'remote', 'cluj', 'iasi', 'timisoara', 'brasov'];

// ---- zgomot cunoscut ----
const NOISE_FROM = /github|jules|google-labs|actions@|sentinel|dependabot|coderabbit/i;
// ---- promotii / marketing ----
const PROMO_FROM = /goatacademy|mercor\.com|marketing|promo|sale|deal/i;
const PROMO_TEXT = /last seats|sign up|spectaculo|black friday|discount|reducere|free trial|join us|inregistreaza/i;
// ---- newsletter / digest ----
const NEWS_FROM = /newsletter|substack|news@|digest|mailchimp|beehiiv|twine|medium\.com/i;
const NEWS_TEXT = /weekly|newsletter|edition|ed\.\s*$|dumitrascu|smart city/i;
// ---- robot: local-part de tip no-reply ----
const ROBOT_LOCAL = /^(no-?reply|do-?not-?reply|donotreply|noreply|notify|notifications?|alerts?|automated|mailer|newsletter|newsletters|news|bounce|postmaster)/i;
// ---- ALERTA DE SECURITATE: cere verificare umana, chiar daca vine de la robot ----
const SECURITY_FROM = /accounts\.google\.com|@google\.com|security|alert@/i;
const SECURITY_TEXT = /security alert|alerta de securitate|new sign-in|new device|dispozitiv nou|someone may be trying|acces neautorizat|verifica.*activit|check activity|secure your account/i;
// ---- CI / workflow esuat: cere actiune, chiar daca e "zgomot de pipeline" ----
const CI_FAIL_SUBJECT = /\brun failed\b|workflow.*fail|\bfailed\b|\bfailure\b|build failed|eroare/i;
const CI_FROM = /notifications@github\.com|githubactions|@github\.com/i;
// ---- CONTUL CERE O ACTIUNE (parola noua, confirmare, reset) ----
const ACCOUNT_TEXT = /trebuie sa (aleg|schimb|confirm|setez|verific)|aleg(e|eti) o parola|schimb(a|i) parola|parola noua|new password|reset your password|confirm(a|ati) (contul|adresa|email)|verifica(i) adresa|completeaz(a) profilul|verificati adresa/i;
// ---- semnale ca un mesaj sa ceara raspuns ----
const REPLY_TEXT = /action requested|opportunity|interview|invitatie|invitație|raspuns|răspuns|your application|aplicatia ta|aplicatia ta a fost|reply to|confirm|accept|offer|contract|negotiat|trebuie sa|urgent|deadline|scadenta/i;
// ---- semnale ca un mesaj sa ceara o decizie legata de joburi ----
const JOB_ALERT = /bestjobs|jooble|indeed|hipo|jobleads|recruit|linkedin job|job alert|joburi|locuri de munca|job openings/i;

const _rxCache = new Map();
function hasWord(text, w) {
  let rx = _rxCache.get(w);
  if (!rx) {
    const esc = w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    rx = new RegExp('(^|[^a-z0-9])' + esc + '($|[^a-z0-9])', 'i');
    _rxCache.set(w, rx);
  }
  return rx.test(text);
}
function hasAny(text, list) { return list.some(k => hasWord(text, k)); }

/** Extrage numele de afisare din headerul From. */
function displayName(from) {
  const m = (from || '').match(/^\s*"?([^"<]*?)"?\s*</);
  return (m ? m[1] : from || '').replace(/\s+/g, ' ').trim();
}
function localPart(from) {
  const m = (from || '').match(/<([^>]+)>/);
  return (m ? m[1] : from || '').split('@')[0].toLowerCase();
}
/** Nume propriu: 2+ cuvinte capitalizate (sau 1 cuvant lung, ex. "Chloe"). */
function looksLikePerson(name) {
  const n = (name || '').replace(/[@_].*$/, '').trim();
  if (!n || /\d/.test(n)) return false;
  const words = n.split(/\s+/).filter(w => /^[A-ZĂÂÎȘȚŞŢ]/.test(w));
  return words.length >= 1 && words.join(' ').length >= 4 && !/newsletter|jobs|alerts?|no-?reply/i.test(n);
}

/**
 * @param {Array} rows rânduri din report-simulate-sort.js
 * @returns {{buckets:Object, counts:Object, all:Array}}
 */
function triage(rows) {
  const out = [];
  for (const r of rows) {
    const from = r.from || '';
    const subj = r.subject || '';
    const snip = r.snippet || '';
    // CORPUL intra in decizie. Fragmentul de text e trunchiat la ~200 de
    // caractere si contine doar antetul; corpul e cel care arata ca un email
    // de alerta cere de fapt confirmare/verificare. (Cost: 0 cereri in plus —
    // corpul vine deja in raspunsul format=full al simulate-sort.)
    //
    // DAR: semnalul "acum cere raspuns" se citeste DOAR din antet+fragment.
    // Un disclaimer legal ("does not constitute an offer to purchase") contine
    // cuvintele-cheie si transforma o reclamatie comerciala intr-un mesaj
    // care "cere raspuns". Antetul + fragmentul spun intentia reala.
    const body = r.body || '';
    const headText = subj + ' ' + snip;              // intentia mesajului
    const text = headText + ' ' + body;              // intentia + continutul
    const dn = displayName(from);
    const lp = localPart(from);
    const isRobot = ROBOT_LOCAL.test(lp);
    const isDesign = hasAny(text, DESIGN_KW);
    const isLoc = hasAny(text, LOC_KW);
    const isJobAlert = JOB_ALERT.test(from) || JOB_ALERT.test(subj);

    let cls, why;
    if (SECURITY_FROM.test(from) && SECURITY_TEXT.test(text)) {
      cls = 'needs-action'; why = 'alerta de securitate — cere verificare umana';
    } else if (CI_FROM.test(from) && CI_FAIL_SUBJECT.test(subj)) {
      cls = 'needs-action'; why = 'workflow CI esuat — cere actiune';
    } else if (ACCOUNT_TEXT.test(text)) {
      cls = 'needs-action'; why = 'contul cere o actiune (parola / confirmare)';
    } else if (NOISE_FROM.test(from)) {
      cls = 'noise'; why = 'zgomot din pipeline-ul propriu';
    } else if (isJobAlert && isDesign) {
      cls = 'needs-action'; why = 'alerta de job cu rol de design';
    } else if (isJobAlert) {
      cls = 'job-alert-other'; why = 'alerta de job, dar nu atinge profilul de design';
    } else if (NEWS_FROM.test(from) || NEWS_TEXT.test(subj)) {
      // newsletter INAINTE de semnalul de raspuns: un digest poate conține
      // cuvinte ca "interview" fara sa ceara nimic (ex. "Interview with ...")
      cls = 'fyi'; why = 'newsletter';
    } else if (PROMO_FROM.test(from) || PROMO_TEXT.test(text)) {
      // promo INAINTE de semnalul de raspuns: o casa de newslettere/promotii
      // scrie cu numele omului, dar nu cere raspuns de la om.
      cls = 'fyi'; why = 'promotie / oferta';
    } else if (REPLY_TEXT.test(headText) && !isRobot && looksLikePerson(dn)) {
      cls = 'needs-reply'; why = 'cere raspuns explicit, de la o persoana';
    } else if (isRobot) {
      cls = 'fyi'; why = 'robot, fara cerere de actiune';
    } else {
      cls = 'fyi'; why = 'fara semnal de actiune';
    }
    out.push({ ...r, cls, why, displayName: dn, isDesign, isLoc, isJobAlert });
  }
  const buckets = { 'needs-reply': [], 'needs-action': [], 'job-alert-other': [], fyi: [], noise: [] };
  for (const r of out) buckets[r.cls].push(r);
  const order = { 'needs-reply': 0, 'needs-action': 1, 'job-alert-other': 2, fyi: 3, noise: 4 };
  for (const k of Object.keys(buckets)) buckets[k].sort((a, b) => new Date(b.date) - new Date(a.date));
  const counts = Object.fromEntries(Object.keys(buckets).map(k => [k, buckets[k].length]));
  return { buckets, counts, all: out.sort((a, b) => order[a.cls] - order[b.cls] || new Date(b.date) - new Date(a.date)) };
}

module.exports = { triage, DESIGN_KW, LOC_KW };

if (require.main === module) {
  const src = process.argv[2] || '/workspace/Mavis/mavis-tools/report-simulate-sort.json';
  const rows = JSON.parse(fs.readFileSync(src, 'utf8')).rows || [];
  const t = triage(rows);
  console.log('COUNTS: ' + JSON.stringify(t.counts));
  for (const cls of ['needs-reply', 'needs-action', 'job-alert-other', 'fyi', 'noise']) {
    console.log(`\n=== ${cls} (${t.buckets[cls].length}) ===`);
    t.buckets[cls].slice(0, 12).forEach(r =>
      console.log(`  ${r.date.slice(0, 22)} | ${(r.displayName || r.from).slice(0, 34).padEnd(34)} | ${(r.subject || '').slice(0, 56).padEnd(56)} | ${r.why}`));
  }
}
