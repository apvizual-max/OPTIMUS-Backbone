# rebuild-classifier.ps1
# Reclassifies all 1,159 personal skills at C:\Users\apviz\.minimax\skills\ into the
# 4-category framework, writes the result to 70_CONNECTORS/70_personal_skill_index.md,
# and appends a JURNAL_OGLINDA entry to 40_REGISTRIES/40_partition_C_system.md.
#
# Scheduled via mavis cron (weekly). Invoked by Mavis in agent context, not standalone.

$ErrorActionPreference = 'Stop'

$pskills = 'C:\Users\apviz\.minimax\skills'
$tmpCsv  = Join-Path $env:TEMP 'personal_skills_index.csv'
$tmpCls  = Join-Path $env:TEMP 'personal_skills_classified.csv'
$out     = 'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\70_CONNECTORS\70_personal_skill_index.md'
$jrPath  = 'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\40_REGISTRIES\40_partition_C_system.md'

# Phase 1: extract name + description from each SKILL.md
if (Test-Path $tmpCsv) { Remove-Item $tmpCsv -Force }
$sb = [System.Text.StringBuilder]::new()
[void]$sb.AppendLine('dir,desc_first_400')

foreach ($d in Get-ChildItem -Path $pskills -Directory -Force -ErrorAction SilentlyContinue) {
  $skill = Join-Path $d.FullName 'SKILL.md'
  if (-not (Test-Path $skill)) { continue }
  $lines = Get-Content $skill -TotalCount 30 -ErrorAction SilentlyContinue
  if ($null -eq $lines) { continue }
  $desc = ''
  $collecting = $false
  foreach ($line in $lines) {
    if ($line -match '^description:\s*(.+)$') {
      $desc = $matches[1].Trim()
      $collecting = $false
    } elseif ($line -match '^description:\s*(>|\|)?\s*$') {
      $collecting = $true
    } elseif ($collecting -and $line -match '^\s+(.+)$') {
      $append = $matches[1].Trim() -replace '^[-`"'']\s*',''
      if ($append.Length -gt 0) { $desc += ' ' + $append }
    }
  }
  if ($desc.Length -gt 400) { $desc = $desc.Substring(0, 397) + '...' }
  $descSafe = $desc -replace '"','""' -replace ',',';'
  $nameSafe = $d.Name -replace '"','""'
  [void]$sb.AppendLine('"' + $nameSafe + '","' + $descSafe + '"')
}
[System.IO.File]::WriteAllText($tmpCsv, $sb.ToString(), [System.Text.Encoding]::UTF8)

# Phase 2: classify into 4 categories
$kwIdentity   = @('path','file location','workspace','directory','filesystem','identifier','memory','knowledge','map','find files','locate','catalog','inventory','registry','locations','where is')
$kwBehavioral = @('review','evaluate','plan','decision','discipline','ethical','best practice','constraint','validate','verify','audit','assess','principle','governance','compliance','philosophy','ethics','guide','discipline')
$kwRole       = @('expert','specialist','master','agent persona','role','voice','style','tone','character','persona','identity','archetype','coach','mentor','advisor','consultant','operator')

if (Test-Path $tmpCls) { Remove-Item $tmpCls -Force }
$sb2 = [System.Text.StringBuilder]::new()
[void]$sb2.AppendLine('dir,category,desc')
$counts = @{ identity=0; behavioral=0; role=0; operations=0 }

$inLines = Get-Content $tmpCsv -ErrorAction SilentlyContinue
for ($i = 1; $i -lt $inLines.Count; $i++) {
  $line = $inLines[$i]
  if ($line.Length -lt 3) { continue }
  $match = [regex]::Match($line, '^"((?:[^"]|"")*)","((?:[^"]|"")*)"$')
  if (-not $match.Success) { continue }
  $dir = $match.Groups[1].Value -replace '""','"'
  $desc = $match.Groups[2].Value -replace '""','"' -replace ';',',' | Select-Object -First 1
  if ($desc.Length -lt 5) {
    [void]$sb2.AppendLine('"' + $dir + '","Operations",""')
    $counts.operations++
    continue
  }
  $descLower = $desc.ToLower()
  $sI = 0; $sB = 0; $sR = 0
  foreach ($kw in $kwIdentity)   { if ($descLower -match [regex]::Escape($kw)) { $sI++ } }
  foreach ($kw in $kwBehavioral) { if ($descLower -match [regex]::Escape($kw)) { $sB++ } }
  foreach ($kw in $kwRole)       { if ($descLower -match [regex]::Escape($kw)) { $sR++ } }
  $maxScore = ($sI, $sB, $sR | Measure-Object -Maximum).Maximum
  $cat = 'Operations'
  if ($maxScore -gt 0) {
    if ($sI -eq $maxScore) { $cat = 'Identity and File Locations' }
    elseif ($sB -eq $maxScore) { $cat = 'Behavioral' }
    elseif ($sR -eq $maxScore) { $cat = 'Role Definition' }
  }
  $key = switch ($cat) {
    'Identity and File Locations' { 'identity' }
    'Behavioral' { 'behavioral' }
    'Role Definition' { 'role' }
    default { 'operations' }
  }
  $counts[$key]++
  $descSafe = $desc -replace '"','""'
  [void]$sb2.AppendLine('"' + $dir + '","' + $cat + '","' + $descSafe.Substring(0, [Math]::Min(300, $descSafe.Length)) + '"')
}
[System.IO.File]::WriteAllText($tmpCls, $sb2.ToString(), [System.Text.Encoding]::UTF8)

# Phase 3: render markdown reference
$byCategory = @{
  'Identity and File Locations' = [System.Collections.Generic.List[string]]::new()
  'Behavioral' = [System.Collections.Generic.List[string]]::new()
  'Role Definition' = [System.Collections.Generic.List[string]]::new()
  'Operations' = [System.Collections.Generic.List[string]]::new()
}

$clsLines = Get-Content $tmpCls -ErrorAction SilentlyContinue
for ($i = 1; $i -lt $clsLines.Count; $i++) {
  $line = $clsLines[$i]
  $match = [regex]::Match($line, '^"((?:[^"]|"")*)","((?:[^"]|"")*)","(.*)"$')
  if (-not $match.Success) { continue }
  $dir = $match.Groups[1].Value -replace '""','"'
  $cat = $match.Groups[2].Value -replace '""','"'
  $desc = $match.Groups[3].Value -replace '""','"' -replace ';',','
  if ($desc.Length -gt 220) { $desc = $desc.Substring(0, 217) + '...' }
  $lineOut = ('- `' + $dir + '` — ' + $desc)
  if ($byCategory.ContainsKey($cat)) {
    $byCategory[$cat].Add($lineOut)
  } else {
    $byCategory['Operations'].Add($lineOut)
  }
}

$dateStr = Get-Date -Format 'yyyy-MM-dd HH:mm'
$sb3 = [System.Text.StringBuilder]::new()
[void]$sb3.AppendLine('# Personal Skills Classifier — Index of 1,159 skills')
[void]$sb3.AppendLine('')
[void]$sb3.AppendLine('**Date**: ' + $dateStr)
[void]$sb3.AppendLine('**Source**: `C:\Users\apviz\.minimax\skills\` (1,159 SKILL.md files)')
[void]$sb3.AppendLine('**Author**: Mavis (orchestrator) — auto-rebuilt weekly by cron')
[void]$sb3.AppendLine('**Status**: Auto-classified via keyword heuristics on SKILL.md `description:` frontmatter.')
[void]$sb3.AppendLine('')
[void]$sb3.AppendLine('---')
[void]$sb3.AppendLine('')
[void]$sb3.AppendLine('## Distribution')
[void]$sb3.AppendLine('')
[void]$sb3.AppendLine('| Category | Count | % |')
[void]$sb3.AppendLine('|---|---|---|')
$total = ($counts.identity + $counts.behavioral + $counts.role + $counts.operations)
foreach ($cat in @('identity','behavioral','role','operations')) {
  $label = switch ($cat) {
    'identity' { 'Identity and File Locations' }
    'behavioral' { 'Behavioral' }
    'role' { 'Role Definition' }
    default { 'Operations' }
  }
  $pct = if ($total -gt 0) { [math]::Round(($counts[$cat] / $total) * 100, 1) } else { 0 }
  [void]$sb3.AppendLine('| ' + $label + ' | ' + $counts[$cat] + ' | ' + $pct + '% |')
}
[void]$sb3.AppendLine('| **Total** | **' + $total + '** | **100%** |')
[void]$sb3.AppendLine('')
[void]$sb3.AppendLine('---')
[void]$sb3.AppendLine('')

foreach ($cat in @('Identity and File Locations','Behavioral','Role Definition','Operations')) {
  [void]$sb3.AppendLine('## ' + $cat + ' (' + $byCategory[$cat].Count + ')')
  [void]$sb3.AppendLine('')
  $sorted = $byCategory[$cat] | Sort-Object
  foreach ($l in $sorted) { [void]$sb3.AppendLine($l) }
  [void]$sb3.AppendLine('')
}

[System.IO.File]::WriteAllText($out, $sb3.ToString(), [System.Text.Encoding]::UTF8)

# Phase 4: insert JURNAL entry INSIDE the JURNAL_OGLINDA table (not at end-of-file)
# Use single-quoted string for the filename to avoid PowerShell stripping the backticks
$dateOnly = Get-Date -Format 'yyyy-MM-dd'
$fname = '70_personal_skill_index.md'
$fnameWithTicks = '`' + $fname + '`'
$jrEntry = '| ' + $dateOnly + ' | Classifier rebuilt (cron) | All ' + $total + ' skills reclassified; ' + $fnameWithTicks + ' updated; distribution: Identity=' + $counts.identity + ', Behavioral=' + $counts.behavioral + ', Role=' + $counts.role + ', Operations=' + $counts.operations + ' |'
# Find the last '| 20' line in the JURNAL_OGLINDA table and insert the new entry right after it.
# This keeps the table well-formed instead of the entry being appended to end-of-file.
$jrContent = Get-Content $jrPath -Raw -ErrorAction SilentlyContinue
if ($jrContent) {
  $linesArr = $jrContent -split "`n"
  $lastJrnLineIdx = -1
  for ($i = 0; $i -lt $linesArr.Count; $i++) {
    if ($linesArr[$i] -match '^\| 20\d{2}-\d{2}-\d{2} \|') { $lastJrnLineIdx = $i }
  }
  if ($lastJrnLineIdx -ge 0) {
    # Insert after the last existing JURNAL row (which is at lastJrnLineIdx + 1 line in 1-based)
    $insertPos = $lastJrnLineIdx + 1
    $newContent = ($linesArr[0..($insertPos - 1)] -join "`n") + "`n" + $jrEntry + "`n" + ($linesArr[$insertPos..($linesArr.Count - 1)] -join "`n")
    [System.IO.File]::WriteAllText($jrPath, $newContent, [System.Text.Encoding]::UTF8)
  } else {
    # No existing JURNAL rows found — fall back to plain append
    Add-Content -Path $jrPath -Value $jrEntry -Encoding UTF8
  }
}

# Phase 5: re-append the Inferred purposes section (it gets wiped by the rebuild in Phase 3)
# The inferred_purposes.ps1 script handles this - it reads the freshly-rebuilt classifier,
# finds skills with empty descriptions, and appends a SPECULATION-marked section.
$inferScript = Join-Path $PSScriptRoot 'inferred_purposes.ps1'
if (Test-Path $inferScript) {
  & $inferScript
}

# Cleanup tmp
Remove-Item $tmpCsv -Force -ErrorAction SilentlyContinue
Remove-Item $tmpCls -Force -ErrorAction SilentlyContinue

Write-Output "rebuild-classifier: complete"
Write-Output "  Total: $total"
Write-Output "  Identity: $($counts.identity)"
Write-Output "  Behavioral: $($counts.behavioral)"
Write-Output "  Role: $($counts.role)"
Write-Output "  Operations: $($counts.operations)"
Write-Output "  Output: $out"
Write-Output "  JURNAL: $jrPath (appended)"
