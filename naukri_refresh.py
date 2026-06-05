# naukri_refresh.py v2 — Fixed login + lock file
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv
import os, time, sys
from datetime import datetime

load_dotenv(r"C:\JobAutomation\.env")
EMAIL     = os.getenv("NAUKRI_EMAIL")
PASSWORD  = os.getenv("NAUKRI_PASSWORD")
LOG_FILE  = r"C:\JobAutomation\log.txt"
LOCK_FILE = r"C:\JobAutomation\naukri_refresh.lock"

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
            log(f"SKIPPED: Another instance is running (lock age: {int(age)}s).")
            return False
        log("Stale lock — removing.")
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

    log("Starting Naukri profile refresh...")
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
            # Go directly to login page
            page.goto("https://www.naukri.com/nlogin/login", timeout=30000)
            page.wait_for_load_state("networkidle", timeout=20000)
            time.sleep(2)

            # Fill email
            for sel in ["input[placeholder='Enter your active Email ID']", "input[id='usernameField']", "input[type='email']", "input[placeholder*='Email']"]:
                try:
                    page.wait_for_selector(sel, timeout=5000, state="visible")
                    page.fill(sel, EMAIL)
                    log(f"Email: {sel}")
                    break
                except:
                    continue

            time.sleep(1)

            # Fill password
            for sel in ["input[placeholder='Enter your password']", "input[id='passwordField']", "input[type='password']"]:
                try:
                    page.wait_for_selector(sel, timeout=5000, state="visible")
                    page.fill(sel, PASSWORD)
                    log(f"Password: {sel}")
                    break
                except:
                    continue

            time.sleep(1)

            # Submit
            for sel in ["button[type='submit']", "button:has-text('Login')"]:
                try:
                    page.click(sel, timeout=5000)
                    break
                except:
                    continue

            page.wait_for_load_state("networkidle", timeout=20000)
            time.sleep(3)
            log("Logged in. Visiting profile to update last-active timestamp...")

            # Visit profile page — this updates "last active" on Naukri
            page.goto("https://www.naukri.com/mnjuser/profile", timeout=30000)
            page.wait_for_load_state("domcontentloaded", timeout=20000)
            time.sleep(4)

            # Try clicking Refresh button if present
            for sel in ["button:has-text('Refresh')", "text=Refresh my Profile", "a:has-text('Refresh')"]:
                try:
                    page.click(sel, timeout=3000)
                    log(f"Clicked refresh: {sel}")
                    time.sleep(2)
                    break
                except:
                    continue

            log("SUCCESS: Naukri profile active timestamp updated!")

        except PlaywrightTimeout as e:
            log(f"TIMEOUT ERROR: {e}")
        except Exception as e:
            log(f"ERROR: {e}")
        finally:
            browser.close()
            release_lock()

if __name__ == "__main__":
    run()
