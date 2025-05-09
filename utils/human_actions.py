import random
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import logging
import allure

# 🎯 Human-like typing simulation
def human_type(element, text, min_delay=0.1, max_delay=0.3):
    """
    Simulates human-like typing into an element.
    """
    try:
        element.click()
        time.sleep(random.uniform(0.2, 0.5))
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(min_delay, max_delay))
        time.sleep(random.uniform(0.3, 0.7))
    except Exception as e:
        logging.error(f"❌ Typing simulation failed: {e}")

# 🖱️ Human-like mouse movement and click simulation
def human_click(driver, element):
    """
    Simulates human-like mouse movement and clicking on an element.
    """
    try:
        actions = ActionChains(driver)
        elem_rect = element.rect
        elem_center_x = elem_rect['x'] + elem_rect['width'] / 2
        elem_center_y = elem_rect['y'] + elem_rect['height'] / 2
        curr_x, curr_y = 0, 0
        steps = 8
        for i in range(1, steps + 1):
            interp_x = curr_x + (elem_center_x - curr_x) * (i / steps)
            interp_y = curr_y + (elem_center_y - curr_y) * (i / steps)
            actions.move_by_offset(interp_x - curr_x, interp_y - curr_y)
            actions.perform()
            curr_x, curr_y = interp_x, interp_y
            time.sleep(random.uniform(0.05, 0.2))
        offset_x = random.randint(-5, 5)
        offset_y = random.randint(-5, 5)
        actions.move_by_offset(offset_x, offset_y).pause(random.uniform(0.1, 0.3)).click().perform()
        time.sleep(random.uniform(0.2, 0.5))
    except Exception as e:
        logging.error(f"❌ Mouse click simulation failed: {e}")

# 📜 Human-like scrolling behavior
def human_scroll_behavior(driver):
    """
    Simulates human-like scrolling behavior on a webpage.
    """
    try:
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        current_scroll = 0
        while current_scroll < scroll_height:
            increment = random.randint(100, 300)
            current_scroll = min(current_scroll + increment, scroll_height)
            driver.execute_script("window.scrollTo(0, arguments[0]);", current_scroll)
            time.sleep(random.uniform(0.5, 1.5))

        # 🧍 Scroll slightly back up (natural correction)
        driver.execute_script("window.scrollTo(0, arguments[0]);", current_scroll - random.randint(100, 300))
        time.sleep(random.uniform(0.5, 1.0))
    except Exception as e:
        logging.error(f"❌ Scrolling simulation failed: {e}")

# ✍️ Combined human-like behavior simulation
def mimic_human_behavior(driver):
    """
    Combines typing, scrolling, and mouse movements to mimic human behavior.
    """
    logging.info("🤖 Mimicking human behavior...")
    human_scroll(driver, scroll_times=random.randint(3, 7))
    random_mouse_movement(driver, steps=random.randint(5, 15))
    human_scroll_behavior(driver)
    logging.info("✅ Human-like behavior simulation completed.")

# 🎯 Random page interaction
def random_page_interaction(driver):
    """
    Performs random interactions on the page to mimic human behavior.
    """
    try:
        # Randomly click on checkboxes or radio buttons
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox'], input[type='radio']")
        if checkboxes:
            checkbox = random.choice(checkboxes)
            if checkbox.is_displayed():
                checkbox.click()
                logging.info(f"✅ Clicked on checkbox/radio button: {checkbox.get_attribute('id') or checkbox.get_attribute('name')}")
                time.sleep(random.uniform(0.5, 1.5))

        # Randomly select dropdown options
        dropdowns = driver.find_elements(By.TAG_NAME, "select")
        if dropdowns:
            dropdown = random.choice(dropdowns)
            if dropdown.is_displayed():
                options = dropdown.find_elements(By.TAG_NAME, "option")
                if options:
                    random.choice(options).click()
                    logging.info(f"✅ Selected dropdown option: {dropdown.get_attribute('id') or dropdown.get_attribute('name')}")
                    time.sleep(random.uniform(0.5, 1.5))

    except Exception as e:
        logging.error(f"❌ Error during random page interaction: {e}")

# 📴 Optional: simulate idle before closing
def simulate_idle(driver, idle_time=(2, 4)):
    """
    Simulates idle behavior before closing the browser.
    """
    time.sleep(random.uniform(*idle_time))
    logging.info("🛑 Simulated idle time completed.")

def simulate_typing(element, text, delay_range=(0.1, 0.3)):
    """
    Types slowly into an element with optional delay between keys.
    Adjusts speed based on element tag and adds random pauses.
    """
    try:
        tag = element.tag_name.lower()
        adjusted_delay_range = delay_range
        if tag in ['textarea', 'input']:
            adjusted_delay_range = (0.12, 0.25)
        elif tag in ['div', 'span']:
            adjusted_delay_range = (0.08, 0.15)
        else:
            adjusted_delay_range = (0.1, 0.2)

        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(*adjusted_delay_range))
            # Random pause to mimic human typing
            if random.random() < 0.1:  # 10% chance of a pause
                time.sleep(random.uniform(0.5, 1.5))

        # Simulate pressing Enter or Tab occasionally
        if random.random() < 0.2:  # 20% chance
            element.send_keys(Keys.TAB)
            time.sleep(random.uniform(0.5, 1.0))

    except Exception as e:
        logging.error(f"❌ Typing simulation failed: {e}")

def human_scroll(driver, scroll_times=5):
    """
    Scrolls the page in a human-like manner with random pauses and distances.
    """
    for _ in range(scroll_times):
        scroll_distance = random.randint(200, 600)
        driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
        time.sleep(random.uniform(0.8, 2.0))
        # Random pause to mimic human behavior
        if random.random() < 0.2:  # 20% chance of a longer pause
            time.sleep(random.uniform(2.0, 4.0))

def random_mouse_movement(driver, steps=10, retry=3):
    """
    Moves the mouse randomly over visible elements and performs random actions.
    Includes retry logic if no elements are found.
    """
    for attempt in range(1, retry + 1):
        try:
            visible_elements = get_visible_elements(driver)
            if not visible_elements:
                logging.warning(f"🔁 Attempt {attempt}: No visible elements found.")
                time.sleep(1)
                continue

            perform_mouse_movements(driver, visible_elements, steps)
            return  # ✅ Done

        except Exception as e:
            logging.error(f"❌ Error during mouse movement (attempt {attempt}): {e}")
            time.sleep(1)

    logging.error("❌ Mouse movement failed after all retries.")


def get_visible_elements(driver):
    """
    Retrieves visible elements on the page.
    """
    elements = driver.find_elements(By.CSS_SELECTOR, "input, button, label, select, textarea, a, .form-control, .p-inputtext")
    return [
        el for el in elements
        if el.is_displayed() and el.size['width'] > 10 and el.size['height'] > 10
    ]


def perform_mouse_movements(driver, visible_elements, steps):
    """
    Performs mouse movements and random actions on visible elements.
    """
    actions = ActionChains(driver)
    for i in range(steps):
        element = random.choice(visible_elements)
        hover_and_log(driver, actions, element)
        random_click(element)
        random_hover_away(actions)
        take_screenshot(driver, i)


def hover_and_log(driver, actions, element):
    """
    Hovers over an element and logs the action.
    """
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    actions.move_to_element(element).perform()
    logging.info(f"🖱️ Hovered over: <{element.tag_name}> {element.get_attribute('id') or element.get_attribute('name')}")
    time.sleep(random.uniform(0.5, 1.5))


def random_click(element):
    """
    Randomly clicks on an element with a 30% chance.
    """
    if random.random() < 0.3:  # 30% chance of clicking
        try:
            element.click()
            logging.info(f"🖱️ Clicked on: <{element.tag_name}> {element.get_attribute('id') or element.get_attribute('name')}")
        except Exception as e:
            logging.warning(f"⚠️ Failed to click on element: {e}")


def random_hover_away(actions):
    """
    Randomly hovers away from the current element with a 20% chance.
    """
    if random.random() < 0.2:  # 20% chance
        actions.move_by_offset(random.randint(-50, 50), random.randint(-50, 50)).perform()
        time.sleep(random.uniform(0.3, 0.8))


def take_screenshot(driver, step):
    """
    Takes a screenshot of the current state.
    """
    filename = f"screenshots/mouse_hover_{step+1}_{int(time.time())}.png"
    driver.save_screenshot(filename)
    allure.attach.file(
        filename,
        name=f"Mouse Hover #{step+1}",
        attachment_type=allure.attachment_type.PNG
    )