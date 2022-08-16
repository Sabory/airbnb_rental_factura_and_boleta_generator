import os
from dataclasses import dataclass, field
import time
from retry import retry

# SELENIUM IMPORTS
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# OWN
from config import config

from core.console import console
import core.webdriver as web
from core.general_utils import Utils
from core.messenger.slack import Slack

from models.bookings.abstract import Booking

from .sii_dte.abstract import Document
from .sii_dte.boleta import BoletaVenta
from .sii_dte.factura import FacturaCompra

from .sii import SII


@dataclass
class BookingSIIManager:
    booking: Booking
    amt_with_taxes: int = field(init=False, repr=True)
    amt_without_taxes: int = field(init=False, repr=True)
    iva_calculated_by_sii: int = field(init=False, repr=False)
    selling_documents: list[Document] = field(
        init=False, repr=False, default_factory=lambda: []
    )  # BOLETAS O FACTURAS
    buying_documents: list[Document] = field(
        init=False, repr=False, default_factory=lambda: []
    )  # FACTURAS POR SERVICIO DE AIRBNB

    def __post_init__(self):
        self.calculate_amounts_with_and_without_taxes()
        self.inform_user_abount_calculations()

    @retry(ValueError, tries=3)
    def calculate_amounts_with_and_without_taxes(self):
        def select_month_and_year(driver, month, year):
            search_box = driver.find_element(By.ID, "item-form")
            search_items = search_box.find_elements(By.CLASS_NAME, "gwt-ListBox")
            if len(search_items) != 2:
                raise ValueError("Could not find search items in SII")
            # MONTH SELECT
            month_select = Select(search_items[0])
            month_select.select_by_value(str(month - 1))
            # YEAR SELECT
            year_input = Select(search_items[1])
            year_input.select_by_visible_text(str(year))
            # SUBMIT BTN
            btn = search_box.find_element(By.CLASS_NAME, "gwt-Button")
            btn.send_keys("\n")
            web.wait_action_for_element(
                driver,
                search_for="tabla_internet",
                search_by=By.CLASS_NAME,
                delay=5,
                action=EC.visibility_of_element_located,
            )

        def select_rol(driver, search_rol):
            info_panel = driver.find_element(By.CLASS_NAME, "panel-derecho")
            info_panel_rows = info_panel.find_elements(By.TAG_NAME, "tr")
            input_for_rol = None
            for row in info_panel_rows:
                td = row.find_elements(By.TAG_NAME, "td")
                for cell in td:
                    if search_rol in cell.text:
                        flag_mark = row.find_element(By.TAG_NAME, "input")
                        flag_mark.click()
                        input_for_rol = flag_mark

            if not input_for_rol:
                console.log(f"Could not find rol {search_rol}")
                raise ValueError(f"Could not find rol {search_rol}")

            if not flag_mark.is_selected():
                raise ValueError("Could not select rol")

        def get_iva_amout_for_booking(driver, booking_amount, nights):
            number_of_nights_input = driver.find_element(
                By.XPATH, '//*[@id="item-form"]/div[3]/div[1]/input'
            )
            number_of_nights_input.clear()
            number_of_nights_input.send_keys(nights)
            time.sleep(1)
            total_amount_input = driver.find_element(
                By.XPATH, '//*[@id="item-form"]/div[3]/div[2]/input'
            )
            total_amount_input.clear()
            total_amount_input.send_keys(booking_amount)
            time.sleep(1)
            btn_data_panel = driver.find_element(
                By.XPATH, '//*[@id="item-form"]/div[9]/button'
            )
            btn_data_panel.send_keys("\n")
            # Wait until loading icon disappears
            loading_widget = {
                "name": "gwt-PopupPanel processing-widget",
                "type": By.CLASS_NAME,
            }
            time.sleep(0.5)
            web.wait_action_for_element(
                driver,
                search_for=loading_widget["name"],
                search_by=loading_widget["type"],
                delay=10,
                action=EC.invisibility_of_element_located,
            )
            # Get resultado from SII and save it to a variable
            time.sleep(0.5)
            result_input = driver.find_element(
                By.XPATH, '//*[@id="item-form"]/div[13]/div/input'
            )
            iva = int(
                result_input.get_attribute("value").replace(".", "").replace("$", "")
            )
            return iva

        def calculate_amounts_with_and_without_taxes(self):
            with_taxes = (
                self.iva_calculated_by_sii
                * (1 + self.booking.tax_iva)
                / config["sii"]["IVA"].get(float)
            )
            without_taxes = self.booking.amount_received - with_taxes
            return round(with_taxes), round(without_taxes)

        def login_in(driver):
            SII.login_to_sii(
                driver,
                usr=os.getenv("SII_CERRO_EL_PLOMO_USR"),
                psw=os.getenv("SII_CERRO_EL_PLOMO_PSW"),
                time_sleep_after=3,
            )
            # COnfirmation of login.
            web.wait_action_for_element(
                driver,
                search_for="item-form",
                search_by=By.ID,
                delay=10,
                action=EC.presence_of_element_located,
            )
            console.log("SII login successful", style="green")

        with web.start_webdriver(headless=True) as driver:
            driver.get(config["sii"]["IVA_calculator"]["URL"].get())
            login_in(driver)
            select_month_and_year(
                driver,
                month=self.booking.check_in.month,
                year=self.booking.check_in.year,
            )
            select_rol(driver, search_rol=os.getenv("SII_CERRO_EL_PLOMO_ROL"))
            self.iva_calculated_by_sii = get_iva_amout_for_booking(
                driver,
                booking_amount=self.booking.amount_received,
                nights=self.booking.stayed_nights,
            )

        (
            self.amt_with_taxes,
            self.amt_without_taxes,
        ) = calculate_amounts_with_and_without_taxes(self)

        if (
            self.amt_with_taxes + self.amt_without_taxes
        ) != self.booking.amount_received:
            ValueError(
                f"Calculated amounts do not match with booking total amount.\n"
                f"Calculated with taxes: {self.amt_with_taxes}\n"
                f"Calculated without taxes: {self.amt_without_taxes}\n"
                f"Booking total amount: {self.booking.amount_received}"
            )
        return

    def inform_user_abount_calculations(self):
        Slack.send_message(
            f"Nueva propuesta de Boleta de venta calculada a nombre de *{self.booking.client_name}*:\n"
            + f"• IVA calculado por SII: {Utils.format_int_to_clp(self.iva_calculated_by_sii)}\n"
            + f"• Boleta con impuestos (Afecta): {Utils.format_int_to_clp(self.amt_with_taxes)}\n"
            + f"• Boleta sin impuestos (Exenta): {Utils.format_int_to_clp(self.amt_without_taxes)}\n"
            + f"• *Total de la reserva: {Utils.format_int_to_clp(self.booking.amount_received)}*"
        )
        return

    def generate_boleta_with_taxes(self):
        file_name = f"{self.booking.client_name.replace(' ', '-')}_{self.booking.check_in:%d-%m-%Y}_AFECTA"

        boleta_w_taxes = BoletaVenta.generate_document(
            amount=self.amt_with_taxes,
            with_taxes=True,
            stayed_nights=self.booking.stayed_nights,
            total_payment_amount=self.booking.amount_received,
            file_name=file_name,
        )
        self.selling_documents.append(boleta_w_taxes)
        console.log(f"Boleta successfully generated", style="bold green")
        return boleta_w_taxes

    def generate_boleta_without_taxes(self):
        file_name = f"{self.booking.client_name.replace(' ', '-')}_{self.booking.check_in:%d-%m-%Y}_EXENTA"

        boleta_wout_taxes = BoletaVenta.generate_document(
            amount=self.amt_without_taxes,
            with_taxes=False,
            stayed_nights=self.booking.stayed_nights,
            total_payment_amount=self.booking.amount_received,
            file_name=file_name,
        )
        self.selling_documents.append(boleta_wout_taxes)
        console.log(f"Boleta successfully generated", style="bold green")
        return boleta_wout_taxes

    def generate_factura(self):
        if not self.booking.need_factura:
            return None

        factura_amount = self.booking.facturable_amount
        book_to_name = self.booking.client.name

        factura = FacturaCompra.generate_document(
            amount=factura_amount, book_to_name=book_to_name
        )
        self.buying_documents.append(factura)
        return
