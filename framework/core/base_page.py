from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from framework.utils.logger import get_logger


class BasePage:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
        self.logger = get_logger(self.__class__.__name__)

    def open(self, url: str):
        self.logger.info(f"Open URL: {url}")
        self.driver.get(url)
        return self

    def wait_visible(self, locator):
        self.logger.info(f"Wait visible: {locator}")
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_clickable(self, locator):
        self.logger.info(f"Wait clickable: {locator}")
        return self.wait.until(EC.element_to_be_clickable(locator))

    def click(self, locator):
        self.logger.info(f"Click element: {locator}")
        self.wait_clickable(locator).click()
        return self

    def type(self, locator, text: str, clear=True):
        self.logger.info(f"Type into element: {locator} | text='{text}'")
        element = self.wait_visible(locator)
        if clear:
            element.clear()
        element.send_keys(text)
        return self

    def get_title(self) -> str:
        return self.driver.title


