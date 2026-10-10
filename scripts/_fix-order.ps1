$ErrorActionPreference = 'Stop'
$f = 'C:\Users\apviz\.minimax-agent\projects\90_CONTROL_CENTER\index.html'
$lines = [System.Collections.ArrayList]@([IO.File]::ReadAllLines($f, [Text.Encoding]::UTF8))

# The two replaces are in the wrong order. A U+FFFD encoded as cp1252 arrives
# as THREE characters (U+00EF U+00BF U+00BD), so a U+FFFD matcher misses it.
# The decode must run first and PRODUCE a real U+FFFD; only then is it replaced.
# Reversed, the mojibake survives pass one and becomes the very character pass
# two already ran past - which is why the fix looked applied and was not.
$swap = -1
for ($i = 0; $i -lt $lines.Count; $i++) {
  if ($lines[$i] -match '\.replace\(/\\uFFFD/g') { $swap = $i; break }
}
if ($swap -lt 0) { throw 'the U+FFFD replace was not found' }
$decodeLine = $swap + 1
if ($lines[$decodeLine] -notmatch '\\u00E0-\\u00FF') { throw "expected the decode replace on line $($decodeLine + 1)" }
$udc = $lines[$swap]        # .replace(/\uFFFD/g,'-')
$dec = $lines[$decodeLine]   # .replace(/[\u00E0-\u00FF].../g,

# reorder, and re-indent to match
$lines[$swap]        = $dec
$lines[$decodeLine] = $udc

# comment above them
$note = [string[]]@(
'    // ORDER MATTERS, and backwards is why this did not work. A U+FFFD encoded',
'    // as cp1252 arrives as THREE characters (U+00EF U+00BF U+00BD), so a U+FFFD',
'    // matcher alone misses it. The decode runs FIRST and produces a real U+FFFD;',
'    // only then is that replaced. Reversed, the mojibake survives pass one and',
'    // becomes the very character pass two already ran past. Found by asking',
'    // /api/ask a real question and reading the answer.'
)
for ($k = 0; $k -lt $note.Count; $k++) { $lines.Insert($swap - 3 + $k, $note[$k]) }

[IO.File]::WriteAllLines($f, $lines.ToArray(), (New-Object Text.UTF8Encoding($false)))
Write-Host 'reordered the two replaces; decode now runs first'
for ($i = $swap - 4; $i -lt $swap + 3; $i++) { if ($i -ge 0) { Write-Host ("  {0,5}: {1}" -f ($i + 1), $lines[$i]) } }
