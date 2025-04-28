# interaction_engine.py
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support.ui import Select
from selenium_utils.BrowserUtils.loader_utils import wait_for_loader_to_disappear
from utils.human_actions import simulate_typing
import unicodedata
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unicodedata
import time
import logging
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium_utils.BrowserUtils.loader_utils import wait_for_loader_to_disappear
from utils.human_actions import simulate_typing
from selenium_utils.elementFinderUtils.element_finder import smart_find_element

def try_selectors(driver, selectors, field_type, input_value=None, label=""):
    by_map = {
        "id": By.ID,
        "name": By.NAME,
        "xpath": By.XPATH,
        "css": By.CSS_SELECTOR
    }

    otp_related_labels = [
        "code", "otp", "verify otp", "verification code", "verification", "otp code", "verify code"
    ]

    # OTP field special handling
    if label.lower().strip() in otp_related_labels and field_type == "textbox":
        logging.info("[SAFE] Trying special OTP field fallback: input.otp-field")

        try:
            otp_inputs = driver.find_elements(By.CSS_SELECTOR, "input.otp-field")
            for otp_input in otp_inputs:
                if otp_input.is_displayed() and otp_input.is_enabled():
                    otp_input.clear()
                    try:
                        simulate_typing(otp_input, input_value)
                        otp_input.send_keys(input_value)
                        logging.info("✅ [SAFE] OTP field entered using simulate_typing and send_keys")
                    except Exception as typing_error:
                        logging.warning(f"[SAFE] Typing OTP failed, retrying after 1 second: {typing_error}")
                        time.sleep(1)
                        otp_input = driver.find_element(By.CSS_SELECTOR, "input.otp-field")
                        otp_input.clear()
                        otp_input.send_keys(input_value)
                        logging.info("✅ [SAFE] OTP field typed successfully after retry")

                    return {
                        "element": otp_input,
                        "selector": {"type": "css", "value": "input.otp-field", "score": 1.0}
                    }
        except Exception as e:
            logging.warning(f"[SAFE] OTP fallback typing failed: {e}")

    # Verify Code button special handling
    if label.lower().strip() == "verify code" and field_type == "click":
        logging.info("[SAFE] Trying special Verify Code fallback...")

        try:
            wait = WebDriverWait(driver, 10)
            verify_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'Verify Code')]")))

            if verify_btn and not verify_btn.is_enabled():
                logging.warning("[SAFE] Verify Code button detected but DISABLED! Waiting for enable...")
                wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Verify Code')]")))
                logging.info("[SAFE] Button is now clickable ✅")

            # Try clicking
            try:
                verify_btn.click()
                logging.info("✅ [SAFE] 'Verify Code' button clicked successfully on first attempt")
            except Exception as first_click_error:
                logging.warning(f"[SAFE] First click failed, retrying: {first_click_error}")
                time.sleep(1)
                verify_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Verify Code')]")))
                verify_btn.click()
                logging.info("✅ [SAFE] 'Verify Code' button clicked successfully after retry")

            return {
                "element": verify_btn,
                "selector": {"type": "xpath", "value": "//button[contains(text(),'Verify Code')]", "score": 1.0}
            }

        except Exception as e:
            logging.warning(f"[SAFE] Verify Code fallback failed even after retry: {e}")

    # Normal flow through selectors
    for selector_type, selector_value, score in selectors:
        try:
            if not selector_type or not selector_value:
                logging.warning(f"[AI] Skipping bad selector: {selector_type} -> {selector_value}")
                continue

            if selector_type.lower() not in by_map:
                logging.warning(f"[AI] Unknown selector type: {selector_type}")
                continue

            if selector_type.lower() == "xpath" and not selector_value.strip().startswith(("/", "//")):
                logging.warning(f"[AI] Skipping invalid XPath: {selector_value}")
                continue

            selector_value = unicodedata.normalize("NFKC", selector_value.strip())
            logging.info(f"[SAFE] Using cleaned locator: {selector_value}")
            by_used = By.XPATH if selector_type.lower() == "xpath" else by_map[selector_type.lower()]

            element = smart_find_element(driver, by_used, selector_value)

            time.sleep(0.5)

            if field_type == "textbox":
                element.clear()
                simulate_typing(element, input_value)
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

    raise Exception("❌ All selector strategies failed after full fallback attempts.")
