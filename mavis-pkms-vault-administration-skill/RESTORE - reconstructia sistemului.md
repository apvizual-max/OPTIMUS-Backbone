# RESTORE — reconstruirea sistemului PKMS din repo

> Repo-ul GitHub e **save point**: nu conține conținutul vaultului, conține **programarea
> lui**. Din repo se poate reface sistemul întreg — nu se poate reface conținutul, și asta
> e corect: conținutul stă pe Drive.

**Repo:** `https://github.com/apvizual-max/pkms-vault-automation` · ramura `master`

## 0. Ce se reface și ce nu

| Se reface din repo | Nu se reface (e pe Drive) |
|---|---|
| cele 12 scripturi ale motorului | conținutul bazelor `00`–`09` |
| contractul §18 + documentația ghidului | fișierele clientului |
| `COTOR.md`, `AGENTS.md`, `MANUAL DE NAVIGARE - cotor.md` | fișierele atașate |
| **skillurile** (`_SYSTEM\Skills_MASTER_Folder\`) | arhiva `_QUARANTINE` |
| **XML-urile celor 4 taskuri** | `INDEX CENTRAL.md` — derivat, se regenerează |
| **scriptul cârligului DriveFS** (`auto-repair-drivefs.ps1`) | fișierele atașate |
| **pachetul de handoff** (`handoff-prompt.md` + `handoff-harta-implementarii.md`) | transcriptul sesiunii (30.412.803 B) — rămâne pe Drive |
| `.gitignore` cu motivele fiecărei reguli | jurnalele vii — stare, nu sistem |

## 1. Ordinea restaurării

### 1.1. Repo-ul

```powershell
git clone https://github.com/apvizual-max/pkms-vault-automation.git C:\temp\pkms-restore
```

### 1.2. Motorul — în locul lui, pe calea nouă

```powershell
$V = 'E:\Google\GDrive\GDrive-Second_Brain_PKMS'
$M = "$V\02_Areas\02-2-AI-SOT\02-2-4-AI-Kit\AI-Kit_manual"
New-Item -ItemType Directory -Path $M -Force | Out-Null
# copiază DOAR scripturile (.ps1) și cele două .txt de registru
Copy-Item 'C:\temp\pkms-restore\02_Areas\02-2-AI-SOT\02-2-4-AI-Kit\AI-Kit_manual\*' $M
```

**Verificarea encodingului e obligatorie** — altfel PowerShell 5.1 citește mojibake:

```powershell
Get-ChildItem $M -Filter *.ps1 | ForEach-Object {
  $b = [System.IO.File]::ReadAllBytes($_.FullName)
  "{0,-24} BOM={1}" -f $_.Name, (($b[0] -eq 0xEF) -and ($b[1] -eq 0xBB) -and ($b[2] -eq 0xBF))
}
```

### 1.3. Ghidul + contractul

```powershell
Copy-Item 'C:\temp\pkms-restore\02_Areas\02-2-AI-SOT\02-2-4-AI-Kit\AI-Kit_guide\*' `
          "$V\02_Areas\02-2-AI-SOT\02-2-4-AI-Kit\AI-Kit_guide" -Recurse -Force
```

### 1.4. Rădăcina

```powershell
Copy-Item 'C:\temp\pkms-restore\COTOR.md'                $V
Copy-Item 'C:\temp\pkms-restore\AGENTS.md'               $V
Copy-Item 'C:\temp\pkms-restore\MANUAL DE NAVIGARE - cotor.md' $V
Copy-Item 'C:\temp\pkms-restore\.gitignore'              $V
```

### 1.5. Skillurile — în vault **și** în sistemul central

```powershell
# în vault (sursa de adevăr)
Copy-Item 'C:\temp\pkms-restore\_SYSTEM\Skills_MASTER_Folder\*' `
          "$V\_SYSTEM\Skills_MASTER_Folder" -Recurse -Force

# în sistemul central al agentului
Copy-Item "$V\_SYSTEM\Skills_MASTER_Folder\PKMS - administrare Skill" `
          'C:\Users\apviz\.minimax\skills\pkms-vault-administration' -Recurse -Force
Copy-Item "$V\_SYSTEM\Skills_MASTER_Folder\PKMS - indexare Skill" `
          'C:\Users\apviz\.minimax\skills\pkms-vault-index' -Recurse -Force
```

### 1.6. Automatizările

**Mai întâi, lansatorul de pe `C:`** — fără el, taskurile mor la logon (vezi §5 al
skillului `PKMS - administrare`):

```powershell
$W = 'C:\Users\apviz\.minimax\pkms'
New-Item -ItemType Directory -Path $W -Force | Out-Null
Copy-Item "$M\rula-din-task.ps1" $W -Force
```

Lansatorul e și în repo (la `...\AI-Kit_manual\rula-din-task.ps1`, deschis de
`.gitignore`), deci save point-ul e complet fără el.

**Apoi scriptul cârligului DriveFS** — fără el, al patrulea task (`PKMS-DriveFS-AutoRepair`)
se înregistrează, dar moare imediat, fiindcă XML-ul pornește exact acest fișier:

```powershell
$D = 'C:\Users\apviz\.minimax\drivefs'
New-Item -ItemType Directory -Path $D -Force | Out-Null
Copy-Item "$V\_SYSTEM\Skills_MASTER_Folder\PKMS - administrare Skill\automations\auto-repair-drivefs.ps1" $D -Force
```

**De ce e în vault și nu doar pe `C:`:** măsurat 2026-10-2026 — scriptul exista doar
la `C:\Users\apviz\.minimax\drivefs\`, `git ls-files` nu returna nimic pentru
`*auto-repair*`, iar RESTORE nu conținea mențiunea `drivefs`. Așadar save point-ul
refăcea **3 din 4** automatizări. Scriptul e acum în folderul `automations\` al
skillului (deschis de `.gitignore` la nivel de fișier), deci se reface din repo.

XML-urile sunt în
`_SYSTEM\Skills_MASTER_Folder\PKMS - administrare Skill\automations\`. Se înregistrează
cu:

```powershell
foreach ($x in Get-ChildItem "$V\_SYSTEM\Skills_MASTER_Folder\PKMS - administrare Skill\automations\*.xml") {
  Register-ScheduledTask -TaskName $x.BaseName -Xml (Get-Content $x.FullName -Raw) -Force
}
```

**Atenție:** XML-ul conține calea **absolută** a lansatorului
(`C:\Users\apviz\.minimax\pkms\rula-din-task.ps1`), iar calea vaultului e **în
interiorul lansatorului**, nu în XML. Dacă vaultul s-a mutat, se schimbă `$Vault` din
`rula-din-task.ps1`, nu XML-ul. Asta e exact cauza rămasă la 19.10.2026: taskurile
arătau spre `02_Areas\02_2-AI-SOT\AI-Kit\AI-Kit_manual`, cale care nu mai exista după
mutarea pe Drive — și au murit cu `ERROR_DIRECTORY` (2147942667).

**Verificare după înregistrare:**

```powershell
Get-ScheduledTask -TaskName 'PKMS-*' | ForEach-Object {
  $i = Get-ScheduledTaskInfo -TaskName $_.TaskName
  "{0,-24} result={1} next={2}" -f $_.TaskName, $i.LastTaskResult, $i.NextRunTime
}
```

### 1.7. Indexurile — se regenerează, nu se restaurează

`INDEX CENTRAL.md` și cei ~2.516 `00_INDEX.md` sunt **derivate**. Nu se restaurează din
repo — se reconstruiesc din conținut:

```powershell
& "$M\build-index.ps1" -Quiet     # regenerează toate indexurile + INDEX CENTRAL.md
& "$M\align-index.ps1" -CeVad     # verdict: trebuie 0 NEALINIAT
```

**Testul că reconstrucția e completă:** dacă `INDEX CENTRAL.md` regenereat are aceleași
cifre ca cel raportat înainte de incident, sistemul e reconstituit. Dacă diferă, motivul
e în conținut, nu în programare.

### 1.8. Pachetul de handoff — portul de intrare

```powershell
$HD = "$V\02_Areas\02-2-AI-SOT\02-2-4-AI-Kit\HANDOFF-2026-10-19"
New-Item -ItemType Directory -Path $HD -Force | Out-Null
Copy-Item 'C:\temp\pkms-restore\02_Areas\02-2-AI-SOT\02-2-4-AI-Kit\HANDOFF-2026-10-19\*.md' $HD
```

`handoff-prompt.md` e promptul de inițiere al sesiunii noi; `handoff-harta-implementarii.md`
e harta construcției sistemului, §1–§14. **Transcriptul (`transcript-complet.json`,
30.412.803 B) NU e în repo** — rămâne pe Drive, fiindcă e dovada unei sesiuni, nu
programarea sistemului.

## 2. Ce NU se face la restaurare

- **Nu se șterge nimic** din backup sau din `_QUARANTINE`.
- **Nu se rescrie istoricul git** — se continuă.
- **Nu se aplică fișiere din repo peste un vault care deja funcționează** fără motiv:
  restore-ul e pentru cazul în care motorul e pierdut, nu pentru a înlocui conținut.
- **Nu se rulează `git clean -fdx` / `git reset --hard`** în vault — `.git` e în
  interiorul vaultului, iar conținutul nu e versionat.

## 3. Test de acceptanță

După restaurare, sistemul e reconstituit **dacă și numai dacă**:

```powershell
& "$M\lint.ps1"                  # 0 erori
& "$M\align-index.ps1" -CeVad    # 0 NEALINIAT
& "$M\health-check.ps1"          # stabilitate: diferenta 0
Get-ScheduledTask -TaskName 'PKMS-*' | ForEach-Object {
  $i = Get-ScheduledTaskInfo -TaskName $_.TaskName
  "{0,-24} result={1}" -f $_.TaskName, $i.LastTaskResult   # toate 0
}
git -C $V status --porcelain     # gol
```

Toate cele cinci trebuie verzi. Unul roșu înseamnă că restaurarea nu s-a terminat.
