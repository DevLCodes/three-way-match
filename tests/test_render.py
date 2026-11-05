import pypdfium2 as pdfium
from PIL import Image

from three_way_match.render import MAX_HEIGHT, MAX_WIDTH, render


def make_pdf(path, sizes):
    pdf = pdfium.PdfDocument.new()
    for width, height in sizes:
        pdf.new_page(width, height)
    pdf.save(path)


def test_one_png_per_page_within_size_limit(tmp_path):
    pdf = tmp_path / "doc.pdf"
    make_pdf(pdf, [(612, 792), (792, 612)])  # US Letter portrait, then landscape
    pages = render(pdf, tmp_path / "pages")
    assert [p.name for p in pages] == ["doc_p1.png", "doc_p2.png"]
    for page in pages:
        with Image.open(page) as img:
            width, height = img.size
            assert width <= MAX_WIDTH and height <= MAX_HEIGHT
            assert width >= MAX_WIDTH - 1 or height >= MAX_HEIGHT - 1  # scaled up until one side reaches the limit


def test_existing_image_is_not_redrawn(tmp_path):
    pdf = tmp_path / "doc.pdf"
    make_pdf(pdf, [(612, 792)])
    first = render(pdf, tmp_path)[0]
    first.write_bytes(b"kept")
    assert render(pdf, tmp_path)[0].read_bytes() == b"kept"
