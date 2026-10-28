#!/usr/bin/env powershell
<#
.SYNOPSIS
    Wrapperul programat pentru mavis-sync.ps1. Ruleaza puntea o data pe zi
    si lasa urma scrisa, ca o rulare sa nu poata fi ceva ce n-a fost vazut.

.DESCRIPTION
    mavis-sync.ps1 face munca. Acest wrapper adauga ce lipseste la o rulare
    nesupravegheata:

    1. LOG DATAT - tot ce iese ajunge in logs\mavis-sync-YYYY-MM-DD.log,
       cu timestamp. Fara log, o rulare reusita si una care a picat silentios
       arata la fel.
    2. HALT AND REPORT - daca apare conflict, divergenta sau un cod de
       iesire nenul, runnerul se opreste si scrie explicit ce a gasit.
       NU face nimic altceva. Nu repara. Nu "rezolva" nimic singur.
    3. INTERZIS ABSOLUT - reset --hard, checkout forcat, clean, sau orice
       operatie care ar putea arunca lucru facut de un om. Daca apare
       conflict, iesirea e raportul, nu o stergere.

    ASCII PUR, din cauza parserului Windows PowerShell 5.1.

.PARAMETER DryRun
    Nu ruleaza nimic, doar arata ce ar face.
#>

[CmdletBinding()]
param(
    [switch]$DryRun
)

$ErrorActionPreference = 'Continue'

$BASE = Split-Path -Parent $PSScriptRoot
$LOGS = Join-Path $BASE 'logs'
$SYNC = Join-Path $PSScriptRoot 'mavis-sync.ps1'

if (-not (Test-Path $SYNC)) {
    Write-Output ("EROARE: nu exista " + $SYNC)
    exit 2
}

if (-not (Test-Path $LOGS)) {
    New-Item -ItemType Directory -Force -Path $LOGS | Out-Null
}

$azi    = Get-Date -Format 'yyyy-MM-dd'
$logFis = Join-Path $LOGS ("mavis-sync-{0}.log" -f $azi)
$stamp  = Get-Date -Format 'HH:mm:ss'

function Scrie([string]$t, [string]$nivel = 'INFO') {
    $linie = ('[{0}] [{1}] {2}' -f $stamp, $nivel, $t)
    Add-Content -Path $logFis -Value $linie -Encoding UTF8
    Write-Output $linie
}

Scrie ('=' * 60)
Scrie ("Rulare programata. DryRun={0}" -f $DryRun)

if ($DryRun) {
    Scrie 'DryRun: NU ruleaza nimic. Iesire.'
    exit 0
}

Scrie 'Se ruleaza mavis-sync.ps1 ...'

$output = & powershell -NoProfile -File $SYNC 2>&1
$code   = $LASTEXITCODE

foreach ($l in $output) {
    $linie = [string]$l
    $nivel = if ($linie -match 'error|fail') { 'WARN' } else { 'INFO' }
    Scrie $linie $nivel
}

Scrie ("Cod de iesire al puntii: {0}" -f $code)

# HALT AND REPORT: semnele de conflict trebuie sa se opreasca, nu sa treaca.
#
# ATENTIE LA FALSUL POZITIV: cautam MARCATORI clari, nu cuvinte.
# Un regex larg ca 'conflict|diverg' s-a declansat pe linia curata
# "OK - sincronizare fara conflict, fara divergent" - adica exact pe
# textul NEGAT. Un HALT fals oprit o punte sanatoasa zilnic.
#
# Regula: linia e conflict doar daca ARE un marker SI NU contine negare.
$MARCAJORI = '^(CONFLICT|CONFLICTING)|\bfatal:|Automatic merge failed|error: Your local changes|merge failed|net/merge|refus[ae] to merge|Could not resolve|unmerged'
$NEGARI    = 'fara conflict|fara divergent|without conflict|no conflict|conflict.*free'

$pericol = @()
foreach ($l in $output) {
    $linie = [string]$l
    $areMarker = [regex]::IsMatch($linie, $MARCAJORI)
    $areNegare = [regex]::IsMatch($linie, $NEGARI)
    if ($areMarker -and -not $areNegare) { $pericol += $linie }
}

if ($pericol.Count -gt 0) {
    Scrie '' 'HALT'
    Scrie ('AU APARUT {0} RINDURI DE CONFLICT/DIVERGENTA.' -f $pericol.Count) 'HALT'
    foreach ($l in $pericol) { Scrie ('  > ' + $l) 'HALT' }
    Scrie 'PUNTEA SE OPRESTE AICI. Nimic nu se repara automat.' 'HALT'
    Scrie ('Detalii in fisierul: {0}' -f $logFis) 'HALT'
    Scrie 'Actiune ceruta: interventa umana. Nu se ruleaza reset --hard.' 'HALT'
    exit 3
}

if ($code -ne 0) {
    Scrie '' 'HALT'
    Scrie ("Cod de iesire nenul ({0}). Puntea s-a oprit cu problema." -f $code) 'HALT'
    Scrie ('Detalii in fisierul: {0}' -f $logFis) 'HALT'
    exit $code
}

Scrie 'OK - sincronizare fara conflict, fara divergent.'
Scrie ('Log: {0}' -f $logFis)
exit 0