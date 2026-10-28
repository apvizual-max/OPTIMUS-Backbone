# queue-deliver.ps1
# DELIVERY of the secondary channel (GitHub) into the Cloud's OWN repo.
#
# THE DEFECT THIS SCRIPT EXISTS TO FIX
#
# MEASURED 2026-10-27: the publisher wrote the secondary channel into the CI
# repo (MAVIS-OPTIMUS-CI). The Cloud, by its own contract - read live from
# its disk, .skills/mavis-cloud-to-local-reporting/SKILL.md - does
# `git pull --rebase origin main` in ITS OWN repo (MAVIS-CLOUD) and reads
# QUEUE/TASKS-FOR-CLOUD.md from THERE. So the tickets sat in a repository the
# Cloud never reads: 2 tickets in the CI queue, 0 in the Cloud's queue.
#
# The gate passed, because it validated the FORMAT of the queue and never
# asked whether the queue REACHED THE CONSUMER. A queue can be perfectly
# formed and perfectly absent. This script is the delivery; the gate checks
# the delivery.
#
# The delivery is append-only: tickets are ADDED to the Cloud's queue, never
# rewritten, never deleted. The Cloud marks what it consumed with [x], and
# that marking survives, because this script never rewrites a line it did
# not write.
#
# Usage:
#   powershell -NoProfile -File queue-deliver.ps1 -Status
#   powershell -NoProfile -File queue-deliver.ps1 -Deliver
#   powershell -NoProfile -File queue-deliver.ps1 -Deliver -Push
#
# Exit codes (the script's OWN, never inherited):
#   0 = measured and true: every local ticket is present in the Cloud's
#       repository, at the tip of the remote branch
#   1 = measured problem: N local tickets are NOT in the Cloud's queue
#   2 = not measurable / refused: a required input is missing, the remote
#       cannot be read, the body is truncated, or the secret scanner blocked
#       the commit. NOTHING was published
#   4 = written but NOT published: no -Push was given, or the push ran and
#       the remote still does not show the tickets. UNKNOWN, reported as such
#   5 = the push was REFUSED by the remote. Nothing was published. The
#       reason git gave is printed
#
# What it will NEVER do: force push, `git reset --hard`, `git clean`,
# rebase, delete anything, or bypass the secret scanner.
#
# ASCII ONLY: executed by Windows PowerShell 5.1.

param(
    [string]$Root = '',
    [string]$CloudRoot = '',
    [string]$QueueFile = '',
    [string]$Remote = 'origin',
    [string]$Branch = 'main',
    [string]$ScriptsDir = '',
    [switch]$Status,
    [switch]$Deliver,
    [switch]$Push
)

$ErrorActionPreference = 'Stop'

# A terminating error must not leave a verdict-shaped exit code behind.
# Exit 2 means "not measurable / refused"; it is the only honest code for
# a script that stopped early. Measured 2026-10-27: a ticket with an empty
# body crashed the script and it exited 1 - the same code the Status mode
# uses for "tickets are missing". A crash and a verdict must never look
# the same.
trap {
    Write-Err ('ERROR=executia s-a oprit: ' + $_.Exception.Message)
    if ($_.InvocationInfo) { Write-Err ('LINIE: ' + $_.InvocationInfo.Line.Trim()) }
    exit 2
}

$Lib = Join-Path $PSScriptRoot 'queue-lib.ps1'
if (-not (Test-Path -LiteralPath $Lib)) {
    [Console]::Error.WriteLine('ERROR=lipseste scripts\queue-lib.ps1: ' + $Lib)
    exit 2
}
. $Lib

if (-not $Root) { $Root = Split-Path -Parent $PSScriptRoot }
if (-not $QueueFile) { $QueueFile = Join-Path $Root 'QUEUE\TASKS-FOR-CLOUD.md' }
if (-not $CloudRoot) { $CloudRoot = Join-Path $Root 'cloud-ingest\MAVIS-CLOUD' }
if (-not $ScriptsDir) { $ScriptsDir = $PSScriptRoot }

$CloudQueueRel = 'QUEUE/TASKS-FOR-CLOUD.md'
$CloudQueueFile = Join-Path $CloudRoot 'QUEUE\TASKS-FOR-CLOUD.md'

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [string]$WorkingDirectory = ''
    )
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    if ($WorkingDirectory) {
        $out = & git -C $WorkingDirectory @Arguments 2>&1
    } else {
        $out = & git @Arguments 2>&1
    }
    $code = $LASTEXITCODE
    $ErrorActionPreference = $prev
    $text = ''
    # NOT Out-String: it wraps long lines at the console width. Wrapped
    # output is a corrupted reading.
    if ($out) { $text = ([string]::Join("`n", @($out))) }
    return [pscustomobject]@{ Code = $code; Text = $text }
}

# Read a file and report whether it starts with a UTF-8 BOM. Writing a file
# back must preserve what was there: a BOM dropped by a rewrite is a silent
# change to a file someone else owns.
function Read-FileText {
    param([Parameter(Mandatory = $true)][string]$Path)
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    $hasBom = $false
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        $hasBom = $true
    }
    return @{ HasBom = $hasBom; Text = [System.IO.File]::ReadAllText($Path) }
}

function Write-TextFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Text,
        [bool]$WithBom = $false
    )
    $enc = New-Object System.Text.UTF8Encoding($WithBom)
    [System.IO.File]::WriteAllText($Path, $Text, $enc)
}

# --- preconditions --------------------------------------------------------
if (-not (Test-Path -LiteralPath $QueueFile)) {
    Write-Err ('ERROR=lipseste coada locala: ' + $QueueFile)
    exit 2
}
if (-not (Test-Path -LiteralPath (Join-Path $CloudRoot '.git'))) {
    Write-Err ('ERROR=lipseste clona Cloud-ului (nu e repo git): ' + $CloudRoot)
    exit 2
}

$local = Read-FileText -Path $QueueFile
$localText = $local.Text

$live = Get-CloudQueueLive -CloudRoot $CloudRoot -Remote $Remote -Branch $Branch
Write-Out ('CLOUD_QUEUE_SOURCE=' + $live.Source)
Write-Out ('CLOUD_QUEUE_DEFINITIVE=' + $live.Definitive)

$known = @()
if ($live.Text) { $known = @(Get-ContractFields -Text $live.Text) }
if ($known.Count -eq 0) {
    $snapshot = Join-Path $Root 'docs\CONTRACT-CLOUD-QUEUE.md'
    if (Test-Path -LiteralPath $snapshot) {
        $known = @(Get-ContractFields -Text ([System.IO.File]::ReadAllText($snapshot)))
    }
}
if ($known.Count -eq 0) { $known = @('cerut de', 'data', 'scope', 'ce trebuie', 'livrare') }

$tickets = @(Get-QueueTickets -Text $localText -Known $known)
$remoteText = ''
if ($live.Text) { $remoteText = $live.Text }

# --- STATUS: measure only, read only --------------------------------------
if (-not $Deliver) {
    $missing = New-Object System.Collections.Generic.List[object]
    foreach ($t in $tickets) {
        if (-not $t.Id) { continue }
        if ($remoteText -notmatch [regex]::Escape($t.Id)) { $missing.Add($t) }
    }
    Write-Out ('LOCAL_TICKETS=' + $tickets.Count)
    Write-Out ('DELIVERED=' + ($tickets.Count - $missing.Count))
    Write-Out ('MISSING=' + $missing.Count)
    if ($missing.Count -gt 0) {
        $ids = New-Object System.Collections.Generic.List[string]
        foreach ($m in $missing) { $ids.Add($m.Id) }
        Write-Out ('MISSING_IDS=' + ($ids -join '|'))
        Write-Out 'MASURAT: tichete in coada locala care NU sunt in coada repo-ului Cloud-ului.'
        exit 1
    }
    if (-not $live.Definitive) {
        Write-Out 'UNKNOWN: sursa cozii Cloud-ului poate fi veche; nu se poate afirma ca tichetele sunt livrate.'
        exit 2
    }
    Write-Out 'Toate tichetele locale sunt prezente in coada repo-ului Cloud-ului.'
    exit 0
}

if (-not $live.Definitive) {
    Write-Err 'ERROR=nu pot livra: sursa cozii Cloud-ului nu este masurabila (remote inaccesibil).'
    exit 2
}

# --- 1. sync the working copy with the remote tip -------------------------
# Nothing is ever rewritten: a fast-forward when the clone has nothing of
# its own, a merge that keeps BOTH histories when it has.
$counts = Invoke-Git -Arguments @('rev-list', '--left-right', '--count', ($Remote + '/' + $Branch + '...HEAD')) -WorkingDirectory $CloudRoot
$behind = 0
$ahead = 0
if ($counts.Code -eq 0) {
    $parts = ($counts.Text.Trim() -split '\s+')
    if ($parts.Count -ge 2) {
        $behind = [int]$parts[0]
        $ahead = [int]$parts[1]
    }
}
Write-Out ('SYNC_BEHIND=' + $behind + ' SYNC_AHEAD=' + $ahead)

if ($behind -gt 0) {
    if ($ahead -eq 0) {
        $ff = Invoke-Git -Arguments @('merge', '--ff-only', ($Remote + '/' + $Branch)) -WorkingDirectory $CloudRoot
        if ($ff.Code -ne 0) {
            Write-Err ('ERROR=nu pot sincroniza clona Cloud-ului cu remote-ul: ' + $ff.Text.Trim())
            exit 2
        }
        Write-Out 'SYNC=ff-only - clona Cloud-ului a fost adusa la varful remote-ului, nimic rescris.'
    } else {
        $mg = Invoke-Git -Arguments @('merge', '--no-ff', ($Remote + '/' + $Branch), '-m', 'merge: sync with remote before delivery') -WorkingDirectory $CloudRoot
        if ($mg.Code -ne 0) {
            Write-Err ('ERROR=conflict la sincronizarea clonei Cloud-ului: ' + $mg.Text.Trim())
            exit 2
        }
        Write-Out 'SYNC=merge --no-ff - ambele istorice pastrate.'
    }
}

# --- 2. what still has to travel -----------------------------------------
# Two different questions, and the difference is the defect that put two
# copies of the same ticket in the Cloud's queue:
#   toAppend - not in the WORKING COPY: the bytes have to be written
#   toPush   - not on the REMOTE: the bytes have to be published
# A delivery that was committed but not pushed is already written; it only
# has to be pushed. Appending it again would duplicate the ticket.
$workText = ''
if (Test-Path -LiteralPath $CloudQueueFile) {
    $workText = [System.IO.File]::ReadAllText($CloudQueueFile)
}
$toAppend = New-Object System.Collections.Generic.List[object]
$toPush = New-Object System.Collections.Generic.List[object]
foreach ($t in $tickets) {
    if (-not $t.Id) { continue }
    if ($workText -notmatch [regex]::Escape($t.Id)) { $toAppend.Add($t) }
    if ($remoteText -notmatch [regex]::Escape($t.Id)) { $toPush.Add($t) }
}
Write-Out ('TO_APPEND=' + $toAppend.Count + ' TO_PUSH=' + $toPush.Count)

if ($toAppend.Count -eq 0 -and $toPush.Count -eq 0) {
    Write-Out 'DELIVERED=0 - nimic de livrat: toate tichetele locale sunt deja in coada Cloud-ului.'
    exit 0
}

# --- 3. build the blocks, in the CONSUMER's contract ----------------------
$nl = "`n"
if ($local.Text -match "`r`n") { $nl = "`r`n" }

$blocks = New-Object System.Collections.Generic.List[string]
foreach ($t in $toAppend) {
    $ceTrebuie = Get-TicketField -Ticket $t -Name 'ce trebuie'
    $detalii = Get-TicketField -Ticket $t -Name 'detalii'
    $livrare = Get-TicketField -Ticket $t -Name 'livrare'
    $scope = Get-TicketField -Ticket $t -Name 'scope'
    $data = Get-TicketField -Ticket $t -Name 'data'
    if (-not $scope) { $scope = 'cloud' }
    if (-not $data) { $data = (Get-Date).ToString('yyyy-MM-dd') }
    if (-not $livrare) { $livrare = 'QUEUE/DONE/' + $t.Id + '.md' }

    # A field declared twice is not a field with a long value; it is two
    # fields, and the parser merges them silently into a value made of
    # both. The merge is invisible, so the count is the witness.
    $contractNames = @('cerut de', 'data', 'scope', 'ce trebuie', 'livrare', 'detalii')
    foreach ($fn in $contractNames) {
        $fk = $fn.ToLower()
        if ($t.Counts.Contains($fk) -and [int]$t.Counts[$fk] -gt 1) {
            Write-Err ('ERROR=refuzat: ticheta ' + $t.Id + ' declara campul "' + $fn + '" de ' + $t.Counts[$fk] + ' ori. Livrarea ar strica contractul.')
            exit 2
        }
    }

    $body = $ceTrebuie.Trim()
    if ($detalii.Trim()) { $body = $body + $nl + $nl + $detalii.Trim() }

    if (-not $body.Trim()) {
        Write-Err ('ERROR=refuzat: ticheta ' + $t.Id + ' nu are instructiune (corpul e gol). O instructiune trunchiata nu e o instructiune.')
        exit 2
    }
    if (-not (Test-ValueComplete -Value $body)) {
        Write-Err ('ERROR=refuzat: corpul tichetei ' + $t.Id + ' se termina la mijlocul propozitiei. O instructiune trunchiata nu e o instructiune.')
        exit 2
    }

    $bodyLines = @($body -split "`r?`n")
    for ($i = 1; $i -lt $bodyLines.Count; $i++) {
        $line = $bodyLines[$i]
        if ($line -match '^###\s*\[') {
            Write-Err ('ERROR=refuzat: linia ' + ($i + 1) + ' a corpului ' + $t.Id + ' ar deschide o ticheta noua in coada Cloud-ului.')
            exit 2
        }
        if ($line -match '^\s*(cerut de|data|scope|ce trebuie|livrare|detalii)\s*:') {
            Write-Err ('ERROR=refuzat: linia ' + ($i + 1) + ' a corpului ' + $t.Id + ' redeclara un camp al contractului si ar strica ticheta livrata.')
            exit 2
        }
    }

    $block = @(
        ('### [' + $t.Id + '] ' + $t.Title),
        ('cerut de: local | data: ' + $data),
        ('scope: ' + $scope),
        ('ce trebuie: ' + $body),
        ('livrare: ' + $livrare)
    ) -join $nl

    # ROUND TRIP. The block is read back with the SAME parser the consumer
    # uses, and it must come back as exactly the ticket that was intended.
    # A block that parses into two tickets, or into a ticket with another
    # delivery target, is refused. This replaces "it looks right": it is
    # the consumer's own reading of the bytes.
    $parsed = @(Get-QueueTickets -Text $block -Known $known)
    if ($parsed.Count -ne 1) {
        Write-Err ('ERROR=refuzat: blocul livrat ar fi citit ca ' + $parsed.Count + ' tichete, nu una.')
        exit 2
    }
    $rt = $parsed[0]
    if ($rt.Id -ne $t.Id) {
        Write-Err ('ERROR=refuzat: idul blocului livrat (' + $rt.Id + ') difera de cel intentionat (' + $t.Id + ').')
        exit 2
    }
    if ((Normalize-BlockText -Text (Get-TicketField -Ticket $rt -Name 'livrare')) -ne (Normalize-BlockText -Text $livrare)) {
        Write-Err ('ERROR=refuzat: tinta de livrare se schimba la citire: "' + (Get-TicketField -Ticket $rt -Name 'livrare') + '".')
        exit 2
    }
    if ((Normalize-BlockText -Text (Get-TicketField -Ticket $rt -Name 'scope')) -ne (Normalize-BlockText -Text $scope)) {
        Write-Err ('ERROR=refuzat: scopul se schimba la citire la ticheta ' + $t.Id + '.')
        exit 2
    }
    if ((Normalize-BlockText -Text (Get-TicketField -Ticket $rt -Name 'ce trebuie')) -ne (Normalize-BlockText -Text $body)) {
        Write-Err ('ERROR=refuzat: instructiunea se schimba la citire la ticheta ' + $t.Id + '.')
        exit 2
    }

    $blocks.Add($block)
}

# --- 4. write the bytes ----------------------------------------------------
$stateDir = Join-Path $Root 'state\tmp\queue-deliver'
if (-not (Test-Path -LiteralPath $stateDir)) {
    New-Item -ItemType Directory -Path $stateDir -Force | Out-Null
}

$scanner = Join-Path $ScriptsDir 'scan-staged-secrets.ps1'
if (-not (Test-Path -LiteralPath $scanner)) {
    Write-Err ('ERROR=lipseste scannerul de secrete: ' + $scanner)
    exit 2
}

if ($blocks.Count -gt 0) {
    $append = New-Object System.Collections.Generic.List[string]
    $append.Add('')
    $append.Add('---')
    $append.Add('')
    $append.Add('## Tichete livrate de Local (CI) - ' + (Get-Date).ToString('yyyy-MM-dd'))
    $append.Add('')
    foreach ($b in $blocks) {
        $append.Add($b)
        $append.Add('')
    }
    $appendText = ($append -join $nl)

    $candidate = Join-Path $stateDir 'candidate-queue.md'
    $cloudRaw = Read-FileText -Path $CloudQueueFile
    $newText = $cloudRaw.Text.TrimEnd("`r", "`n") + $nl + $appendText
    Write-TextFile -Path $candidate -Text $newText -WithBom $cloudRaw.HasBom

    # The secret scanner runs BEFORE the Cloud's repository is touched. A
    # secret is blocked before it exists.
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $scanOut = & powershell -NoProfile -File $scanner -ProbeFile $candidate 2>&1
    $scanCode = $LASTEXITCODE
    $ErrorActionPreference = $prev
    Write-Out ('SECRET_SCAN_EXIT=' + $scanCode)
    if ($scanCode -ne 0) {
        Write-Err 'ERROR=blocat de scannerul de secrete. Nimic nu a fost scris in repo-ul Cloud-ului.'
        if ($scanOut) { Write-Err ([string]::Join("`n", @($scanOut))) }
        exit 2
    }

    Write-TextFile -Path $CloudQueueFile -Text $newText -WithBom $cloudRaw.HasBom
}

# Stage the queue file whatever it holds now. A run that was BLOCKED after
# writing (by the secret scanner, for instance) leaves the content in the
# working tree and in the index, uncommitted. Re-running the delivery must
# finish that job, not report "nothing to deliver" while the content sits
# unpublished.
$add = Invoke-Git -Arguments @('add', '--', $CloudQueueRel) -WorkingDirectory $CloudRoot
if ($add.Code -ne 0) {
    Write-Err ('ERROR=git add a esuat: ' + $add.Text.Trim())
    exit 2
}

# The authoritative scan: what THIS change adds to the Cloud's index.
# The index-wide scan reports pre-existing documentation that lists example
# tokens, and those are already published; blocking a delivery because of
# them is a false accusation.
$prev = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
$scanOut2 = & powershell -NoProfile -File $scanner -StagedDiff -RepoPath $CloudRoot 2>&1
$scanCode2 = $LASTEXITCODE
$ErrorActionPreference = $prev
Write-Out ('SECRET_SCAN_DIFF_EXIT=' + $scanCode2)
if ($scanCode2 -ne 0) {
    Write-Err 'ERROR=blocat de scannerul de secrete pe dif. Nimic nu a fost comitat.'
    if ($scanOut2) { Write-Err ([string]::Join("`n", @($scanOut2))) }
    exit 2
}

# Is there anything to commit for this path?
$diffCheck = Invoke-Git -Arguments @('diff', '--cached', '--quiet', '--', $CloudQueueRel) -WorkingDirectory $CloudRoot
if ($diffCheck.Code -eq 0) {
    Write-Out 'COMMIT=skip - coada nu are nimic nou in index.'
} elseif ($diffCheck.Code -eq 1) {
    # The message goes through a file: no BOM, no shell quoting accident.
    $ids = New-Object System.Collections.Generic.List[string]
    foreach ($t in $toPush) { $ids.Add($t.Id) }
    $msgFile = Join-Path $stateDir 'commit-msg.txt'
    $ticketWord = 'tickets'
    if ($ids.Count -eq 1) { $ticketWord = 'ticket' }
    $msg = @(
        ('local: deliver queue to MAVIS-CLOUD (' + $ids.Count + ' ' + $ticketWord + ')'),
        '',
        ('TASK_IDs: ' + ($ids -join ', ')),
        'Livrate de Local (CI) in coada consumatorului, in contractul lui Cloud.'
    ) -join $nl
    Write-TextFile -Path $msgFile -Text $msg -WithBom $false

    $commit = Invoke-Git -Arguments @('commit', '-F', $msgFile, '--', $CloudQueueRel) -WorkingDirectory $CloudRoot
    if ($commit.Code -ne 0) {
        Write-Err ('ERROR=commit a esuat: ' + $commit.Text.Trim())
        exit 2
    }
    $newSha = (Invoke-Git -Arguments @('rev-parse', 'HEAD') -WorkingDirectory $CloudRoot).Text.Trim()
    Write-Out ('COMMIT=' + $newSha)
} else {
    Write-Err 'ERROR=nu pot citi diferenta din index.'
    exit 2
}

# --- 5. push --------------------------------------------------------------
if (-not $Push) {
    Write-Out 'PUBLISHED=no - fara -Push. Cloud-ul nu vede inca tichetele.'
    Write-Out 'VERDICT=UNKNOWN - nimic nu a fost publicat in repo-ul Cloud-ului.'
    exit 4
}

# The remote is the judge. The push is verified against the remote, never
# against the exit code of git.
$pushResult = Invoke-Git -Arguments @('push', $Remote, ('HEAD:refs/heads/' + $Branch)) -WorkingDirectory $CloudRoot
Write-Out ('PUSH_EXIT=' + $pushResult.Code)
if ($pushResult.Code -ne 0) {
    Write-Err ('ERROR=push refuzat. Nimic nu a fost publicat: ' + $pushResult.Text.Trim())
    exit 5
}

# --- 6. verify against the remote, twice ----------------------------------
$remoteLine = Invoke-Git -Arguments @('ls-remote', $Remote, ('refs/heads/' + $Branch)) -WorkingDirectory $CloudRoot
$remoteSha = ''
if ($remoteLine.Code -eq 0) {
    $parts = ($remoteLine.Text.Trim() -split '\s+')
    if ($parts.Count -ge 1) { $remoteSha = $parts[0] }
}
$localSha = (Invoke-Git -Arguments @('rev-parse', 'HEAD') -WorkingDirectory $CloudRoot).Text.Trim()
Write-Out ('REMOTE_HEAD=' + $remoteSha)
Write-Out ('LOCAL_HEAD=' + $localSha)

[void](Invoke-Git -Arguments @('fetch', $Remote, $Branch) -WorkingDirectory $CloudRoot)
$remoteQueue = Get-GitBlob -RepoRoot $CloudRoot -Spec ($Remote + '/' + $Branch + ':' + $CloudQueueRel)
if ($null -eq $remoteQueue) { $remoteQueue = '' }

$absent = New-Object System.Collections.Generic.List[string]
foreach ($t in $toPush) {
    if ($remoteQueue -notmatch [regex]::Escape($t.Id)) { $absent.Add($t.Id) }
}

if ($remoteSha -ne $localSha) {
    Write-Err 'ERROR=pushul a reusit, dar remote-ul nu arata HEAD-ul local. UNKNOWN, nu succes.'
    exit 4
}
if ($absent.Count -gt 0) {
    Write-Err ('ERROR=pushul a reusit, dar tichetele nu sunt in coada remote-ului: ' + ($absent -join ', '))
    exit 4
}

$deliveredIds = New-Object System.Collections.Generic.List[string]
foreach ($t in $toPush) { $deliveredIds.Add($t.Id) }
Write-Out ('DELIVERED_IDS=' + ($deliveredIds -join '|'))
Write-Out 'VERDICT=OK - tichetele sunt in coada repo-ului Cloud-ului, la varful ramurii remote.'
exit 0
