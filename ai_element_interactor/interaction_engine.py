
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium_utils.BrowserUtils.loader_utils import wait_for_loader_to_disappear
import unicodedata
import logging
import time

def try_selectors(driver, selectors, field_type, input_value=None, label=""):
    by_map = {
        "id": By.ID,
        "name": By.NAME,
        "xpath": By.XPATH,
        "css": By.CSS_SELECTOR
    }

    # 🔁 Smart fallback: OTP input field
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

    # 🔁 Smart fallback: Verify Code button
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

    # 🧠 Try all AI-recommended selectors
    for selector_type, selector_value, score in selectors:
        try:
            if not selector_type or not selector_value:
                logging.warning(f"[AI] Skipping bad selector: {selector_type} -> {selector_value}")
                continue

            # 🚨 Validate XPath
            if selector_type.lower() == "xpath" and not selector_value.strip().startswith(("/", "//")):
                logging.warning(f"[AI] Skipping invalid XPath: {selector_value}")
                continue

            if selector_type.lower() not in by_map:
                logging.warning(f"[AI] Unknown selector type: {selector_type}")
                continue

            # 🚀 Force correction: If locator looks like XPath but by_type is wrong
            if selector_value.strip().startswith(("/", "//")):
                logging.info(f"[SAFE] Forcing By.XPATH due to detected XPath pattern: {selector_value}")
                by_used = By.XPATH
            else:
                by_used = by_map[selector_type.lower()]

            # 🚿 Sanitize locator
            selector_value = selector_value.strip()
            selector_value = selector_value.replace('\n', '').replace('\t', '').replace('\r', '')
            selector_value = unicodedata.normalize("NFKC", selector_value)
            logging.info(f"[SAFE] Using cleaned locator: {selector_value}")

            # 🔁 Retry mechanism
            retry_attempts = 3
            for attempt in range(retry_attempts):
                try:
                    element = driver.find_element(by_used, selector_value)
                    break  # ✅ Success
                except Exception as e_inner:
                    if attempt < retry_attempts - 1:
                        logging.warning(f"[RETRY] Selector attempt {attempt+1} failed, retrying after 1s... | {e_inner}")
                        time.sleep(1)
                    else:
                        raise e_inner

            if field_type == "textbox":
                element.clear()
                element.send_keys(input_value)
            elif field_type == "dropdown":
                Select(element).select_by_visible_text(input_value)
            elif field_type == "click":
                element.click()

            # 🚀 Wait for loader after interaction
            wait_for_loader_to_disappear(driver)

            return {
                "element": element,
                "selector": {"type": selector_type, "value": selector_value, "score": score}
            }

        except (NoSuchElementException, ElementNotInteractableException, Exception) as e:
            logging.warning(f"[AI] Selector failed: {selector_type} -> {selector_value} | Error: {e}")
            continue

    raise Exception("❌ All selector strategies failed.")
