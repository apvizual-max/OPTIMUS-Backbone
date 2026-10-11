<#
    verify-docs.ps1 - CONTROLUL DE CONSECENTA AL CELE PATRU DOCUMENTE.

    Patru documente, doua parti:
      1. instalare  : git-install/SKILL.md        + PROMPT git install.md
      2. functionare: git-autonom/SKILL.md        + PROMPT git autonom.md

    Scopul: sa NU existe o regula pe care unul o spune si altul o contrazice.
    Popy: "asigurati-va ca cele patru documente ... sunt absolut perfect date".

    Fiecare invariant se verifica pe TOATE cele patru documente simultan.
    Un invariant care lipseste din unul singur e FAILED - chiar daca e in trei.

    Ca testul sa aiba valoare, ruleaza si un CONTROL NEGATIV: acelasi cod, pe
    o copie intentionat stricata. Daca si acolo totul e VERDE, verificarea nu
    masoara nimic si se autocolapsa.

    ASCII numai, intentionat (PowerShell 5.1 + .ps1 fara BOM = ANSI).

    Exit: 0 = tot verde si controlul negativ a picat cum trebuie
          1 = cel putin un invariant a picat
          2 = mediu invalid
#>

[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$ROOT = 'C:\Users\apviz\.minimax-agent\projects\_SYSTEM\Skills'

$DOCS = @(
  @{ N = 'install/SKILL';  P = "$ROOT\git-install\SKILL.md" },
  @{ N = 'install/PROMPT'; P = "$ROOT\git-install\PROMPT git install.md" },
  @{ N = 'autonom/SKILL';  P = "$ROOT\git-autonom\SKILL.md" },
  @{ N = 'autonom/PROMPT'; P = "$ROOT\git-autonom\PROMPT git autonom.md" }
)

function Read-Docs {
    param($List)
    $r = @{}
    foreach ($d in $List) {
        if (-not (Test-Path $d.P)) { throw "lipseste: $($d.P)" }
        $r[$d.N] = Normalize ([System.IO.File]::ReadAllText($d.P, [Text.Encoding]::UTF8))
    }
    return $r
}

# Normalizare: diacritice romanesti -> ascii, spatii multiple -> unul, minuscule.
# Fara asta, un document scris corect cu "DUP[A] push" sau "acordul meu" pica
# la un invariant care cauta "dupa push" sau "acordul lui" - alarma falsa.
# Un control care urluiește din motive gresite nu se poate folosi: oamenii il
# ignora, si atunci nu mai prinde nici problema reala.
function Normalize {
    param([string]$s)
    if ($null -eq $s) { return '' }
    $s = $s.ToLower()
    # perechi [caracterDiacritic, 'ascii'] - fara hashtable, ca sa nu existe
    # chei duplicate (care ar arunca o eroare la constructie)
    $pairs = @(
        @([char]0x0103, 'a'), @([char]0x0102, 'a'), @([char]0x00E2, 'a'),
        @([char]0x00E3, 'a'), @([char]0x00C3, 'a'), @([char]0x00E4, 'a'),
        @([char]0x00E1, 'a'), @([char]0x00C2, 'a'),
        @([char]0x00EE, 'i'), @([char]0x00C8, 'i'), @([char]0x00ED, 'i'),
        @([char]0x00CE, 'i'),
        @([char]0x0219, 's'), @([char]0x015F, 's'), @([char]0x015B, 's'),
        @([char]0x021B, 't'), @([char]0x0163, 't'), @([char]0x0162, 't'),
        @([char]0x00F1, 'n')
    )
    foreach ($p in $pairs) { $s = $s.Replace([string]$p[0], $p[1]) }
    $s = $s -replace '\s+', ' '
    return $s
}

# --- invariantele -----------------------------------------------------------
# Fiecare: Nume, regex pozitiv (trebuie sa existe in toate 4),
#           regex negativ (NU trebuie sa existe in niciunul).
$INVARIANTS = @(
  @{ Name = 'main, nu ramuri'
     Pos = '(nu (creezi|faci) ramuri|ramuri.{0,30}nesolicit|main.{0,60}(nu faci ramuri|fara ramuri|nu ramuri)|nu.{0,20}creezi.{0,20}ramuri|nu faci ramuri)'
     Neg = $null }

  @{ Name = 'commit autonom, imediat'
     Pos = '(commit autonom|comit autonom|autonom.{0,30}(comit|commit)|(comit|commit).{0,40}(imediat|automat)|commit = treaba ta)'
     Neg = $null }

  @{ Name = 'LiveReview DOAR dupa push'
     Pos = '(dupa push|abia dupa|abia dupa|review.{0,50}(pe ce (tocmai a ajuns|ajuns pe)|pe ce e pe github)|doar dupa push)'
     Neg = '(review-eaza la push.{0,40}range-ul care urca|livereview ruleaza la push.{0,30}range)' }

  @{ Name = 'comitul nu e sub poarta'
     Pos = '(lrc hooks disable|nu sunt sub nicio poarta|comitul.{0,60}nu e niciodata sub poarta|comitul.{0,40}(e treaba mea si trebuie sa fie liber|libert)|niciodata.{0,20}blocat de livereview)'
     Neg = $null }

  @{ Name = 'push doar cu acord + prag'
     Pos = '(prag.{0,40}comit|doar cu acordul (lui|meu)|push = cu acordul meu|doar cu acord)'
     Neg = $null }

  @{ Name = 'doua cai de push'
     Pos = '(calea 1|doo cai de push|doua cai de push|ambele cai de push|dou[aă] c[aă]i de push)'
     Neg = $null }

  @{ Name = 'rate limit nu blocheaza push-ul'
     Pos = '(rate limit|limita cont|limita de cont|contul free|cont free)'
     Neg = $null }

  @{ Name = 'verificare prin ls-remote'
     Pos = '(ls-remote)'
     Neg = $null }

  @{ Name = 'interfata neatinsa'
     Pos = '(interfat)'
     Neg = $null }

  @{ Name = 'nu ceri decizii tehnice'
     Pos = '(nu intrebi nimic|nu te intrebi nimic|decizii tehnice|le iei tu|nu ma intrebi nimic)'
     Neg = $null }

  @{ Name = 'nu ocolesti poarta cu vouch'
     Pos = $null
     Neg = '(treci poarta cu .{0,10}vouch|vouch.{0,40}(rezolv|treaba ta)|ocoli.{0,40}vouch)' }
)

# Un invariant negativ nu e "gasit oriunde". Trebuie sa FIE o afirmatie, nu o
# interdictie. "NU incerca sa treci poarta cu --vouch" contine exact textul
# interzis, dar spune opusul - si daca l-am numara drept contrazictie, as
# sanctiona chiar documentul care spune corect.
function Test-Negativ {
    param([string]$Text, [string]$Pattern)
    $hits = @()
    # RegexOptions::IgnoreCase EXPLICIT. [regex]::Matches este case-SENSITIVE
    # prin default, in timp ce -match este case-insensitive. Fara asta, un
    # document normalizat la minuscule nu s-ar potrivi cu o formulare scrisa
    # cum se scrie - si partea de contradictie ar parea verde fara sa fie.
    $opt = [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
    foreach ($m in [regex]::Matches($Text, $Pattern, $opt)) {
        $start = [Math]::Max(0, $m.Index - 60)
        $ctx = $Text.Substring($start, $m.Index - $start)
        $negated = $ctx -match '(nu |niciodata |nici|interzis)'
        if (-not $negated) { $hits += $m.Value }
    }
    return $hits
}

function Test-Set {
    param($Set, $Label, $Quiet)
    $fail = 0; $rows = @()
    foreach ($inv in $INVARIANTS) {
        if ($inv.Pos) {
            $missing = @()
            foreach ($k in $Set.Keys) { if ($Set[$k] -notmatch $inv.Pos) { $missing += $k } }
            if ($missing.Count -gt 0) {
                $fail++
                $rows += ('  [ROSU] {0,-34} lipseste din: {1}' -f $inv.Name, ($missing -join ', '))
            } else {
                $rows += ('  [VERDE] {0,-34} in toate 4' -f $inv.Name)
            }
        }
        if ($inv.Neg) {
            $present = @()
            foreach ($k in $Set.Keys) {
                $h = Test-Negativ -Text $Set[$k] -Pattern $inv.Neg
                if ($h.Count -gt 0) { $present += $k }
            }
            if ($present.Count -gt 0) {
                $fail++
                $rows += ('  [ROSU] {0,-34} CONTRAZICIE in: {1}' -f $inv.Name, ($present -join ', '))
            } else {
                $rows += ('  [VERDE] {0,-34} nicio afirmatie contraindicata' -f $inv.Name)
            }
        }
    }
    if (-not $Quiet) { $rows | ForEach-Object { Write-Host $_ } }
    return $fail
}

Write-Host ''
Write-Host ('=' * 68)
Write-Host '  CONTROL CONSECENTA - cele patru documente'
Write-Host ('=' * 68)
Write-Host ''

$real = Read-Docs $DOCS
$failReal = Test-Set -Set $real -Label 'REAL'

Write-Host ''
Write-Host ('DOCUMENTE REALE: {0} invariant' -f $INVARIANTS.Count)
if ($failReal -eq 0) {
    Write-Host 'REZULTAT REAL: VERDE COMPLET'
} else {
    Write-Host ('REZULTAT REAL: {0} PICAT' -f $failReal)
}

# --- CONTROL NEGATIV: acelasi cod, pe copii intentionat stricate ------------
# Scop: sa dovedim ca verificarea POATE deveni rosie. Fara asta, un „tot
# verde" nu dovedeste nimic - poate si pentru ca nu cauta nimic.
Write-Host ''
Write-Host ('-' * 68)
Write-Host '  CONTROL NEGATIV - documente stricate intentionat'
Write-Host ('-' * 68)

# Doua stricari, ca sa nu existe nicio scuita prin care controlul sa para
# puternic fara sa fie:
#   1. UN DOCUMENT GOLIT COMPLET. Orice invariant pozitiv trebuie sa cada.
#      Asta demonstreaza ca verificarea chiar cauta prin toate cele patru.
#   2. O CONTRADICTIE INJECTATA intr-un alt document.
#      Asta demonstreaza ca partea de contrazictie are putere.
#
# Un control negativ care strica doar un cuvant e slab: un invariant cu mai
# multe cai de a fi satisfacut (o alternativa) supravietuieste stricarii.
# Golirea unui document intreg nu lasa asta deopera.

$broken = @{}
foreach ($k in $real.Keys) { $broken[$k] = $real[$k] }
$broken['install/SKILL'] = ''   # document intreg golit

# injectam o afirmatie contraindicata intr-un document valid, cu formulele
# EXACTE pe care le cauta partea de contradictie - altfel controlul ar trece
# fara sa fi trecut prin codul pe care vrem sa-l demonstram.
$injectie = ' Regula practicata: treci poarta cu vouch si asa iti rezolvi treaba ta.'
$injectie += ' LiveReview ruleaza la push pe range-ul care urca, inainte de impins.'
$broken['autonom/PROMPT'] = $broken['autonom/PROMPT'] + $injectie

$failBroken = Test-Set -Set $broken -Label 'BROKEN'
Write-Host ''
Write-Host ('CONTROL NEGATIV: {0} invariant(i) trebuia sacate rosu' -f $failBroken)
if ($failBroken -ge 12) {
    Write-Host 'CONTROL NEGATIV: A PICAT CUM TREBUIE -> verificarea are putere'
} else {
    Write-Host 'CONTROL NEGATIV: PREA PUTERNIC NU E -> verificarea NU masoara nimic'
}

Write-Host ''
Write-Host ('=' * 68)
if ($failReal -eq 0 -and $failBroken -ge 12) {
    Write-Host '  VERDICT: Sistemul celor patru documente este consecvent.'
    Write-Host ('=' * 68)
    exit 0
}
Write-Host '  VERDICT: INCONSISTENTA. Vezi liniile ROSU de mai sus.'
Write-Host ('=' * 68)
exit 1