import os
from dataclasses import dataclass
import time
import random

# SELENIUM IMPORTS
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert

# OWN
from config import config
from core.console import console
import core.webdriver as web
from core.general_utils import Utils
from core.messenger.slack import Slack

from models.servicio_impuesto_interno.sii import SII

from .abstract import Document


@dataclass
class FacturaCompra(Document):
    headless: bool = False

    @classmethod
    def generate_document(
        cls,
        amount: int,
        book_to_name: str,
        rut: str = config["airbnb"]["factura"]["RUT"].get(),
        street: str = config["airbnb"]["factura"]["street"].get(),
        comuna: str = config["airbnb"]["factura"]["comuna"].get(),
        city: str = config["airbnb"]["factura"]["city"].get(),
        giro: str = config["airbnb"]["factura"]["giro"].get(),
        detalle: str = config["airbnb"]["factura"]["details"].get(),
        interactive: bool = True,
    ):
        assert amount > 0 and isinstance(
            amount, int
        ), "Amount must be a integer and greater than 0"

        def login_in(driver):
            SII.login_to_sii(
                driver, usr=os.getenv("SII_PANCHO_USR"), psw=os.getenv("SII_PANCHO_PSW")
            )
            # COnfirmation of login.
            web.wait_action_for_element(
                driver,
                search_for='//select[@class="form-control" and @name="RUT_EMP"]',
                search_by=By.XPATH,
                delay=10,
                action=EC.element_to_be_clickable,
            )
            console.log("SII login successful", style="green")

        def choose_society(driver):
            emp_ruts = driver.find_element(
                By.XPATH, '//*[@class="form-control" and @name="RUT_EMP"]'
            )
            emp_select = Select(emp_ruts)
            rut = os.getenv("CERRO_EL_PLOMO_RUT").replace(".", "")
            emp_select.select_by_value(rut)

        def fill_factura_details(driver):
            def recheck_everything_is_ok(driver):
                # RUT
                x = driver.find_element(By.XPATH, '//input[@name="EFXP_RUT_RECEP"]')
                assert str(x.get_attribute("value")) == str(
                    rut.replace(".", "").split("-")[0]
                ), "RUT loaded is not the same as the one used to login"
                x = driver.find_element(By.XPATH, '//input[@name="EFXP_DV_RECEP"]')
                assert str(x.get_attribute("value")) == str(
                    rut.split("-")[1]
                ), "RUT Verificator Digit loaded is not the same as the one used to login"
                # Final Price
                x = driver.find_element(By.XPATH, '//input[@name="EFXP_MNT_TOTAL"]')
                assert str(x.get_attribute("value")) == str(
                    amount
                ), "Final Price loaded is not the same as the one used to login"

            def input_keys(driver, element, keys):
                element.clear()
                element.send_keys(keys)
                time.sleep(round(random.random(), 2) * 3)

            # RUT WITHOUT VERIFICATION CODE
            console.log("Filling RUT...")
            rut_input_no_ver = driver.find_element(
                By.XPATH, '//input[@name="EFXP_RUT_RECEP"]'
            )
            rut_no_ver = rut.split("-")[0].replace(".", "")
            input_keys(driver, rut_input_no_ver, rut_no_ver)
            # VERIFICATION DIGIT FROM RUT
            rut_input_ver = driver.find_element(
                By.XPATH, '//input[@name="EFXP_DV_RECEP"]'
            )
            rut_ver = rut.split("-")[1]
            input_keys(driver, rut_input_ver, rut_ver)
            # need to loose focus from element after send_keys
            rut_input_no_ver.click()

            # POP UP HANDLER
            alert = Alert(driver)
            console.log("Alert poped up with message:", alert.text)
            alert.accept()
            console.log("Alert accepted", style="green")

            # ADDRESS
            console.log("filling Adress...")
            ## STREET
            address_input = driver.find_element(
                By.XPATH, '//input[@name="EFXP_DIR_RECEP"]'
            )
            input_keys(driver, address_input, street)
            ## COMUNA
            address_input = driver.find_element(
                By.XPATH, '//input[@name="EFXP_CMNA_RECEP"]'
            )
            input_keys(driver, address_input, comuna)
            ## CITY
            address_input = driver.find_element(
                By.XPATH, '//input[@name="EFXP_CIUDAD_RECEP"]'
            )
            input_keys(driver, address_input, city)
            ## GIRO
            address_input = driver.find_element(
                By.XPATH, '//input[@name="EFXP_GIRO_RECEP"]'
            )
            input_keys(driver, address_input, giro)

            # COD Prod
            console.log("filling COD PROD...")
            cod_prod_input = Select(
                driver.find_element(By.XPATH, '//select[@name="EFXP_COD_01"]')
            )
            cod_prod_input.select_by_value("1500")
            time.sleep(round(random.random(), 2) * 3)

            # Descrip flag
            console.log("filling description flag...")
            descrip_flag_input = driver.find_element(
                By.XPATH, '//input[@name="DESCRIP_01"]'
            )
            descrip_flag_input.click()
            time.sleep(round(random.random(), 2) * 3)
            console.log("filling Description text area...")
            text_area = '//textarea[@name="EFXP_DSC_ITEM_01"]'
            web.wait_action_for_element(
                driver,
                search_for=text_area,
                search_by=By.XPATH,
                delay=10,
                action=EC.element_to_be_clickable,
            )
            descrip_textarea = driver.find_element(By.XPATH, text_area)
            input_keys(driver, descrip_textarea, detalle)

            # Cantidad
            console.log("filling QTY...")
            cantidad_input = driver.find_element(
                By.XPATH, '//input[@name="EFXP_QTY_01"]'
            )
            input_keys(driver, cantidad_input, "1")

            # Precio
            console.log("filling Price...")
            precio_input = driver.find_element(By.XPATH, '//input[@name="EFXP_PRC_01"]')
            input_keys(driver, precio_input, amount)
            # UN FOCUS precio
            cantidad_input.click()

            console.log("Rechecking everything is ok...")
            recheck_everything_is_ok(driver)
            console.log("Everything is ok!", style="green bold")

        with web.start_webdriver(headless=cls.headless) as driver:
            driver.get(config["sii"]["factura"]["compra"]["login_URL"].get())

            login_in(driver)
            choose_society(driver)  # Choose company
            # Submit form
            submit_btn = driver.find_element(By.XPATH, '//button[text()="Enviar"]')
            submit_btn.click()
            # wait until form fill is loaded
            e = '//*[@id="VIEW_EFXP"]/fieldset[1]/table[1]/tbody/tr/td[2]/table/tbody/tr[1]/td/table/tbody/tr/td/table/tbody/tr[1]/td/strong'
            web.wait_action_for_element(
                driver, search_for=e, search_by=By.XPATH, delay=10
            )

            # Check if Company RUT is correct
            loadedRUT = driver.find_element(By.XPATH, e)
            if (
                loadedRUT.text
                != f"Rut {os.getenv('CERRO_EL_PLOMO_RUT').replace('.', '')}"
            ):
                raise ValueError(
                    "[FACTURA COMPRA] RUT loaded is not the same as the one used to login"
                )
            console.log(
                "[FACTURA COMPRA] SUCCESS - RUT loaded is the same as the one used to login",
                style="green",
            )
            console.log("Filling Factura...")
            fill_factura_details(driver)

            # SUBMIT INFORMATION
            console.log(":warning: Submitting information...")
            submit_btn = driver.find_element(By.XPATH, '//*[@id="VIEW_EFXP"]/input[7]')
            submit_btn.click()

            # wait until form fill is loaded
            e = '//input[@type="button" and @value="Firmar"]'
            web.wait_action_for_element(
                driver,
                search_for=e,
                search_by=By.XPATH,
                delay=10,
                action=EC.element_to_be_clickable,
            )
            Utils.ask_confirmation(
                "[FACTURA COMPRA] Do you want to submit the form?",
                interactive,
                dont_exit=False,
            )
            firmar_btn = driver.find_element(By.XPATH, e)
            firmar_btn.click()
            # TODO: DESCARGAR ARCHIVO CUANDO YA SE HAYA FIRMADO.
            e = '//*[@id="myPass"]'
            web.wait_action_for_element(
                driver,
                search_for=e,
                search_by=By.XPATH,
                delay=10,
                action=EC.element_to_be_clickable,
            )
            psw_input = driver.find_element(By.XPATH, e)
            psw_input.clear()
            psw_input.send_keys(os.getenv("CERTIFICADO_DIGITAL_PANCHO_PSW"))
            time.sleep(round(random.random(), 2) * 2)
            console.log("Confirming factura with firma digital...")
            firmar_btn = driver.find_element(By.XPATH, '//*[@id="btnFirma"]')
            firmar_btn.click()
            # wait until form fill is loaded
            e = '//a[contains(text(), "Ver Documento")]'
            web.wait_action_for_element(
                driver,
                search_for=e,
                search_by=By.XPATH,
                delay=10,
                action=EC.element_to_be_clickable,
            )
            go_to_document = driver.find_element(By.XPATH, e)
            go_to_documentURL = go_to_document.get_attribute("href")

            Slack.send_message(
                f"Nueva factura de compra creada a nombre de ({book_to_name}) [{go_to_documentURL}]."
            )
