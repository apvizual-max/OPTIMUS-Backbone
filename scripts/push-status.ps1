<#
    push-status.ps1 - PERETELE.

    Popy nu citeste git si nu deschide fisiere. Trebuie sa fie anuntat, tare,
    ca un perete, NU o linie de text care se pierde in scroll.

    Asta afiseaza:
      - un TABEL mare pentru FIECARE repo pe care il manageriez, mereu
      - un singur balon in tavita, care strange toate repo-urile

    De ce mai multe repo-uri: masurat 2026-10-11, trei repo-uri aveau comituri
    neimpinse si peretele se uita la UNUL. Un perete care acopera o treime din
    realitate e un perete mincinos. Cerinta lui Popy spune "cand se aduna
    prea multe comituri locale pe main", nu "in repo-ul X".

    Nu impinge nimic. Nu comita nimic. Doar masoara si striga.

    Iesire: 0 = toate repo-urile la zi (serverul e la HEAD)
           1 = exista comituri neimpinse in cel putin un repo (peretele e aprins)
           2 = mediu invalid

    ASCII numai, intentionat (PowerShell 5.1 + .ps1 fara BOM = ANSI).
#>

[CmdletBinding()]
param(
    [string] $Remote  = 'origin',
    [string] $Branch  = 'main',
    [string] $Prag    = 25,
    [switch] $SilentBalloon,
    # Daca e dat, se uita DOAR la acest repo. Implicit: cele trei pe care le
    # manageriez eu, ca sa nu apara in perete ceva ce nu stiu ce este.
    [string[]] $Repo
)

$ErrorActionPreference = 'Stop'
$CC = 'C:\Users\apviz\.minimax-agent\projects\90_CONTROL_CENTER'

if (-not $Repo -or $Repo.Count -eq 0) {
    $Repo = @(
        'C:\Users\apviz\.minimax-agent\projects',
        'C:\Users\apviz\.minimax-agent\projects\SENTINEL_PRIME',
        'C:\Users\apviz\.minimax-agent\projects\60_SKILLS\_links\mavis-skills'
    )
}

function Invoke-Git {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$GitArgs)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { $o = & git @GitArgs 2>&1; $c = $LASTEXITCODE }
    finally { $ErrorActionPreference = $prev }
    # normalizare explicita: un obiect ErrorRecord NU are .Trim() si arunca
    # MethodNotFoundException. Masurat 2026-10-11 cu git push --dry-run.
    $s = @()
    foreach ($x in @($o)) { $s += [string]$x }
    return [pscustomobject]@{ Out = $s; Code = $c }
}

# ls-remote intoarce "<sha>\t<refs/...>". Daca git a scris ceva pe stderr
# inainte, primul element nu e hash-ul. Se cauta forma exacta a unui SHA.
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
    foreach ($x in @($Lines)) { if (([string]$x).Trim()) { $n++ } }
    return $n
}

# ---------------------------------------------------------------- MASURARE
$masurari = @()
foreach ($r in $Repo) {
    $m = [pscustomobject]@{
        Cale      = $r
        Nume      = (Split-Path $r -Leaf)
        Exista    = (Test-Path $r)
        Ramura    = ''
        LocalSha  = ''
        ServerSha = ''
        Neimpinse = 0
        Dirty     = 0
        Comituri  = @()
        Eroare    = ''
    }
    if (-not $m.Exista) {
        $m.Eroare = 'repo lipsa'
        $masurari += $m
        continue
    }
    Push-Location $r
    try {
        $localSha = (Invoke-Git rev-parse HEAD).Out | Where-Object { $_ -match '^[0-9a-f]{40}' } | Select-Object -First 1
        if (-not $localSha) { $m.Eroare = 'nu e repo git'; $masurari += $m; continue }
        $m.Ramura    = ([string](Invoke-Git rev-parse --abbrev-ref HEAD).Out | Select-Object -First 1).Trim()
        $m.LocalSha  = ([string]$localSha).Trim()
        $srv = Get-LsRemoteSha (Invoke-Git ls-remote $Remote $Branch).Out
        $m.ServerSha = $(if ($srv) { $srv } else { 'FARA RAMURA' })
        $c = (Invoke-Git rev-list --count "$Remote/$Branch..HEAD").Out | Where-Object { $_ -match '^\d+$' } | Select-Object -First 1
        if ($c) { $m.Neimpinse = [int]$c }
        $m.Dirty = Get-DirtyCount (Invoke-Git status --porcelain).Out
        if ($m.Neimpinse -gt 0) {
            $m.Comituri = @((Invoke-Git log --oneline "$Remote/$Branch..HEAD").Out | Where-Object { $_ -and $_.Trim() })
        }
    } catch {
        $m.Eroare = $_.Exception.Message
    } finally {
        Pop-Location
    }
    $masurari += $m
}

$totalNeimpinse = ($masurari | Measure-Object -Property Neimpinse -Sum).Sum
if ($null -eq $totalNeimpinse) { $totalNeimpinse = 0 }
$cuEroare = @($masurari | Where-Object { $_.Eroare }).Count
# Un repo care NU poate fi masurat nu e un repo la zi. Masurat 2026-10-11:
# cu un repo inexistent, totalul era 0, peretele zicea "LA ZI" si iesea cu 0 -
# un senzor mort care raporteaza sanatate. Exact clasa pe care o corectam
# peste tot. Daca o masuratoare picteaza, peretele NU e verde.
$laZi = ($totalNeimpinse -eq 0 -and $cuEroare -eq 0)

# ---------------------------------------------------------------- PERETE
$W = 74
$bar = '=' * $W
$ln  = '-' * $W
Write-Host ''
Write-Host $bar
$t = 'PERETELE PUSH'
if ($laZi) { $t = 'PERETELE PUSH - LA ZI' }
if ($cuEroare -gt 0) { $t = 'PERETELE PUSH - MASURATURA INCOMPLETA' }
Write-Host ('  ' + $t.PadRight($W - 2))
Write-Host $bar

foreach ($m in $masurari) {
    Write-Host ''
    Write-Host ('  REPO: {0}' -f $m.Nume)
    if ($m.Eroare) {
        Write-Host ('    {0,-22} {1}' -f 'STAREA', ('NEREUSITA - ' + $m.Eroare))
        continue
    }
    Write-Host ('    {0,-22} {1}' -f 'RAMURA', $m.Ramura)
    Write-Host ('    {0,-22} {1}' -f 'LOCAL', $m.LocalSha.Substring(0,12))
    Write-Host ('    {0,-22} {1}' -f 'SERVER (adevarul)', $(if ($m.ServerSha.Length -ge 12) { $m.ServerSha.Substring(0,12) } else { $m.ServerSha }))
    Write-Host ('    {0,-22} {1}' -f 'COMITURI NEIMPINSE', $m.Neimpinse)
    Write-Host ('    {0,-22} {1}' -f 'FISIERE NECOMITATE', $m.Dirty)
    if ($m.Neimpinse -gt 0) {
        Write-Host ('    {0,-22} {1}' -f 'STARE', $(if ($m.Neimpinse -ge $Prag) { "PRAG ATINS ($($m.Neimpinse)/$Prag)" } else { "sub prag ($($m.Neimpinse)/$Prag) - se aduna" }))
    }
    if ($m.Comituri.Count -gt 0) {
        Write-Host $ln
        Write-Host ('    CE NU ESTE INCA PE GITHUB - {0} ({1} comituri)' -f $m.Nume, $m.Neimpinse)
        Write-Host $ln
        $shown = 0
        foreach ($cm in $m.Comituri) {
            if ($shown -ge 8) {
                Write-Host ('      ... si inca {0} comituri' -f ($m.Comituri.Count - $shown))
                break
            }
            Write-Host ('      ' + $cm)
            $shown++
        }
        Write-Host $ln
    }
}

Write-Host ''
Write-Host ('  TOTAL COMITURI NEIMPINSE: {0}   PRAG: {1}   REPO-URI: {2}' -f $totalNeimpinse, $Prag, $masurari.Count)
if ($cuEroare -gt 0) {
    Write-Host ('  REPO-URI NEMASURATE: {0} - peretele NU poate spune ca totul e in ordine.' -f $cuEroare)
}
Write-Host '  PUSH = cu acordul lui Popy. Nici din initiativa agentului.'
Write-Host $bar
Write-Host ''

# Mediu invalid: o masuratoare a picat. Exit 2, NU 0 - un perete care nu
# stie ce se intampla nu are voie sa arate verde.
if ($cuEroare -gt 0) { exit 2 }
if ($laZi) { exit 0 }

# ---------------------------------------------------------------- BALON
if (-not $SilentBalloon) {
    $repoNames = @($masurari | Where-Object { $_.Neimpinse -gt 0 } | ForEach-Object { "$($_.Nume):$($_.Neimpinse)" })
    $titlu = "PUSH NECESAR - $totalNeimpinse comituri neimpinse"
    $mesaj = ($repoNames -join ' | ') + ". Impinge doar cu acordul lui Popy."
    # Cat timp balonul e anuntat ca 15 secunde, el trebuie sa TRAIASCA 15
    # secunde. Masurat 2026-10-11: codul dormea 4 secunde si apoi arunca
    # iconul - iar balonul dispare odata cu iconul. Promisiunea era mai lunga
    # decat realitatea, cu 11 secunde.
    $durataBalonMs = 15000
    # ATENTIE la unitati: $durataBalonMs/1000 da SECUNDE. Cum era scris cu
    # -Milliseconds, se dormea 15 ms, iar raportul zicea "balon programat 15s".
    # Masurat 2026-10-11: peretele cu balon s-a terminat in 4 secunde, nu in
    # 15. Exact clasa de minciuna pe care o reparei la fiecare pas - si pe care
    # o lasam sa se strecoare inapoi intr-un colt nou.
    try {
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing

        # Fara desktop interactiv balonul NU ARE CUM sa apara, oricat de bine
        # arata codul de mai jos. Se cere desktopul, nu se presupune.
        if (-not [System.Windows.Forms.SystemInformation]::UserInteractive) {
            Write-Host '  BALOAN NU A MERS: sesiune fara desktop interactiv.'
            Write-Host '  peretele e tot pe ecran, dar balonul nu s-a putut arata'
        } else {
            $ni = New-Object System.Windows.Forms.NotifyIcon
            $ni.Icon = [System.Drawing.SystemIcons]::Warning
            $ni.Visible = $true
            $ni.BalloonTipTitle = $titlu
            $ni.BalloonTipText = $mesaj
            $ni.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Warning
            $ni.ShowBalloonTip($durataBalonMs)
            # ShowBalloonTip trimite ASINCRON: revine imediat, iar balonul
            # traieste cat timp iconul e viu. De aceea se asteapta durata
            # completa inainte de Dispose.
            Start-Sleep -Seconds ([int]($durataBalonMs / 1000))
            $ni.Dispose()
            # Se raporteaza ce s-a MASURAT: desktop interactiv confirmat,
            # apel fara eroare. Nu se pretinde livrare - asta n-o poate
            # confirma niciun apel, pentru ca s-ar vedea sau nu s-ar vedea.
            Write-Host ("  balon programat " + [int]($durataBalonMs / 1000) + "s pe desktop interactiv, fara eroare raportata")
        }
    } catch {
        Write-Host ('  BALOAN NU A MERS: ' + $_.Exception.Message)
        Write-Host '  peretele e tot pe ecran, dar balonul nu s-a aratat'
    }
}

# ---------------------------------------------------------------- FISIER
# Supravietuieste restartului de sesiune: daca nu mai suntem aici, peretele ramane.
try {
    if (-not (Test-Path $CC)) { New-Item -ItemType Directory -Path $CC -Force | Out-Null }
    $f = Join-Path $CC 'api\push-pending.json'
    $o = [pscustomobject]@{
        measured_at = (Get-Date).ToString('o')
        branch      = $Branch
        threshold   = $Prag
        total_unpushed = $totalNeimpinse
        needs_push  = (-not $laZi)
        # Fiecare repo cu numele lui, nu doar o cale - altfel peretele scris
        # era la fel de greu de citit cum era inainte.
        repos = @($masurari | ForEach-Object {
            [pscustomobject]@{
                name     = $_.Nume
                path     = $_.Cale
                branch   = $_.Ramura
                local    = $_.LocalSha
                server   = $_.ServerSha
                unpushed = $_.Neimpinse
                dirty    = $_.Dirty
                error    = $_.Eroare
            }
        })
    }
    $json = $o | ConvertTo-Json -Depth 5
    [System.IO.File]::WriteAllText($f, $json, (New-Object System.Text.UTF8Encoding($false)))
    Write-Host ('  stare scrisa: ' + $f)
} catch {
    Write-Host ('  NU am putut scrie starea: ' + $_.Exception.Message)
}

exit 1