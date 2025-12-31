import pytest
from projects.hello.page.hello_page import HelloPage


@pytest.mark.smoke
def test_hello_title_and_text(driver, base_url):
    page = HelloPage(driver).open_home(base_url)

    assert "Hello World" in driver.title
    assert page.get_h1_text() == "Hello World"


def test_fail_for_screenshot(driver, base_url):
    driver.get(base_url)

    # Cố tình fail để kích hoạt screenshot
    assert "THIS_WILL_FAIL" in driver.title


