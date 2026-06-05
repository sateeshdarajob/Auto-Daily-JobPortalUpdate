@echo off
setlocal

echo ================================================
echo  Job Portal Automation - %DATE% %TIME%
echo ================================================

REM Check if already running (master lock)
if exist "C:\JobAutomation\master.lock" (
    for /f %%i in ('powershell -command "(Get-Date) - (Get-Item C:\JobAutomation\master.lock).LastWriteTime | Select-Object -ExpandProperty TotalMinutes"') do set AGE=%%i
    echo Lock age: %AGE% minutes
    if %AGE% LSS 15 (
        echo SKIPPED: Already running. Exiting.
        exit /b 0
    )
    echo Removing stale master lock.
    del "C:\JobAutomation\master.lock"
)

REM Create master lock
echo %DATE% %TIME% > "C:\JobAutomation\master.lock"

echo.
echo [1/3] Naukri Resume Upload...
python C:\JobAutomation\naukri_upload.py
echo Naukri done. Waiting 10 seconds...
timeout /t 10 /nobreak > nul

echo.
echo [2/3] Foundit Resume Upload...
python C:\JobAutomation\foundit_upload.py
echo Foundit done. Waiting 10 seconds...
timeout /t 10 /nobreak > nul

echo.
echo [3/3] Naukri Profile Refresh...
python C:\JobAutomation\naukri_refresh.py

echo.
echo ================================================
echo  All done! Check C:\JobAutomation\log.txt
echo ================================================

REM Remove master lock
del "C:\JobAutomation\master.lock"
