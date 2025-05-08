import random
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import logging
import allure

def simulate_typing(element, text, delay_range=(0.05, 0.15)):
    """
    Types slowly into an element with optional delay between keys.
    Adjusts speed based on element tag.
    """
    try:
        tag = element.tag_name.lower()
        adjusted_delay_range = delay_range
        if tag in ['textarea', 'input']:
            adjusted_delay_range = (0.07, 0.18)
        elif tag in ['div', 'span']:
            adjusted_delay_range = (0.04, 0.1)
        else:
            adjusted_delay_range = (0.05, 0.12)

        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(*adjusted_delay_range))

    except Exception as e:
        logging.error(f"❌ Typing simulation failed: {e}")

def human_scroll(driver, scroll_times=3):
    for _ in range(scroll_times):
        driver.execute_script("window.scrollBy(0, 300);")
        time.sleep(random.uniform(0.5, 1.2))

def random_mouse_movement(driver, steps=5, retry=2):
    """
    Hovers randomly over visible form-related elements and takes a screenshot.
    Includes retry logic if no elements found.
    """
    for attempt in range(1, retry + 1):
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, "input, button, label, select, textarea, a, .form-control, .p-inputtext")
            visible_elements = [
                el for el in elements
                if el.is_displayed() and el.size['width'] > 10 and el.size['height'] > 10
            ]

            if not visible_elements:
                logging.warning(f"🔁 Attempt {attempt}: No visible elements found.")
                time.sleep(1)
                continue

            actions = ActionChains(driver)

            for i in range(steps):
                element = random.choice(visible_elements)
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                actions.move_to_element(element).perform()
                logging.info(f"🖱️ Hovered over: <{element.tag_name}> {element.get_attribute('id') or element.get_attribute('name')}")
                time.sleep(random.uniform(0.4, 1.0))

                # Screenshot proof
                filename = f"screenshots/mouse_hover_{i+1}_{int(time.time())}.png"
                driver.save_screenshot(filename)
                allure.attach.file(
                    filename,
                    name=f"Mouse Hover #{i+1}",
                    attachment_type=allure.attachment_type.PNG
                )

            return  # ✅ Done

        except Exception as e:
            logging.error(f"❌ Error during mouse movement (attempt {attempt}): {e}")
            time.sleep(1)

    logging.error("❌ Mouse movement failed after all retries.")
