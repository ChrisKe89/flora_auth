from typing import Dict
from playwright.async_api import async_playwright, TimeoutError as PwTimeout

LOGIN_MENU_TEXT = "Log In"  # clickable user-menu entry
LOGIN_NAME_SELECTOR = "#loginName"
LOGIN_PSW_SELECTOR = "#loginPsw"
LOGIN_BUTTON_SELECTOR = "#loginButton"

ADMIN_HASH_URL = "http://{ip}/system/index.html#hashSystem"
ROOT_URL = "http://{ip}"

# Administrator Settings page bits
ADMIN_SETTINGS_LABEL_TEXT = "Administrator Settings"

# Inputs on the admin settings section
ADMIN_LOGIN_NAME_INPUT = "input#loginName"
ADMIN_PASSWORD_INPUT = "input#password"
ADMIN_RETYPE_INPUT = "input#retypePassword"
ADMIN_OK_BUTTON_TEXT = "OK"

DEFAULT_TIMEOUT = 15000  # ms


async def change_device_credentials(
    ip: str,
    current_username: str,
    current_password: str,
    new_username: str,
    new_password: str,
) -> Dict:
    """
    Performs:
      - open http://{ip}
      - open login modal -> enter current creds -> submit
      - navigate to /system/index.html#hashSystem
      - click 'Administrator Settings'
      - set Username, Password, Retype -> OK
    Returns a dict with small details for logging.
    """

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        # 1) Landing page and login
        await page.goto(ROOT_URL.format(ip=ip), timeout=DEFAULT_TIMEOUT)
        # The login menu item
        await page.get_by_text(LOGIN_MENU_TEXT, exact=True).click(
            timeout=DEFAULT_TIMEOUT
        )

        # Fill credentials
        await page.fill(LOGIN_NAME_SELECTOR, current_username)
        await page.fill(LOGIN_PSW_SELECTOR, current_password)

        # The login button may be disabled until inputs; press Enter on password field as a backup
        try:
            await page.click(LOGIN_BUTTON_SELECTOR, timeout=3000)
        except PwTimeout:
            await page.press(LOGIN_PSW_SELECTOR, "Enter")

        # Optionally wait a small navigation/DOM change
        await page.wait_for_timeout(800)

        # 2) Navigate directly to admin settings shell page
        target_url = ADMIN_HASH_URL.format(ip=ip)
        await page.goto(target_url, timeout=DEFAULT_TIMEOUT)

        # The "Administrator Settings" section can be a label; click by visible text
        await page.get_by_text(ADMIN_SETTINGS_LABEL_TEXT, exact=True).click(
            timeout=DEFAULT_TIMEOUT
        )

        # 3) Fill new credentials
        # Some pages duplicate id="loginName" in different scopes; be on current page and use the first visible
        await page.fill(ADMIN_LOGIN_NAME_INPUT, new_username)
        await page.fill(ADMIN_PASSWORD_INPUT, new_password)
        await page.fill(ADMIN_RETYPE_INPUT, new_password)

        # 4) Click OK (by button text)
        await page.get_by_text(ADMIN_OK_BUTTON_TEXT, exact=True).click(
            timeout=DEFAULT_TIMEOUT
        )

        # Wait a moment to let device process save
        await page.wait_for_timeout(900)

        await context.close()
        await browser.close()

    return {"ip": ip, "admin_url": target_url, "changed_user_to": new_username}
