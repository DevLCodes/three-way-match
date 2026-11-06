from pathlib import Path

from three_way_match import read
from three_way_match.schemas import Document, DocType

DOC = Document(order_id="1", lines=[{"product": "Chai", "quantity": 1, "unit_price": 18}], total=18)


def fake_pipeline(monkeypatch, tmp_path, missing=()):
    calls = []
    monkeypatch.setattr(read, "fetch_pdf", lambda t, o: None if t in missing else tmp_path / f"{t}_{o}.pdf")
    monkeypatch.setattr(read, "render", lambda pdf: [Path(f"{pdf.stem}_p1.png"), Path(f"{pdf.stem}_p2.png")])
    monkeypatch.setattr(read, "parse_page", lambda page: f"<class_Text>{page.stem}")
    def fake_extract(text, doc_type):
        calls.append(text)
        return DOC
    monkeypatch.setattr(read, "extract", fake_extract)
    return calls


def test_pages_are_cleaned_joined_and_extracted_once(monkeypatch, tmp_path):
    calls = fake_pipeline(monkeypatch, tmp_path)
    cache = tmp_path / "extracted"
    assert read.read_document(DocType.INVOICE, "1", cache_dir=cache) == DOC
    assert calls == ["invoice_1_p1\n\ninvoice_1_p2"]
    assert read.read_document(DocType.INVOICE, "1", cache_dir=cache) == DOC
    assert len(calls) == 1  # second read came from the cache


def test_missing_document_is_none(monkeypatch, tmp_path):
    fake_pipeline(monkeypatch, tmp_path, missing={DocType.RECEIPT})
    assert read.read_document(DocType.RECEIPT, "1", cache_dir=tmp_path) is None
