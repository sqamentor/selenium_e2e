import re
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pathlib
import os

# ------------------------- Setup Logging ------------------------------------------------------------------------------------------------
#Define the directory and log file path
BASE_DIR = pathlib.Path(__file__).parent.resolve()
LOG_FILE_PATH = os.path.join(BASE_DIR, "RequestAppointmentPage.log")

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

class RequestAppointmentPage:
    def __init__(self, driver, finder, timeout=30):
        self.driver = driver
        self.finder = finder
        self.wait = WebDriverWait(driver, timeout)

    def wait_for_page_to_load(self):
        try:
            # Ensure loader is gone
            self.wait.until(EC.invisibility_of_element_located((By.ID, "preloader")))
            logging.info("✅ Preloader vanished.")

            # Check page heading
            self.wait.until(EC.visibility_of_element_located((
                By.XPATH, "//h4[contains(text(),'Request an Appointment')]"
            )))
            logging.info("✅ Request Appointment page loaded successfully.")
        except Exception as e:
            path = "screenshots/error_request_appointment_page_load.png"
            self.driver.save_screenshot(path)
            logging.error(f"❌ Request Appointment page did not load properly: {e}")
            raise

    def wait_for_session_timer(self):
        try:
            timer_text = self.finder.find("xpath", "//div[contains(text(),'Session will be expiring')]", visible=True).text
            logging.info(f"⏳ Session countdown detected: {timer_text}")
        except Exception as e:
            logging.warning(f"⚠️ Session expiration timer not found: {e}")

    def click_next_button(self):
        try:
            next_btn = self.finder.find("xpath", "//button[contains(text(),'Next')]", clickable=True)
            next_btn.click()
            logging.info("✅ Clicked 'Next' button.")
        except Exception as e:
            logging.error(f"❌ Failed to click 'Next' button: {e}")
            self.driver.save_screenshot("screenshots/error_click_next.png")
            raise

    def click_request_call_back(self):
        try:
            callback_btn = self.finder.find("xpath", "//button[contains(.,'Request Call Back')]", clickable=True)
            callback_btn.click()
            logging.info("✅ Clicked 'Request Call Back' button.")
        except Exception as e:
            logging.warning(f"⚠️ 'Request Call Back' button not available or clickable: {e}")

    def validate_appointment_summary(self):
            try:
                self.wait.until(EC.presence_of_element_located((By.XPATH, "//h4[contains(text(),'Appointment Details')]")))
                logging.info("✅ Appointment Details section detected.")

                date, time, location, address = None, None, None, None

                # 🔁 1. Loop through summary blocks
                summary_blocks = self.driver.find_elements(By.XPATH, "//div[contains(@class,'grid') or contains(@class,'flex')]")
                #logging.info(f"Summary_Block is  {summary_blocks}")
                for block in summary_blocks:
                    text = block.text.strip()
                    #logging.info(f"Block Text is  {text}")

                    if not date and re.search(r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+[A-Z][a-z]{2,}\s+\d{1,2}", text):
                        date = text
                        #logging.info(f"Date is  {date}")

                    elif not time and re.search(r"\b\d{1,2}:\d{2}\s?(AM|PM)", text, re.IGNORECASE):
                        time = text
                        #logging.info(f"Time is  {time}")

                    elif not location and ("CVR" in text or "Center" in text):
                        location = text
                        #logging.info(f"Location is  {location}")

                #🔁 2. Address with primary and fallback strategies
                try:
                    address_elem = self.wait.until(EC.visibility_of_element_located((
                        By.XPATH, "//a[contains(@href,'centerforvein') or contains(text(),'Suite') or contains(text(),'Drive')]"
                    )))
                    address = address_elem.text.strip()
                    #logging.info(f"Address1 is  {address}")
                except:
                    try:
                        # Try getting raw address if not a link
                        address = self.driver.find_element(By.XPATH, "//div[contains(text(),', MD')]").text.strip()
                        #logging.info(f"Address2 is  {address}")
                    except:
                        logging.warning("⚠️ Could not find appointment address.")

                # 🔐 Assertions
                assert date is not None, "❌ Appointment date not found."
                assert time is not None, "❌ Appointment time not found."
                assert location is not None, "❌ Appointment location not found."
                assert address is not None, "❌ Appointment address not found."

                # ✅ Final output
                summary = f"""
                📅 Date     : {date}
                ⏰ Time     : {time}
                🏥 Location : {location}
                📍 Address  : {address}
                """
                logging.info(f"✅ Appointment Summary:\n{summary.strip()}")

            except AssertionError as ae:
                logging.error(f"❌ Appointment summary failed: {ae}")
                self.driver.save_screenshot("screenshots/error_appointment_summary_assertion.png")
                raise

            except Exception as e:
                logging.error(f"❌ Unexpected error during summary validation: {e}")
                self.driver.save_screenshot("screenshots/error_appointment_summary_exception.png")
                raise