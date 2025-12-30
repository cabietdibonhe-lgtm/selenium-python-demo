#import pytest
#import allure
#from pathlib import Path

#from framework.utils.config_loader import get_project_base_url
##from framework.core.driver_factory import get_driver
#from framework.utils.screenshot import take_screenshot
#from framework.utils.logger import get_logger

#def pytest_addoption(parser):
    #parser.addoption("--browser", action="store", default="chrome")
    #parser.addoption("--headless", action="store_true", help="Run browser headless")
    #parser.addoption("--env", action="store", default="dev", help="Environment")
    #parser.addoption(
        #"--project",
        #action="store",
        #default="hello",
        #help="Tên project (hello, duckduckgo, google, ...)",
    #)

#from drivers.driver_factory import create_driver


#@pytest.fixture
#def driver():
    #driver = create_driver()
    #yield driver
    #driver.quit()

#@pytest.fixture
#def base_url(request):
    #env = request.config.getoption("--env")
    #project = request.config.getoption("--project")
    #return get_project_base_url(project_name=project, env=env)


#from framework.utils.screenshot import take_screenshot


#@pytest.hookimpl(hookwrapper=True)
#def pytest_runtest_makereport(item, call):
    #outcome = yield
    #rep = outcome.get_result()

    #if rep.when == "call" and rep.failed:
        #driver = item.funcargs.get("driver")
        #if driver:
            #png = driver.get_screenshot_as_png()
            #allure.attach(png, name="screenshot", attachment_type=allure.attachment_type.PNG)






#from framework.utils.logger import get_logger

#@pytest.hookimpl(tryfirst=True)
#def pytest_runtest_setup(item):
    #logger = get_logger("TEST")
    #logger.info(f"===== START TEST: {item.nodeid} =====")

#@pytest.hookimpl(trylast=True)
#def pytest_runtest_teardown(item, nextitem):
    #logger = get_logger("TEST")
    #logger.info(f"===== END TEST: {item.nodeid} =====")




#def pytest_configure(config):
    # chỉ tạo khi bạn chạy có --alluredir
    #alluredir = config.getoption("--alluredir", default=None)
    #if alluredir:
        #env = config.getoption("--env")
        #project = config.getoption("--project")
        #browser = config.getoption("--browser")

        #p = Path(alluredir)
        #p.mkdir(parents=True, exist_ok=True)

        #(p / "environment.properties").write_text(
            #f"env={env}\nproject={project}\nbrowser={browser}\n",
           # encoding="utf-8"
        #)


#@pytest.hookimpl(hookwrapper=True)
#def pytest_runtest_makereport(item, call):
    #outcome = yield
    #rep = outcome.get_result()

    #if rep.when == "call" and rep.failed:
        #driver = item.funcargs.get("driver")
        #if driver:
            # Screenshot
            #png = driver.get_screenshot_as_png()
            #allure.attach(png, name="screenshot", attachment_type=allure.attachment_type.PNG)

            # Current URL
            #try:
                #allure.attach(driver.current_url, name="url", attachment_type=allure.attachment_type.TEXT)
            #except Exception:
               # pass

            # Page source (HTML)
            #try:
                #allure.attach(driver.page_source, name="page_source", attachment_type=allure.attachment_type.HTML)
            #except Exception:
                #pass

import os
import re
import time
from pathlib import Path

import pytest
import allure

from framework.utils.config_loader import get_project_base_url
from framework.utils.logger import get_logger
from drivers.driver_factory import create_driver


# =========================
# CLI options
# =========================
def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome")
    parser.addoption("--headless", action="store_true", help="Run browser headless")
    parser.addoption("--env", action="store", default="dev", help="Environment")
    parser.addoption(
        "--project",
        action="store",
        default="hello",
        help="Tên project (hello, duckduckgo, google, ...)",
    )


# =========================
# Fixtures
# =========================
@pytest.fixture
def driver():
    d = create_driver()
    yield d
    try:
        d.quit()
    except Exception:
        pass


@pytest.fixture
def base_url(request):
    env = request.config.getoption("--env")
    project = request.config.getoption("--project")
    return get_project_base_url(project_name=project, env=env)


# =========================
# Logging start/end test
# =========================
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    logger = get_logger("TEST")
    logger.info(f"===== START TEST: {item.nodeid} =====")


@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item, nextitem):
    logger = get_logger("TEST")
    logger.info(f"===== END TEST: {item.nodeid} =====")


# =========================
# Allure environment.properties
# =========================
def pytest_configure(config):
    # Chỉ tạo khi bạn chạy có --alluredir
    # (pytest option --alluredir được cung cấp bởi plugin allure-pytest)
    alluredir = getattr(config.option, "alluredir", None)

    if alluredir:
        env = config.getoption("--env")
        project = config.getoption("--project")
        browser = config.getoption("--browser")

        p = Path(alluredir)
        p.mkdir(parents=True, exist_ok=True)

        (p / "environment.properties").write_text(
            f"env={env}\nproject={project}\nbrowser={browser}\n",
            encoding="utf-8",
        )


# =========================
# Screenshot + attachments on failure
# =========================
def _safe_filename(s: str) -> str:
    # Biến nodeid thành tên file an toàn để lưu file
    s = re.sub(r"[^a-zA-Z0-9_.-]+", "_", s)
    return s[:180]


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Chỉ chụp khi test FAIL ở phase 'call' (đúng lúc fail).
    - Lưu file png vào ./screenshots (để TeamCity publish artifacts)
    - Attach screenshot + URL + page_source vào Allure
    """
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        d = item.funcargs.get("driver", None)
        if not d:
            return

        # tạo folder artifacts
        Path("screenshots").mkdir(parents=True, exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        test_id = _safe_filename(item.nodeid)
        file_path = Path("screenshots") / f"{test_id}_{timestamp}.png"

        # chờ chút để UI ổn định tránh chụp sớm
        time.sleep(0.5)

        # 1) Save screenshot file (artifacts)
        try:
            d.save_screenshot(str(file_path))
        except Exception:
            pass

        # 2) Attach screenshot to Allure
        try:
            png = d.get_screenshot_as_png()
            allure.attach(
                png,
                name=f"screenshot_{timestamp}",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass

        # 3) Attach current URL
        try:
            allure.attach(d.current_url, name="url", attachment_type=allure.attachment_type.TEXT)
        except Exception:
            pass

        # 4) Attach page source (HTML)
        try:
            allure.attach(d.page_source, name="page_source", attachment_type=allure.attachment_type.HTML)
        except Exception:
            pass
