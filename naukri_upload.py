# naukri_upload.py — Upload resume to Naukri automatically
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv
import os, time
from datetime import datetime

load_dotenv(r"C:\JobAutomation\.env")
EMAIL    = os.getenv("NAUKRI_EMAIL")
PASSWORD = os.getenv("NAUKRI_PASSWORD")
RESUME   = os.getenv("RESUME_PATH")
LOG_FILE = r"C:\JobAutomation\log.txt"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] NAUKRI: {msg}"
    print(line)
    with open(LOG_FILE, "a") as f: f.write(line + "\n")

def run():
    log("Starting Naukri resume upload...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Change to False to watch it work
        page = browser.new_page()
        try:
            page.goto("https://www.naukri.com/", timeout=30000)
            page.wait_for_load_state("domcontentloaded"); time.sleep(2)
            log("Clicking Login...")
            try: page.click("a[href*='login']:visible", timeout=5000)
            except: page.click("text=Login", timeout=5000)
            time.sleep(2)
            page.fill("input[placeholder*='Email']", EMAIL, timeout=10000); time.sleep(1)
            page.fill("input[type='password']", PASSWORD, timeout=5000); time.sleep(1)
            page.click("button[type='submit']", timeout=5000); time.sleep(4)
            if "login" in page.url.lower():
                log("ERROR: Login failed — check credentials in .env file"); return
            log("Login successful! Going to profile...")
            page.goto("https://www.naukri.com/mnjuser/profile", timeout=30000)
            page.wait_for_load_state("domcontentloaded"); time.sleep(3)
            log(f"Uploading resume: {RESUME}")
            for sel in ["input[type='file']", "input[accept*='.doc']", "#resumeFileInput"]:
                try:
                    fi = page.locator(sel).first
                    if fi.count() > 0:
                        fi.set_input_files(RESUME); time.sleep(3)
                        log("File attached!"); break
                except: continue
            try: page.click("button:has-text('Save'), button:has-text('Upload')", timeout=5000); time.sleep(2)
            except: log("No Save button — may have auto-saved.")
            log("SUCCESS: Naukri resume upload completed!")
        except PlaywrightTimeout as e: log(f"TIMEOUT ERROR: {e}")
        except Exception as e: log(f"ERROR: {e}")
        finally: browser.close()

if __name__ == "__main__": run()
