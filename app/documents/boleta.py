import os
from dataclasses import dataclass, field
from datetime import datetime
import time
import pytz
chileanTZ = pytz.timezone('America/Santiago')
from rich.markdown import Markdown

# SELENIUM 
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
import sii as s
from discord import Discord
from general_utils import Utils
from documents.abstract import Document




@dataclass
class BoletaVenta(Document):
    @classmethod
    def generate_document(cls, amount: int, with_taxes: bool, 
                        stayed_nights: int, total_payment_amount: int, 
                        file_name: str, interactive: bool):

        def select_elegible_society(driver, society_rut):
            console.log("Selecting elegible society...")
            p = '//*[@id="app"]/div[1]/div/header/div[2]/div/div/div/div/div[2]/div[1]'
            web.wait_action_for_element(driver, search_for=p, search_by=By.XPATH, delay=10, action=EC.presence_of_element_located)
            societies_select = driver.find_element(By.XPATH, p)
            societies_select.click()
            time.sleep(0.5)
            societies_options = driver.find_elements(By.XPATH, '//*[@role="listbox"]/*[@role="option"]')
            society_rut = society_rut.split('-')[0].replace('.', '')
            for s in societies_options:
                rut = s.text.split('-')[0].replace('.', '')
                if rut == society_rut:
                    console.log('Rut of Cerro El Plomo found:', s.text)
                    actions = ActionChains(driver)
                    actions.move_to_element(s).click().perform()
            # ENSURING THAT THE SOCIETY IS SELECTED
            society_input = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div/header/div[2]/div/div/div/div/div[2]/div[1]')
            if society_input.text.split('-')[0].replace('.', '') != society_rut:
                raise ValueError(f"Society 'Cerro El Plomo' was wrongly selected. Current selected society: {society_input.text}")
            console.log("Society was selected.")

        def input_amount(driver, amount:int):
            num_grid = driver.find_elements(By.XPATH, '//*[@id="app"]/div[1]/div/main/div/div[2]/div/div/div[2]/*[@class="col col-4"]')
            num_grid_elements = {}
            for num_element in num_grid:
                num_grid_elements[num_element.text] = num_element
            amount_str = str(amount)
            for _, digit in enumerate(amount_str):
                num_grid_elements[digit].click()
            inputed_amount = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div/main/div/div[2]/div/div/div[1]/div/div/span')
            inputed_amount = inputed_amount.text.replace('$', '').replace('.', '').replace(' ', '')
            if amount_str != inputed_amount:
                raise ValueError(f"Amount that should have been inputed ({amount_str}) is not the same as the registered one ({inputed_amount})")

        def submit_amount(driver, interactive):
            Utils.ask_confirmation(confirmation="Esta todo OK?", interactive=interactive, dont_exit=False)
            p = '//*[@id="app"]/div[1]/div/main/div/div[2]/div/div/div[2]/div[13]/button'
            web.wait_action_for_element(driver, search_for=p, search_by=By.XPATH, delay=5, action=EC.element_to_be_clickable)
            send_btn = driver.find_element(By.XPATH, p)
            send_btn.click()
            time.sleep(0.5)
            web.wait_action_for_element(driver, 
                                        search_for='//*[@id="app"]/div[3]/div/div[1]/div[1]/div/v-template[1]/form/div/div[2]/div/div/div',
                                        search_by=By.XPATH,
                                        action=EC.element_to_be_clickable)
        
        def submit_amount_wrapper(driver, interactive, n=1):
            if n == 3:
                raise ValueError("Couldn't submit amount")
            try:
                submit_amount(driver, interactive)
            except ElementClickInterceptedException:
                console.log("ElementClickInterceptedException. Trying again after 2 seconds.")
                time.sleep(2)
                submit_amount_wrapper(driver, interactive, n+1)

        def fill_boleta_information(driver, with_taxes:bool, stayed_nights:int, total_payment_amount:int):
            # TODO: FILL INFO
            boleta_type_input = driver.find_element(By.XPATH, '//*[@id="app"]/div[3]/div/div[1]/div[1]/div/v-template[1]/form/div/div[2]/div/div/div')
            boleta_type_input.click()
            time.sleep(0.5)
            options = driver.find_elements(By.XPATH, '//div[contains(@id, "list-item") and @role="option" and @tabindex="0"]')
            selected_option = None
            for option in options:
                if option.text == 'Boleta afecta':
                    option_type = True
                elif option.text == 'Boleta exenta':
                    option_type = False
                else:
                    option_type = None

                if with_taxes == option_type:
                    console.log('Found type of boleta:', option.text)
                    selected_option = option
            selected_option.click()
            # Ensuring that the type of boleta was correctly selected
            selected = driver.find_element(By.XPATH, '//*[@id="app"]/div[3]/div/div[1]/div[1]/div/v-template[1]/form/div/div[2]/div/div/div/div[1]/div[1]')
            if not(((selected.text == 'Boleta exenta') and (with_taxes == False)) or ((selected.text == 'Boleta afecta') and (with_taxes == True))):
                raise ValueError(f"Selected type for boleta is not what it shoud. Selected: {selected.text}. Should been: {with_taxes}")
            
            # DETALLE INFORMATIOn
            detail_info = driver.find_element(By.XPATH, "//label[contains(text(), 'Detalle')]")
            detail_info.click()
            time.sleep(0.5)
            inputs = driver.find_elements(By.XPATH, "//*[@class='v-text-field__slot']")
            detalle_input = None
            for input in inputs:
                if input.text == 'Detalle':
                    if detalle_input is not None:
                        raise ValueError("Two detalles input found. Please check.")
                    detalle_input = input
            if detalle_input is None:
                raise ValueError("Detalle input was not found.")
            detalle_input = detalle_input.find_element(By.TAG_NAME, 'input')
            type = "afecta" if with_taxes else "exenta"
            detalle_input.send_keys(f"Arriendo bien inmueble amoblado {stayed_nights} noches (Total: {'${:,.0f}'.format(total_payment_amount).replace(',','.')}) parte {type}")
            return
        
        def submit_boleta(cls, driver, interactive):
            Utils.ask_confirmation(confirmation="Esta todo OK?", interactive=interactive, dont_exit=False)
            p='//*[@id="app"]/div[3]/div/div[1]/div[1]/div/v-template[1]/div[7]/div/button'
            web.wait_action_for_element(driver, search_for=p, search_by=By.XPATH, delay=5, action=EC.element_to_be_clickable)
            submit_btn = driver.find_element(By.XPATH, p)
            submit_btn.click()
            time.sleep(0.5)
        
        def get_boleta_url(driver):
            btn = '//*[@id="app"]/div[3]/div/div[1]/div[1]/div/v-template[3]/div[2]/div[2]/a'
            web.wait_action_for_element(driver, search_for=btn, search_by=By.XPATH, delay=10, action=EC.element_to_be_clickable)
            download_btn = driver.find_element(By.XPATH, btn)
            if not 'descargar' in download_btn.text.lower():
                raise ValueError("Download button text is not 'Descargar'")
            #TODO: DEFINE NAME FOR FILE
            dwn_ulr = download_btn.get_attribute('href')
            boleta_number = get_boleta_ID(dwn_ulr)
            Discord.send_message(f"Boleta {boleta_number} generada: {dwn_ulr}")
            return dwn_ulr

        def get_boleta_ID(url):
            try:
                return int(url.split('folio')[1].split('_')[0])
            except IndexError or ValueError as e:
                raise ValueError(f"Couldn't get boleta ID number from url.\n - Error: {e}")

        def download_from_url(url, file_name, with_taxes):
            boletaID = get_boleta_ID(url)
            file_name = f"{file_name}_{boletaID}"
            full_path = f"{p.BOLETA_DWN_PATH}/{file_name}.pdf"
            if Utils.download_file_from_URL(url, full_path):
                if with_taxes:
                    msg= f"Boleta Afecta No:{boletaID} descargada: `{full_path}`"
                else:
                    msg= f"Boleta Exenta No:{boletaID} descargada: `{full_path}`"
                console.log(msg, style="bold green")
                Discord.send_message(msg)
                return full_path
            else:
                console.log(":warning: An error ocurred while downloading boleta.", style="red")
                return None 

        console.log(f"Generating Boleta for amount {amount}. Affected by taxes: {with_taxes}")
        driver = web.start_webdriver()
        s.SII.login_to_s.SII_boletas(driver)
        select_elegible_society(driver, society_rut=os.getenv('CERRO_EL_PLOMO_RUT'))
        input_amount(driver, amount=amount)
        # Send input amount
        submit_amount_wrapper(driver, interactive)
        fill_boleta_information(driver, with_taxes, stayed_nights, total_payment_amount)
        #* CREATE BOLETA FINAL BUTTON
        console.log(Markdown("## Submitting boleta with taxes: `{}`".format(with_taxes)))
        submit_boleta(cls, driver, interactive)
        boleta_url = get_boleta_url(driver)
        console.log("Boleta generated!", style='bold green')
        boleta_num = get_boleta_ID(boleta_url)
        console.log("Creating boleta instance...")
        boleta = cls(id=boleta_num, file_name=file_name, with_taxes=with_taxes, url=boleta_url)
        console.log("Downloading boleta...")
        file_path = download_from_url(boleta_url, file_name, with_taxes)
        if file_path is not None:
            console.log("Boleta downloaded!", style='bold green')
            boleta.path = file_path
            return boleta
        else: 
            console.log(":warning: An error ocurred while downloading boelta.", style='bold yellow')
            return boleta
