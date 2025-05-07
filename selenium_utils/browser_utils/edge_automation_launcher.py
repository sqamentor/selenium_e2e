import os
import requests
import zipfile
import time
import subprocess
import json
import tempfile
import shutil
import logging
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from dotenv import load_dotenv
import re

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

# ------------------------- URL Validation -------------------------
def is_valid_url(url):
    return bool(re.match(r'^https?://', url))

# ------------------------- Utility Functions -------------------------

# Removes old EdgeDriver paths from PATH
def remove_old_edgedriver_from_path(edgedriver_dir):
    try:
        current_path = os.environ.get('PATH', '')
        path_dirs = [d for d in current_path.split(os.pathsep) if edgedriver_dir not in d]
        os.environ['PATH'] = os.pathsep.join(path_dirs)
        logging.info("[OK] Old EdgeDriver paths removed from PATH.")
    except Exception as e:
        logging.exception("Failed to remove old EdgeDriver from PATH.")

# Detects the locally installed Edge version from Windows registry
def get_local_edge_version():
    try:
        result = subprocess.run(
            ['reg', 'query', r'HKEY_CURRENT_USER\Software\Microsoft\Edge\BLBeacon', '/v', 'version'],
            capture_output=True,
            text=True,
            check=True
        )
        version_line = result.stdout.strip().split('\n')[-1]
        version = version_line.split()[-1]
        logging.info(f"[OK] Detected local Edge version: {version}")
        return version
    except subprocess.CalledProcessError as e:
        raise RuntimeError("Unable to detect Edge version via registry.") from e

# Fetches the latest compatible EdgeDriver version
def get_matching_edgedriver_version(edge_version):
    try:
        logging.info("[OK] Fetching compatible EdgeDriver version...")
        major = edge_version.split('.')[0]
        url = f"https://msedgedriver.azureedge.net/LATEST_RELEASE_{major}"
        response = requests.get(url)
        matched_version = response.text.strip()
        if not matched_version:
            raise RuntimeError("Failed to fetch matching EdgeDriver version.")
        download_url = f"https://msedgedriver.azureedge.net/{matched_version}/edgedriver_win64.zip"
        logging.info(f"[OK] Matched EdgeDriver version: {matched_version}")
        return matched_version, download_url
    except Exception as e:
        raise RuntimeError("Error fetching matching EdgeDriver version.") from e

# Downloads files with progress bar
def download_with_progress(url, output_path):
    try:
        logging.info(f"[OK] Starting EdgeDriver download from {url}")
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
        logging.info(f"[OK] Downloaded EdgeDriver to {output_path}")
    except Exception as e:
        raise RuntimeError("Failed to download EdgeDriver.") from e

# Extracts the zipped driver
def extract_zip(zip_path, extract_to):
    try:
        logging.info("[OK] Extracting EdgeDriver...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        logging.info(f"[OK] Extracted EdgeDriver to {extract_to}")
    except Exception as e:
        raise RuntimeError("Error extracting EdgeDriver zip.") from e

# Kills existing Edge/EdgeDriver processes
def kill_existing_edge_instances():
    try:
        logging.info("[OK] Terminating existing Edge/EdgeDriver processes...")
        subprocess.run("taskkill /f /im msedge.exe", check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run("taskkill /f /im msedgedriver.exe", check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logging.info("[OK] Edge/EdgeDriver processes terminated.")
    except Exception as e:
        logging.warning("Could not terminate Edge processes.")

# Creates a temporary Edge profile
def create_temp_profile():
    profile_path = tempfile.mkdtemp()
    default_profile = os.path.join(profile_path, "Default")
    os.makedirs(default_profile, exist_ok=True)
    prefs_path = os.path.join(default_profile, "Preferences")
    prefs_content = {
        "profile": {"exit_type": "Normal", "exited_cleanly": True},
        "session": {"restore_on_startup": 0},
        "browser": {"has_seen_welcome_page": True}
    }
    with open(prefs_path, "w") as f:
        json.dump(prefs_content, f)
    logging.info(f"[OK] Temporary Edge profile created at {profile_path}")
    return profile_path

# Configures Edge browser options
def setup_edge_options(profile_path, headless=False):
    options = Options()
    options.use_chromium = True  # Required for Edge
    options.add_argument(f"user-data-dir={profile_path}")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--lang=en-US")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-background-networking")
    options.add_argument("--mute-audio")
    options.add_argument("--disable-logging")
    options.add_argument("--metrics-recording-only")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-default-apps")
    options.add_argument("--no-first-run")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.1000.0 Safari/537.36")

    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.geolocation": 1,
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

# ------------------------- Reusable Function -------------------------
def run_edge_automation(target_url: str = None):
    """
    Reusable function to run the entire Edge automation sequence with a single line.
    Requires a valid HTTP/HTTPS target URL.
    """
    if not target_url:
        raise ValueError("❌ Target URL must be provided.")

    if not is_valid_url(target_url):
        raise ValueError(f"❌ Invalid URL passed to Edge: '{target_url}' (must start with http:// or https://)")

    temp_profile = None
    driver = None
    try:
        logging.info("[OK] Setting up driver directory...")
        os.makedirs(DRIVERS_DIR, exist_ok=True)
        remove_old_edgedriver_from_path(DRIVERS_DIR)
        kill_existing_edge_instances()

        logging.info("[OK] Detecting local Edge version...")
        edge_version = get_local_edge_version()
        driver_version, download_url = get_matching_edgedriver_version(edge_version)

        zip_path = os.path.join(DRIVERS_DIR, 'edgedriver.zip')
        download_with_progress(download_url, zip_path)
        extract_zip(zip_path, DRIVERS_DIR)

        os.environ['PATH'] += os.pathsep + DRIVERS_DIR

        temp_profile = create_temp_profile()
        options = setup_edge_options(temp_profile, HEADLESS)

        logging.info("[OK] Launching Edge browser with WebDriver...")
        driver = webdriver.Edge(service=Service(), options=options)
        driver.get(target_url)

        geolocation_coordinates = {
            "latitude": float(37.7749),
            "longitude": float(-122.4194),
            "accuracy": float(100)
        }
        driver.execute_cdp_cmd("Emulation.setGeolocationOverride", geolocation_coordinates)

        logging.info("[OK] Browser is up and running. Geolocation applied.")

        logging.info("[OK] Browser launched with geolocation spoofed.")

    except Exception as e:
        logging.exception("An unexpected error occurred during browser setup.")

    finally:
        logging.info("[OK] Cleaning up resources...")
        if driver:
            driver.quit()
        if temp_profile and os.path.exists(temp_profile):
            shutil.rmtree(temp_profile, ignore_errors=True)
        logging.info("[OK] Cleanup completed.")

# ------------------------- Standalone Execution -------------------------
if __name__ == "__main__":
    run_edge_automation("https://google.com")
