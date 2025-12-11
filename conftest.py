import pytest
import allure

from framework.utils.config_loader import get_project_base_url
from framework.core.driver_factory import get_driver
from framework.utils.screenshot import take_screenshot
from framework.utils.logger import get_logger

def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome")
    parser.addoption("--headless", action="store_true", help="Run browser headless")
    parser.addoption("--env", action="store", default="dev", help="Environment")
    parser.addoption(
        "--project",
        action="store",
        default="duckduckgo",
        help="Tên project (duckduckgo, google, ...)",
    )

@pytest.fixture
def driver(request):
    browser = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")
    driver = get_driver(browser=browser, headless=headless)
    yield driver
    driver.quit()

@pytest.fixture
def base_url(request):
    env = request.config.getoption("--env")
    project = request.config.getoption("--project")
    return get_project_base_url(project_name=project, env=env)


from framework.utils.screenshot import take_screenshot

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    # Chỉ xử lý phase "call"
    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("driver", None)
        if driver:
            # Chụp screenshot
            file_path = take_screenshot(driver, item.name)
            print(f"\n[SCREENSHOT] Test failed, saved to: {file_path}")

            # Attach screenshot vào Allure
            try:
                allure.attach.file(
                    str(file_path),
                    name=item.name,
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception as e:
                print(f"[ALLURE] Cannot attach screenshot: {e}")




from framework.utils.logger import get_logger

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    logger = get_logger("TEST")
    logger.info(f"===== START TEST: {item.nodeid} =====")

@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item, nextitem):
    logger = get_logger("TEST")
    logger.info(f"===== END TEST: {item.nodeid} =====")
