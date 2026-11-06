"""The reading pipeline: fetch -> render -> parse -> clean -> extract, for one document or a whole order."""

import sys
import time
from collections.abc import Callable
from pathlib import Path

from .clean import clean
from .extract import extract
from .fetch import fetch_pdf
from .parse import parse_page
from .render import render
from .schemas import Document, DocType

EXTRACTED_DIR = Path("data/extracted")
Log = Callable[[str], None]


def _quiet(_: str) -> None:
    pass


def read_document(doc_type: DocType, order_id: str, log: Log = _quiet, cache_dir: Path = EXTRACTED_DIR) -> Document | None:
    """Return the order's document of this type, or None if the source has none. The final Document is cached."""
    start = time.monotonic()
    pdf = fetch_pdf(doc_type, order_id)
    if pdf is None:
        log(f"{doc_type}: no document for order {order_id}")
        return None
    log(f"{doc_type}: fetched {pdf} ({time.monotonic() - start:.1f} s)")

    cached = cache_dir / f"{pdf.stem}.json"
    if cached.exists():
        log(f"{doc_type}: using cached extraction {cached}")
        return Document.model_validate_json(cached.read_text())

    pages = render(pdf)
    log(f"{doc_type}: rendered {len(pages)} page(s) ({time.monotonic() - start:.1f} s)")
    text = "\n\n".join(clean(parse_page(page)) for page in pages)
    log(f"{doc_type}: parsed and cleaned {len(text)} characters ({time.monotonic() - start:.1f} s)")
    document = extract(text, doc_type)
    log(f"{doc_type}: extracted {len(document.lines)} line(s) ({time.monotonic() - start:.1f} s)")

    cache_dir.mkdir(parents=True, exist_ok=True)
    cached.write_text(document.model_dump_json())
    return document


def read_order(order_id: str, log: Log = _quiet) -> dict[DocType, Document | None]:
    """Read the purchase order, receipt and invoice for one order."""
    return {doc_type: read_document(doc_type, order_id, log) for doc_type in DocType}


if __name__ == "__main__":
    for doc_type, document in read_order(sys.argv[1], log=print).items():
        if document is None:
            print(f"\n{doc_type}: none")
            continue
        print(f"\n{doc_type}: order {document.order_id}, date {document.doc_date}, party {document.party}, total {document.total}")
        for line in document.lines:
            print(f"  {line.product:<36} qty {line.quantity:>4}  price {line.unit_price}")
