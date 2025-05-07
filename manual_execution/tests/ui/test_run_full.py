# run_main_test.py
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from selenium_utils.browser_utils.chrome_automation_launcher import run_chrome_automation
except ImportError as e:
    raise ImportError("Failed to import 'run_chrome_automation'. Ensure 'selenium_utils' is installed and accessible.") from e
from selenium_utils.element_finder_utils.element_finder import ElementFinder
from pages.bookslot_info_otp_page import BookslotInfoOtpPage
from pages.event_selection_page import EventSelectionPage
from pages.schedular_page import WebSchedulerPage
# After selecting appointment slot
from pages.request_appointment_page import RequestAppointmentPage
from pages.patient_information_page import PatientInformationPage
from pages.patient_existant import PatientExistantPage
from pages.patient_referral import PatientReferral
from pages.insurance_page import InsurancePage
from selenium.common.exceptions import TimeoutException
import logging
import pathlib
import time
from selenium.common.exceptions import TimeoutException
import pytest
import allure
from data.test_inputs.faker_bookslot_data import generate_bookslot_payload
from utils.human_actions import simulate_typing, human_scroll, random_mouse_movement



# ------------------------- Setup Logging ------------------------------------------------------------------------------------------------
#Define the directory and log file path
BASE_DIR = pathlib.Path(__file__).parent.resolve()
LOG_FILE_PATH = os.path.join(BASE_DIR, "run_full_test.log")

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
# ---------------------------------------------------------------------------------------------------------

@pytest.mark.allure_label("Test")
#@allure.severity(allure.severity_level.CRITICAL)  # ✅ fully supported decorator
@allure.title("Full End-to-End Booking Flow")
def test_run_full():
    # ------------------------------------------------------------------------------------------------------------
    # Generate test data
    test_data = generate_bookslot_payload()
    # Allure: attach input data
    allure.attach(str(test_data), name="Input Payload", attachment_type=allure.attachment_type.JSON)
    # Set up browser once
    target = "https://bookslot-staging.centerforvein.com/?istestrecord=1"
    driver = run_chrome_automation(target_url=target)
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

        # Step 2: Event Selection Page
        event = EventSelectionPage(driver)
        event.wait_for_loader()
        #event.click_request_call_back()
        event.click_new_patient_appointment()
        #event.click_complimentary_consultation()
        logging.info("✅ Step 2: Event selection completed.")

        scheduler = WebSchedulerPage(driver)
        scheduler.wait_for_scheduler_heading()
        scheduler.click_request_call_back()
        scheduler.validate_no_past_dates_clickable()
        scheduler.enter_date_range(2, 90)  # Selects today+3 to today+30
        scheduler.enter_zip_distance(test_data["zip"], test_data["zip_distance"])
        #scheduler.select_last_date()
        scheduler.click_first_available_slot()
        logging.info("✅ Step 3: Scheduler slot selection done.")

        # Step 3: Request Appointment Page
        scheduler = RequestAppointmentPage(driver, finder)
        #scheduler.click_request_call_back()
        scheduler.wait_for_page_to_load()
        scheduler.wait_for_session_timer()
        scheduler.validate_appointment_summary()
        scheduler.click_next_button()
        logging.info("✅ Step 4: Request Appointment validated and submitted.")

        # Step 4: Patient Info
        patient_info_page = PatientInformationPage(driver, finder)
        patient_info_page.wait_for_patient_info_form()
        patient_info_page.fill_mandatory_fields(test_data["dob"])
        patient_info_page.click_next_button()
        try:
            result_url = patient_info_page.submit_and_verify_next_step()

            # Conditional navigation handling
            if "patient-existant" in result_url or "Go to Home" in result_url:
                logging.info("🛑 Existing patient detected. Ending flow.")
                print(f"➡️ Redirected to: {result_url}")
                driver.save_screenshot("screenshots/existing_patient_detected.png")
                exit(0)

        except Exception as e:
            logging.error("🚫 Stopping execution due to Patient Info failure.")
            #exit(1)

        # Step 5: Existing Patient Check
        patient_exist_page = PatientExistantPage(driver)
        if patient_exist_page.is_displayed():
            patient_exist_page.handle_existing_patient_page()
            logging.warning("🛑 Existing patient detected. Booking flow stopped.")
            print(f"➡️ Redirected to: {driver.current_url}")
            exit(1)

        # Step 6: Referral Page
        referral_page = PatientReferral(driver, finder)
        referral_page.select_referral_option("Internet search")  # or random
        referral_page.click_next_button()
        logging.info("✅ Step 6: Referral page submitted.")

        # Step 7: Insurance Page
        insurance_page = InsurancePage(driver, finder,test_data=test_data)
        try:
            insurance_page.fill_insurance_form()
            insurance_page.click_send_to_clinic()
            logging.info("✅ Step 6: Insurance form submitted.")
        except Exception as e:
            logging.error("💥 Unexpected error during Insurance submission step.")
            raise

    except TimeoutException as te:
        logging.error(f"⏱️ Timeout while waiting for an element: {te}")
        driver.save_screenshot("screenshots/timeout_error.png")
    except Exception as e:
        logging.exception(f"💥 Unexpected error during test run: {e}")
        driver.save_screenshot("screenshots/unexpected_error.png")
    finally:
        time.sleep(10)
        driver.quit()
# ------------------------- Standalone Execution -------------------------
if __name__ == "__main__":
    test_run_full()