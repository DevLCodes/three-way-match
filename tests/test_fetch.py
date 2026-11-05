import httpx

from three_way_match.fetch import fetch_pdf


def client_for(status: int, body: bytes = b"") -> tuple[httpx.Client, list[str]]:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url))
        return httpx.Response(status, content=body)

    return httpx.Client(transport=httpx.MockTransport(handler)), calls


def test_downloads_once_then_uses_cache(tmp_path):
    client, calls = client_for(200, b"%PDF-1.4 fake")
    first = fetch_pdf("invoice", "10250", client, tmp_path)
    second = fetch_pdf("invoice", "10250", client, tmp_path)
    assert first == second == tmp_path / "invoice_10250.pdf"
    assert first.read_bytes() == b"%PDF-1.4 fake"
    assert calls == ["https://huggingface.co/datasets/AyoubChLin/northwind_invocies/resolve/main/invoice_10250.pdf"]


def test_missing_document_is_none(tmp_path):
    client, _ = client_for(404)
    assert fetch_pdf("receipt", "99999", client, tmp_path) is None
    assert not (tmp_path / "order_99999.pdf").exists()
