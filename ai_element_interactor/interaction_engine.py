
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium_utils.BrowserUtils.loader_utils import wait_for_loader_to_disappear
from utils.human_actions import simulate_typing
import logging
import unicodedata
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

    # Fallback for OTP textbox input
    if label.lower().strip() in otp_related_labels and field_type == "textbox":
        logging.info("[SAFE] Trying special OTP field fallback: CSS input.otp-field")
        try:
            otp_inputs = driver.find_elements(By.CSS_SELECTOR, "input.otp-field")
            for otp_input in otp_inputs:
                if otp_input.is_displayed() and otp_input.is_enabled():
                    otp_input.clear()
                    simulate_typing(otp_input, input_value)  # Human typing
                    driver.execute_script("arguments[0].value = arguments[1];", otp_input, input_value)
                    otp_input.send_keys(input_value)
                    logging.info("✅ [FALLBACK] Entered OTP into input.otp-field (dynamic input)")
                    return {
                        "element": otp_input,
                        "selector": {"type": "css", "value": "input.otp-field", "score": 1.0}
                    }
        except Exception as e:
            logging.warning(f"[SAFE] OTP field fallback failed: {e}")

    # Separate Fallback for Verify Code button clicking
    if label.lower().strip() == "verify code" and field_type == "click":
        logging.info("[SAFE] Trying special fallback: Clicking Verify Code button")
        try:
            wait = WebDriverWait(driver, 10)
            verify_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Verify Code')]")))
            verify_btn.click()
            logging.info("✅ [FALLBACK] 'Verify Code' button clicked via fallback")
            return {
                "element": verify_btn,
                "selector": {"type": "xpath", "value": "//button[contains(text(),'Verify Code')]", "score": 1.0}
            }
        except Exception as e:
            logging.warning(f"[FALLBACK] Verify Code button click failed: {e}")


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

            if selector_value.strip().startswith(("/", "//")):
                by_used = By.XPATH
            else:
                by_used = by_map[selector_type.lower()]

            selector_value = unicodedata.normalize("NFKC", selector_value.strip())
            logging.info(f"[SAFE] Using cleaned locator: {selector_value}")

            element = smart_find_element(driver, by_used, selector_value)

            time.sleep(0.5)

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
