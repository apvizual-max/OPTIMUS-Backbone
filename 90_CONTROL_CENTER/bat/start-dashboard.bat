@echo off
REM ===========================================================================
REM  MiniMax OPTIMUS Control Center
REM  Starts the local dashboard server and opens it in the default browser.
REM
REM  A file:// page cannot execute PowerShell, so live monitoring and the
REM  command buttons both need this local HTTP origin. It binds 127.0.0.1
REM  ONLY -- never reachable from off-box.
REM ===========================================================================
setlocal
set "CC=C:\Users\apviz\.minimax-agent\projects\90_CONTROL_CENTER"
set "PORT=8900"

echo.
echo   MiniMax OPTIMUS Control Center
echo   ---------------------------------------------
echo   URL  : http://127.0.0.1:%PORT%/
echo   API  : http://127.0.0.1:%PORT%/api/state
echo   loopback only. Close this window to stop.
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%CC%\api\server.ps1" -Port %PORT%
endlocal
