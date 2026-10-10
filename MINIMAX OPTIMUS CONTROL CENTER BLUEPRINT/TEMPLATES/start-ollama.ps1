# start-ollama.ps1 - single-instance guard for the local Ollama server.
#
# WHY THIS EXISTS
# The Ollama_Server logon task ran `ollama.exe serve` directly. When an Ollama
# instance was ALREADY listening on 127.0.0.1:11434, the task's process died
# with:
#
#   Error: listen tcp 127.0.0.1:11434: bind: Only one usage of each socket
#   address (protocol/network address/port) is normally permitted.
#
# repeated dozens of times, and the task recorded LastTaskResult = 1. So the task
# was not "failing to start Ollama" - it was fighting a healthy Ollama, and when
# the instance it could not displace finally died, nothing took over. Ollama is
# down right now because the task had no way to notice it was redundant, and no
# second way to bring the service back.
#
# This wrapper makes the start IDEMPOTENT, which is what a "start the service"
# task has to be:
#   - already answering  -> exit 0, do not touch anything
#   - nothing listening   -> start it, wait for it to answer, then exit 0
#   - started but silent -> exit 1 so the task's own restart policy applies
#
# It does NOT kill anything. A server that is up and answering is correct
# behaviour, and the only previous failure came from starting a duplicate.

[CmdletBinding()]
param(
  [int]$Port = 11434,
  [int]$WaitSeconds = 45
)

$ErrorActionPreference = 'Stop'

function Test-Answering {
  param([int]$OnPort)
  try {
    $c = New-Object Net.Sockets.TcpClient
    $iar = $c.BeginConnect('127.0.0.1', $OnPort, $null, $null)
    $ok = $iar.AsyncWaitHandle.WaitOne(1500, $false)
    if ($ok) { $c.EndConnect($iar) }
    $c.Close()
    return $ok
  } catch { return $false }
}

# 1. Already serving? Nothing to do, and that is success.
if (Test-Answering -OnPort $Port) {
  Write-Host "Ollama already answering on 127.0.0.1:$Port - not starting a second instance."
  exit 0
}

# 2. Nothing there. Start it.
$exe = Join-Path $env:LOCALAPPDATA 'Programs\Ollama\ollama.exe'
if (-not (Test-Path -LiteralPath $exe)) {
  Write-Host "No Ollama binary at $exe - the machine-wide install has not been done."
  exit 1
}

$logDir = Join-Path $env:LOCALAPPDATA 'Ollama'
if (-not (Test-Path -LiteralPath $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

Write-Host "Starting Ollama serve on 127.0.0.1:$Port ..."
$p = Start-Process -FilePath $exe -ArgumentList 'serve' -WindowStyle Hidden -PassThru `
       -RedirectStandardOutput (Join-Path $logDir 'server.log') `
       -RedirectStandardError  (Join-Path $logDir 'server.err.log')
# Release the handle so ExitCode is readable later, per the usual trap.
$null = $p.Handle

# 3. Wait for it to actually answer - starting is not serving.
$deadline = (Get-Date).AddSeconds($WaitSeconds)
while ((Get-Date) -lt $deadline) {
  Start-Sleep -Seconds 2
  if (Test-Answering -OnPort $Port) {
    Write-Host "Ollama is answering on 127.0.0.1:$Port."
    exit 0
  }
  if ($p.HasExited) {
    Write-Host "Ollama exited immediately with code $($p.ExitCode). See $logDir\server.err.log"
    exit 1
  }
}

Write-Host "Started pid $($p.Id) but it did not answer within $WaitSeconds s. Not reporting success."
exit 1