import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from datetime import datetime, timedelta

from selenium_utils.elementFinderUtils.element_finder import ElementFinder

class WebSchedulerPage:
    def __init__(self, driver, timeout=25):
        self.driver = driver
        self.finder = ElementFinder(driver)
        self.wait = WebDriverWait(driver, timeout)
        self.timeout = timeout

    def wait_for_scheduler_heading(self):
        try:
            self.finder.find("xpath", "//h5[contains(text(), 'Web Scheduler')]", visible=True)
            logging.info("✅ Web Scheduler page loaded.")
        except TimeoutException:
            logging.error("❌ Web Scheduler heading not found.")

    def enter_date_range(self, from_offset_days=2, to_offset_days=90):
        # Compute dynamic dates
        today = datetime.today()
        from_date = today + timedelta(days=from_offset_days)
        to_date = today + timedelta(days=to_offset_days)

        from_str = from_date.strftime("%b %d, %Y")  # e.g., Apr 16, 2025
        to_str = to_date.strftime("%b %d, %Y")

        try:
            from_input = self.finder.find("xpath", "(//input[@role='combobox'])[1]", visible=True)
            to_input = self.finder.find("xpath", "(//input[@role='combobox'])[2]", visible=True)

            if not from_input or not to_input:
                logging.error("❌ Date inputs not found.")
                return

            # Click & clear From Date
            from_input.click()
            from_input.send_keys(Keys.CONTROL + "a")
            from_input.send_keys(Keys.BACKSPACE)
            from_input.send_keys(from_str)
            from_input.send_keys(Keys.TAB)
            logging.info(f"✅ Set From Date: {from_str}")

            # Click & clear To Date
            to_input.click()
            to_input.send_keys(Keys.CONTROL + "a")
            to_input.send_keys(Keys.BACKSPACE)
            to_input.send_keys(to_str)
            to_input.send_keys(Keys.TAB)
            logging.info(f"✅ Set To Date: {to_str}")

            # Validate calendar doesn't allow past dates
            past_day_elements = self.driver.find_elements(By.XPATH, "//td[@class='ui-datepicker-unselectable ui-state-disabled']")
            if past_day_elements:
                logging.info(f"✅ Calendar properly disabled past dates.")
            else:
                logging.warning("⚠️ Past dates might be selectable — review calendar settings.")

        except Exception as e:
            logging.error(f"❌ Error setting date range: {e}")

    def validate_no_past_dates_clickable(self):
        past_dates = self.driver.find_elements(By.XPATH, "//td[contains(@class,'ui-state-disabled')]")
        for el in past_dates:
            try:
                el.click()
                logging.warning("⚠️ Past date was clickable — check calendar config!")
                return False
            except:
                continue
        logging.info("✅ All past dates correctly unclickable.")
        return True

    def enter_zip_distance(self, zip_code="20678", miles="30"):
        zip_input = self.finder.find("xpath", "(//input[@formcontrolname='PinCode'])[1]", visible=True)
        miles_input = self.finder.find("xpath", "(//input[@formcontrolname='Mile'])[1]", visible=True)

        if zip_input and miles_input:
            miles_input.clear()
            miles_input.send_keys(miles)

            zip_input.clear()
            zip_input.send_keys(zip_code)

            search_btn = self.finder.find("xpath", "//button[contains(@class,'scheduler-btn')]", clickable=True)
            if search_btn:
                search_btn.click()
                logging.info("✅ Clicked search button.")
            else:
                logging.warning("⚠️ Search button not found.")
        else:
            logging.error("❌ Zip code or distance input not found.")

    def select_last_date(self):
        try:
            # Get all matching date elements
            date_elements = self.finder.find_all("xpath", "//small[@class='large-date']", visible=True)
            
            if date_elements:
                # Click the last date element
                date_elements[-1].click()
                logging.info(f"✅ Selected last date: {date_elements[-1].text}")
            else:
                logging.warning("⚠️ No date elements found to select.")
        except Exception as e:
            logging.error(f"❌ Failed to select last date: {e}")


    def click_first_available_slot(self):
        try:
            btn = self.finder.find("xpath", "(//div[@id='slot']//button[contains(text(), 'AM') or contains(text(), 'PM')])[1]", clickable=True)
            if btn:
                btn.click()
                logging.info("✅ Clicked first available time slot.")
            else:
                logging.warning("⚠️ No available slot button found.")
        except Exception as e:
            logging.error(f"❌ Failed to click time slot: {e}")

    def click_request_call_back(self):
        try:
            btn = self.finder.find("id", "request", clickable=True)
            btn.click()
            logging.info("✅ Clicked 'Request Call Back'.")
        except Exception as e:
            logging.warning(f"⚠️ Could not click Request Call Back: {e}")