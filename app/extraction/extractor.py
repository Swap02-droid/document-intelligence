from typing import Any
from PIL import Image

from app.inference.base import VisionEngine
from app.preprocessing.text_regions import iter_text_regions
from app.preprocessing.table_layout import find_table_crop, rows_to_table
from app.preprocessing.image_normalizer import normalize_image, upscale_crop
from app.extraction.schemas.document_schemas import SCHEMAS


def _unwrap_form(result: dict[str, Any]) -> dict[str, Any]:
    value = result.get("form", result)
    return value if isinstance(value, dict) else {}


def _clean_scalar_fields(values: dict[str, Any], allowed: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key in allowed:
        value = values.get(key)
        # Mirage form answers can be wrapped as {"value": ..., "probabilities": ...}.
        if isinstance(value, dict) and "value" in value:
            value = value.get("value")
        if value is None or isinstance(value, (str, int, float, bool)):
            cleaned[key] = value.strip() if isinstance(value, str) else value
        else:
            cleaned[key] = str(value)
    return cleaned


def _table_chunks(crop: Image.Image, chunk_height: int = 1500, overlap: int = 120):
    if crop.height <= chunk_height:
        yield crop
        return
    top = 0
    while top < crop.height:
        bottom = min(crop.height, top + chunk_height)
        yield crop.crop((0, top, crop.width, bottom))
        if bottom == crop.height:
            break
        top = bottom - overlap


def extract_page(engine: VisionEngine, image: Image.Image, document_type: str, page_number: int) -> dict[str, Any]:
    schema = SCHEMAS[document_type]
    normalized = normalize_image(image)
    try:
        raw = engine.describe(normalized, keywords=list(schema.keywords))
        regions = list(iter_text_regions(raw))
        page_warnings: list[str] = []

        table_crop = find_table_crop(normalized, regions)
        table = {"headers": [], "rows": []}
        if table_crop is not None:
            crop_regions = []
            enhanced_crop = upscale_crop(table_crop)
            try:
                chunk_count = 0
                for chunk in _table_chunks(enhanced_crop):
                    chunk_count += 1
                    try:
                        crop_result = engine.describe(chunk, keywords=list(schema.keywords))
                        crop_regions.extend(iter_text_regions(crop_result))
                    finally:
                        if chunk is not enhanced_crop:
                            chunk.close()
                if chunk_count > 1:
                    page_warnings.append("Tall table was processed in overlapping image slices; inspect boundary rows for possible duplicates.")
            finally:
                enhanced_crop.close()
                table_crop.close()
            if crop_regions:
                table = rows_to_table(crop_regions, schema.table_header_hints)
            else:
                page_warnings.append("Table crop was identified, but the second OCR pass returned no text regions.")
        else:
            # If no dense region is found, retain a best-effort table from page OCR.
            table = rows_to_table(regions, schema.table_header_hints)
            if not table["rows"]:
                page_warnings.append("No repeated multi-column region was detected on this page.")

        text_preview = [region.text for region in sorted(regions, key=lambda r: (r.bbox[1], r.bbox[0]))[:80]]
        return {
            "page_number": page_number,
            "regions": regions,
            "table": table,
            "text_preview": text_preview,
            "warnings": page_warnings,
            "table_detected": bool(table.get("headers") and table.get("rows")),
        }
    finally:
        normalized.close()


def extract_document_fields(engine: VisionEngine, first_page: Image.Image, document_type: str) -> tuple[dict[str, Any], list[str]]:
    schema = SCHEMAS[document_type]
    warnings: list[str] = []
    normalized = normalize_image(first_page)
    try:
        result = engine.extract(normalized, schema.mirage_form)
        fields = _clean_scalar_fields(_unwrap_form(result), schema.mirage_form)
        return fields, warnings
    except Exception as exc:
        warnings.append(f"Mirage schema-form extraction was unavailable for this page: {exc}")
        return {key: None for key in schema.mirage_form}, warnings
    finally:
        normalized.close()
