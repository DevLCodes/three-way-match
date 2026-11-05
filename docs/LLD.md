# Three-Way Match Agent: Low-Level Design

High-level design: [Three-Way Match Agent](https://devlcodes.github.io/agentic-ai-notebook/system-design/three-way-match.html). This document grows one step at a time and describes only code that exists on `main`.

## Modules

| Module | Responsibility | Added in step |
|---|---|---|
| `src/three_way_match/__init__.py` | Package marker | [00.1](steps/00.1-create-repo.md) |
| [`src/three_way_match/fetch.py`](../src/three_way_match/fetch.py) | Download source PDFs from Hugging Face, cached on disk | [01.1](steps/01.1-fetch-pdf.md) |
| [`src/three_way_match/render.py`](../src/three_way_match/render.py) | Render PDF pages to PNG within the parser's size limit | [01.2](steps/01.2-render-pages.md) |

## Data model

## Document reading pipeline

```python
def fetch_pdf(kind: str, order_id: str, client: httpx.Client | None = None, pdf_dir: Path = Path("data/pdfs")) -> Path | None
def render(pdf_path: Path, out_dir: Path = Path("data/pages")) -> list[Path]
```

| Step | Detail | Cache |
|---|---|---|
| Fetch ([01.1](steps/01.1-fetch-pdf.md)) | `GET https://huggingface.co/datasets/AyoubChLin/<repo>/resolve/main/<file>`, redirects followed, 60 s timeout. `kind` is `purchase_order` (`northwind_PurchaseOrders`, `purchase_orders_<id>.pdf`), `receipt` (`northwind_Shipping_orders`, `order_<id>.pdf`) or `invoice` (`northwind_invocies`, `invoice_<id>.pdf`). `404` returns `None`; other errors raise | `data/pdfs/`, checked before any request |
| Render ([01.2](steps/01.2-render-pages.md)) | pypdfium2; scale = min(1664 / width, 2048 / height) with page size in points; RGB PNG; `thumbnail((1664, 2048))` corrects pdfium's round-up overshoot. Output `<stem>_p<n>.png` | `data/pages/`, per page |

## Matching rules

## Workflow state machine

## Job queue and worker

## HTTP API

## Telemetry

## Deployment
