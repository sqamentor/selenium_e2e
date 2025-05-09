from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support.ui import Select
from selenium_utils.browser_utils.loader_utils import wait_for_loader_to_disappear
from utils.human_actions import simulate_typing
import unicodedata
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def smart_find_element(driver, by, value, retries=3, wait_between=1):
    for attempt in range(retries):
        try:
            element = driver.find_element(by, value)
            logging.info(f"[SMART_FIND] Found normally on attempt {attempt+1}: {value}")
            return element
        except Exception as normal_e:
            logging.warning(f"[SMART_FIND] Normal find attempt {attempt+1} failed: {normal_e}")

            try:
                all_elements = driver.execute_script('return document.querySelectorAll("*")')
                for root in all_elements:
                    try:
                        shadow_root = driver.execute_script('return arguments[0].shadowRoot', root)
                        if shadow_root:
                            found = shadow_root.find_element(by, value)
                            if found:
                                logging.info(f"[SMART_FIND] Found inside Shadow DOM on attempt {attempt+1}: {value}")
                                return found
                    except Exception:
                        continue
            except Exception:
                pass

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

            time.sleep(wait_between)

    raise Exception(f"❌ smart_find_element() failed after {retries} retries for {value}")