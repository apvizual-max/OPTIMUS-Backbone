<#
.SYNOPSIS
  Add a status banner to point-in-time reports so nobody mistakes them for current truth.

.DESCRIPTION
  Popy asked that every file in projects/ reflect the latest system state. But a
  dated report that is REWRITTEN stops being a record of what was true then.

  So: orientation docs are refreshed; point-in-time reports get a banner saying
  what they are and where current truth lives. Content is never destroyed.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$P = 'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard'
$NOW = (Get-Date -Format 'yyyy-MM-dd HH:mm')

# name -> one line on what this document is
$docs = @{
  'MAVIS_FULL_SYSTEMS_REPORT.md'                       = 'a point-in-time system survey from before the MiniMax integration was completed'
  'OPTIMUS_MINIMAX_INTEGRATION_GAP_REPORT.md'          = 'the original gap analysis that defined the P0/P1/P2 work queue'
  'HERMES_DEFECT_relaunch_loop_venv_sync.md'           = 'the diagnosis of the Hermes relaunch-loop / venv-sync defect that has since been FIXED'
  'minimax-h3-skills_assessment.md'                    = 'an assessment of the minimax-h3-skills plugin'
  'code_review_rules.md'                               = 'standing code-review rules (still in force)'
  'memory_summary.md'                                  = 'a memory summary snapshot'
  'SENTINEL_OPERATIONAL_DOCTRINE.md'                   = 'the SENTINEL doctrine — the paste-into-Custom-instructions file. Unchanged; only a pointer is added.'
  'OPTIMUS_MINIMAX_HERMES_ANTIGRAVITY_INTEGRATION_REPORT.md' = 'integration report v3, superseded by the v2 status report of today'
  'OPTIMUS_SYSTEM_TIMELINE.md'                         = 'the append-only project timeline'
}

foreach ($name in $docs.Keys) {
  $path = Join-Path $P $name
  if (-not (Test-Path -LiteralPath $path)) { Write-Host "  missing: $name" -ForegroundColor DarkYellow; continue }
  $text = Get-Content -LiteralPath $path -Raw
  if ($text -match '<!-- SOT-STATUS-BANNER') { Write-Host "  already banner'd: $name" -ForegroundColor DarkGray; continue }

  $banner = @"
<!-- SOT-STATUS-BANNER
  Added $NOW by scripts\stamp-doc-status.ps1

  THIS IS A POINT-IN-TIME DOCUMENT: $($docs[$name]).

  It is deliberately NOT rewritten -- rewriting it would destroy the record of
  what was true when it was written. For the CURRENT system state read:

    POPY_MiniMax_OPTIMUS_Status_Report-10-02-2026.md   <- current state, for Popy
    mavis-minimax-optimus-system                        <- skill: restore + config SOT
    mavis-minimax-index-folder-update                   <- skill: how to index this folder
    optimus status   /  cc start   /  cc guard          <- live truth, measured
-->

"@
  Set-Content -LiteralPath $path -Value ($banner + $text) -Encoding UTF8
  Write-Host ("  banner added: {0}" -f $name) -ForegroundColor Green
}
