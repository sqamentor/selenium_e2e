import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class PatientExistantPage:
    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
    
    def is_displayed(self):
        try:
            # This is the element that confirms the "Existing Patient" page is showing
            self.wait.until(EC.visibility_of_element_located((
                By.XPATH,
                "//div[contains(text(),'we see you have an upcoming appointment')]"
            )))
            logging.info("✅ Existing Patient page detected.")
            return True
        except:
            logging.info("ℹ️ Existing Patient page not detected.")
            return False

    def handle_existing_patient_page(self):
        try:
            # ✅ Wait for conditional text block
            message_elem = self.wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//div[contains(text(),'To make modifications to this appointment')]")
                )
            )
            message_text = message_elem.text.strip()
            logging.info(f"📋 Existing Patient Message: {message_text}")

            # ✅ Click "Go To Home" button
            go_home_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Go To Home')]"))
            )
            go_home_btn.click()
            logging.info("✅ Clicked 'Go To Home' button.")

            # ✅ Wait for redirect and print the current URL
            self.wait.until(lambda driver: driver.current_url != "")  # ensure navigation happens
            logging.info(f"🌐 Redirected to URL: {self.driver.current_url}")

        except Exception as e:
            self.driver.save_screenshot("screenshots/error_patient_exists.png")
            logging.warning(f"⚠️ Patient Existant page not shown or failed to process: {e}")
