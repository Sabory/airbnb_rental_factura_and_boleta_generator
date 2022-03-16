from dotenv import load_dotenv
load_dotenv()
import os
from console import console


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def start_webdriver(headless=False):
   console.log("Starting webdriver...")
   options = Options()
   options.headless = headless
   options.add_argument("window-size=800,600")
   options.add_experimental_option("prefs", {\
        "profile.default_content_setting_values.notifications":1
        })
   service = Service(os.getenv('CHROMEDRIVER_PATH'))
   driver = webdriver.Chrome(options=options, service=service) 
   console.log("Webdriver initialized.", style="green")
   return driver

def wait_action_for_element(driver, search_for, search_by=By.ID, action=EC.presence_of_element_located, delay=5, **kwargs):
   try:
         myElem = WebDriverWait(driver, delay).until(action((search_by, search_for)))
         success_msg = kwargs.pop('success_msg', f"Element with ID {search_for} was loaded successfully")
         console.log(success_msg)
   except TimeoutException:
         error_msg = kwargs.pop('error_msg', f"Element with ID {search_for} was not found. Asuming error.")
         raise ValueError(error_msg)
