import os

folders = [
    "tests/ui", "tests/api", "tests/regression", "tests/bdd",
    "pages", "utils", "config", "resources", "drivers",
    "reports/allure-results", "fixtures", "features/steps"
]

files = [
    "tests/test_smoke_ui.py",
    "pages/login_page.py",
    "pages/dashboard_page.py",
    "utils/browser_launcher.py",
    "utils/element_finder.py",
    "utils/logger.py",
    "utils/data_loader.py",
    "utils/screenshot.py",
    "utils/retry_handler.py",
    "config/env_config.py",
    "config/credentials.yaml",
    "resources/testdata.json",
    "drivers/chromedriver.exe",  # placeholder file
    "fixtures/conftest.py",
    "features/login.feature",
    "features/steps/login_steps.py",
    ".env", "pytest.ini", "requirements.txt",
    "run_tests.bat", "run_tests.sh", "README.md"
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

for file in files:
    folder = os.path.dirname(file)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    with open(file, "w", encoding="utf-8") as f:
        f.write(f"# {os.path.basename(file)}\n")

print("✅ Framework structure created successfully.")