from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ExtractionSchema:
    document_type: str
    title: str
    keywords: tuple[str, ...]
    mirage_form: dict[str, Any]
    primary_table_name: str
    table_header_hints: tuple[str, ...]


SCHEMAS: dict[str, ExtractionSchema] = {
    "invoice_receipt": ExtractionSchema(
        document_type="invoice_receipt",
        title="Invoice / Receipt",
        keywords=("invoice number", "invoice date", "vendor", "supplier", "bill to", "subtotal", "tax", "total", "quantity", "description", "unit price", "amount"),
        mirage_form={
            "vendor_name": {"type": "string"},
            "invoice_number": {"type": "string"},
            "invoice_date": {"type": "string"},
            "due_date": {"type": "string"},
            "customer_name": {"type": "string"},
            "subtotal": {"type": "string"},
            "tax": {"type": "string"},
            "total_amount": {"type": "string"},
            "currency": {"type": "string"},
        },
        primary_table_name="line_items",
        table_header_hints=("description", "item", "product", "qty", "quantity", "unit price", "rate", "amount", "total"),
    ),
    "bank_statement": ExtractionSchema(
        document_type="bank_statement",
        title="Bank Statement",
        keywords=("account holder", "account number", "statement period", "opening balance", "closing balance", "transaction date", "description", "debit", "credit", "balance"),
        mirage_form={
            "bank_name": {"type": "string"},
            "account_holder": {"type": "string"},
            "account_number": {"type": "string"},
            "statement_period": {"type": "string"},
            "opening_balance": {"type": "string"},
            "closing_balance": {"type": "string"},
            "currency": {"type": "string"},
        },
        primary_table_name="transactions",
        table_header_hints=("date", "transaction date", "description", "particulars", "debit", "withdrawal", "credit", "deposit", "balance"),
    ),
    "medical_form_prescription": ExtractionSchema(
        document_type="medical_form_prescription",
        title="Medical Form / Prescription",
        keywords=("patient name", "patient id", "doctor", "provider", "date", "diagnosis", "medicine", "medication", "dosage", "frequency", "duration"),
        mirage_form={
            "patient_name": {"type": "string"},
            "patient_id": {"type": "string"},
            "provider_name": {"type": "string"},
            "document_date": {"type": "string"},
            "diagnosis": {"type": "string"},
            "notes": {"type": "string"},
        },
        primary_table_name="prescriptions",
        table_header_hints=("medicine", "medication", "drug", "dosage", "dose", "frequency", "duration", "quantity"),
    ),
    "general_table_report": ExtractionSchema(
        document_type="general_table_report",
        title="General Table / Report",
        keywords=("title", "report date", "headers", "table", "column", "row", "total", "summary"),
        mirage_form={
            "report_title": {"type": "string"},
            "organization": {"type": "string"},
            "report_date": {"type": "string"},
            "summary": {"type": "string"},
        },
        primary_table_name="rows",
        table_header_hints=(),
    ),
}
