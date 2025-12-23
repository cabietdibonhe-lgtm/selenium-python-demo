#from projects.duckduckgo.pages.home_page import DuckHomePage
#import time

#def test_duck_search(driver, base_url):
    #page = DuckHomePage(driver)
    #page.open_home(base_url)
    #page.search("selenium python")
    #page.open_home(base_url).search("selenium python")

    #time.sleep(3)  # chỉ để bạn nhìn, sau này bỏ

    #assert "duckduckgo" in driver.title.lower()
    #assert False

#from projects.duckduckgo.pages.home_page import DuckHomePage


#from projects.duckduckgo.pages.home_page import DuckHomePage


#def test_duck_search(driver, base_url):
    #DuckHomePage(driver) \
        #.open_home(base_url) \
        #.search("selenium python")

    #assert "duckduckgo" in driver.title.lower()

#def test_duck_search(driver, base_url):
    #page = DuckHomePage(driver).open_home(base_url).search("selenium python")
    #assert page.has_results()

#from projects.duckduckgo.pages.home_page import DuckHomePage


#def test_duck_search(driver, base_url):
    #page = DuckHomePage(driver).open_home(base_url).search("selenium python")
    #assert page.has_results()


import pytest
from projects.duckduckgo.pages.home_page import DuckHomePage

@pytest.mark.smoke
def test_duck_search(driver, base_url):
    page = DuckHomePage(driver).open_home(base_url).search("selenium python")
    assert page.has_results()






    


