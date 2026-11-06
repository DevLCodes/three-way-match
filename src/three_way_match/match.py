"""Three-way match with fixed rules. No LLM is involved: code decides whether money can be paid."""

import sys
from decimal import Decimal

from .schemas import Document, Exception_, LineItem, MatchResult

TOLERANCE = Decimal("0.01")


def product_key(product: str) -> str:
    """Join lines by product name, ignoring case and extra spaces: 'Chai ' and 'chai' are the same product."""
    return " ".join(product.casefold().split())


def by_product(doc: Document | None) -> dict[str, LineItem]:
    return {product_key(line.product): line for line in doc.lines} if doc else {}


def match(po: Document | None, receipt: Document | None, invoice: Document) -> MatchResult:
    """Compare every invoice line with the PO (ordered) and the receipt (delivered), then check the invoice's arithmetic."""
    found: list[Exception_] = []
    if po is None:
        found.append(Exception_(code="missing_po", detail="No purchase order found"))
    if receipt is None:
        found.append(Exception_(code="missing_receipt", detail="No receipt found"))

    ordered_lines, received_lines = by_product(po), by_product(receipt)
    for key, line in by_product(invoice).items():
        name = line.product
        if po:
            ordered = ordered_lines.get(key)
            if ordered is None:
                found.append(Exception_(code="not_on_po", product=name, detail="Invoiced but not ordered"))
            else:
                if line.quantity != ordered.quantity:
                    found.append(Exception_(code="quantity_vs_po", product=name, detail=f"Invoiced {line.quantity}, ordered {ordered.quantity}"))
                if line.unit_price is None or ordered.unit_price is None:
                    found.append(Exception_(code="price_missing", product=name, detail="Unit price not found"))
                elif abs(line.unit_price - ordered.unit_price) > TOLERANCE:
                    found.append(Exception_(code="price_vs_po", product=name, detail=f"Invoiced {line.unit_price}, ordered at {ordered.unit_price}"))
        if receipt:
            received = received_lines.get(key)
            if received is None:
                found.append(Exception_(code="not_received", product=name, detail="Invoiced but not received"))
            elif line.quantity > received.quantity:
                found.append(Exception_(code="quantity_vs_receipt", product=name, detail=f"Invoiced {line.quantity}, received {received.quantity}"))

    calculated = sum((l.quantity * l.unit_price for l in invoice.lines if l.unit_price is not None), Decimal(0))
    if invoice.total is None or abs(invoice.total - calculated) > TOLERANCE:
        found.append(Exception_(code="total_mismatch", detail=f"Invoice total {invoice.total}, lines add up to {calculated}"))

    return MatchResult(order_id=invoice.order_id, approved=not found, exceptions=found)


if __name__ == "__main__":
    from .read import read_order
    from .schemas import DocType

    docs = read_order(sys.argv[1])
    po, receipt, invoice = docs[DocType.PO], docs[DocType.RECEIPT], docs[DocType.INVOICE]
    if invoice is None:
        raise SystemExit(f"No invoice for order {sys.argv[1]}")
    ordered, received = by_product(po), by_product(receipt)
    print(f"{'product':<34} {'invoiced':>12} {'ordered (PO)':>14} {'received':>9}")
    for key, line in by_product(invoice).items():
        o, r = ordered.get(key), received.get(key)
        inv = f"{line.quantity} @ {line.unit_price}"
        po_text = f"{o.quantity} @ {o.unit_price}" if o else "-"
        print(f"{line.product:<34} {inv:>12} {po_text:>14} {str(r.quantity) if r else '-':>9}")
    calculated = sum(l.quantity * l.unit_price for l in invoice.lines if l.unit_price is not None)
    print(f"{'invoice total':<34} {str(invoice.total):>12}   lines add up to {calculated}")
    print()
    print(match(po, receipt, invoice).model_dump_json(indent=2))
