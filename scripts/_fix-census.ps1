$ErrorActionPreference = 'Stop'
$f = 'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\90_CONTROL_CENTER\api\collect-state.ps1'
$lines = [System.Collections.ArrayList]@([IO.File]::ReadAllLines($f, [Text.Encoding]::UTF8))

# Replace the process-census ancestry walk. The previous version called
# Get-CimInstance once per HOP, which is hundreds of WMI round trips and made
# the collector slower than before, not faster. One table, then walk it in
# memory.
$start = -1; $end = -1
for ($i = 0; $i -lt $lines.Count; $i++) {
  if ($start -lt 0 -and $lines[$i] -match '\$nodes = @\(Get-CimInstance Win32_Process') { $start = $i }
  if ($start -ge 0 -and $lines[$i] -match '^\} catch \{ \$state\.sections\.processes\.note = "census failed') { $end = $i; break }
}
if ($start -lt 0 -or $end -lt 0) { throw "anchors not found (start=$start end=$end)" }
Write-Host ("replacing census body, lines {0}..{1}" -f ($start + 1), ($end + 1))

$new = [string[]]@(
'  # ONE process table for the whole machine, then walk ancestry in memory.',
'  # Querying per hop means hundreds of WMI round trips, which is how the first',
'  # attempt at this fix made the collector SLOWER than the bug it was fixing.',
'  $all = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue)',
'  $pp  = @{}',
'  foreach ($p in $all) { $pp[[int]$p.ProcessId] = [int]$p.ParentProcessId }',
'  $nodes = @($all | Where-Object { $_.Name -eq ''node.exe'' })',
'  $orph = 0; $omb = 0; $att = 0',
'  foreach ($n in $nodes) {',
'    # Walk the WHOLE ancestry, not one hop. A node whose parent is itself an',
'    # orphan is orphaned too; scoring it "attached" understated the real leak',
'    # by 2x (24 processes / 1.45 GB versus 48 / 2.73 GB).',
'    $id = [int]$n.ProcessId; $hop = 0; $parentAlive = $false',
'    while ($hop -lt 24) {',
'      $parent = $pp[$id]',
'      if ($null -eq $parent -or $parent -eq 0) { $parentAlive = $false; break }',
'      if ($pp.ContainsKey($parent)) { $parentAlive = $true; break }',
'      $id = $parent; $hop++',
'    }',
'    if ($parentAlive) { $att++ } else {',
'      $orph++',
'      try { $omb += (Get-Process -Id $n.ProcessId -ErrorAction SilentlyContinue).WorkingSet64 } catch { }',
'    }',
'  }'
)

for ($i = $end; $i -ge $start; $i--) { $lines.RemoveAt($i) }
for ($j = 0; $j -lt $new.Count; $j++) { $lines.Insert($start + $j, $new[$j]) }
[IO.File]::WriteAllLines($f, $lines.ToArray(), (New-Object Text.UTF8Encoding($false)))

$errs = $null; $toks = $null
[void][System.Management.Automation.Language.Parser]::ParseFile($f, [ref]$toks, [ref]$errs)
if ($errs -and $errs.Count) {
  Write-Host 'PARSE ERRORS:' -ForegroundColor Red
  $errs | Select-Object -First 5 | ForEach-Object { Write-Host ("  L{0}: {1}" -f $_.Extent.StartLineNumber, $_.Message) }
  exit 1
}
Write-Host 'collect-state.ps1 parses OK'
