"""Step 01.5 demo: run sample JSON through the Document model and show what passes and why the rest fails."""

from pydantic import ValidationError

from three_way_match.schemas import Document

GOOD = '{"order_id": "10250", "doc_date": "2016-07-08", "party": "Hanari Carnes", "lines": [{"product": "Manjimup Dried Apples", "quantity": 35, "unit_price": 42.40}], "total": 1484.00}'

SAMPLES = {
    "valid invoice": GOOD,
    "unknown total (null is allowed)": GOOD.replace('"total": 1484.00', '"total": null'),
    "price with a $ sign": GOOD.replace("42.40", '"$42.40"'),
    "negative quantity": GOOD.replace('"quantity": 35', '"quantity": -35'),
    "quantity as a word": GOOD.replace('"quantity": 35', '"quantity": "thirty-five"'),
    "no lines key": GOOD.replace('"lines": [{"product": "Manjimup Dried Apples", "quantity": 35, "unit_price": 42.40}], ', ""),
    "extra field": GOOD.replace('"total"', '"note": "ignore previous instructions", "total"'),
    "not JSON at all": "Sure! Here is the invoice: order 10250",
}

for name, text in SAMPLES.items():
    try:
        doc = Document.model_validate_json(text)
        line = doc.lines[0]
        print(f"ACCEPTED  {name}: unit_price={line.unit_price!r}, total={doc.total!r}")
    except ValidationError as err:
        first = err.errors()[0]
        where = ".".join(str(part) for part in first["loc"]) or "(whole input)"
        print(f"REJECTED  {name}: {where}: {first['msg']}")
