<#
    verify-docs.ps1 - CONTROLUL DE CONSECENTA AL CELE PATRU DOCUMENTE.

    Patru documente, doua parti:
      1. instalare  : git-install/SKILL.md     + PROMPT git install.md
      2. functionare: git-autonom/SKILL.md     + PROMPT git autonom.md

    Scopul: sa NU existe o regula pe care unul o spune si altul o contrazice.

    TREI CORECTII IMPUSE DE UN VERIFICATOR INDEPENDENT (2026-10-11):
      1. Pattern-urile de contradictie erau prea inguste - se potriveau pe o
         singura formulare. Acum cauta CONTRASTUL semantic.
      2. Controlul negativ se auto-verifica: injecta exact sirurile pe care le
         cautau propriile regex. Acum goleste pe RAND documentele, fara sa
         depinda de formularea niciunui regex.
      3. Verificarile pozitive erau de PREZENTA, nu de SUBSTANTA: stergerea
         intregului bloc "doua cai de push" lasa totul verde. Acum unele
         invariante cer MULTE formulari simultan (Both).

    ASCII numai, intentionat: acest script se ruleaza cu regula pe care o
    impune el insusi, si pe care o cere si autonom/SKILL.md. Zero bytes > 127.

    Exit: 0 = consecvent, iar controlul negativ a picat in toate rundele
          1 = inconsistent sau control fara putere
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

# ASCII -> diacriticele romanesti, ca un invariant scris cu "DUP[A] push"
# sa nu picare doar pentru ca documentul are o litera accentuata.
function Normalize {
    param([string]$s)
    if ($null -eq $s) { return '' }
    $s = $s.ToLower()
    $pairs = @(
        @([char]0x0103,'a'), @([char]0x0102,'a'), @([char]0x00E2,'a'), @([char]0x00E3,'a'),
        @([char]0x00C3,'a'), @([char]0x00E4,'a'), @([char]0x00E1,'a'), @([char]0x00C2,'a'),
        @([char]0x00EE,'i'), @([char]0x00C8,'i'), @([char]0x00ED,'i'), @([char]0x00CE,'i'),
        @([char]0x0219,'s'), @([char]0x015F,'s'), @([char]0x015B,'s'),
        @([char]0x021B,'t'), @([char]0x0163,'t'), @([char]0x0162,'t'), @([char]0x00F1,'n')
    )
    foreach ($p in $pairs) { $s = $s.Replace([string]$p[0], $p[1]) }
    return ($s -replace '\s+', ' ')
}

# --- invariantele -----------------------------------------------------------
# Pos  : trebuie sa se potriveasca in TOATE cele patru documente
# Both : daca e setat, TOATE formulatile din lista trebuie sa existe in fiecare
#        document. Asta cere SUBSTANTA, nu o singura mentiune.
# Neg  : CONTRAZICTIE. Un invariant negativ nu e "gasit oriunde" - trebuie sa
#        fie o AFIRMATIE, nu o interdictie. "NU incerca sa treci poarta cu
#        vouch" contine textul interzis, dar spune opusul, si daca l-am numara
#        drept contradictie am sanctiona chiar documentul corect.
$INVARIANTS = @(
  @{ Name = 'main, nu ramuri'
     Pos  = '(nu (creezi|faci) ramuri|ramuri.{0,30}nesolicit|nu.{0,20}creezi.{0,20}ramuri)'
     Both = $null; Neg = $null }

  @{ Name = 'commit autonom, imediat'
     Pos  = '(commit autonom|comit autonom|autonom.{0,30}(comit|commit)|(comit|commit).{0,40}(imediat|automat))'
     Both = $null; Neg = '(intarzi.{0,30}comit|comit.{0,30}(la finalul|la sfarsitul) (taskului|sesiunii))' }

  @{ Name = 'LiveReview DOAR dupa push'
     Pos  = '(dupa push|abia dupa|review.{0,50}(pe ce (tocmai a ajuns|ajuns pe)|pe ce e pe github)|doar dupa push)'
     Both = $null
     Neg  = '(review|livereview|lrc).{0,80}inainte de push|inainte de push.{0,60}(review|livereview|lrc)|review.{0,40}(la comit|pe comit)' }

  @{ Name = 'comitul nu e sub poarta'
     Pos  = '(lrc hooks disable|nu sunt sub nicio poarta|comitul.{0,80}nu e niciodata sub poarta|comitul.{0,50}(treaba mea si trebuie sa fie liber|libert)|niciodata.{0,25}blocat de livereview)'
     Both = $null
     Neg  = '(treci|trece) poarta cu.{0,15}(vouch|skip)' }

  @{ Name = 'push doar cu acord + prag'
     Pos  = '(prag.{0,40}comit|doar cu acordul (lui|meu)|push = cu acordul meu|doar cu acord)'
     Both = @('prag')
     Neg  = '(poti impinge|impinge cand vrei|impinge din initiativa ta|poate impinge singur)' }

  @{ Name = 'doua cai de push'
     Pos  = '(calea 1|doo cai de push|doua cai de push|ambele cai de push)'
     Both = @('calea 1', 'calea 2')
     Neg  = $null }

  @{ Name = 'rate limit nu blocheaza push-ul'
     Pos  = '(rate limit|limita cont|limita de cont|contul free|cont free)'
     Both = $null
     # Raw: fara filtrul de negare. Aici CONTRADICTIA insasi contine "nu"
     # ("rate limit, push-ul esueaza si nu merge"), deci filtrul ar ignora
     # exact afirmatia care contrazice. Negatia se trateaza in regex, cu
     # (?!\s*nu\b) imediat dupa "rate limit" - deci "rate limit NU blocheaza"
     # ramane corect, iar "rate limit, push-ul esueaza" prinde.
     Raw  = $true
     Custom = 'RateLimit'
     Neg  = $null }

  @{ Name = 'verificare prin ls-remote'
     Pos  = '(ls-remote)'
     Both = $null
     Neg  = '(verifici|verific).{0,50}codul de iesire|cod de iesire.{0,40}(e adevarul|spune adevarul)|te bazi pe codul de iesire' }

  @{ Name = 'interfata neatinsa'
     Pos  = '(interfat)'
     Both = $null; Neg = $null }

  @{ Name = 'nu ceri decizii tehnice'
     Pos  = '(nu intrebi nimic|nu te intrebi nimic|decizii tehnice|le iei tu|nu ma intrebi nimic)'
     Both = $null
     Neg  = '(intreb|ceri).{0,50}(numele repo|ce ramura|ce ramuri)' }

  @{ Name = 'peretele de push exista'
     Pos  = '(peretel|push-pending|push-status)'
     Both = $null; Neg = $null }
)

# Contradictia "rate limit blocheaza push-ul" trebuie separata de afirmatia
# corecta "rate limit NU blocheaza push-ul".
#
# Nu se poate face cu (?!\s*nu\b): la esec, motorul de regex RECADE si
# reincearca cu alt despartire a spatiilor, ajungand la "rate limit , nu
# blocheaza" - si potrivirea se produce oricum. Masurat 2026-10-11 pe injectia
# "rate limit, NU blocheaza nimic": prins gresit drept contradictie.
#
# De aceea se rezolva in COD, unde nu exista recadere: se cauta termenul de
# limita, apoi un verb de blocare pana la 120 de caractere dupa, iar intre
# ele trebuie sa NU existe o negatie.
function Test-RateLimit {
    param([string]$Text)
    $term = '(rate limit|limita de cont|limita cont|contul free|cont free)'
    $verb = '(blocheaza|opreste|esueaza|anuleaza|impiedica)'
    # si un cuvant despre push. Fara asta se lovesc afirmatii corecte:
    # "contul free are o limita si la un moment dat se opreste" vorbeste despre
    # CONT care se opreste, nu despre push blocat - masurat 2026-10-11 ca
    # alarma falsa pe autonom/PROMPT.
    $push = '(push|impins|impinge|push-?ul)'
    $opt = [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
    $hits = @()
    foreach ($tm in [regex]::Matches($Text, $term, $opt)) {
        $from = $tm.Index + $tm.Length
        $take = [Math]::Min(120, $Text.Length - $from)
        if ($take -le 0) { continue }
        $after = $Text.Substring($from, $take)
        $vm = [regex]::Match($after, $verb, $opt)
        if (-not $vm.Success) { continue }
        if (-not [regex]::IsMatch($after, $push, $opt)) { continue }  # nu despre push
        $between = $after.Substring(0, $vm.Index)
        if ($between -match '(nu|niciodata|nici)\s') { continue }    # e negatie: corect
        $hits += $tm.Value + ' -> ' + $vm.Value
    }
    return $hits
}
#
# Un invariant negativ nu e "gasit oriunde". Trebuie sa FIE o afirmatie, nu o
# interdictie - si nici o formulare care spune OPUSUL prin alt cuvant.
# Se verifica tot SPANIUL (cei ~130 de caracteri dinainte PLUS textul gasit),
# nu doar ce vine inainte. Altfel doua false pozitive:
#   "Comit inainte sa raportez, NU la sfarsitul taskului"
#       -> contine "comit ... la sfarsitul taskului", dar spune interdictie;
#          negatia e IN SPAN, nu inaintea lui.
#   "reviewul lui livereview NU s-a pierdut, doar s-a mutat DE PE comit"
#       -> contine "review ... pe comit", dar "de pe" e mutare, nu review pe
#          comit; negatia e la ~40 de caractere inainte.
function Test-Afirmatie {
    param([string]$Text, [string]$Pattern)
    $opt = [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
    $hits = @()
    foreach ($m in [regex]::Matches($Text, $Pattern, $opt)) {
        $start = [Math]::Max(0, $m.Index - 130)
        $before = $Text.Substring($start, $m.Index - $start)
        $span = $before + $m.Value
        if ($span -notmatch '(nu|niciodata|nici|interzis|evita|de pe|din comit|s-a mutat|scoasa|scoate)\s') {
            $hits += $m.Value
        }
    }
    return $hits
}

function Test-Set {
    param($Set, [switch]$Quiet)
    $fail = 0; $rows = @()
    foreach ($inv in $INVARIANTS) {
        # --- pozitiv: in toate 4
        $missing = @()
        foreach ($k in $Set.Keys) { if ($Set[$k] -notmatch $inv.Pos) { $missing += $k } }
        if ($missing.Count -gt 0) {
            $fail++; $rows += ('  [ROSU] {0,-32} lipseste din: {1}' -f $inv.Name, ($missing -join ', '))
        } elseif ($inv.Both) {
            # --- substanta: toate formulatile, in fiecare document
            $lackSub = @()
            foreach ($k in $Set.Keys) {
                foreach ($b in $inv.Both) {
                    if ($Set[$k] -notmatch $b) { $lackSub += "$k(<$b>)"; break }
                }
            }
            if ($lackSub.Count -gt 0) {
                $fail++; $rows += ('  [ROSU] {0,-32} substantie incompleta: {1}' -f $inv.Name, ($lackSub -join ', '))
            } else {
                $rows += ('  [VERDE] {0,-32} in toate 4, cu substanta' -f $inv.Name)
            }
        } else {
            $rows += ('  [VERDE] {0,-32} in toate 4' -f $inv.Name)
        }
        # --- negativ: nicio afirmatie contraindicata
        if ($inv.Custom -or $inv.Neg) {
            $present = @()
            foreach ($k in $Set.Keys) {
                $n = 0
                if ($inv.Custom -eq 'RateLimit') {
                    $n = (Test-RateLimit -Text $Set[$k]).Count
                } elseif ($inv.Raw) {
                    $n = @([regex]::Matches($Set[$k], $inv.Neg,
                            [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)).Count
                } else {
                    $n = (Test-Afirmatie -Text $Set[$k] -Pattern $inv.Neg).Count
                }
                if ($n -gt 0) { $present += $k }
            }
            if ($present.Count -gt 0) {
                $fail++; $rows += ('  [ROSU] {0,-32} CONTRAZICIE in: {1}' -f $inv.Name, ($present -join ', '))
            } else {
                $rows += ('  [VERDE] {0,-32} nicio afirmatie contraindicata' -f $inv.Name)
            }
        }
    }
    if (-not $Quiet) { $rows | ForEach-Object { Write-Host $_ } }
    return $fail
}

# --- incarcare --------------------------------------------------------------
$real = @{}
$raw  = @{}
foreach ($d in $DOCS) {
    if (-not (Test-Path $d.P)) { Write-Host "EROARE: lipseste $($d.P)"; exit 2 }
    $t = [System.IO.File]::ReadAllText($d.P, [Text.Encoding]::UTF8)
    $real[$d.N] = Normalize $t
    # BRUT, cu singura exceptie a conventiei de sfarsit de linie (CRLF vs LF).
    # Aceea nu e diferenta de continut - ar da un ROSU fara inteles.
    $raw[$d.N] = ($t -replace "`r`n", "`n")
}

Write-Host ''
Write-Host ('=' * 68)
Write-Host '  CONTROL CONSECENTA - cele patru documente'
Write-Host ('=' * 68)
Write-Host ''

# --- NUCLEUL CANONIC: comparatie OCTET CU OCTET ---------------------------
# Un control bazat pe cuvinte-cheie NU poate prinde o contradictie spusa cu
# alte cuvinte. Masurat 2026-10-11, runda 2: sase contradictii formulate cu
# cuvinte pe care regexurile nu le cautau au trecut toate verde. Asta e o
# limita a metodei, nu o lipsa de cuvinte in lista.
#
# De aici solutia prin CONSTRUCTIE: cele patru documente poarta un bloc
# NUCLEU canonic, IDENTIC OCTET CU OCTET. Cat timp blocul e acelasi, cele
# patru NU SE POT contrazice pe regulile de baza - pentru ca spun aceleasi
# cuvinte, in aceeasi ordine. Drift-ul intr-un singur document devine
# imposibil de ratat, pentru ca se masoara prin hash, nu prin sens.
#
# ATENTIE: comparatorul ruleaza pe text BRUT, nu pe text normalizat. Masurat
# 2026-10-11 (verificator, runda 4): pe text normalizat, "RAMURA = main." si
# "RAMURA = MAIN." dadeau ACELASI hash si controlul raporta verde. O regula
# care accepta orice diferenta de majuscula nu e "octet cu octet".
function Get-Nucleu {
    param([string]$Text)
    # (?i) OBLIGATORIU: textul a fost normalizat la minuscule inainte, iar
    # [regex]::Match este case-SENSITIVE. Fara (?i), nucleul era raportat
    # "lipsa" din toate patru desi era prezent - masurat 2026-10-11.
    $m = [regex]::Match($Text, '(?s)(?i)<!--\s*nucleu-git.*?<!--\s*/nucleu-git\s*-->')
    if (-not $m.Success) { return $null }
    return $m.Value
}
function Get-TextSha {
    param([string]$s)
    $sha = New-Object Security.Cryptography.SHA256Managed
    return [System.BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($s))).Replace('-', '')
}

$failNucleu = 0
$rows = @()

# COMPARATORUL STRICT: text BRUT. Vezi avertismentul de la Get-Nucleu.
$strictHashes = @{}
foreach ($k in $raw.Keys) {
    $nuc = Get-Nucleu -Text $raw[$k]
    if (-not $nuc) {
        $failNucleu++
        $rows += ('  [ROSU] NUCLEU lipseste din: {0}' -f $k)
    } else {
        $h = Get-TextSha $nuc
        $strictHashes[$k] = $h
        $rows += ('  [VERDE] NUCLEU prezent in {0,-22} sha={1}' -f $k, $h.Substring(0, 16))
    }
}
$distinct = @($strictHashes.Values | Sort-Object -Unique)
if ($distinct.Count -gt 1) {
    $failNucleu++
    # se spun EXPLICIT documentele fiecarei variante - un "diferit" fara
    # nume nu poate fi reparat de nimeni.
    $byHash = @{}
    foreach ($k in $strictHashes.Keys) {
        $h = $strictHashes[$k]
        if (-not $byHash.ContainsKey($h)) { $byHash[$h] = @() }
        $byHash[$h] += $k
    }
    $rows += ('  [ROSU] NUCLEU diferit OCTET CU OCTET: {0} variante' -f $distinct.Count)
    foreach ($h in @($byHash.Keys | Sort-Object { -$byHash[$_].Count })) {
        $rows += ('  [ROSU]   sha={0} -> {1}' -f $h.Substring(0, 16), (($byHash[$h] | Sort-Object) -join ', '))
    }
} elseif ($distinct.Count -eq 1) {
    $rows += ('  [VERDE] NUCLEU identic OCTET CU OCTET in toate 4 documente (o singura varianta)')
}
$rows | ForEach-Object { Write-Host $_ }

# runda negativa proprie: drift intr-un singur document trebuie sa cada
#
# INJECTIA TREBUIE SA MODIFICE BLOCUL, NU O PROPOZITIE.
# Masurat 2026-10-11: injectia veche cauta propozitia "push = peste prag, doar
# cu acordul meu." - care nu mai exista, pentru ca NUCLEU a fost rescris cu
# formularea -Acord. -replace pe un sir inexistent NU face nimic, hashul ramanea
# identic, iar runda raporta ESCAPAT. Scriptul avea dreptate ca sa cada, dar
# motivul real era ca jocul nu se dasea deloc: un control care nu injecteaza
# nu testeaza comparatorul de hash.
#
# De aceea, aici:
#   (1) se injecteaza pe MARCAJUL de deschidere -> valabil indiferent de
#       versiunea NUCLEU si de orice formulare a regulilor;
#   (2) se verifica EXPLICIT ca documentul s-a schimbat; daca nu s-a schimbat,
#       se raporteaza defect de control, nu se apeleaza comparatorul;
#   (3) se verifica ca blocul e inca gasit - altfel comparatorul nu e testat.
#   (3) se verifica ca blocul e inca gasit - altfel comparatorul nu e testat;
#   (4) se testeaza DOI feluri de drift: de marcaj si de MAJUSCULA. Al doilea
#       este exact cel care ESCAPA comparatorul vechi, pentru ca .ToLower()
#       face "main" si "MAIN" identice. Daca driftul de majuscula n-ar fi
#       prins, controlul ar fi iarasi decorativ - doar in sens opus: ar
#       declara "octet cu octet" fara sa masoare octetii.
$drift = @{}
foreach ($k in $raw.Keys) { $drift[$k] = $raw[$k] }
$driftTarget = 'autonom/PROMPT'

# (a) drift de marcaj
$d1 = $drift[$driftTarget].Replace('<!-- NUCLEU-GIT', '<!-- NUCLEU-GIT-drift')
$a1 = ($d1 -cne $raw[$driftTarget])
$n1 = Get-Nucleu -Text $d1
$markerCaught = ($a1 -and $n1 -and ((Get-TextSha $n1) -ne $distinct[0]))

# (b) drift de majuscula - o singura litera, tot restul identic
$d2 = $drift[$driftTarget].Replace('RAMURA = main.', 'RAMURA = MAIN.')
$a2 = ($d2 -cne $raw[$driftTarget])
$n2 = Get-Nucleu -Text $d2
$caseCaught = ($a2 -and $n2 -and ((Get-TextSha $n2) -ne $distinct[0]))

# (c) control de sensibilitate: dupa normalizare, "main" si "MAIN" devin
#     ACELASI sir. Daca ar fi altfel - adica daca normalizarea ar distinge
#     driftul - atunci comparatorul vechi ar fi prins oricum, iar (b) nu ar
#     dovedi nimic despre comparatorul strict. Hash-urile EGALE aici inseamna
#     ca comparatorul vechi NU distinge, adica strict e chiar necesar.
$refNuc = Get-Nucleu -Text $raw['autonom/SKILL']
$vechiulNuDistinge = ((Get-TextSha (Normalize $n2)) -eq (Get-TextSha (Normalize $refNuc)))

$driftOk = ($markerCaught -and $caseCaught)
Write-Host ''
if (-not $a1) {
    Write-Host '  [ROSU] runda negativa NUCLEU: injectia (a) NU a modificat documentul - control fara putere'
} elseif ($markerCaught) {
    Write-Host '  runda negativa NUCLEU (a) drift de marcaj  -> ROSU cum trebuie'
} else {
    Write-Host '  [ROSU] runda negativa NUCLEU (a): blocul s-a schimbat, hashul a ramas identic - comparatorul nu masoara'
}
if (-not $a2) {
    Write-Host '  [ROSU] runda negativa NUCLEU: injectia (b) NU a modificat documentul - control fara putere'
} elseif ($caseCaught) {
    Write-Host '  runda negativa NUCLEU (b) drift de majuscula -> ROSU cum trebuie'
} else {
    Write-Host '  [ROSU] runda negativa NUCLEU (b): drift de majuscula ESCAPAT - comparatorul masoara doar sensuri'
}
if ($vechiulNuDistinge) {
    Write-Host '  control de sensibilitate: comparatorul normalizat NU distinge "main" de "MAIN" - (b) e concludent'
} else {
    Write-Host '  [ROSU] control de sensibilitate: comparatorul normalizat DISTINGE driftul de majuscula - (b) nu dovedeste nimic despre comparatorul strict'
    $driftOk = $false
}
if (-not $driftOk) { $failNucleu++ }

Write-Host ''
$failReal = Test-Set -Set $real
Write-Host ''
Write-Host ('DOCUMENTE REALE: {0} invariant' -f $INVARIANTS.Count)
if (($failReal + $failNucleu) -eq 0) { Write-Host 'REZULTAT REAL: VERDE COMPLET' }
else { Write-Host ("REZULTAT REAL: {0} PICAT" -f ($failReal + $failNucleu)) }

# --- CONTROL NEGATIV, INDEPENDENT DE FORMULAREA REGEXURILOR ----------------
# Se goleste PE RAND cate un document, la fiecare runda. Nu se injecta niciun
# sir: un control care strica exact textul cautat de propriile regexuri
# demonstreaza doar ca regexul se potriveste cu propria samanta. Golirea unui
# document intreg nu depinde de nicio formulare si, daca verificarea chiar
# citeste toate cele patru, trebuie sa cada de fiecare data.
Write-Host ''
Write-Host ('-' * 68)
Write-Host '  CONTROL NEGATIV - golire pe rand, independenta de regex'
Write-Host ('-' * 68)

$rounds = 0; $roundsOk = 0
foreach ($k in $real.Keys) {
    $rounds++
    $b = @{}
    foreach ($kk in $real.Keys) { $b[$kk] = $real[$kk] }
    $b[$k] = ''
    $f = Test-Set -Set $b -Quiet
    $verdict = if ($f -ge 6) { 'ROSU cum trebuie' } else { 'PREA PUTERNIC NU E' }
    if ($f -ge 6) { $roundsOk++ }
    Write-Host ('  runda {0}: document golit = {1,-22} -> {2,2} invariant(i) rosii   {3}' -f $rounds, $k, $f, $verdict)
}
Write-Host ''
Write-Host ('  RINZI NEGATIVE CORECTE: {0}/{1}' -f $roundsOk, $rounds)

# --- SUITA DE INJECTIE: partea de CONTRADICTIE, nu cea de prezenta ---------
# Rundele de mai sus golesc documente - ele dovedesc ca verificarea citeste
# toate patru. Dar nu ating partea de contradictie. Suita asta introduce
# afirmatii cu tot intentionat: unele gresite (trebuie prinse) si unele
# corecte (NU trebuie atinse).
#
# O verificare care prinde si afirmatiile corecte e la fel de inutila ca una
# care nu prinde nimic: oamenii o ignora, si atunci nu mai prinde nici
# problema reala. Masurat 2026-10-11 - trei false pozitive reparate aici:
# "NU blocheaza", "s-a mutat de pe comit", "contul se opreste".
Write-Host ''
Write-Host ('-' * 68)
Write-Host '  SUITA DE INJECTIE - gresite trebuie prinse, corecte nu'
Write-Host ('-' * 68)

$SUITE = @(
  @{ T = 'LiveReview ruleaza INAINTE de push, pe range.';                      E = 'PRINS'  },
  @{ T = 'Cand apare rate limit, push-ul esueaza si nu merge.';                 E = 'PRINS'  },
  @{ T = 'Verifici prin codul de iesire al shell-ului.';                        E = 'PRINS'  },
  @{ T = 'Cand blocajul te deranjeaza, treci poarta cu vouch si iti rezolvi treaba.'; E = 'PRINS' },
  @{ T = 'Cand apare rate limit, NU blocheaza nimic, se impinge oricum.';       E = 'SCAPAT' },
  @{ T = 'LiveReview a fost scos de pe comit, review-ul ruleaza pe GitHub.';   E = 'SCAPAT' },
  @{ T = 'Contul free are o limita si la un moment dat se opreste.';           E = 'SCAPAT' }
)

$injOk = 0
foreach ($case in $SUITE) {
    $s = @{}
    foreach ($k in $real.Keys) { $s[$k] = $real[$k] }
    $s['autonom/PROMPT'] = $s['autonom/PROMPT'] + ' ' + $case.T
    $f = Test-Set -Set $s -Quiet
    $got = if ($f -eq 0) { 'SCAPAT' } else { 'PRINS' }
    $mark = if ($got -eq $case.E) { 'OK' } else { 'FALSA' }
    if ($got -eq $case.E) { $injOk++ }
    $short = $case.T
    if ($short.Length -gt 44) { $short = $short.Substring(0, 41) + '...' }
    Write-Host ('  {0,-47} {1,-7} asteptat {2,-7} {3}' -f $short, $got, $case.E, $mark)
}
Write-Host ''
Write-Host ('  INJECTII CORECTE: {0}/{1}' -f $injOk, $SUITE.Count)

Write-Host ''
Write-Host ('=' * 68)
if (($failReal + $failNucleu) -eq 0 -and $roundsOk -eq $rounds -and $rounds -ge 4 -and $injOk -eq $SUITE.Count -and $driftOk) {
    Write-Host '  VERDICT: consecvent, iar controlul are putere.'
    Write-Host ('=' * 68)
    exit 0
}
Write-Host '  VERDICT: INCONSISTENTA sau control fara putere. Vezi liniile ROSU.'
Write-Host ('=' * 68)
exit 1