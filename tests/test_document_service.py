from pathlib import Path
from PIL import Image

from app.inference.cactus_engine import FakeMirageEngine
from app.services.document_service import DocumentService


def test_document_service_processes_image_with_fake_engine(tmp_path: Path):
    image_path = tmp_path / "input.png"
    Image.new("RGB", (1000, 600), "white").save(image_path)
    result = DocumentService(FakeMirageEngine()).process(image_path, "general_table_report")
    assert result["page_count"] == 1
    assert result["inference_mode"] == "local"
    assert result["tables"]
    assert result["tables"][0]["headers"] == ["Date", "Description", "Amount"]
    assert result["tables"][0]["rows"][0]["Amount"] == "1250.00"
    assert result["review_required"] is True


def test_document_service_processes_multipage_pdf_sequentially_and_preserves_identical_rows():
    sample_pdf = Path(__file__).resolve().parents[1] / "samples" / "sample_multipage.pdf"
    result = DocumentService(FakeMirageEngine()).process(sample_pdf, "general_table_report", dpi=150)
    assert result["page_count"] == 2
    assert result["metrics"]["pages_processed"] == 2
    # Identical-looking rows may be genuine repeated transactions/items, so do not silently deduplicate.
    assert len(result["tables"][0]["rows"]) == 2
