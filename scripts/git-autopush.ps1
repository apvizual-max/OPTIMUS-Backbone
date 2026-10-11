<#
    git-autopush.ps1 - fluxul de PUSH al lui Popy.

    LRC (LiveReview) ruleaza la PUSH pe GitHub, NICIODATA la comit.
    Comiturile sunt libere si autonome; poarta nu are ce le opreasca.

    Ordinea e fixa:
      1. masoara   - HEAD local, adevarul de pe server, cate comituri urca
      2. review    - LRC pe RANGE-ul care urca, cu timeout, fara blocare
      3. push      - oricum, chiar daca review-ul a picat sau a dat rate limit
      4. verifica  - git ls-remote; SHA-ul serverului trebuie sa fie HEAD-ul

    RATE LIMIT NU BLOCHEAZA PUSH-UL. Daca lrc picat, se raporteaza si se
    impinge oricum. Un review lipsa e informatie, nu o oprire.

    NU face: commit, stash, reset, checkout, force. Nu atinge interfata.

    ASCII only, intentionat: PowerShell 5.1 citeste .ps1 ca ANSI daca nu are
    BOM, iar orice semn ne-ASCII (ex. linie lunga, diacritice) rupe parserul.

    Exit:  0 = pushat si verificat pe server
           1 = push esuat SAU serverul nu corespunde
           2 = nu exista remote / git lipsa / repo invalid
#>

[CmdletBinding()]
param(
    [string]   $Remote = 'origin',
    [string]   $Branch = 'main',
    [int]      $ReviewTimeoutSec = 90,
    [switch]   $SkipReview,
    [switch]   $DryRun
)

$ErrorActionPreference = 'Stop'
$LRC = 'C:\Users\apviz\AppData\Local\Programs\lrc\lrc.exe'

function Say($msg) { Write-Host $msg }
function Line($msg = '') { Write-Host $msg }

# git scrie PROGRESUL pe stderr chiar cand reuseste. Cu
# ErrorActionPreference='Stop' shell-ul arunca o eroare rosie si ar opri
# scriptul chiar cand push-ul a mers. Masurat pe 2026-10-11: push reusit,
# scriptul a murit inainte de verificare. De aici functia de mai jos.
function Invoke-Git {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $out = & git @Args 2>&1
        $code = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $prev
    }
    return [pscustomobject]@{ Out = $out; Code = $code }
}

# --- 0. masurare baza ------------------------------------------------------
$top = (Invoke-Git rev-parse --show-toplevel).Out
if (-not $top) { Say 'EROARE: nu e repo git.'; exit 2 }
$top = ($top | Select-Object -First 1)
Set-Location $top

$localSha = ((Invoke-Git rev-parse HEAD).Out | Select-Object -First 1)
if (-not $localSha) { Say 'EROARE: HEAD ilizibil.'; exit 2 }
$localShort = $localSha.Substring(0,7)

$serverLine = ((Invoke-Git ls-remote $Remote $Branch).Out | Select-Object -First 1)
$serverSha = if ($serverLine) { ($serverLine -split '\s+')[0] } else { $null }

if (-not $serverSha) { Say ("EROARE: ramura '$Branch' nu exista pe $Remote."); exit 2 }

$toPush = 0
$cnt = (Invoke-Git rev-list --count "$Remote/$Branch..HEAD").Out | Select-Object -First 1
if ($cnt) { $toPush = [int]$cnt }

Line '=============================================='
Line '  PUSH - masurare'
Line '=============================================='
Say ("  local   : " + $localShort)
Say ("  server  : " + $serverSha.Substring(0,7))
Say ("  de urcat: $toPush comit" + $(if ($toPush -eq 1) { '' } else { 'uri' }))
Line

if ($toPush -eq 0) {
    Say 'Nimic de urcat. Serverul e deja la HEAD.'
    exit 0
}

Line '  comiturile care urca:'
(Invoke-Git log --oneline "$Remote/$Branch..HEAD").Out | ForEach-Object { Say ("    $_") }
Line

if ($DryRun) {
    Say 'DRY-RUN: nu s-a impins nimic.'
    exit 0
}

# --- 2. REVIEW pe range ----------------------------------------------------
# Non-blocant prin constructie: orice esec, orice timeout, orice rate limit
# se inregistreaza si se merge la push oricum.
$reviewState = 'cerut'
$reviewNote  = ''

if ($SkipReview) {
    $reviewState = 'sarit'
    $reviewNote  = '--SkipReview'
} elseif (-not (Test-Path $LRC)) {
    $reviewState = 'absent'
    $reviewNote  = 'lrc.exe nu e pe loc'
} else {
    Say '  review LRC pe range-ul care urca (nu blocheaza)...'
    $log = Join-Path $env:TEMP ("lrc-push-" + [guid]::NewGuid().ToString('N') + '.log')

    $p = Start-Process -FilePath $LRC -PassThru -NoNewWindow -RedirectStandardOutput $log `
         -RedirectStandardError "$log.err" `
         -ArgumentList @('review','--range',"$Remote/$Branch..HEAD",'--no-serve','--output','json')

    $done = $p.WaitForExit($ReviewTimeoutSec * 1000)
    if (-not $done) {
        try { $p.Kill() } catch { }
        $reviewState = 'timeout'
        $reviewNote  = "nu a raspuns in ${ReviewTimeoutSec}s"
    } else {
        $code = $p.ExitCode
        $out  = ''
        if (Test-Path $log) { $out = [System.IO.File]::ReadAllText($log) }
        $rid  = ''
        if ($out -match 'Review submitted, ID:\s*(\d+)') { $rid = $Matches[1] }

        if ($code -eq 0) {
            $reviewState = 'trecut'
            $reviewNote  = $(if ($rid) { "review #$rid" } else { 'ok' })
        } else {
            $why = ''
            foreach ($pat in @('rate.?limit','too many requests','quota','429')) {
                if ($out -match $pat) { $why = 'rate limit'; break }
            }
            if (-not $why) { $why = "lrc exit $code" }
            $reviewState = 'picat'
            $reviewNote  = "$why (push merge oricum)"
        }
    }
    foreach ($f in @($log, "$log.err")) { if (Test-Path $f) { Remove-Item $f -Force -ErrorAction SilentlyContinue } }
}
Say ("  review: $reviewState - $reviewNote")
Line

# --- 3. PUSH ---------------------------------------------------------------
# intentionat DUPA review si intentionat neconditionat de rezultatul lui
Say '  push...'
$pushRes = Invoke-Git push $Remote "HEAD:refs/heads/$Branch"
Say ("  push exit: " + $pushRes.Code)
Line

# --- 4. VERIFICARE pe server ----------------------------------------------
# singurul loc unde se afla adevarul. niciodata codul de iesire al shell-ului.
$after = ((Invoke-Git ls-remote $Remote $Branch).Out | Select-Object -First 1)
$afterSha = if ($after) { ($after -split '\s+')[0] } else { $null }

Line '=============================================='
Line '  PUSH - verificare pe server'
Line '=============================================='

if ($afterSha -and $afterSha -eq $localSha) {
    Say ("  OK  server = " + $afterSha.Substring(0,7) + " = HEAD local")
    Say ("  comituri urcate: " + $toPush)
    if ($reviewState -eq 'picat' -or $reviewState -eq 'timeout') {
        Say ("  NOTE: review LRC a picat (" + $reviewNote + "). Push-ul a mers oricum, intentionat.")
    }
    exit 0
}

if (-not $afterSha) {
    Say '  FAILED: serverul nu mai raspunde. Nu raporta succes.'
    exit 1
}

Say ("  FAILED: server = " + $afterSha.Substring(0,7) + "  !=  local = " + $localShort)
Say '  Pushul NU a ajuns. Nu raporta succes.'
exit 1