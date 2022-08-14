from dotenv import load_dotenv

load_dotenv()

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from config import config


def start_webdriver(headless=False):
    options = Options()
    options.headless = headless
    # options.add_argument('--start-fullscreen')
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("disable-infobars")
    options.add_experimental_option(
        "prefs", {"profile.default_content_setting_values.notifications": 1}
    )
    service = Service(config["scrapper"]["webdriverPath"].get(str))
    driver = webdriver.Chrome(options=options, service=service)
    return driver


def wait_action_for_element(
    driver,
    search_for,
    search_by=By.ID,
    action=EC.presence_of_element_located,
    delay=5,
    **kwargs,
):
    try:
        myElem = WebDriverWait(driver, delay).until(action((search_by, search_for)))
        success_msg = kwargs.pop(
            "success_msg", f"Element with ID {search_for} was loaded successfully"
        )
    except TimeoutException:
        error_msg = kwargs.pop(
            "error_msg", f"Element with ID {search_for} was not found. Asuming error."
        )
        raise ValueError(error_msg)
