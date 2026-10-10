$ErrorActionPreference = 'Stop'
$f = 'C:\Users\apviz\.minimax-agent\projects\90_CONTROL_CENTER\index.html'
$lines = [System.Collections.ArrayList]@([IO.File]::ReadAllLines($f, [Text.Encoding]::UTF8))

# The self-test block was inserted where the FABRIC section comment began, so the
# comment's opening delimiter was consumed and its body was left dangling as
# code. Re-open the comment immediately before that orphaned text, matched by
# its content rather than a line number.
$marker = 'The system as a graph, not a list. Borrowed in spirit from the Qwen'
$at = -1
for ($i = 0; $i -lt $lines.Count; $i++) {
  if ($lines[$i].Trim().StartsWith($marker)) { $at = $i; break }
}
if ($at -lt 0) { throw 'orphaned comment body not found' }
Write-Host ("re-opening the FABRIC section comment before line {0}" -f ($at + 1))
# the opener has to be its own line, with the body continuing underneath it
$opener = '/* ================================ FABRIC ================================='
# walk back to the end of the preceding line so the body sits inside the comment
$lines.Insert($at, $opener)
# the line before must be indented as a comment body line; give the opener and
# the first body line matching indentation
$lines[$at + 1] = '   ' + $lines[$at + 1].TrimStart()

[IO.File]::WriteAllLines($f, $lines.ToArray(), (New-Object Text.UTF8Encoding($false)))
for ($i = $at - 1; $i -lt $at + 3; $i++) { if ($i -ge 0) { Write-Host ("  {0,5}: {1}" -f ($i + 1), $lines[$i]) } }
