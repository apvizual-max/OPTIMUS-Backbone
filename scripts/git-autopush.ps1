<#
    git-autopush.ps1 - singurul drum prin care iese codul spre GitHub.

    ORDINEA, care nu se schimba:
        1. masoara   - HEAD local, server prin git ls-remote, comituri neimpinse
        2. decide    - sub prag? NU se atinge nimic. peste prag? cere acord
        3. push      - git push PUR. Fara LiveReview. Fara review. Fara poarta.
        4. verifica  - git ls-remote; SHA server == SHA HEAD
        5. review    - LiveReview, DOAR DUPA ce push-ul e confirmat pe GitHub

    LiveReview nu apare inainte de push, niciodata. Ce a ajuns pe GitHub se
    review-eaza acolo; ce sta local nu e treaba lui.

    DOUA CAI, cum a cerut Popy:
        calea 1  - push, apoi review cu LiveReview
        calea 2  - push FARA review (rate limit atins, cont epuizat, LRC cazut)
    In ambele cazuri push-ul se face SI se verifica. Calea 2 nu e degradare:
    e calea de rezerva prevazuta. Un review lipsa nu e o eroare si nu apare
    niciodata in panoul lui Popy ca un push esuat.

    COMMIT: nu se atinge. Scriptul nu comita, nu stash-eaza, nu face branch.

    ASCII numai, intentionat: PowerShell 5.1 citeste .ps1 fara BOM ca ANSI si
    parserul moare pe primul semn ne-ASCII.

    Exit: 0 = pushat si verificat / nimic de urcat
          1 = push NU a ajuns, sau serverul nu corespunde
          2 = mediu invalid (nu e repo, nu exista remote)
          3 = sub prag - nu s-a atins nimic
#>

[CmdletBinding()]
param(
    [string] $Remote   = 'origin',
    [string] $Branch   = 'main',
    [int]    $Prag     = 25,
    [int]    $ReviewTimeoutSec = 120,
    [switch] $Acord,
    [switch] $FaraReview,
    [switch] $DryRun
)

$ErrorActionPreference = 'Stop'
$LRC = 'C:\Users\apviz\AppData\Local\Programs\lrc\lrc.exe'

function Say($m) { Write-Host $m }
function Line($m = '') { Write-Host $m }

# git scrie PROGRESSUL pe stderr chiar cand reuseste. Cu
# ErrorActionPreference='Stop' asta devine eroare terminala si omoara scriptul.
# Masurat 2026-10-11: push reusit, ls-remote a confirmat SHA-ul, scriptul a
# iesit totusi cu 1 si NU a verificat nimic.
#
# ATENTIE la 2>&1: un obiect ErrorRecord ajunge in iesire, NU un sir. Un
# $_.Trim() pe ErrorRecord arunca MethodNotFoundException - si pentru ca
# ErrorActionPreference e repus pe 'Stop', asta e TERMINANT: scriptul moare in
# loc sa raporteze. Masurat 2026-10-11 cu `git push --dry-run`.
function Invoke-Git {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$GitArgs)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $o = & git @GitArgs 2>&1
        $c = $LASTEXITCODE
    } finally { $ErrorActionPreference = $prev }
    # normalizare explicita: orice element devine SIR, inclusiv ErrorRecord
    $s = @()
    foreach ($x in @($o)) { $s += [string]$x }
    return [pscustomobject]@{ Out = $s; Code = $c }
}

# ls-remote intoarce "<sha>\t<refs/heads/main>". Daca git a scris ceva pe
# stderr inainte, primul element NU e linia de hash - si un CompareString
# degeaba ar da "PUSH NU A AJUNS" la un push reusit. Deci se cauta EXACT
# forma unui SHA, nu "primul element".
function Get-LsRemoteSha {
    param([string[]]$Lines)
    foreach ($l in $Lines) {
        $t = ([string]$l).Trim()
        if ($t -match '^([0-9a-f]{40})\s') { return $Matches[1] }
    }
    return $null
}

function Get-DirtyCount {
    param($Lines)
    $n = 0
    foreach ($x in @($Lines)) {
        $t = ([string]$x).Trim()
        if ($t) { $n++ }
    }
    return $n
}

# --- 1. masurare ------------------------------------------------------------
$top = (Invoke-Git rev-parse --show-toplevel).Out | Select-Object -First 1
if (-not $top) { Say 'EROARE: nu e repo git.'; exit 2 }
Set-Location $top

$branchReal = (Invoke-Git rev-parse --abbrev-ref HEAD).Out | Select-Object -First 1
$localSha  = (Invoke-Git rev-parse HEAD).Out | Select-Object -First 1
if (-not $localSha) { Say 'EROARE: HEAD ilizibil.'; exit 2 }

$srvSha  = Get-LsRemoteSha (Invoke-Git ls-remote $Remote $Branch).Out
if (-not $srvSha) { Say ("EROARE: ramura '$Branch' nu exista pe '$Remote'."); exit 2 }

$neimpinse = 0
$c = (Invoke-Git rev-list --count "$Remote/$Branch..HEAD").Out | Where-Object { $_ -match '^\d+$' } | Select-Object -First 1
if ($c) { $neimpinse = [int]$c }
$dirty = Get-DirtyCount (Invoke-Git status --porcelain).Out

Line '================================================================'
Line '  PUSH - masurare'
Line '================================================================'
Say ("  ramura   : " + $branchReal + $(if ($branchReal -ne $Branch) { "  (ATENTIE: nu e '$Branch')" } else { '' }))
Say ("  local    : " + $localSha.Substring(0,7))
Say ("  server   : " + $srvSha.Substring(0,7))
Say ("  neimpinse: " + $neimpinse)
Say ("  necomitat: " + $dirty)
Say ("  prag     : " + $Prag)
Line

if ($neimpinse -eq 0 -and $dirty -eq 0) {
    Say 'Nimic de urcat. Serverul e la HEAD, arbore curat.'
    exit 0
}

if ($neimpinse -eq 0) {
    Say ("ATENTIE: " + $dirty + " fisier(e) necomitat(e), dar nimic de impins.")
    Say 'Comit mai intai, apoi reia.'
    exit 0
}

# DRY-RUN INAINTE DE POARTA. Masuratoarea nu impinge nimic, deci nu are ce
# cere acord. Masurat 2026-10-11: -DryRun era DUPA poarta de acord si iesea
# cu 3, adica singurul mod de a masura fara sa impinga nu mai functiona -
# iar singurul mod de a verifica daca se poate impinge era chiar masurarea.
if ($DryRun) {
    Say 'DRY-RUN: masurat, nimic impins.'
    Line
    Line '  comiturile care ar urca:'
    (Invoke-Git log --oneline "$Remote/$Branch..HEAD").Out | ForEach-Object { Say ("    " + [string]$_) }
    exit 0
}

# ACORDUL: pragul spune CAND se poate, -Acord spune CA ISE IMPINGE.
# Fara -Acord nu se impinge NIMICATI - nici sub prag, nici peste prag.
# Asa cerinta 3 devine impusa de masina, nu doar o propozitie: un agent care
# uita acordul primeste exit 3, nu un push facut in plus pe main.
# Masurat 2026-10-11 de verificator: peste prag, scriptul impingea necondi-
# cionat, iar acordul ramanea doar o regula scrisa.
if (-not $Acord) {
    Line '----------------------------------------------------------------'
    Say ("COMITURI NEIMPINSE: " + $neimpinse + " / prag " + $Prag)
    Line '----------------------------------------------------------------'
    (Invoke-Git log --oneline "$Remote/$Branch..HEAD").Out | ForEach-Object { Say ("  " + [string]$_) }
    Line '----------------------------------------------------------------'
    if ($neimpinse -lt $Prag) {
        Say ("Sub prag (" + $neimpinse + "/" + $Prag + "). Se aduna.")
    } else {
        Say ("Prag atins (" + $neimpinse + "/" + $Prag + "). Se poate face push.")
    }
    Say 'NU se impinge fara acordul lui Popy.'
    Say 'Cum el spune "faci push", ruleaza din nou cu -Acord.'
    exit 3
}

# --- 2. PRAG ATINS: push, cu acord ------------------------------------------
Line '================================================================'
Line '  PUSH - incepere'
Line '================================================================'
Say '  push pur. Fara LiveReview inainte de push. Fara poarta.'
$r = Invoke-Git push $Remote "HEAD:refs/heads/$Branch"
Say ("  push exit: " + $r.Code)
Line

# --- 3. VERIFICARE (adevarul e aici, nu in codul de iesire) -----------------
$afterSha = Get-LsRemoteSha (Invoke-Git ls-remote $Remote $Branch).Out

if (-not $afterSha -or $afterSha -ne $localSha) {
    Line '================================================================'
    Line '  PUSH - NU A AJUNS'
    Line '================================================================'
    Say ("  server: " + $(if ($afterSha) { $afterSha.Substring(0,7) } else { 'nu raspunde' }))
    Say ("  local : " + $localSha.Substring(0,7))
    Say 'Pushul nu a ajuns. Nu raporta succes.'
    exit 1
}

Say ("  PUSH CONFIRMAT PE SERVER: " + $afterSha.Substring(0,7))
Say ("  comituri urcate: " + $neimpinse)
Line

# --- 4. LIVE REVIEW, DOAR ACUM, PE CE E PE GITHUB ---------------------------
# Ruleaza pe ce tocmai a ajuns. Nu poate bloca push-ul: push-ul deja s-a facut
# si a fost verificat. Rolul lui e sa raporteze, nu sa opreasca ceva.
$reviewState = 'neprocerat'
$reviewNote  = ''

if ($FaraReview) {
    $reviewState = 'calea 2'
    $reviewNote  = '-FaraReview: push fara LiveReview, intentionat'
} elseif (-not (Test-Path $LRC)) {
    $reviewState = 'neprocerat'
    $reviewNote  = 'lrc.exe nu e pe loc; pushul e deja confirmat'
} else {
    Say '  review LiveReview pe ce tocmai a ajuns pe GitHub...'
    $log = Join-Path $env:TEMP ("lrc-post-" + [guid]::NewGuid().ToString('N') + '.log')
    # Start-Process POATE arunca (executable corupt sau strain). Cu
    # ErrorActionPreference='Stop' ar fi TERMINANT si scriptul ar iesi cu
    # cod nenul DUPA un push deja reusit si verificat - adica un push bun
    # raportat ca esuat. Masurat 2026-10-11 de verificator.
    # Aici push-ul e deja GATA. Review-ul doar raporteaza, deci orice
    # abatere merge in calea 2, fara sa atingem rezultatul push-ului.
    try {
        $p = Start-Process -FilePath $LRC -PassThru -NoNewWindow `
             -RedirectStandardOutput $log -RedirectStandardError "$log.err" `
             -ArgumentList @('review','--range',"$Remote/$Branch..$localSha",'--no-serve','--output','json')
    } catch {
        $p = $null
        $reviewState = 'limita'
        $reviewNote  = "lrc nu a pornit ($($_.Exception.GetType().Name)); pushul e deja gata"
    }
    # $p e null doar daca Start-Process a aruncat: atunci reviewState e deja
    # 'limita' de mai sus, se ramane pe calea 2 si nu se porneste nimic.
    # (Inainte era `if ($p -eq $null) { } else {` - ramanea o acolada deschisa
    # fara pereche si scriptul NU se mai parsa. Masurat 2026-10-11.)
    if ($p -ne $null) {
    $gata = $p.WaitForExit($ReviewTimeoutSec * 1000)
    if (-not $gata) {
        try { $p.Kill() } catch { }
        $reviewState = 'timeout'
        $reviewNote  = "nu a raspuns in ${ReviewTimeoutSec}s"
    } else {
        $p.WaitForExit()
        $code = $p.ExitCode
        $out  = ''
        if (Test-Path $log) { $out = [System.IO.File]::ReadAllText($log) }
        $rid = ''
        if ($out -match 'Review submitted, ID:\s*(\d+)') { $rid = $Matches[1] }
        if ($code -eq 0) {
            $reviewState = 'trimis'
            $reviewNote  = $(if ($rid) { "review #$rid" } else { 'ok' })
        } else {
            $why = ''
            foreach ($pat in @('rate.?limit','too many requests','quota','429','plan')) {
                if ($out -match $pat) { $why = 'limita cont / rate limit'; break }
            }
            if (-not $why) { $why = "lrc a raspuns negativ (exit $code)" }
            $reviewState = 'limita'
            $reviewNote  = "$why - calea 2, pushul oricum e gata"
        }
    }
    foreach ($f in @($log, "$log.err")) { if (Test-Path $f) { Remove-Item $f -Force -ErrorAction SilentlyContinue } }
}
}   # inchide: if ($p -ne $null)  |  inchide: else-ul ramurii de review
    # MASURAT 2026-10-11: aceasta a doua acolada LIPSEA. Scriptul nu se parsa
    # deloc, deci nu rula nici masuratoarea - si un script care nu ruleaza nu
    # poate fi "functionand". Lipsa era sub linia de un comentariu despre
    # aceeasi problema, ceea ce o facea usor de ratacit la citit.
Say ("  review: $reviewState - " + $reviewNote)
Line

Line '================================================================'
Line '  PUSH - REZULTAT'
Line '================================================================'
Say ("  server = " + $afterSha.Substring(0,7) + " = HEAD local")
Say ("  " + $neimpinse + " comituri au ajuns pe GitHub")
if ($dirty -gt 0) { Say ("  ATENTIE: " + $dirty + " fisiere inca necomitate") }
exit 0