# naukri_upload.py v3 -- Cookie-based login (no CAPTCHA issues)
#
# HOW IT WORKS:
#   First time only:  python naukri_upload.py --setup
#     Opens a VISIBLE browser, you log in manually, cookies are saved.
#   Every run after:  python naukri_upload.py
#     Uses saved cookies, runs invisibly. No login prompt ever.
#
# If cookies expire (30-90 days), just run --setup again.

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv
import os, time, sys
from datetime import datetime

load_dotenv(r"C:\JobAutomation\.env")
RESUME      = os.getenv("RESUME_PATH")
LOG_FILE    = r"C:\JobAutomation\log.txt"
LOCK_FILE   = r"C:\JobAutomation\naukri_upload.lock"
COOKIE_FILE = r"C:\JobAutomation\naukri_state.json"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] NAUKRI: {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def acquire_lock():
    if os.path.exists(LOCK_FILE):
        age = time.time() - os.path.getmtime(LOCK_FILE)
        if age < 600:
            log(f"SKIPPED: Another instance running (lock age {int(age)}s).")
            return False
        log("Stale lock removed.")
    open(LOCK_FILE, "w").close()
    return True

def release_lock():
    try: os.remove(LOCK_FILE)
    except: pass

# -------------------------------------------------------
# SETUP MODE: run once to save your login session
# -------------------------------------------------------
def setup_mode():
    print("\n" + "="*55)
    print("  NAUKRI SETUP -- One-time login to save your session")
    print("="*55)
    print("\nA browser window will open.")
    print("Log into Naukri normally (email + password + OTP if asked).")
    print("Once you see your Naukri DASHBOARD, come back here")
    print("and press ENTER to save your session.\n")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )
        page = context.new_page()
        page.goto("https://www.naukri.com/nlogin/login")
        print("Waiting for you to log in... (browser is now open)")
        input("\n>>> Press ENTER once you are on the Naukri dashboard: ")
        if "nlogin" in page.url or "login" in page.url:
            print("\nWARNING: Still looks like the login page.")
            print("Make sure you are fully logged in, then press ENTER again.")
            input(">>> Press ENTER to save anyway: ")
        context.storage_state(path=COOKIE_FILE)
        print(f"\nSESSION SAVED to: {COOKIE_FILE}")
        print("Now run normally: python C:\\JobAutomation\\naukri_upload.py\n")
        browser.close()

# -------------------------------------------------------
# UPLOAD MODE: uses saved cookies, fully headless
# -------------------------------------------------------
def upload_mode():
    if not os.path.exists(COOKIE_FILE):
        log("ERROR: No saved session found. Run setup first:")
        log("  python C:\\JobAutomation\\naukri_upload.py --setup")
        return
    if not acquire_lock():
        sys.exit(0)
    log("Starting Naukri resume upload (saved session)...")
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
            log("Opening profile page (no login needed)...")
            page.goto("https://www.naukri.com/mnjuser/profile", timeout=30000)
            page.wait_for_load_state("domcontentloaded", timeout=20000)
            time.sleep(4)

            # Check session expired
            if "nlogin" in page.url or "login" in page.url:
                log("ERROR: Session expired! Re-run setup:")
                log("  python C:\\JobAutomation\\naukri_upload.py --setup")
                return
            log(f"Logged in. URL: {page.url}")

            # Dismiss popups
            for sel in ["[class*='close']", "button:has-text('Maybe Later')", "button:has-text('Skip')"]:
                try: page.click(sel, timeout=2000)
                except: pass

            # Scroll to resume section and click Update button
            page.evaluate("window.scrollTo(0, 500)")
            time.sleep(2)

            for btn in ["text=Update Resume", "text=Add Resume", "text=Upload Resume",
                        "button:has-text('Resume')", "[class*='resumeHead'] button"]:
                try:
                    page.click(btn, timeout=3000)
                    log(f"Clicked resume button: {btn}")
                    time.sleep(2)
                    break
                except: pass

            # Find file input and upload
            uploaded = False
            for sel in ["input[type='file']", "input[accept*='.doc']",
                        "input[accept*='pdf']", "#attachCV", "input[name='resume']"]:
                try:
                    page.wait_for_selector(sel, timeout=8000, state="attached")
                    page.locator(sel).first.set_input_files(RESUME)
                    log(f"Resume attached: {sel}")
                    uploaded = True
                    time.sleep(5)
                    break
                except: continue

            if not uploaded:
                log("ERROR: Could not find file input. Saving cookies for next run.")
                context.storage_state(path=COOKIE_FILE)
                return

            # Click Save
            for sel in ["button:has-text('Save')", "button:has-text('Upload')", ".saveBtn"]:
                try:
                    page.click(sel, timeout=5000)
                    log(f"Clicked save: {sel}")
                    time.sleep(3)
                    break
                except: pass

            # Refresh and save cookies for next run
            context.storage_state(path=COOKIE_FILE)
            log("SUCCESS: Naukri resume uploaded + session refreshed!")

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
