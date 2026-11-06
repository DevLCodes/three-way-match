"""Catch parser read errors: every money amount in the PDF's own text layer must also appear in the parsed text."""

import re
import sys
from decimal import Decimal
from pathlib import Path

import pypdfium2 as pdfium

# Any decimal number, with or without a $: $1,374.60 on invoices, 7.7 on receipts and POs.
# Parsed text writes $ as \$ (LaTeX escape), so the $ is optional. Dates (2016-07-08) have no decimal point.
MONEY = re.compile(r"\$?\s?(\d[\d,]*\.\d+)")
NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")


def text_layer(pdf_path: Path) -> str:
    """The text a PDF carries for copy-and-paste. Scanned PDFs have none."""
    pdf = pdfium.PdfDocument(pdf_path)
    return "\n".join(page.get_textpage().get_text_range() for page in pdf)


def _amounts(text: str, pattern: re.Pattern) -> list[Decimal]:
    return [Decimal(match.replace(",", "")) for match in pattern.findall(text)]


def missing_amounts(pdf_path: Path, parsed_text: str) -> list[Decimal] | None:
    """Amounts in the text layer that the parsed text lacks, in page order. None means no text layer to check against."""
    layer = text_layer(pdf_path)
    if not layer.strip():
        return None
    seen = set(_amounts(parsed_text, NUMBER))
    return [amount for amount in _amounts(layer, MONEY) if amount not in seen]


if __name__ == "__main__":
    from .clean import clean
    from .fetch import fetch_pdf
    from .parse import parse_page
    from .render import render

    kind, order_id = sys.argv[1], sys.argv[2]
    pdf = fetch_pdf(kind, order_id)
    parsed = "\n\n".join(clean(parse_page(page)) for page in render(pdf))
    layer_amounts = _amounts(text_layer(pdf), MONEY)
    missing = missing_amounts(pdf, parsed)
    print(f"{kind} {order_id}: {len(layer_amounts)} amounts in the text layer")
    if missing is None:
        print("  no text layer: check skipped")
    elif missing:
        print(f"  MISSING from parsed text: {', '.join(f'${a}' for a in missing)}")
    else:
        print("  all found in the parsed text")
