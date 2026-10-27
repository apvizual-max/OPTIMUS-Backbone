<#
  auto-repair-drivefs.ps1

  Cârligul de auto-repair pentru DriveFS.
  R0 dat de Popy pe 2026-10-19. Defect D2/D3/D4/D5 reparat 2026-10-19.
  Reperul de backup adaptat la oglinda Google Drive Cloud pe 2026-10-21 (Decizia 1).
  Silent failure reparat pe 2026-10-21: 104 reporniri pe o cale moarta.

  CE FACE:
    1. rezolva REPERUL VAULTULUI din sursa dinamica (shortcutul creat de DriveFS)
       si verifica daca procesul DriveFS ruleaza
    2. citeste, de fapt (ReadAllBytes), cateva fisiere santinela din vault
    3. daca citirea pica cu er specifica DriveFS, repornește DriveFS
    4. verifica dupa restart ca s-a recuperat, si scrie totul intr-un jurnal

  CE NU FACE (pe masura):
    - NU cauta si NU inventeaza cauza degradarii. Logurile DriveFS arata o
      semnatura, masurata pe 2026-10-19: 8.397 aparitii "0x91" (= 145, "The
      directory is not empty") in logurile scrise in ziua aceea. REMASURAT pe
      19->20.10: 67.874 aparitii in total. Legatura cauza->efect NU e masurata.
      Cârligul trateaza SIMPTOMUL.
    - NU se auto-amplifica: cooldown, plafon de restarturi pe ora, si
      verificare ca restartul chiar a ajutat. Daca nu ajuta, nu reincearca
      imediat.
    - NU atinge git: daca exista index.lock, un commit e in curs, si se
      sareste. Un restart in mijlocul unui commit corupte istoricul.
    - NU sterge nimic si NU scrie in vault.
    - NU poate esua lantul: orice exceptie e prinsa, exit 0 intotdeauna.

  RULARE: task programat 'PKMS-DriveFS-AutoRepair', la fiecare 5 minute.
#>
param(
  [string]$Vault = '',
  [string]$Baza  = 'C:\Users\apviz\.minimax\drivefs',
  [int]$CooldownSecunde = 600,
  [int]$MaxPeOra = 3
)
$ErrorActionPreference = 'Continue'   # NU 'Stop': cârligul nu poate arunca

# --- REPERUL VAULTULUI ---
# MASURAT 2026-10-21 22:26: calea 'G:\My Drive\GDrive-Second_Brain_PKMS' NU exista
# pe aceasta masina. 'G:\My Drive' nici nu e director (doar shortcutul
# 'G:\My Drive.lnk' -> 'E:\Google\GDrive'). Carligul o folosea ca implicit, deci
# Test-MountMort raspundea "MOUNT MORT" la FIECARE rulare, iar el reporni
# DriveFS: 104 reporniri, 410 verdicte "MOUNT MORT", 0 recuperari reale.
# Adica: un instrument de sanatate care se apara singur pe o cale pe care nu se
# afla nimic, si care reporneste exact lucrul pe care trebuia sa-l urmareasca.
#
# REPARAT (2026-10-21): reperul se rezolva din sursa dinamica (shortcutul pe
# care DriveFS il creeaza), iar o cale fara amprenta de vault (COTOR.md) e
# CONFIG, nu MOUNT MORT.
$MountRoot = ''

# Sursa dinamica a mountpoint-ului: shortcutul pe care DriveFS il creeaza la
# prima rulare. MASURAT 2026-10-21 22:5x: 'G:\My Drive.lnk' -> 'E:\Google\GDrive'.
# Daca DriveFS se remonteaza pe alt volum, shortcutul se actualizeaza singur,
# iar reperul urmeaza mountul fara sa fie editat manual.
function Get-DriveFsMountRoot {
  try {
    $sh = New-Object -ComObject WScript.Shell
    foreach ($lnk in @('G:\My Drive.lnk', (Join-Path $env:USERPROFILE 'Desktop\My Drive.lnk'))) {
      try {
        if ([System.IO.File]::Exists($lnk)) {
          $t = $sh.CreateShortcut($lnk).TargetPath
          if ($t -and [System.IO.Directory]::Exists($t)) { return $t }
        }
      } catch { }
    }
  } catch { }
  return ''
}

# Amprenta de mount DriveFS: 'desktop.ini' cu icoana GoogleDriveFS.
# MASURAT 2026-10-21: prezent DOAR la radacina mountului (E:\Google\GDrive),
# absent la E:\Google si absent in vault. Deci discriminator, nu noroc.
function Test-MountDriveFs([string]$Cale) {
  if (-not $Cale) { return $false }
  if (-not [System.IO.Directory]::Exists($Cale)) { return $false }
  $di = [System.IO.Path]::Combine($Cale, 'desktop.ini')
  try {
    if (-not [System.IO.File]::Exists($di)) { return $false }
    $txt = [System.IO.File]::ReadAllText($di)
    return ($txt -like '*GoogleDriveFS.exe*')
  } catch { return $false }
}

# Cel mai apropiat stramos al unei cai care e radacina unui mount DriveFS.
function Find-MountRootAncestor([string]$Cale) {
  $d = $Cale
  while ($d) {
    if (Test-MountDriveFs $d) { return $d }
    $parent = [System.IO.Path]::GetDirectoryName($d)
    if (-not $parent -or $parent -eq $d) { break }
    $d = $parent
  }
  return ''
}

$VaultCandidati = @()
$mnt = Get-DriveFsMountRoot
if ($mnt) { $VaultCandidati += ([System.IO.Path]::Combine($mnt, 'GDrive-Second_Brain_PKMS')) }
$VaultCandidati += 'E:\Google\GDrive\GDrive-Second_Brain_PKMS'
$VaultCandidati += 'G:\My Drive\GDrive-Second_Brain_PKMS'

if (-not $Vault) {
  foreach ($c in $VaultCandidati) {
    if ([System.IO.Directory]::Exists($c)) { $Vault = $c; break }
  }
  if (-not $Vault) { $Vault = $VaultCandidati[0] }
}

# Radacina de mount folosita la proba "mountul e viu?". Se cauta intai printre
# stramosii reperului (ca sa functioneze si cand -Vault e pasat explicit), apoi
# se cade inapoi pe sursa dinamica (shortcut).
$MountRoot = Find-MountRootAncestor $Vault
if (-not $MountRoot) { $MountRoot = (Get-DriveFsMountRoot) }

$logFile  = Join-Path $Baza 'auto-repair.log'
$stateFile = Join-Path $Baza 'state.json'
$launchBat = 'C:\Program Files\Google\Drive File Stream\launch.bat'

function Log([string]$msg) {
  # DateTime NU are metoda Format() -- are ToString(format). Cu .Format(),
  # $ts ramane $null (eroare neterminatoare, pentru ca ErrorActionPreference
  # e Continue) si jurnalul se scrie fara timp: "[] SANATOS". Masurat.
  $ts = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
  try {
    $line = "[$ts] $msg`r`n"
    [System.IO.File]::AppendAllText($logFile, $line, (New-Object System.Text.UTF8Encoding($false)))
  } catch { }
}

function Read-State {
  if (-not [System.IO.File]::Exists($stateFile)) {
    return [pscustomobject]@{ ultimaRepornire = 0; reporniriOra = @(); totalReporniri = 0; ultimaVerdict = 'necunoscut' }
  }
  try {
    $raw = [System.IO.File]::ReadAllText($stateFile)
    if ($raw.Trim() -eq '') { throw 'gol' }
    return $raw | ConvertFrom-Json
  } catch {
    Log "STATE CORUPT (refacut): $($_.Exception.Message)"
    return [pscustomobject]@{ ultimaRepornire = 0; reporniriOra = @(); totalReporniri = 0; ultimaVerdict = 'necunoscut' }
  }
}

function Save-State($s) {
  try {
    $json = $s | ConvertTo-Json -Depth 4
    [System.IO.File]::WriteAllText($stateFile, $json, (New-Object System.Text.UTF8Encoding($false)))
  } catch { Log "STATE NU S-A PUTUT SCRIE: $($_.Exception.Message)" }
}

# --- santinelele: locuri diferite din arbore, ca sa nu depindem de un punct ---
# [System.IO.Path]::Combine in loc de Join-Path: Join-Path arunca
# DriveNotFoundException daca litera unitatii nu exista (ex.: G: demontat),
# iar erorile umpleau jurnalul cu zgomot. Combine e operatie pura de sir.
$santinel = @(
  ([System.IO.Path]::Combine($Vault, 'COTOR.md')),
  ([System.IO.Path]::Combine($Vault, 'INDEX CENTRAL.md')),
  ([System.IO.Path]::Combine($Vault, '00_Inbox\00_INDEX.md')),
  ([System.IO.Path]::Combine($Vault, '02_Areas\00_INDEX.md'))
)

$procDriveFs = (@(Get-Process GoogleDriveFS -EA SilentlyContinue).Count -gt 0)

# --- mountul DriveFS e viu? ---
# Independent de reper: verificam radacina de mount (amprenta desktop.ini +
# e enumerabila). Daca mountul e viu dar reperul nu exista, atunci problema
# e CALEA, nu mountul -- si repornirea ar distruge exact ce trebuie urmarit.
function Test-MountRootViabil {
  if (-not $script:MountRoot) { return $false }
  if (-not (Test-MountDriveFs $script:MountRoot)) { return $false }
  try {
    $entries = @([System.IO.Directory]::GetFileSystemEntries($script:MountRoot))
    return ($entries.Count -gt 0)
  } catch { return $false }
}

# --- mountul e mort? ---
# D2 (defect real, masurat): santinelele LIPSA erau SALTATE (continue), deci
# $picate.Count era 0 si carligul loga SANATOS exact cand vaultul disparea.
# Discriminantul: daca procesul DriveFS nu ruleaza, mountul e mort -> lipsa
# santinelelor e un SIMPTOM, nu o lipsa de continut. Daca procesul ruleaza si
# radacina exista, iar o santinela lipseste, e vorba despre continut
# (fisier renumat) -> se raporteaza, dar NU se reporneste DriveFS (altfel
# bucla de restarturi la o redenumire).
function Test-MountMort {
  if (-not $procDriveFs) { return 'procesul DriveFS nu ruleaza' }
  if (-not [System.IO.Directory]::Exists($Vault)) {
    # Mountul e viu, dar reperul lipseste -> cale gresita, tratata de gard 0.
    if (Test-MountRootViabil) { return '' }
    return "radacina vaultului nu exista: $Vault"
  }
  return ''
}

# CONFIG, nu MOUNT MORT: calea exista, dar nu e vaultul (lipseste COTOR.md);
# sau calea lipseste, dar mountul DriveFS e demonstrat viu.
# In acest caz DriveFS e SANATOS si calea e gresita. Repornirea lui aici e
# exact lecuitura care a produs 104 de reporniri pe o cale moarta.
function Test-CaleGresita([string]$Cale) {
  if (-not $Cale) { return $false }
  if ([System.IO.Directory]::Exists($Cale)) {
    return (-not [System.IO.File]::Exists([System.IO.Path]::Combine($Cale, 'COTOR.md')))
  }
  # calea nu exista: daca mountul e viu, e cale gresita. Daca nici mountul nu
  # poate fi dovedit viu, e ambiguu -> ramane MOUNT MORT (nu pierdem capacitatea).
  return (Test-MountRootViabil)
}

function Test-Citibilitate {
  $picate  = New-Object System.Collections.Generic.List[string]
  $lipsuri = New-Object System.Collections.Generic.List[string]
  foreach ($p in $santinel) {
    if (-not [System.IO.File]::Exists($p)) { $lipsuri.Add($p); continue }
    try {
      $b = [System.IO.File]::ReadAllBytes($p)
      if ($b.Length -eq 0) { $picate.Add("$p (gol)") }
    } catch {
      $picate.Add("$p :: $($_.Exception.Message)")
    }
  }
  return [pscustomobject]@{
    picate  = $picate
    lipsuri = $lipsuri
    citite  = ($santinel.Count - $lipsuri.Count)
  }
}

try { [System.IO.Directory]::CreateDirectory($Baza) | Out-Null } catch { }

$st = Read-State

# --- gard 1: un commit e in curs? ---
$gitLock = [System.IO.Path]::Combine($Vault, '.git\index.lock')
$commitInCurs = [System.IO.File]::Exists($gitLock)

$mountMort = Test-MountMort
$r = Test-Citibilitate
$picate  = @($r.picate)
$lipsuri = @($r.lipsuri)

# --- gard 0: calea e gresita? (nu e MOUNT MORT) ---
# Un instrument de sanatate care se apara singur pe o cale pe care nu se afla
# nimic e cel mai periculos tip de instrument: distruge exact ce trebuia sa
# urmareasca. Masurat 2026-10-21: 104 reporniri, zero recuperari.
# Daca procesul DriveFS e mort, gardul 0 NU se declanseaza: atunci e nevoie
# reala de repornire, chiar daca calea configurata e gresita.
if ($procDriveFs -and (Test-CaleGresita $Vault)) {
  $st.ultimaVerdict = 'config-eroare'
  Save-State $st
  Log "CONFIG: calea '$Vault' nu e vaultul (lipseste COTOR.md sau nu exista, dar mountul DriveFS e viu). DriveFS e sanatos; calea e gresita. NU repornesc."
  exit 0
}

# D4: jurnalul spunea "4 santinele citite" chiar daca 0 erau citite.
# Acum se raporteaza numarul REAL.
$cititeReal = $r.citite

# --- verdict ---
# Cazul 1: mount mort -> santinelele lipsesc, dar cauza e montarea, nu continutul.
# Cazul 2: mount viu, santinele de citit cad -> degradare reala.
# Cazul 3: mount viu, radacina se citeste, doar o santinela lipseste -> continut
#           (fisier renumat). Se raporteaza, NU se reporneste DriveFS.
if ($picate.Count -eq 0 -and $lipsuri.Count -eq 0 -and $mountMort -eq '') {
  $st.ultimaVerdict = 'sanatos'
  Save-State $st
  Log "SANATOS: $cititeReal din $($santinel.Count) santinele citite fara eroare."
  exit 0
}

if ($picate.Count -eq 0 -and $lipsuri.Count -gt 0 -and $mountMort -eq '') {
  # mountul traieste, radacina se citeste -> lipsa e de continut, nu de montare
  $st.ultimaVerdict = 'atentie-lipsa'
  Save-State $st
  Log "ATENTIE: $cititeReal din $($santinel.Count) santinele citite; $($lipsuri.Count) lipsesc, dar mountul e viu. Nu repornesc DriveFS (probabil continut renumat). Prima lipsa: $($lipsuri[0])"
  exit 0
}

if ($mountMort -ne '') {
  Log "MOUNT MORT: $mountMort. $($lipsuri.Count) din $($santinel.Count) santinele lipsesc, $($picate.Count) nu se citesc."
} else {
  Log "PICAT: $($picate.Count) santinele nu se citesc. Prima: $($picate[0])"
}

if ($commitInCurs) {
  Log "SALTAT: exista .git\index.lock -- un commit e in curs. Nu repornesc DriveFS in mijlocul unui commit."
  $st.ultimaVerdict = 'skip-commit-in-curs'
  Save-State $st
  exit 0
}

# --- gard 2: cooldown ---
# timp epoch real. Masurat: Get-Date -UFormat %s da cu 3 ore in plus pe
# aceasta masina (UTC+3), pentru ca interpreteaza ora locala ca UTC. Diferenta
# nu conteaza la cooldown, dar epoch-ul adevarat conteaza daca se compara cu
# un jurnal scris de altceva.
$acum = [int][DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$ultima = [int]$st.ultimaRepornire
if (($acum - $ultima) -lt $CooldownSecunde) {
  Log "SALTAT: cooldown. Ultima repornire a fost cu $($acum - $ultima) secunde in urma (minim $CooldownSecunde)."
  $st.ultimaVerdict = 'skip-cooldown'
  Save-State $st
  exit 0
}

# --- gard 3: plafon pe ora ---
$ora = @($st.reporniriOra | Where-Object { ($acum - [int]$_) -lt 3600 })
if ($ora.Count -ge $MaxPeOra) {
  Log "SALTAT: plafon atins -- $($ora.Count) reporniri in ultima ora (maxim $MaxPeOra). Nu mai repornesc."
  $st.ultimaVerdict = 'skip-plafon'
  Save-State $st
  exit 0
}

# --- repornirea ---
Log "ACTION: repornesc DriveFS."
foreach ($p in @(Get-Process GoogleDriveFS -EA SilentlyContinue)) {
  try { Stop-Process -Id $p.Id -Force -EA Stop } catch { Log "  oprire proces $($p.Id): $($_.Exception.Message)" }
}
Start-Sleep -Seconds 5
if (-not [System.IO.File]::Exists($launchBat)) {
  Log "ACTION IMPOSIBIL: launch.bat nu exista la $launchBat"
  $st.ultimaVerdict = 'nu exista launch.bat'
  Save-State $st
  exit 0
}
try {
  Start-Process -FilePath $launchBat -WindowStyle Hidden
} catch {
  Log "ACTION IMPOSIBIL: nu pot porni launch.bat: $($_.Exception.Message)"
  $st.ultimaVerdict = 'pornire esuita'
  Save-State $st
  exit 0
}
Start-Sleep -Seconds 25

# --- verificare: restartul a ajutat? ---
# D3 (defect real, masurat): verificarea repeta aceeasi logica de "sare", deci
# un restart care NU a ajutat era raportat "recuperat". Acum se verifica cu
# aceeasi semantica: mount viu + toate santinelele citite.
$mountMort2 = Test-MountMort
$r2 = Test-Citibilitate
$picate2  = @($r2.picate)
$lipsuri2 = @($r2.lipsuri)

$st.totalReporniri = [int]$st.totalReporniri + 1
$st.ultimaRepornire = $acum
$st.reporniriOra = @($ora + $acum)
if ($picate2.Count -eq 0 -and $lipsuri2.Count -eq 0 -and $mountMort2 -eq '') {
  $st.ultimaVerdict = 'recuperat'
  Log "RECUPERAT: dupa repornire, toate santinelele se citesc."
} else {
  $st.ultimaVerdict = 'nerecuperat'
  $detaliu = "mount=$mountMort2, nu se citesc=$($picate2.Count), lipsesc=$($lipsuri2.Count)"
  Log "NERECUPERAT: dupa repornire, inca nu e sanatos ($detaliu)."
  if ($picate2.Count -gt 0) { Log "  prima santinela care nu se citeste: $($picate2[0])" }
  elseif ($lipsuri2.Count -gt 0) { Log "  prima santinela care lipseste: $($lipsuri2[0])" }
}
Save-State $st
exit 0
