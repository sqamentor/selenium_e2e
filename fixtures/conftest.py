# fixtures/conftest.py

import os
import sys
from dotenv import load_dotenv
from utils.path_initializer import ensure_project_root_in_sys_path
import pytest
import os
import allure
import pytest
from selenium_utils.BrowserUtils.chrome_automation_launcher import run_chrome_automation


# ✅ Ensure project root is always in sys.path
ensure_project_root_in_sys_path(relative_levels_up=1, print_debug=False)

# ✅ Load .env + .env.local if available
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path)
dotenv_local = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env.local'))
if os.path.exists(dotenv_local):
    load_dotenv(dotenv_local, override=True)

# ✅ Validate required env vars
required_vars = ["BASE_URL", "BROWSER"]
missing = [var for var in required_vars if os.getenv(var) is None]
if missing:
    raise RuntimeError(f"❌ Missing required environment variables: {', '.join(missing)}")

# ✅ Log important environment settings on test session start
def pytest_sessionstart(session):
    print("\n🧪 Starting Pytest Test Session")
    print("------------------------------------------------")
    print(f"📦 ENVIRONMENT  : {os.getenv('ENV', 'N/A')}")
    print(f"🌐 BASE_URL     : {os.getenv('BASE_URL', 'N/A')}")
    print(f"🌍 BROWSER      : {os.getenv('BROWSER', 'chrome')}")
    print(f"🕶️ HEADLESS     : {os.getenv('HEADLESS', 'false')}")
    print("------------------------------------------------\n")

#--------------------------------You can now access these environment settings anywhere in your tests:-------------------------------------------------------------
#import os
#base_url = os.getenv("BASE_URL")
#browser = os.getenv("BROWSER")
#headless = os.getenv("HEADLESS") == "true"

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # This hook is called for each phase of a test
    outcome = yield
    result = outcome.get_result()

    screenshot_enabled = os.getenv("SCREENSHOT_ON_FAIL", "true").lower() == "true"
    browser = item.funcargs.get("browser")

    if result.when == "call" and result.failed and screenshot_enabled and browser:
        if "driver" in item.funcargs:
            allure.attach(item.funcargs["driver"].get_screenshot_as_png(),
                          name="screenshot", attachment_type=allure.attachment_type.PNG)
        screenshot_path = f"screenshots/{item.name}.png"
        os.makedirs("screenshots", exist_ok=True)
        browser.save_screenshot(screenshot_path)
        allure.attach.file(
            screenshot_path,
            name="Failure Screenshot",
            attachment_type=allure.attachment_type.PNG
        )


@pytest.fixture(scope="function")
def driver():
    driver = run_chrome_automation()
    yield driver
    driver.quit()
