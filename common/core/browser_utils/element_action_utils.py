# selenium_utils/BrowserUtils/element_action_utils.py

import time

def retry_click_element(driver, by, value, retries=10, wait_between=1):
    """
    Retry clicking an element multiple times if it's disabled initially.
    """
    from selenium.common.exceptions import ElementNotInteractableException, ElementClickInterceptedException
    last_exception = None
    for attempt in range(retries):
        try:
            element = driver.find_element(by, value)
            if element.is_displayed() and element.is_enabled():
                element.click()
                return True
            else:
                time.sleep(wait_between)
        except (ElementNotInteractableException, ElementClickInterceptedException) as e:
            last_exception = e
            time.sleep(wait_between)
    raise Exception(f"[CLICK RETRY] Failed to click after {retries} retries: {value}. Last error: {last_exception}")
