import logging
import time
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class FormFillerBase:
    def __init__(self, driver, wait, test_data, section=""):
        self.driver = driver
        self.wait = wait
        self.test_data = test_data
        self.section = section

        # Attach test data to Allure once per form section
        if self.test_data:
            allure.attach(
                str(self.test_data),
                name=f"Input Data - {self.section or 'Form'}",
                attachment_type=allure.attachment_type.JSON
            )

    def fill_form_fields(self, fields_dict):
        for field_id, value in fields_dict.items():
            try:
                logging.info(f"🔍 Locating field '{field_id}'")
                input_field = self.wait.until(EC.visibility_of_element_located((By.ID, field_id)))
                input_field.clear()
                input_field.send_keys(value)
                logging.info(f"✅ Filled '{field_id}' with value: {value}")
            except Exception as e:
                screenshot_path = f"screenshots/timeout_id_{field_id}_{int(time.time())}.png"
                self.driver.save_screenshot(screenshot_path)
                logging.error(f"❌ Could not fill '{field_id}' | Error: {e}")
                raise
