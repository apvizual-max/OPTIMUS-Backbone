@echo off
REM ===========================================================================
REM  guard-compose.bat
REM
REM  WHY THIS EXISTS
REM  On 2026-10-02 C:\Users\apviz\docker-compose.yml was found DELETED, leaving 18
REM  running containers as orphans with no definition on disk. A prune, a Docker
REM  restart, or `compose up --remove-orphans` would have destroyed load-bearing
REM  services with no way to recreate them.
REM
REM  WHAT IT DOES
REM  1. Proves docker-compose.yml exists.
REM  2. Proves it still parses (docker compose config).
REM  3. If it is MISSING, rebuilds it from live container state.
REM  4. Keeps a dated backup of every good copy it sees.
REM
REM  Safe to run any time. It never stops or recreates a container.
REM ===========================================================================
setlocal
set "COMPOSE=C:\Users\apviz\docker-compose.yml"
set "GUARD=C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\90_CONTROL_CENTER\api\guard-compose.ps1"

powershell -NoProfile -ExecutionPolicy Bypass -File "%GUARD%"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo   RESULT: compose file is present and valid.
) else (
  echo   RESULT: PROBLEM DETECTED - see above.
)
echo.
pause
endlocal
