# Memory maintenance — capcanele instrumentelor host

## `memory_read` NORMALIZEAZĂ textul; `memory_search` îl dă raw

Observat 2026-10-24: `memory_read` a afișat „**prezentat**", dar fișierul stă
efectiv „**prezintat**". `memory_search` pe același fragment a returnat textul
brut, diferit de cel afișat de read.

**Consecință:** un `old_string` copiat din output-ul lui `memory_read` poate
eșua cu `OLD_STRING_NOT_FOUND` chiar dacă fragmentul există în fișier.

**Workflow sigur:**
1. Copiază din `memory_read`.
2. Dacă `memory_edit` dă `OLD_STRING_NOT_FOUND`, **nu presupune că textul nu
   există** — caută fragmentul cu `memory_search` (returnează textul real, cu
   `L<linie>`) și corectează diferențele de caractere.
3. Testează mai întâi cu `old_string` scurt (un cuvânt, o linie) ca să
   localizezi exact caracterul problematic.

## Alte capcane măsurate

- `memory_edit` cu `old_string` = `new_string` e acceptat (no-op) — util ca test
  de potrivire.
- `replace_all: true` pe `"\n\n\n"` → `"\n\n"` curăță rândurile goale, dar
  replace-urile se consumă non-overlapping: o secvență de 4 newline-uri devine
  3, nu 2. Rulează de mai multe ori sau folosește `"\n\n\n\n"` primul.
- `replace_all` pe `"\n\n"` → `"\n"` șterge TOATE rândurile goale dintre secțiuni
  (afișarea devine un bloc continuu). Nu-l folosi ca „curățare" — e o
  degradare de formatare.
- `memory_topic_edit` acceptă blocuri mari, dar un singur caracter diferit
  (ex. `în place` vs `in place`) face match-ul să cadă.
- `memory_topic_create` e create-only; topicul vechi se șterge cu
  `memory_topic_delete` după ce noul îl înlocuiește.
- `memory_summary_write` cere două apeluri: primul returnează `confirm_token`
  + preview, al doilea commită cu același content + token.
- `memory_summary_write` e limitat la 4KB și maximum 15 intrări.


## Regula de aur: arhivezi înainte să tai (POPY, 2026-10-24)

**Optimizarea memoriei fără arhivarea a ce ai tăiat e EROARE, nu optimizare.**

Flux: `SNAPSHOT → MANIFEST → COMMIT → PUSH → APOI tai → COMMIT → PUSH`.
Dacă push-ul arhivei pică, nu tai nimic.

- **Unde arhivez:** `docs/arhiva/memorie/<DATA>-<etichetă>/` în repo
  `apvizual-max/MAVIS-CLOUD` — `MEMORY.md` + `topics/` + `MANIFEST.md` (sha256).
- **Cum:** `mavis-tools/memory-snapshot.js` (`--from <dir>`, `--stdin`,
  `--verify <etichetă>` → exit 1 dacă arhiva lipsește, `--list`).
- **Procedura:** `docs/PROCEDURA-OPTIMIZARE-MEMORIE.md` · regula e și în
  `AGENTS.md` (Regula 4).
- **Topic șters → întâi arhivezi**, apoi `memory_topic_delete`.
- **Task cloud:** snapshot săptămânal duminica 23:00 (task `455764418027683`).
  Doar arhivează, nu taie.
- **Secrete:** se elimină din memorie **înainte** de arhivare — repo public.

**Ce s-a întâmplat în 2026-10-24:** am tăiat ~13KB din memorie fără arhivare
(≈23KB → 9,9KB). POPY: „Optimizările făcute FĂRĂ arhivare se cheamă ERORI".
Recuperarea: arhiva reconstructă în `docs/arhiva/memorie/2026-10-24-pre-optimizare/`
(din output `memory_read` — deci **nu byte-identică** cu originalul; de aceea
scriptul scrie arhiva **din fișier**, nu din view).
