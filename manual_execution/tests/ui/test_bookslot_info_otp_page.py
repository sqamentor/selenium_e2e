import pathlib
import logging
import sys, os

# Ensure project root is added dynamically regardless of depth
current_file = os.path.abspath(__file__)
project_root = os.path.abspath(os.path.join(current_file, *[".."] * 4))  # 4 levels up from 'ui'
print(f"Project root: {project_root}")

# Import BookslotInfoOtpPage
sys.path.append(os.path.join(project_root, "manual_execution", "pages"))
sys.path.append(os.path.join(project_root, "manual_execution", "pages"))
try:
    from bookslot_info_otp_page import BookslotInfoOtpPage
except ModuleNotFoundError as e:
    logging.error(f"Module not found: {e}")
    raise

if project_root not in sys.path:
    sys.path.insert(0, project_root)
print(f"sys.path: {sys.path}")

from imports_manager import imports
import selenium.webdriver.support.expected_conditions as EC
import allure

print("Current sys.path:", sys.path)

#-------------------------------------------------------------------------------------------------
# Assign dynamic imports to local variables
run_chrome_automation = imports['run_chrome_automation']
ElementFinder = imports['ElementFinder']
simulate_typing = imports['simulate_typing']
human_scroll = imports['human_scroll']
random_mouse_movement = imports['random_mouse_movement']
simulate_human_behavior = imports['simulate_human_behavior']
WebDriverWait = imports['WebDriverWait']
By = imports['By']
Keys = imports['Keys']
TimeoutException = imports['TimeoutException']
NoSuchElementException = imports['NoSuchElementException']
WebDriverWait = imports['WebDriverWait']
EC = imports["EC"]  # ✅ Only if EC is fixed as shown earlier
faker_bookslot_payload = imports["generate_bookslot_payload"]

from dotenv import load_dotenv
load_dotenv()
# ------------------------------------------------------------------------------------------------------------
# Generate test data
test_data = faker_bookslot_payload()
# Allure: attach input data
allure.attach(str(test_data), name="Input Payload", attachment_type=allure.attachment_type.JSON)
# Set up browser once
target = "https://bookslot-staging.centerforvein.com/?istestrecord=1"
driver = run_chrome_automation(target_url=target)
finder = ElementFinder(driver)
# simulate human-like behavior
try:
    # Step 1: Book Slot Page
    @allure.title("Full End-to-End Booking Flow")
    def book_slot():
        #form = BookslotInfoOtpPage(driver)
        form = BookslotInfoOtpPage(driver, simulate_human_behavior)  # Updated to include simulate_human_behavior
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
    
    book_slot()
except TimeoutException as te:
    logging.error(f"⏱️ Timeout while waiting for an element: {te}")
    driver.save_screenshot("screenshots/timeout_error.png")
except Exception as e:
    logging.exception(f"💥 Unexpected error during test run: {e}")
    driver.save_screenshot("screenshots/unexpected_error.png")
