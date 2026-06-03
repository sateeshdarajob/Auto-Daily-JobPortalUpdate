# Auto-Daily-JobPortalUpdate

Automated daily resume upload to **Naukri** and **Foundit** job portals using Python + Playwright.
Runs **twice daily** (8 AM & 6 PM) via Windows Task Scheduler — fully hands-free.

## Files

| File | Purpose |
|------|---------|
| `naukri_upload.py` | Logs into Naukri and uploads your resume |
| `foundit_upload.py` | Logs into Foundit and uploads your resume |
| `naukri_refresh.py` | Refreshes Naukri profile to show "Active Today" |
| `run_upload.bat` | Runs all 3 scripts in sequence (Task Scheduler calls this) |
| `SETUP_INSTRUCTIONS.txt` | Quick start guide |
| `Job_Portal_Automation_Guide.md` | Full step-by-step setup guide |

## Quick Start

1. Copy all files to `C:\JobAutomation\`
2. Create `C:\JobAutomation\.env` with your credentials
3. Run `pip install playwright python-dotenv && playwright install chromium`
4. Test: `python naukri_upload.py`
5. Schedule `run_upload.bat` in Windows Task Scheduler (8 AM + 6 PM)

## Requirements
- Python 3.8+
- playwright
- python-dotenv

## Author
Sateesh Kumar Dara
