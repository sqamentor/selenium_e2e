import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from utils.form_filler_base import FormFillerBase

class InsurancePage(FormFillerBase):
    def __init__(self, driver, finder,test_data, timeout=15):
        self.driver = driver
        self.finder = finder
        self.wait = WebDriverWait(driver, timeout)
        #self.test_data = test_data  # ✅ Now it's available to all methods
        super().__init__(driver, self.wait, test_data, section="Insurance")

    def wait_for_insurance_form(self):
        try:
            self.wait.until(EC.invisibility_of_element_located((By.ID, "preloader")))
            self.wait.until(EC.presence_of_element_located((
                By.XPATH, "//h5[contains(text(),'Insurance')]"
            )))
            logging.info("✅ Insurance page loaded.")
        except Exception as e:
            logging.error(f"❌ Insurance form not found: {e}")
            self.driver.save_screenshot("screenshots/error_insurance_page_load.png")
            raise

    def fill_insurance_form(self):
        try:
            self.wait_for_insurance_form()

            # Each field - with visibility and fallback logging
            fields = {
                "MemberName": self.test_data["MemberName"],
                "idNumber": self.test_data["idNumber"],
                "GroupNumber": self.test_data["GroupNumber"],
                "PayerName": self.test_data["PayerName"]
            }

            for field_id, value in fields.items():
                logging.info(f"🔍 Finding visible element: id = {field_id}")
                try:
                    input_field = self.wait.until(EC.visibility_of_element_located((By.ID, field_id)))
                    input_field.clear()
                    input_field.send_keys(value)
                    logging.info(f"✅ Filled '{field_id}' with value: {value}")
                except Exception as e:
                    screenshot_path = f"screenshots/timeout_id_{field_id}_{int(time.time())}.png"
                    self.driver.save_screenshot(screenshot_path)
                    logging.error(f"❌ Timeout: Element not found using id = {field_id}")
                    raise

        except Exception as e:
            logging.error(f"❌ Error filling insurance form: {e}")
            raise

    def click_send_to_clinic(self):
        try:
            self.wait.until(EC.invisibility_of_element_located((By.ID, "preloader")))
            send_btn = self.wait.until(EC.element_to_be_clickable((By.ID, "SendToClinic")))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", send_btn)
            send_btn.click()
            logging.info("✅ Clicked 'Send to clinic' button.")
        except Exception as e:
            self.driver.save_screenshot("screenshots/error_click_send_to_clinic.png")
            logging.error(f"❌ Failed to click 'Send to clinic': {e}")
            raise
