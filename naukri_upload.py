# naukri_upload.py — FINAL CLEAN VERSION
#
# FIRST TIME ONLY:  python naukri_upload.py --setup
#   Opens browser, you log in + complete OTP, press Enter → session saved.
#
# EVERY DAY (automated):  python naukri_upload.py
#   Uses saved session, runs headless, uploads resume silently.
#
# SESSION EXPIRED?  Just re-run --setup (every 30-90 days).

import os, sys, time
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from dotenv import load_dotenv

load_dotenv(r"C:\JobAutomation\.env")
RESUME      = os.getenv("RESUME_PATH")
LOG_FILE    = r"C:\JobAutomation\log.txt"
LOCK_FILE   = r"C:\JobAutomation\naukri_upload.lock"
COOKIE_FILE = r"C:\JobAutomation\naukri_state.json"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def log(msg):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] NAUKRI: {msg}"
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


# ── SETUP: run once, log in manually ────────────────────────────
def setup():
    print("\n[ NAUKRI SETUP ]\nA browser will open. Log in normally (email/OTP/password).")
    print("Once you reach your Naukri homepage, press Enter here.\n")
    with sync_playwright() as p:
        ctx = p.chromium.launch(headless=False).new_context(user_agent=UA, viewport={"width":1280,"height":800})
        pg  = ctx.new_page()
        pg.goto("https://www.naukri.com/nlogin/login")
        input(">>> Press Enter when fully logged in: ")
        ctx.storage_state(path=COOKIE_FILE)
        print(f"Session saved → {COOKIE_FILE}")
        print("Run normally: python C:\\JobAutomation\\naukri_upload.py\n")
        ctx.browser.close()


# ── UPLOAD: uses saved session every time ────────────────────────
def upload():
    if not os.path.exists(COOKIE_FILE):
        log("No session file. Run: python naukri_upload.py --setup"); return
    if not lock(): sys.exit(0)

    log("Starting upload (saved session)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx     = browser.new_context(storage_state=COOKIE_FILE, user_agent=UA, viewport={"width":1280,"height":800})
        pg      = ctx.new_page()
        try:
            # 1. Open profile page — no login needed
            pg.goto("https://www.naukri.com/mnjuser/profile", timeout=30000)
            pg.wait_for_load_state("domcontentloaded"); time.sleep(3)

            if "login" in pg.url.lower():
                log("Session expired. Run: python naukri_upload.py --setup"); return
            log(f"Loaded: {pg.url}")

            # 2. Close any popup
            for s in ["[class*='close']","button:has-text('Maybe Later')","button:has-text('Skip')"]:
                try: pg.click(s, timeout=1500)
                except: pass

            # 3. Scroll to resume section
            pg.evaluate("window.scrollTo(0,600)"); time.sleep(2)

            # 4. Intercept file chooser BEFORE clicking Update Resume
            #    This is the key fix — handles the native Windows file dialog.
            log(f"Uploading: {RESUME}")
            with pg.expect_file_chooser(timeout=12000) as fc:
                # Try each possible button text
                clicked = False
                for btn in ["text=Update Resume","text=Add Resume","text=Upload Resume",
                            "button:has-text('Resume')","[class*='widgetHead'] button"]:
                    try: pg.click(btn, timeout=4000); clicked = True; break
                    except: continue
                if not clicked:
                    log("ERROR: Could not find the Update Resume button."); return
            fc.value.set_files(RESUME)
            log("File handed to browser.")
            time.sleep(5)

            # 5. Click Save if present
            for s in ["button:has-text('Save')","button:has-text('Upload')","button[type='submit']"]:
                try: pg.click(s, timeout=5000); log(f"Clicked: {s}"); time.sleep(3); break
                except: pass

            # 6. Save refreshed cookies
            ctx.storage_state(path=COOKIE_FILE)
            log("SUCCESS: Resume uploaded and session refreshed.")

        except PWTimeout as e: log(f"TIMEOUT: {e}")
        except Exception as e: log(f"ERROR: {e}")
        finally: browser.close(); unlock()


if __name__ == "__main__":
    setup() if "--setup" in sys.argv else upload()
