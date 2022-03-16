from console import console
import properties as p
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import os
import webdriver as web
import time

class SII():
   @classmethod
   def login_to_sii(cls, driver, usr, psw, time_sleep_after=0.2):
      """ Confirmation_statement: """
      web.wait_action_for_element(driver, search_for='rutcntr', 
                                 search_by=By.ID, delay=5, 
                                 action=EC.presence_of_element_located)
      rut_input = driver.find_element(By.ID, 'rutcntr')
      rut_input.clear()
      rut_input.send_keys(usr)
      psw_input = driver.find_element(By.ID, 'clave')
      psw_input.clear()
      psw_input.send_keys(psw)
      login_btn = driver.find_element(By.ID, 'bt_ingresar')
      login_btn.click()
      time.sleep(time_sleep_after)
      console.log("Logging in...")