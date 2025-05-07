# selenium_utils/BrowserUtils/element_wait_utils.py

import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def wait_for_element_to_be_enabled(driver, by, value, timeout=10):
    """
    Waits until the element is both visible and enabled, within a timeout.
    """
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            element = driver.find_element(by, value)
            if element.is_displayed() and element.is_enabled():
                return element
        except Exception:
            pass
        time.sleep(1)
    raise Exception(f"[WAIT] Element not enabled within {timeout} seconds: {value}")
