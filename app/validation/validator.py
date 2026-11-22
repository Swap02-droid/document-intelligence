from typing import Any
from app.validation.models import DocumentResult


def validate_document(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate the outer result contract; never invent or silently repair extracted values."""
    validated = DocumentResult.model_validate(payload)
    result = validated.model_dump(mode="json")
    if not result["tables"]:
        result["warnings"].append("No table structure was confidently reconstructed. Review the page OCR and try a higher DPI or crop adjustment.")
    if not result["extracted_fields"] or all(v in (None, "", []) for v in result["extracted_fields"].values()):
        result["warnings"].append("No document-level fields were returned by Mirage. The OCR table/text preview is still available.")
    result["review_required"] = True
    return result
