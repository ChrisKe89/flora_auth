# flora_auth

A tiny Windows-friendly tool to update device admin credentials across many IPs using Playwright automation.

## What it does

- Reads IPs from `.\data\device_list.csv` (first column only)
- Opens each device at `http://{ip}`
- Clicks **Log In**, enters current credentials, submits
- Goes to `http://{ip}/system/index.html#hashSystem`
- Opens **Administrator Settings**
- Sets **Login Name**, **Password**, **Retype Password**, clicks **OK**
- Streams progress to the UI and writes JSON logs in `.\logs\`
- Resumes safely after interruption (skips already-completed devices for the same credential change)

## Prereqs (Windows)

1. Install **Python 3.11+** from python.org. During install, tick “Add Python to PATH”.
2. In **PowerShell** (or Command Prompt), from the project root:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   python -m playwright install chromium
