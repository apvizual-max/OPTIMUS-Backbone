$ErrorActionPreference = 'Stop'
$f = 'C:\Users\apviz\.minimax-agent\projects\90_CONTROL_CENTER\index.html'
$lines = [System.Collections.ArrayList]@([IO.File]::ReadAllLines($f, [Text.Encoding]::UTF8))

# locate the block by its anchors rather than by reproducing the exact bytes,
# because the block contains the very characters that are hard to type
$start = -1; $end = -1
for ($i = 0; $i -lt $lines.Count; $i++) {
  if ($start -lt 0 -and $lines[$i] -match 'const clean = s => String') { $start = $i }
  if ($start -ge 0 -and $lines[$i] -match '^\s*out\.textContent = clean\(out\.textContent\);') { $end = $i; break }
}
if ($start -lt 0 -or $end -lt 0) { throw "anchor not found (start=$start end=$end)" }
Write-Host ("replacing lines {0}..{1}" -f ($start + 1), ($end + 1))

# Pure-ASCII replacement. Every non-ASCII character is written as a \u escape,
# because a literal Latin-1 character in a character class gets re-encoded on
# the way into this file - which is the exact defect being fixed.
$new = [string[]]@(
'    // Written in pure ASCII on purpose. A character class spanning Latin-1 MUST',
'    // be written with \u escapes: typing the literal characters into this file',
'    // re-encodes them on the way in, reintroducing the very mojibake this exists',
'    // to remove. The first version of this fix did precisely that and failed the',
'    // very check it had just written. Range E0-FF covers the leading byte of a',
'    // mis-decoded 2- or 3-byte UTF-8 run.',
'    const clean = s => String(s==null?'''':s)',
'      .replace(/�/g,''-'')',
'      .replace(/[\u00E0-\u00FF][\u0080-\u00BF][\u0080-\u00BF]?/g,',
'               m => { try{ return decodeURIComponent(escape(m)); }catch(e){ return m; } });',
'    out.textContent = clean(out.textContent);'
)
# the U+FFFD literal is also expressed as an escape, for the same reason
$new[6] = '      .replace(/\uFFFD/g,''-'')'

for ($i = $end; $i -ge $start; $i--) { $lines.RemoveAt($i) }
for ($j = 0; $j -lt $new.Count; $j++) { $lines.Insert($start + $j, $new[$j]) }

[IO.File]::WriteAllLines($f, $lines.ToArray(), (New-Object Text.UTF8Encoding($false)))
Write-Host ("index.html now {0:N0} bytes" -f (Get-Item $f).Length)
Write-Host "block replaced"
