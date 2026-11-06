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
