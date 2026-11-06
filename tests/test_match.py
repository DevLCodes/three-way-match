from three_way_match.match import match, product_key
from three_way_match.schemas import Document


def doc(lines, total=None):
    return Document(order_id="1", lines=[{"product": p, "quantity": q, "unit_price": u} for p, q, u in lines], total=total)


LINES = [("Chai", 10, "18.00"), ("Tofu", 2, "23.25")]


def test_clean_order_is_approved():
    result = match(doc(LINES), doc(LINES), doc(LINES, total="226.50"))
    assert result.approved is True
    assert result.exceptions == []


def test_product_names_match_ignoring_case_and_spaces():
    assert product_key("  Jack's  New England CLAM Chowder ") == "jack's new england clam chowder"
    invoice = doc([("CHAI", 10, "18.00")], total="180.00")
    assert match(doc([("chai ", 10, "18.00")]), doc([("Chai", 10, "18.00")]), invoice).approved


def test_price_within_one_cent_is_accepted():
    invoice = doc([("Chai", 10, "18.01")], total="180.10")
    assert match(doc([("Chai", 10, "18.00")]), doc([("Chai", 10, "18.00")]), invoice).approved


import pytest

PO = doc(LINES)
REC = doc(LINES)
INV = doc(LINES, total="226.50")


@pytest.mark.parametrize(
    "po, receipt, invoice, codes",
    [
        (None, REC, INV, ["missing_po"]),
        (PO, None, INV, ["missing_receipt"]),
        (PO, REC, doc(LINES + [("Kaviar", 1, "15.00")], total="241.50"), ["not_on_po", "not_received"]),
        (PO, REC, doc([("Chai", 11, "18.00"), ("Tofu", 2, "23.25")], total="244.50"), ["quantity_vs_po", "quantity_vs_receipt"]),
        (PO, REC, doc([("Chai", 10, None), ("Tofu", 2, "23.25")], total="226.50"), ["price_missing", "total_mismatch"]),
        (PO, REC, doc([("Chai", 10, "19.00"), ("Tofu", 2, "23.25")], total="236.50"), ["price_vs_po"]),
        (PO, doc([("Tofu", 2, "23.25")]), INV, ["not_received"]),
        (PO, doc([("Chai", 8, "18.00"), ("Tofu", 2, "23.25")]), INV, ["quantity_vs_receipt"]),
        (PO, REC, doc(LINES, total="300.00"), ["total_mismatch"]),
        (PO, REC, doc(LINES, total=None), ["total_mismatch"]),
    ],
)
def test_each_exception_code(po, receipt, invoice, codes):
    result = match(po, receipt, invoice)
    assert [e.code for e in result.exceptions] == codes
    assert result.approved is False
