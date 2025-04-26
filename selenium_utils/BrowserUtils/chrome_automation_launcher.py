# Allow script to run standalone by injecting root to sys.path
import sys
import os

current_file_path = os.path.abspath(__file__)
project_root = os.path.abspath(os.path.join(current_file_path, "../../.."))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

import requests
import zipfile
import time
import subprocess
import json
import tempfile
import shutil
import logging
#import platform
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from dotenv import load_dotenv
import re
import pathlib
from selenium_utils.BrowserUtils.browser_ai_utils import (
    explain_error_with_ai,
    summarize_logs_with_ai,
    analyze_screenshot_with_gpt,
    verify_page_with_ai
)
from dotenv import load_dotenv
# ------------------------- Setup Logging -------------------------
# ✅ Step 1: Define the directory and log file path
BASE_DIR = pathlib.Path(__file__).parent.resolve()
LOG_FILE_PATH = os.path.join(BASE_DIR, "browser_automation.log")

# ✅ Step 2: Set up logging using that path
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# ✅ Step 3 (optional): Log where the logs are going
logging.info(f"[OK]-[LOGGING] Writing logs to: {LOG_FILE_PATH}")

# ------------------------- Environment Setup -------------------------
load_dotenv()
ENABLE_AI = os.getenv("ENABLE_AI", "False").lower() == "true"
DRIVERS_DIR = "./drivers"
HEADLESS = False
target_url = os.getenv("TARGET_URL")
print(f"This is target URL Confirmation from local .Env: {target_url}")


def is_valid_url(url):
    return bool(re.match(r'^https?://', url))


# ------------------------- Utility Functions -------------------------

def get_local_chrome_version():
    try:
        result = subprocess.run(
            ['reg', 'query', r'HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon', '/v', 'version'],
            capture_output=True,
            text=True,
            check=True
        )
        version_line = result.stdout.strip().split('\n')[-1]
        version = version_line.split()[-1]
        logging.info(f"[OK] Detected local Chrome version: {version}")
        return version
    except subprocess.CalledProcessError as e:
        if ENABLE_AI:
            explain_error_with_ai(str(e))
        raise RuntimeError("Unable to detect Chrome version via registry.") from e

def get_existing_chromedriver_version(driver_path):
    if not os.path.exists(driver_path):
        logging.warning(f"[!] ChromeDriver not found at expected path: {driver_path}")
        return None
    try:
        result = subprocess.run([driver_path, "--version"], capture_output=True, text=True)
        output = result.stdout.strip()  # e.g. 'ChromeDriver 135.0.7049.84'
        version = output.split(" ")[1]
        logging.info(f"[OK] Existing ChromeDriver version detected: {version}")
        return version
    except Exception as e:
        logging.warning(f"[!] Could not get existing ChromeDriver version: {e}")
        if ENABLE_AI:
            explain_error_with_ai(str(e))
        return None


def get_matching_chromedriver_version(chrome_version):
    try:
        logging.info("[OK] Checking existing ChromeDriver compatibility...")

        major = chrome_version.split('.')[0]
        chromedriver_path = os.path.join(DRIVERS_DIR, "chromedriver.exe")
        existing_version = get_existing_chromedriver_version(chromedriver_path)

        if existing_version and existing_version.startswith(major + "."):
            logging.info(f"[✓] Reusing existing ChromeDriver {existing_version} compatible with Chrome {chrome_version}")
            return existing_version, None  # No need to download

        logging.info("[→] Existing ChromeDriver not compatible. Fetching latest match...")

        url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
        response = requests.get(url)
        data = response.json()

        for channel_info in data.get("channels", {}).values():
            version = channel_info.get("version", "")
            downloads = channel_info.get("downloads", {}).get("chromedriver", [])
            if version.startswith(major + "."):
                for driver in downloads:
                    if driver["platform"] == "win32":
                        logging.info(f"[OK] Matched ChromeDriver version: {version}")
                        return version, driver["url"]

        raise RuntimeError("No matching ChromeDriver version found.")
    except Exception as e:
        if ENABLE_AI:
            explain_error_with_ai(str(e))
        raise RuntimeError("Error fetching matching ChromeDriver version.") from e

def download_with_progress(url, output_path):
    try:
        logging.info(f"[OK] Starting ChromeDriver download from {url}")
        response = requests.get(url, stream=True)
        total = int(response.headers.get('content-length', 0))

        with open(output_path, 'wb') as file, tqdm(
            desc="⬇ Downloading",
            total=total,
            unit='B',
            unit_scale=True,
            unit_divisor=1024
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                file.write(data)
                bar.update(len(data))
        logging.info(f"[OK] Downloaded ChromeDriver to {output_path}")
    except Exception as e:
        if ENABLE_AI:
            explain_error_with_ai(str(e))
        raise RuntimeError("Failed to download ChromeDriver.") from e

def extract_zip(zip_path, extract_to):
    try:
        logging.info("[OK] Extracting ChromeDriver...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        logging.info(f"[OK] Extracted ChromeDriver to {extract_to}")

        # Automatically move chromedriver.exe to drivers/ if needed
        extracted_driver = os.path.join(extract_to, "chromedriver-win32", "chromedriver.exe")
        if os.path.exists(extracted_driver):
            shutil.move(extracted_driver, os.path.join(extract_to, "chromedriver.exe"))
            shutil.rmtree(os.path.join(extract_to, "chromedriver-win32"))
            logging.info("[OK] Moved ChromeDriver to root drivers directory.")
    except Exception as e:
        if ENABLE_AI:
            explain_error_with_ai(str(e))
        raise RuntimeError("Error extracting ChromeDriver zip.") from e

def kill_existing_chrome_instances():
    try:
        logging.info("[OK] Terminating existing Chrome/Chromedriver processes...")
        subprocess.run("taskkill /f /im chrome.exe", check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run("taskkill /f /im chromedriver.exe", check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logging.info("[OK] Chrome/Chromedriver processes terminated.")
    except Exception as e:
        if ENABLE_AI:
            explain_error_with_ai(str(e))
        logging.warning("Could not terminate Chrome processes.")

def create_temp_profile():
    profile_path = tempfile.mkdtemp()
    default_profile = os.path.join(profile_path, "Default")
    os.makedirs(default_profile, exist_ok=True)
    
    # Write Preferences before Chrome ever launches
    prefs_path = os.path.join(default_profile, "Preferences")
    prefs_content = {
        "profile": {"exit_type": "Normal", # Indicates last session ended properly
                    "exited_cleanly": True}, # Prevents restore popup
        "session": {"restore_on_startup": 0}, # Do not restore tabs
        "browser": {"has_seen_welcome_page": True} # Prevent welcome tab
    }
    with open(prefs_path, "w") as f:
        json.dump(prefs_content, f)
    
    # Remove files that would trigger restore popup
    session_files = [
        "Last Session",
        "Last Tabs",
        "Current Session",
        "Current Tabs",
        "CrashpadMetrics.pma"
    ]
    for file in session_files:
        full_path = os.path.join(default_profile, file)
        if os.path.exists(full_path):
            os.remove(full_path)

    # Prevent Safe Browsing crash behavior
    safe_browsing_dir = os.path.join(default_profile, "Safe Browsing")
    if not os.path.exists(safe_browsing_dir):
        os.makedirs(safe_browsing_dir)
    
    logging.info(f"[OK] Temporary Chrome profile created at {profile_path}")
    return profile_path

def clean_session_files(profile_path):
    session_files = [
        "Last Session",
        "Last Tabs",
        "Current Session",
        "Current Tabs",
        "CrashpadMetrics.pma"
    ]
    for file in session_files:
        path = os.path.join(profile_path, file)
        if os.path.exists(path):
            os.remove(path)

def setup_chrome_options(profile_path, headless=False):
    options = Options()
    #options.add_argument(f"user-data-dir={profile_path}")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")

    # KEY for removing "automation" infobar
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")

    options.add_argument("--lang=en-US")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-background-networking")
    options.add_argument("--mute-audio")
    options.add_argument(f"user-data-dir=c:/Users/{os.getlogin()}/AppData/Local/Google/Chrome/User Data")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.1000.0 Safari/537.36")
    options.add_argument("--lang=en-US")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-logging")
    options.add_argument("--metrics-recording-only")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-default-apps")
    options.add_argument("--no-first-run")
    options.add_argument("--disable-session-crashed-bubble")
    #options.add_argument("--incognito")



    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.geolocation": 1,
         "session.restore_on_startup": 0,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.exit_type": "Normal",
        "profile.exited_cleanly": True,
        "translate.enabled": False
    })

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    
    return options

def dismiss_google_signin_popup(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Stay signed out')]"))
        )
        stay_out_btn = driver.find_element(By.XPATH, "//div[contains(text(), 'Stay signed out')]")
        stay_out_btn.click()
        logging.info("[OK] 'Stay signed out' clicked.")
    except Exception as e:
        if ENABLE_AI:
            explain_error_with_ai(str(e))
        logging.info(f"[INFO] Sign-in prompt not found or already dismissed: {e}")

def did_page_fail_to_load(driver):
    try:
        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        known_errors = [
            "this site can’t be reached",
            "err_name_not_resolved",
            "dns_probe_finished",
            "no internet",
            "server ip address could not be found"
        ]
        return any(err in body_text for err in known_errors)
    except Exception:
        return False

# ------------------------- Reusable Function -------------------------
#def run_chrome_automation(target_url: str = None):
def run_chrome_automation(target_url):

    if not target_url:
        raise ValueError("❌ Target URL must be provided.")

    if not is_valid_url(target_url):
        raise ValueError(
            f"❌ Invalid URL passed to Chrome: '{target_url}' (must start with http:// or https://)"
        )

    temp_profile = None
    driver = None
    try:
        logging.info("[OK] Setting up driver directory...")
        os.makedirs(DRIVERS_DIR, exist_ok=True)
        kill_existing_chrome_instances()

        logging.info("[OK] Detecting local Chrome version...")
        chrome_version = get_local_chrome_version()
        driver_version, download_url = get_matching_chromedriver_version(chrome_version)

        if download_url:
            zip_path = os.path.join(DRIVERS_DIR, 'chromedriver.zip')
            download_with_progress(download_url, zip_path)
            extract_zip(zip_path, DRIVERS_DIR)

        os.environ['PATH'] += os.pathsep + DRIVERS_DIR

        # Create the temp profile first
        temp_profile = create_temp_profile()
        # Then clean up crash-related session files
        clean_session_files(temp_profile) # Create clean profile

        options = setup_chrome_options(temp_profile, HEADLESS) # Configure options with that profile

        logging.info("[OK] Launching Chrome browser with WebDriver...")
        driver = webdriver.Chrome(service=Service(), options=options) # Launch Chrome
        #time.sleep(3)
        driver.maximize_window()
        driver.get(target_url)
        # After page load:
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "form"))
            )
            logging.info("✅ Booking form detected.")
        except TimeoutException:
            logging.error("❌ Booking form not detected even after wait. Page might be broken.")
        #time.sleep(3)  # wait a moment for the page to try loading
        
        if ENABLE_AI:
            verify_page_with_ai(driver, target_url)

        if did_page_fail_to_load(driver):
            logging.error("❌ Chrome could not load the URL. Likely a DNS or network error (e.g., ERR_NAME_NOT_RESOLVED).")
            # Save a screenshot
            #screenshot_path = os.path.join(os.getcwd(), "load_failure.png")
            screenshot_path = os.path.join(BASE_DIR, "load_failure.png")
            if driver.save_screenshot(screenshot_path):
                logging.error(f"[✗] Screenshot saved to: {screenshot_path}")
            else:
                logging.warning("[!] Failed to save screenshot.")
            return None
        
        logging.info("[OK] Browser successfully launched and page loaded.")
        return driver  # ✅ SUCCESS CASE — return live driver

    except Exception as e:
        logging.exception("❌ An unexpected error occurred during browser setup.")
        if ENABLE_AI:
            explain_error_with_ai(str(e))

        # Save screenshot for debugging (if driver still exists)
        try:
            if driver:
                screenshot_path = os.path.join(BASE_DIR, "unhandled_exception.png")
                #screenshot_path = os.path.join(os.getcwd(), "unhandled_exception.png")
                if driver.save_screenshot(screenshot_path):
                    logging.error(f"[✗] Screenshot saved for exception at: {screenshot_path}")
                    analyze_screenshot_with_gpt(screenshot_path)  # OCR + AI
                else:
                    logging.warning("[!] Could not save screenshot for exception.")

            return driver  # Only return if still usable
        
        except Exception as screenshot_err:
            if ENABLE_AI:
                explain_error_with_ai(str(screenshot_err))
            logging.warning(f"[!] Failed while saving exception screenshot: {screenshot_err}")

        dismiss_google_signin_popup(driver)
        
        geolocation_coordinates = {
            "latitude": float(37.7749),
            "longitude": float(-122.4194),
            "accuracy": float(100)
        }
        driver.execute_cdp_cmd("Emulation.setGeolocationOverride", geolocation_coordinates)

        logging.info("[OK] Browser is up and running. Geolocation applied.")

        logging.info("[OK] Browser launched with geolocation spoofed.")
        # ✅ Add this here!
        
        return driver

    except Exception as e:
        if ENABLE_AI:
            explain_error_with_ai(str(e))
        logging.exception("An unexpected error occurred after browser launch.")

#    finally:
#        logging.info("[OK] Cleaning up resources...")
#        if 'driver' in locals():
#            driver.quit()
#        if os.path.exists(temp_profile):
#            shutil.rmtree(temp_profile, ignore_errors=True)
#        logging.info("[OK] Cleanup completed.")
#-------------------------------------------------------------------------
    finally:
        logging.info("[OK] Cleaning up resources...")
        
        # Don't auto-quit here; let the calling script decide
        if os.path.exists(temp_profile):
            shutil.rmtree(temp_profile, ignore_errors=True)

        logging.info("[OK] Cleanup completed.")
        
        if ENABLE_AI:
            summarize_logs_with_ai(LOG_FILE_PATH)
#--------------------------------------------------------------------

# ------------------------- Standalone Execution -------------------------
#if __name__ == "__main__":
#    run_chrome_automation("https://bookslots.centerforvein.com")
