import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from selenium_utils.BrowserUtils.chrome_automation_launcher import run_chrome_automation
#from utils.BrowserUtils.edge_automation_launcher import run_edge_automation
from selenium_utils.elementFinderUtils.element_finder import ElementFinder
from pages.bookslot_info_otp_page import BookslotInfoOtpPage
from pages.schedular_page import WebSchedulerPage
# After selecting appointment slot
from selenium.common.exceptions import TimeoutException
import logging
import pathlib
import time
from selenium.common.exceptions import TimeoutException
import pytest
import allure
from data.test_inputs.faker_bookslot_data import generate_bookslot_payload
from utils.human_actions import simulate_typing, human_scroll, random_mouse_movement
import pytest
from pages.patient_information_page import PatientInformationPage


# ------------------------------------------------------------------------------------------------------------
# Generate test data
test_data = generate_bookslot_payload()
# Allure: attach input data
allure.attach(str(test_data), name="Input Payload", attachment_type=allure.attachment_type.JSON)
# Set up browser once
target = "https://bookslot-staging.centerforvein.com/?istestrecord=1"
driver = run_chrome_automation(target_url=target)
#driver = run_edge_automation(target_url=target)
finder = ElementFinder(driver)
# simulate human-like behavior
try:
    # Step 1: Book Slot Page
    #@allure.title("Full End-to-End Booking Flow")
    form = BookslotInfoOtpPage(driver)
    #form = BookslotInfoOtpPage(browser, simulate_human_behavior)
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
except TimeoutException as te:
    logging.error(f"⏱️ Timeout while waiting for an element: {te}")
    driver.save_screenshot("screenshots/timeout_error.png")
except Exception as e:
    logging.exception(f"💥 Unexpected error during test run: {e}")
    driver.save_screenshot("screenshots/unexpected_error.png")
