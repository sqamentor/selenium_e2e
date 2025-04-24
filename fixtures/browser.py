import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

from selenium_utils.undetected_chrome_launcher import launch_undetected_chrome

@pytest.fixture(scope="function")
def browser():
    browser_type = os.getenv("BROWSER", "chrome").lower()
    headless = os.getenv("HEADLESS", "false").lower() == "true"
    use_profile = os.getenv("REAL_PROFILE", "true").lower() == "true"
    profile_dir = os.getenv("PROFILE_DIR", "Default")

    if browser_type == "chrome":
        # Use undetected Chrome for stealth mode
        driver = launch_undetected_chrome(
            headless=headless,
            use_profile=use_profile,
            profile_dir=profile_dir,
            enable_incognito=not use_profile
        )
    elif browser_type == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
    elif browser_type == "edge":
        options = EdgeOptions()
        if headless:
            options.add_argument("--headless")
        driver = webdriver.Edge(options=options)
    else:
        raise ValueError(f"❌ Unsupported BROWSER: '{browser_type}'")

    yield driver
    driver.quit()
