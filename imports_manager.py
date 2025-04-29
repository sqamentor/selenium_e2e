"""
imports_manager.py
-------------------

Centralized dynamic import manager with retry logic for robust Selenium-Pytest automation.

- Dynamically imports modules/attributes.
- Provides safe imports with detailed logging.
- Automatically retries failed imports (up to 3 attempts).

Author: Your Name
Date: 2025
"""

# 🔹 Standard Library
import importlib
import logging
import time
import os
import sys

# 🔹 Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ----------------------------------------------------------------
# 🚩 STEP 1: INITIALIZE PROJECT ROOT PATH (Best placed at the top)
# ----------------------------------------------------------------

def ensure_project_root_in_sys_path(relative_levels_up=2):
    """
    Ensures the project root is in sys.path for robust imports.

    Args:
        relative_levels_up (int): Levels to navigate up to reach the project root.
    """
    current_file = os.path.abspath(__file__)
    project_root = os.path.abspath(os.path.join(current_file, *[".."] * relative_levels_up))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        logging.info(f"✅ Project root '{project_root}' added to sys.path.")
    else:
        logging.info(f"ℹ️ Project root '{project_root}' already in sys.path.")

# Initialize immediately
ensure_project_root_in_sys_path(relative_levels_up=2)

def safe_import(module_path, attribute_name=None, alias=None, retries=3, delay=2):
    """
    Safely imports a module or attribute, retrying upon failure.

    Args:
        module_path (str): Module path to import.
        attribute_name (str, optional): Specific attribute or class to import.
        alias (str, optional): Friendly name for logging.
        retries (int): Number of retry attempts upon failure.
        delay (int): Delay in seconds between retries.

    Returns:
        Imported object or None if all retries fail.
    """
    attempt = 1
    while attempt <= retries:
        try:
            module = importlib.import_module(module_path)
            imported_obj = getattr(module, attribute_name) if attribute_name else module
            display_name = alias or attribute_name or module_path
            logging.info(f"✅ Successfully imported '{display_name}' from '{module_path}' (Attempt {attempt}).")
            return imported_obj
        except ModuleNotFoundError as e:
            logging.warning(f"⚠️ Attempt {attempt} failed importing '{module_path}.{attribute_name or ''}': {e}")
            if attempt < retries:
                logging.info(f"⏳ Retrying '{module_path}' in {delay} seconds...")
                time.sleep(delay)
                attempt += 1
            else:
                logging.error(f"❌ All {retries} attempts failed for '{module_path}'.")
                return None
        except Exception as e:
            logging.error(f"❌ Unexpected error during import '{module_path}.{attribute_name or ''}': {e}")
            return None


def bulk_safe_imports(imports_dict, retries=3, delay=2):
    """
    Bulk imports multiple modules/attributes with retry logic.

    Args:
        imports_dict (dict): Dictionary with alias as key, full module paths as value.
        retries (int): Number of retry attempts for each import.
        delay (int): Delay in seconds between retries.

    Returns:
        dict: Dictionary of imported objects.
    """
    imported_objects = {}
    for alias, full_path in imports_dict.items():
        module_path, _, attribute_name = full_path.rpartition('.')
        if not module_path:
            module_path = full_path
            attribute_name = None
        imported_obj = safe_import(module_path, attribute_name, alias, retries, delay)
        imported_objects[alias] = imported_obj
    return imported_objects


# 🔹 Centralized import definitions
imports_needed = {
    # Standard Library
    "time": "time",
    "pathlib": "pathlib",
    "logging": "logging",

    # Selenium Imports
    "webdriver": "selenium.webdriver",
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

    # Selenium WebDriver & WebElement Classes
    "WebDriver": "selenium.webdriver.remote.webdriver.WebDriver",
    "WebElement": "selenium.webdriver.remote.webelement.WebElement",

    # Custom Utility Functions
    "simulate_typing": "utils.human_actions.simulate_typing",
    "human_scroll": "utils.human_actions.human_scroll",
    "random_mouse_movement": "utils.human_actions.random_mouse_movement",
    "run_chrome_automation": "selenium_utils.BrowserUtils.chrome_automation_launcher.run_chrome_automation",
    "ElementFinder": "selenium_utils.elementFinderUtils.element_finder.ElementFinder",
}


# 🚀 Execute bulk imports with retry logic
logging.info("\n🚀 Starting dynamic imports with retry logic...")
imports = bulk_safe_imports(imports_needed, retries=3, delay=2)
logging.info("✅ Dynamic imports with retry completed.\n")

