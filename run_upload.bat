@echo off
setlocal enabledelayedexpansion
echo ============================================
echo  Job Portal Automation  %DATE% %TIME%
echo ============================================

REM Master lock: skip if already running
if exist "C:\JobAutomation\master.lock" (
    for /f %%i in ('powershell -command "(New-TimeSpan -Start (Get-Item C:\JobAutomation\master.lock).LastWriteTime -End (Get-Date)).TotalMinutes"') do set AGE=%%i
    if !AGE! LSS 15 (
        echo SKIPPED: Already running. Exiting.
        exit /b 0
    )
    del "C:\JobAutomation\master.lock"
)
echo. > "C:\JobAutomation\master.lock"

echo.
echo [1/3] Naukri Resume Upload...
python C:\JobAutomation\naukri_upload.py
timeout /t 10 /nobreak > nul

echo.
echo [2/3] Foundit Resume Upload...
python C:\JobAutomation\foundit_upload.py
timeout /t 10 /nobreak > nul

echo.
echo [3/3] Naukri Profile Refresh...
python C:\JobAutomation\naukri_refresh.py

del "C:\JobAutomation\master.lock"
echo.
echo Done! Check C:\JobAutomation\log.txt for results.
