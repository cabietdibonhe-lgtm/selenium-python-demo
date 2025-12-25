from selenium.webdriver.common.by import By
from framework.core.base_page import BasePage


class HelloPage(BasePage):
    TITLE = (By.ID, "title")  # <h1 id="title">Hello World</h1>

    def open_home(self, base_url: str):
        self.open(base_url)
        return self

    def get_h1_text(self) -> str:
        return self.wait_visible(self.TITLE).text
