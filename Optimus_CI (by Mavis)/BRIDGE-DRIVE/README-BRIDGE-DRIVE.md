# BRIDGE-DRIVE — puntea primară Local ↔ Cloud

> **Asta e canalul principal.** Nu repo-ul GitHub — acela e canalul secundar,
> de rezervă.
>
> Folderul acesta trăiește în mirrorul Google Drive
> (`E:\Google\GDrive\...`), pe discul lui Popy. Google Drive for Desktop
> îl sincronizează, iar instanța Cloud — care are acces la Google Drive —
> vede **exact aceiași octeți**. Fără server, fără webhook, fără API în
> cale.

---

## 1. Ce e măsurat, nu ce se presupune

| Ce | Valoare măsurată (2026-10-27) | Cum |
|---|---|---|
| Folderul proiectului în Drive | **cloud_id `1V87h9Pbw52chSVNkxQ_NNuMh-CLfZeuI`** | `drivefs_probe.py --title` |
| Calea lui în Drive | `My Drive > GDrive-Second_Brain_PKMS > 02_Areas > 02-2-AI-SOT > CASA > OPTIMUS - Prime > Optimus_CI (by Mavis)` | lanțul de părinți din `stable_parents` |
| Rădăcina mirrorului | `Google\GDrive` → `E:\Google\GDrive`, `root_id=23`, `sync_type=MIRROR` | `drive_fs.txt`, `ReceiveMirrorRoots` |
| Starea rădăcinii | **connected = true** | același log, ultimul dump de startup |
| Lag de propagare | **≈ 80 min** (scris local 22:11 → în Drive 23:31) | `modified` din indice vs mtime local |
| Coadă de operațiuni | `PENDING_OPERATIONS=0` | `operations` din baza DriveFS |

**Concluzia:** puntea e reală — folderul e un folder Drive, nu niște octeți
locali. **Dar nu e instantă.** Deci cerințele care cer răspuns în minute nu
trimit pe canalul Drive; alea trimit pe canalul GitHub.

---

## 2. Cele patru canale

```
BRIDGE-DRIVE/
├── README-BRIDGE-DRIVE.md      ← acest fișier: protocolul
├── TASKURI-PENTRU-CLOUD.md     ← Local → Cloud, STRUCTURAT. Scris de Local.
├── INTENTII.md                 ← Popy → Cloud, LIBER. Scris de Popy.
├── INTRARI-CLOUD/              ← Cloud → Local. Un fișier nou per răspuns.
└── ISTORIC/                    ← taskuri consumate: se MUTĂ, nu se șterg.
```

Canalul secundar, pe GitHub: `QUEUE/TASKS-FOR-CLOUD.md` — **același task,
același `TASK_ID`**, scris simultan. Deci Cloud-ul are două căi în, și
vede care e activă.

---

## 3. Cine scrie ce

| Canal | Scrie | Citește | Regula |
|---|---|---|---|
| `TASKURI-PENTRU-CLOUD.md` | Local | Cloud | secțiuni noi, în jos; **niciodată** suprascriere |
| `INTENTII.md` | Popy | Cloud | text liber, fără format impus |
| `INTRARI-CLOUD/` | Cloud | Local | `RASPUNS-MAVIS-CLOUD-<data>-<ora>.md` |
| `ISTORIC/` | Local | — | task consumat, **mutat** |

**Cine arhivează — rezolvat pe fapte (2026-10-27).** Protocolul spunea în două
locuri diferite: antetul acestui folder și antetul lui
`TASKURI-PENTRU-CLOUD.md` spuneau „Cloud-ul mută secțiunea consumată", iar
tabelul de mai sus spunea „Local". Cloud-ul a citit antetul, a răspuns corect
și a scris în raport: *„Nu am mutat nimic în ISTORIC/ — mutarea e sarcina
mea"* (Local). **Regula, care acum e într-un singur loc:** Cloud-ul **marchează**
ce a consumat; Local **mută** secțiunea în `ISTORIC/`, cu conținutul păstrat
integral. Ticheta rămâne activă în coada secundară până când Cloud-ul o trece
în `QUEUE/DONE/` — pentru că poarta cere ca fiecare `TASK_ID` din coadă să
apară și în canalul primar, iar amputarea lui ar stinge poarta.

**De ce nu se scoate secțiunea din canalul primar:** invariantul de paritate
(`scripts/queue-contract-check.ps1`, proba „același TASK_ID în ambele canale")
cer ca fiecare tichetă din coadă să fie prezentă și în
`TASKURI-PENTRU-CLOUD.md`. Deci arhivarea înseamnă **arhivă + marcaj**, nu
amputare.

**Convenția de denumire a instanțelor** rămâne cea din
`docs/PROTOCOL-DENUMIRE-LOCAL-CLOUD.md`: `MAVIS-LOCAL-*` / `MAVIS-CLOUD-*`.
Un document fără prefix nu aparține nimănui — și e o lipsă de prefix.

---

## 4. Cele patru interdicții

1. **Nu suprascrii** un fișier al celeilalte instanțe. **Niciodată.** Nici
   pentru o corectură de un cuvânt.
2. **Corecția se face printr-un fișier nou**, care îl citește pe celălalt.
3. **Nu redenumești** fișierele celeilalte instanțe.
4. **Nu ștergi nimic din `BRIDGE-DRIVE/`.** Mutarea în `ISTORIC/` e
   suficientă.

---

## 5. Cum se publică — și cum se măsoară

```powershell
# publică un task (scrie pe ambele canale, apoi măsoară)
powershell -NoProfile -File scripts\mavis-drive-bridge.ps1 `
  -Publish -Title "ce cer" -Body "detalii"

# starea punții: transport, lag, canal activ
powershell -NoProfile -File scripts\mavis-drive-bridge.ps1 -Status

# poarta
powershell -NoProfile -File scripts\mavis-drive-bridge-selfcheck.ps1
```

**„Publicat” înseamnă măsurat.** Scriptul nu declară nimic pe baza scrierii:
verifică în indicele Drive și raportează `SYNCED`, `PENDING`,
`NOT_UPLOADED` sau `UNVERIFIED`. Un `UNVERIFIED` **nu** e un succes.

---

## 6. Când transportul cade

`TRANSPORT=DOWN` înseamnă că rădăcina mirrorului e deconectată în DriveFS.
Atunci:

- canalul activ devine **GITHUB** (`QUEUE/TASKS-FOR-CLOUD.md`);
- puntea GitHub cere R0 la push — deci și canalul de rezervă are o poartă;
- **nimic nu se pierde**: taskul e scris în ambele locuri, cu același id.

O punte cu o singură gură nu e o punte. De aceea canalul secundar e scris
**la publicare**, nu doar când primul cade.

---

## 7. Ce NU e aici

- **Nu e CD.** Platforma Jules, Live Review, triajul PR-urilor — sunt în
  folderul CD, cu sesiunea lor. `docs/ARHITECTURA-CI-CD.md`.
- **Nu e conținut de business.** CV-uri, clienți, prețuri — nu intră aici.
- **Nu e vault.** Vaultul e în PKMS, la nivel superior.

---

*Măsurat 2026-10-27 · Mavis Local · protocol aditiv · nu rescrie, completează*
