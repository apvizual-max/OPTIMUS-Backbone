$ErrorActionPreference = 'Continue'
$q    = 'C:\Users\apviz\.minimax-agent\projects'
$docs = Join-Path $q 'FULL_BACKUP_2026-10-04_QUARANTINE\_DOCS'
New-Item -ItemType Directory -Force -Path (Join-Path $docs '03_TREES') | Out-Null

$script:out = New-Object System.Collections.ArrayList
$script:skip = 'FULL_BACKUP*'

function Walk([string]$dir, [int]$depth, [string]$pre) {
  if ($depth -gt 3) { return }
  $items = @(Get-ChildItem -LiteralPath $dir -Force -EA SilentlyContinue |
             Where-Object { $_.Name -notlike $script:skip } |
             Sort-Object @{e={$_.PSIsContainer};Descending=$true}, Name)
  foreach ($i in $items) {
    if ($i.LinkType) {
      [void]$script:out.Add($pre + $i.Name + '  ->  ' + ($i.Target -join '') + '   [JUNCTION, not followed]')
    }
    elseif ($i.PSIsContainer) {
      $n = @(Get-ChildItem -LiteralPath $i.FullName -Recurse -File -Force -EA SilentlyContinue).Count
      [void]$script:out.Add($pre + $i.Name + '/    (' + $n + ' files)')
      Walk $i.FullName ($depth + 1) ($pre + '  ')
    } else {
      [void]$script:out.Add($pre + $i.Name)
    }
  }
}

[void]$script:out.Add('# 03 - FILE TREE')
[void]$script:out.Add('')
[void]$script:out.Add('Generated: ' + (Get-Date).ToString('yyyy-MM-dd HH:mm:ss zzz'))
[void]$script:out.Add('')
[void]$script:out.Add('Root: `' + $q + '`')
[void]$script:out.Add('')
[void]$script:out.Add('Depth limited to 4 levels. Junctions are shown with their target and NOT')
[void]$script:out.Add('followed - they point outside this root and are recreated as junctions in')
[void]$script:out.Add('the backup, with targets recorded in BACKUP-MANIFEST.json.')
[void]$script:out.Add('')
[void]$script:out.Add('```')
Walk $q 0 ''
[void]$script:out.Add('```')

[IO.File]::WriteAllLines((Join-Path $docs '03_TREES\FILE_TREE.md'), $script:out, (New-Object Text.UTF8Encoding($false)))
Write-Host ('FILE_TREE.md: {0} lines' -f $script:out.Count)
