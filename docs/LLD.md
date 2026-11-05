# Three-Way Match Agent: Low-Level Design

High-level design: [Three-Way Match Agent](https://devlcodes.github.io/agentic-ai-notebook/system-design/three-way-match.html). This document grows one step at a time and describes only code that exists on `main`.

## Modules

| Module | Responsibility | Added in step |
|---|---|---|
| `src/three_way_match/__init__.py` | Package marker | [00.1](steps/00.1-create-repo.md) |
| [`src/three_way_match/fetch.py`](../src/three_way_match/fetch.py) | Download source PDFs from Hugging Face, cached on disk | [01.1](steps/01.1-fetch-pdf.md) |

## Data model

## Document reading pipeline

```python
def fetch_pdf(kind: str, order_id: str, client: httpx.Client | None = None, pdf_dir: Path = Path("data/pdfs")) -> Path | None
```

| Step | Detail | Cache |
|---|---|---|
| Fetch ([01.1](steps/01.1-fetch-pdf.md)) | `GET https://huggingface.co/datasets/AyoubChLin/<repo>/resolve/main/<file>`, redirects followed, 60 s timeout. `kind` is `purchase_order` (`northwind_PurchaseOrders`, `purchase_orders_<id>.pdf`), `receipt` (`northwind_Shipping_orders`, `order_<id>.pdf`) or `invoice` (`northwind_invocies`, `invoice_<id>.pdf`). `404` returns `None`; other errors raise | `data/pdfs/`, checked before any request |

## Matching rules

## Workflow state machine

## Job queue and worker

## HTTP API

## Telemetry

## Deployment
