$ErrorActionPreference = 'Continue'
$STAMP = '2026-10-12'
$ROOT  = 'D:\_OPTIMUS-SNAPSHOT\' + $STAMP
New-Item -ItemType Directory -Force -Path $ROOT | Out-Null

$jobs = @(
  @{ src = 'D:\Alex_Knowlege_Vault';                                                     dst = "$ROOT\D-Alex_Knowlege_Vault" },
  @{ src = 'E:\CLAUDE\MINTE\OLD DATA - To Adresss for Integration\- OLD Work Files';    dst = "$ROOT\E-OLD-Work-Files" },
  @{ src = "$env:USERPROFILE\.minimax\vault-manifest\git-parked-2026-10-07";             dst = "$ROOT\git-parked-2026-10-07" }
)

$report = @()
foreach ($j in $jobs) {
  if (-not (Test-Path -LiteralPath $j.src)) {
    $report += "SKIP|$($j.src)|MISSING"
    continue
  }
  $before = (Get-ChildItem -LiteralPath $j.src -Recurse -Force -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum)
  $rc = Start-Process -FilePath 'robocopy.exe' `
        -ArgumentList @("`"$($j.src)`"", "`"$($j.dst)`"", '/E', '/COPY:DAT', '/DCOPY:DAT', '/R:1', '/W:1', '/NFL', '/NDL', '/NP', '/MT:8', '/XJ') `
        -Wait -PassThru -NoNewWindow
  $after = (Get-ChildItem -LiteralPath $j.dst -Recurse -Force -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum)
  $match = if ($before.Count -eq $after.Count) { 'MATCH' } else { 'MISMATCH' }
  $report += ("COPY|$($j.src)|robocopy_rc={0}|srcFiles={1}|dstFiles={2}|srcMB={3:N0}|dstMB={4:N0}|{5}" -f `
              $rc.ExitCode, $before.Count, $after.Count, ($before.Sum/1MB), ($after.Sum/1MB), $match)
}

# ⚡ Bolt: Removed pipeline | ForEach-Object to eliminate overhead
foreach ($line in $report) { Write-Output $line }
# ⚡ Bolt: Removed pipeline | Set-Content and used -Value parameter directly for faster array writing
Set-Content -LiteralPath "$ROOT\SNAPSHOT-REPORT.txt" -Value $report -Encoding UTF8
Write-Output "DONE|root=$ROOT"