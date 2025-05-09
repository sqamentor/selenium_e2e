from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)
import logging
import pathlib
import os
import time
from selenium_utils.browser_utils.loader_utils import wait_for_loader_to_disappear

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
    def __init__(self, driver, timeout=15, poll_frequency=0.5):
        self.driver = driver
        self.timeout = timeout
        self.poll_frequency = poll_frequency

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

    def find(self, locator_type, locator_value, visible=True, clickable=False, multiple=False):
        by_locator = self.get_locator(locator_type, locator_value)
        try:
            wait = WebDriverWait(self.driver, self.timeout, self.poll_frequency, ignored_exceptions=[StaleElementReferenceException])
            
            if multiple:
                logging.info(f"🔍 Finding all elements: {by_locator}")
                elements = wait.until(EC.presence_of_all_elements_located(by_locator))
                for elem in elements: self.highlight(elem)
                return elements
            if clickable:
                logging.info(f"🔍 Finding clickable element: {by_locator}")
                #element = wait.until(EC.element_to_be_clickable(by_locator))
                element = wait.until(EC.element_to_be_clickable((getattr(By, locator_type.upper()), locator_value)))
            elif visible:
                logging.info(f"🔍 Finding visible element: {by_locator}")
                #element = wait.until(EC.visibility_of_element_located(by_locator))
                element = wait.until(EC.visibility_of_element_located((getattr(By, locator_type.upper()), locator_value)))
            else:
                logging.info(f"🔍 Finding present element (not necessarily visible): {by_locator}")
                #element = wait.until(EC.presence_of_element_located(by_locator))
                element = wait.until(EC.presence_of_element_located((getattr(By, locator_type.upper()), locator_value)))
            logging.info(f"✅ Found element [{locator_type}] {locator_value}")

            # 🚀 After finding, wait for any loaders to disappear
            wait_for_loader_to_disappear(self.driver)

            self.highlight(element)
            return element

        except TimeoutException:
            logging.error(f"⏱️ Timeout: Element not found using {locator_type} = {locator_value}")
            self._capture_failure_screenshot(f"timeout_{locator_type}_{locator_value}")
            return None
        except Exception as e:
            logging.exception(f"❌ Unexpected error while finding element: {e}")
            self._capture_failure_screenshot(f"error_{locator_type}_{locator_value}")
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