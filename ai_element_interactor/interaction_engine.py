
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

def try_selectors(driver, selectors, field_type, input_value=None):
    by_map = {
        "id": By.ID,
        "name": By.NAME,
        "xpath": By.XPATH
    }

    for selector_type, selector_value, score in selectors:
        try:
            element = driver.find_element(by_map[selector_type], selector_value)
            if field_type == "textbox":
                element.clear()
                element.send_keys(input_value)
            elif field_type == "dropdown":
                Select(element).select_by_visible_text(input_value)
            elif field_type == "click":
                element.click()

            return {
                "element": element,
                "selector": { "type": selector_type, "value": selector_value, "score": score }
            }

        except (NoSuchElementException, ElementNotInteractableException):
            continue

    raise Exception("❌ All selector strategies failed.")
