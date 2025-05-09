import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


# 🧠 Locate ChromeDriver
root_dir = r"c:\Users\LokendraSingh\selenium_e2e"
chromedriver_name = "chromedriver.exe"

for dirpath, dirnames, filenames in os.walk(root_dir):
    if chromedriver_name in filenames:
        chrome_driver_Path = os.path.join(dirpath, chromedriver_name)
        print(f"✅ ChromeDriver found: {chrome_driver_Path}")
        break
else:
    raise FileNotFoundError("❌ ChromeDriver not found in the current root directory.")

# 🧠 Set up Chrome with stealth options
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

# 🚀 Start browser
service = Service(executable_path=chrome_driver_Path)
driver = webdriver.Chrome(service=service, options=options)


# 🧙‍♂️ Hide webdriver flag from navigator
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
    """
})

# 🎯 Human-like typing simulation
def human_type(element, text, min_delay=0.1, max_delay=0.3):
    element.click()
    time.sleep(random.uniform(0.2, 0.5))
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(min_delay, max_delay))
    time.sleep(random.uniform(0.3, 0.7))

# 🖱️ Human-like mouse movement and click simulation
def human_click(element):
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

# 🌐 Visit target page (demo login site)
driver.get("https://www.saucedemo.com/")
time.sleep(random.uniform(2, 4))

# 🔐 Locate login fields
username_field = driver.find_element(By.ID, "user-name")
password_field = driver.find_element(By.ID, "password")
login_button = driver.find_element(By.ID, "login-button")

# ✍️ Human-like typing
human_type(username_field, "standard_user")
human_type(password_field, "secret_sauce")

# 🤏 Optional hesitation before clicking
time.sleep(random.uniform(1, 3))

# ✅ Human-like click
human_click(login_button)

# ⌛ Wait after login
time.sleep(random.uniform(3, 5))

# 📜 Human-like scrolling behavior
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

# 📴 Optional: simulate idle before closing
time.sleep(random.uniform(2, 4))
driver.quit()
