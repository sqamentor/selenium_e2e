import os
import time
import allure

def capture_screenshot(driver, name="step"):
    os.makedirs("screenshots", exist_ok=True)
    timestamp = int(time.time())
    filename = f"screenshots/{name}_{timestamp}.png"
    driver.save_screenshot(filename)
    
    # Attach to Allure
    allure.attach.file(
        filename,
        name=f"Screenshot - {name}",
        attachment_type=allure.attachment_type.PNG
    )
    return filename