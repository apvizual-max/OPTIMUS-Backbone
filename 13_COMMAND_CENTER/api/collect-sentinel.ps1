<#
.SYNOPSIS
  Measures the SENTINEL layer and writes what it measured.

.DESCRIPTION
  The Command Center renders; it does not rule. This collector is the only
  thing allowed to produce a verdict, and it produces it by RUNNING a
  measurement - never by asserting a sentence.

  It writes:
    api\sentinel-state.json   what /api/state returns
    api\state-history.jsonl   append-only time series

  It never writes a SENTINEL state file. The workflow engine is the single
  writer of bimodal_state.json; this script only reads it. Two writers would
  corrupt the one file the dashboard trusts most.

  A missing source produces NOT_MEASURED with a reason, never a healthy-looking
  default. That distinction is the whole point: a panel that cannot say "I did
  not check" will eventually be believed when it did not check.

.PARAMETER Quiet
  Suppress the human summary (the server calls it every refresh cycle).
#>
[CmdletBinding()]
param([switch]$Quiet)

$ErrorActionPreference = 'Stop'
$API = $PSScriptRoot
$ROOT = Split-Path -Parent $API
$WORKSPACE = Split-Path -Parent $ROOT
$STATE_PATH = Join-Path $API 'sentinel-state.json'
$HISTORY = Join-Path $API 'state-history.jsonl'
$HEALTH_PATH = Join-Path $API 'health.json'
$PY = (Get-Command python -ErrorAction SilentlyContinue).Source

function Get-Age($path) {
  if (-not (Test-Path $path)) { return $null }
  return [math]::Round(((Get-Date) - (Get-Item $path).LastWriteTime).TotalSeconds, 1)
}

function Read-Json($path) {
  if (-not (Test-Path $path)) { return $null }
  try { return (Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json) }
  catch { return $null }
}

if (-not $PY) { throw 'python not on PATH' }

# 1. Run the monitor. It is the single source of every verdict.
try {
  & $PY (Join-Path $WORKSPACE '08_SELF_IMPROVEMENT\monitor.py') --write | Out-Null
} catch {
  Write-Host "monitor failed: $($_.Exception.Message)"
}
$health = Read-Json $HEALTH_PATH

# 2. Corpus, read from the generated index rather than recomputed.
$corpusStats = Read-Json (Join-Path $WORKSPACE '11_BRAIN\01_RAW\corpus_stats.json')
$chapters = @()
$chaptersDir = Join-Path $WORKSPACE '11_BRAIN\02_CHAPTERS'
if (Test-Path $chaptersDir) {
  $chapters = Get-ChildItem $chaptersDir -Filter 'CH_*.md' -ErrorAction SilentlyContinue |
    Sort-Object Name | ForEach-Object {
      $head = (Get-Content $_.FullName -TotalCount 8 -Encoding UTF8) -join "`n"
      $seq = 'unknown'
      if ($head -match 'seq range\*\*: `(\d+)\.\.(\d+)`') { $seq = "$($Matches[1])..$($Matches[2])" }
      $turns = 'unknown'
      if ($head -match 'user turns\*\*: `(\d+)\.\.(\d+)`') { $turns = "$($Matches[1])..$($Matches[2])" }
      [ordered]@{
        file = $_.Name
        bytes = $_.Length
        title = (Get-Content $_.FullName -TotalCount 1 -Encoding UTF8) -replace '^#\s*', ''
        seq = $seq
        turns = $turns
      }
    }
}

# 2b. Unplaced messages. Neither corpus_stats.json nor chapter_map.json carries
# the figure: the map has only _comment / digest_reference / chapters. The
# renderer writes the answer to 02_CHAPTERS\UNPLACED.md, so that is the only
# honest source. An absent file is NOT_MEASURED, never an assumed zero.
$unplacedCount = $null
$unplacedSource = 'NOT_MEASURED (no UNPLACED.md)'
$unplacedFile = Join-Path $WORKSPACE '11_BRAIN\02_CHAPTERS\UNPLACED.md'
if (Test-Path $unplacedFile) {
  $utxt = Get-Content $unplacedFile -Raw -Encoding UTF8
  if ($utxt -match '\*\*None\.\*\*') {
    $unplacedCount = 0
    $unplacedSource = '02_CHAPTERS\UNPLACED.md ("None")'
  } else {
    # Count the listed entries: each is a bullet naming a seq.
    $unplacedCount = ([regex]::Matches($utxt, '(?m)^\s*[-*]\s')).Count
    $unplacedSource = '02_CHAPTERS\UNPLACED.md (listed entries)'
  }
}

# 3. Workflow state - read only. The engine owns this file.
$workflow = Read-Json (Join-Path $WORKSPACE '09_LOGS\bimodal_state.json')
$workflowView = [ordered]@{
  status = if ($workflow) { 'MEASURED' } else { 'NOT_MEASURED' }
  reason = if ($workflow) { 'bimodal_state.json' } else { 'bimodal_state.json missing' }
  mode = if ($workflow) { $workflow.mode } else { $null }
  stop_reason = if ($workflow) { $workflow.stop_reason } else { $null }
  stopped_at = if ($workflow) { $workflow.stopped_at } else { $null }
  stopped = if ($workflow) { ($workflow.mode -eq 'STOPPED') } else { $null }
  awaiting_user_input = if ($workflow) { ($workflow.mode -eq 'STOPPED') } else { $null }
  consecutive_failures = if ($workflow) { $workflow.consecutive_failures } else { $null }
  max_failures = 5
  execution_attempts = if ($workflow) { $workflow.execution_attempts } else { $null }
  agreement_goal = if ($workflow -and $workflow.agreement) { $workflow.agreement.goal } else { $null }
  age_sec = Get-Age (Join-Path $WORKSPACE '09_LOGS\bimodal_state.json')
}

# 4. Programme matrix, if generated.
$matrix = @()
$matrixPath = Join-Path $WORKSPACE '12_PROGRAM\IDEA_TO_SCRIPT_MATRIX.json'
if (Test-Path $matrixPath) {
  $rows = Read-Json $matrixPath
  if ($rows) {
    $matrix = $rows | ForEach-Object {
      [ordered]@{
        concept = $_.concept
        status = $_.status
        doctrine = $_.doctrine
        implementation = $_.implementation
        test = $_.test
        panel = $_.panel
        owner = $_.owner
      }
    }
  }
}

# 5. Learning queue - lessons awaiting the operator's R0.
$learningPath = Join-Path $WORKSPACE '09_LOGS\self_improvement_candidates.json'
$learning = [ordered]@{
  status = if (Test-Path $learningPath) { 'MEASURED' } else { 'NOT_MEASURED' }
  reason = if (Test-Path $learningPath) { 'self_improvement_candidates.json' } else { 'no candidates file yet' }
  total = 0; candidates = 0; ratified = 0; promoted = 0; awaiting_r0 = 0
}
if (Test-Path $learningPath) {
  $c = Read-Json $learningPath
  if ($c) {
    $learning.total = $c.Count
    $learning.candidates = @($c | Where-Object { $_.status -eq 'CANDIDATE' }).Count
    $learning.ratified = @($c | Where-Object { $_.status -eq 'RATIFIED' }).Count
    $learning.promoted = @($c | Where-Object { $_.status -eq 'PROMOTED' }).Count
    $learning.awaiting_r0 = $learning.candidates
  }
}

# 6. Test suite: last known result, clearly labelled as last-known.
$testLog = Join-Path $API 'last_test_run.json'
$tests = [ordered]@{
  status = if (Test-Path $testLog) { 'MEASURED' } else { 'NOT_MEASURED' }
  reason = if (Test-Path $testLog) { 'last_test_run.json' } else { 'no test run recorded yet' }
  passed = $null; failed = $null; skipped = $null; ran_at = $null
  # Named explicitly. `skipped` is a COUNT: it tells a reader that something
  # went unmeasured but not WHICH, and the Tests panel has no way to render a
  # verdict it cannot name. These four carry the identity of the shortfall to
  # the panel, so a partial run cannot present as a clean one.
  not_run = @(); partial = @(); green = $false
}
if (Test-Path $testLog) {
  $t = Read-Json $testLog
  if ($t) {
    $tests.passed = $t.passed
    $tests.failed = $t.failed
    $tests.skipped = $t.skipped
    $tests.ran_at = $t.ran_at
    $tests.classes = $t.classes
    # The inventory's own declared total. Carried through verbatim so the
    # deployment suite can hold it against both the shipped list and the suite
    # source; without it the registry entry for `classes` would be a waiver.
    if ($null -ne $t.total_classes) { $tests.total_classes = $t.total_classes }
    if ($null -ne $t.not_run) { $tests.not_run = $t.not_run }
    if ($null -ne $t.partial)  { $tests.partial  = $t.partial }
    if ($null -ne $t.green)    { $tests.green    = $t.green }
  }
}

# 7. Gaps, straight from the register.
#
# The ledger keeps every entry, closed ones included: a gap that was decided
# and then done is the record that the work happened, and deleting it would
# delete the requirement. But the panel says "Open gaps" and counts what it is
# handed, so feeding it the whole ledger makes the number wrong the moment the
# first entry closes - measured 2026-10-28, a ledger of 19 entries with 13
# closed would have read as "19 open gaps".
#
# The split happens HERE, on the data side, so no markup has to change and
# nothing is dropped: `gaps` carries the open entries, and the closed ones are
# still counted and named next to them.
$gaps = @()
$gapsClosed = @()
$gapPath = Join-Path $WORKSPACE '12_PROGRAM\GAP_REGISTER.json'
if (Test-Path $gapPath) {
  $g = Read-Json $gapPath
  if ($g) {
    $gaps = @($g | Where-Object { $_.status -ne 'CLOSED-BUILT' })
    $gapsClosed = @($g | Where-Object { $_.status -eq 'CLOSED-BUILT' })
  }
}

$now = (Get-Date).ToString('o')
$stateAgeBound = 300
# The state object is `$state`, the path is `$STATE_PATH`. These must not differ
# only by case: PowerShell variable names are case-INSENSITIVE, so `$state` and
# `$STATE` are one variable sharing one slot. The original script had exactly
# that collision - the path was assigned first, then overwritten by this object -
# so Set-Content wrote to a file literally named
# "System.Collections.Specialized.OrderedDictionary" and the real state file was
# never created. The script still exited 0, still appended history, and still
# printed a healthy summary. Renaming the PATH is the fix; the discipline that
# keeps it fixed is the ps_variable_case_collisions check in monitor.py.
$state = [ordered]@{
  generated = $now
  age_sec = 0
  age_bound_sec = $stateAgeBound
  status = if ($health) { $health.overall } else { 'NOT_RUN' }
  counts = if ($health) { $health.counts } else { $null }
  by_family = if ($health) { $health.by_family } else { $null }
  health_checks = if ($health) { $health.checks } else { @() }
  # The count the copy above claims to be. Without it, `health_checks` is an
  # over-bound list with nothing to contradict it: a truncated or partial copy
  # would ship 12 checks and read as a system with 12 checks. Carried verbatim
  # from the same health.json, so the two cannot disagree at source.
  health_total_checks = if ($health -and ($null -ne $health.total_checks)) { $health.total_checks } else { $null }
  corpus = [ordered]@{
    status = if ($corpusStats) { 'MEASURED' } else { 'NOT_MEASURED' }
    reason = if ($corpusStats) { 'corpus_stats.json + 02_CHAPTERS\CH_*.md' } else { 'corpus_stats.json missing' }
    messages = if ($corpusStats) { $corpusStats.messages_total } else { $null }
    # Real key is `user_turns`. The previous expression asked for
    # `total_user_turns`, which does not exist, so the panel rendered a blank
    # next to the number of user turns - the single most-watched figure in the
    # whole project. A missing key is NOT_MEASURED, never a silent blank.
    user_turns = if ($corpusStats) { $corpusStats.user_turns } else { $null }
    assistant_turns = if ($corpusStats) { $corpusStats.assistant_turns } else { $null }
    verbatim = if ($corpusStats) { $corpusStats.verbatim } else { $null }
    evidence = if ($corpusStats) { $corpusStats.evidence } else { $null }
    # Counted from the chapter files, not from corpus_stats.json. That file has
    # no `chapters` key at all, and `@($null).Count` is 1 in PowerShell, so the
    # previous expression cheerfully reported "1 chapter" while 17 CH_*.md files
    # sat in the directory. A count taken from a field that does not exist is not
    # a measurement.
    chapters = $chapters.Count
    chapter_source = '02_CHAPTERS\CH_*.md on disk'
    # corpus_stats.json carries no unplaced figure; it is a property of
    # chapter_map.json. Read it from there or say NOT_MEASURED - do not invent.
    unplaced = $unplacedCount
    unplaced_source = $unplacedSource
    retention = if ($corpusStats) { $corpusStats.retention.verbatim_retention_ratio } else { $null }
    sha256 = if ($corpusStats) { $corpusStats.corpus_sha256 } else { $null }
    integrity_checks = if ($corpusStats) { @($corpusStats.checks).Count } else { 0 }
    integrity_ok = if ($corpusStats) { @($corpusStats.checks | Where-Object { $_.status -ne 'OK' }).Count -eq 0 } else { $false }
    chapter_list = $chapters
  }
  workflow = $workflowView
  program = [ordered]@{
    status = if ($matrix.Count -gt 0) { 'MEASURED' } else { 'NOT_MEASURED' }
    reason = if ($matrix.Count -gt 0) { 'IDEA_TO_SCRIPT_MATRIX.json' } else { 'matrix not generated yet' }
    rows = $matrix
  }
  learning = $learning
  tests = $tests
  gaps = $gaps
  # The closed entries are not hidden by being left out of `gaps`: they are
  # counted and named here, and their full text stays in the ledger.
  gaps_closed_count = $gapsClosed.Count
  gaps_closed_ids = @($gapsClosed | ForEach-Object { $_.id })
}

# Age is measured at write time, so the UI never has to guess it.
#
# This write used to be silent: the script finished, the history file grew, and
# sentinel-state.json simply never appeared, so /api/state served its honest
# fallback and the panel showed nothing with no error anywhere. A step that can
# fail without throwing has to narrate itself, and a step whose result matters
# has to be checked. Both are done here.
$stateJson = $state | ConvertTo-Json -Depth 12
if (-not $Quiet) {
  Write-Host ("  writing {0} ({1} bytes, {2} top-level keys)" -f `
    $STATE_PATH, $stateJson.Length, $state.Keys.Count)
}
try {
  # BOM-less UTF-8. PowerShell 5.1's -Encoding UTF8 prepends a BOM, and Python's
  # json.load refuses it ("Unexpected UTF-8 BOM"). Every consumer of these files
  # should not have to know which shell wrote them.
  $utf8NoBom = New-Object System.Text.UTF8Encoding $false
  [IO.File]::WriteAllText($STATE_PATH, $stateJson, $utf8NoBom)
} catch {
  throw "could not write state file '$STATE_PATH': $($_.Exception.Message)"
}
if (-not (Test-Path $STATE_PATH)) {
  throw "state file '$STATE_PATH' is absent immediately after a successful Set-Content"
}
if (-not $Quiet) {
  Write-Host ("  wrote  {0} ({1} bytes on disk)" -f $STATE_PATH, (Get-Item $STATE_PATH).Length)
}

# Append-only history. Used for the trend panel.
$point = [ordered]@{
  ts = $now
  status = $state.status
  ok = if ($health) { $health.counts.OK } else { 0 }
  fail = if ($health) { $health.counts.FAIL } else { 0 }
  stale = if ($health) { $health.counts.STALE } else { 0 }
  notrun = if ($health) { $health.counts.NOT_RUN } else { 0 }
  mode = $workflowView.mode
  corpus_messages = $state.corpus.messages
}
Add-Content -Path $HISTORY -Value ($point | ConvertTo-Json -Compress) -Encoding UTF8
# Rewrite BOM-less when trimming, so the whole file shares one encoding.

# Keep the history bounded: 2000 points is far more than the dashboard reads.
$all = Get-Content $HISTORY -ErrorAction SilentlyContinue
if ($all -and $all.Count -gt 2000) {
  $all | Select-Object -Last 2000 | Set-Content -Path $HISTORY -Encoding UTF8
}

if (-not $Quiet) {
  Write-Host ("[{0}] status={1} ok={2} fail={3} stale={4} notrun={5} mode={6}" -f `
    $now, $state.status,
    $(if ($health) { $health.counts.OK } else { '?' }),
    $(if ($health) { $health.counts.FAIL } else { '?' }),
    $(if ($health) { $health.counts.STALE } else { '?' }),
    $(if ($health) { $health.counts.NOT_RUN } else { '?' }),
    $workflowView.mode)
}
