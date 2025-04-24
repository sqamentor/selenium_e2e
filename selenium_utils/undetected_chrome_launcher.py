import undetected_chromedriver as uc
import os
import subprocess
import re

def launch_undetected_chrome(headless=False, use_profile=True, profile_dir="Default",enable_incognito=False):
    """
    Launch undetected Chrome with optional headless mode and real profile support.
    """

    options = uc.ChromeOptions()

    # ✅ Load real Chrome user profile if requested
    if use_profile:
        user_data_dir = os.path.expandvars(r"C:\Users\%USERNAME%\AppData\Local\Google\Chrome\User Data")
        options.user_data_dir = user_data_dir
        options.add_argument(f"profile-directory={profile_dir}")
    elif enable_incognito:
        options.add_argument("--incognito")

    # ✅ Headless mode support
    if headless:
        options.add_argument("--headless=new")

    # ✅ Basic performance & compatibility options
    options.add_argument("--no-first-run")
    options.add_argument("--no-service-autorun")
    options.add_argument("--password-store=basic")
    options.add_argument("--start-maximized")

    # ✅ Launch Chrome with detected or overridden version
    return uc.Chrome(options=options, version_main=undetected_version_finder())

def undetected_version_finder():
    """
    Tries to find installed Chrome version for correct uc.Chrome driver.
    """
    try:
        result = subprocess.run(["chrome", "--version"], capture_output=True, text=True, shell=True)
        match = re.search(r'(\d+)\.', result.stdout)
        return int(match.group(1)) if match else 120
    except Exception:
        return 120  # fallback
