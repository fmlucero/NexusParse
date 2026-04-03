import pytest
from pydantic import ValidationError
from worker.schemas import InvoiceInformation, LineItem
from datetime import date

def test_valid_invoice_schema():
    # Strict valid calculation
    invoice = InvoiceInformation(
        invoice_id="123",
        date_issued=date(2023, 10, 1),
        vendor_name="Acme Corp",
        client_name="Test Client",
        items=[
            LineItem(description="Service A", quantity=2, unit_price=10.0, total_price=20.0)
        ],
        subtotal=20.0,
        tax_amount=2.0,
        total_due=22.0
    )
    assert invoice.total_due == 22.0

def test_invalid_math_schema():
    # Intentional math error (e.g., an LLM hallucination where quantity * unit_price != total_price)
    with pytest.raises(ValidationError) as exc_info:
        InvoiceInformation(
            invoice_id="123",
            date_issued=date(2023, 10, 1),
            vendor_name="Acme Corp",
            client_name="Test Client",
            items=[
                LineItem(description="Service A", quantity=2, unit_price=10.0, total_price=30.0) # Should be 20
            ],
            subtotal=20.0,
            tax_amount=2.0,
            total_due=22.0
        )
    assert "does not match quantity * unit_price" in str(exc_info.value)

def test_invalid_totals_schema():
    with pytest.raises(ValidationError) as exc_info:
        InvoiceInformation(
            invoice_id="123",
            date_issued=date(2023, 10, 1),
            vendor_name="Acme Corp",
            client_name="Test Client",
            items=[
                LineItem(description="Service A", quantity=1, unit_price=20.0, total_price=20.0)
            ],
            subtotal=20.0,
            tax_amount=5.0,
            total_due=20.0 # Should be 25!
        )
    assert "does not match subtotal + tax_amount" in str(exc_info.value)
