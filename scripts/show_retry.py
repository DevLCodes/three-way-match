"""Step 01.6 demo: force a bad first answer, then let the real model fix it from the validation error."""

import sys
from pathlib import Path

from three_way_match import extract as ex
from three_way_match.clean import clean
from three_way_match.schemas import DocType

BAD_FIRST_REPLY = '{"order_id": "10250", "lines": [{"product": "Chai", "quantity": "ten", "unit_price": "$18"}]}'
calls = 0


def chat(messages):
    global calls
    calls += 1
    print(f"--- call {calls}: {len(messages)} message(s) sent ---")
    if calls == 1:
        reply = BAD_FIRST_REPLY
        print(f"reply (forced, not from the model): {reply}")
    else:
        print(f"last message: {messages[-1]['content'][:400]}")
        reply = ex.chat(messages)
        print(f"reply (real model): {reply}")
    return reply


document = ex.extract(clean(Path(sys.argv[1]).read_text()), DocType.INVOICE, chat=chat)
print(f"--- accepted after {calls} calls: {len(document.lines)} lines, total {document.total} ---")
