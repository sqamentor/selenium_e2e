import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pathlib
import logging
from imports_manager import imports
# Assign dynamic imports to local variables
run_chrome_automation = imports['run_chrome_automation']
ElementFinder = imports['ElementFinder']
simulate_typing = imports['simulate_typing']
human_scroll = imports['human_scroll']
random_mouse_movement = imports['random_mouse_movement']
WebDriverWait = imports['WebDriverWait']
By = imports['By']
Keys = imports['Keys']
TimeoutException = imports['TimeoutException']
NoSuchElementException = imports['NoSuchElementException']
EC = imports['EC']  # ✅ Only if EC is fixed as shown earlier

from dotenv import load_dotenv
load_dotenv()

# ------------------------- Setup Logging ------------------------------------------------------------------------------------------------
#Define the directory and log file path
BASE_DIR = pathlib.Path(__file__).parent.resolve()
LOG_FILE_PATH = os.path.join(BASE_DIR, "Bookslot_info_otp_page.log")

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

# ------------------------------------------------------------------------------------------------------------
# UI Component: Book Slot Page (Center for Vein Restoration)
logging.info("🚀 Starting UI interaction with Book Slot page...")
target_url = imports["getenv"]("TARGET_URL")
driver = run_chrome_automation(target_url)
finder = ElementFinder(driver)

# simulate human-like behavior
random_mouse_movement(driver)
human_scroll(driver)

class BookslotInfoOtpPage:
    def __init__(self, driver, simulate_human_behavior:bool, timeout: int = 20):
        self.driver = driver
        self.simulated = simulate_human_behavior  # triggers on instantiation
        self.finder = ElementFinder(driver)
        self.wait = WebDriverWait(driver, timeout)
        self.timeout = timeout
        if simulate_human_behavior:
            # Called once at form start (fixture will already run)
            logging.info("🧠 Human-like behavior applied before form actions.")

    def wait_for_loader(self):
        try:
            loader = self.driver.find_element(By.ID, "loader")
            self.wait.until(EC.invisibility_of(loader))
            logging.info("✅ Loader disappeared.")
        except (TimeoutException, NoSuchElementException):
            logging.info("⏩ No loader or already hidden.")

    def verify_field_value(self, element, expected_value, field_name="Field"):
        actual_value = element.get_attribute("value").strip()
        
        # For numeric match (input mask): clean digits
        if expected_value.isdigit():
            clean_actual = ''.join(filter(str.isdigit, actual_value))
            clean_expected = ''.join(filter(str.isdigit, expected_value))
        else:
            clean_actual = actual_value
            clean_expected = expected_value

        if clean_actual == clean_expected:
            logging.info(f"✅ {field_name} verified: {actual_value}")
            return True
        else:
            logging.warning(f"❌ {field_name} mismatch. Expected: '{expected_value}', Got: '{actual_value}'")
            return False

    def type_text(self, locator_type: str, locator_value: str, text: str, field_name: str):
        element = self.finder.find(locator_type, locator_value, visible=True)
        if element:
            element.clear()
            simulate_typing(element, text)  # ✅ Simulate human typing
            #element.send_keys(text)
            logging.info(f"✅ Entered '{text}' in {field_name}.")
            self.verify_field_value(element, text, field_name)  # ✅ Validation here
        else:
            logging.error(f"❌ {field_name} field not found.")

    def enter_first_name(self, first_name):
        self.type_text("id", "FirstName", first_name, "First Name")

    def enter_last_name(self, last_name):
        self.type_text("id", "LastName", last_name, "Last Name")

    def enter_email(self, email):
        self.type_text("id", "Email", email, "Email")

    def enter_zip(self, zip_code):
        self.type_text("id", "ZipCode", zip_code, "ZIP Code")
#-------------------------------------------------------------------------------------------------------------------------
    def enter_phone_number(self, phone_number):
        try:
            # Locate inner <input> inside the p-inputmask wrapper
            wrapper = self.driver.find_element(By.ID, "CellPhone")
            inner_input = wrapper.find_element(By.CSS_SELECTOR, "input.p-inputtext")

            self.driver.execute_script("arguments[0].scrollIntoView(true);", inner_input)
            #time.sleep(1)

            inner_input.click()
            inner_input.clear()
            inner_input.send_keys(Keys.HOME)  # ✅ move cursor to beginning

            for digit in phone_number:
                inner_input.send_keys(digit)
                #time.sleep(0.1)

            logging.info(f"✅ Entered phone number: {phone_number}")
        except Exception as e:
            logging.error(f"❌ Failed to enter phone number: {e}")

    def select_contact_method(self, method: str):
        method = method.capitalize()
        try:
            label = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.XPATH, f"//label[normalize-space()='{method}']"))
            )
            label.click()
            logging.info(f"✅ Selected contact method: {method}")
        except Exception as e:
            logging.error(f"❌ Failed to select contact method '{method}': {e}")

#---------------------------------------------------------------------------------------------------------------------------------------
    def click_send_code(self):
        btn = self.finder.find("xpath", "(//button[normalize-space()='Send Me The Code'])[1]", clickable=True)
        if btn:
            btn.click()
            logging.info("✅ 'Send Me The Code' button clicked.")
        else:
            logging.error("❌ 'Send Me The Code' button not found.")

    def enter_code(self, code: str):
        try:
            otp = self.finder.find("xpath", "//input[contains(@class, 'otp-field')]", visible=True, clickable=True)
            if otp:
                otp.clear()
                otp.send_keys(code)
                logging.info(f"✅ Entered OTP: {code}")
            else:
                logging.error("❌ OTP input field not found.")
        except Exception as e:
            logging.error(f"❌ Failed to Entered OTP: {e}")

    def verify_code(self):
        btn = self.finder.find("xpath", "(//button[normalize-space()='Verify Code'])[1]", clickable=True)
        if btn:
            btn.click()
            logging.info("✅ 'Verify Code' button clicked.")
        else:
            logging.error("❌ 'Verify Code' button not found.")

if __name__ == "__main__":
    # Simulate human-like behavior before filling form
    random_mouse_movement(driver)
    human_scroll(driver)

    form = BookslotInfoOtpPage(driver)
    form.enter_first_name("Lokendra")
    form.enter_last_name("Singh")
    form.enter_email("lokendra.singh@abjima.com")
    form.enter_phone_number("1234567890")
    form.enter_zip("20678")
    form.select_contact_method("Text")
    form.click_send_code()
    form.enter_code("123456")
    form.verify_code()

    logging.info("⏳ Bookslots Patient Information Page Test complete. Inspect form state.")
    input("Press Enter to quit...")
    driver.quit()
    logging.info("🧹 Session ended.")
