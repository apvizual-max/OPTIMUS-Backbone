# queue-lib.ps1
# Shared functions for the Local<->Cloud queue.
#
# Why this file exists
# A defect that lives in two places is one defect with two addresses. The
# queue parser was needed by two scripts (the gate that validates the queue
# and the publisher that delivers it). Written twice, the two copies drift,
# and a ticket that one of them calls valid is invisible to the Cloud.
# So the parser lives here once, and both scripts dot-source it.
#
# ASCII ONLY: executed by Windows PowerShell 5.1.

# The five fields the Cloud's contract declares, plus the CI's own note field.
# The list is a FALLBACK: the real contract is read live from the Cloud's
# own file (see Get-ContractFields). It is used only when the live contract
# cannot be read, and in that case the caller reports UNKNOWN.
$script:QueueStandardFields = @('cerut de', 'data', 'scope', 'ce trebuie', 'livrare')

function Write-Out {
    param([AllowEmptyString()][string]$Message)
    [Console]::Out.WriteLine($Message)
}

function Write-Err {
    param([AllowEmptyString()][string]$Message)
    [Console]::Error.WriteLine($Message)
}

# Extract the contract field names from a queue file, by reading the fenced
# block under the "## Format" heading. The fields are declared in the
# Cloud's own file, so this is a measurement, not a constant: if Cloud
# renames a field, the extraction follows.
function Get-ContractFields {
    param([Parameter(Mandatory = $true)][string]$Text)
    $lines = $Text -split "`r?`n"
    $inFormat = $false
    $inFence = $false
    $block = New-Object System.Collections.Generic.List[string]
    foreach ($line in $lines) {
        if ($line -match '^#{2,3}\s*Format\b') { $inFormat = $true; continue }
        if ($inFormat -and $line -match '^##\s') { $inFormat = $false }
        if (-not $inFormat) { continue }
        if ($line -match '^\s*```') {
            if ($inFence) { break }
            $inFence = $true
            continue
        }
        if ($inFence) { $block.Add($line) }
    }
    if ($block.Count -eq 0) { return @() }
    $text = ($block -join "`n")
    $names = New-Object System.Collections.Generic.List[string]
    # A field may be declared at the start of a line or after a pipe:
    # "cerut de: local | data: YYYY-MM-DD" declares TWO fields.
    foreach ($m in [regex]::Matches($text, '(?m)(?:^|\|)\s*([a-z][a-z ]{1,14})\s*:')) {
        $n = $m.Groups[1].Value.Trim()
        if ($names -notcontains $n) { $names.Add($n) }
    }
    return $names.ToArray()
}

# A value is complete when its last visible character closes a thought.
# "Nu intai" is not complete; "si cum il accesezi." is.
function Test-ValueComplete {
    # AllowEmptyString: an empty value is a real state (a ticket with no
    # instruction at all) and must be REPORTED as incomplete, not crash the
    # caller with a binding error. A crash is not a verdict.
    param([AllowEmptyString()][string]$Value)
    $v = $Value.Trim()
    if (-not $v) { return $false }
    $lines = @($v -split "`r?`n" | Where-Object { $_.Trim() })
    if ($lines.Count -eq 0) { return $false }
    $last = $lines[$lines.Count - 1].TrimEnd()
    if ($last -match '^\s*[-*+]\s+(.*)$') { $last = $Matches[1].TrimEnd() }
    elseif ($last -match '^\s*\d+\.\s+(.*)$') { $last = $Matches[1].TrimEnd() }
    if (-not $last) { return $false }
    $c = $last[$last.Length - 1]
    $ok = ($c -eq '.' -or $c -eq '!' -or $c -eq '?' -or $c -eq [char]0x2026 -or
           $c -eq ')' -or $c -eq ']' -or $c -eq '}' -or $c -eq '"' -or
           $c -eq [char]0x201D -or $c -eq '`' -or $c -eq ':')
    return $ok
}

# Split one ticket line into field declarations. A line may declare more
# than one field ("cerut de: local | data: 2026-10-27"), and a value may
# itself contain a pipe. Only a KNOWN field name starts a new field;
# anything else is a continuation of the previous one.
function Split-FieldLine {
    param(
        [Parameter(Mandatory = $true)][string]$Line,
        [Parameter(Mandatory = $true)][string[]]$Known
    )
    $out = New-Object System.Collections.Generic.List[object]
    $parts = @($Line -split '\s\|\s')
    foreach ($part in $parts) {
        $m = [regex]::Match($part, '^\s*([a-z][a-z ]{1,14})\s*:\s*(.*)$')
        $isField = $false
        $name = ''
        if ($m.Success) {
            $name = $m.Groups[1].Value.Trim()
            $lower = $name.ToLower()
            foreach ($k in $Known) { if ($k.ToLower() -eq $lower) { $isField = $true } }
        }
        if ($isField) {
            $out.Add(@{ Name = $name; Value = $m.Groups[2].Value.Trim() })
        } elseif ($out.Count -gt 0) {
            $out[$out.Count - 1].Value = $out[$out.Count - 1].Value + "`n" + $part.Trim()
        }
    }
    return $out.ToArray()
}

# Parse a queue file into tickets.
#
# Returns an array of objects:
#   Id      - the ticket id, without brackets
#   Title   - the ticket title
#   Fields  - ordered dictionary: field name (lowercase) -> value
#   Lines   - the raw lines of the ticket body (excluding the header line)
function Get-QueueTickets {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [string[]]$Known = @()
    )
    if (-not $Known -or $Known.Count -eq 0) { $Known = $script:QueueStandardFields }
    $known = @($Known) + @('detalii')

    $lines = $Text -split "`r?`n"
    $tickets = New-Object System.Collections.Generic.List[object]
    $current = $null

    foreach ($line in $lines) {
        if ($line -match '^###\s*\[([^\]]*)\]\s*(.*)$') {
            if ($null -ne $current) { $tickets.Add($current) }
            $current = [PSCustomObject]@{
                Id     = $Matches[1]
                Title  = $Matches[2]
                Fields = (New-Object System.Collections.Specialized.OrderedDictionary)
                Counts = (New-Object System.Collections.Specialized.OrderedDictionary)
                Lines  = (New-Object System.Collections.Generic.List[string])
            }
            continue
        }
        if ($null -ne $current) { $current.Lines.Add($line) }
    }
    if ($null -ne $current) { $tickets.Add($current) }

    foreach ($t in $tickets) {
        $lastName = ''
        foreach ($line in $t.Lines.ToArray()) {
            if (-not $line.Trim()) { continue }
            $decls = @(Split-FieldLine -Line $line -Known $known)
            if ($decls.Count -eq 0) {
                if ($lastName) {
                    $t.Fields[$lastName] = $t.Fields[$lastName] + "`n" + $line.Trim()
                }
                continue
            }
            foreach ($d in $decls) {
                $key = $d.Name.ToLower()
                if (-not $t.Fields.Contains($key)) {
                    # The indexer setter on an OrderedDictionary ADDS the key,
                    # so using it here and then Add() again throws "Item has
                    # already been added". One way to add, or none.
                    [void]$t.Fields.Add($key, '')
                }
                if (-not $t.Counts.Contains($key)) {
                    [void]$t.Counts.Add($key, 0)
                }
                # How many TIMES the field was declared. A ticket that
                # declares "livrare" twice does not carry one delivery
                # target; it carries two, and the parser merges them into a
                # path made of both. The merge is silent, so the count is
                # the only witness.
                $t.Counts[$key] = [int]$t.Counts[$key] + 1
                if ($d.Value) { $t.Fields[$key] = $t.Fields[$key] + $d.Value }
                $lastName = $key
            }
        }
    }

    return $tickets.ToArray()
}

function Get-TicketField {
    param(
        [Parameter(Mandatory = $true)]$Ticket,
        [Parameter(Mandatory = $true)][string]$Name
    )
    $key = $Name.ToLower()
    if ($Ticket.Fields.Contains($key)) { return [string]$Ticket.Fields[$key] }
    return ''
}

# Normalize a text for comparison: line endings unified, runs of blank
# lines collapsed, ends trimmed. A parser drops blank lines, so a value
# read back and a value written differ by blank lines alone. Comparing the
# raw forms would report a difference that is not one.
function Normalize-BlockText {
    param([AllowEmptyString()][string]$Text)
    if ($null -eq $Text) { return '' }
    $x = $Text -replace "`r`n", "`n"
    $x = $x -replace "`n{2,}", "`n"
    return $x.Trim()
}

# Read a file from the Cloud's repository, from the most authoritative
# source available.
#
# The truth is the tip of the Cloud's own repository, because that is what
# the Cloud reads after its `git pull --rebase origin main`. A working tree
# can be many commits behind that tip, and a delivery that was never pushed
# is invisible to the Cloud.
#
# Returned object:
#   Source    - which source was read
#   Text      - the content (empty when nothing could be read)
#   Definitive- $true when the source IS the tip, so a verdict on it is a
#               verdict on what the Cloud will actually read.
#               $false when the source may be stale: an unmeasurable state,
#               which must never be reported as a healthy one.
function Get-CloudFileLive {
    param(
        [string]$CloudRoot = '',
        [string]$Remote = 'origin',
        [string]$Branch = 'main',
        [Parameter(Mandatory = $true)][string]$RelativePath
    )
    $result = @{ Source = 'NONE'; Text = ''; Definitive = $false }

    if (-not $CloudRoot) { return $result }
    $gitDir = Join-Path $CloudRoot '.git'
    $isRepo = (Test-Path -LiteralPath $gitDir)

    if ($isRepo) {
        $remotes = @(& git -C $CloudRoot remote 2>$null | Where-Object { $_ -and $_.Trim() })
        if ($remotes.Count -gt 0) {
            # Refresh the remote-tracking ref so the read is the live tip.
            $prev = $ErrorActionPreference
            $ErrorActionPreference = 'Continue'
            & git -C $CloudRoot fetch $Remote $Branch 2>&1 | Out-Null
            $fetchCode = $LASTEXITCODE
            $ErrorActionPreference = $prev
            if ($fetchCode -eq 0) {
                $text = Get-GitBlob -RepoRoot $CloudRoot -Spec ($Remote + '/' + $Branch + ':' + $RelativePath)
                if ($null -ne $text) {
                    $result.Source = 'MAVIS-CLOUD-ORIGIN-MAIN'
                    $result.Text = $text
                    $result.Definitive = $true
                    return $result
                }
            }
            # The fetch failed: whatever ref we have may be behind the tip.
            $text = Get-GitBlob -RepoRoot $CloudRoot -Spec ($Remote + '/' + $Branch + ':' + $RelativePath)
            if ($null -ne $text) {
                $result.Source = 'MAVIS-CLOUD-ORIGIN-MAIN-STALE'
                $result.Text = $text
                $result.Definitive = $false
                return $result
            }
            $text = Get-GitBlob -RepoRoot $CloudRoot -Spec ('HEAD:' + $RelativePath)
            if ($null -ne $text) {
                $result.Source = 'MAVIS-CLOUD-HEAD-STALE'
                $result.Text = $text
                $result.Definitive = $false
                return $result
            }
        } else {
            # No remote: this repository's own HEAD is the tip by definition.
            $text = Get-GitBlob -RepoRoot $CloudRoot -Spec ('HEAD:' + $RelativePath)
            if ($null -ne $text) {
                $result.Source = 'MAVIS-CLOUD-LOCAL-HEAD'
                $result.Text = $text
                $result.Definitive = $true
                return $result
            }
        }
    }

    $file = Join-Path $CloudRoot ($RelativePath -replace '/', '\')
    if (Test-Path -LiteralPath $file) {
        $result.Source = 'MAVIS-CLOUD-WORKTREE'
        $result.Text = [System.IO.File]::ReadAllText($file)
        $result.Definitive = $true
        return $result
    }

    return $result
}

function Get-CloudQueueLive {
    param(
        [string]$CloudRoot = '',
        [string]$Remote = 'origin',
        [string]$Branch = 'main'
    )
    return Get-CloudFileLive -CloudRoot $CloudRoot -Remote $Remote -Branch $Branch -RelativePath 'QUEUE/TASKS-FOR-CLOUD.md'
}

# Read one blob from a git repository. Returns $null when the object does
# not exist - an absent object and an unreadable repository are not the
# same thing, and only the first one is a legitimate "not there".
function Get-GitBlob {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string]$Spec
    )
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $out = & git -C $RepoRoot show $Spec 2>&1
    $code = $LASTEXITCODE
    $ErrorActionPreference = $prev
    if ($code -ne 0) { return $null }
    if ($null -eq $out) { return '' }
    # NOT Out-String: it wraps lines at the console width, and a wrapped
    # line is a corrupted file. A ticket body is a contract; it is joined
    # byte for byte.
    return ([string]::Join("`n", @($out)))
}
