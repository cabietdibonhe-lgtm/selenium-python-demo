import pytest
from projects.hello.pages.hello_page import HelloPage


@pytest.mark.smoke
def test_hello_title_and_text(driver, base_url):
    page = HelloPage(driver).open_home(base_url)

    assert "Hello World" in driver.title
    assert page.get_h1_text() == "Hello World"

