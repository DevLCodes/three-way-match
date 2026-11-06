"""Step 02.2 demo: alter order 10250's real documents one way at a time and show which exception fires."""

from decimal import Decimal

from three_way_match.match import match
from three_way_match.read import read_order
from three_way_match.schemas import Document, DocType, LineItem

docs = read_order("10250")
PO, RECEIPT, INVOICE = docs[DocType.PO], docs[DocType.RECEIPT], docs[DocType.INVOICE]


def with_lines(doc: Document, lines: list[LineItem], fix_total: bool = True) -> Document:
    """A copy of the document with new lines; by default the total is recalculated so only one thing is wrong."""
    total = sum(l.quantity * l.unit_price for l in lines if l.unit_price is not None) if fix_total else doc.total
    return doc.model_copy(update={"lines": lines, "total": total if doc.total is not None else None})


def changed(doc: Document, product: str, **fields) -> list[LineItem]:
    return [l.model_copy(update=fields) if l.product.startswith(product) else l for l in doc.lines]


SCENARIOS = {
    "no PO at all": (None, RECEIPT, INVOICE),
    "no receipt at all": (PO, None, INVOICE),
    "invoice bills an extra product": (PO, RECEIPT, with_lines(INVOICE, INVOICE.lines + [LineItem(product="Chai", quantity=1, unit_price=Decimal("18"))])),
    "invoice bills 12 chowders, PO ordered 10": (PO, RECEIPT, with_lines(INVOICE, changed(INVOICE, "Jack", quantity=Decimal(12)))),
    "invoice price for apples unreadable": (PO, RECEIPT, with_lines(INVOICE, changed(INVOICE, "Manjimup", unit_price=None), fix_total=False)),
    "invoice charges 45.00 for apples, PO says 42.40": (PO, RECEIPT, with_lines(INVOICE, changed(INVOICE, "Manjimup", unit_price=Decimal("45.00")))),
    "receipt has no pepper sauce": (PO, with_lines(RECEIPT, [l for l in RECEIPT.lines if not l.product.startswith("Louisiana")]), INVOICE),
    "only 30 of 35 apples arrived": (PO, with_lines(RECEIPT, changed(RECEIPT, "Manjimup", quantity=Decimal(30))), INVOICE),
    "invoice total printed as 1900": (PO, RECEIPT, INVOICE.model_copy(update={"total": Decimal(1900)})),
}

for name, (po, receipt, invoice) in SCENARIOS.items():
    result = match(po, receipt, invoice)
    print(f"{name}: approved={result.approved}")
    for e in result.exceptions:
        print(f"    {e.code:<20} {e.product or '':<34} {e.detail}")

print("\nreal order 11077 (no alterations):")
real = read_order("11077", log=lambda m: None)
result = match(real[DocType.PO], real[DocType.RECEIPT], real[DocType.INVOICE])
print(f"  approved={result.approved}, {len(real[DocType.INVOICE].lines)} invoice lines")
for e in result.exceptions:
    print(f"    {e.code:<20} {e.product or '':<34} {e.detail}")
