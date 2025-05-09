from utils.screenshot_utils import capture_screenshot

def get_with_screenshot(driver, url: str, label="page_load"):
    driver.get(url)
    capture_screenshot(driver, name=label)
