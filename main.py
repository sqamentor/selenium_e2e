"""
main.py
--------
Centralized test runner that:
- Loads .env configuration
- Executes either manual or AI-driven page interaction
- Falls back to AI if manual execution fails
"""

import os
import logging
from dotenv import load_dotenv
from imports_manager import imports

# Load environment variables
load_dotenv()
EXECUTION_MODE = os.getenv("EXECUTION_MODE", "manual").lower()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Optional: Driver setup using Chrome
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def create_driver():
    """
    Create and return a Chrome WebDriver instance.
    Customize options as needed for headless, user profiles, etc.
    """
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument("--headless")  # Uncomment for CI
    return webdriver.Chrome(service=Service(), options=chrome_options)

def run_test(driver, mode, imports_dict):
    """
    Attempt to execute the Bookslot test using the given mode (manual or ai).
    Returns True on success, False on failure.
    """
    try:
        logging.info(f"🚀 Running test in {mode.upper()} mode.")
        BookslotPage = imports_dict["BookslotPage"]
        page = BookslotPage(driver)
        page.enter_first_name("Lokendra")
        page.enter_last_name("Singh")
        page.submit_form()
        logging.info(f"✅ {mode.upper()} execution completed.")
        return True
    except Exception as e:
        logging.error(f"❌ {mode.upper()} execution failed: {e}")
        return False

if __name__ == "__main__":
    driver = create_driver()

    if EXECUTION_MODE == "manual":
        success = run_test(driver, "manual", imports)
        if not success:
            # Retry with AI
            logging.info("🔁 Falling back to AI execution...")
            os.environ["EXECUTION_MODE"] = "ai"
            from imports_manager import imports as ai_imports
            run_test(driver, "ai", ai_imports)
    else:
        # Run AI directly
        run_test(driver, "ai", imports)

    driver.quit()
    logging.info("🧹 WebDriver session ended.")
