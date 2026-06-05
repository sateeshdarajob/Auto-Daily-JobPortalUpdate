# naukri_refresh.py v3 -- Cookie-based session refresh
# Requires naukri_state.json created by: python naukri_upload.py --setup

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import os, time, sys
from datetime import datetime

LOG_FILE    = r"C:\JobAutomation\log.txt"
LOCK_FILE   = r"C:\JobAutomation\naukri_refresh.lock"
COOKIE_FILE = r"C:\JobAutomation\naukri_state.json"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] REFRESH: {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def acquire_lock():
    if os.path.exists(LOCK_FILE):
        age = time.time() - os.path.getmtime(LOCK_FILE)
        if age < 600:
            log(f"SKIPPED: Lock age {int(age)}s.")
            return False
        log("Stale lock removed.")
    open(LOCK_FILE, "w").close()
    return True

def release_lock():
    try: os.remove(LOCK_FILE)
    except: pass

def run():
    if not os.path.exists(COOKIE_FILE):
        log("ERROR: No saved session. Run: python C:\\JobAutomation\\naukri_upload.py --setup")
        return
    if not acquire_lock():
        sys.exit(0)
    log("Starting Naukri profile refresh...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context(
            storage_state=COOKIE_FILE,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )
        page = context.new_page()
        try:
            page.goto("https://www.naukri.com/mnjuser/profile", timeout=30000)
            page.wait_for_load_state("domcontentloaded", timeout=20000)
            time.sleep(3)
            if "nlogin" in page.url or "login" in page.url:
                log("ERROR: Session expired! Run: python C:\\JobAutomation\\naukri_upload.py --setup")
                return
            # Try clicking Refresh button if present
            for sel in ["button:has-text('Refresh')", "text=Refresh my Profile", "a:has-text('Refresh')"]:
                try:
                    page.click(sel, timeout=3000)
                    log(f"Clicked refresh: {sel}")
                    time.sleep(2)
                    break
                except: pass
            # Save refreshed cookies
            context.storage_state(path=COOKIE_FILE)
            log("SUCCESS: Profile active timestamp updated!")
        except PlaywrightTimeout as e: log(f"TIMEOUT: {e}")
        except Exception as e: log(f"ERROR: {e}")
        finally:
            browser.close()
            release_lock()

if __name__ == "__main__":
    run()
