from enum import Enum


class DocumentType(str, Enum):
    INVOICE = "invoice_receipt"
    BANK_STATEMENT = "bank_statement"
    MEDICAL = "medical_form_prescription"
    GENERAL_TABLE = "general_table_report"


class OutputFormat(str, Enum):
    JSON = "json"
    CSV = "csv"
    XLSX = "xlsx"


ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}
CONTENT_TYPES = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}
