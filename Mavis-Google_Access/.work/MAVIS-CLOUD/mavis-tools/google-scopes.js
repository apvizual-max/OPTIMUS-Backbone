#!/usr/bin/env node
/**
 * SCOPE-URI GOOGLE — SINGURA SURSA DE ADEVAR.
 *
 * De ce exista: pana la 28 oct 2026, cinci scripturi fiecare aveau propria
 * lista de 6 scope-uri (drive, gmail.modify, calendar, documents,
 * spreadsheets, presentations). Cand s-a regenerat un link de autorizare,
 * tokenul nou venea cu DOAR acele 6 — pierzand `gmail.settings.basic`
 * (fara care filtrele Gmail nu se pot repara din cloud), plus contacts,
 * chat, forms, script.projects, youtube, drive.appdata, books.
 *
 * MESAJUL: lista de scope-uri trebuie sa fie UN SINGUR LOC. Nu o lista
 * per-script.
 *
 * LISTA DE MAI JOS este cea obtinuta efectiv la re-consimtamantul din
 * 2026-10-28 (27 scope-uri, appul IN PRODUCTION). Reproduce exact ce a
 * fost acordat, ca un viitor re-consimtamant sa nu degradeze tokenul.
 *
 * NOTA: `include_granted_scopes=true` (in linkurile de autorizare) face ca
 * un consimtamant nou sa NU revokeze scope-urile deja acordate. Deci chiar
 * si o lista mai scurta nu ar " pierde" nimic la prima re-autentificare —
 * dar ar impune un consimtamant suplimentar, pe care sa-l evitam.
 */

const AUTH = 'https://www.googleapis.com/auth/';

/** Scope-uri de baza — absolut necesare, verificate functional. */
const CORE = [
  AUTH + 'drive',
  AUTH + 'gmail.modify',
  AUTH + 'calendar',
  AUTH + 'documents',
  AUTH + 'spreadsheets',
  AUTH + 'presentations',
];

/**
 * Scope-uri extinse — acordate explicit de POPY pe 28 oct 2026.
 * Fiecare cu motivul pentru care e cerut.
 */
const EXTENDED = {
  'https://mail.google.com/':
    'Acces COMPLET la Gmail (interfata + toate setarile, inclusiv filtre). ' +
    'Este scope-ul care acopera gestionarea filtrelor la nivel de cont.',
  [AUTH + 'gmail.settings.basic']:
    'CITIRE + SCRIERE filtre Gmail. FARA ASTA: filters PATCH/POST raspunde 403. ' +
    'Fara asta, reparam filtrele doar de pe masina lui POPY.',
  [AUTH + 'gmail.readonly']: 'Citire Gmail fara risc de scriere.',
  [AUTH + 'gmail.compose']: 'Drafturi. NU trimite fara comanda explicita a lui POPY.',
  [AUTH + 'gmail.send']: 'Trimitere. Regula: POPY apasa butonul, agentul nu trimite.',
  [AUTH + 'drive.readonly']: 'Citire Drive fara drepturi de scriere.',
  [AUTH + 'drive.appdata']:
    'Datele aplicatiei in Drive — fisierele ascunse ale aplicatiei. ' +
    'Permite salvarea configuratiei Mavis Cloud fara sa atinga fisierele lui POPY.',
  [AUTH + 'calendar.events']: 'Creare/modificare evenimente din Calendar.',
  [AUTH + 'contacts']: 'Google Contacts — lista de contacte.',
  [AUTH + 'chat.spaces.readonly']: 'Citire spatii Google Chat.',
  [AUTH + 'chat.messages']: 'Mesaje Google Chat.',
  [AUTH + 'forms.body']: 'Citire/editare corp formulare Google Forms.',
  [AUTH + 'forms.responses.readonly']: 'Citire raspunsuri Google Forms.',
  [AUTH + 'script.projects']: 'Google Apps Script — proiecte scriptate.',
  [AUTH + 'books']: 'Google Books.',
  [AUTH + 'youtube.readonly']: 'Citire YouTube.',
  [AUTH + 'youtube.upload']: 'Publicare YouTube. Nu se foloseste fara comanda.',
  [AUTH + 'photospicker.mediaitems.readonly']:
    'Google Photos Picker (readonly). NOTA: nu e photoslibrary.readonly — ' +
    'API-ul Photos Library (albumuri) are nevoie de scope separat, ' +
    'de aceea photos:albums da 403 si in prezent.',
  [AUTH + 'userinfo.email']: 'Adresa de email a utilizatorului.',
  [AUTH + 'userinfo.profile']: 'Profilul de utilizator.',
  'openid': 'Identitate standard OpenID.',
};

/** Lista completa, in ordine stabila (pentru comparatii deterministe). */
const ALL = [
  ...CORE,
  ...Object.keys(EXTENDED).sort(),
];

module.exports = {
  AUTH,
  CORE,
  EXTENDED,
  ALL,
  /** Scope-uri care cer aprobare suplimentara la consent screen (sensibil). */
  SENSITIVE: [
    AUTH + 'gmail.send',
    AUTH + 'gmail.compose',
    AUTH + 'youtube.upload',
    AUTH + 'chat.messages',
  ],
  /** Scope-uri care NU functioneaza si n-au fost incluse. */
  KNOWN_UNAVAILABLE: {
    'photoslibrary.readonly':
      'Photos Library API (albumuri) — 403 "insufficient authentication scopes". ' +
      'Nu e in lista: n-a fost acordat, iar API-ul Photos Library e deprecated ' +
      'in favoarea Photos Picker.',
    'drive.metadata.readonly':
      'Nu e nevoie — drive.readonly si drive acopera deja.',
  },
};

/** CLI: `node mavis-tools/google-scopes.js` — afiseaza lista. */
if (require.main === module) {
  const s = module.exports;
  console.log(`\n=== SCOPE-URI GOOGLE (${s.ALL.length}) — sursa unica de adevar ===\n`);
  console.log('  CORE (verificate functional):');
  s.CORE.forEach((x) => console.log('    ' + x.replace(AUTH, '')));
  console.log('\n  EXTINSE (acordate 28 oct 2026):');
  for (const [k, why] of Object.entries(s.EXTENDED)) {
    console.log(`    ${k.replace(AUTH, '').padEnd(38)} ${why}`);
  }
  console.log('\n  SENSITIVE (nu se folosesc fara comanda explicita):');
  s.SENSITIVE.forEach((x) => console.log('    ' + x.replace(AUTH, '')));
  console.log('\n  INCLUSE IN TOKENUL CURENT: ' + s.ALL.length + ' scope-uri');
  console.log('  (tokenul acordat pe 28 oct are 27 — diferenta e openid, care se adauga automat)\n');
}
