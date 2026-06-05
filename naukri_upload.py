# naukri_upload.py v2 — Fixed login selectors + lock file to prevent duplicate runs
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv
import os, time, sys
from datetime import datetime

load_dotenv(r"C:\JobAutomation\.env")
EMAIL    = os.getenv("NAUKRI_EMAIL")
PASSWORD = os.getenv("NAUKRI_PASSWORD")
RESUME   = os.getenv("RESUME_PATH")
LOG_FILE = r"C:\JobAutomation\log.txt"
LOCK_FILE = r"C:\JobAutomation\naukri_upload.lock"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] NAUKRI: {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def acquire_lock():
    """Prevent duplicate runs. Returns False if another instance is running."""
    if os.path.exists(LOCK_FILE):
        age = time.time() - os.path.getmtime(LOCK_FILE)
        if age < 600:  # 10 minutes — if lock is fresh, skip
            log(f"SKIPPED: Another instance is running (lock age: {int(age)}s). Exiting.")
            return False
        else:
            log("Stale lock found — removing and continuing.")
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

    log("Starting Naukri resume upload...")
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
            # ── STEP 1: Go directly to Naukri login page ──
            log("Opening Naukri login page...")
            page.goto("https://www.naukri.com/nlogin/login", timeout=30000)
            page.wait_for_load_state("networkidle", timeout=20000)
            time.sleep(2)

            # Dismiss any cookie/popup overlay
            for dismiss in ["button:has-text('Accept')", "button:has-text('OK')", ".cookie-btn", "[class*='close']"]:
                try:
                    page.click(dismiss, timeout=2000)
                    time.sleep(0.5)
                except:
                    pass

            # ── STEP 2: Fill email ──
            log("Filling email...")
            email_selectors = [
                "input[placeholder='Enter your active Email ID']",
                "input[id='usernameField']",
                "input[type='email']",
                "input[placeholder*='Email']",
                "input[name='username']",
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
                log("ERROR: Could not find email field.")
                return

            time.sleep(1)

            # ── STEP 3: Fill password ──
            log("Filling password...")
            pwd_selectors = [
                "input[placeholder='Enter your password']",
                "input[id='passwordField']",
                "input[type='password']",
                "input[placeholder*='password']",
                "input[placeholder*='Password']",
            ]
            for sel in pwd_selectors:
                try:
                    page.wait_for_selector(sel, timeout=5000, state="visible")
                    page.fill(sel, PASSWORD)
                    log(f"Password filled using: {sel}")
                    break
                except:
                    continue

            time.sleep(1)

            # ── STEP 4: Submit login ──
            log("Submitting login...")
            submit_selectors = [
                "button[type='submit']",
                "button:has-text('Login')",
                "input[type='submit']",
                "button:has-text('Sign in')",
            ]
            for sel in submit_selectors:
                try:
                    page.click(sel, timeout=5000)
                    log(f"Clicked submit: {sel}")
                    break
                except:
                    continue

            # Wait for redirect after login
            page.wait_for_load_state("networkidle", timeout=20000)
            time.sleep(3)

            current_url = page.url
            log(f"After login URL: {current_url}")
            if "nlogin" in current_url or "login" in current_url:
                log("WARNING: Still on login page — check credentials or CAPTCHA.")
                # Try to continue anyway in case it's just a slow redirect
                time.sleep(3)

            # ── STEP 5: Navigate to profile page ──
            log("Going to profile page...")
            page.goto("https://www.naukri.com/mnjuser/profile", timeout=30000)
            page.wait_for_load_state("domcontentloaded", timeout=20000)
            time.sleep(4)

            # ── STEP 6: Find resume upload input ──
            log("Looking for resume upload input...")
            upload_selectors = [
                "input[type='file']",
                "input[accept*='.doc']",
                "input[accept*='pdf']",
                "#attachCV",
                "[data-type='upload'] input",
            ]
            uploaded = False
            for sel in upload_selectors:
                try:
                    fi = page.locator(sel).first
                    page.wait_for_selector(sel, timeout=5000)
                    fi.set_input_files(RESUME)
                    log(f"Resume attached via: {sel}")
                    uploaded = True
                    time.sleep(5)
                    break
                except:
                    continue

            if not uploaded:
                # Try clicking "Update Resume" button first, then look for input
                for btn in ["text=Update Resume", "text=Upload Resume", "button:has-text('Update')"]:
                    try:
                        page.click(btn, timeout=5000)
                        time.sleep(2)
                        fi = page.locator("input[type='file']").first
                        fi.set_input_files(RESUME)
                        uploaded = True
                        log("Resume attached after clicking Update button.")
                        time.sleep(5)
                        break
                    except:
                        continue

            if not uploaded:
                log("ERROR: Could not find resume upload input. Naukri UI may have changed.")
                return

            # ── STEP 7: Save ──
            for save_sel in ["button:has-text('Save')", "button:has-text('Upload')", ".saveBtn", "button[type='submit']"]:
                try:
                    page.click(save_sel, timeout=5000)
                    log(f"Clicked save: {save_sel}")
                    time.sleep(3)
                    break
                except:
                    continue

            log("SUCCESS: Naukri resume upload completed!")

        except PlaywrightTimeout as e:
            log(f"TIMEOUT ERROR: {e}")
        except Exception as e:
            log(f"ERROR: {e}")
        finally:
            browser.close()
            release_lock()

if __name__ == "__main__":
    run()
