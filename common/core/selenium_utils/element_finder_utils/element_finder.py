from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)
import logging
import time
import pathlib
import os
from selenium_utils.browser_utils.loader_utils import wait_for_loader_to_disappear
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support.ui import Select
from utils.human_actions import simulate_typing

# ------------------------- Setup Logging -------------------------
# ✅ Step 1: Define the directory and log file path
BASE_DIR = pathlib.Path(__file__).parent.resolve()
LOG_FILE_PATH = os.path.join(BASE_DIR, "TestScript-ElementFinder.log")

# ✅ Step 2: Set up logging using that path
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
# ✅ Step 3 (optional): Log where the logs are going
logging.info(f"[OK]-[LOGGING] Writing logs to: {LOG_FILE_PATH}")

class ElementFinder:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.timeout = timeout

    def get_locator(self, locator_type, locator_value):
        locator_type = locator_type.lower()
        mapping = {
            "id": By.ID,
            "name": By.NAME,
            "xpath": By.XPATH,
            "css": By.CSS_SELECTOR,
            "class": By.CLASS_NAME,
            "link_text": By.LINK_TEXT,
            "partial_link_text": By.PARTIAL_LINK_TEXT,
            "tag": By.TAG_NAME
        }
        if locator_type not in mapping:
            raise ValueError(f"Unsupported locator type: {locator_type}")
        return (mapping[locator_type], locator_value)

    def find(self, by_type, locator, visible=False, clickable=False):
        try:
            if clickable:
                # Wait for the element to be clickable
                element = WebDriverWait(self.driver, self.timeout).until(
                    EC.element_to_be_clickable((getattr(By, by_type.upper()), locator))
                )
            elif visible:
                # Wait for the element to be visible
                element = WebDriverWait(self.driver, self.timeout).until(
                    EC.visibility_of_element_located((getattr(By, by_type.upper()), locator))
                )
            else:
                # Find the element without waiting for visibility or clickability
                element = self.driver.find_element(getattr(By, by_type.upper()), locator)
            return element
        except Exception as e:
            logging.error(f"❌ Error finding element ({by_type}, {locator}): {e}")
            return None

    def highlight(self, element):
        try:
            self.driver.execute_script(
                "arguments[0].style.border='1px solid red'; arguments[0].scrollIntoView(true);", element
            )
        except Exception as e:
            logging.warning(f"⚠️ Unable to highlight element: {e}")

    def _capture_failure_screenshot(self, name="element_error"):
        try:
            os.makedirs("screenshots", exist_ok=True)
            path = f"screenshots/{name}_{int(time.time())}.png"
            self.driver.save_screenshot(path)
            logging.info(f"🖼️ Screenshot captured: {path}")
        except Exception as e:
            logging.warning(f"⚠️ Failed to capture screenshot: {e}")

    def find_shadow(self, shadow_host_locator, inner_css_selector):
        try:
            host = self.find(*shadow_host_locator)
            if not host:
                logging.error("❌ Shadow host not found.")
                return None
            shadow_root = self.driver.execute_script("return arguments[0].shadowRoot", host)
            element = shadow_root.find_element(By.CSS_SELECTOR, inner_css_selector)
            self.highlight(element)
            logging.info("✅ Found element inside Shadow DOM.")
            return element
        except Exception as e:
            logging.error(f"❌ Shadow DOM lookup failed: {e}")
            return None

    def is_visible_js(self, xpath_locator):
        try:
            script = """
                const el = document.evaluate(arguments[0], document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                return el ? !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length) : false;
            """
            visible = self.driver.execute_script(script, xpath_locator)
            logging.info(f"🧠 JS visibility of '{xpath_locator}': {visible}")
            return visible
        except Exception as e:
            logging.warning(f"⚠️ JS visibility check failed: {e}")
            return False
    def find_all(self, by, locator, visible=False):
        try:
            elements = self.driver.find_elements(getattr(By, by.upper()), locator)
            if visible:
                elements = [el for el in elements if el.is_displayed()]
            if not elements:
                logging.warning(f"⚠️ No elements found for: ({by}, {locator})")
            else:
                logging.debug(f"🔍 Found {len(elements)} elements for: ({by}, {locator})")
            return elements
        except Exception as e:
            logging.error(f"❌ Failed to find elements: ({by}, {locator}) - {e}")
            return []

    def find_clickable(self, locator, timeout=15):
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator))
        except TimeoutException:
            self.logger.error(f"❌ Clickable element not found: {locator}")
            self.driver.save_screenshot("screenshots/element_not_clickable.png")
            raise

    def smart_find_element(self, driver, by, value, retries=3, wait_between=1):
        for attempt in range(retries):
            try:
                return self._find_normally(driver, by, value, attempt)
            except Exception as normal_e:
                logging.warning(f"[SMART_FIND] Normal find attempt {attempt+1} failed: {normal_e}")
                if self._find_in_shadow_dom(driver, by, value, attempt):
                    return self._find_in_shadow_dom(driver, by, value, attempt)
                if self._find_in_iframes(driver, by, value, attempt):
                    return self._find_in_iframes(driver, by, value, attempt)
                time.sleep(wait_between)

        raise NoSuchElementException(f"❌ smart_find_element() failed after {retries} retries for {value}")

    def _find_normally(self, driver, by, value, attempt):
        element = driver.find_element(by, value)
        logging.info(f"[SMART_FIND] Found normally on attempt {attempt+1}: {value}")
        return element

    def _find_in_shadow_dom(self, driver, by, value, attempt):
        try:
            all_elements = driver.execute_script('return document.querySelectorAll("*")')
            for root in all_elements:
                shadow_root = driver.execute_script('return arguments[0].shadowRoot', root)
                if shadow_root:
                    found = shadow_root.find_element(by, value)
                    if found:
                        logging.info(f"[SMART_FIND] Found inside Shadow DOM on attempt {attempt+1}: {value}")
                        return found
        except Exception:
            pass
        return None

    def _find_in_iframes(self, driver, by, value, attempt):
        try:
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            for index, iframe in enumerate(iframes):
                try:
                    driver.switch_to.frame(iframe)
                    iframe_element = driver.find_element(by, value)
                    logging.info(f"[SMART_FIND] Found inside iframe {index+1}: {value}")
                    return iframe_element
                except Exception:
                    driver.switch_to.default_content()
                    continue
            driver.switch_to.default_content()
        except Exception:
            pass
        return None