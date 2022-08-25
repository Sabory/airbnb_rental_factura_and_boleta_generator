from dataclasses import dataclass, field
from math import factorial
from retry import retry


# OWN
from config import config

from core.console import console
from core.general_utils import Utils
from core.messenger.slack import Slack

from models.bookings.abstract import Booking

from .sii_dte.abstract import Document
from .sii_dte.boleta import BoletaVenta
from .sii_dte.factura import FacturaCompra

from commands.calculate_amounts_with_and_without_taxes import (
    CalculateAmountsWithAndWithoutTaxes,
)


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

    @property
    def selling_documents_paths(self):
        return [x.path for x in self.selling_documents]

    @property
    def has_selling_documents(self):
        return len(self.selling_documents) > 0

    @retry(ValueError, tries=3)
    def calculate_amounts_with_and_without_taxes(self):
        self = CalculateAmountsWithAndWithoutTaxes.perform(booking_sii_manager=self)

    def inform_user_abount_calculations(self):
        Slack.send_message(
            f"Nueva propuesta de Boleta de venta calculada a nombre de *{self.booking.client_name}*:\n"
            + f"• IVA calculado por SII: {Utils.format_int_to_clp(self.iva_calculated_by_sii)}\n"
            + f"• Boleta con impuestos (Afecta): {Utils.format_int_to_clp(self.amt_with_taxes)}\n"
            + f"• Boleta sin impuestos (Exenta): {Utils.format_int_to_clp(self.amt_without_taxes)}\n"
            + f"• *Total de la reserva: {Utils.format_int_to_clp(self.booking.amount_received)}*"
        )
        return

    def generate_document_with_taxes(self):
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

    def generate_document_without_taxes(self):
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
        factura_file_name = f"{self.booking.client.name_without_spaces}_{self.booking.check_in:%d-%m-%Y}_FACTURA_ID-0.pdf"

        factura = FacturaCompra.generate_document(
            amount=factura_amount,
            file_name=factura_file_name,
        )

        self.buying_documents.append(factura)
        return factura
