"""
selenium_wrapper.py
--------------------
Adds smart retries around Selenium actions like click, send_keys, etc.
Handles common exceptions gracefully.
"""

import time
import logging
from selenium.common.exceptions import (ElementClickInterceptedException, ElementNotInteractableException, TimeoutException)

def smart_retry(retries=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 1
            while attempt <= retries:
                try:
                    return func(*args, **kwargs)
                except (ElementClickInterceptedException, ElementNotInteractableException, TimeoutException) as e:
                    logging.warning(f"⚠️ Attempt {attempt}: Retrying due to {e}")
                    time.sleep(delay)
                    attempt += 1
            logging.error(f"❌ Failed after {retries} attempts.")
            raise
        return wrapper
    return decorator

class SeleniumWrapper:
    def __init__(self, driver):
        self.driver = driver

    @smart_retry(retries=3, delay=2)
    def click(self, element):
        element.click()

    @smart_retry(retries=3, delay=2)
    def send_keys(self, element, text):
        element.clear()
        element.send_keys(text)

    def get_text(self, element):
        return element.text.strip()

    def capture_screenshot(self, name):
        screenshot_path = f"resources/screenshots/{name}.png"
        self.driver.save_screenshot(screenshot_path)
        logging.info(f"🖼️ Screenshot saved: {screenshot_path}")
        return screenshot_path
