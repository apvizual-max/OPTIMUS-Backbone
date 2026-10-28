$ErrorActionPreference = 'Stop'
$f = 'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\90_CONTROL_CENTER\index.html'
$lines = [System.Collections.ArrayList]@([IO.File]::ReadAllLines($f, [Text.Encoding]::UTF8))

# Identify the stale line by its CONTENT: it contains the cp1252 rendering of
# U+FFFD (U+00EF U+00BF U+00BD) as a literal. Matching on the characters rather
# than on a line number is the only reliable way, because the previous splice was
# off by one and the surrounding lines have already moved.
$bad = [string]([char]0x00EF) + [char]0x00BF + [char]0x00BD
$removed = 0
for ($i = $lines.Count - 1; $i -ge 0; $i--) {
  if ($lines[$i].Contains($bad)) {
    Write-Host ("  removing line {0}: {1}" -f ($i + 1), $lines[$i].Trim())
    $lines.RemoveAt($i); $removed++
  }
}
if ($removed -eq 0) { Write-Host "  nothing to remove" }
[IO.File]::WriteAllLines($f, $lines.ToArray(), (New-Object Text.UTF8Encoding($false)))
Write-Host ("  removed {0} line(s)" -f $removed)
