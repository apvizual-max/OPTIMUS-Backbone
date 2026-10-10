@echo off
REM ===========================================================================
REM  optimus.cmd - the single front door for the OPTIMUS ecosystem
REM  Wraps optimus.ps1 so the command is usable from any shell.
REM ===========================================================================
setlocal
set "OPTIMUS_HOME=C:\Users\apviz\.minimax-agent\projects"
powershell -NoProfile -ExecutionPolicy Bypass -File "%OPTIMUS_HOME%\scripts\optimus.ps1" %*
exit /b %ERRORLEVEL%
