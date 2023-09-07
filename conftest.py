import os
import pytest
from selene.support.conditions import be
from selene.support.shared import browser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# @pytest.fixture(scope="function", autouse=True)
def setup_browser():
    options = Options()
    options.capabilities.update(
        {
            "browserName": 'chrome',
            "browserVersion": '114.0',
            "selenoid:options": {
                "enableVNC": True,
                "enableVideo": True,
                "screenResolution": "1920x1080x24",
            },
        }
    )

    driver = webdriver.Remote(
        command_executor=f"http://10.210.0.19:4444/wd/hub", options=options
    )

    browser.config.driver = driver
    browser.config.window_width = 1920
    browser.config.window_height = 1080
    browser.config.base_url = os.getenv(
        "selene.base_url",
        "https://app.powerbi.com/view?r=eyJrIjoiYzE1NGI1ZWItN2NhYi00MGJlLTllMGQtZDA0MTRhZTI3N2JjIiwidCI6IjhiYzM0YTk5LTYzMWMtNDhlMi04NjM4LTRiMzg0YmFmOTI3MCIsImMiOjl9"
    )

    browser.open("")
    browser.element('.canvasFlexBox').wait_until(be.visible)
    yield browser

    browser.close()
