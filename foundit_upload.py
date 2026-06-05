# foundit_upload.py — ROBUST VERSION
#
# FIRST TIME ONLY:  python foundit_upload.py --setup
# DEBUG (watch it):  python foundit_upload.py --debug
# EVERY DAY:         python foundit_upload.py
#
# Runs a VISIBLE browser (Foundit does not render the resume widget for
# headless/automated browsers), waits for the page to settle, and retries
# with reloads until the resume input appears. Never raises — all errors
# are logged.

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
PROFILE_URL = "https://www.foundit.in/seeker/profile"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
ARGS = ["--no-sandbox", "--disable-dev-shm-usage", "--disable-blink-features=AutomationControlled"]


def log(msg):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] FOUNDIT: {msg}"
    print(line)
    try: open(LOG_FILE, "a", encoding="utf-8").write(line + "\n")
    except Exception: pass


def lock():
    if os.path.exists(LOCK_FILE):
        if time.time() - os.path.getmtime(LOCK_FILE) < 600:
            log("SKIPPED: Already running."); return False
    try: open(LOCK_FILE, "w").close()
    except Exception: pass
    return True


def unlock():
    try: os.remove(LOCK_FILE)
    except Exception: pass


def _dismiss(pg):
    for s in ["button:has-text('Okay')", "button:has-text('Got it')",
              "button:has-text('Skip')", "[class*='close']", "[aria-label='close']"]:
        try: pg.click(s, timeout=1200)
        except Exception: pass


# -- SETUP --------------------------------------------------------
def setup():
    print("\n[ FOUNDIT SETUP ]\nA browser will open. Log in normally.")
    print("Once you reach your Foundit homepage, press Enter here.\n")
    with sync_playwright() as p:
        ctx = p.chromium.launch(headless=False, args=ARGS).new_context(user_agent=UA, viewport={"width":1280,"height":900})
        pg  = ctx.new_page()
        pg.goto("https://www.foundit.in/")
        input(">>> Press Enter when fully logged in: ")
        ctx.storage_state(path=COOKIE_FILE)
        print(f"Session saved -> {COOKIE_FILE}")
        ctx.browser.close()


# -- ONE UPLOAD ATTEMPT -------------------------------------------
def _attempt(p, headless, debug):
    """Return 'OK', 'EXPIRED', or 'NOTFOUND'. Never raises."""
    mode = "headless" if headless else "visible"
    browser = p.chromium.launch(headless=headless, args=ARGS)
    try:
        ctx = browser.new_context(storage_state=COOKIE_FILE, user_agent=UA, viewport={"width":1280,"height":900})
        ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
        pg = ctx.new_page()
        pg.goto(PROFILE_URL, timeout=60000, wait_until="domcontentloaded")
        try: pg.wait_for_load_state("networkidle", timeout=20000)
        except Exception: pass
        time.sleep(2)

        if "login" in pg.url.lower() or "register" in pg.url.lower():
            return "EXPIRED"
        log(f"Profile page ({mode}): {pg.url}")
        _dismiss(pg)

        attempts = 1 if headless else 3
        found = False
        for i in range(attempts):
            try:
                pg.mouse.wheel(0, 1500); time.sleep(1); pg.mouse.wheel(0, -1500)
                pg.wait_for_selector("input[name='resume']", state="attached", timeout=15000)
                found = True; break
            except PWTimeout:
                log(f"Resume input not present yet ({mode}, try {i+1}/{attempts}).")
                if i < attempts - 1:
                    try:
                        pg.reload(timeout=60000, wait_until="domcontentloaded")
                        try: pg.wait_for_load_state("networkidle", timeout=15000)
                        except Exception: pass
                        _dismiss(pg)
                    except Exception: pass

        if not found:
            if debug:
                try: pg.screenshot(path=DEBUG_SS, full_page=True); log(f"Debug screenshot: {DEBUG_SS}")
                except Exception: pass
            return "NOTFOUND"

        log(f"Uploading: {RESUME}")
        pg.set_input_files("input[name='resume']", RESUME)
        log("File set on input[name=resume].")
        time.sleep(6)

        for s in ["button:has-text('Save')", "button:has-text('Confirm')",
                  "button:has-text('Yes')", "button:has-text('Upload')", "button[type='submit']"]:
            try: pg.click(s, timeout=4000); log(f"Confirmed via: {s}"); time.sleep(3); break
            except Exception: pass

        try: ctx.storage_state(path=COOKIE_FILE)
        except Exception: pass
        if debug:
            try: pg.screenshot(path=DEBUG_SS, full_page=True)
            except Exception: pass
        return "OK"
    finally:
        try: browser.close()
        except Exception: pass


# -- UPLOAD (orchestrator) ----------------------------------------
def upload(debug=False):
    if not RESUME or not os.path.exists(RESUME):
        log(f"ERROR: RESUME_PATH missing or file not found: {RESUME}"); return
    if not os.path.exists(COOKIE_FILE):
        log("No session file. Run: python foundit_upload.py --setup"); return
    if not debug and not lock(): sys.exit(0)

    log("Starting upload (saved session)...")
    try:
        with sync_playwright() as p:
            modes = [False] if debug else [True, False]  # try invisible first, fall back to visible
            result = "NOTFOUND"
            for headless in modes:
                try:
                    result = _attempt(p, headless, debug)
                except Exception as e:
                    log(f"Attempt ({'headless' if headless else 'visible'}) error: {e}")
                    result = "ERROR"
                if result == "OK":
                    log("SUCCESS: Foundit resume uploaded and session refreshed."); break
                if result == "EXPIRED":
                    log("Session expired. Run: python foundit_upload.py --setup"); break
            if result not in ("OK", "EXPIRED"):
                log("ERROR: Could not find the resume upload control (tried headless + visible).")
    except Exception as e:
        log(f"FATAL: {e}")
    finally:
        if not debug: unlock()


if __name__ == "__main__":
    if "--setup" in sys.argv:
        setup()
    elif "--debug" in sys.argv:
        upload(debug=True)
    else:
        upload()
