# SII manager for property bookings

This code if for the purpose of managing the SII needed documents (factura & boletas) when renting a property.
For now, a property rental only can be performed by `Airbnb` or `Direct booking`.

- When booking was through Airbnb: also is needed a `factura compra` for the service provided by Airbnb.
- When direct booking needs a factura, then a `factura venta` is needed instead of a `boleta` -> PENDING

> ⚠️ This flow does not support Airbnb with "factura" instead of "boletas" yet.

## Instalation

## Usage

Just run the `./app/generate_pending_documents.py` script.

### Tasks

- Check if there is a pending document to be generated. If so, notify:

    ```bash
    python -m tasks -t <task_to_run>
    ```

---

## Pending ToDo's

- [ ] Add a `factura venta` when a clients wants to pay with a `factura` instead of a `boleta`.
- [ ] Check if the SII taxes calculation is already calculated.
- [ ] Make quick command for generating a specific document for custom needs.
