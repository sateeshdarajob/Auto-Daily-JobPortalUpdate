# foundit_upload.py v3 -- Cookie-based login
#
# First time: python foundit_upload.py --setup
# Every run:  python foundit_upload.py

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv
import os, time, sys
from datetime import datetime

load_dotenv(r"C:\JobAutomation\.env")
RESUME      = os.getenv("RESUME_PATH")
LOG_FILE    = r"C:\JobAutomation\log.txt"
LOCK_FILE   = r"C:\JobAutomation\foundit_upload.lock"
COOKIE_FILE = r"C:\JobAutomation\foundit_state.json"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] FOUNDIT: {msg}"
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

def setup_mode():
    print("\n" + "="*55)
    print("  FOUNDIT SETUP -- One-time login to save your session")
    print("="*55)
    print("\nA browser window will open.")
    print("Log into Foundit (email + password + OTP if asked).")
    print("Once you see your Foundit DASHBOARD, come back here")
    print("and press ENTER.\n")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )
        page = context.new_page()
        page.goto("https://www.foundit.in/login")
        print("Waiting for you to log in... (browser is open)")
        input("\n>>> Press ENTER once you are logged in to Foundit dashboard: ")
        context.storage_state(path=COOKIE_FILE)
        print(f"\nSESSION SAVED to: {COOKIE_FILE}")
        print("Now run normally: python C:\\JobAutomation\\foundit_upload.py\n")
        browser.close()

def upload_mode():
    if not os.path.exists(COOKIE_FILE):
        log("ERROR: No saved session. Run: python C:\\JobAutomation\\foundit_upload.py --setup")
        return
    if not acquire_lock():
        sys.exit(0)
    log("Starting Foundit resume upload (saved session)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            storage_state=COOKIE_FILE,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )
        page = context.new_page()
        try:
            log("Going to resume update page...")
            page.goto("https://www.foundit.in/seeker/updateResume", timeout=30000)
            page.wait_for_load_state("domcontentloaded", timeout=20000)
            time.sleep(4)

            if "login" in page.url:
                log("ERROR: Session expired! Run: python C:\\JobAutomation\\foundit_upload.py --setup")
                return
            log(f"Logged in. URL: {page.url}")

            # Find file input and upload
            uploaded = False
            for sel in ["input[type='file']", "input[accept*='pdf']", "input[accept*='doc']"]:
                try:
                    page.wait_for_selector(sel, timeout=8000)
                    page.locator(sel).first.set_input_files(RESUME)
                    log(f"File attached: {sel}")
                    uploaded = True
                    time.sleep(5)
                    break
                except: continue

            if not uploaded:
                log("ERROR: File input not found on Foundit.")
                return

            for sel in ["button:has-text('Upload')", "button:has-text('Save')", "button[type='submit']"]:
                try:
                    page.click(sel, timeout=5000)
                    log(f"Saved: {sel}")
                    time.sleep(3)
                    break
                except: pass

            context.storage_state(path=COOKIE_FILE)
            log("SUCCESS: Foundit resume uploaded + session refreshed!")

        except PlaywrightTimeout as e: log(f"TIMEOUT: {e}")
        except Exception as e: log(f"ERROR: {e}")
        finally:
            browser.close()
            release_lock()

if __name__ == "__main__":
    if "--setup" in sys.argv:
        setup_mode()
    else:
        upload_mode()
