from typing import List, Dict
import os
from dataclasses import dataclass, field
import time
import pytz
chileanTZ = pytz.timezone('America/Santiago')
from rich.markdown import Markdown

# SELENIUM IMPORTS
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import ElementClickInterceptedException

# OWN
from console import console
import properties as p
import webdriver as web
from discord import Discord
from general_utils import Utils
from documents.abstract import Document
from bookings.abstract import Booking
from documents.boleta import BoletaVenta


class SII():
   boletas_url = p.boletasURL

   @classmethod
   def login_to_sii(cls, driver: webdriver, usr: str, psw: str, 
         time_sleep_after:float=0.5):
      """ Login to main SII page"""
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
      console.log("Logging in...")
      time.sleep(time_sleep_after)
      # Confirmation of login needed here

      return
   
   @classmethod
   def login_to_sii_boletas(cls, driver: webdriver):
      """ Login to SII boletas page"""
      console.log(f"Loging to {cls.boletas_url}")
      driver.get(cls.boletas_url)
      web.wait_action_for_element(driver, search_for="input-14", search_by=By.ID)
      usr_input = driver.find_element(By.ID, "input-14")
      usr_input.clear()
      usr_input.send_keys(os.getenv('SII_PANCHO_USR'))
      psw_input = driver.find_element(By.ID, "input-15")
      psw_input.clear()
      psw_input.send_keys(os.getenv('SII_PANCHO_PSW'))
      login_btn = driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div/v-template/div[1]/div[1]/div/div[2]/div/form/div/div[4]/button')
      console.log("Logging in...")
      login_btn.click()
      time.sleep(0.5)
      price_console_screen = '//*[@id="app"]/div[1]/div/main/div/div[2]/div/div/div[1]/div/div/span'
      web.wait_action_for_element(driver, 
                                    search_for=price_console_screen, 
                                    search_by=By.XPATH, 
                                    delay=10, 
                                    action=EC.presence_of_element_located)
      console.log("Logged in successful", style="green")
      time.sleep(0.5)
      return



@dataclass
class BookingSIIManager:
    booking: Booking
    amt_with_taxes: int = field(init=False, repr=True)
    amt_without_taxes: int = field(init=False, repr=True)
    iva_calculated_by_sii: int = field(init=False, repr=False)
    selling_documents: List[Document] = field(init=False, repr=False, 
                                                default_factory=lambda : []) # BOLETAS O FACTURAS
    buying_documents: List[Document] = field(init=False, repr=False, 
                                                default_factory=lambda : []) # FACTURAS POR SERVICIO DE AIRBNB

    def __post_init__(self):
        console.log(Markdown("## Calculating amounts with and without taxes"))
        self.calculate_amounts_with_and_without_taxes()
        self.inform_user_abount_calculations()

    def calculate_amounts_with_and_without_taxes(self):
        def select_month_and_year(driver, month, year):
            console.log(f"Selecting month {month} and year {year}")
            search_box = driver.find_element(By.ID, 'item-form')
            search_items = search_box.find_elements(By.CLASS_NAME, 'gwt-ListBox')
            if len(search_items) != 2:
                raise ValueError("Could not find search items in SII")
            # MONTH SELECT
            month_select = Select(search_items[0])
            month_select.select_by_value(str(month-1))
            # YEAR SELECT
            year_input = Select(search_items[1])
            year_input.select_by_visible_text(str(year))
            # SUBMIT BTN
            btn = search_box.find_element(By.CLASS_NAME, 'gwt-Button')
            btn.send_keys("\n")
            web.wait_action_for_element(driver, search_for='tabla_internet', search_by=By.CLASS_NAME, delay=5, action=EC.visibility_of_element_located)
            console.log("Month and year selection loaded successfully")

        def select_rol(driver, search_rol):
            info_panel = driver.find_element(By.CLASS_NAME, 'panel-derecho')
            info_panel_rows = info_panel.find_elements(By.TAG_NAME, 'tr')
            for row in info_panel_rows:
                td = row.find_elements(By.TAG_NAME, 'td')
                for cell in td:
                    if search_rol in cell.text:
                        console.log(f"Found rol {search_rol}")
                        flag_mark = cell.find_element(By.TAG_NAME, 'input')
                        flag_mark.click()
                        return
            console.log(f"Could not find rol {search_rol}")
            raise ValueError(f"Could not find rol {search_rol}")

        def get_iva_amout_for_booking(driver, booking_amount, nights):
            # FILL WITH BOOKING DATA
            #nights = 3
            #booking_amount = 100000
            console.log(f"Filling IVA form with booking data: {booking_amount} and {nights} nights")
            number_of_nights_input = driver.find_element(By.XPATH, '//*[@id="item-form"]/div[3]/div[1]/input')
            number_of_nights_input.clear()
            number_of_nights_input.send_keys(nights)
            time.sleep(1)
            total_amount_input = driver.find_element(By.XPATH, '//*[@id="item-form"]/div[3]/div[2]/input')
            total_amount_input.clear()
            total_amount_input.send_keys(booking_amount)
            time.sleep(1)
            btn_data_panel = driver.find_element(By.XPATH, '//*[@id="item-form"]/div[9]/button')
            btn_data_panel.send_keys("\n")
            # Wait until loading icon disappears
            loading_widget = {'name':'gwt-PopupPanel processing-widget', 'type':By.CLASS_NAME}
            time.sleep(0.5)
            web.wait_action_for_element(driver, search_for=loading_widget['name'], search_by=loading_widget['type'], delay=10, action=EC.invisibility_of_element_located)
            console.log(f"Data panel loaded. Calculating IVA information by botom '{btn_data_panel.text}'")
            # Get resultado from SII and save it to a variable
            time.sleep(0.5)
            result_input = driver.find_element(By.XPATH, '//*[@id="item-form"]/div[13]/div/input')
            iva = int(result_input.get_attribute('value').replace('.', '').replace('$', ''))
            console.log(f"IVA calculated: {iva} for total: {booking_amount} and nights: {nights}")
            return iva

        def calculate_amounts_with_and_without_taxes(self):
            console.log("Calculating amounts with and without taxes")
            with_taxes = self.iva_calculated_by_sii*(1+self.booking.tax_iva)/p.IVA
            without_taxes = self.booking.total_payment_amount - with_taxes
            return round(with_taxes), round(without_taxes)

        def login_in(driver):
            SII.login_to_sii(driver, usr=os.getenv('SII_CERRO_EL_PLOMO_USR'),  
                        psw=os.getenv('SII_CERRO_EL_PLOMO_PSW'), time_sleep_after=3)
            # COnfirmation of login.
            web.wait_action_for_element(driver, search_for='item-form', 
                                        search_by=By.ID, delay=10, 
                                        action=EC.presence_of_element_located)
            console.log("SII login successful", style='green')


        console.log("Calculating amounts affected by taxes and not affected by it.")
        driver = web.start_webdriver()
        driver.get(p.calculo_iva_arriendo_inmuebles_amobladosURL)
        login_in(driver)
        select_month_and_year(driver, month=self.booking.check_in.month, year=self.booking.check_in.year)
        select_rol(driver, search_rol=os.getenv('SII_CERRO_EL_PLOMO_ROL'))
        self.iva_calculated_by_sii = get_iva_amout_for_booking(
                                                                driver,
                                                                booking_amount=self.booking.total_payment_amount, 
                                                                nights=self.booking.stayed_nights
                                                                )
        driver.quit()
        console.log('Webdriver quited.')
        self.amt_with_taxes, self.amt_without_taxes = calculate_amounts_with_and_without_taxes(self)
        if (self.amt_with_taxes + self.amt_without_taxes) != self.booking.total_payment_amount:
            ValueError(f"Calculated amounts do not match with booking total amount.\n"
                          f"Calculated with taxes: {self.amt_with_taxes}\n"
                          f"Calculated without taxes: {self.amt_without_taxes}\n"
                          f"Booking total amount: {self.booking.total_payment_amount}")
        console.log(f"Calculated amounts successfully", style="green")
        return

    def inform_user_abount_calculations(self):
        console.log("Informing user about calculated amounts")
        Discord.send_message(
            f"Nueva propuesta de Boleta de venta calculada a nombre de {self.booking.name}:\n"
            + f"- IVA calculado por SII: {Utils.format_int_to_clp(self.iva_calculated_by_sii)}\n"
            + f"- Boleta con impuestos (Afecta): {Utils.format_int_to_clp(self.amt_with_taxes)}\n"
            + f"- Boleta sin impuestos (Exenta): {Utils.format_int_to_clp(self.amt_without_taxes)}\n"
            + "-"*25 + "\n"
            + f"**- Total de la reserva: {Utils.format_int_to_clp(self.booking.total_payment_amount)}**"
            )
        return

    def generate_boleta_with_taxes(self, interactive: bool = True):
        console.log(Markdown("## Generating Boletas with taxes"))
        console.log("Generating boleta with taxes for the amount of:", self.amt_with_taxes)
        file_name = f"{self.booking.name.replace(' ', '-')}_{self.booking.check_in=:'%d/%m/%Y'}_AFECTA_IVA"
        
        boleta_w_taxes = BoletaVenta.generate_document(amount=self.amt_with_taxes, 
                                                with_taxes=True, 
                                                stayed_nights=self.booking.stayed_nights, 
                                                total_payment_amount=self.booking.total_payment_amount,
                                                file_name=file_name,
                                                interactive=interactive)
        self.selling_documents.append(boleta_w_taxes)
        console.log(f"Boleta successfully generated", style="bold green")
        return

    def generate_boleta_without_taxes(self, interactive: bool = True):
        console.log(Markdown("## Generating Boletas withoyt taxes"))
        console.log("Generating boleta without taxes for the amount of:", self.amt_without_taxes)
        file_name = f"{self.booking.name.replace(' ', '-')}_{self.booking.check_in=:'%d/%m/%Y'}_EXENTA_IVA"
        
        boleta_wout_taxes = BoletaVenta.generate_document(amount=self.amt_without_taxes, 
                                                with_taxes=False, 
                                                stayed_nights=self.booking.stayed_nights, 
                                                total_payment_amount=self.booking.total_payment_amount,
                                                file_name=file_name,
                                                interactive=interactive)
        self.selling_documents.append(boleta_wout_taxes)
        console.log(f"Boleta successfully generated", style="bold green")
        return
