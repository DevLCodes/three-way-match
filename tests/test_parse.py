import httpx

from three_way_match.parse import PARSE_URL, parse_page


def test_sends_image_once_and_caches_content(tmp_path, monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "test-key")
    image = tmp_path / "invoice_1_p1.png"
    image.write_bytes(b"png-bytes")
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"content": "<class_Title>INVOICE"})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    assert parse_page(image, tmp_path / "parsed", client) == "<class_Title>INVOICE"
    assert parse_page(image, tmp_path / "parsed", client) == "<class_Title>INVOICE"
    assert len(requests) == 1
    assert str(requests[0].url) == PARSE_URL
    assert requests[0].headers["Authorization"] == "Bearer test-key"
    assert b"png-bytes" in requests[0].content
    assert (tmp_path / "parsed" / "invoice_1_p1.txt").read_text() == "<class_Title>INVOICE"
