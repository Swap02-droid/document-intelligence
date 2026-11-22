from pathlib import Path
from time import perf_counter
from typing import Callable

from PIL import Image

from app.core.config import get_settings
from app.extraction.extractor import extract_page, extract_document_fields
from app.extraction.schemas.document_schemas import SCHEMAS
from app.ingestion.image_processor import load_image
from app.ingestion.pdf_processor import iter_pdf_pages, pdf_page_count
from app.validation.validator import validate_document


class DocumentServiceError(RuntimeError):
    pass


class DocumentService:
    def __init__(self, engine, progress: Callable[[int, int, str], None] | None = None):
        self.engine = engine
        self.progress = progress or (lambda current, total, message: None)
        self.settings = get_settings()

    def process(self, path: Path, document_type: str, dpi: int = 250) -> dict:
        started = perf_counter()
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            total_pages = pdf_page_count(path)
            if total_pages > self.settings.max_pdf_pages:
                raise DocumentServiceError(f"PDF has {total_pages} pages; limit is {self.settings.max_pdf_pages}.")
            page_iterator = iter_pdf_pages(path, dpi=dpi, max_pixels=self.settings.max_render_pixels)
        else:
            total_pages = 1
            page_iterator = iter([(1, load_image(path, self.settings.max_image_edge, self.settings.max_image_pixels))])

        schema = SCHEMAS[document_type]
        page_summaries = []
        table_rows: list[dict] = []
        merged_headers: list[str] = []
        fields: dict = {}
        warnings: list[str] = []
        total_regions = 0
        for page_number, image in page_iterator:
            self.progress(page_number - 1, total_pages, f"Analyzing page {page_number} of {total_pages}")
            try:
                page_data = extract_page(self.engine, image, document_type, page_number)
                total_regions += len(page_data["regions"])
                if not fields:
                    fields, field_warnings = extract_document_fields(self.engine, image, document_type)
                    warnings.extend(field_warnings)
                current_table = page_data["table"]
                if current_table.get("headers"):
                    current_headers = current_table["headers"]
                    current_rows = current_table.get("rows", [])
                    if not merged_headers:
                        merged_headers = current_headers
                        table_rows.extend(row for row in current_rows if row and any(str(v).strip() for v in row.values()))
                    elif [h.strip().lower() for h in current_headers] == [h.strip().lower() for h in merged_headers]:
                        # Repeated header on a continuation page: append only data rows.
                        table_rows.extend(row for row in current_rows if row and any(str(v).strip() for v in row.values()))
                    else:
                        # Some PDFs omit the table header on continuation pages. In that
                        # case the row parser may interpret the first data row as headers.
                        if len(current_headers) == len(merged_headers):
                            table_rows.append({merged_headers[i]: current_headers[i] for i in range(len(merged_headers))})
                            for row in current_rows:
                                values = list(row.values())
                                table_rows.append({merged_headers[i]: values[i] if i < len(values) else "" for i in range(len(merged_headers))})
                            warnings.append(f"Page {page_number}: no matching repeated table header was found; column positions were aligned to the first page. Review this page's rows.")
                        else:
                            warnings.append(f"Page {page_number}: table column count differs from the first page; this page's table was not merged automatically.")
                page_summaries.append({
                    "page_number": page_number,
                    "ocr_region_count": len(page_data["regions"]),
                    "text_preview": page_data["text_preview"],
                    "table_detected": page_data["table_detected"],
                    "warnings": page_data["warnings"],
                })
                warnings.extend(page_data["warnings"])
            finally:
                image.close()
            self.progress(page_number, total_pages, f"Completed page {page_number} of {total_pages}")

        if not page_summaries:
            raise DocumentServiceError("No pages could be processed.")
        if not merged_headers and table_rows:
            merged_headers = list(table_rows[0].keys())
        # Preserve every detected row: identical transactions/items can be legitimate.
        # Chunk-boundary duplicates are surfaced as review warnings instead of silently dropped.
        table_payload = {
            "name": schema.primary_table_name,
            "headers": merged_headers,
            "rows": table_rows,
            "page_numbers": [p["page_number"] for p in page_summaries if p["table_detected"]],
        }
        payload = {
            "document_type": document_type,
            "document_name": path.name,
            "page_count": total_pages,
            "extracted_fields": fields,
            "tables": [table_payload] if merged_headers or table_rows else [],
            "pages": page_summaries,
            "warnings": warnings,
            "review_required": True,
            "engine": "Cactus Mirage",
            "inference_mode": "local",
            "metrics": {
                "processing_seconds": round(perf_counter() - started, 3),
                "pages_processed": len(page_summaries),
                "ocr_regions": total_regions,
                "dpi": dpi if suffix == ".pdf" else None,
            },
        }
        return validate_document(payload)
