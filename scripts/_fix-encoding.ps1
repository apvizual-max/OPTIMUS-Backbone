# Repairs the mojibake I introduced into index.html. Uses the SAME targeted
# algorithm as scripts\repair-mojibake.ps1 (which handles .md only), applied
# repeatedly because three Get-Content -Raw / WriteAllText round-trips
# triple-encoded the file.
#
# Rules honoured, and they are the reason this is not a global re-decode:
#   - read/write as explicit UTF-8, never Get-Content -Raw
#   - repair ONLY runs of cp1252 high-range chars that decode to valid UTF-8
#   - leave every correctly-encoded character untouched
#   - loop only while it keeps improving, so it cannot run away
$ErrorActionPreference = 'Stop'
$file = 'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\90_CONTROL_CENTER\index.html'
$utf8 = [Text.Encoding]::UTF8
$cp1252 = [Text.Encoding]::GetEncoding(1252)
$REPL = [string][char]0xFFFD

$hi = @()
for ($b = 0x80; $b -le 0xFF; $b++) {
  $ch = $cp1252.GetString([byte[]]$b)
  if ($ch.Length -eq 1) { $hi += [regex]::Escape($ch) }
}
$RUN = [regex](('[' + ($hi -join '') + ']') + '{2,3}')

function Repair-Text([string]$s) {
  $sb = New-Object Text.StringBuilder
  $pos = 0
  foreach ($m in $RUN.Matches($s)) {
    if ($m.Index -gt $pos) { [void]$sb.Append($s.Substring($pos, $m.Index - $pos)) }
    $run = $m.Value
    $dec = $utf8.GetString($cp1252.GetBytes($run))
    if (($dec -notmatch [regex]::Escape($REPL)) -and ($dec.Length -lt $run.Length)) { [void]$sb.Append($dec) }
    else { [void]$sb.Append($run) }
    $pos = $m.Index + $run.Length
  }
  if ($pos -lt $s.Length) { [void]$sb.Append($s.Substring($pos)) }
  $sb.ToString()
}
function Count-Moj([string]$s) {
  $n = 0
  foreach ($m in $RUN.Matches($s)) {
    $d = $utf8.GetString($cp1252.GetBytes($m.Value))
    if (($d -notmatch [regex]::Escape($REPL)) -and ($d.Length -lt $m.Value.Length)) { $n++ }
  }
  $n
}

$text = [IO.File]::ReadAllText($file, $utf8)
$start = Count-Moj $text
Write-Host ("before      : {0} repairable runs, {1:N0} bytes" -f $start, (Get-Item $file).Length)

for ($pass = 1; $pass -le 6; $pass++) {
  $b = Count-Moj $text
  if ($b -eq 0) { Write-Host ("pass {0}     : already clean" -f $pass); break }
  $text = Repair-Text $text
  $a = Count-Moj $text
  Write-Host ("pass {0}     : {1} -> {2}" -f $pass, $b, $a)
  if ($a -ge $b) { Write-Host "  no further improvement - stopping" -Break; break }
}

$final = Count-Moj $text
$fffdBefore = ([regex]::Matches([IO.File]::ReadAllText($file, $utf8), [regex]::Escape($REPL))).Count
$fffdAfter  = ([regex]::Matches($text, [regex]::Escape($REPL))).Count
Write-Host ""
Write-Host ("final       : {0} runs, {1} U+FFFD (was {2})" -f $final, $fffdAfter, $fffdBefore)

if ($final -eq 0 -and $fffdAfter -le $fffdBefore) {
  [IO.File]::WriteAllText($file, $text, (New-Object Text.UTF8Encoding($false)))
  Write-Host ("WRITTEN     : {0:N0} bytes" -f (Get-Item $file).Length) -ForegroundColor Green
} else {
  Write-Host "NOT WRITTEN - repair did not reach zero" -ForegroundColor Red
}
