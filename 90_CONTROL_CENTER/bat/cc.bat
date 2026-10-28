@echo off
REM ===========================================================================
REM  Control Center command bar.
REM  Every action the dashboard can take, also runnable directly.
REM
REM  Usage:  cc <command>
REM  Example: cc status
REM ===========================================================================
setlocal
set "OPTIMUS=C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\scripts\optimus.cmd"
set "OPTIMUS_ROOT=C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard"
set "CC=C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\90_CONTROL_CENTER"
set "CMD=%~1"

if "%CMD%"=="" goto :help

if /i "%CMD%"=="start"    goto :start
if /i "%CMD%"=="guard"    goto :guard
if /i "%CMD%"=="status"   goto :status
if /i "%CMD%"=="doctor"   goto :doctor
if /i "%CMD%"=="census"   goto :census
if /i "%CMD%"=="bridge"   goto :bridge
if /i "%CMD%"=="sot"      goto :sot
if /i "%CMD%"=="skills"   goto :skills
if /i "%CMD%"=="qwen"     goto :qwen
if /i "%CMD%"=="compose"  goto :compose
if /i "%CMD%"=="ai"       goto :ai
if /i "%CMD%"=="refresh"  goto :refresh
if /i "%CMD%"=="selftest" goto :selftest
if /i "%CMD%"=="watchdog" goto :watchdog
if /i "%CMD%"=="install"  goto :install
if /i "%CMD%"=="uninstall" goto :uninstall
if /i "%CMD%"=="health"   goto :health
goto :unknown

:start
  echo Starting the Control Center at http://127.0.0.1:8900/ ...
  start "" "%CC%\bat\start-dashboard.bat"
  goto :done

:guard
  call "%CC%\bat\guard-compose.bat"
  goto :done

:status
  "%OPTIMUS%" status
  goto :done

:doctor
  "%OPTIMUS%" doctor --deep
  goto :done

:census
  "%OPTIMUS%" docker census
  goto :done

:bridge
  "%OPTIMUS%" bridge %2 %3 %4
  goto :done

:sot
  "%OPTIMUS%" sot %2
  goto :done

:skills
  "%OPTIMUS%" skills list
  goto :done

:qwen
  "%OPTIMUS%" qwen %2
  goto :done

:compose
  docker compose -f C:\Users\apviz\docker-compose.yml config --quiet
  echo compose exit=%ERRORLEVEL%
  goto :done

:ai
  "%OPTIMUS%" ai %2 %3
  goto :done

:refresh
  echo Rebuilding the SOT index ...
  "%OPTIMUS%" sot build
  goto :done

:selftest
  REM Parses the page's inline script, checks for mojibake, confirms the icon
  REM font is local, and proves the API and supervisor answer. A JS parse error
  REM kills the whole page while it still renders and the console stays silent,
  REM so this asserts EFFECTS rather than the absence of errors.
  powershell -NoProfile -ExecutionPolicy Bypass -File "%OPTIMUS_ROOT%\scripts\verify-ui.ps1"
  exit /b %ERRORLEVEL%

:watchdog
  REM The supervisor. Without it the server is a console window: close it, or
  REM let it crash, and the dashboard is simply gone with nothing reporting it.
  echo Starting the Control Center supervisor. It checks every 30s and restarts
  echo the server if it stops serving fresh state. Close this window to stop it.
  powershell -NoProfile -ExecutionPolicy Bypass -File "%OPTIMUS_ROOT%\scripts\cc-watchdog.ps1"
  goto :done

:health
  powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "try{ $h=(Invoke-WebRequest 'http://127.0.0.1:8900/api/health' -UseBasicParsing -TimeoutSec 20).Content | ConvertFrom-Json; ^
       if($h.supervised){ Write-Host ('supervised: ' + $(if($h.supervisor.healthy){'HEALTHY'}else{'UNHEALTHY'}) + '  restarts=' + $h.supervisor.restarts); exit $(if($h.supervisor.healthy){0}else{1}) } ^
       else { Write-Host 'NOT SUPERVISED - nothing will restart this if it dies' -ForegroundColor Yellow; exit 2 } } ^
     catch { Write-Host 'Control Center is not answering on 8900' -ForegroundColor Red; exit 3 }"
  goto :done

:install
  REM Register a logon task so the supervisor comes back after a reboot. The
  REM supervisor is a process; nothing restarts a process when Windows starts.
  echo Registering the logon task ...
  powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$a=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File \"C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\scripts\cc-watchdog.ps1\"'; ^
     $t=New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME; ^
     Register-ScheduledTask -TaskName 'OPTIMUS_ControlCenter' -Action $a -Trigger $t -Description 'Keeps the OPTIMUS Control Center alive. Checks every 30s and restarts it if it stops serving fresh state.' -Force | Out-Null; ^
     Write-Host '  installed: OPTIMUS_ControlCenter (runs at logon)' -ForegroundColor Green"
  goto :done

:uninstall
  powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "Unregister-ScheduledTask -TaskName 'OPTIMUS_ControlCenter' -Confirm:$false -ErrorAction SilentlyContinue; ^
     Write-Host '  removed the logon task. The running supervisor is untouched.'"
  goto :done

:unknown
  echo Unknown command: %CMD%
  goto :help

:help
  echo.
  echo   OPTIMUS Control Center - command bar
  echo   ---------------------------------------
  echo   cc start            open the dashboard
  echo   cc selftest         prove the page parses, is clean, and is served
  echo   cc watchdog         run the self-healing supervisor (keeps it alive)
  echo   cc install          register the supervisor to start at logon
  echo   cc health           is it supervised, and how many restarts
  echo   cc guard            check/repair docker-compose.yml
  echo   cc status           one-screen system status
  echo   cc doctor           deep health check
  echo   cc census           container counts
  echo   cc bridge health    both bridges
  echo   cc sot list         show the SOT links
  echo   cc refresh          rebuild the SOT index
  echo   cc skills           list Mavis skills
  echo   cc qwen status      Qwen diagnosis
  echo   cc compose          validate docker-compose.yml
  echo   cc ai auth          MiniMax CLI auth
  echo.
  echo   Or just use:  optimus ^<command^>
  echo.

:done
endlocal
