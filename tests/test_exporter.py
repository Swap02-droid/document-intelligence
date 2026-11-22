import json
from pathlib import Path

import pandas as pd
from app.exporters.exporter import export_result


SAMPLE = {
    "document_type": "general_table_report",
    "document_name": "sample.png",
    "page_count": 1,
    "extracted_fields": {"report_title": "Sample", "report_date": None},
    "tables": [{"name": "rows", "headers": ["Name", "Value"], "rows": [{"Name": "A", "Value": "10"}], "page_numbers": [1]}],
    "pages": [], "warnings": [], "review_required": True,
    "engine": "Cactus Mirage", "inference_mode": "local", "metrics": {},
}


def test_json_export(tmp_path: Path):
    path = export_result(SAMPLE, "json", tmp_path / "result.json")
    assert json.loads(path.read_text(encoding="utf-8"))["document_name"] == "sample.png"


def test_csv_export(tmp_path: Path):
    path = export_result(SAMPLE, "csv", tmp_path / "result.csv")
    frame = pd.read_csv(path)
    assert frame.loc[0, "Name"] == "A"


def test_xlsx_export(tmp_path: Path):
    path = export_result(SAMPLE, "xlsx", tmp_path / "result.xlsx")
    workbook = pd.ExcelFile(path)
    assert "Summary" in workbook.sheet_names
    assert "rows" in workbook.sheet_names
