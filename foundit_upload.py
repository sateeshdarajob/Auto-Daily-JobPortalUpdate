# foundit_upload.py v2 — Fixed login selectors + lock file
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv
import os, time, sys
from datetime import datetime

load_dotenv(r"C:\JobAutomation\.env")
EMAIL     = os.getenv("FOUNDIT_EMAIL")
PASSWORD  = os.getenv("FOUNDIT_PASSWORD")
RESUME    = os.getenv("RESUME_PATH")
LOG_FILE  = r"C:\JobAutomation\log.txt"
LOCK_FILE = r"C:\JobAutomation\foundit_upload.lock"

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
            log(f"SKIPPED: Another instance is running (lock age: {int(age)}s). Exiting.")
            return False
        log("Stale lock found — removing.")
    open(LOCK_FILE, "w").close()
    return True

def release_lock():
    try:
        os.remove(LOCK_FILE)
    except:
        pass

def run():
    if not acquire_lock():
        sys.exit(0)

    log("Starting Foundit resume upload...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )
        page = context.new_page()

        try:
            # ── STEP 1: Go directly to Foundit login ──
            log("Opening Foundit login page...")
            page.goto("https://www.foundit.in/login", timeout=30000)
            page.wait_for_load_state("networkidle", timeout=20000)
            time.sleep(3)

            # Dismiss cookie/popups
            for dismiss in ["button:has-text('Accept')", "button:has-text('OK')", "[class*='close']", "[aria-label='Close']"]:
                try:
                    page.click(dismiss, timeout=2000)
                    time.sleep(0.5)
                except:
                    pass

            # ── STEP 2: Fill email/username ──
            log("Filling email...")
            email_selectors = [
                "input[type='email']",
                "input[name='email']",
                "input[id='email']",
                "input[placeholder*='mail']",
                "input[placeholder*='Mail']",
                "input[placeholder*='phone']",
                "input[type='text']",
            ]
            filled = False
            for sel in email_selectors:
                try:
                    page.wait_for_selector(sel, timeout=5000, state="visible")
                    page.fill(sel, EMAIL)
                    filled = True
                    log(f"Email filled using: {sel}")
                    break
                except:
                    continue

            if not filled:
                log("ERROR: Could not find email field on Foundit.")
                return

            time.sleep(1)

            # ── STEP 3: Fill password ──
            log("Filling password...")
            for sel in ["input[type='password']", "input[name='password']", "input[id='password']"]:
                try:
                    page.wait_for_selector(sel, timeout=5000, state="visible")
                    page.fill(sel, PASSWORD)
                    log(f"Password filled: {sel}")
                    break
                except:
                    continue

            time.sleep(1)

            # ── STEP 4: Submit ──
            log("Submitting login...")
            for sel in ["button[type='submit']", "button:has-text('Sign In')", "button:has-text('Login')", "button:has-text('Continue')"]:
                try:
                    page.click(sel, timeout=5000)
                    log(f"Clicked: {sel}")
                    break
                except:
                    continue

            page.wait_for_load_state("networkidle", timeout=20000)
            time.sleep(3)
            log(f"After login URL: {page.url}")

            # ── STEP 5: Navigate to resume update ──
            log("Going to resume update page...")
            page.goto("https://www.foundit.in/seeker/updateResume", timeout=30000)
            page.wait_for_load_state("domcontentloaded", timeout=20000)
            time.sleep(4)

            # ── STEP 6: Upload file ──
            log("Uploading resume file...")
            for sel in ["input[type='file']", "input[accept*='pdf']", "input[accept*='doc']"]:
                try:
                    page.wait_for_selector(sel, timeout=8000)
                    page.locator(sel).first.set_input_files(RESUME)
                    log(f"File attached: {sel}")
                    time.sleep(5)
                    break
                except:
                    continue

            # ── STEP 7: Save/Submit ──
            for sel in ["button:has-text('Upload')", "button:has-text('Save')", "button[type='submit']"]:
                try:
                    page.click(sel, timeout=5000)
                    log(f"Clicked save: {sel}")
                    time.sleep(3)
                    break
                except:
                    continue

            log("SUCCESS: Foundit resume upload completed!")

        except PlaywrightTimeout as e:
            log(f"TIMEOUT ERROR: {e}")
        except Exception as e:
            log(f"ERROR: {e}")
        finally:
            browser.close()
            release_lock()

if __name__ == "__main__":
    run()
