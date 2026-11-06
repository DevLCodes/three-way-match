import pytest

from three_way_match.completeness import item_rows
from three_way_match.extract import IncompleteExtraction, extract
from three_way_match.schemas import DocType

INVOICE = r"""\begin{tabular}{cccc}
\thead{Product Name} & \thead{Unit Price} & \thead{Quantity} & \thead{Total Price}\\
Chai & \$18.00 & 2 & \$36.00\\
Tofu & \$23.25 & 1 & \$23.25\\
\mbox{} & \mbox{} & **Total:** & \$59.25\\
\end{tabular}"""

TWO_PAGE_PO = r"""\begin{tabular}{ccc}
\thead{Order ID} & \thead{Order Date} & \thead{Customer Name}\\
11077 & 1998-05-06 & Rattlesnake Canyon Grocery\\
\end{tabular}

\begin{tabular}{cccc}
\thead{Product ID:} & \thead{Product:} & \thead{Quantity:} & \thead{Unit Price:}\\
2 & Chang & 24 & 19\\
3 & Aniseed Syrup & 4 & 10\\
\end{tabular}

_Page 1_

\begin{tabular}{cccc}
7 & Uncle Bob's Organic Dried Pears & 1 & 30\\
\end{tabular}"""


def test_counts_items_not_headers_or_totals():
    assert item_rows(INVOICE) == 2


def test_continued_table_counts_and_order_table_does_not():
    assert item_rows(TWO_PAGE_PO) == 3


def test_text_without_tables_is_not_counted():
    assert item_rows("Product: Chai\nQuantity: 10") is None


def lines_json(n):
    lines = ",".join(f'{{"product": "P{i}", "quantity": 1, "unit_price": 1}}' for i in range(n))
    return f'{{"order_id": "1", "lines": [{lines}], "total": null}}'


def test_missing_lines_are_sent_back_and_retried():
    sent = []
    replies = [lines_json(2), lines_json(3)]

    def chat(messages):
        sent.append(messages[-1]["content"])
        return replies[len(sent) - 1]

    assert len(extract(TWO_PAGE_PO, DocType.PO, chat=chat).lines) == 3
    assert "You returned 2 lines, but the document's tables have 3 item rows" in sent[1]


def test_still_incomplete_after_retry_raises():
    with pytest.raises(IncompleteExtraction):
        extract(TWO_PAGE_PO, DocType.PO, chat=lambda m: lines_json(2))
