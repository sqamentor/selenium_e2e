# run_main_test.py
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

import pathlib
import time
import logging
import sys
import os
import selenium.webdriver.support.expected_conditions as EC
import pytest
import allure
from auto_importer import smart_import
# Dynamically import the imports dictionary from imports_manager
get_imports = smart_import("imports_manager.get_imports")
imports = get_imports() if get_imports else {}
# Pull specific objects dynamically
run_chrome_automation = imports.get("run_chrome_automation")
ElementFinder = imports.get("ElementFinder")
WebSchedulerPage = imports.get("WebSchedulerPage")
simulate_typing = imports.get("simulate_typing")
human_scroll = imports.get("human_scroll")
random_mouse_movement = imports.get("random_mouse_movement")
simulate_human_behavior = imports.get("simulate_human_behavior")
WebDriverWait = imports.get("WebDriverWait")
By = imports.get("By")
RequestAppointmentPage = imports.get("RequestAppointmentPage")
EventSelectionPage = imports.get("EventSelectionPage")
PatientInformationPage = imports.get("PatientInformationPage")
PatientExistantPage = imports.get("PatientExistantPage")
PatientReferral = imports.get("PatientReferral")
InsurancePage = imports.get("InsurancePage")
Keys = imports.get("Keys")
TimeoutException = imports.get("TimeoutException")
NoSuchElementException = imports.get("NoSuchElementException")
faker_bookslot_payload = imports.get("generate_bookslot_payload")

if not run_chrome_automation:
    raise ImportError("❌ run_chrome_automation was not imported.")
# Load environment variables
smart_import("dotenv.load_dotenv")()
# Attach generated test data to Allure
if not faker_bookslot_payload:
    raise ImportError("❌ generate_bookslot_payload was not imported.")
test_data = faker_bookslot_payload()
allure.attach(str(test_data), name="Input Payload", attachment_type=allure.attachment_type.JSON)
# Generate test data
# Allure: attach input data
allure.attach(str(test_data), name="Input Payload", attachment_type=allure.attachment_type.JSON)
# Start browser and form logic
target = os.getenv("TARGET_URL")
driver = run_chrome_automation(target)
finder = ElementFinder(driver)
BookslotInfoOtpPage = smart_import("manual_execution.pages.bookslot_info_otp_page.BookslotInfoOtpPage")
@allure.title("Full End-to-End Booking Flow")


@pytest.mark.allure_label("Test")
#@allure.severity(allure.severity_level.CRITICAL)  # ✅ fully supported decorator
@allure.title("Full End-to-End Booking Flow")
def test_run_full():
    try:
        # Step 1: Book Slot Page
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