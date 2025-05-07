"""
imports_manager.py
-------------------
Centralized dynamic import manager with retry logic for robust Selenium-Pytest automation.

- Dynamically imports modules/attributes.
- Provides safe imports with detailed logging.
- Automatically retries failed imports (up to 3 attempts).
- Detects execution mode (manual / ai) and imports accordingly.

Author: Your Name
Date: 2025
"""

# -----------------------------------------------------------------------------
# 🔹 Standard Library Imports
# -----------------------------------------------------------------------------
import importlib
import logging
import time
import os
import sys
from dotenv import load_dotenv
from selenium.webdriver.support import expected_conditions as EC

# -----------------------------------------------------------------------------
# 🔹 Load Environment and Detect Execution Mode
# -----------------------------------------------------------------------------
load_dotenv()
EXECUTION_MODE = os.getenv("EXECUTION_MODE", "manual").lower()

# -----------------------------------------------------------------------------
# 🔹 Configure Logging for the Entire Script
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure site-packages in sys.path
site_packages_path = os.path.join(sys.prefix, 'Lib', 'site-packages')
if site_packages_path not in sys.path:
    sys.path.insert(0, site_packages_path)
    logging.info(f"✅ site-packages added to sys.path: {site_packages_path}")

# -----------------------------------------------------------------------------
# 🚩 STEP 1: Ensure project root is available in sys.path
# -----------------------------------------------------------------------------
def ensure_project_root_in_sys_path(relative_levels_up=4):
    """Ensure the project root directory is included in sys.path."""
    current_file = os.path.abspath(__file__)
    project_root = os.path.abspath(os.path.join(current_file, *[".."] * relative_levels_up))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        logging.info(f"✅ Project root '{project_root}' added to sys.path.")
    else:
        logging.info(f"ℹ️ Project root '{project_root}' already in sys.path.")

# Execute immediately
#sure_project_root_in_sys_path(relative_levels_up=2)
ensure_project_root_in_sys_path(relative_levels_up=2)

# -----------------------------------------------------------------------------
# 🚩 STEP 2: Define Safe Import Function with Retry Logic
# -----------------------------------------------------------------------------
def safe_import(module_path, attribute_name=None, alias=None, retries=3, delay=2):
    """
    Import a module or its attribute safely with retry mechanism.

    Args:
        module_path (str): Dotted path of the module.
        attribute_name (str): Optional attribute (function/class/etc.) to extract.
        alias (str): Friendly name for logging.
        retries (int): Number of retry attempts.
        delay (int): Seconds to wait between retries.

    Returns:
        object or None
    """
    def attempt_import(attempt):
        try:
            module = importlib.import_module(module_path)
            imported_obj = module if attribute_name is None else getattr(module, attribute_name)
            display_name = alias or attribute_name or module_path
            logging.info(f"✅ Successfully imported '{display_name}' from '{module_path}' (Attempt {attempt}).")
            return imported_obj
        except ModuleNotFoundError as e:
            logging.warning(f"⚠️ Attempt {attempt} failed importing '{module_path}.{attribute_name or ''}': {e}")
        except AttributeError as e:
            logging.error(f"❌ AttributeError during import '{module_path}.{attribute_name or ''}': {e}")
            return None
        except Exception as e:
            logging.error(f"❌ Unexpected error during import '{module_path}.{attribute_name or ''}': {e}")
            return None

    for attempt in range(1, retries + 1):
        imported_obj = attempt_import(attempt)
        if imported_obj is not None:
            return imported_obj
        if attempt < retries:
            logging.info(f"⏳ Retrying '{module_path}' in {delay} seconds...")
            time.sleep(delay)
    logging.error(f"❌ All {retries} attempts failed for '{module_path}.{attribute_name or ''}'.")
    return None

# -----------------------------------------------------------------------------
# 🚩 STEP 3: Define Bulk Import Loader
# -----------------------------------------------------------------------------
def bulk_safe_imports(imports_dict, retries=3, delay=2):
    """Import multiple entries from a dictionary of module.attribute paths."""
    imported_objects = {}
    for alias, full_path in imports_dict.items():
        module_path, _, attribute_name = full_path.rpartition('.')
        if not module_path:
            module_path = full_path
            attribute_name = None
        imported_objects[alias] = safe_import(module_path, attribute_name, alias, retries, delay)
    return imported_objects

# -----------------------------------------------------------------------------
# 🚩 STEP 4: Centralized Import Definitions (Standard + Custom)
# -----------------------------------------------------------------------------
imports_needed = {
    # Standard Library
    "time": "time",
    "pathlib": "pathlib",
    "logging": "logging",
    "getenv": "os.getenv",

    # Selenium Core
    "WebDriver": "selenium.webdriver.remote.webdriver.WebDriver",
    "Service": "selenium.webdriver.chrome.service.Service",
    "Options": "selenium.webdriver.chrome.options.Options",
    "By": "selenium.webdriver.common.by.By",
    "Keys": "selenium.webdriver.common.keys.Keys",
    "ActionChains": "selenium.webdriver.common.action_chains.ActionChains",
    "WebDriverWait": "selenium.webdriver.support.ui.WebDriverWait",
    "EC": "selenium.webdriver.support.expected_conditions",

    # Selenium Exceptions
    "TimeoutException": "selenium.common.exceptions.TimeoutException",
    "NoSuchElementException": "selenium.common.exceptions.NoSuchElementException",
    "ElementClickInterceptedException": "selenium.common.exceptions.ElementClickInterceptedException",
    "ElementNotInteractableException": "selenium.common.exceptions.ElementNotInteractableException",

    # WebDriver Classes
    "WebElement": "selenium.webdriver.remote.webelement.WebElement",

    # Custom Utilities
    "simulate_typing": "utils.human_actions.simulate_typing",
    "human_scroll": "utils.human_actions.human_scroll",
    "random_mouse_movement": "utils.human_actions.random_mouse_movement",
    "run_chrome_automation": "selenium_utils.BrowserUtils.chrome_automation_launcher.run_chrome_automation",
    "ElementFinder": "selenium_utils.elementFinderUtils.element_finder.ElementFinder",
    "generate_bookslot_payload": "data.test_inputs.faker_bookslot_data.generate_bookslot_payload",

    # dotenv loader
    "load_dotenv": "dotenv.load_dotenv",
}
# -----------------------------------------------------------------------------
# 🚩 STEP 5: Run the Bulk Import Process
# -----------------------------------------------------------------------------
logging.info("\n🚀 Starting dynamic imports with retry logic...")
imports = bulk_safe_imports(imports_needed, retries=3, delay=2)
logging.info("✅ Dynamic imports with retry completed.\n")

# -----------------------------------------------------------------------------
# 🚩 STEP 6: Load Environment Variables via dotenv if available
# -----------------------------------------------------------------------------
if imports.get("load_dotenv"):
    imports["load_dotenv"]()
    logging.info("✅ .env file loaded successfully.")
else:
    logging.warning("⚠️ load_dotenv not available; .env variables were not loaded.")

# 🚩 STEP 7: Verify and Print Import Status
logging.info("\n🔍 Verifying import status for all modules:")
for alias, imported_obj in imports.items():
    if imported_obj is not None:
        logging.info(f"✅ Import successful: {alias} -> {imported_obj}")
    else:
        logging.error(f"❌ Import failed: {alias}")

EC = imports['EC']
