"""Step 01.9 demo: count item rows in every parsed document, then re-extract PO 11077 and watch the retry."""

from pathlib import Path

from three_way_match import extract as ex
from three_way_match.clean import clean
from three_way_match.completeness import item_rows
from three_way_match.schemas import Document, DocType


def parsed_text(stem: str) -> str:
    return "\n\n".join(clean(p.read_text()) for p in sorted(Path("data/parsed").glob(f"{stem}_p*.txt")))


print("item rows in the parsed text vs lines in the cached extraction:")
for stem in ["purchase_orders_10250", "order_10250", "invoice_10250", "purchase_orders_11077", "invoice_11077"]:
    cached = Path(f"data/extracted/{stem}.json")
    lines = len(Document.model_validate_json(cached.read_text()).lines) if cached.exists() else "-"
    print(f"  {stem:<24} rows {str(item_rows(parsed_text(stem))):>4}   extracted {lines:>3}")

print("\nre-extracting purchase_orders_11077:")
calls = 0


def chat(messages):
    global calls
    calls += 1
    reply = ex.chat(messages)
    if calls > 1:
        print(f"  feedback sent: {messages[-1]['content']}")
    print(f"  call {calls}: reply has {reply.count('product')} lines")
    return reply


document = ex.extract(parsed_text("purchase_orders_11077"), DocType.PO, chat=chat)
print(f"  accepted: {len(document.lines)} lines; last: {document.lines[-1].product}")
Path("data/extracted/purchase_orders_11077.json").write_text(document.model_dump_json())

print("\nforcing the earlier 14-line answer as call 1, to show the retry:")
first_14 = document.model_copy(update={"lines": document.lines[:14]}).model_dump_json()
calls = 0


def chat_forced(messages):
    global calls
    calls += 1
    if calls == 1:
        print("  call 1 (forced, not from the model): reply has 14 lines")
        return first_14
    print(f"  feedback sent: {messages[-1]['content']}")
    reply = ex.chat(messages)
    print(f"  call {calls} (real model): reply has {reply.count('product')} lines")
    return reply


retried = ex.extract(parsed_text("purchase_orders_11077"), DocType.PO, chat=chat_forced)
print(f"  accepted: {len(retried.lines)} lines; last: {retried.lines[-1].product}")
