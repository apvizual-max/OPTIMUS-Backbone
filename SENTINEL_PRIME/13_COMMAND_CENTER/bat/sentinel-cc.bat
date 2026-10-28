@echo off
REM ===========================================================================
REM  SENTINEL Command Center - manual launcher for BOTH planes
REM
REM  Double-click to bring the whole deployment up and open it.
REM
REM  REWRITTEN 2026-10-09. This file used to call sentinel-cc.ps1 with
REM  -Port 8910. That was correct when the Command Center was a single
REM  Windows server. It is not correct now, and the README had already
REM  stopped recommending it:
REM
REM    8910  FRONT   the container mavis-sentinel-hub (nginx). Bookmarked URL.
REM    8912  BACKEND a Windows PowerShell HttpListener. Owns every measurement.
REM
REM  THREE failure modes were measured on this path, not reasoned about.
REM
REM  1. SILENT FAILURE. With the container up and the backend down,
REM     sentinel-cc.ps1 saw 8910 already listening - the CONTAINER was
REM     listening - declared victory, exited 0, and opened a browser on a
REM     page that could only ever return 502. The operator was told "UP".
REM
REM  2. PORT HIJACK. With the container down, nothing listened on 8910, so it
REM     started server.ps1 -Port 8910: the backend squatting the front port.
REM     8910 then kept answering 200 after the container was gone, and every
REM     "is the link up" probe said yes. This is the exact fault already
REM     documented in anger at sentinel-hub.ps1, which now hunts for and kills
REM     such strays on `stop`.
REM
REM  3. AN EXIT CODE A SIGNED COMPARISON CANNOT SEE. When
REM     `powershell.exe -File <missing script>` fails, it prints the argument error
REM     and exits with code -196608. Measured on this machine, and the number is the
REM     point: `if errorlevel 1` is a SIGNED greater-or-equal test, and -196608 is not
REM     greater than 1, so the gate passes silently and the launcher reports success
REM     having started nothing. A failure code that far into the negative is the worst
REM     possible input to that construct - it is not a value anyone would think to test
REM     for. So a missing, renamed or unrunnable hub script - the single most likely
REM     reason a double-click produces nothing - walked straight past the gate that
REM     existed to report it.
REM
REM  The fix is not a different port number, and it is not a better exit code.
REM  It is two changes:
REM    (a) delegate to the script that already knows both planes exist -
REM        sentinel-hub.ps1 starts the backend on 8912, starts the container,
REM        waits for /healthz and /readyz to agree, and names WHICH plane is
REM        missing when it does not come up;
REM    (b) MEASURE success instead of inferring it. After the start, this file
REM        asks the front plane a real question - does /readyz answer 200? -
REM        and only opens the browser if it does. The probe exits 1 on any
REM        failure, so its own exit code means something.
REM
REM  A page loaded over file:// cannot reach the API, so live monitoring and
REM  the action buttons both need this local HTTP origin. Both planes bind
REM  127.0.0.1 ONLY and are never reachable from off-box.
REM
REM  Port 8900/8901 belongs to the separate OPTIMUS Control Center. This file
REM  never reads, writes or stops it.
REM ===========================================================================
setlocal
set "HUB=C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\SENTINEL_PRIME\13_COMMAND_CENTER\api\sentinel-hub.ps1"
set "API=C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\SENTINEL_PRIME\13_COMMAND_CENTER\api"
set "FRONT=8910"
set "BACK=8912"

echo.
echo   SENTINEL Command Center - MINIMAX SENTINEL BRAIN
echo   ------------------------------------------------
echo   front    http://127.0.0.1:%FRONT%/   container
echo   backend  http://127.0.0.1:%BACK%/   data plane
echo   both loopback only.
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%HUB%" -Action start -FrontPort %FRONT% -BackPort %BACK%

echo.
echo   Verifying the deployment actually serves ...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:%FRONT%/readyz' -UseBasicParsing -TimeoutSec 15; $d = $r.Headers['X-SENTINEL-Deployment']; if ($r.StatusCode -eq 200) { Write-Output ('  readyz  OK    served by: ' + $d); exit 0 } } catch { Write-Output ('  readyz  FAIL  ' + $_.Exception.Message) }; exit 1"
if errorlevel 1 goto DEAD

echo.
echo   Opening http://127.0.0.1:%FRONT%/ ...
start "" "http://127.0.0.1:%FRONT%/"
echo.
echo   Both planes run in the background and survive this window closing.
echo   To stop them:  powershell -NoProfile -ExecutionPolicy Bypass -File "%HUB%" -Action stop
echo.
timeout /t 4 /nobreak >nul 2>&1
endlocal
exit /b 0

:DEAD
echo.
echo   NOT SERVING. The start step did not produce a working deployment,
echo   so the browser was NOT opened - an unmeasured success would be a lie.
echo.
echo   Full diagnosis of both planes:
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%HUB%" -Action status
echo.
echo   Container log:   powershell -NoProfile -ExecutionPolicy Bypass -File "%HUB%" -Action logs
echo   Backend stderr:  %API%\sentinel-cc.err.log
echo.
pause
endlocal
exit /b 1