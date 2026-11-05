"""Turn each PDF page into a PNG image, because the parser reads images, not PDFs."""

import sys
from pathlib import Path

import pypdfium2 as pdfium

PAGE_DIR = Path("data/pages")
# Nemotron Parse's recommended maximum image size, in pixels.
MAX_WIDTH, MAX_HEIGHT = 1664, 2048


def render(pdf_path: Path, out_dir: Path = PAGE_DIR) -> list[Path]:
    """Render every page to <stem>_p<n>.png, scaled to fit MAX_WIDTH x MAX_HEIGHT. Existing images are reused."""
    out_dir.mkdir(parents=True, exist_ok=True)
    pages = []
    pdf = pdfium.PdfDocument(pdf_path)
    for i, page in enumerate(pdf):
        path = out_dir / f"{pdf_path.stem}_p{i + 1}.png"
        if not path.exists():
            width, height = page.get_size()  # in PDF points: 1 point = 1/72 inch
            scale = min(MAX_WIDTH / width, MAX_HEIGHT / height)
            image = page.render(scale=scale).to_pil().convert("RGB")
            # pdfium rounds pixel sizes up, which can land 1 px over the limit; shrink back inside it.
            image.thumbnail((MAX_WIDTH, MAX_HEIGHT))
            image.save(path)
        pages.append(path)
    return pages


if __name__ == "__main__":
    from PIL import Image

    pdf_path = Path(sys.argv[1])
    pdf = pdfium.PdfDocument(pdf_path)
    print(f"{pdf_path}: {len(pdf)} page(s)")
    for i, image in enumerate(render(pdf_path)):
        width, height = pdf[i].get_size()
        scale = min(MAX_WIDTH / width, MAX_HEIGHT / height)
        with Image.open(image) as img:
            print(f"  page {i + 1}: {width:.0f} x {height:.0f} pt, scale {scale:.2f} -> {image} {img.size[0]} x {img.size[1]} px")
