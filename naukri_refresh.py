# naukri_refresh.py — FINAL CLEAN VERSION
# Updates your Naukri "last active" timestamp (shows recruiters "Active Today")
# Uses the same saved session as naukri_upload.py

import os, sys, time
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

LOG_FILE    = r"C:\JobAutomation\log.txt"
LOCK_FILE   = r"C:\JobAutomation\naukri_refresh.lock"
COOKIE_FILE = r"C:\JobAutomation\naukri_state.json"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def log(msg):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] REFRESH: {msg}"
    print(line)
    open(LOG_FILE, "a", encoding="utf-8").write(line + "\n")

def lock():
    if os.path.exists(LOCK_FILE):
        if time.time() - os.path.getmtime(LOCK_FILE) < 600:
            log("SKIPPED: Already running."); return False
    open(LOCK_FILE, "w").close(); return True

def unlock():
    try: os.remove(LOCK_FILE)
    except: pass


def run():
    if not os.path.exists(COOKIE_FILE):
        log("No session file. Run: python naukri_upload.py --setup"); return
    if not lock(): sys.exit(0)

    log("Refreshing profile activity...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx     = browser.new_context(storage_state=COOKIE_FILE, user_agent=UA, viewport={"width":1280,"height":800})
        pg      = ctx.new_page()
        try:
            pg.goto("https://www.naukri.com/mnjuser/profile", timeout=30000)
            pg.wait_for_load_state("domcontentloaded"); time.sleep(3)

            if "login" in pg.url.lower():
                log("Session expired. Run: python naukri_upload.py --setup"); return

            # Try Refresh button if present
            for s in ["button:has-text('Refresh')","text=Refresh my Profile","a:has-text('Refresh')"]:
                try: pg.click(s, timeout=3000); log(f"Clicked: {s}"); time.sleep(2); break
                except: pass

            ctx.storage_state(path=COOKIE_FILE)
            log("SUCCESS: Profile active timestamp updated.")

        except PWTimeout as e: log(f"TIMEOUT: {e}")
        except Exception as e: log(f"ERROR: {e}")
        finally: browser.close(); unlock()


if __name__ == "__main__":
    run()
