# SENTINEL Context Monitor - own version (auto-generated)
# Monitors session state and proposes actions
#
# Measured 2026-10-28: this script published two numbers it had never
# measured. `mimicryScore` was the constant 100, commented "Placeholder:
# returns perfect score", and `dorScore` was the constant 75, commented
# "placeholder". Both were written into 09_LOGS\session_status.json as if
# they were readings, and the guards below them compared against those same
# constants - so the guards could never fire, and the file announced a perfect
# session forever.
#
# What holds now:
#   * DOR is a state function in the doctrine (01_FOUNDATION/proverbs/
#     SENTINEL_PROVERBS.md), so it has no 0-100 scale to report. Its honest
#     form is a flag, read from the file the hub writes.
#   * The anti-mimicry score IS measurable, but only by the 13 documented
#     detectors in 08_SELF_IMPROVEMENT/mimicry_detectors.py, and they need the
#     output text to inspect. This script has no text, so it reports the state
#     flag and points at the tool that can measure the score.
#
# A measurement that was not taken is reported as not taken, never as a
# perfect score.
#
# Exit codes: 0 - a measurement was taken and written. 1 - the measurement
# failed (the counter is unreadable, or the status could not be written).

param(
    [string]$WorkspaceRoot = 'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\SENTINEL_PRIME',
    [switch]$Verbose
)

# Configuration
$COUNTER_FILE = Join-Path $WorkspaceRoot '09_LOGS\context_counter.txt'
$STATUS_FILE = Join-Path $WorkspaceRoot '09_LOGS\session_status.json'
$PRESSURE_LOG = Join-Path $WorkspaceRoot '09_LOGS\pressure_log.json'
$STATE_FILE = Join-Path $WorkspaceRoot '09_LOGS\sentinel_state.json'
$LEARNINGS_FILE = Join-Path $WorkspaceRoot '09_LOGS\learnings.log'
$DECISIONS_FILE = Join-Path $WorkspaceRoot '09_LOGS\decisions.log'

$THRESHOLDS = @{
    WARN = 50
    TRIGGER = 70
    CRITICAL = 85
}

# The pressure log keeps the last N entries. The doctrine's reference
# implementation appends without a bound, and the file is rewritten in full on
# every run, so it would grow without limit on a session that runs it often.
$PRESSURE_LOG_KEEP = 500

# Writes UTF-8 with no byte order mark.
#
# Measured 2026-10-28: `Set-Content -Encoding UTF8` on PowerShell 5.1 writes a
# BOM. A reader that opens the file as plain UTF-8 then sees the BOM as the
# first character of the text, and json.loads refuses the document. The
# artefacts this script writes are read by the monitor's `logs_parse` check,
# so a BOM here would turn a good file into a parse failure.
function Write-Utf8NoBom {
    param([string]$Path, [string]$Content)
    $parent = Split-Path $Path -Parent
    if ($parent -and -not (Test-Path $parent)) {
        New-Item -Path $parent -ItemType Directory -Force | Out-Null
    }
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Content, $encoding)
}

# Reads the counter.
#
# The three states are kept apart on purpose:
#   missing - no turn has ever been recorded. The first turn creates it.
#   ok      - a count is there and can be incremented.
#   corrupt - a file is there but does not hold an integer. It is NOT
#             overwritten: the broken counter is the evidence, and the run
#             reports the failure instead of hiding it.
function Read-Counter {
    if (-not (Test-Path $COUNTER_FILE)) {
        return @{ state = 'missing'; value = 0; reason = 'no counter file yet' }
    }
    $raw = $null
    try {
        $raw = [System.IO.File]::ReadAllText($COUNTER_FILE)
    } catch {
        return @{ state = 'corrupt'; value = $null; reason = "the counter file is unreadable: $($_.Exception.Message)" }
    }
    $text = $raw.Trim()
    if ($text.Length -eq 0) {
        return @{ state = 'corrupt'; value = $null; reason = 'the counter file is empty' }
    }
    $value = 0
    if (-not [int]::TryParse($text, [ref]$value)) {
        return @{ state = 'corrupt'; value = $null; reason = "the counter file does not hold an integer: '$text'" }
    }
    return @{ state = 'ok'; value = $value; reason = '' }
}

# Reads the SENTINEL state flags the hub writes through sentinel_set_state.
#
# Measured 2026-10-28: this file does not exist on this machine - nothing has
# ever called sentinel_set_state. That is the honest state of affairs, so the
# flags are reported as NOT MEASURED rather than as "true by default".
function Read-SentinelState {
    $result = @{
        measured = $false
        anti_mimicry = $null
        dor = $null
        source = $STATE_FILE
        reason = ''
    }
    if (-not (Test-Path $STATE_FILE)) {
        $result.reason = 'the sentinel state file has never been written on this machine'
        return $result
    }
    $raw = $null
    try {
        $raw = [System.IO.File]::ReadAllText($STATE_FILE)
    } catch {
        $result.reason = "the sentinel state file is unreadable: $($_.Exception.Message)"
        return $result
    }
    $parsed = $null
    try {
        $parsed = $raw | ConvertFrom-Json
    } catch {
        $result.reason = 'the sentinel state file does not hold valid JSON'
        return $result
    }
    if ($null -eq $parsed) {
        $result.reason = 'the sentinel state file is empty'
        return $result
    }
    $names = @($parsed.PSObject.Properties.Name)
    if ($names -contains 'anti_mimicry') {
        $result.anti_mimicry = [bool]$parsed.anti_mimicry
    }
    if ($names -contains 'dor') {
        $result.dor = [bool]$parsed.dor
    }
    if ($null -ne $result.anti_mimicry -or $null -ne $result.dor) {
        $result.measured = $true
    } else {
        $result.reason = 'the sentinel state file carries neither anti_mimicry nor dor'
    }
    return $result
}

# Appends the pressure reading to the log the doctrine names.
#
# The doctrine's reference implementation writes 09_LOGS\pressure_log.json as
# a JSON array. It is written here too, bounded to the last PRESSURE_LOG_KEEP
# entries, so the file the doctrine names actually exists.
function Write-PressureLog {
    param([hashtable]$Entry)
    $entries = @()
    if (Test-Path $PRESSURE_LOG) {
        try {
            $parsed = [System.IO.File]::ReadAllText($PRESSURE_LOG) | ConvertFrom-Json
            if ($parsed -is [System.Array]) {
                $entries = @($parsed)
            }
        } catch {
            $entries = @()
        }
    }
    $entries = @($entries) + @($Entry)
    if ($entries.Count -gt $PRESSURE_LOG_KEEP) {
        $entries = @($entries[($entries.Count - $PRESSURE_LOG_KEEP)..($entries.Count - 1)])
    }
    $json = ConvertTo-Json -InputObject @($entries) -Depth 5
    if ($entries.Count -eq 1 -and -not $json.TrimStart().StartsWith('[')) {
        # A single entry must still be an array: the doctrine's log is a list.
        $json = '[' + $json + ']'
    }
    Write-Utf8NoBom -Path $PRESSURE_LOG -Content $json
}

# Main
function Invoke-Monitor {
    $counter = Read-Counter

    if ($counter.state -eq 'corrupt') {
        Write-Host "==============================================================="
        Write-Host "SENTINEL PRIME - Context Monitor - MEASUREMENT FAILED" -ForegroundColor Red
        Write-Host "==============================================================="
        Write-Host ""
        Write-Host "Counter:        UNREADABLE - $($counter.reason)" -ForegroundColor Red
        Write-Host ""
        Write-Host "STATUS: ERROR - the counter was NOT overwritten." -ForegroundColor Red
        Write-Host "ACTION: repair 09_LOGS\context_counter.txt by hand, then run again." -ForegroundColor Red

        $errorStatus = [ordered]@{
            timestamp = (Get-Date).ToString('o')
            counter = $null
            estimated_pct = $null
            status = 'ERROR'
            action = 'repair the context counter, then run the monitor again'
            counter_state = 'corrupt'
            counter_reason = $counter.reason
        }
        try {
            Write-Utf8NoBom -Path $STATUS_FILE -Content (ConvertTo-Json -InputObject $errorStatus -Depth 5)
        } catch {
            Write-Host "Could not write the status file: $($_.Exception.Message)" -ForegroundColor Red
        }
        exit 1
    }

    $newCount = $counter.value + 1
    Write-Utf8NoBom -Path $COUNTER_FILE -Content ([string]$newCount)

    # The 100 is a double on purpose.
    #
    # Measured 2026-10-28: `[Math]::Min(100, [Math]::Round(1 * 2.5, 1))`
    # returned 2, not 2.5. PowerShell picked the Math.Min(Int32, Int32)
    # overload and truncated the double on the way in, so every pressure
    # figure this script printed was silently floored. The hub tool and the
    # monitor compute the same quantity in Python and reported 2.5 - two
    # instruments measuring one thing and disagreeing. The threshold verdicts
    # survived (50, 70 and 85 are whole numbers), but the number the
    # operator reads did not.
    $estimatedPct = [Math]::Min(100.0, [Math]::Round($newCount * 2.5, 1))

    Write-Host "==============================================================="
    Write-Host "SENTINEL PRIME - Context Monitor - $newCount messages" -ForegroundColor Cyan
    Write-Host "==============================================================="
    Write-Host ""
    Write-Host "Counter:        $newCount"
    Write-Host "Estimated:      $estimatedPct%"
    Write-Host ""

    $status = 'OK'
    $action = 'Continue normally'

    if ($estimatedPct -ge $THRESHOLDS.CRITICAL) {
        $status = 'CRITICAL'
        $action = 'STRATEGIC-COMPACT MANDATORY NOW'
        Write-Host "STATUS: CRITICAL (>=$($THRESHOLDS.CRITICAL)%)" -ForegroundColor Red
        Write-Host "ACTION: $action" -ForegroundColor Red
    } elseif ($estimatedPct -ge $THRESHOLDS.TRIGGER) {
        $status = 'TRIGGER'
        $action = 'Strategic-compact RECOMMENDED before next large batch'
        Write-Host "STATUS: TRIGGER (>=$($THRESHOLDS.TRIGGER)%)" -ForegroundColor Yellow
        Write-Host "ACTION: $action" -ForegroundColor Yellow
    } elseif ($estimatedPct -ge $THRESHOLDS.WARN) {
        $status = 'WARN'
        $action = 'Monitor active; do not launch batches of more than 4 agents'
        Write-Host "STATUS: WARN (>=$($THRESHOLDS.WARN)%)" -ForegroundColor DarkYellow
        Write-Host "ACTION: $action" -ForegroundColor DarkYellow
    } else {
        Write-Host "STATUS: OK (<$($THRESHOLDS.WARN)%)" -ForegroundColor Green
        Write-Host "ACTION: Freedom for normal iterations" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "==============================================================="
    Write-Host "ANTI-MIMICRY AND DOR"
    Write-Host "==============================================================="

    $state = Read-SentinelState

    $antiMimicry = [ordered]@{
        measured = $state.measured
        active = $state.anti_mimicry
        score = $null
        score_measured = $false
        score_source = 'the score needs the output text; use the sentinel_check_mimicry tool (13 documented detectors)'
        source = $STATE_FILE
        reason = $state.reason
    }

    $dor = [ordered]@{
        measured = $state.measured
        active = $state.dor
        score = $null
        score_measured = $false
        note = 'DOR is a state function in the doctrine, not a number on a scale'
        source = $STATE_FILE
        reason = $state.reason
    }

    if ($state.measured) {
        if ($state.anti_mimicry) {
            Write-Host "Anti-mimicry:  ACTIVE (state flag from sentinel_state.json)" -ForegroundColor Green
        } else {
            Write-Host "Anti-mimicry:  OFF (state flag from sentinel_state.json)" -ForegroundColor Red
            Write-Host "WARNING: anti-mimicry is off. Re-anchor the detectors." -ForegroundColor Red
        }
        if ($state.dor) {
            Write-Host "DOR:          ACTIVE (state flag from sentinel_state.json)" -ForegroundColor Green
        } else {
            Write-Host "DOR:          OFF (state flag from sentinel_state.json)" -ForegroundColor Red
            Write-Host "WARNING: DOR low. Re-anchor EU SENT and search." -ForegroundColor Red
        }
        Write-Host "Scores:       NOT MEASURED here - a score needs the output text." -ForegroundColor DarkGray
    } else {
        Write-Host "Anti-mimicry:  NOT MEASURED - $($state.reason)" -ForegroundColor DarkGray
        Write-Host "DOR:          NOT MEASURED - $($state.reason)" -ForegroundColor DarkGray
        Write-Host "No score is reported: a score that was not measured is not a perfect score." -ForegroundColor DarkGray
    }

    # Save status
    $statusObj = [ordered]@{
        timestamp = (Get-Date).ToString('o')
        counter = $newCount
        estimated_pct = $estimatedPct
        status = $status
        action = $action
        anti_mimicry = $antiMimicry
        dor = $dor
    }

    Write-Utf8NoBom -Path $STATUS_FILE -Content (ConvertTo-Json -InputObject $statusObj -Depth 6)

    try {
        Write-PressureLog -Entry ([ordered]@{
            timestamp = $statusObj.timestamp
            counter = $newCount
            estimated_pct = $estimatedPct
            status = $status
            action = $action
        })
    } catch {
        Write-Host "Could not write the pressure log: $($_.Exception.Message)" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "==============================================================="
    Write-Host "Status saved: $STATUS_FILE"
    Write-Host "Pressure log: $PRESSURE_LOG"
    Write-Host "==============================================================="
}

# Run
Invoke-Monitor
exit 0
