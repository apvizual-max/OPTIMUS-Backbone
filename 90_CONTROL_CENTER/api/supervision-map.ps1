# Get-SupervisionMap - who actually supervises each of these ports?
#
# Dot-source this, then call:
#     . $path
#     $map = Get-SupervisionMap @(8082, 3001, 8765, 8910, 8912)
#
# WHY IT IS BUILT LIKE THIS
# MEASURED: Get-NetTCPConnection takes 4681 ms PER CALL on this machine. The
# first version asked it once per port and added ~30 s to a collector that ran
# in 33 s - pure waiting, not work. It also returned EMPTY under the collector
# while working standalone, which is the worst combination: slow and wrong.
#
# So: three lookups, each done exactly once, then every question is a hashtable
# hit.
#     1. netstat -ano      -> which pid owns each listening port
#     2. docker ps        -> which container publishes it, and its restart policy
#     3. Win32_Process    -> for a host process, is its parent still alive?
#
# The third is the question that actually matters. A container with
# unless-stopped is supervised by Docker. A bare python.exe or powershell.exe is
# supervised by nothing but its parent - and a process whose parent has EXITED
# has no supervisor at all, whatever else is true about it. That distinction was
# missing entirely, and it is the one that decides whether a service comes back.

function Get-SupervisionMap {
  param([int[]]$Ports)

  $ErrorActionPreference = 'Continue'

  # 1. one netstat
  $listener = @{}
  foreach ($ln in @(& netstat.exe -ano 2>$null)) {
    if ($ln -notmatch '^\s*TCP\s+(\S+):(\d+)\s+\S+\s+LISTENING\s+(\d+)\s*$') { continue }
    $p = [int]$Matches[2]
    if ($Ports -contains $p -and -not $listener.ContainsKey($p)) { $listener[$p] = [int]$Matches[3] }
  }

  # 2. one docker ps, and inspect ONLY the containers that publish our ports.
  #    Inspecting all 63 costs ~15 s by itself.
  $relev = @{}
  foreach ($ln in @(& docker.exe ps --format '{{.Names}}|{{.Ports}}' 2>$null)) {
    $parts = $ln -split '\|'
    foreach ($m in [regex]::Matches($parts[1], ':(\d+)->')) {
      $p = [int]$m.Groups[1].Value
      if ($Ports -contains $p -and -not $relev.ContainsKey($p)) { $relev[$p] = $parts[0] }
    }
  }
  $container = @{}
  foreach ($p in $relev.Keys) {
    $n = $relev[$p]
    $rp = & docker.exe inspect $n --format '{{.HostConfig.RestartPolicy.Name}}' 2>$null
    $container[$p] = [ordered]@{ Name = $n; Restart = if ($rp) { [string]$rp } else { 'unknown' } }
  }

  # 3. one process table
  $procs = @{}
  foreach ($q in @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue)) {
    $procs[[int]$q.ProcessId] = [pscustomobject]@{
      Name = $q.Name; PPid = [int]$q.ParentProcessId; Cmd = [string]$q.CommandLine
    }
  }

  $map = @{}
  foreach ($p in $Ports) {
    $rec = [ordered]@{
      port = $p; kind = 'none'; owner = 'nothing is listening'
      restart = 'n/a'; parent_alive = $null; supervised = $false; note = ''
    }
    if ($container.ContainsKey($p)) {
      $c = $container[$p]
      $rec.kind = 'docker'; $rec.owner = $c.Name; $rec.restart = $c.Restart
      $rec.supervised = ($c.Restart -ne 'no' -and $c.Restart -ne 'unknown')
      $rec.note = "container restart policy = $($c.Restart)"
    }
    elseif ($listener.ContainsKey($p)) {
      $op = $listener[$p]
      $proc = $procs[$op]

      # A port owned by pid 4 (System) is an HTTP.sys front, not the application.
      # netstat then reports the KERNEL as the owner, which would print
      # "System / orphaned" for a service that is really a PowerShell process -
      # a new false claim in the same shape as the old one. So resolve the real
      # process out of HTTP.sys before judging it.
      #
      # Order matters, and getting it wrong is how the first attempt picked up
      # WebManagement.exe: `netsh http show servicestate` prints
      #     ID: <pid>, image: <exe>          <- the real process
      #     Registered URLs:
      #         HTTP://127.0.0.1:<port>...   <- the URL it serves
      # The ID comes BEFORE the URL. Matching the URL first and taking the next
      # ID grabs the following service block instead.
      $viaHttpSys = $false
      $realPid = $null
      if ($op -eq 4) {
        $pending = $null
        foreach ($sl in @(& netsh.exe http show servicestate 2>$null)) {
          if ($sl -match 'ID:\s*(\d+),\s*image:\s*(.+?)\s*$') { $pending = [int]$Matches[1]; continue }
          # The URL is printed as HTTP://127.0.0.1:<port>:<bindhost>/ , so the
          # port is followed by ':' - not by '/' or end of line. Match the
          # delimiter, not the tail.
          if ($pending -ne $null -and $sl -match "127\.0\.0\.1:$p(?=[:/\s]|$)") {
            $realPid = $pending; $pending = $null; break
          }
        }
        if ($realPid -ne $null -and $procs.ContainsKey($realPid)) { $proc = $procs[$realPid]; $viaHttpSys = $true }
      }

      $rec.kind = if ($viaHttpSys) { 'host (HTTP.sys)' } else { 'host' }
      $rec.owner = if ($proc) { $proc.Name } else { "pid $op" }
      $pp = if ($proc) { $proc.PPid } else { 0 }
      $rec.parent_alive = ($pp -ne 0 -and $procs.ContainsKey($pp))
      $rec.supervised = [bool]$rec.parent_alive
      $rec.restart = if ($rec.parent_alive) { 'inherited from parent' } else { 'NONE - orphaned' }
      $rec.note = if ($viaHttpSys) {
        if ($rec.parent_alive) { "HTTP.sys fronts pid $realPid ($($proc.Name)); its parent pid $pp is alive" }
        else { "HTTP.sys fronts pid $realPid ($($proc.Name)); its parent has EXITED" }
      } else {
        if ($rec.parent_alive) { "parent pid $pp is alive" } else { 'its parent has EXITED' }
      }
      # A dead parent proves the process is DETACHED. It does not prove that
      # nothing restarts it - and I asserted exactly that, wrongly. The SENTINEL
      # hub log showed 13 startup invocations and 8 distinct backend pids in
      # four hours, so something plainly does bring it back. The honest claim is
      # the one I measured: no parent, and no supervisor found in the four
      # watchdogs or the task scheduler. Whether some other path revives it is
      # not something this probe can see, and saying it is would be a guess
      # dressed as a finding.
      if (-not $rec.parent_alive) {
        $rec.note += ' - detached: no parent, and no supervisor found in the task scheduler or the running watchdogs'
      }
      if ($proc -and $proc.Cmd) {
        $c = ($proc.Cmd -replace '\s+', ' ')
        $rec.note += ' - ' + $c.Substring(0, [Math]::Min(88, $c.Length))
      }
    }
    $map[$p] = $rec
  }
  return $map
}
