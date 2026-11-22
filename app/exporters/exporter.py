import json
from pathlib import Path
from typing import Any

import pandas as pd


def export_result(result: dict[str, Any], output_format: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if output_format == "json":
        destination.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        return destination

    tables = result.get("tables") or []
    primary = tables[0] if tables else {"headers": [], "rows": []}
    rows = primary.get("rows", [])
    frame = pd.DataFrame(rows)
    if output_format == "csv":
        # CSV is flat by nature. Export the primary detected table; full nested data remains in the UI result.
        if frame.empty and primary.get("headers"):
            frame = pd.DataFrame(columns=primary["headers"])
        frame.to_csv(destination, index=False, encoding="utf-8-sig")
        return destination

    if output_format == "xlsx":
        with pd.ExcelWriter(destination, engine="openpyxl") as writer:
            summary = pd.DataFrame(
                [{"field": key, "value": value} for key, value in result.get("extracted_fields", {}).items()]
            )
            summary.to_excel(writer, sheet_name="Summary", index=False)
            if frame.empty and primary.get("headers"):
                frame = pd.DataFrame(columns=primary["headers"])
            frame.to_excel(writer, sheet_name=(primary.get("name") or "Table")[:31], index=False)
            pages = pd.DataFrame(result.get("pages", []))
            if not pages.empty:
                pages.drop(columns=["text_preview"], errors="ignore").to_excel(writer, sheet_name="Pages", index=False)
        return destination

    raise ValueError(f"Unsupported output format: {output_format}")
