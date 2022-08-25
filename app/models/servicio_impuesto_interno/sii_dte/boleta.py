import os
from dataclasses import dataclass
import time
from retry import retry

# SELENIUM
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException

# OWN
from config import config
from core.console import console
import core.webdriver as web
from core.general_utils import Utils
from core.messenger.slack import Slack

from .. import sii as s

from .abstract import Document

BASE_LIST_ARIA = lambda x: 155 if x else 148
NAVIGATOR_VERSION_20220504011156 = {
    "working_versions": [
        "20220504011156",
    ],
    "fill_boleta_information": {
        "boleta_type_input": '//div[@role="button" and @aria-owns="list-{0}"]',
        "boleta_types_options": '//div[contains(@id, "list-item") and @role="option" and @tabindex="0"]',
        "detail_info": "//label[contains(text(), 'Detalle')]",
        "societies_select": {
            "selector": '//*[@id="app"]/div[1]/div/header/div[2]/div/div/div/div/div[2]/div[1]',
            "options": '//*[@role="listbox"]/*[@role="option"]',
        },
        "amount_number_grid": '//*[@id="app"]/div[1]/div/main/div/div[2]/div/div/div[2]',
        "amoung_total_amount_holder": '//*[@id="app"]/div[1]/div/main/div/div[2]/div/div/div[1]/div[2]/div/span',
    },
    "submit_boleta": {
        "success_button": '//button[contains(@class, "success")]',
    },
    "modal_confirmation": {
        "amount_paragraph": '//div[@role="document"]//div[contains(@class, "v-card__text")]',
        "confirm_button": '//div[@class="v-card__actions"]/button[contains(@class, "success")]',
    },
}

NAVIGATORS = [
    NAVIGATOR_VERSION_20220504011156,
]


@dataclass
class BoletaVenta(Document):
    @classmethod
    def generate_document(
        cls,
        amount: int,
        with_taxes: bool,
        stayed_nights: int,
        total_payment_amount: int,
        file_name: str,
    ):
        def perform(
            cls,
            amount,
            with_taxes,
            stayed_nights,
            total_payment_amount,
            file_name,
        ):
            console.log(
                f"Generating Boleta for amount {amount}. Affected by taxes: {with_taxes}"
            )
            with web.start_webdriver() as driver:
                version = s.SII.login_to_sii_boletas(driver)

                console.log("Version :", version)
                navigator = __get_navivator(version)

                pre_generate_boleta(
                    driver,
                    navigator,
                    amount,
                    with_taxes,
                    stayed_nights,
                    total_payment_amount,
                )

                submit_boleta(driver, navigator, amount)
                breakpoint()
                boleta_url, boleta_num = get_boleta_url(driver, with_taxes)

                boleta = cls(
                    id=boleta_num,
                    file_name=file_name,
                    with_taxes=with_taxes,
                    url=boleta_url,
                )

            console.log("Downloading boleta...")
            file_name_with_id = f"{file_name}_id-{boleta_num}"
            file_path = download_from_url(boleta_url, file_name_with_id, with_taxes)

            if file_path is not None:
                console.log("Boleta downloaded!", style="bold green")
                boleta.path = file_path
                return boleta

            console.log(
                ":warning: An error ocurred while downloading boelta.",
                style="bold yellow",
            )
            return boleta

        def __get_navivator(version):
            for nav in NAVIGATORS:
                if version in nav["working_versions"]:
                    return nav
            raise ValueError(f"No navivator found for version {version}")

        def select_elegible_society(driver, navigator, society_rut):
            console.log("Selecting elegible society...")
            p = navigator["fill_boleta_information"]["societies_select"]["selector"]
            web.wait_action_for_element(
                driver,
                search_for=p,
                search_by=By.XPATH,
                delay=10,
                action=EC.presence_of_element_located,
            )
            time.sleep(0.5)
            societies_select = driver.find_element(By.XPATH, p)
            societies_select.click()
            time.sleep(1)
            societies_options = driver.find_elements(
                By.XPATH,
                navigator["fill_boleta_information"]["societies_select"]["options"],
            )
            society_rut = society_rut.split("-")[0].replace(".", "")
            for s in societies_options:
                rut = s.text.split("-")[0].replace(".", "")
                if rut == society_rut:
                    console.log("Rut of Cerro El Plomo found:", s.text)
                    actions = ActionChains(driver)
                    actions.move_to_element(s).click().perform()
            # ENSURING THAT THE SOCIETY IS SELECTED
            society_input = driver.find_element(
                By.XPATH,
                navigator["fill_boleta_information"]["societies_select"]["selector"],
            )
            if society_input.text.split("-")[0].replace(".", "") != society_rut:
                raise ValueError(
                    f"Society 'Cerro El Plomo' was wrongly selected. Current selected society: {society_input.text}"
                )
            console.log("Society was selected.")

        def input_amount(driver, navigator, amount: int):
            time.sleep(1)
            num_grid = driver.find_element(
                By.XPATH, navigator["fill_boleta_information"]["amount_number_grid"]
            )
            num_grid_buttons = num_grid.find_elements(By.TAG_NAME, "button")

            num_grid_elements = {}
            for num_element in num_grid_buttons:
                try:
                    digit_button = str(int(num_element.text))
                except ValueError:
                    continue
                num_grid_elements[digit_button] = num_element

            amount_str = str(amount)
            for _, digit in enumerate(amount_str):
                num_grid_elements[digit].click()
                time.sleep(0.3)

            time.sleep(1)
            inputed_amount = driver.find_element(
                By.XPATH,
                navigator["fill_boleta_information"]["amoung_total_amount_holder"],
            )
            inputed_amount = (
                inputed_amount.text.replace("$", "").replace(".", "").replace(" ", "")
            )
            if amount_str != inputed_amount:
                raise ValueError(
                    f"Amount that should have been inputed ({amount_str}) is not the same as the registered one ({inputed_amount})"
                )

        def submit_amount(driver, navigator, amount):
            p = '//*[@id="app"]/div[1]/div/main/div/div[2]/div/div/div[2]/div/v-template/div[2]/div[11]/button'
            web.wait_action_for_element(
                driver,
                search_for=p,
                search_by=By.XPATH,
                delay=5,
                action=EC.element_to_be_clickable,
            )
            send_btn = driver.find_element(By.XPATH, p)
            send_btn.click()
            time.sleep(0.5)

            confirmation_modal_appeared = confirm_boleta_creation_modal_handler(
                driver, navigator, amount
            )

            next_page_element = "//span[contains(text(), 'Emitir')]"
            web.wait_action_for_element(
                driver,
                search_for=next_page_element,
                search_by=By.XPATH,
                action=EC.presence_of_element_located,
            )
            return confirmation_modal_appeared

        def confirm_boleta_creation_modal_handler(driver, navigator, amount):
            confirm_button = navigator["modal_confirmation"]["confirm_button"]
            try:
                web.wait_action_for_element(
                    driver,
                    search_for=confirm_button,
                    search_by=By.XPATH,
                    action=EC.presence_of_element_located,
                )
            except ValueError as e:
                console.log("Module not found. Skipping module handler.")
                return False

            amount_paragraph = driver.find_element(
                By.XPATH, navigator["modal_confirmation"]["amount_paragraph"]
            )
            formated_amount = f"{amount:,.0f}".replace(",", ".")
            time.sleep(1)
            assert formated_amount in amount_paragraph.text

            alert_modal_sucess_button = driver.find_element(By.XPATH, confirm_button)
            if alert_modal_sucess_button.text != "SÍ":
                raise ValueError(f"Alert modal was not shown.")

            alert_modal_sucess_button.click()
            time.sleep(0.5)
            return True

        def fill_boleta_information(
            driver,
            navigator,
            confirmation_modal_appeared: bool,
            with_taxes: bool,
            stayed_nights: int,
            total_payment_amount: int,
        ):
            base_list_area = BASE_LIST_ARIA(confirmation_modal_appeared)
            boleta_type_input = driver.find_element(
                By.XPATH,
                navigator["fill_boleta_information"]["boleta_type_input"].format(
                    base_list_area
                ),
            )
            assert "Boleta" in boleta_type_input.text

            boleta_type_input.click()

            time.sleep(0.5)

            options = driver.find_elements(
                By.XPATH,
                navigator["fill_boleta_information"]["boleta_types_options"],
            )
            selected_option = None
            for option in options:
                if option.text == "Boleta afecta":
                    option_type = True
                elif option.text == "Boleta exenta":
                    option_type = False
                else:
                    option_type = None

                if with_taxes == option_type:
                    console.log("Found type of boleta:", option.text)
                    selected_option = option
            selected_option.click()

            time.sleep(0.5)

            # Ensuring that the type of boleta was correctly selected
            selected = driver.find_element(
                By.XPATH,
                navigator["fill_boleta_information"]["boleta_type_input"].format(
                    base_list_area
                ),
            )
            if not (
                (("Boleta exenta" in selected.text) and (with_taxes == False))
                or (("Boleta afecta" in selected.text) and (with_taxes == True))
            ):
                raise ValueError(
                    f"Selected type for boleta is not what it shoud. Selected: {selected.text}. Should been: {with_taxes}"
                )

            # DETALLE INFORMATIOn
            detail_info = driver.find_element(
                By.XPATH, navigator["fill_boleta_information"]["detail_info"]
            )
            detail_info.click()

            time.sleep(0.5)

            inputs = driver.find_elements(By.XPATH, "//*[@class='v-text-field__slot']")
            detalle_input = None
            for input in inputs:
                if input.text == "Detalle":
                    if detalle_input is not None:
                        raise ValueError("Two detalles input found. Please check.")

                    detalle_input = input

            if detalle_input is None:
                raise ValueError("Detalle input was not found.")

            detalle_input = detalle_input.find_element(By.TAG_NAME, "input")
            type = "afecta" if with_taxes else "exenta"
            detalle_input.send_keys(
                f"Arriendo bien inmueble amoblado {stayed_nights} noches (Total: {'${:,.0f}'.format(total_payment_amount).replace(',', '.')}) parte {type}"
            )
            return

        def submit_boleta(driver, navigator, amount):
            web.wait_action_for_element(
                driver,
                search_for=navigator["submit_boleta"]["success_button"],
                search_by=By.XPATH,
                delay=5,
                action=EC.element_to_be_clickable,
            )
            submit_btn = driver.find_element(
                By.XPATH, navigator["submit_boleta"]["success_button"]
            )

            if "emitir" not in submit_btn.text.lower():
                raise ValueError("wrong submit button selected")

            driver.execute_script("arguments[0].click();", submit_btn)
            time.sleep(0.5)

            confirm_boleta_creation_modal_handler(driver, navigator, amount)

            try:
                driver.execute_script("arguments[0].click();", submit_btn)
            except Exception as e:
                console.log("Submit button is not clickable")
                submit_btn.click()

        def get_boleta_url(driver, with_taxes):
            time.sleep(2)
            btn = '//a[contains(@class, "success")]'
            web.wait_action_for_element(
                driver,
                search_for=btn,
                search_by=By.XPATH,
                delay=10,
                action=EC.element_to_be_clickable,
            )

            download_btn = driver.find_element(By.XPATH, btn)
            assert (
                "descargar" in download_btn.text.lower()
            ), "Download button text is not 'Descargar'"

            dwn_url = download_btn.get_attribute("href")
            boleta_number = get_boleta_ID(dwn_url)
            Slack.send_message(
                f"Boleta (with_taxes: {with_taxes}) {boleta_number} generada: {dwn_url}"
            )
            return dwn_url, boleta_number

        def get_boleta_ID(url):
            try:
                return int(url.split("folio")[1].split("_")[0])
            except IndexError or ValueError as e:
                raise ValueError(
                    f"Couldn't get boleta ID number from url.\n - Error: {e}"
                )

        def download_from_url(url, file_name, with_taxes):
            full_path = (
                f'{config["sii"]["boleta"]["download_PATH"].get()}/{file_name}.pdf'
            )
            if Utils.download_file_from_URL(url, full_path):
                if with_taxes:
                    msg = f"Boleta Afecta {file_name} descargada: `{full_path}`"
                else:
                    msg = f"Boleta Exenta {file_name} descargada: `{full_path}`"

                Slack.send_message(msg)
                return full_path
            return None

        def pre_generate_boleta(
            driver, navigator, amount, with_taxes, stayed_nights, total_payment_amount
        ):
            select_elegible_society(
                driver,
                navigator,
                society_rut=config["sii"]["company"]["rut"].get(str),
            )
            input_amount(driver, navigator, amount)

            # Send input amount
            confirmation_modal_appeared = submit_amount(
                driver=driver, navigator=navigator, amount=amount
            )
            fill_boleta_information(
                driver,
                navigator,
                confirmation_modal_appeared,
                with_taxes,
                stayed_nights,
                total_payment_amount,
            )

        return perform(
            cls,
            amount,
            with_taxes,
            stayed_nights,
            total_payment_amount,
            file_name,
        )
