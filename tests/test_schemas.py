from decimal import Decimal

import pytest
from pydantic import ValidationError

from three_way_match.schemas import Document, DocType

GOOD = {"order_id": "10250", "lines": [{"product": "Chai", "quantity": 10, "unit_price": "18.00"}], "total": "180.00"}


def test_money_is_exact_decimal():
    doc = Document.model_validate(GOOD)
    assert doc.lines[0].unit_price == Decimal("18.00")
    assert doc.total == Decimal("180.00")


@pytest.mark.parametrize(
    "change",
    [
        {"lines": [{"product": "Chai", "quantity": -1}]},
        {"lines": [{"product": "", "quantity": 1}]},
        {"lines": [{"product": "Chai", "quantity": 1, "unit_price": "$18"}]},
        {"note": "extra"},
        {"order_id": ""},
    ],
)
def test_invalid_documents_are_rejected(change):
    with pytest.raises(ValidationError):
        Document.model_validate(GOOD | change)


def test_doc_type_values():
    assert [t.value for t in DocType] == ["purchase_order", "receipt", "invoice"]
