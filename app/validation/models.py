from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class ExtractedTable(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: str
    headers: list[str] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)
    page_numbers: list[int] = Field(default_factory=list)


class PageResult(BaseModel):
    page_number: int
    ocr_region_count: int = 0
    text_preview: list[str] = Field(default_factory=list)
    table_detected: bool = False
    warnings: list[str] = Field(default_factory=list)


class DocumentResult(BaseModel):
    document_type: str
    document_name: str
    page_count: int
    extracted_fields: dict[str, Any] = Field(default_factory=dict)
    tables: list[ExtractedTable] = Field(default_factory=list)
    pages: list[PageResult] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    review_required: bool = True
    engine: str = "Cactus Mirage"
    inference_mode: str = "local"
    metrics: dict[str, Any] = Field(default_factory=dict)
