# foundit_upload.py — FINAL CLEAN VERSION
#
# FIRST TIME ONLY:  python foundit_upload.py --setup
# DEBUG (see what's on page): python foundit_upload.py --debug
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
DEBUG_SS    = r"C:\JobAutomation\foundit_debug.png"

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


# -- SETUP --------------------------------------------------------
def setup():
    print("\n[ FOUNDIT SETUP ]\nA browser will open. Log in normally.")
    print("Once you reach your Foundit homepage, press Enter here.\n")
    with sync_playwright() as p:
        ctx = p.chromium.launch(headless=False).new_context(user_agent=UA, viewport={"width":1280,"height":800})
        pg  = ctx.new_page()
        pg.goto("https://www.foundit.in/")
        input(">>> Press Enter when fully logged in: ")
        ctx.storage_state(path=COOKIE_FILE)
        print(f"Session saved -> {COOKIE_FILE}")
        print("Run normally: python C:\\JobAutomation\\foundit_upload.py\n")
        ctx.browser.close()


# -- UPLOAD -------------------------------------------------------
def upload(debug=False):
    if not os.path.exists(COOKIE_FILE):
        log("No session file. Run: python foundit_upload.py --setup"); return
    if not debug and not lock(): sys.exit(0)

    log("Starting upload (saved session)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx     = browser.new_context(storage_state=COOKIE_FILE, user_agent=UA, viewport={"width":1280,"height":800})
        pg      = ctx.new_page()
        try:
            # Go STRAIGHT to the seeker profile page -- this is where the resume
            # upload control actually lives. The homepage ("/") has NO resume input,
            # which is why every previous run timed out.
            pg.goto("https://www.foundit.in/seeker/profile", timeout=45000)
            pg.wait_for_load_state("domcontentloaded"); time.sleep(3)

            if "login" in pg.url.lower() or "register" in pg.url.lower():
                log("Session expired. Run: python foundit_upload.py --setup"); return
            log(f"Profile page: {pg.url}")

            # Dismiss cookie consent + any popups
            for s in ["button:has-text('Okay')", "button:has-text('Got it')",
                      "button:has-text('Skip')", "[class*='close']", "[aria-label='close']"]:
                try: pg.click(s, timeout=1500)
                except: pass

            if debug:
                pg.screenshot(path=DEBUG_SS, full_page=True)
                log(f"Screenshot saved: {DEBUG_SS}")

            log(f"Uploading: {RESUME}")

            # The page contains a hidden <input name="resume" type="file"
            # accept="doc,docx,rtf,pdf">. Playwright can set files on a hidden
            # input directly (no click / native dialog needed) -- most reliable.
            uploaded = False
            try:
                fi = pg.locator("input[name='resume']")
                fi.wait_for(state="attached", timeout=20000)
                fi.set_input_files(RESUME)
                log("File set on hidden input[name=resume].")
                uploaded = True
            except Exception as e:
                log(f"Direct input[name=resume] failed: {e}")

            # Fallback 1: click 'Replace resume' / 'Upload Resume' and catch the file chooser
            if not uploaded:
                try:
                    with pg.expect_file_chooser(timeout=10000) as fc:
                        for btn in ["button:has-text('Replace resume')",
                                    "text=Upload Resume", "text=Update Resume"]:
                            try: pg.click(btn, timeout=3000); log(f"Clicked: {btn}"); break
                            except: continue
                    fc.value.set_files(RESUME)
                    log("File handed via file chooser.")
                    uploaded = True
                except Exception as e:
                    log(f"File chooser fallback failed: {e}")

            # Fallback 2: any other file input on the page
            if not uploaded:
                try:
                    pg.locator("input[type='file']").first.set_input_files(RESUME)
                    log("File set via input[type=file].")
                    uploaded = True
                except Exception as e:
                    log(f"input[type=file] fallback failed: {e}")

            if not uploaded:
                log("ERROR: Could not find any resume upload element on Foundit profile page.")
                if debug:
                    pg.screenshot(path=DEBUG_SS, full_page=True)
                    log(f"Debug screenshot saved: {DEBUG_SS}")
                return

            # Let the upload process
            time.sleep(6)

            # Confirm/Save if a dialog appears (e.g. "Replace resume?")
            for s in ["button:has-text('Save')", "button:has-text('Confirm')",
                      "button:has-text('Upload')", "button:has-text('Yes')",
                      "button[type='submit']"]:
                try: pg.click(s, timeout=4000); log(f"Confirmed via: {s}"); time.sleep(3); break
                except: pass

            if debug:
                pg.screenshot(path=DEBUG_SS, full_page=True)
                log(f"Final screenshot saved: {DEBUG_SS}")

            ctx.storage_state(path=COOKIE_FILE)
            log("SUCCESS: Foundit resume uploaded and session refreshed.")

        except PWTimeout as e: log(f"TIMEOUT: {e}")
        except Exception as e: log(f"ERROR: {e}")
        finally:
            browser.close()
            if not debug: unlock()


if __name__ == "__main__":
    if "--setup" in sys.argv:
        setup()
    elif "--debug" in sys.argv:
        upload(debug=True)
    else:
        upload()
