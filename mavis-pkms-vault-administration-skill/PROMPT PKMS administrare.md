# PROMPT — inițierea unei sesiuni noi pe vaultul PKMS

> Copiază blocul de mai jos într-o sesiune nouă, cu proiectul setat pe
> `E:\Google\GDrive\GDrive-Second_Brain_PKMS`. E scris ca să funcționeze **fără memorie
> despre conversația anterioară**.

---

## Prompt de inițiere

```
Lucrez pe vaultul meu personal de knowledge management, pe Google Drive:
E:\Google\GDrive\GDrive-Second_Brain_PKMS

Sistemul e administrat de un motor de scripturi PowerShell, aflat la:
02_Areas\02-2-AI-SOT\02-2-4-AI-Kit\AI-Kit_manual\
și documentat în:
02_Areas\02-2-AI-SOT\02-2-4-AI-Kit\AI-Kit_guide\

Înainte să atingi orice, citește, în această ordine:

1. COTOR.md                          (rădăcină) — contractul sistemului
2. AGENTS.md                         (rădăcină) — rampa de intrare
3. MANUAL DE NAVIGARE - cotor.md     (rădăcină) — cum se citește arborele
4. _SYSTEM\Skills_MASTER_Folder\PKMS - administrare Skill\SKILL.md
5. _SYSTEM\Skills_MASTER_Folder\PKMS - indexare Skill\SKILL.md
6. 02_Areas\02-2-AI-SOT\02-2-4-AI-Kit\AI-Kit_guide\SPECIFICATII - contractul vaultului.md

Regulile care nu se negociază:

- NIMIC NU SE ȘTERGE. Ștergerea e interzisă; mutarea în _QUARANTINE se face doar cu R0
  explicit al meu și cu MOTIV.txt lângă ea.
- NU MUTI NIMIC fără R0-ul meu. Propune, măsoară, raportează — apoi așteaptă.
- Arhiva H:\CLAUDE_Archive se CITEȘTE, nu se atinge.
- Înainte de fiecare scriere: backup sub D:\PKMS-tooling\handoff\backup\<data>\.
- Măsoară înainte să vorbești. Cifra care n-a fost măsurată în sesiunea curentă e
  NOT_MEASURED.
- Scripturile .ps1 au BOM UTF-8 obligatoriu; documentele .md au UTF-8 fără BOM, LF.
  Nu folosi Set-Content -Encoding UTF8 pe .ps1.
- Commitul git e automat și nu cere R0. Push-ul cere acordul meu.

Primele două porți de verificare (rulează-le și raportează exit code-ul):
  $M = "E:\Google\GDrive\GDrive-Second_Brain_PKMS\02_Areas\02-2-AI-SOT\02-2-4-AI-Kit\AI-Kit_manual"
  $env:PKMS_VAULT = "E:\Google\GDrive\GDrive-Second_Brain_PKMS"
  $env:PKMS_BACKUP = "H:\CLAUDE_Archive"
  & "$M\lint.ps1"                  # aștept: 0 erori
  & "$M\align-index.ps1" -CeVad    # aștept: 0 NEALINIAT

Apoi spune-mi, pe scurt: ce ai citit, ce e starea sistemului, și ce vrei să atacăm.
Nu modifica nimic până nu îmi spui ce ai de gândit.
```

---

## Prompt de administrare (când vaultul crește)

```
Vaultul a crescut și trebuie rearanjat. Procedura, în ordine, e în
_SYSTEM\Skills_MASTER_Folder\PKMS - administrare Skill\SKILL.md §6.

Reține: codul e poziția, nu eticheta; numerotarea se oprește la al treilea nivel;
rădăcinile cu _ nu primesc cod.

Ordinea obligatorie:
  1. health-check.ps1  → cifrele vii, înainte de orice schimbare
  2. decide schema, nu etichetele
  3. mută și renumeră
  4. align-index.ps1 -DoarCargol '<subarbore>'   ← doar blocurile derivate
  5. build-index.ps1                              ← regenerează INDEX CENTRAL.md
  6. align-index.ps1 -CeVad                       ← trebuie: 0 NEALINIAT
  7. actualizează COTOR.md cu cifrele NOI
  8. lint.ps1 + health-check.ps1                  ← porțile
  9. commit + push

Nu inventa cifre. Nu muta nimic fără R0-ul meu. Nu șterge nimic.
```

## Prompt de diagnostic (când ceva e nealiniat)

```
Censusul a raportat NEALINIAT. Nu repara încă.

Rulează:
  align-index.ps1 -CeVad        → verdictul complet, cu cifrele
  health-check.ps1              → cifrele vii

Apoi verifică ipoteza „măsurătoare instabilă": există în folderul respectiv un
fișier care CREȘTE în timp ce măsoară (un jurnal viu)? Compară numărul de fișiere
din index cu numărul real de pe disc, fișier cu fișier.

Dacă e o buclă de măsurătoare: cauza e în paths.ps1 → Test-PkmsLiveLog, nu în
index. Nu adăuga fișiere la excludere unul câte unul — lista e centralizată acolo
și se aplică identic în build-index, align-index și verifica-schema.

Raportează cauza, cu măsurătoare, înainte să schimbi ceva.
```
