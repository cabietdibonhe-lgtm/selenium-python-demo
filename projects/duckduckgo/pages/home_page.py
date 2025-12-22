
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.common.by import By
#from framework.core.base_page import BasePage

#class DuckHomePage(BasePage):
    #SEARCH_INPUT = (By.ID, "searchbox_input")

    #def open_home(self, base_url: str):
        #self.open(base_url)

    #def search(self, text: str):
        #self.type(self.SEARCH_INPUT, text + "\n")




# ví dụ DuckHomePage
#from framework.core.base_page import BasePage
#from selenium.webdriver.common.by import By

#class DuckHomePage(BasePage):
    #SEARCH_INPUT = (By.ID, "searchbox_input")

    #def __init__(self, driver):
        #super().__init__(driver)   # đảm bảo BasePage init logger + wait

    #def open_home(self, base_url: str):
        #self.open(base_url)

    #def search(self, text: str):
        #self.type(self.SEARCH_INPUT, text + "\n")

#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC

#class DuckHomePage:
    #def __init__(self, driver):
        #self.driver = driver
        #self.wait = WebDriverWait(driver, 10)

    #def open_home(self, base_url: str):
        #self.driver.get(base_url)
    #def search(self, text):
        #search_box = self.wait.until(
            #EC.visibility_of_element_located(("id", "searchbox_input"))
        #)
        #search_box.send_keys(text)
        #search_box.submit()


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class DuckHomePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def open_home(self, base_url: str):
        self.driver.get(base_url)
        return self

    def search(self, text: str):
        search_box = self.wait.until(
            EC.visibility_of_element_located((By.ID, "searchbox_input"))
        )
        search_box.clear()
        search_box.send_keys(text)
        search_box.submit()
        return self
