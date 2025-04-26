from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support.ui import Select
from selenium_utils.BrowserUtils.loader_utils import wait_for_loader_to_disappear
import unicodedata
import time
import logging
from utils.human_actions import simulate_typing

def smart_find_element(driver, by, value, retries=3, wait_between=1):
    """
    Find element with retries, Shadow DOM fallback, and iframe switching.
    """
    for attempt in range(retries):
        try:
            element = driver.find_element(by, value)
            logging.info(f"[SMART_FIND] Found normally on attempt {attempt+1}: {value}")
            return element
        except Exception as normal_e:
            logging.warning(f"[SMART_FIND] Normal find attempt {attempt+1} failed. Trying Shadow DOM and iframe fallback... {normal_e}")

            # Try Shadow DOM fallback
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

            # Try switching into iframes if shadow fails
            try:
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                logging.info(f"[IFRAME] Found {len(iframes)} iframe(s) on the page during fallback check.")

                for index, iframe in enumerate(iframes):
                    try:
                        driver.switch_to.frame(iframe)
                        logging.info(f"[IFRAME] Switched into iframe {index+1}/{len(iframes)} for search...")

                        iframe_element = driver.find_element(by, value)
                        logging.info(f"[IFRAME] Found element inside iframe {index+1}: {value}")
                        return iframe_element
                    except Exception:
                        driver.switch_to.default_content()
                        continue

                driver.switch_to.default_content()

            except Exception as iframe_error:
                logging.warning(f"[IFRAME] Iframe search fallback failed: {iframe_error}")

            time.sleep(wait_between)

    raise Exception(f"❌ smart_find_element() failed after {retries} retries (including Shadow DOM and iframe fallback) for: {value}")

def try_selectors(driver, selectors, field_type, input_value=None, label=""):
    by_map = {
        "id": By.ID,
        "name": By.NAME,
        "xpath": By.XPATH,
        "css": By.CSS_SELECTOR
    }

    # OTP fallback for 'Code' field
    if label.lower() in ["code", "otp", "verify otp","verify otp"] and field_type == "textbox":
        logging.info("[SAFE] Trying special OTP field fallback: CSS input.otp-field")
        try:
            otp_input_candidates = driver.find_elements(By.CSS_SELECTOR, "input.otp-field")
            for otp_input in otp_input_candidates:
                if otp_input.is_displayed() and otp_input.is_enabled():
                    otp_input.clear()
                    simulate_typing(otp_input, input_value)
                    otp_input.send_keys(input_value)
                    logging.info("✅ [FALLBACK] Entered OTP into input.otp-field (dynamic input)")
                    return {
                        "element": otp_input,
                        "selector": {"type": "css", "value": "input.otp-field", "score": 1.0}
                    }
        except Exception as e:
            logging.warning(f"[FALLBACK] OTP fallback failed: {e}")

    # After 1 sec retry if above fails
    time.sleep(1)

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

            selector_value = selector_value.strip()
            selector_value = selector_value.replace('\\n', '').replace('\\t', '').replace('\\r', '')
            selector_value = unicodedata.normalize("NFKC", selector_value)
            logging.info(f"[SAFE] Using cleaned locator: {selector_value}")

            # Smart Find Element
            element = smart_find_element(driver, by_used, selector_value)

            # Wait slightly for DOM stability
            time.sleep(0.5)

            # Re-fetch element freshly before action
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