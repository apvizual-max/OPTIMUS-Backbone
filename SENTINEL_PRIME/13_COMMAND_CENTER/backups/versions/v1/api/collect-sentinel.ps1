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
$STATE = Join-Path $API 'sentinel-state.json'
$HISTORY = Join-Path $API 'state-history.jsonl'
$HEALTH = Join-Path $API 'health.json'
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
$health = Read-Json $HEALTH

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
}
if (Test-Path $testLog) {
  $t = Read-Json $testLog
  if ($t) {
    $tests.passed = $t.passed
    $tests.failed = $t.failed
    $tests.skipped = $t.skipped
    $tests.ran_at = $t.ran_at
    $tests.classes = $t.classes
  }
}

# 7. Gaps, straight from the register.
$gaps = @()
$gapPath = Join-Path $WORKSPACE '12_PROGRAM\GAP_REGISTER.json'
if (Test-Path $gapPath) {
  $g = Read-Json $gapPath
  if ($g) { $gaps = $g }
}

$now = (Get-Date).ToString('o')
$stateAgeBound = 300
$state = [ordered]@{
  generated = $now
  age_sec = 0
  age_bound_sec = $stateAgeBound
  status = if ($health) { $health.overall } else { 'NOT_RUN' }
  counts = if ($health) { $health.counts } else { $null }
  by_family = if ($health) { $health.by_family } else { $null }
  health_checks = if ($health) { $health.checks } else { @() }
  corpus = [ordered]@{
    status = if ($corpusStats) { 'MEASURED' } else { 'NOT_MEASURED' }
    reason = if ($corpusStats) { 'corpus_stats.json' } else { 'corpus_stats.json missing' }
    messages = if ($corpusStats) { $corpusStats.messages_total } else { $null }
    user_turns = if ($corpusStats) { $corpusStats.total_user_turns } else { $null }
    chapters = if ($corpusStats) { @($corpusStats.chapters).Count } else { 0 }
    unplaced = if ($corpusStats) { $corpusStats.unplaced_messages } else { $null }
    retention = if ($corpusStats) { $corpusStats.retention.verbatim_retention_ratio } else { $null }
    sha256 = if ($corpusStats) { $corpusStats.corpus_sha256 } else { $null }
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
}

# Age is measured at write time, so the UI never has to guess it.
$stateFileItem = Get-Item $STATE -ErrorAction SilentlyContinue
$bytes = [Text.Encoding]::UTF8.GetBytes(($state | ConvertTo-Json -Depth 12 -Compress:$false))
Set-Content -Path $STATE -Value ($state | ConvertTo-Json -Depth 12) -Encoding UTF8

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
