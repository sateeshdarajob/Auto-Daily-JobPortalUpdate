# foundit_upload.py — Upload resume to Foundit automatically
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv
import os, time
from datetime import datetime

load_dotenv(r"C:\JobAutomation\.env")
EMAIL    = os.getenv("FOUNDIT_EMAIL")
PASSWORD = os.getenv("FOUNDIT_PASSWORD")
RESUME   = os.getenv("RESUME_PATH")
LOG_FILE = r"C:\JobAutomation\log.txt"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] FOUNDIT: {msg}"
    print(line)
    with open(LOG_FILE, "a") as f: f.write(line + "\n")

def run():
    log("Starting Foundit resume upload...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto("https://www.foundit.in/", timeout=30000)
            page.wait_for_load_state("domcontentloaded"); time.sleep(2)
            log("Logging in...")
            try: page.click("a:has-text('Login'), button:has-text('Login')", timeout=5000)
            except: page.goto("https://www.foundit.in/login", timeout=15000)
            time.sleep(2)
            page.fill("input[type='email'], input[placeholder*='Email']", EMAIL, timeout=10000); time.sleep(1)
            page.fill("input[type='password']", PASSWORD, timeout=5000); time.sleep(1)
            page.click("button[type='submit'], button:has-text('Sign In')", timeout=5000); time.sleep(4)
            log("Logged in! Going to resume update page...")
            page.goto("https://www.foundit.in/seeker/updateResume", timeout=30000)
            page.wait_for_load_state("domcontentloaded"); time.sleep(3)
            fi = page.locator("input[type='file']").first
            fi.set_input_files(RESUME); time.sleep(3)
            try: page.click("button:has-text('Upload'), button:has-text('Save')", timeout=5000); time.sleep(2)
            except: log("No submit button — may have auto-uploaded.")
            log("SUCCESS: Foundit resume upload completed!")
        except PlaywrightTimeout as e: log(f"TIMEOUT ERROR: {e}")
        except Exception as e: log(f"ERROR: {e}")
        finally: browser.close()

if __name__ == "__main__": run()
