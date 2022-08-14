from msilib.schema import Condition
import os
import time

# SELENIUM IMPORTS
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# OWN
from config import config
from core.console import console
import core.webdriver as web

SII_NAVIGATOR = {"version": '//*[@id="app"]/div/div/div/v-template/div[2]/div'}


class SII:
    boletas_url = config["sii"]["boleta"]["login_URL"].get()

    @classmethod
    def login_to_sii(
        cls, driver: webdriver, usr: str, psw: str, time_sleep_after: float = 0.5
    ):
        """Login to main SII page"""
        web.wait_action_for_element(
            driver,
            search_for="rutcntr",
            search_by=By.ID,
            delay=5,
            action=EC.presence_of_element_located,
        )
        rut_input = driver.find_element(By.ID, "rutcntr")
        rut_input.clear()
        rut_input.send_keys(usr)
        psw_input = driver.find_element(By.ID, "clave")
        psw_input.clear()
        psw_input.send_keys(psw)
        login_btn = driver.find_element(By.ID, "bt_ingresar")
        login_btn.click()
        console.log("Logging in...")
        time.sleep(time_sleep_after)
        # Confirmation of login needed here

        return

    @classmethod
    def login_to_sii_boletas(cls, driver: webdriver) -> str:
        """Login to SII boletas page"""

        def get_webapp_version(driver):
            return (
                driver.find_element(By.XPATH, SII_NAVIGATOR["version"])
                .text.split("VERSIÓN ")[1]
                .replace(" ", "")
            )

        console.log(f"Loging to {cls.boletas_url}")
        driver.get(cls.boletas_url)

        web.wait_action_for_element(driver, search_for="input-14", search_by=By.ID)

        version = get_webapp_version(driver)

        usr_input = driver.find_element(By.ID, "input-14")
        usr_input.clear()
        usr_input.send_keys(os.getenv("SII_PANCHO_USR"))
        psw_input = driver.find_element(By.ID, "input-15")
        psw_input.clear()
        psw_input.send_keys(os.getenv("SII_PANCHO_PSW"))
        login_btn = driver.find_element(
            By.XPATH,
            '//*[@id="app"]/div/div/div/v-template/div[1]/div[1]/div/div[2]/div/form/div/div[4]/button',
        )
        console.log("Logging in...")
        login_btn.click()
        time.sleep(0.5)
        price_console_screen = (
            '//*[@id="app"]/div[1]/div/main/div/div[2]/div/div/div[1]/div/div/span'
        )
        web.wait_action_for_element(
            driver,
            search_for=price_console_screen,
            search_by=By.XPATH,
            delay=10,
            action=EC.presence_of_element_located,
        )
        console.log("Logged in successful", style="green")
        time.sleep(0.5)
        return version
