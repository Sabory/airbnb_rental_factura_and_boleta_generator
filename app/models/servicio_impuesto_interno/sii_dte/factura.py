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
    headless: bool = config["sii"]["factura"]["compra"]["headless"].get(bool)
    LEGAL_REPRESENTATIVE = config["sii"]["company"]["legal_representative"]
    FACTURAS_DOWNLOAD_DIRECTORY = "./data/facturas/"
    BASE_FILE_NAME = "pending_factura_"

    @classmethod
    def generate_document(
        cls,
        amount: int,
        file_name: str,
        rut: str = config["airbnb"]["factura"]["RUT"].get(str),
        street: str = config["airbnb"]["factura"]["street"].get(str),
        comuna: str = config["airbnb"]["factura"]["comuna"].get(str),
        city: str = config["airbnb"]["factura"]["city"].get(str),
        giro: str = config["airbnb"]["factura"]["giro"].get(str),
        detalle: str = config["airbnb"]["factura"]["details"].get(str),
        interactive: bool = True,
    ):
        assert amount > 0 and isinstance(
            amount, int
        ), "Amount must be a integer and greater than 0"

        def login_in(driver):
            SII.login_to_sii(
                driver,
                usr=cls.LEGAL_REPRESENTATIVE["sii_account"]["user"].get(str),
                psw=cls.LEGAL_REPRESENTATIVE["sii_account"]["password"].get(str),
            )
            # COnfirmation of login.
            web.wait_action_for_element(
                driver,
                search_for='//select[@class="form-control" and @name="RUT_EMP"]',
                search_by=By.XPATH,
                delay=10,
                action=EC.element_to_be_clickable,
            )

        def choose_society(driver):
            emp_ruts = driver.find_element(
                By.XPATH, '//*[@class="form-control" and @name="RUT_EMP"]'
            )
            emp_select = Select(emp_ruts)
            rut = config["sii"]["company"]["rut"].get(str).replace(".", "")
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
            alert.accept()

            # ADDRESS
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
            cod_prod_input = Select(
                driver.find_element(By.XPATH, '//select[@name="EFXP_COD_01"]')
            )
            cod_prod_input.select_by_value("1500")
            time.sleep(round(random.random(), 2) * 3)

            # Descrip flag
            descrip_flag_input = driver.find_element(
                By.XPATH, '//input[@name="DESCRIP_01"]'
            )
            descrip_flag_input.click()
            time.sleep(round(random.random(), 2) * 3)
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
            cantidad_input = driver.find_element(
                By.XPATH, '//input[@name="EFXP_QTY_01"]'
            )
            input_keys(driver, cantidad_input, "1")

            # Precio
            precio_input = driver.find_element(By.XPATH, '//input[@name="EFXP_PRC_01"]')
            input_keys(driver, precio_input, amount)
            # UN FOCUS precio
            cantidad_input.click()

            recheck_everything_is_ok(driver)

        with web.start_webdriver(headless=cls.headless) as driver:
            driver.get(config["sii"]["factura"]["compra"]["login_URL"].get(str))

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
                != f'Rut {config["sii"]["company"]["rut"].get(str).replace(".", "")}'
            ):
                raise ValueError(
                    "[FACTURA COMPRA] RUT loaded is not the same as the one used to login"
                )
            console.log(
                "[FACTURA COMPRA] SUCCESS - RUT loaded is the same as the one used to login",
                style="green",
            )
            fill_factura_details(driver)

            # SUBMIT INFORMATION
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
            psw_input.send_keys(
                cls.LEGAL_REPRESENTATIVE["sii_account"]["digital_certificate"].get(str)
            )
            time.sleep(round(random.random(), 2) * 2)
            console.log("Confirming factura with firma digital...", style="bold yellow")
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
            go_to_document.click()

            print(
                f"Please download the file manually and upload it to: {cls.FACTURAS_DOWNLOAD_DIRECTORY}.",
                f"With a file name: {cls.BASE_FILE_NAME}<id>.pdf",
            )
            generated_factura_path = None
            while generated_factura_path is None:
                if os.path.exists(cls.FACTURAS_DOWNLOAD_DIRECTORY):
                    all_files = os.listdir(cls.FACTURAS_DOWNLOAD_DIRECTORY)
                    for file in all_files:
                        if cls.BASE_FILE_NAME in file:
                            print("File found!")
                            generated_factura_path = os.path.join(
                                cls.FACTURAS_DOWNLOAD_DIRECTORY, file
                            )
                            original_file_name = file

                time.sleep(1)

            factura_id = int(
                original_file_name.split(cls.BASE_FILE_NAME)[1].split(".pdf")[0]
            )
            file_name = file_name.replace("ID-0", f"ID-{factura_id}")

            generated_factura_path_procesed = os.path.join(
                cls.FACTURAS_DOWNLOAD_DIRECTORY, file_name
            )

            os.rename(generated_factura_path, generated_factura_path_procesed)

            factura = cls(
                id=factura_id,
                file_name=os.path.basename(generated_factura_path_procesed),
                url=None,
                with_taxes=True,
            )

            factura.path = generated_factura_path_procesed

            return factura
