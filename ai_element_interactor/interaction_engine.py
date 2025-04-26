# 🔹 Standard Library
import logging
import time
import unicodedata

# 🔹 Third-Party
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support.ui import Select

# 🔹 Internal Utilities
from selenium_utils.BrowserUtils.loader_utils import wait_for_loader_to_disappear
from utils.human_actions import simulate_typing

def smart_find_element(driver, by, value, retries=3, wait_between=1):
    """
    Find element robustly with retries, Shadow DOM fallback, and iframe switching.
    """
    for attempt in range(retries):
        try:
            element = driver.find_element(by, value)
            logging.info(f"[SMART_FIND] Found normally on attempt {attempt+1}: {value}")
            return element
        except Exception as normal_e:
            logging.warning(f"[SMART_FIND] Normal find attempt {attempt+1} failed. Trying Shadow DOM and iframe fallback... {normal_e}")

            # Shadow DOM fallback
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

            # iframe fallback
            try:
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                logging.info(f"[IFRAME] Found {len(iframes)} iframe(s) on page during fallback.")
                for index, iframe in enumerate(iframes):
                    try:
                        driver.switch_to.frame(iframe)
                        logging.info(f"[IFRAME] Switched to iframe {index+1}/{len(iframes)} for searching.")
                        iframe_element = driver.find_element(by, value)
                        logging.info(f"[IFRAME] Found element inside iframe {index+1}: {value}")
                        return iframe_element
                    except Exception:
                        driver.switch_to.default_content()
                        continue
                driver.switch_to.default_content()
            except Exception as iframe_error:
                logging.warning(f"[IFRAME] Iframe fallback failed: {iframe_error}")

            time.sleep(wait_between)

    raise Exception(f"❌ smart_find_element() failed after {retries} retries (including Shadow DOM and iframe fallback) for: {value}")

def try_selectors(driver, selectors, field_type, input_value=None, label=""):
    """
    Try a list of selectors safely and fallback to special strategies for OTP or Verify buttons.
    """
    by_map = {
        "id": By.ID,
        "name": By.NAME,
        "xpath": By.XPATH,
        "css": By.CSS_SELECTOR
    }

    # OTP fallback for Code field
    if label.lower() in ["code", "otp", "verify otp", "verification code"] and field_type == "textbox":
        logging.info("[SAFE] Trying special OTP fallback: CSS 'input.otp-field' inside p-inputmask")
        try:
            # Find ALL otp input fields
            otp_inputs = driver.find_elements(By.CSS_SELECTOR, "input.otp-field")
            for otp_input in otp_inputs:
                if otp_input.is_displayed() and otp_input.is_enabled():
                    otp_input.clear()
                    simulate_typing(otp_input, input_value)
                    otp_input.send_keys(input_value)
                    logging.info(f"✅ [FALLBACK] OTP code entered successfully into input.otp-field: {input_value}")
                    wait_for_loader_to_disappear(driver)
                    return {
                        "element": otp_input,
                        "selector": {"type": "css", "value": "input.otp-field", "score": 1.0}
                    }
            logging.error("❌ [FALLBACK] No visible enabled OTP input found.")
        except Exception as e:
            logging.warning(f"[FALLBACK] OTP fallback error: {e}")


    # Verify Code button fallback
    if label.lower() in ["verify code", "verify otp", "submit code"] and field_type == "click":
        logging.info("[SAFE] Trying special Verify Code button fallback.")
        try:
            # Look for button by text
            verify_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Verify')]")
            for button in verify_buttons:
                if button.is_displayed() and button.is_enabled():
                    button.click()
                    logging.info("✅ [FALLBACK] 'Verify Code' button clicked via fallback XPath (button[contains(text(),'Verify')])")
                    wait_for_loader_to_disappear(driver)
                    return {
                        "element": button,
                        "selector": {"type": "xpath", "value": "//button[contains(text(), 'Verify')]", "score": 1.0}
                    }
            logging.error("❌ [FALLBACK] No visible enabled Verify button found.")
        except Exception as e:
            logging.warning(f"[FALLBACK] Verify Code button fallback error: {e}")

    time.sleep(1)  # slight delay after fallback attempt

    # Normal selector attempts
    for selector_type, selector_value, score in selectors:
        try:
            if not selector_type or not selector_value:
                logging.warning(f"[AI] Skipping bad selector: {selector_type} -> {selector_value}")
                continue

            selector_type = selector_type.lower()
            selector_value = selector_value.strip()

            if selector_type not in by_map:
                logging.warning(f"[AI] Unknown selector type: {selector_type}")
                continue

            if selector_type == "xpath" and not selector_value.startswith(("/", "//")):
                logging.warning(f"[AI] Skipping invalid XPath: {selector_value}")
                continue

            if selector_value:
                selector_value = unicodedata.normalize("NFKC", selector_value)
                selector_value = selector_value.replace("\\n", "").replace("\\t", "").replace("\\r", "")
                logging.info(f"[SAFE] Using cleaned locator: {selector_value}")

            by_used = by_map.get(selector_type)

            # Smart Find
            element = smart_find_element(driver, by_used, selector_value)
            time.sleep(0.5)
            element = smart_find_element(driver, by_used, selector_value)

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

    raise Exception("❌ All selector strategies failed after full fallback attempts.")