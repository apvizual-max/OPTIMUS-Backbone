$ErrorActionPreference = 'Continue'
$f = 'C:\Users\apviz\AI_Tools\mcp-database-bridge.js'
$t = [IO.File]::ReadAllText($f)
Write-Host ("mcp-database-bridge.js : {0:N0} bytes" -f $t.Length)
Write-Host ''
Write-Host '=== does it implement the MCP/SSE protocol, or just a REST shim? ==='
foreach ($k in @('text/event-stream','initialize','tools/list','jsonrpc','Last-Event-ID','/sse','/message','405')) {
  $c = ([regex]::Matches($t, [regex]::Escape($k))).Count
  Write-Host ("  {0,-22} {1}" -f $k, $(if ($c) { "present x$c" } else { 'ABSENT' }))
}
Write-Host ''
Write-Host '=== routes and verbs it registers ==='
$lines = $t -split "`r?`n"
for ($i = 0; $i -lt $lines.Count; $i++) {
  $l = $lines[$i]
  if ($l -match 'createServer|req\.method|req\.url|\.on\(') {
    Write-Host ("  L{0,-4} {1}" -f ($i + 1), $l.Trim().Substring(0, [Math]::Min(118, $l.Trim().Length)))
  }
}
Write-Host ''
Write-Host '=== the first 25 non-comment, non-blank lines ==='
$n = 0
foreach ($l in $lines) {
  $s = $l.Trim()
  if (-not $s) { continue }
  if ($s.StartsWith('//') -or $s.StartsWith('/*') -or $s.StartsWith('*')) { continue }
  Write-Host ("  " + $s.Substring(0, [Math]::Min(118, $s.Length)))
  $n++
  if ($n -ge 25) { break }
}
