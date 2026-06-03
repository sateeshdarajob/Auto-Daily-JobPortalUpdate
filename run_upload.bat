@echo off
echo ========================================
echo Job Portal Automation - %DATE% %TIME%
echo ========================================
echo [1/3] Naukri Resume Upload...
python C:\JobAutomation\naukri_upload.py
echo.
echo [2/3] Foundit Resume Upload...
python C:\JobAutomation\foundit_upload.py
echo.
echo [3/3] Naukri Profile Refresh...
python C:\JobAutomation\naukri_refresh.py
echo.
echo All done! Check C:\JobAutomation\log.txt for results.
