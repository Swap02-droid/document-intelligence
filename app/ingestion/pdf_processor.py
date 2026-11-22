from pathlib import Path
from typing import Iterator

import pypdfium2 as pdfium
from PIL import Image


class PDFProcessingError(RuntimeError):
    pass


def pdf_page_count(path: Path) -> int:
    try:
        pdf = pdfium.PdfDocument(str(path))
        try:
            return len(pdf)
        finally:
            pdf.close()
    except Exception as exc:
        raise PDFProcessingError(f"Unable to open PDF: {exc}") from exc


def iter_pdf_pages(path: Path, dpi: int = 250, max_pixels: int = 18_000_000) -> Iterator[tuple[int, Image.Image]]:
    """Render one page at a time to bound peak memory use."""
    pdf = None
    try:
        pdf = pdfium.PdfDocument(str(path))
        scale = dpi / 72.0
        for page_index in range(len(pdf)):
            page = pdf[page_index]
            try:
                width_pt, height_pt = page.get_size()
                estimated_pixels = width_pt * scale * height_pt * scale
                page_scale = scale
                if estimated_pixels > max_pixels:
                    page_scale *= (max_pixels / estimated_pixels) ** 0.5
                bitmap = page.render(scale=page_scale, rotation=0)
                try:
                    image = bitmap.to_pil().convert("RGB")
                    yield page_index + 1, image
                finally:
                    bitmap.close()
            finally:
                page.close()
    except PDFProcessingError:
        raise
    except Exception as exc:
        raise PDFProcessingError(f"PDF rendering failed: {exc}") from exc
    finally:
        if pdf is not None:
            pdf.close()
