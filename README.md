# 🤖 Job Portal Auto-Resume Upload — Complete Setup Guide
### For Naukri & Foundit | Runs Automatically Twice Daily  - using Python + Playwright.

## Files

| File | Purpose |
|------|---------|
| `naukri_upload.py` | Logs into Naukri and uploads your resume |
| `foundit_upload.py` | Logs into Foundit and uploads your resume |
| `naukri_refresh.py` | Refreshes Naukri profile to show "Active Today" |
| `run_upload.bat` | Runs all 3 scripts in sequence (Task Scheduler calls this) |
| `SETUP_INSTRUCTIONS.txt` | Quick start guide |
| `Job_Portal_Automation_Guide.md` | Full step-by-step setup guide |

## Quick Start

1. Copy all files to `C:\JobAutomation\`
2. Create `C:\JobAutomation\.env` with your credentials
3. Run `pip install playwright python-dotenv && playwright install chromium`
4. Test: `python naukri_upload.py`
5. Schedule `run_upload.bat` in Windows Task Scheduler (8 AM + 6 PM)

## Requirements
- Python 3.8+
- playwright
- python-dotenv

## Author
Sateesh Kumar Dara

---

## 📌 What This Guide Covers

| Option | What It Does | Difficulty |
|--------|-------------|------------|
| **Option 1** | Playwright script uploads your actual resume file to Naukri + Foundit | ⭐⭐ Easy |
| **Option 2** | Python script refreshes your Naukri profile (marks you "active" daily) | ⭐ Easiest |

> **Think of it like this:**
> - Option 1 = A robot opens the website, logs in, and uploads your resume file — just like YOU would do manually.
> - Option 2 = A robot logs in and clicks the "Refresh Profile" button — so Naukri shows recruiters that you were "active today."

---

---

# ✅ OPTION 1: Playwright Script + Windows Task Scheduler

## 🧱 PART A — One-Time Setup (~30 minutes)

---

### 🔵 STEP 1: Check if Python is Already Installed

1. Press **Windows key + R** on your keyboard
2. Type `cmd` and press **Enter** — a black window opens
3. Type this and press Enter:
   ```
   python --version
   ```
4. **If you see something like `Python 3.11.4`** → Python is installed! Skip to Step 3.
5. **If you see `'python' is not recognized`** → You need to install Python. Go to Step 2.

---

### 🔵 STEP 2: Install Python (Only if Step 1 failed)

1. Open your browser and go to: **https://www.python.org/downloads/**
2. Click the big yellow **"Download Python 3.x.x"** button
3. Run the downloaded file (`.exe`)
4. **IMPORTANT:** On the first screen, tick the box that says **"Add Python to PATH"** ✅
5. Click **"Install Now"**
6. Wait for it to finish, then click **Close**
7. Repeat Step 1 to confirm it works

---

### 🔵 STEP 3: Create Your Project Folder

1. Open **File Explorer** (Windows key + E)
2. Go to `C:\` drive (or wherever you prefer)
3. Create a new folder called **`JobAutomation`**
4. Full path will be: `C:\JobAutomation\`

> This folder will hold ALL your scripts and files.

---

### 🔵 STEP 4: Install Required Packages

1. Open the black **Command Prompt** window (Windows key + R → type `cmd` → Enter)
2. Type each line below and press Enter after each one — **wait for it to finish before typing the next**:

```
pip install playwright
```
```
pip install python-dotenv
```
```
playwright install chromium
or
python -m pip install --upgrade pip
python -m pip install playwright
python -m playwright install chromium
python -m playwright --version
```

> The last command downloads a mini-browser (~150 MB). It will take a minute. This is normal.

3. When done, you'll see the cursor blinking again — that means it's finished.

---

### 🔵 STEP 5: Create Your Credentials File

> **Why a separate file?** So your password is NOT written directly inside the script. Much safer.

1. Open **Notepad** (search for Notepad in Start menu)
2. Copy and paste this exactly:

```
NAUKRI_EMAIL=your_naukri_email@gmail.com
NAUKRI_PASSWORD=your_naukri_password

FOUNDIT_EMAIL=your_foundit_email@gmail.com
FOUNDIT_PASSWORD=your_foundit_password

RESUME_PATH=C:\Lappy\New-Oppo\Docs\SATEESH-KUMAR-DARA.docx
```

3. Replace the values with YOUR actual email, password, and resume path
4. Click **File → Save As**
5. Navigate to `C:\JobAutomation\`
6. In the **"File name"** box, type: `.env`
7. In the **"Save as type"** box, select: **All Files (\*.\*)**
8. Click **Save**

> Your file should now be at `C:\JobAutomation\.env`

---

### 🔵 STEP 6: Create the Naukri Upload Script  -- **Which is already there naukri_upload.py**

### 🔵 STEP 7: Create the Foundit Upload Script  -- **Which is already there foundit_upload.py**

### 🔵 STEP 8: Create the "Run Both" Batch File -- **Which is already there run_upload.bat**
This is the file that Task Scheduler will run. It runs BOTH scripts one after another.

### 🔵 STEP 9: Test It First (IMPORTANT!)

Before scheduling, run it manually once to make sure it works.

1. **First test — run Naukri script visibly:**
   - Open `C:\JobAutomation\naukri_upload.py` in Notepad
   - Find the line: `browser = p.chromium.launch(headless=True)`
   - Change `True` to **`False`** — this makes the browser VISIBLE so you can watch
   - Save the file
   - Open Command Prompt, type:
     ```
     python C:\JobAutomation\naukri_upload.py
     ```
   - **Watch the browser open** and see if it logs in and uploads
   - Check `C:\JobAutomation\log.txt` to see what happened

2. If it works, change `headless=False` back to **`headless=True`** (invisible mode)

3. Run the batch file to test both at once:
   ```
   C:\JobAutomation\run_upload.bat
   ```

> **Common Issue:** If Naukri asks for OTP during login, see the "Troubleshooting" section at the bottom.

---

### 🔵 STEP 10: Set Up Windows Task Scheduler

This makes the script run automatically at 8 AM and 6 PM every day — WITHOUT you doing anything.

**10a. Open Task Scheduler:**
1. Press **Windows key**
2. Type `Task Scheduler`
3. Click on it to open

**10b. Create First Task (8 AM):**
1. On the right side, click **"Create Basic Task..."**
2. **Name:** Type `Resume Upload - Morning`
3. Click **Next**
4. **Trigger:** Select **"Daily"** → Click Next
5. **Start time:** Type `08:00:00` → Click Next
6. **Action:** Select **"Start a program"** → Click Next
7. **Program/script:** Click **Browse** → navigate to `C:\JobAutomation\run_upload.bat` → click Open
8. Click **Next → Finish**

**10c. Create Second Task (6 PM):**
1. Click **"Create Basic Task..."** again
2. **Name:** `Resume Upload - Evening`
3. **Trigger:** Daily → **Start time: 18:00:00**
4. **Action:** Start a program → Browse → `C:\JobAutomation\run_upload.bat`
5. Click **Next → Finish**

**10d. Make tasks run even if you're not logged in:**
1. Find your task in the list → Right-click → **Properties**
2. In the **General** tab, select: **"Run whether user is logged on or not"**
3. Tick: **"Run with highest privileges"**
4. Click **OK** → Enter your Windows password when asked

✅ **DONE! Option 2 is fully set up.**

---

### 📁 Your Final Folder Structure

```
C:\JobAutomation\
├── .env                  ← Your credentials (keep private!)
├── naukri_upload.py      ← Naukri script
├── foundit_upload.py     ← Foundit script
├── run_upload.bat        ← Runs both scripts
└── log.txt               ← Created automatically; shows what happened
```

---

---

# ✅ OPTION 2: Naukri Profile Refresh Script

## What This Does
Instead of uploading a file, this script simply **logs into Naukri and clicks "Refresh Profile"** — which tells Naukri's system you were active TODAY. Recruiters searching for candidates see "Active Today" next to your name, which makes them more likely to contact you.

> Think of it like: "I don't need to rewrite my resume daily — I just need Naukri to show I'm ACTIVE."

---

## PART A — Setup (5 minutes — uses Python already installed from Option 2)

### 🔵 STEP 1: Create the Refresh Script -- **Which is already there naukri_refresh.py**
### 🔵 STEP 2: Update Your Batch File to Include Refresh -- **Which is already done**
### 🔵 STEP 3: Test the Refresh Script

In Command Prompt:
```
python C:\JobAutomation\naukri_refresh.py
```

Then open Naukri in your browser and check your profile — the "Last active" should say **"Today"**.

---

### 🔵 STEP 4: Task Scheduler is Already Set Up!

Since you already set up Task Scheduler in Option 2 (pointing to `run_upload.bat`), the refresh script will ALSO run automatically at 8 AM and 6 PM — because it's now included in the same batch file. **No extra steps needed.**

---

---

# 🚨 TROUBLESHOOTING

### Problem: "Naukri asks for OTP on login"
**Solution:** Log into Naukri manually in Chrome, tick "Remember me / Keep me logged in", then export cookies:
```
pip install browser-cookie3
```
Then modify the script to load cookies instead of logging in each time. (Ask Claude to help with this step.)

### Problem: "Script runs but nothing happens"
**Solution:**
1. Open `naukri_upload.py`
2. Change `headless=True` to `headless=False`
3. Run again and WATCH what happens
4. Take a screenshot if it gets stuck and share with Claude

### Problem: "Login fails — wrong credentials"
**Solution:** Check your `.env` file — make sure there are NO spaces around the `=` sign:
- ✅ Correct: `NAUKRI_EMAIL=myemail@gmail.com`
- ❌ Wrong: `NAUKRI_EMAIL = myemail@gmail.com`

### Problem: "Naukri UI changed — upload button not found"
**Solution:** This is the most common issue with scripts. The fix is simple:
1. Open `naukri_upload.py` and set `headless=False`
2. Run it and watch where it gets stuck
3. Right-click on the stuck element in the browser → "Inspect"
4. Find the element's `id` or `class`
5. Update the selector in the script
(Or just ask Claude to update the selector for you.)

### Problem: "Task Scheduler doesn't run the script"
**Solution:**
1. Open Task Scheduler → find your task → Right-click → **Run** (to test manually)
2. Check: **Action tab** — make sure the path to `.bat` file is correct
3. Check: the task is set to run even when not logged in

---

# 📊 How to Check If It's Working

Every time the scripts run, they write to `C:\JobAutomation\log.txt`.

Open it anytime in Notepad to see:
```
[2026-06-03 08:00:01] NAUKRI: Starting Naukri resume upload...
[2026-06-03 08:00:05] NAUKRI: Login successful!
[2026-06-03 08:00:12] NAUKRI: ✅ Naukri resume upload COMPLETED successfully!
[2026-06-03 08:00:15] FOUNDIT: Starting Foundit resume upload...
[2026-06-03 08:00:22] FOUNDIT: ✅ Foundit resume upload COMPLETED successfully!
[2026-06-03 08:00:28] REFRESH: ✅ Naukri profile refresh COMPLETED!
```

If you see ✅ — it's working!
If you see ERROR — check the message and refer to Troubleshooting above.

---

# 🗂️ COMPLETE FILE LIST

| File | What It Does |
|------|-------------|
| `C:\JobAutomation\.env` | Your login credentials (private) |
| `C:\JobAutomation\naukri_upload.py` | Uploads resume to Naukri |
| `C:\JobAutomation\foundit_upload.py` | Uploads resume to Foundit |
| `C:\JobAutomation\naukri_refresh.py` | Refreshes Naukri profile activity |
| `C:\JobAutomation\run_upload.bat` | Runs all 3 scripts in sequence |
| `C:\JobAutomation\log.txt` | Auto-created log of all runs |


