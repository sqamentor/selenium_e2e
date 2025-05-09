import logging
import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

class PatientInformationPage:
    def __init__(self, driver, finder, timeout=20):
        self.driver = driver
        self.finder = finder
        self.wait = WebDriverWait(driver, timeout)

    def wait_for_patient_info_form(self):
        try:
            self.wait.until(EC.invisibility_of_element_located((By.ID, "preloader")))
            self.wait.until(EC.visibility_of_element_located((
                By.XPATH, "//h5[contains(text(),'Patient Information')]"
            )))
            logging.info("✅ Patient Information form loaded.")
        except Exception as e:
            screenshot_path = "screenshots/error_patient_info_page_load.png"
            self.driver.save_screenshot(screenshot_path)
            logging.error(f"❌ Patient Information form did not load. Message: {e}")
            raise

    def fill_mandatory_fields(self, dob: str = "01/01/1990"):
        try:
            # ✅ Fill Sex (Dropdown)
            gender_field = self.wait.until(EC.element_to_be_clickable((By.ID, "Gender")))
            gender_field.click()
            time.sleep(1)
            gender_options = self.driver.find_elements(By.XPATH, "//li[@role='option']")
            assert gender_options, "❌ No gender options found in dropdown."

            selected = random.choice(gender_options)
            selected_text = selected.text.strip()
            selected.click()
            logging.info(f"✅ Selected Gender: {selected_text}")

            # ✅ Fill DOB
            dob_input = self.wait.until(EC.visibility_of_element_located((By.ID, "icondisplay")))
            dob_input.clear()
            dob_input.send_keys(dob)
            dob_input.send_keys(Keys.TAB)
            logging.info(f"✅ Date of Birth entered: {dob}")

        except Exception as e:
            screenshot_path = "screenshots/error_fill_mandatory_fields.png"
            self.driver.save_screenshot(screenshot_path)
            logging.error(f"❌ Failed to fill mandatory fields: {e}")
            raise

    def click_next_button(self):
        try:
            next_button = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, "//button[contains(.,'Next')]"
            )))
            next_button.click()
            logging.info("✅ Clicked 'Next' button.")
        except Exception as e:
            screenshot_path = "screenshots/error_click_next_patient.png"
            self.driver.save_screenshot(screenshot_path)
            logging.error(f"❌ Failed to click 'Next' on Patient Information page: {e}")
            raise
    def submit_and_verify_next_step(self):
        
        WebDriverWait(self.driver, 20).until(EC.invisibility_of_element_located((By.ID, "preloader")))
        try:
            # Ensure mandatory fields are filled first
            #self.fill_mandatory_fields("03/15/1991")
            #logging.info("✅ Mandatory fields filled.")

            # Check if 'Next' is enabled
            next_btn = self.driver.find_element(By.XPATH, "//button[contains(text(),'Next')]")
            is_enabled = next_btn.is_enabled()
            logging.info(f"📋 Is 'Next' button enabled? {is_enabled}")

            # Optional force-submit if Angular fails to trigger form submission
            #self.driver.execute_script("""
            #    const form = document.querySelector('form');
            #    if (form) {
            #        form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
            #    }
            #""")
            #logging.info("✅ Force-submitted the patient info form via JavaScript.")

            if not is_enabled:
                logging.warning("⚠️ 'Next' button is disabled. Possible validation issue.")
                raise Exception("Next button not enabled")

            # Click the button and submit
            #self.click_next_button()

            # Allow frontend event propagation
            #time.sleep(1)
            #self.driver.execute_script("document.querySelector('form')?.dispatchEvent(new Event('submit'));")

            # Wait for possible navigation or visible content changes
            WebDriverWait(self.driver, 15).until(lambda d: (
                "patient-referral" in d.current_url or
                "insurance" in d.current_url or
                "patient-existant" in d.current_url or
                len(d.find_elements(By.XPATH, "//h5[contains(text(), 'Referral')]")) > 0 or
                len(d.find_elements(By.XPATH, "//h5[contains(text(), 'Insurance')]")) > 0 or
                len(d.find_elements(By.XPATH, "//h1[contains(text(), 'Patient Already Exists')]")) > 0 or
                len(d.find_elements(By.XPATH, "//button[contains(text(),'Go to Home')]")) > 0
            ))

            logging.info(f"🔀 Navigation after patient info submission: {self.driver.current_url}")
            return self.driver.current_url

        except TimeoutException:
            self.driver.save_screenshot("screenshots/patient_info_timeout.png")
            logging.error("⏱️ Timeout while waiting for post-patient-info navigation or element load.")
            raise
        except Exception as e:
            self.driver.save_screenshot("screenshots/patient_info_submission_error.png")
            logging.exception("💥 Unexpected error during Patient Info submission step.")
            raise
