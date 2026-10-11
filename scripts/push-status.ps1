<#
    push-status.ps1 - PERETELE.

    Popy nu citeste git si nu deschide fisiere. Trebuie sa fie anuntat, tare,
    ca un perete, NU o linie de text care se pierde in scroll.

    Asta afiseaza:
      - un TABEL mare, mereu, la fiecare rulare
      - un balon in tavita, repetat, cat timp comiturile stau neimpinse

    Nu impinge nimic. Nu comita nimic. Doar masoara si striga.

    Iesire: 0 = la zi (serverul e la HEAD)
           1 = sunt comituri neimpinse (peretele e aprins)
           2 = mediu invalid

    ASCII numai, intentionat (PowerShell 5.1 + .ps1 fara BOM = ANSI).
#>

[CmdletBinding()]
param(
    [string] $Remote  = 'origin',
    [string] $Branch  = 'main',
    [string] $Repo    = 'C:\Users\apviz\.minimax-agent\projects',
    [int]    $Prag    = 25,
    [switch] $SilentBalloon
)

$ErrorActionPreference = 'Stop'
$CC = 'C:\Users\apviz\.minimax-agent\projects\90_CONTROL_CENTER'

function Invoke-Git {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$GitArgs)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { $o = & git @GitArgs 2>&1; $c = $LASTEXITCODE }
    finally { $ErrorActionPreference = $prev }
    return [pscustomobject]@{ Out = $o; Code = $c }
}

if (-not (Test-Path $Repo)) { Write-Host "EROARE: repo lipsa: $Repo"; exit 2 }
Set-Location $Repo

$localSha = (Invoke-Git rev-parse HEAD).Out | Select-Object -First 1
if (-not $localSha) { Write-Host 'EROARE: nu e repo git.'; exit 2 }
$branchReal = (Invoke-Git rev-parse --abbrev-ref HEAD).Out | Select-Object -First 1
$srvLine = (Invoke-Git ls-remote $Remote $Branch).Out | Select-Object -First 1
$srvSha  = if ($srvLine) { ($srvLine -split '\s+')[0] } else { 'FARA RAMURA' }

$neimpinse = 0
$c = (Invoke-Git rev-list --count "$Remote/$Branch..HEAD").Out | Select-Object -First 1
if ($c) { $neimpinse = [int]$c }
$dirtyList = @((Invoke-Git status --porcelain).Out | Where-Object { $_ -and $_.Trim() })
$dirty = $dirtyList.Count

$laZi = ($neimpinse -eq 0)
$comituri = @()
if (-not $laZi) {
    $comituri = @((Invoke-Git log --oneline "$Remote/$Branch..HEAD").Out | Where-Object { $_ -and $_.Trim() })
}

# ---------------------------------------------------------------- PERETE
$W = 68
$bar = '=' * $W
$ln  = '-' * $W
Write-Host ''
Write-Host $bar
$t = 'PERETELE PUSH'
if ($laZi) { $t = 'PERETELE PUSH - LA ZI' }
Write-Host ('  ' + $t.PadRight($W - 2))
Write-Host $bar
Write-Host ''
Write-Host ('  {0,-22} {1,-42}' -f 'RAMURA', $branchReal)
Write-Host ('  {0,-22} {1,-42}' -f 'LOCAL', $localSha.Substring(0,12))
Write-Host ('  {0,-22} {1,-42}' -f 'SERVER (adevarul)', $(if ($srvSha.Length -ge 12) { $srvSha.Substring(0,12) } else { $srvSha }))
Write-Host ('  {0,-22} {1,-42}' -f 'COMITURI NEIMPINSE', $neimpinse)
Write-Host ('  {0,-22} {1,-42}' -f 'PRAG PENTRU PUSH', $Prag)
Write-Host ('  {0,-22} {1,-42}' -f 'FISIERE NECOMITATE', $dirty)
Write-Host ''

if ($laZi) {
    Write-Host '  Serverul este la HEAD. Nimic de impins. Nimic de semnalat.'
    Write-Host ''
    Write-Host $bar
    exit 0
}

Write-Host $ln
Write-Host ('  CE NU ESTE INCA PE GITHUB ({0} comituri)' -f $neimpinse)
Write-Host $ln
$shown = 0
foreach ($cm in $comituri) {
    if ($shown -ge 12) {
        $rest = $comituri.Count - 12
        Write-Host ('  ... si inca {0} comituri' -f $rest)
        break
    }
    Write-Host ('    ' + $cm)
    $shown++
}
Write-Host $ln
Write-Host ''
if ($neimpinse -ge $Prag) {
    Write-Host ('  PRAG ATINS ({0}/{1}). Se poate face push.' -f $neimpinse, $Prag)
} else {
    Write-Host ('  Sub prag ({0}/{1}). Se aduna.' -f $neimpinse, $Prag)
}
Write-Host '  PUSH = cu acordul lui Popy. Nici din initiativa agentului.'
Write-Host ''
Write-Host $bar
Write-Host ''

# ---------------------------------------------------------------- BALON
if (-not $SilentBalloon) {
    $titlu = "PUSH NECESAR - $neimpinse comituri neimpinse"
    $mesaj = "Server: $($srvSha.Substring(0,7)) | Local: $($localSha.Substring(0,7)) | Prag: $neimpinse/$Prag. Impinge doar cu acordul lui Popy."
    try {
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing
        $ni = New-Object System.Windows.Forms.NotifyIcon
        $ni.Icon = [System.Drawing.SystemIcons]::Warning
        $ni.Visible = $true
        $ni.BalloonTipTitle = $titlu
        $ni.BalloonTipText = $mesaj
        $ni.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Warning
        $ni.ShowBalloonTip(15000)
        Start-Sleep -Seconds 4
        $ni.Dispose()
        Write-Host '  balon trimis in tavita'
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
        repo        = $Repo
        branch      = $branchReal
        local_sha   = $localSha
        server_sha  = $srvSha
        unpushed    = $neimpinse
        threshold   = $Prag
        dirty       = $dirty
        needs_push  = (-not $laZi)
    }
    $json = $o | ConvertTo-Json
    [System.IO.File]::WriteAllText($f, $json, (New-Object System.Text.UTF8Encoding($false)))
    Write-Host ('  stare scrisa: ' + $f)
} catch {
    Write-Host ('  NU am putut scrie starea: ' + $_.Exception.Message)
}

exit 1