# MavisCloud-Gmail

**Document pentru încărcare în notebookul `MavisCloud-Gmail`**
Pregătit de Mavis Cloud · 2026-10-12 · **actualizat 2026-10-27 (măsurat live)**

Gmail-ul lui POPY: sortare, etichete, flux de joburi, spam

---

**Stare (27 oct 2026, măsurată live)** — 83.505 mesaje în cont · 20.780 etichetate · Trash 626 · Spam 2.

**Taxonomia s-a schimbat** — nu mai sunt 8 etichete `MAVIS/*`, sunt 36 în 7 familii.
Doar `MAVIS/Joburi` a supraviețuit; restul au pierdut prefixul sau au fost mutate.
Detalii + corespondența veche→nouă: `10-GMAIL/TAXONOMIE-2026-10-27.md`.

**Cele mai mari** — MAVIS/Joburi 8.125 · Newsletter 4.558 · Socials 2.864 ·
AI Folder/AI si Comunitati 2.499 · De raspuns 1.750 · Optimus CD 687

**Reguli** — 19 filtre server-side, toate validate la 27 oct: 0 sparte.
Etichetele fără filtră automat: `De raspuns`, `Personal`, `Facturi si Conturi`
(triaj manual).

**Cum se sortează** — mavis-tools/email-sort-full.js — parcurge tot inbox-ul, fără fereastră de vârstă.

**Regulă de măsurare** — Numără cu paginare. resultSizeEstimate e plafonat și nu e numărătoare.

**Regulă CRITICĂ** — Nu număra niciodată cât rulează altă operațiune Gmail. Zero înseamnă nemăsurat, nu gol.

**Capcană reparată** — MAVIS/Actiune - de raspuns conținea o linie, deci era de nescărcat. Rebrendată MAVIS/De raspuns.

**Capcană reparată** — .replace(' ','') ștergea doar primul spațiu și producea zerouri false.

**Capcană reparată** — Etichetele cu spații cer ghilimele la căutare.

**Spam** — 106 fire scoase din spam în inbox la prima curățare.

---

*2026-10-27 · Mavis Cloud · fișier gata de încărcare în notebookul `MavisCloud-Gmail`*