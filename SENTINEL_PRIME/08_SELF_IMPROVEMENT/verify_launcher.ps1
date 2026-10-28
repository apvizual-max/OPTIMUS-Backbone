<#
  SENTINEL Command Center - launcher self-test.

  Written 2026-10-04 after the launcher shipped with two defects that a
  "does the file exist" check would never have found:

    * `try/catch/else` is not valid PowerShell. The bad statement sat in the
      `stop` branch, so `start` and `status` worked and only `stop`/`restart`
      failed. The file parses, so a syntax audit of the whole script would not
      have caught it either - only running every verb does.
    * `Start-Process -PassThru` with redirection leaves a .NET Process object
      holding handles tied to a child that keeps running, so the launcher could
      block on exit.

  The test therefore runs EVERY verb, from a known-down state, and checks the
  exit code as well as the port.

  HOW TO RUN A VERB WITHOUT THE PIPE ARTIFACT
  --------------------------------------------
  Do NOT measure the launcher with `& powershell ... | Out-String`. The server
  inherits the write end of that pipe, so the pipeline never reaches EOF and the
  measurement hangs forever even though the launcher exited normally. That cost
  a full debugging cycle chasing a "hang" that did not exist. Each verb below
  is therefore launched with Start-Process -Wait and its own log files - the
  instrument must not be able to hold the target's output.

  Run:  powershell -NoProfile -ExecutionPolicy Bypass -File verify_launcher.ps1
#>
[CmdletBinding()]
param([int]$Port = 8910)

$ErrorActionPreference = 'Stop'
$LAUNCHER = Join-Path $PSScriptRoot '..\13_COMMAND_CENTER\api\sentinel-cc.ps1'
$LOGDIR = Join-Path $PSScriptRoot '..\09_LOGS\launcher_selftest'
if (-not (Test-Path $LOGDIR)) { New-Item -ItemType Directory -Path $LOGDIR -Force | Out-Null }

$script:results = @()

function Invoke-Verb {
  param([string]$Verb)
  $out = Join-Path $LOGDIR "$Verb.out.log"
  $err = Join-Path $LOGDIR "$Verb.err.log"
  $sw = [Diagnostics.Stopwatch]::StartNew()
  # NOT -Wait. PowerShell's Start-Process -Wait waits for the whole process TREE,
  # and `start` launches a server that runs forever, so -Wait never returns and
  # the test hangs on a launcher that has already exited correctly. Process
  # objects are a trap here in two directions: piping stdout lets the server
  # inherit the pipe write-end and the reader never sees EOF; -Wait waits for
  # descendants. WaitForExit() on the object itself waits for that one process.
  $p = Start-Process -FilePath 'powershell' `
       -ArgumentList '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $LAUNCHER, $Verb, '-Port', $Port `
       -PassThru -WindowStyle Hidden `
       -RedirectStandardOutput $out -RedirectStandardError $err
  # Cache the handle before waiting. Without this, ExitCode reads back as
  # $null once the process is gone and the whole run reports FAIL on a launcher
  # that behaved correctly - 6 of 16 assertions, every one of them this.
  $null = $p.Handle
  if (-not $p.WaitForExit(120000)) {
    $sw.Stop()
    try { $p.Kill() } catch { }
    return [pscustomobject]@{
      Verb = $Verb; Exit = -1; Ms = $sw.ElapsedMilliseconds
      Out = (Get-Content $out -Raw -ErrorAction SilentlyContinue)
      Err = 'TIMED OUT after 120s - the launcher did not exit'
    }
  }
  $sw.Stop()
  return [pscustomobject]@{
    Verb = $Verb; Exit = $p.ExitCode; Ms = $sw.ElapsedMilliseconds
    Out = (Get-Content $out -Raw -ErrorAction SilentlyContinue)
    Err = (Get-Content $err -Raw -ErrorAction SilentlyContinue)
  }
}

function Test-Port {
  try {
    $c = New-Object Net.Sockets.TcpClient
    $iar = $c.BeginConnect('127.0.0.1', $Port, $null, $null)
    $ok = $iar.AsyncWaitHandle.WaitOne(800, $false)
    if ($ok) { $c.EndConnect($iar) }
    $c.Close(); return $ok
  } catch { return $false }
}

function Assert-That {
  param([string]$Label, [bool]$Ok, [string]$Detail = '')
  $script:results += [pscustomobject]@{ Label = $Label; Ok = $Ok; Detail = $Detail }
  $mark = if ($Ok) { 'PASS' } else { 'FAIL' }
  Write-Host ("  [{0}] {1}{2}" -f $mark, $Label, $(if ($Detail) { "  ($Detail)" } else { '' }))
}

Write-Host ''
Write-Host '  LAUNCHER SELF-TEST - every verb, from a known-down state' -ForegroundColor Cyan
Write-Host '  ' + ('-' * 62)

# 0. Known-down start point. A test that cannot fail is not a test.
$r = Invoke-Verb 'stop'
Start-Sleep -Seconds 2
Assert-That 'server is down before the cycle' (-not (Test-Port)) 'port 8910'

$r = Invoke-Verb 'status'
Assert-That 'status when down exits 1' ($r.Exit -ne 0) "exit=$($r.Exit) $($r.Ms)ms"
Assert-That 'status does not claim a live port' ($r.Out -notmatch 'LISTENING') ''

$r = Invoke-Verb 'start'
Assert-That 'start exits 0' ($r.Exit -eq 0) "exit=$($r.Exit) $($r.Ms)ms"
Assert-That 'the port really answers after start' (Test-Port) 'probed independently of the launcher'
Assert-That 'start reports no stderr' (-not ($r.Err -and $r.Err.Trim())) ''

$r = Invoke-Verb 'start'
Assert-That 'start is idempotent (2nd call exits 0)' ($r.Exit -eq 0) "exit=$($r.Exit)"
Assert-That '2nd start did not start a second server' ($r.Out -match 'Already listening') ''

$r = Invoke-Verb 'status'
Assert-That 'status when up exits 0' ($r.Exit -eq 0) "exit=$($r.Exit) $($r.Ms)ms"
Assert-That 'status reports LISTENING' ($r.Out -match 'LISTENING') ''

$r = Invoke-Verb 'stop'
Assert-That 'stop exits 0' ($r.Exit -eq 0) "exit=$($r.Exit) $($r.Ms)ms"
Assert-That 'stop actually closed the port' (-not (Test-Port)) 'probed independently'

$r = Invoke-Verb 'restart'
Assert-That 'restart exits 0' ($r.Exit -eq 0) "exit=$($r.Exit) $($r.Ms)ms"
Assert-That 'the port answers after restart' (Test-Port) ''

$r = Invoke-Verb 'status'
Assert-That 'status after restart exits 0' ($r.Exit -eq 0) "exit=$($r.Exit) $($r.Ms)ms"
Assert-That 'no verb wrote to stderr' (-not ($r.Err -and $r.Err.Trim())) ''

$failed = @($script:results | Where-Object { -not $_.Ok })
Write-Host '  ' + ('-' * 62)
Write-Host ("  {0}/{1} assertions passed" -f ($script:results.Count - $failed.Count), $script:results.Count)
Write-Host ("  server left RUNNING on port {0} for use" -f $Port)
Write-Host ''
if ($failed.Count -gt 0) { exit 1 }
exit 0
