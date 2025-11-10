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

---

## Prereqs (Windows)

1. Install **Python 3.11+** from [python.org](https://www.python.org/downloads/).  
   During install, tick **“Add Python to PATH”**.

2. Open **VS Code’s integrated terminal** (or PowerShell) and create a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies and the Playwright browser **locally inside the repo**:

   ```powershell
   pip install -r requirements.txt
   $env:PLAYWRIGHT_BROWSERS_PATH = "$PWD\.pw-browsers"
   python -m playwright install chromium
   ```

   - This creates a `.pw-browsers` folder inside the project.
   - The Chromium engine is stored here instead of under your Windows user profile.
   - It ensures consistent behavior for all users and avoids path restrictions on managed systems.

4. Verify the install:

   ```powershell
   python -m playwright --version
   ```

   You should see a version number like `Version 1.xx.x`.

---

## Run the App

Activate the virtual environment and start the tool:

```powershell
.\.venv\Scripts\Activate.ps1
python app.py
```

The window will open.
Fill in **Current Credentials** and **New Credentials**, make sure the passwords match, then click **Change Password**.

> CSV path is fixed to `.\data\device_list.csv` — only column A is read.
> A header like `IP` is optional and ignored.

---

## Logs & Resume

- A JSONL log file is created in `.\logs\` with the pattern:

  ```markdown
  YYYY-MM-DDTHH-MM-SS__<run_id>.json
  ```

  Each line is a JSON object with `"status": "ok"` or `"error"`.

- A resume file is kept per credential change in:

  ```markdown
  .\logs\runs\<run_id>.json
  ```

  where `run_id = sha256(current_user|current_pass|new_user|new_pass)[:16]`.

  Running again with the same four values skips completed IPs.

---

## Troubleshooting

- **Playwright browser not found:**
  If you see

  ```markdown
  BrowserType.launch: Executable doesn't exist ...
  ```

  run again:

  ```powershell
  $env:PLAYWRIGHT_BROWSERS_PATH = "$PWD\.pw-browsers"
  python -m playwright install chromium
  ```

- **Network timeout:**
  Increase `DEFAULT_TIMEOUT` in `bots/device_actions.py` (default: 15000 ms).

- **Debug visually:**
  Set `headless=False` in `device_actions.py` to watch the browser automation.

---

## Security Notes

- Credentials are used only in memory during execution.
- Logs record only outcomes (success/error), never plaintext passwords.
- Prefer using a dedicated temporary admin account for rotations.

---

## Project Structure

```markdown
flora_auth/
├─ app.py
├─ requirements.txt
├─ data/
│  └─ device_list.csv
├─ logs/
│  └─ (auto-created)
├─ bots/
│  └─ device_actions.py
└─ services/
   ├─ runner.py
   ├─ csv_loader.py
   ├─ json_logger.py
   └─ state.py
```

---

## Packaging (Optional)

To build a single-file executable for helpdesk deployment:

```powershell
.\.venv\Scripts\activate
pip install pyinstaller
pyinstaller --noconsole --onefile --name flora_auth app.py
```

Place `data\device_list.csv` beside the EXE; it will create a `logs` folder at runtime.

---

## Notes

This project is designed for Windows, but Playwright automation is cross-platform.
To run on macOS or Linux, adjust activation scripts (`source .venv/bin/activate`) and file paths accordingly.
