import time

# SELENIUM IMPORTS
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


from config import config
import core.webdriver as web
from core.console import console
from models.servicio_impuesto_interno.sii import SII

from commands import CommandAbstract


class CalculateAmountsWithAndWithoutTaxes(CommandAbstract):
    @classmethod
    def perform(cls, booking_sii_manager):
        with web.start_webdriver(headless=True) as driver:
            driver.get(config["sii"]["IVA_calculator"]["URL"].get(str))
            cls._login_in(driver)
            cls._select_month_and_year(
                driver,
                month=booking_sii_manager.booking.check_in.month,
                year=booking_sii_manager.booking.check_in.year,
            )
            cls._select_rol(
                driver,
                search_rol=config["sii"]["company"]["sii_account"]["rol"].get(str),
            )

            booking_sii_manager.iva_calculated_by_sii = cls._get_iva_amout_for_booking(
                driver,
                booking_amount=booking_sii_manager.booking.amount_received,
                nights=booking_sii_manager.booking.stayed_nights,
            )

        (
            booking_sii_manager.amt_with_taxes,
            booking_sii_manager.amt_without_taxes,
        ) = cls._calculate_amounts_with_and_without_taxes(booking_sii_manager)

        if (
            booking_sii_manager.amt_with_taxes + booking_sii_manager.amt_without_taxes
        ) != booking_sii_manager.booking.amount_received:
            ValueError(
                f"Calculated amounts do not match with booking total amount.\n"
                f"Calculated with taxes: {booking_sii_manager.amt_with_taxes}\n"
                f"Calculated without taxes: {booking_sii_manager.amt_without_taxes}\n"
                f"Booking total amount: {booking_sii_manager.booking.amount_received}"
            )
        return booking_sii_manager

    def _select_month_and_year(driver, month, year):
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

    def _select_rol(driver, search_rol):
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

    def _get_iva_amout_for_booking(driver, booking_amount, nights):
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
        iva = int(result_input.get_attribute("value").replace(".", "").replace("$", ""))
        return iva

    def _calculate_amounts_with_and_without_taxes(booking_sii_manager):
        with_taxes = (
            booking_sii_manager.iva_calculated_by_sii
            * (1 + booking_sii_manager.booking.tax_iva)
            / config["sii"]["IVA"].get(float)
        )
        without_taxes = booking_sii_manager.booking.amount_received - with_taxes
        return round(with_taxes), round(without_taxes)

    def _login_in(driver):
        SII.login_to_sii(
            driver,
            usr=config["sii"]["company"]["sii_account"]["user"].get(str),
            psw=config["sii"]["company"]["sii_account"]["password"].get(str),
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
