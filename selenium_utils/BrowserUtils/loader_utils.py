# selenium_utils/BrowserUtils/loader_utils.py

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging

def wait_for_loader_to_disappear(driver, timeout=20):
    try:
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located(("ID", "loader"))
        )
        logging.info("✅ Loader disappeared successfully.")
    except TimeoutException:
        logging.warning("⚠️ Loader did not disappear within timeout.")

def wait_for_loader_to_appear_and_disappear(driver, timeout=20):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(("ID", "loader"))
        )
        logging.info("✅ Loader appeared.")
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located(("ID", "loader"))
        )
        logging.info("✅ Loader disappeared after appearing.")
    except TimeoutException:
        logging.warning("⚠️ Loader did not behave as expected.")
