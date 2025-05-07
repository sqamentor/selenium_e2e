# 🔹 Standard Library
# 🚀 Bootstraps project root to sys.path so all modules like `utils` are accessible
import os, sys
current_file = os.path.abspath(__file__)
project_root = os.path.abspath(os.path.join(current_file, "..", ".."))  # Go up 2 levels
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from utils.path_initializer import ensure_project_root_in_sys_path
ensure_project_root_in_sys_path(relative_levels_up=2)

# 🔹 Standard Library
import time
import pathlib
import logging

# 🔹 Third-Party: Selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
load_dotenv()


# 🔹 AI Interaction Utility
from ai_element_interactor.ai_field_interactor import interact_by_label

# ✅ Human Behavior Simulation Utilities
from utils.human_actions import simulate_typing, human_scroll, random_mouse_movement

# ✅ Browser Launcher
from selenium_utils.BrowserUtils.chrome_automation_launcher import run_chrome_automation

# ✅ Global Smart Loader Wait
from selenium_utils.BrowserUtils.loader_utils import wait_for_loader_to_disappear

# ------------------------- Setup Logging ------------------------------------------------------------------------------------------------
BASE_DIR = pathlib.Path(__file__).parent.resolve()
LOG_FILE_PATH = os.path.join(BASE_DIR, "Bookslot_info_otp_page_ai.log")

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logging.info(f"[OK]-[LOGGING] Writing logs to: {LOG_FILE_PATH}")

# ------------------------------------------------------------------------------------------------------------
# UI Component: Book Slot Page (Center for Vein Restoration)
logging.info("🚀 Starting AI-driven UI interaction with Book Slot page...")

target_url = os.getenv("TARGET_URL")
logging.info(f"[ENV] Target URL: {target_url}")

driver = run_chrome_automation(target_url)
wait = WebDriverWait(driver, 20)

# simulate human-like behavior
random_mouse_movement(driver)
human_scroll(driver)

# 🧠 Begin AI-Driven Form Entry
try:
    interact_by_label(driver, label="First Name", field_type="textbox", value="Lokendra")
    interact_by_label(driver, label="Last Name", field_type="textbox", value="Singh")
    interact_by_label(driver, label="Email", field_type="textbox", value="lokendra.singh@abjima.com")
    interact_by_label(driver, label="Phone Number", field_type="textbox", value="1234567890")
    interact_by_label(driver, label="ZIP Code", field_type="textbox", value="20678")
except Exception as e:
    logging.error(f"❌ Failed to interact with a field using AI: {e}")
# 🧠 AI-Driven Clicks for Radio + Buttons
try:
    interact_by_label(driver, label="Text", field_type="click")
    interact_by_label(driver, label="Send Me The Code", field_type="click")
    # Correct OTP Input
    wait_for_loader_to_disappear(driver)
    # ⏳ Wait for OTP Field to appear after sending OTP
    try:
        logging.info("[WAIT] Waiting for OTP input field to become available after sending code...")
        wait = WebDriverWait(driver, 15)  # Give generous time for slower systems
        otp_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.otp-field")))
        wait.until(EC.visibility_of(otp_field))
        logging.info("[WAIT] OTP input field is now visible and ready for typing.")
    except Exception as e:
        logging.error(f"[WAIT] OTP field did not appear in time: {e}")
        raise TimeoutException("❌ OTP field did not load after sending code")
    interact_by_label(driver, label="Code", field_type="textbox", value="123456")
    # Then explicitly click the button
    interact_by_label(driver, label="Verify Code", field_type="click")
except Exception as e:
    logging.error(f"❌ Failed during button or interaction click: {e}")
# Cleanup
logging.info("⏳ Bookslots Patient Information Page AI Test complete.")
input("Press Enter to quit...")
driver.quit()
logging.info("🧹 Session ended.")
