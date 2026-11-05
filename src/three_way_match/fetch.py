"""Download source PDFs from the Hugging Face Northwind datasets, which stand in for an ERP."""

import sys
from pathlib import Path

import httpx

HF = "https://huggingface.co/datasets/AyoubChLin"
PDF_DIR = Path("data/pdfs")

# Document kind -> (dataset repo, file name pattern).
SOURCES = {
    "purchase_order": ("northwind_PurchaseOrders", "purchase_orders_{}.pdf"),
    "receipt": ("northwind_Shipping_orders", "order_{}.pdf"),
    "invoice": ("northwind_invocies", "invoice_{}.pdf"),
}


def fetch_pdf(kind: str, order_id: str, client: httpx.Client | None = None, pdf_dir: Path = PDF_DIR) -> Path | None:
    """Return the local path of the PDF, downloading it once. None means the order has no such document."""
    repo, pattern = SOURCES[kind]
    path = pdf_dir / pattern.format(order_id)
    if path.exists():
        return path
    client = client or httpx.Client(follow_redirects=True, timeout=60)
    response = client.get(f"{HF}/{repo}/resolve/main/{path.name}")
    if response.status_code == 404:
        return None
    response.raise_for_status()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(response.content)
    return path


if __name__ == "__main__":
    kind, order_id = sys.argv[1], sys.argv[2]
    path = fetch_pdf(kind, order_id)
    if path is None:
        print(f"{kind} {order_id}: not found (404)")
    else:
        print(f"{kind} {order_id}: {path} ({path.stat().st_size:,} bytes), header {path.read_bytes()[:5]!r}")
