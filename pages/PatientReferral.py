from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import logging
import time


class PatientReferral:
    def __init__(self, driver, finder, timeout=15):
        self.driver = driver
        self.finder = finder
        self.wait = WebDriverWait(driver, timeout)

    def wait_for_referral_page(self):
        try:
            self.wait.until(EC.invisibility_of_element_located((By.ID, "preloader")))
            self.wait.until(EC.visibility_of_element_located((
                By.XPATH, "//h5[contains(text(),'How did you hear about us?')]"
            )))
            logging.info("✅ Referral question loaded successfully.")
        except Exception as e:
            self.driver.save_screenshot("screenshots/error_wait_referral_page.png")
            logging.error(f"❌ Referral question not visible: {e}")
            raise

    def select_referral_option(self, option_text="Internet search"):
        try:
            self.wait_for_referral_page()

            option_btn = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, f"//button[.//span[text()='{option_text}']]"
            )))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option_btn)
            time.sleep(0.5)
            option_btn.click()
            logging.info(f"✅ Selected referral option: {option_text}")

        except Exception as e:
            self.driver.save_screenshot("screenshots/error_select_referral_option.png")
            logging.error(f"❌ Failed to select referral option '{option_text}': {e}")
            raise

    def click_next_button(self):
        try:
            self.wait.until(EC.invisibility_of_element_located((By.ID, "preloader")))
            next_btn = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, "//button[@id='patient-referral' and not(@disabled)]"
            )))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
            time.sleep(0.5)
            next_btn.click()
            logging.info("✅ Clicked 'Next' button on Referral page.")
        except Exception as e:
            self.driver.save_screenshot("screenshots/error_click_next_referral.png")
            logging.error(f"❌ Failed to click 'Next' on referral page: {e}")
            raise
