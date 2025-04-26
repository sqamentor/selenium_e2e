# selenium_utils/BrowserUtils/loader_utils.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time

def wait_for_loader_to_disappear(driver, timeout=30, poll_frequency=0.5):
    """
    Wait until common loader/spinner elements disappear from the DOM or become hidden.
    Supports multiple common loader types: ID-based, aria-busy, spinners, etc.
    """
    logging.info("[LOADER] Waiting for any active loader to disappear...")
    loader_selectors = [
        (By.ID, "loader"),
        (By.CLASS_NAME, "spinner"),
        (By.CLASS_NAME, "loading"),
        (By.CSS_SELECTOR, "[aria-busy='true']"),
        (By.CSS_SELECTOR, ".p-progress-spinner"),
        (By.CSS_SELECTOR, ".p-datatable-loading-overlay")
    ]

    end_time = time.time() + timeout

    while time.time() < end_time:
        active_loaders = []

        for by, locator in loader_selectors:
            try:
                elements = driver.find_elements(by, locator)
                for elem in elements:
                    if elem.is_displayed():
                        active_loaders.append(elem)
            except Exception:
                continue

        if not active_loaders:
            logging.info("[LOADER] ✅ No visible loaders found.")
            return True

        time.sleep(poll_frequency)

    logging.warning("[LOADER] ❌ Timeout reached. Loaders may still be active!")
    return False