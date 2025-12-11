from selenium.webdriver.common.by import By
from framework.core.base_page import BasePage

class DuckHomePage(BasePage):
    SEARCH_INPUT = (By.ID, "searchbox_input")

    def open_home(self, base_url: str):
        self.open(base_url)

    def search(self, text: str):
        self.type(self.SEARCH_INPUT, text + "\n")

