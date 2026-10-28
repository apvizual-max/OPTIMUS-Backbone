<#
.SYNOPSIS
  Runs a command string with a hard ceiling, and writes results atomically.

.DESCRIPTION
  Extracted from server.ps1 so that BOTH the request path and a background job
  can use it. A PowerShell scriptblock does not cross into a Start-Job, so
  before this was a file the bounded-run logic existed in one place and the
  action runner had to either duplicate it or give up its timeout. One
  implementation, two callers.

  Two properties matter and are easy to lose in a refactor:

  1. THE CAP. Without it, an action is an unbounded freeze on a
     single-threaded listener. A command that hangs is killed and REPORTED, not
     waited on - an action that times out silently is worse than one that never
     returns, because it looks like it worked.

  2. ATOMIC WRITES. A reader must never see half a result. Write to a temp file
     in the same directory, then move it over the target.

.NOTES
  ASCII-only on purpose. PowerShell 5.1 reads a BOM-less .ps1 as ANSI, so a
  non-ASCII literal written into this file is a parse hazard, not a cosmetic
  one. (This exact failure produced a 33 KB error message of concatenated
  "0.010275..." during the change that created this file.)
#>

# The temp-file helper lives in one canonical place. This file is dot-sourced
# by server.ps1 AND by a Start-Job runspace, and the job needs the same helper,
# so it is loaded here rather than at each call site.
. (Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) 'scripts\lib\mavis-temp.ps1')

function Read-SharedText {
  param([string]$Path)  # NOT [IO.File]::ReadAllText. When a child is KILLED, the redirected handle can
  # still be open, and ReadAllText opens exclusively - so the kill-and-report
  # path threw "being used by another process" instead of reporting the timeout.
  # That path had no runtime coverage at all until this was called directly with
  # a command that outlived its cap, and it failed on the first try. A timeout
  # handler that cannot read the output is not a timeout handler.
  if (-not (Test-Path -LiteralPath $Path)) { return '' }
  try {
    $fs = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
    try {
      $sr = New-Object System.IO.StreamReader($fs, [System.Text.Encoding]::UTF8)
      try { return $sr.ReadToEnd() } finally { $sr.Dispose() }
    } finally { $fs.Dispose() }
  } catch {
    try { return [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8) } catch { return '' }
  }
}

function Invoke-Bounded {
  # The full result: text, exit code, and whether it was killed.
  #
  # Invoke-BoundedCommand below is a thin wrapper over this for callers that
  # only want the text. The split exists because the exit code is REAL
  # information and dropping it is how a caller ends up reporting a healthy
  # result from a command that failed: $LASTEXITCODE is set by the LAST native
  # command in the session, and a bounded run happens in a child process, so
  # after one returns, $LASTEXITCODE describes something else entirely. That
  # bug shipped here first - `compose_valid` started reporting False on a
  # perfectly valid compose file - and it is invisible unless you compare the
  # value before and after the change.
  #
  # Do not try to smuggle the exit code out through the text with
  # `& echo %ERRORLEVEL%`: cmd.exe expands that BEFORE the first command runs,
  # so it reports the inherited value and the check always passes. Delayed
  # expansion (`!ERRORLEVEL!` with /v:on) would work, but the process object
  # already knows the answer, so asking it is both simpler and correct.
  param(
    [Parameter(Mandatory = $true)][string]$Command,
    [int]$TimeoutSec = 120,
    [string]$WorkDir,
    [string]$StdinFile
  )
  $outFile = New-MavisTempFile
  $errFile = New-MavisTempFile
  $timedOut = $false
  $exitCode = $null
  try {
    if (-not $StdinFile) { $StdinFile = New-MavisTempFile }
    if (-not (Test-Path -LiteralPath $StdinFile)) { [IO.File]::WriteAllText($StdinFile, '') }
    # -WorkingDirectory is passed ONLY when non-empty. Start-Process validates
    # that argument and throws on a null or empty string, so an unconditional
    # -WorkingDirectory $WorkDir turns "caller did not care about the folder"
    # into a hard failure. Found by calling this function directly rather than
    # through the server, where the one caller always supplies a value.
    $sp = @{
      FilePath               = 'cmd.exe'
      ArgumentList           = @('/c', $Command)
      RedirectStandardOutput = $outFile
      RedirectStandardError  = $errFile
      RedirectStandardInput  = $StdinFile
      WindowStyle            = 'Hidden'
      PassThru               = $true
    }
    if ($WorkDir -and (Test-Path -LiteralPath $WorkDir)) { $sp['WorkingDirectory'] = $WorkDir }
    $cp = Start-Process @sp
    # Cache the handle BEFORE waiting. .NET only exposes ExitCode on a Process
    # whose handle it still holds; without this touch the property comes back
    # $null after the process exits, and every caller that trusted it saw an
    # empty exit code rather than an error. Measured: 5 of 5 non-timeout cases
    # returned $null until this line was added.
    $null = $cp.Handle
    if (-not $cp.WaitForExit(($TimeoutSec * 1000))) {
      # taskkill /T, NOT $cp.Kill(). Killing cmd.exe does not kill what cmd.exe
      # started: measured, a timed-out `cmd /c ping` left the ping.exe running
      # after the wrapper died. A timeout that orphans the work it was meant to
      # stop has not stopped anything.
      $killer = Start-Process -FilePath 'taskkill.exe' `
        -ArgumentList '/PID', $cp.Id, '/T', '/F' -WindowStyle Hidden -PassThru -EA SilentlyContinue
      if ($killer) { try { $null = $killer.WaitForExit(10000) } catch { } }
      try { $cp.Kill() } catch { }
      try { $null = $cp.WaitForExit(5000) } catch { }
      $timedOut = $true
    }
    $text = Read-SharedText -Path $outFile
    $errText = Read-SharedText -Path $errFile
    if ($errText.Trim()) { $text = $text.TrimEnd() + "`n[stderr] " + $errText.Trim() }
    if ($timedOut) {
      $text = $text.TrimEnd() + "`n[TIMED OUT after ${TimeoutSec}s] the command was killed. Nothing else on this console was affected."
    } else {
      try { $exitCode = $cp.ExitCode } catch { $exitCode = $null }
    }
    return [pscustomobject]@{ Text = $text; ExitCode = $exitCode; TimedOut = $timedOut }
  } finally {
    foreach ($f in @($outFile, $errFile)) { try { if (Test-Path $f) { Remove-Item -LiteralPath $f -Force -ErrorAction SilentlyContinue } } catch { } }
  }
}

function Invoke-BoundedCommand {
  param(
    [Parameter(Mandatory = $true)][string]$Command,
    [int]$TimeoutSec = 120,
    [string]$WorkDir,
    [string]$StdinFile
  )
  return (Invoke-Bounded -Command $Command -TimeoutSec $TimeoutSec -WorkDir $WorkDir -StdinFile $StdinFile).Text
}

function Write-AtomicJson {
  param(
    [Parameter(Mandatory = $true)][string]$Path,
    [Parameter(Mandatory = $true)]$Value,
    [int]$Depth = 8
  )
  # [IO.File]::Replace, not Move-Item -Force. The replace is the atomic primitive
  # on Windows and it refuses to clobber a target it did not create in this
  # operation, whereas Move-Item -Force has silently copied over a live file in
  # enough ways to be worth avoiding on a path a poller is reading. The fallback
  # exists for the volume types that do not support Replace.
  $tmp = "$Path.$PID.tmp"
  [System.IO.File]::WriteAllText($tmp, ($Value | ConvertTo-Json -Depth $Depth -Compress), (New-Object System.Text.UTF8Encoding($false)))
  try { [System.IO.File]::Replace($tmp, $Path, $null, $true) }
  catch { Move-Item -LiteralPath $tmp -Destination $Path -Force }
}
