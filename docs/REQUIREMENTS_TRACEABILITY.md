# Requirements Traceability Matrix

| Requirement | Implementation | Verification |
|---|---|---|
| Local FastAPI server | `app/main.py`, `app/api/routes.py`, `run.bat` | API health and end-to-end API tests |
| Local HTML/JS UI | `frontend/index.html`, `style.css`, `app.js` | Static root route and manual browser acceptance |
| PDF + image inputs | `app/ingestion/` | PDF renderer and image document-service tests |
| Multi-page PDFs | `iter_pdf_pages()` generator | `test_pdf_processor.py`, multipage service test |
| Configurable 150–300 DPI | Upload endpoint and PDF renderer | API validation; manual PDF acceptance |
| CPU-only inference | Cactus Mirage adapter and bounded thread setting | Real target-machine smoke test |
| Model loaded once | `JobManager._get_engine()` singleton | Code inspection; real run acceptance |
| No external inference services | No network client/API configured; local Mirage adapter | Offline target-machine acceptance |
| Telemetry disabled | Set before Cactus import | Code inspection and target-machine check |
| Full-page OCR | `CactusMirageEngine.describe()` | `scripts/smoke_test.py` |
| Dense table crop | `find_table_crop()` | Table geometry tests and manual accuracy evaluation |
| Tall-table slicing | `_table_chunks()` | Review warning; manual accuracy evaluation |
| Document-specific schemas | `document_schemas.py` | Schema map inspection and service tests |
| Structured form extraction | `extract_document_fields()` via Mirage `extract()` | Real Mirage smoke/integration test required |
| Strict result contract | Pydantic `DocumentResult` | Document service tests |
| JSON export | `exporter.py` | `test_exporter.py` |
| CSV export | `exporter.py` | `test_exporter.py` |
| Excel export | `exporter.py` | `test_exporter.py` |
| Preview and download | UI result tabs + download endpoint | API end-to-end test; manual browser acceptance |
| 10–50 page CPU memory discipline | Single background worker, page iterator, pixel caps | Multipage tests; benchmark on target PC |
| Future WASM portability | `VisionEngine` interface and architecture docs | Design boundary documented; WASM not implemented in v1 |

## Acceptance status

- Automated application tests: run in this build environment using `FakeMirageEngine`.
- Actual Cactus Mirage model initialization and OCR: not executable in this build environment because the native Cactus package/runtime and model cache are not installed here. The included Windows smoke test is the required target-machine verification.
- Offline inference: designed for with `HF_HUB_OFFLINE=1`; must be confirmed on the target Windows PC after the initial model download.
