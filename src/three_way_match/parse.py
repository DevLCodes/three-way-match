"""Read a page image with NVIDIA Nemotron 3.5 Parse, which returns the page's text with layout tags."""

import os
import sys
from pathlib import Path

import httpx

PARSE_URL = "https://ai.api.nvidia.com/v1/retrieval/nvidia/nemotron-3.5-parse/parse"
PARSED_DIR = Path("data/parsed")


def parse_page(image: Path, cache_dir: Path = PARSED_DIR, client: httpx.Client | None = None) -> str:
    """Return the parser's raw output for one page image. Each page is sent once; the result is kept on disk."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached = cache_dir / f"{image.stem}.txt"
    if cached.exists():
        return cached.read_text()
    client = client or httpx.Client(timeout=120)
    response = client.post(
        PARSE_URL,
        headers={"Authorization": f"Bearer {os.environ['NVIDIA_API_KEY']}", "Accept": "application/json"},
        files={
            "document": (image.name, image.read_bytes(), "image/png"),
            "options": (None, '{"decoding":{"max_output_tokens":4096}}', "application/json"),
        },
    )
    response.raise_for_status()
    content = response.json()["content"]
    cached.write_text(content)
    return content


if __name__ == "__main__":
    print(parse_page(Path(sys.argv[1])))
