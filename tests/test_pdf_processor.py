from pathlib import Path
from PIL import Image
from app.ingestion.pdf_processor import pdf_page_count, iter_pdf_pages


def test_pdf_pages_are_iterated_one_at_a_time(tmp_path: Path):
    first = Image.new("RGB", (240, 160), "white")
    second = Image.new("RGB", (240, 160), "#eeeeee")
    path = tmp_path / "two_pages.pdf"
    first.save(path, "PDF", save_all=True, append_images=[second], resolution=72.0)
    assert pdf_page_count(path) == 2
    pages = list(iter_pdf_pages(path, dpi=150, max_pixels=2_000_000))
    assert [number for number, _ in pages] == [1, 2]
    assert all(image.mode == "RGB" for _, image in pages)
    for _, image in pages:
        image.close()
