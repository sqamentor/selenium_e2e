import os
import requests
import zipfile
import time
import subprocess
import json
import tempfile
import shutil
import logging
import re
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from dotenv import load_dotenv

# ------------------------- Setup Logging -------------------------
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("automation.log"),
        logging.StreamHandler()
    ]
)

# ------------------------- Environment Setup -------------------------
load_dotenv()
DRIVERS_DIR = "./drivers"
HEADLESS = False


def is_valid_url(url):
    return bool(re.match(r'^https?://', url))


# ------------------------- Utility Functions -------------------------
def remove_old_geckodriver_from_path(geckodriver_dir):
    try:
        current_path = os.environ.get('PATH', '')
        path_dirs = [d for d in current_path.split(os.pathsep) if geckodriver_dir not in d]
        os.environ['PATH'] = os.pathsep.join(path_dirs)
        logging.info("[OK] Old GeckoDriver paths removed from PATH.")
    except Exception as e:
        logging.exception("Failed to remove old GeckoDriver from PATH.")


def download_latest_geckodriver():
    try:
        logging.info("[OK] Fetching latest GeckoDriver release info...")
        response = requests.get("https://api.github.com/repos/mozilla/geckodriver/releases/latest")
        data = response.json()
        version = data['tag_name']
        logging.info(f"[OK] Latest GeckoDriver version: {version}")

        asset = next(
            (a for a in data['assets'] if 'win64.zip' in a['name']),
            None
        )
        if not asset:
            raise RuntimeError("No Windows 64-bit GeckoDriver found.")

        url = asset['browser_download_url']
        return version, url
    except Exception as e:
        raise RuntimeError("Error fetching latest GeckoDriver release.") from e


def download_with_progress(url, output_path):
    try:
        logging.info(f"[OK] Downloading GeckoDriver from {url}")
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
        logging.info(f"[OK] GeckoDriver downloaded to {output_path}")
    except Exception as e:
        raise RuntimeError("Failed to download GeckoDriver.") from e


def extract_zip(zip_path, extract_to):
    try:
        logging.info("[OK] Extracting GeckoDriver...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        logging.info(f"[OK] Extracted GeckoDriver to {extract_to}")
    except Exception as e:
        raise RuntimeError("Error extracting GeckoDriver zip.") from e


def kill_existing_firefox_instances():
    try:
        logging.info("[OK] Terminating existing Firefox/GeckoDriver processes...")
        subprocess.run("taskkill /f /im firefox.exe", check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run("taskkill /f /im geckodriver.exe", check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logging.info("Firefox/GeckoDriver processes terminated.")
    except Exception as e:
        logging.warning("Could not terminate Firefox processes.")


def create_temp_firefox_profile():
    profile_dir = tempfile.mkdtemp()
    profile = FirefoxProfile(profile_dir)

    profile.set_preference("browser.startup.homepage_override.mstone", "ignore")
    profile.set_preference("startup.homepage_welcome_url.additional", "")
    profile.set_preference("browser.startup.page", 0)
    profile.set_preference("browser.usedOnWindows10.introURL", "")
    profile.set_preference("geo.enabled", True)
    profile.set_preference("geo.provider.network.url", "")
    profile.set_preference("geo.prompt.testing", True)
    profile.set_preference("geo.prompt.testing.allow", True)
    profile.set_preference("dom.webnotifications.enabled", False)
    profile.update_preferences()

    logging.info(f"[OK] Temporary Firefox profile created at {profile_dir}")
    return profile

def setup_firefox_options(headless=False):
    options = Options()

    # Set preferences directly
    options.set_preference("dom.webnotifications.enabled", False)
    options.set_preference("browser.startup.page", 0)
    options.set_preference("startup.homepage_welcome_url.additional", "")
    options.set_preference("browser.startup.homepage_override.mstone", "ignore")
    options.set_preference("geo.enabled", True)
    options.set_preference("geo.prompt.testing", True)
    options.set_preference("geo.prompt.testing.allow", True)
    options.set_preference("intl.accept_languages", "en-US")

    if headless:
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")

    return options

# ------------------------- Reusable Function -------------------------
def run_firefox_automation(target_url: str = None):
    """
    Reusable function to run the entire Firefox automation sequence with a single line.
    Requires a valid HTTP/HTTPS target URL.
    """
    if not target_url:
        raise ValueError("❌ Target URL must be provided.")

    if not is_valid_url(target_url):
        raise ValueError(
            f"❌ Invalid URL passed to Firefox: '{target_url}' (must start with http:// or https://)"
        )

    temp_profile = None
    driver = None
    try:
        logging.info("[OK] Setting up driver directory...")
        os.makedirs(DRIVERS_DIR, exist_ok=True)
        remove_old_geckodriver_from_path(DRIVERS_DIR)
        kill_existing_firefox_instances()

        logging.info("[OK] Fetching latest GeckoDriver version info...")
        gecko_version, download_url = download_latest_geckodriver()

        zip_path = os.path.join(DRIVERS_DIR, 'geckodriver.zip')
        download_with_progress(download_url, zip_path)
        extract_zip(zip_path, DRIVERS_DIR)

        os.environ['PATH'] += os.pathsep + DRIVERS_DIR

        temp_profile = create_temp_firefox_profile()
        options = setup_firefox_options(HEADLESS)

        logging.info("[OK] Launching Firefox browser with WebDriver...")
        #driver = webdriver.Firefox(service=Service(), options=options, firefox_profile=temp_profile)
        driver = webdriver.Firefox(service=Service(), options=options)

        driver.get(target_url)

        logging.info("[OK] Browser is up and running.")

        logging.info("[OK] Browser launched and stabilized.")

    except Exception as e:
        logging.exception("An unexpected error occurred during Firefox browser setup.")

    finally:
        logging.info("[OK] Cleaning up resources...")
        if 'driver' in locals():
            driver.quit()
        if temp_profile and os.path.exists(temp_profile.path):
            shutil.rmtree(temp_profile.path, ignore_errors=True)
        logging.info("[OK] Cleanup completed.")


# ------------------------- Standalone Execution -------------------------
if __name__ == "__main__":
    run_firefox_automation("https://google.com")


