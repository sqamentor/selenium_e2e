
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium_utils.BrowserUtils.loader_utils import wait_for_loader_to_disappear
import unicodedata
import time
import logging

def smart_find_element(driver, by, value, retries=3, wait_between=1):
    """
    Find element with retries and Shadow DOM fallback.
    """
    for attempt in range(retries):
        try:
            element = driver.find_element(by, value)
            logging.info(f"[SMART_FIND] Found normally on attempt {attempt+1}: {value}")
            return element
        except Exception as normal_e:
            logging.warning(f"[SMART_FIND] Normal find attempt {attempt+1} failed. Trying Shadow DOM fallback... | {normal_e}")
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
                    except Exception as inner_shadow_e:
                        continue
            except Exception as shadow_e:
                continue

            # If not found, wait and retry
            time.sleep(wait_between)

    raise Exception(f"❌ smart_find_element() failed after {retries} retries for: {value}")

def try_selectors(driver, selectors, field_type, input_value=None, label=""):
    by_map = {
        "id": By.ID,
        "name": By.NAME,
        "xpath": By.XPATH,
        "css": By.CSS_SELECTOR
    }

    # Fallbacks for OTP or Verify
    if label.lower() in ["code", "otp", "verify otp"] and field_type == "textbox":
        try:
            otp_input = driver.find_element(By.CSS_SELECTOR, "input.otp-field")
            otp_input.clear()
            otp_input.send_keys(input_value)
            logging.info("✅ [FALLBACK] Entered OTP into input.otp-field")
            return {
                "element": otp_input,
                "selector": {"type": "css", "value": "input.otp-field", "score": 1.0}
            }
        except Exception as e:
            logging.warning(f"[FALLBACK] OTP field fallback failed: {e}")

    if label.lower() == "verify code" and field_type == "click":
        try:
            button = driver.find_element(By.XPATH, "//button[normalize-space()='Verify Code']")
            button.click()
            logging.info("✅ [FALLBACK] 'Verify Code' button clicked via fallback XPath")
            return {
                "element": button,
                "selector": {"type": "xpath", "value": "//button[normalize-space()='Verify Code']", "score": 1.0}
            }
        except Exception as e:
            logging.warning(f"[FALLBACK] Verify Code fallback failed: {e}")

    # Try all selectors
    for selector_type, selector_value, score in selectors:
        try:
            if not selector_type or not selector_value:
                logging.warning(f"[AI] Skipping bad selector: {selector_type} -> {selector_value}")
                continue

            if selector_type.lower() == "xpath" and not selector_value.strip().startswith(("/", "//")):
                logging.warning(f"[AI] Skipping invalid XPath: {selector_value}")
                continue

            if selector_type.lower() not in by_map:
                logging.warning(f"[AI] Unknown selector type: {selector_type}")
                continue

            if selector_value.strip().startswith(("/", "//")):
                logging.info(f"[SAFE] Forcing By.XPATH due to detected XPath pattern: {selector_value}")
                by_used = By.XPATH
            else:
                by_used = by_map[selector_type.lower()]

            # Clean the locator
            selector_value = selector_value.strip()
            selector_value = selector_value.replace('\n', '').replace('\t', '').replace('\r', '')
            selector_value = unicodedata.normalize("NFKC", selector_value)
            logging.info(f"[SAFE] Using cleaned locator: {selector_value}")

            time.sleep(0.5)  # slight wait for stability
            element = smart_find_element(driver, by_used, selector_value)  # 🛠 re-fetch fresh

            if field_type == "textbox":
                element.clear()
                element.send_keys(input_value)
            elif field_type == "dropdown":
                Select(element).select_by_visible_text(input_value)
            elif field_type == "click":
                element.click()

            wait_for_loader_to_disappear(driver)

            return {
                "element": element,
                "selector": {"type": selector_type, "value": selector_value, "score": score}
            }

        except (NoSuchElementException, ElementNotInteractableException, Exception) as e:
            logging.warning(f"[AI] Selector failed: {selector_type} -> {selector_value} | Error: {e}")
            continue

    raise Exception("❌ All selector strategies failed.")
