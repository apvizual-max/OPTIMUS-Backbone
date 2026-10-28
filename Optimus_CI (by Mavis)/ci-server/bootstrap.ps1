# bootstrap.ps1 - porneste serverul Mavis-Optimus-CI in cel mult 5 minute.
#
# ASTA E PUNTA DE REINTRARE: dupa un an, daca nu mai functioneaza nimic,
# se ruleaza asta si totul e inapoi.
#
# Ce face, in ordine:
#   1. verifica Docker
#   2. asigura tokenul GitHub (il ia din gh auth daca lipseste; NU se afiseaza)
#   3. construiesc imaginea
#   4. recreeaza containerul Mavis-Optimus-CI cu monturile corecte
#   5. asteapta sanatatea
#   6. ruleaza doctorul si arata raportul de pornire
#
# Nu atinge nimic din proiectele surori (CD, PKMS). Nu face push. Nu face
# commit. Doar porneste serverul si spune, masurat, daca sistemul e gata.
#
# ASCII ONLY: executat de Windows PowerShell 5.1.

[CmdletBinding()]
param(
    [switch]$Rebuild,
    [switch]$SkipDoctor
)

$ErrorActionPreference = 'Stop'

$Root       = Split-Path -Parent $PSScriptRoot
$CiServer   = Join-Path $Root 'ci-server'
$GitData    = 'E:\Google\GitData-Optimus-CI'
$GaData     = 'C:\Users\apviz\.minimax\google-access\data'
$Secrets    = 'E:\--- System Secrets'
$TokenFile  = Join-Path $Secrets 'github-token-apvizual-max.txt'
$ConsentFile = Join-Path $GaData 'consent-result.json'
$SharedGate = 'C:\Users\apviz\.minimax-agent\projects\scripts\git-hooks'
$Image      = 'mavis/optimus-ci:1.0.0'
$Container  = 'Mavis-Optimus-CI'
$ApiPort    = 8790

function Say {
    param([string]$Message)
    Write-Host $Message
}

# Apeluri native fara capcana PS 5.1: un program care scrie pe stderr cu
# $ErrorActionPreference='Stop' arunca NativeCommandError chiar daca a reusit.
# Aici stderr-ul e capturat ca text, iar verdictul vine din exit code.
function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)][string]$Exe,
        [string[]]$NativeArgs = @()
    )
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $out = & $Exe @NativeArgs 2>&1 | Out-String
    $code = $LASTEXITCODE
    $ErrorActionPreference = $prev
    return @{ Code = $code; Out = $out }
}

# --- 1. docker --------------------------------------------------------------
Say '=== 1. Docker ==='
$dockerOk = $null -ne (Get-Command docker -ErrorAction SilentlyContinue)
if (-not $dockerOk) { Say 'ERROR: docker nu e pe PATH.'; exit 2 }
$dv = Invoke-Native -Exe 'docker' -NativeArgs @('version', '--format', '{{.Server.Version}}')
if ($dv.Code -ne 0) { Say ('ERROR: docker daemon nu raspunde: ' + $dv.Out); exit 2 }
Say ('docker server: ' + $dv.Out.Trim())

# --- 2. token ---------------------------------------------------------------
Say '=== 2. Token GitHub ==='
if (-not (Test-Path -LiteralPath $TokenFile)) {
    $tok = & gh auth token 2>$null
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($tok)) {
        Say 'ERROR: nu exista token GitHub si gh auth token a esuat.'
        Say '      Autentifica cu: gh auth login'
        exit 2
    }
    $enc = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($TokenFile, $tok.Trim(), $enc)
    Say 'token creat in volumul de secrete (nu se afiseaza)'
} else {
    Say 'token prezent (nu se afiseaza)'
}

# --- 3. imagine -------------------------------------------------------------
Say '=== 3. Imagine ==='
if ($Rebuild) { Invoke-Native -Exe 'docker' -NativeArgs @('image', 'rm', '-f', $Image) | Out-Null }
$have = Invoke-Native -Exe 'docker' -NativeArgs @('images', '--format', '{{.Repository}}:{{.Tag}}')
if ($have.Out -notmatch [regex]::Escape($Image)) {
    Say 'construiesc imaginea (poate dura 1-2 minute)...'
    $b = Invoke-Native -Exe 'docker' -NativeArgs @('build', '-t', $Image, $CiServer)
    ($b.Out -split "`n") | Select-Object -Last 8 | ForEach-Object { Say ('  ' + $_.TrimEnd()) }
    if ($b.Code -ne 0) { Say ('ERROR: build esuat, exit ' + $b.Code); exit 1 }
} else {
    Say ('imagine deja exista: ' + $Image)
}

# --- 4. container -----------------------------------------------------------
Say '=== 4. Container ==='
$existing = Invoke-Native -Exe 'docker' -NativeArgs @('ps', '-a', '--format', '{{.Names}}')
if ($existing.Out -match [regex]::Escape($Container)) {
    Say 'recreez containerul existent (strict doar pe acest container)'
    Invoke-Native -Exe 'docker' -NativeArgs @('rm', '-f', $Container) | Out-Null
}

$runArgs = @(
    'run', '-d',
    '--name', $Container,
    '--restart', 'unless-stopped',
    '-p', ('127.0.0.1:' + $ApiPort + ':' + $ApiPort),
    '-v', ($Root + ':/workspace/project'),
    '-v', ($GitData + ':/workspace/gitdata'),
    '-v', ($TokenFile + ':/secrets/github-token-apvizual-max.txt:ro'),
    '-v', ($ConsentFile + ':/ga-data/consent-result.json:ro'),
    '-v', ($SharedGate + ':/workspace/gate:ro'),
    '-e', 'MAVIS_SECRET_SCANNER=/workspace/project/scripts/scan-staged-secrets.ps1',
    '-e', 'MAVIS_PUSH_GATE=/workspace/gate/pre-push',
    $Image
)
$run = Invoke-Native -Exe 'docker' -NativeArgs $runArgs
Say ('  ' + $run.Out.Trim())
if ($run.Code -ne 0) { Say ('ERROR: container nu a pornit, exit ' + $run.Code); exit 1 }

# --- 5. sanatate ------------------------------------------------------------
Say '=== 5. Sanatate ==='
$ok = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 2
    try {
        $r = Invoke-RestMethod -Uri ('http://127.0.0.1:' + $ApiPort + '/health') -TimeoutSec 5
        if ($r.ok) { $ok = $true; break }
    } catch { }
}
if (-not $ok) { Say 'ERROR: containerul nu a raspuns la /health in 60s.'; exit 1 }
Say ('containerul e viu: ' + $r.container + ' ' + $r.version)

# --- 6. doctor --------------------------------------------------------------
if (-not $SkipDoctor) {
    Say '=== 6. Doctor ==='
    $doc = Invoke-Native -Exe 'docker' -NativeArgs @('exec', $Container, 'node', '/opt/optimus-ci/engine/cli.mjs', 'doctor')
    ($doc.Out -split "`n") | ForEach-Object { if ($_.Trim() -ne '') { Say ('  ' + $_.TrimEnd()) } }
    Say ('doctor exit: ' + $doc.Code)
    Say ''
    Say 'Daca vrei si starea repo-urilor:'
    Say ('  docker exec ' + $Container + ' node /opt/optimus-ci/engine/cli.mjs status')
}

Say ''
Say 'GATA. Serverul e sus. Urmatorul pas: cer R0 si apeleaza pluginul (ci_push).'
exit 0
