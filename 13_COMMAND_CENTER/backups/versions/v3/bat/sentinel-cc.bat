@echo off
REM ===========================================================================
REM  SENTINEL Command Center - MINIMAX SENTINEL BRAIN
REM  Starts the local server and opens it in the default browser.
REM
REM  A page loaded over file:// cannot reach the API, so live monitoring and the
REM  action buttons both need this local HTTP origin. It binds 127.0.0.1 ONLY
REM  and is never reachable from off-box.
REM
REM  Port 8910. Port 8900 belongs to the separate OPTIMUS Control Center;
REM  the two must never collide.
REM ===========================================================================
setlocal
set "CC=C:\Users\apviz\.minimax-agent\projects\SENTINEL_PRIME\13_COMMAND_CENTER"
set "PORT=8910"

echo.
echo   SENTINEL Command Center - MINIMAX SENTINEL BRAIN
echo   ------------------------------------------------
echo   URL : http://127.0.0.1:%PORT%/
echo   API : http://127.0.0.1:%PORT%/api/state
echo   HLTH : http://127.0.0.1:%PORT%/api/health
echo   loopback only. Close this window to stop.
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%CC%\api\server.ps1" -Port %PORT%
endlocal
