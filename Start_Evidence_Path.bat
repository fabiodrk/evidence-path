@echo off
setlocal
cd /d "%~dp0"
py -3 --version >nul 2>&1
if %errorlevel% equ 0 (
  py -3 launch.py
) else (
  python launch.py
)
if errorlevel 1 pause
endlocal
