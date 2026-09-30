@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Aetherion-License-Manager.ps1"
if errorlevel 1 pause
