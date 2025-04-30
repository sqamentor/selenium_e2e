"""
driver_factory.py - Browser Driver Manager
------------------------------------------
Creates and returns browser driver instances based on config.
Supports local and remote (Selenium Grid / BrowserStack).
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import os

def get_driver(browser="chrome", headless=False, remote_url=None):
    if browser == "chrome":
        options = ChromeOptions()
        options.add_argument("--start-maximized")
        if headless:
            options.add_argument("--headless")
        return webdriver.Remote(command_executor=remote_url, options=options) if remote_url else webdriver.Chrome(options=options)

    elif browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.headless = True
        return webdriver.Remote(command_executor=remote_url, options=options) if remote_url else webdriver.Firefox(options=options)

    else:
        raise ValueError(f"❌ Unsupported browser: {browser}")
