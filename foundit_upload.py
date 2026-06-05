# foundit_upload.py — FINAL CLEAN VERSION
#
# FIRST TIME ONLY:  python foundit_upload.py --setup
# EVERY DAY:        python foundit_upload.py

import os, sys, time
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from dotenv import load_dotenv

load_dotenv(r"C:\JobAutomation\.env")
RESUME      = os.getenv("RESUME_PATH")
LOG_FILE    = r"C:\JobAutomation\log.txt"
LOCK_FILE   = r"C:\JobAutomation\foundit_upload.lock"
COOKIE_FILE = r"C:\JobAutomation\foundit_state.json"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def log(msg):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] FOUNDIT: {msg}"
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


def setup():
    print("\n[ FOUNDIT SETUP ]\nA browser will open. Log in normally.")
    print("Once you reach your Foundit homepage, press Enter here.\n")
    with sync_playwright() as p:
        ctx = p.chromium.launch(headless=False).new_context(user_agent=UA, viewport={"width":1280,"height":800})
        pg  = ctx.new_page()
        pg.goto("https://www.foundit.in/login")
        input(">>> Press Enter when fully logged in: ")
        ctx.storage_state(path=COOKIE_FILE)
        print(f"Session saved → {COOKIE_FILE}")
        print("Run normally: python C:\\JobAutomation\\foundit_upload.py\n")
        ctx.browser.close()


def upload():
    if not os.path.exists(COOKIE_FILE):
        log("No session file. Run: python foundit_upload.py --setup"); return
    if not lock(): sys.exit(0)

    log("Starting upload (saved session)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx     = browser.new_context(storage_state=COOKIE_FILE, user_agent=UA, viewport={"width":1280,"height":800})
        pg      = ctx.new_page()
        try:
            pg.goto("https://www.foundit.in/seeker/updateResume", timeout=30000)
            pg.wait_for_load_state("domcontentloaded"); time.sleep(3)

            if "login" in pg.url.lower():
                log("Session expired. Run: python foundit_upload.py --setup"); return
            log(f"Loaded: {pg.url}")

            # Close any popup
            for s in ["[class*='close']","button:has-text('Skip')"]:
                try: pg.click(s, timeout=1500)
                except: pass

            log(f"Uploading: {RESUME}")

            # Try file chooser interception first (for button-triggered dialogs)
            try:
                with pg.expect_file_chooser(timeout=8000) as fc:
                    for btn in ["button:has-text('Upload')", "button:has-text('Update')",
                                "text=Upload Resume", "label[for*='resume']"]:
                        try: pg.click(btn, timeout=3000); break
                        except: continue
                fc.value.set_files(RESUME)
                log("File uploaded via file chooser.")
            except:
                # Fallback: direct DOM file input
                fi = pg.locator("input[type='file']").first
                fi.set_input_files(RESUME)
                log("File uploaded via direct input.")

            time.sleep(5)

            for s in ["button:has-text('Save')","button:has-text('Upload')","button[type='submit']"]:
                try: pg.click(s, timeout=5000); log(f"Clicked: {s}"); time.sleep(3); break
                except: pass

            ctx.storage_state(path=COOKIE_FILE)
            log("SUCCESS: Foundit resume uploaded and session refreshed.")

        except PWTimeout as e: log(f"TIMEOUT: {e}")
        except Exception as e: log(f"ERROR: {e}")
        finally: browser.close(); unlock()


if __name__ == "__main__":
    setup() if "--setup" in sys.argv else upload()
