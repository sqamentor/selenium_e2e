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
human_type = imports.get("human_type")
human_click = imports.get("human_click")
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
@allure.title("Full End-to-End Booking Flow")
def test_run_full():
    try:
        # Step 1: Book Slot Page
        form = BookslotInfoOtpPage(driver, simulate_human_behavior)

        # Call methods directly with required arguments
        form.enter_first_name(test_data["first_name"])
        form.enter_last_name(test_data["last_name"])
        form.enter_email(test_data["email"])
        form.enter_phone_number(test_data["phone_number"])
        form.enter_zip(test_data["zip"])

        # Simulate human-like click for contact method and send code
        form.select_contact_method(test_data["contact_method"])
        form.click_send_code()

        # Simulate human-like typing for verification code
        form.enter_code(test_data["verification_code"])
        form.verify_code()
        logging.info("✅ Step 1: Book Slot completed.")

        # Step 2: Event Selection Page
        event = EventSelectionPage(driver)
        event.wait_for_loader()
        human_click(driver, event.click_new_patient_appointment_button())
        logging.info("✅ Step 2: Event selection completed.")

        # Step 3: Scheduler Page
        scheduler = WebSchedulerPage(driver)
        scheduler.wait_for_scheduler_heading()
        human_click(driver, scheduler.click_request_call_back_button())
        scheduler.validate_no_past_dates_clickable()
        scheduler.enter_date_range(2, 90)  # Selects today+2 to today+90
        scheduler.enter_zip_distance(test_data["zip"], test_data["zip_distance"])
        human_click(driver, scheduler.click_first_available_slot_button())
        logging.info("✅ Step 3: Scheduler slot selection done.")

        # Step 4: Request Appointment Page
        request_appointment = RequestAppointmentPage(driver, finder)
        request_appointment.wait_for_page_to_load()
        request_appointment.wait_for_session_timer()
        request_appointment.validate_appointment_summary()
        human_click(driver, request_appointment.click_next_button())
        logging.info("✅ Step 4: Request Appointment validated and submitted.")

        # Step 5: Patient Info Page
        patient_info_page = PatientInformationPage(driver, finder)
        patient_info_page.wait_for_patient_info_form()
        human_type(patient_info_page.enter_dob_field(), test_data["dob"])
        human_click(driver, patient_info_page.click_next_button())
        try:
            result_url = patient_info_page.submit_and_verify_next_step()

            # Conditional navigation handling
            if "patient-existant" in result_url or "Go to Home" in result_url:
                logging.info("🛑 Existing patient detected. Ending flow.")
                print(f"➡️ Redirected to: {result_url}")
                driver.save_screenshot("screenshots/existing_patient_detected.png")
                return

        except Exception as e:
            logging.error("🚫 Stopping execution due to Patient Info failure.")
            raise

        # Step 6: Referral Page
        referral_page = PatientReferral(driver, finder)
        referral_page.select_referral_option("Internet search")  # or random
        human_click(driver, referral_page.click_next_button())
        logging.info("✅ Step 6: Referral page submitted.")

        # Step 7: Insurance Page
        insurance_page = InsurancePage(driver, finder, test_data=test_data)
        try:
            insurance_page.fill_insurance_form()
            human_click(driver, insurance_page.click_send_to_clinic_button())
            logging.info("✅ Step 7: Insurance form submitted.")
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
        # Simulate idle before closing
        time.sleep(5)  # Simulate idle time before closing
        driver.quit()

# ------------------------- Standalone Execution -------------------------
if __name__ == "__main__":
    test_run_full()