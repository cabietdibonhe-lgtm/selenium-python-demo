from projects.duckduckgo.pages.home_page import DuckHomePage
import time

def test_duck_search(driver, base_url):
    page = DuckHomePage(driver)
    page.open_home(base_url)
    page.search("selenium python")

    time.sleep(3)  # chỉ để bạn nhìn, sau này bỏ

    #assert "duckduckgo" in driver.title.lower()
    assert False



    


