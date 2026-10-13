#!/usr/bin/env powershell
<#
.SYNOPSIS
    Compilator de meta-prompt: aduna regulile din surse si emite UN prompt
    de pornire rapida pentru orice sesiune noua sau orice repo nou.

.DESCRIPTION
    Fiecare sesiune noua repeta aceeasi intrebare: ce reguli se aplica acum?
    Asta are raspuns pretuit, dar raspunsul e spalat in 15+ fisiere.

    Acest script le aduna intr-un singur document gata de trimis, fara sa
    invente nimic. Ce e in fisierele-sursa ramane in fisierele-sursa; aici
    se doar le stranse laolalta si se marcheaza.

    Nu ruleaza git. Nu scrie in repo-uri. Nu atinge nimic.
    Singurul efect: scrie (sau afiseaza) un singur fisier de iesire.

    RULE TEHNICA: fisierul asta este ASCII PUR. Caracterele Unicode
    (linii punctate, diacritice) rup parserul lui Windows PowerShell 5.1,
    chiar si in interiorul sirurilor cu interpolare.

.PARAMETER Output
    Fisierul de iesire. Implicit: docs/META-PROMPT.md

.PARAMETER Show
    Scrie doar pe ecran, nu atinge disk-ul.

.EXAMPLE
    powershell -NoProfile -File scripts\meta-prompt.ps1
    powershell -NoProfile -File scripts\meta-prompt.ps1 -Show
#>

[CmdletBinding()]
param(
    [string]$Output = 'docs/META-PROMPT.md',
    [switch]$Show
)

$ErrorActionPreference = 'Stop'

$BASE = Split-Path -Parent $PSScriptRoot

# Surse, in ordinea in care trebuie citite la pornire.
# oblig = true -> nu se poate porni fara ea
$SURSE = @(
    @{ f = 'docs/CI-POLICY.md';                     rol = 'governanta'; oblig = $true  }
    @{ f = 'docs/BRIDGE-LOCAL-CLOUD.md';            rol = 'punte';      oblig = $true  }
    @{ f = 'docs/PROTOCOL-DENUMIRE-LOCAL-CLOUD.md'; rol = 'namespace';  oblig = $true  }
    @{ f = 'docs/INVENTAR-REPO-URI.md';             rol = 'inventar';   oblig = $false }
    @{ f = 'docs/RECUPERARE-GIT.md';                rol = 'recuperare'; oblig = $false }
    @{ f = 'docs/CONFLICTE-DOZTRINA.md';            rol = 'diverse';    oblig = $false }
)

# ATENTIE: pkms-vault-automation e pe 'master', NU pe 'main'.
$ramuri = [ordered]@{
    'MAVIS-CLOUD'           = 'main'
    'MAVIS-OPTIMUS-CI'      = 'main'
    'Optimus-Mavis-Skills'  = 'main'
    'pkms-vault-automation' = 'master'
}

$out = New-Object System.Text.StringBuilder

function Add-Line([string]$t = '') { [void]$out.AppendLine($t) }

Add-Line '# META-PROMPT - prompt de pornire rapida'
Add-Line
Add-Line ("Generat: {0}  |  sursa: {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm'), $PSCommandPath)
Add-Line
Add-Line 'Regulile de mai jos NU sunt aici. Sunt in fisierele-sursa, citite la'
Add-Line 'prima accesare. Documentul asta iti spune CE sa citesti, in ce ordine.'
Add-Line
Add-Line '## 1. Obiectiv'
Add-Line
Add-Line 'Construirea si operarea sistemului OPTIMUS Prime / Mavis Optimus CI.'
Add-Line 'Regiune: niciun pas nu se declara daca nu a fost masurat.'
Add-Line
Add-Line '## 2. Triada inviolabila'
Add-Line
Add-Line '| Pilon | Cand se declanseaza | Cine decide |'
Add-Line '|---|---|---|'
Add-Line '| ACCES | Ai nevoie de ceva ce poate da doar Popy: cheie, cod MFA, confirmare de plata, actiune fizica. | Popy |'
Add-Line '| DRIFT | Actiunea nu mai e urmaribila la taskul activ. | Eu - ma opresc si raportez |'
Add-Line '| TAIL | Te-ai batut de acelasi lucru si nu iese nimic nou. | Eu - schimb perspectiva |'
Add-Line
Add-Line 'Nu te opresti pentru: dificultate tehnica, alegere tehnica, sau pentru a'
Add-Line 'construi optiuni si a intreba care se alege. Alegerile tehnice sunt ale mele.'
Add-Line
Add-Line '## 3. Porti si rate'
Add-Line
Add-Line '- COMMIT pe main: automat, fara intrebare'
Add-Line '- PUSH spre remote: cer R0 explicit'
Add-Line '- MERGE de PR pe GitHub: este push, deci R0'
Add-Line '- DEPLOY sau publicare in extern: R0, intotdeauna'
Add-Line '- Stergere definitiva: interzisa. Se arhiveaza prin git mv'
Add-Line '- git clean -fdx, git reset --hard, force push: interzise'
Add-Line
Add-Line '## 4. Namespace-uri'
Add-Line
Add-Line 'minimax si Hermes sunt universuri SEPARATE. Nu folosi unelte, MCP-uri,'
Add-Line 'secrete sau profiluri ale celuilalt. Daca minimax are nevoie de ce are'
Add-Line 'Hermes, construieste o dublura: doua instante separate nu se pot distruge'
Add-Line 'reciproc, una comuna da. Numeste namespace-ul la fiecare folosire de unealta.'
Add-Line
Add-Line '## 5. Maparea ramurilor'
Add-Line
Add-Line '| Repo | Ramura |'
Add-Line '|---|---|'
foreach ($k in $ramuri.Keys) {
    Add-Line ('| {0} | {1} |' -f $k, $ramuri[$k])
}
Add-Line
Add-Line '> CAPCANA MASURATA: git ls-remote origin main pe Vault intoarce VID cu'
Add-Line '> exit 0. Nu e dezincronizare, e un branch care nu exista. Interogheaza'
Add-Line '> intotdeauna ramura de mai sus.'
Add-Line
Add-Line '## 6. Magistrala de date: QUEUE/'
Add-Line
Add-Line 'QUEUE/ este singurul canal de intrare intre masini. Nu se cauta cross-mediu'
Add-Line 'cronuri: taskurile Cloud-ului traiesc pe platforma web, cele locale in'
Add-Line 'Task Scheduler. Fiecare scrie acolo, nu in fata celuilalt.'
Add-Line
Add-Line 'Citeste la pull: QUEUE\TASKS-FOR-CLOUD.md'
Add-Line 'Livrare:      QUEUE\DONE\TASK-NNN.md, cu [x] pe bilet'
Add-Line
Add-Line '## 7. Ce sa citesti la pornire'
Add-Line

$absente = @()
foreach ($s in $SURSE) {
    $exista = Test-Path (Join-Path $BASE $s.f)
    if ($exista) {
        $badge = if ($s.oblig) { 'OBLIGATORIU' } else { 'optional' }
        Add-Line ('- [x] {0} - rol: {1} - {2}' -f $s.f, $s.rol, $badge)
    } else {
        $absente += $s.f
        $badge = if ($s.oblig) { 'OBLIGATORIU' } else { 'optional' }
        Add-Line ('- [ ] {0} - LIPSA DE PE DISC - rol: {1} - {2}' -f $s.f, $s.rol, $badge)
    }
}
Add-Line

if ($absente.Count -gt 0) {
    Add-Line '### Surse lipsa'
    Add-Line
    Add-Line 'Se raporteaza ca MASURATURA INCOMPLETA. Nu se inventa continutul lor,'
    Add-Line 'si nu se porneste un task care depinde de ele.'
    Add-Line
    foreach ($a in $absente) { Add-Line ('- {0}' -f $a) }
    Add-Line
}

Add-Line '## 8. Ordinea primei sesiuni'
Add-Line
Add-Line '1. Nu declara nimic. Citeste sursele de mai sus.'
Add-Line '2. Masoareaza starea reala a celor 4 repo-uri, pe ramura lor.'
Add-Line '3. Verifica ce a fost deja rezolvat si de cine, ca sa nu repeti lucru.'
Add-Line '4. Abia apoi formuleaza obiectivul si propune un plan.'
Add-Line
Add-Line '## 9. Cinci reguli care nu se negotiaza'
Add-Line
Add-Line '1. Un numar pe care nu l-ai masurat, nu il scrii.'
Add-Line '2. Un artefact pe care nu l-ai deschis, nu il aprobi.'
Add-Line '3. Un raport al altui agent e o afirmatie, nu o masuratoare.'
Add-Line '4. Un workflow care doar TRIMITE taskul nu produce efect in acelasi run.'
Add-Line '5. Un check care nu poate esua nu e check.'

$text = $out.ToString()

if ($Show) {
    Write-Output $text
    exit 0
}

$dest = Join-Path $BASE $Output
$dir = Split-Path -Parent $dest
if ($dir -and -not (Test-Path $dir)) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}
[System.IO.File]::WriteAllText($dest, $text, (New-Object System.Text.UTF8Encoding($false)))

$kb = [math]::Round((Get-Item $dest).Length / 1KB, 1)
Write-Output ('OK  {0}' -f $dest)
Write-Output ('    {0} linii, {1} KB' -f ($text -split "`n").Count, $kb)
Write-Output ('    surse prezente: {0}/{1}' -f ($SURSE.Count - $absente.Count), $SURSE.Count)
if ($absente.Count -gt 0) {
    Write-Output ('    LIPSA: {0}' -f ($absente -join ', '))
}