"""Count the item rows in the parsed tables, so extraction can't silently drop lines (e.g. a table's second page)."""

import re

TABLE = re.compile(r"\\begin\{tabular\}.*?\\end\{tabular\}", re.S)
ITEM_HEADER = re.compile(r"product|quantity|unit price", re.I)


def item_rows(text: str) -> int | None:
    """Data rows in item tables. A table is an item table if its header names products, quantities or prices,
    or if it has no header and follows an item table (the same table continued on the next page).
    Header rows and total rows are not items. None means the text has no item table to count."""
    rows, in_items = 0, False
    for table in TABLE.findall(text):
        lines = [l.strip() for l in table.splitlines()[1:-1] if l.strip().endswith("\\\\")]
        header = next((l for l in lines if "\\thead" in l), None)
        if header is not None:
            in_items = bool(ITEM_HEADER.search(header))
        if not in_items:
            continue
        rows += sum(1 for l in lines if "\\thead" not in l and "total" not in l.lower() and "\\mbox{}" not in l)
    return rows if in_items or rows else None
