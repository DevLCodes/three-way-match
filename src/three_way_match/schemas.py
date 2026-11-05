"""The exact shape of an extracted document. Anything else is rejected before it reaches the matcher."""

from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class DocType(StrEnum):
    PO = "purchase_order"
    RECEIPT = "receipt"
    INVOICE = "invoice"


class LineItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product: str = Field(min_length=1)
    quantity: Decimal = Field(ge=0)
    unit_price: Decimal | None = Field(default=None, ge=0)


class Document(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: str = Field(min_length=1)
    doc_date: str | None = None
    party: str | None = None
    lines: list[LineItem]
    total: Decimal | None = None
