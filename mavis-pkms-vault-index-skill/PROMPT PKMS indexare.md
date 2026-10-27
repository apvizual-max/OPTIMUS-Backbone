# PROMPT — indexarea și alinierea vaultului PKMS

> Pentru o sesiune nouă, sau pentru un operator care preia rearanjarea fără memorie.

---

## Prompt: aliniere sigură (operația de zi cu zi)

```
Vaultul meu PKMS e pe E:\Google\GDrive\GDrive-Second_Brain_PKMS.
Indexatorul e la:
02_Areas\02-2-AI-SOT\02-2-4-AI-Kit\AI-Kit_manual\align-index.ps1

Vreau sa realiniez un subarbore, fara sa ating restul vaultului.

1. Citește întâi _SYSTEM\Skills_MASTER_Folder\PKMS - indexare Skill\SKILL.md
   (contractul de navigare, cele cinci stări, regula «jurnalele vii nu sunt conținut»).
2. Rularea de diagnostic, ÎNTOTDEAUNA înainte de orice scriere:
     $M = "E:\Google\GDrive\GDrive-Second_Brain_PKMS\02_Areas\02-2-AI-SOT\02-2-4-AI-Kit\AI-Kit_manual"
     $env:PKMS_VAULT = "E:\Google\GDrive\GDrive-Second_Brain_PKMS"
     $env:PKMS_BACKUP = "H:\CLAUDE_Archive"
     & "$M\align-index.ps1" -CeVad
   Citește ultima linie: «rezumat: ... · N NEALINIAT · ...».
3. Scrierea, DOAR pe subarborele vizat:
     & "$M\align-index.ps1" -DoarCargol '<calea-relative>'
   -DoarCargol rescrie DOAR blocurile derivate. Rândul «**De ce e aici:**» rămâne.
4. Verificare:
     & "$M\align-index.ps1" -CeVad     → trebuie 0 NEALINIAT pe subarbore

Dacă NEALINIAT persistă după aliniere, NU re-rula. Verifică ipoteza
«măsurătoare instabilă»: e vreun fișier în folder care CREȘTE în timp ce
măsoară? Un jurnal viu în cifre face bucla să nu se oprească. Lista centrală
e în paths.ps1 → Test-PkmsLiveLog; nu adăuga fișiere cu excepție unul câte unul.
```

## Prompt: regenerare completă (când cifrele se schimbă)

```
Cifrele vaultului s-au schimbat (am rearanjat / am adăugat conținut).
Trebuie regenerat stratul de indexuri, nu editat.

1.   & "$M\build-index.ps1" -Quiet
     Timp: ~5-6 minute pe DriveFS. NU poate fi scoped — rescrie tot arborele.
     NU rula în paralel cu altă rulare de indexare: există mutex, dar
     suprapunerea strică un fișier la mijloc.
2.   & "$M\align-index.ps1" -CeVad      → 0 NEALINIAT
3.   & "$M\lint.ps1"                   → 0 erori
4.   & "$M\health-check.ps1"           → stabilitate: diferenta 0

Apoi, manual, două lucruri pe care generatorul NU le atinge:
  - COTOR.md: cifrele vii (tabelele de baze, rafturi, mașină, indexuri)
  - rândul «**De ce e aici:**» din indexurile nou apărute

Dacă build-index produce un diff mare (sute de indexuri), înseamnă că cele
două generatoare nu se recunosc. STOP. Nu împinge. Verifică octet cu octet
un index, și revino pe git (indexurile sunt urmărite de git).
```

## Prompt: diagnostic de nealiniere

```
Censusul raportează NEALINIAT. Vreau cauza, nu un „reparat”.

1.   & "$M\align-index.ps1" -CeVad     → verdict + cifre
2.   & "$M\health-check.ps1"           → cifrele vii, ca să compari

3. Pentru UN folder raportat NEALINIAT, compară fișier cu fișier:
     - câte fișiere sunt REAL pe disc
     - câte spune indexul
     - care e fișierul care nu se potrivește (dimensiune, extensie)
   Numele se citesc DE PE DISC, nu din memorie — un typo al meu a produs
   odată un „ștergere” care nu existase.

4. Verifică dacă în folder există un fișier care crește în timp ce măsoară
   (jurnal viu). Dacă da: cauza e în paths.ps1 → Test-PkmsLiveLog, nu în index.

5. Raportează cauza cu cifre, înainte să schimbi ceva.
```

## Prompt: ce NU se face

```
Reține, pentru tot restul sesiunii:
- NIMIC NU SE ȘTERGE. Nici din vault, nici din backup.
- NU MUTI NIMIC fără R0-ul meu. Mutarea se propune, se așteaptă, se execută.
- INDEX CENTRAL.md e DERIVAT. Nu se patch-ează — se regenerează.
  Un „declarativ” editat manual e rescris la următoarea rulare a generatorului.
- Scripturile .ps1 au BOM UTF-8 obligatoriu; documentele .md au UTF-8 fără BOM, LF.
  Nu folosi Set-Content -Encoding UTF8 pe .ps1.
- Backup înainte de fiecare scriere: D:\PKMS-tooling\handoff\backup\<data>\.
- Commitul git e automat și nu cere R0. Push-ul cere acordul meu.
- Cifrele se măsoară în sesiunea curentă. Altfel: NOT_MEASURED.
```
