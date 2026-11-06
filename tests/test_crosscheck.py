from decimal import Decimal

import pypdfium2 as pdfium

from three_way_match import crosscheck


def test_finds_amount_the_parser_dropped(monkeypatch):
    monkeypatch.setattr(crosscheck, "text_layer", lambda _: "Chai $18.00 2 $36.00\nTotal: $1,374.60")
    parsed = "Chai & \\$18.00 & 2 & \\$36.00\\\\\n\\thead{Total:}"
    assert crosscheck.missing_amounts(None, parsed) == [Decimal("1374.60")]


def test_amounts_match_even_when_written_differently(monkeypatch):
    monkeypatch.setattr(crosscheck, "text_layer", lambda _: "Total: $1,813.00")
    assert crosscheck.missing_amounts(None, "Total Price:1813.0") == []


def test_no_text_layer_skips_the_check(tmp_path):
    pdf = pdfium.PdfDocument.new()
    pdf.new_page(612, 792)
    path = tmp_path / "scan.pdf"
    pdf.save(path)
    assert crosscheck.missing_amounts(path, "anything") is None


def test_bare_decimals_on_receipts_are_checked(monkeypatch):
    monkeypatch.setattr(crosscheck, "text_layer", lambda _: "Order Date: 2016-07-08\nUnit Price: 7.7\nTotal: 77.0")
    assert crosscheck.missing_amounts(None, "Unit Price: 7.7") == [Decimal("77.0")]
