# Local Document Intelligence

A Windows-friendly, CPU-first document and table extraction application using **Cactus Mirage** locally. It accepts PDFs and images, processes PDF pages sequentially, extracts OCR regions and schema-guided document fields, reconstructs a best-effort table, previews the result, and exports JSON, CSV or Excel.

> **Important accuracy note:** Mirage is a compact on-device vision model, not a guaranteed accounting-grade OCR engine. The application preserves warnings and always marks the result for human review. Dense/low-quality scans, merged cells, multi-line descriptions, rotated pages and handwriting may need manual correction.

## Requirements

- Windows 11 x64
- Python **3.11** (recommended; install the 64-bit build)
- CPU; no CUDA or GPU is required by this project
- 8 GB RAM minimum recommended; 16 GB is more comfortable for large PDFs
- Internet for the initial package/model download only; after model files are cached, inference can be run offline

The actual inference speed depends on your CPU. A 10–50 page document is processed one page at a time. The application deliberately uses a single worker so it does not load multiple model instances or render all pages into memory at once.

## Quick start (Windows)

1. Extract the ZIP to a writable folder, e.g. `C:\Projects\document-intelligence`.
2. Install 64-bit Python 3.11 and ensure the Python Launcher (`py`) is available.
3. Double-click `install.bat`. It creates `.venv` and installs pinned dependencies.
4. While online, double-click `scripts\download_model.bat`. This initializes Mirage and lets Cactus download/cache its runtime and weights.
5. Run `scripts\smoke_test.py` from the project folder to inspect the real Mirage OCR output:

   ```powershell
   .venv\Scripts\python.exe scripts\smoke_test.py
   ```

6. Double-click `run.bat` and open **http://127.0.0.1:8000**.
7. Upload a PDF/image, select a document type and output format, and start extraction.

API documentation is available locally at `http://127.0.0.1:8000/api/docs`.

## Offline verification

After the first successful model initialization:

1. Close the application.
2. Disconnect Wi-Fi/Ethernet (or use Windows Firewall to block outbound access for the Python process).
3. Run `run.bat` and process `samples/sample_invoice.png`.
4. If it works without a network connection, the cached model inference path is offline.

Do not run the first-time `download_model.py` step offline. It is expected to download the engine/model cache if absent. The app sets `HF_HUB_OFFLINE=1` and `DO_NOT_TRACK=1` before model initialization, does not call external OCR/LLM services or cloud endpoints, and binds to `127.0.0.1` only. If model files are missing, it should fail locally rather than download them at inference time. Cactus telemetry is disabled via `CACTUS_TELEMETRY=0` before importing the package.

## Demo mode

`run_demo.bat` starts a deterministic fake inference adapter. It is useful to verify upload, job polling, preview and export plumbing before downloading Mirage. **Demo mode does not run OCR and must not be used to evaluate extraction accuracy.**

## Document types

- Invoice / Receipt: vendor/customer/invoice scalar fields and a best-effort `line_items` table.
- Bank Statement: bank/account/period scalar fields and a best-effort `transactions` table.
- Medical Form / Prescription: patient/provider/date/diagnosis scalar fields and a best-effort `prescriptions` table.
- General Table / Report: title/organization/date/summary and generic `rows` table.

Mirage's `extract()` API fills the document-type-specific scalar form. Table rows are reconstructed from OCR text-region bounding boxes using deterministic geometry. This is intentional: Mirage's documented form extraction is for typed fields and box references; the application does not pretend that it natively guarantees arbitrary-length table arrays.

## Output formats

- JSON preserves extracted fields, page summaries, warnings and table rows.
- CSV exports the primary table only because CSV cannot represent nested document metadata or multiple worksheets.
- Excel creates `Summary`, the primary table sheet, and (when available) a `Pages` sheet.

## Project layout

```text
app/
  api/                 FastAPI upload, job, result and download endpoints
  core/                Configuration and enums
  ingestion/           PDF page renderer and image loader
  preprocessing/       Image normalization, OCR region parsing, table geometry
  inference/           Portable engine interface and Cactus Mirage adapter
  extraction/          Document-type forms and multi-pass extraction orchestration
  validation/          Pydantic result contract
  exporters/           JSON, CSV and XLSX exporters
  services/            Sequential document processing and background job manager
frontend/              Local HTML, CSS and JavaScript UI (no CDN)
samples/                Synthetic invoice image and multipage PDF
scripts/                Model cache initialization and real Mirage smoke test
tests/                  Unit and API tests (no model download required)
docs/                   Architecture, privacy and test notes
```

## Architecture and processing flow

1. Browser uploads a supported file to the loopback FastAPI server.
2. API checks extension, file signature, upload size, DPI and PDF page limit.
3. A single background worker processes one page at a time.
4. PDFs are rendered through `pypdfium2`; image files are EXIF-corrected and normalized with Pillow.
5. Mirage `describe()` returns OCR text regions and bounding boxes. The application groups nearby text boxes into visual lines.
6. A repeated multi-column text region is cropped and sent through a second Mirage OCR pass; tall regions are split into overlapping horizontal strips.
7. Mirage `extract()` is called with a document-specific form for scalar metadata.
8. OCR rows from each page are combined, exact duplicate rows are removed, and the result is validated with Pydantic.
9. The selected export is written locally and served back to the browser.

## Accuracy / design limitations to know

- Bounding boxes are normalized to Mirage's documented 0–1000 coordinate system. The OCR parser tolerates a few common result envelope shapes, but the exact structure returned by your installed runtime is printed by the smoke test. If a new Cactus release changes the shape, update `app/preprocessing/text_regions.py`.
- Current table reconstruction is geometry-based, not a full grid-line/table-structure model. It is a practical baseline and should be evaluated on representative scans before production use.
- Cross-page table continuation is merged by detected column names and row order. When a later page appears to omit the header, column positions are aligned to the first page and a warning is added. Complex repeated headers, subtotals and split rows may need specialized logic.
- Medical content is sensitive. This application is not a medical device and does not verify clinical correctness. Keep the machine secured and review all output.
- The application currently stores job results in process memory and export files under `temp/exports`; expired job artifacts are cleaned when a new job is submitted. Close the server and remove `temp/` if you want to clear local artifacts immediately.
- This is a single-user local application, not a hardened multi-user deployment. Do not expose it to a LAN or public internet.

## Run tests

```powershell
.venv\Scripts\python.exe -m pytest -v
```

Tests use a fake inference engine and do not download or require Cactus model weights. Run `scripts/smoke_test.py` separately to verify actual Mirage installation and inference.

## Troubleshooting

- **`No module named cactus`:** activate the project venv and rerun `install.bat`.
- **Model initialization/download error:** connect to the internet, run `scripts\download_model.bat`, and confirm the Cactus model cache can be written by your Windows user.
- **C++ runtime/DLL load error:** install the latest Microsoft Visual C++ Redistributable (x64), restart PowerShell, and rerun the smoke test.
- **No OCR boxes:** inspect the raw smoke-test output, test a sharper/straight image, increase PDF DPI, and check whether the document's script is supported. Mirage's text reader is documented for Latin script.
- **Slow processing:** lower DPI to 175–200, use fewer page crops, and close other memory-heavy applications. Do not increase worker count on a CPU-only machine.
- **PDF render memory:** the app caps the rendered pixel count per page; it does not keep all page images in memory.

## Security and privacy

- Server binds to `127.0.0.1` only.
- No cloud OCR/LLM endpoints are configured.
- Cactus telemetry is disabled before import.
- Uploaded files are stored under `temp/` with random names and deleted after processing.
- Export files remain locally available until job retention cleanup or manual deletion of `temp/`.
- No third-party frontend scripts, fonts, analytics or CDN assets are loaded.

See `docs/ARCHITECTURE.md`, `docs/PRIVACY_AND_THREAT_MODEL.md`, and `docs/TEST_REPORT.md`.

## CPU tuning

The Cactus adapter calls `cactus.set_threads()` when that function is exposed by the installed SDK. The default is two threads (`CACTUS_THREADS=2` in `.env.example`). Start with 1–2 threads on a desktop and benchmark your own machine; more threads are not always faster when the CPU is busy. The model adapter is loaded once and inference calls are serialized.
