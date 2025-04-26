from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import logging
from selenium_utils.BrowserUtils.loader_utils import wait_for_loader_to_disappear


def try_selectors(driver, selectors, field_type, input_value=None, label=""):
    by_map = {
        "id": By.ID,
        "name": By.NAME,
        "xpath": By.XPATH,
        "css": By.CSS_SELECTOR
    }

    # 🔁 Smart fallback: OTP field
    if label.lower() in ["code", "otp", "verify otp"] and field_type == "textbox":
        try:
            otp_input = driver.find_element(By.CSS_SELECTOR, "input.otp-field")
            otp_input.clear()
            otp_input.send_keys(input_value)
            logging.info("✅ [FALLBACK] Entered OTP in input.otp-field")
            return {
                "element": otp_input,
                "selector": { "type": "css", "value": "input.otp-field", "score": 1.0 }
            }
        except Exception as e:
            logging.warning(f"[FALLBACK] OTP selector failed: {e}")

    # 🔁 Smart fallback: Verify Code button
    if label.lower() == "verify code" and field_type == "click":
        try:
            button = driver.find_element(By.XPATH, "//button[normalize-space()='Verify Code']")
            button.click()
            logging.info("✅ [FALLBACK] 'Verify Code' button clicked via XPath")
            return {
                "element": button,
                "selector": { "type": "xpath", "value": "//button[normalize-space()='Verify Code']", "score": 1.0 }
            }
        except Exception as e:
            logging.warning(f"[FALLBACK] Verify Code button click failed: {e}")

    # 🔁 Try all AI-ranked selectors
    for selector_type, selector_value, score in selectors:
        try:
            if not selector_type or not selector_value:
                logging.warning(f"[AI] Skipping bad selector: {selector_type} -> {selector_value}")
                continue

            if selector_type not in by_map:
                logging.warning(f"[AI] Unknown selector type: {selector_type}")
                continue

            element = driver.find_element(by_map[selector_type], selector_value)
            if field_type == "textbox":
                element.clear()
                element.send_keys(input_value)
            elif field_type == "dropdown":
                Select(element).select_by_visible_text(input_value)
            elif field_type == "click":
                element.click()

            # 🚀 After any interaction, wait for loader
            wait_for_loader_to_disappear(driver)

            return {
                "element": element,
                "selector": { "type": selector_type, "value": selector_value, "score": score }
            }

        except (NoSuchElementException, ElementNotInteractableException, Exception) as e:
            logging.warning(f"[AI] Selector failed: {selector_type} -> {selector_value} | Error: {e}")
            continue

    raise Exception("❌ All selector strategies failed.")