# 🔹 Standard Library
import sys
import os
import time
import pathlib
import logging

# 🔹 Third-Party: Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    ElementNotInteractableException
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


# 👇 Go up 3 levels from TestScript.py to reach AutomationUtilities

# Auto-detect and add project root
current_file = pathlib.Path(__file__).resolve()
project_root = current_file.parents[1]  # Goes up to /AutomationUtilities

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    print(f"[INFO] Added project root to sys.path: {project_root}")
else:
    print(f"[INFO] Project root already in sys.path")

# Debug: Print sys.path
print("\n[DEBUG] sys.path:")
for p in sys.path:
    print("   ", p)
# Try importing
try:
    from selenium_utils.elementFinderUtils.element_finder import ElementFinder
    print("\n✅ Import successful!")
except ModuleNotFoundError as e:
    print("\n❌ Import failed:", e)
    print("👉 Double check the path and file name.")
# Now import other packages
#from utils.BrowserUtils.chrome_automation_launcher import run_chrome_automation
#from utils.elementFinderUtils.element_finder import ElementFinder

# ------------------------- Setup Logging ------------------------------------------------------------------------------------------------
#Define the directory and log file path
BASE_DIR = pathlib.Path(__file__).parent.resolve()
LOG_FILE_PATH = os.path.join(BASE_DIR, "event_selection_page.log")

#Set up logging using that path
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
#Log where the logs are going
logging.info(f"[OK]-[LOGGING] Writing logs to: {LOG_FILE_PATH}")
#------------------------------------------------------------------------------------------------------------------

class EventSelectionPage:
    def __init__(self, driver: WebDriver, timeout=20):
        self.driver = driver
        self.finder = ElementFinder(driver)
        self.wait = WebDriverWait(driver, timeout)

    def wait_for_loader(self):
        try:
            WebDriverWait(self.driver, 20).until(
                EC.invisibility_of_element_located((By.ID, "loader"))
            )
            logging.info("✅ Loader disappeared.")
        except TimeoutException:
            logging.warning("⚠️ Loader still visible after timeout.")
        except Exception as e:
            logging.error(f"❌ Error while waiting for loader: {e}")

    def click_new_patient_appointment(self):
        btn = self.finder.find("xpath", "//h3[contains(text(), 'New Patient')]/following::button[contains(text(), 'Book Now')][1]", clickable=True)
        if btn:
            btn.click()
            logging.info("✅ Clicked 'Book Now' on New Patient Appointment.")
        else:
            logging.error("❌ Failed to click New Patient Appointment button.")

    def click_complimentary_consultation(self):
        #btn = self.finder.find("xpath", "//h5[contains(text(), 'Complimentary Consultation')]/ancestor::div[contains(@class,'field')]//button[contains(text(), 'Book Now')]", clickable=True)
        btn = self.finder.find("xpath", "//h3[contains(text(), 'Complimentary Consultation')]/following::button[contains(text(), 'Book Now')][2]", clickable=True)
        if btn:
            btn.click()
            logging.info("✅ Clicked 'Book Now' on Complimentary Consultation.")
        else:
            logging.error("❌ Failed to click Complimentary Consultation button.")

    def click_request_call_back(self):
        btn = self.finder.find("xpath", "//button[contains(.,'Request Call Back')]", clickable=True)
        if btn:
            btn.click()
            logging.info("✅ Clicked 'Request Call Back' button.")
        else:
            logging.warning("⚠️ Request Call Back button not found or not clickable.")

logging.info("⏳ Event Selection Page Test complete. Inspect form state.")