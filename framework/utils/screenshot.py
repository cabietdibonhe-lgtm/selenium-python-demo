from pathlib import Path
from datetime import datetime

SCREENSHOT_DIR = Path("screenshots")

def take_screenshot(driver, test_name: str):
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = SCREENSHOT_DIR / f"{test_name}_{timestamp}.png"
    driver.save_screenshot(str(filename))
    return filename
