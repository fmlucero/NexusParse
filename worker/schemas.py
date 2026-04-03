from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date

class LineItem(BaseModel):
    description: str = Field(description="Description of the item or service")
    quantity: float = Field(description="Quantity of the item")
    unit_price: float = Field(description="Price per single unit")
    total_price: float = Field(description="Total price for this line item (quantity * unit_price)")

    @validator("total_price")
    def validate_math(cls, v, values):
        if "quantity" in values and "unit_price" in values:
            expected = values["quantity"] * values["unit_price"]
            # Tolerance for floating points
            if abs(v - expected) > 0.01:
                raise ValueError(f"total_price {v} does not match quantity * unit_price ({expected})")
        return v

class InvoiceInformation(BaseModel):
    """
    Highly strict schema demonstrating structural bounds on LLM extraction.
    We enforce data types, math checking and strict formatting.
    """
    invoice_id: str = Field(description="The unique identifier for the invoice")
    date_issued: date = Field(description="The date the invoice was issued (YYYY-MM-DD)")
    vendor_name: str = Field(description="Name of the company that issued the invoice")
    vendor_tax_id: Optional[str] = Field(description="Tax ID or VAT number of the vendor, if present")
    client_name: str = Field(description="Name of the individual or company receiving the invoice")
    
    items: List[LineItem] = Field(description="List of items/services billed")
    
    subtotal: float = Field(description="Sum of all line amounts before taxes")
    tax_amount: float = Field(default=0.0, description="Amount of taxes applied")
    total_due: float = Field(description="Final total amount due (subtotal + tax_amount)")

    @validator("total_due")
    def validate_totals(cls, v, values):
        if "subtotal" in values and "tax_amount" in values:
            expected = values["subtotal"] + values["tax_amount"]
            if abs(v - expected) > 0.01:
                raise ValueError(f"total_due {v} does not match subtotal + tax_amount ({expected})")
        return v
