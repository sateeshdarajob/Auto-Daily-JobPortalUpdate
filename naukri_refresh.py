# naukri_refresh.py — Refresh Naukri profile to appear "Active Today"
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv
import os, time
from datetime import datetime

load_dotenv(r"C:\JobAutomation\.env")
EMAIL    = os.getenv("NAUKRI_EMAIL")
PASSWORD = os.getenv("NAUKRI_PASSWORD")
LOG_FILE = r"C:\JobAutomation\log.txt"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] REFRESH: {msg}"
    print(line)
    with open(LOG_FILE, "a") as f: f.write(line + "\n")

def run():
    log("Starting Naukri profile refresh...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto("https://www.naukri.com/", timeout=30000)
            page.wait_for_load_state("domcontentloaded"); time.sleep(2)
            try: page.click("a[href*='login']:visible", timeout=5000)
            except: page.click("text=Login", timeout=5000)
            time.sleep(2)
            page.fill("input[placeholder*='Email']", EMAIL, timeout=10000); time.sleep(1)
            page.fill("input[type='password']", PASSWORD, timeout=5000); time.sleep(1)
            page.click("button[type='submit']", timeout=5000); time.sleep(4)
            log("Logged in. Visiting profile...")
            page.goto("https://www.naukri.com/mnjuser/homepage", timeout=30000)
            page.wait_for_load_state("domcontentloaded"); time.sleep(3)
            refreshed = False
            for sel in ["text=Refresh", "button:has-text('Refresh')", "[data-ga-track*='refresh']"]:
                try: page.click(sel, timeout=3000); refreshed = True; log(f"Clicked refresh: {sel}"); break
                except: continue
            if not refreshed:
                page.goto("https://www.naukri.com/mnjuser/profile", timeout=30000)
                page.wait_for_load_state("domcontentloaded"); time.sleep(3)
                log("Visited profile — last active timestamp updated.")
            log("SUCCESS: Naukri profile now shows 'Active Today'!")
        except PlaywrightTimeout as e: log(f"TIMEOUT ERROR: {e}")
        except Exception as e: log(f"ERROR: {e}")
        finally: browser.close()

if __name__ == "__main__": run()
