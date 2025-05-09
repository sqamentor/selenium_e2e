import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

import pathlib
import time
import logging
import sys
import os
import selenium.webdriver.support.expected_conditions as EC
import allure
from auto_importer import smart_import
# Dynamically import the imports dictionary from imports_manager
get_imports = smart_import("imports_manager.get_imports")
imports = get_imports() if get_imports else {}
# Pull specific objects dynamically
run_chrome_automation = imports.get("run_chrome_automation")
ElementFinder = imports.get("ElementFinder")
simulate_typing = imports.get("simulate_typing")
human_scroll = imports.get("human_scroll")
random_mouse_movement = imports.get("random_mouse_movement")
simulate_human_behavior = imports.get("simulate_human_behavior")
WebDriverWait = imports.get("WebDriverWait")
By = imports.get("By")
Keys = imports.get("Keys")
TimeoutException = imports.get("TimeoutException")
NoSuchElementException = imports.get("NoSuchElementException")
faker_bookslot_payload = imports.get("generate_bookslot_payload")
if not run_chrome_automation:
    raise ImportError("❌ run_chrome_automation was not imported.")
# Load environment variables
smart_import("dotenv.load_dotenv")()
# Attach generated test data to Allure
test_data = faker_bookslot_payload()
allure.attach(str(test_data), name="Input Payload", attachment_type=allure.attachment_type.JSON)
# Start browser and form logic
target = os.getenv("TARGET_URL")
driver = run_chrome_automation(target)
finder = ElementFinder(driver)
BookslotInfoOtpPage = smart_import("manual_execution.pages.bookslot_info_otp_page.BookslotInfoOtpPage")
@allure.title(" Book Slot Information OTP Page Flow")
def book_slot():
    form = BookslotInfoOtpPage(driver, simulate_human_behavior)
    form.enter_first_name(test_data["first_name"])
    form.enter_last_name(test_data["last_name"])
    form.enter_email(test_data["email"])
    form.enter_phone_number(test_data["phone_number"])
    form.enter_zip(test_data["zip"])
    form.select_contact_method(test_data["contact_method"])
    form.click_send_code()
    form.enter_code(test_data["verification_code"])
    form.verify_code()
    logging.info("✅ Step 1: Book Slot completed.")
    time.sleep(100)
try:
    book_slot()
except TimeoutException as te:
    logging.error(f"⏱️ Timeout while waiting for an element: {te}")
    driver.save_screenshot("screenshots/timeout_error.png")
except Exception as e:
    logging.exception(f"💥 Unexpected error during test run: {e}")
    driver.save_screenshot("screenshots/unexpected_error.png")
