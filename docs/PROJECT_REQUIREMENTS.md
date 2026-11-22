# Project Requirements Baseline

## Goal

Build a 100% on-device document and table extraction application powered by Cactus Mirage (`cactus-compute`). It accepts PDFs or images containing complex layouts (multi-column tables, forms, receipts and statements) and converts them into structured data without sending document content to external cloud APIs.

## Functional requirements

1. **Input:** single PDF (including multi-page PDF) or PNG/JPG/JPEG/WEBP image.
2. **Document type selector:** Invoice / Receipt; Bank Statement; Medical Form / Prescription; General Table / Report.
3. **Output selector:** JSON, CSV or Excel.
4. **Preview:** show extracted fields and table data in the browser.
5. **Download:** generate the selected output locally.
6. **PDF ingestion:** render pages using pypdfium2 at a configurable 150–300 DPI, default 250 DPI.
7. **Image ingestion:** correct EXIF orientation, convert to RGB and apply conservative normalization.
8. **Multi-pass OCR:** inspect the full page, locate dense multi-column text regions, crop them, upscale and optionally split tall crops into overlapping horizontal chunks.
9. **Schema-guided extraction:** use document-type-specific Mirage form fields and keyword hints.
10. **Validation:** validate the final JSON contract and retain warnings; never silently invent missing values.
11. **Export:** JSON preserves nested structure; CSV exports the primary flat table; XLSX separates summary, primary table and page metadata.

## Non-functional requirements

- Windows 11, CPU-only, Python local server.
- Sequential page processing for documents up to 50 pages.
- Load one Mirage instance and reuse it; serialize inference calls.
- No external OCR/LLM endpoints.
- Disable Cactus telemetry.
- Cache model files during setup; set offline mode for application inference.
- Bind the server to 127.0.0.1 only.
- Keep inference behind an interface so a future WebAssembly engine can implement the same domain contract.

## Explicit constraints and assumptions

- Initial setup requires internet to install packages and cache the Cactus runtime and Mirage weights.
- The first release is a single-user desktop-local application, not a network-hosted multi-user service.
- Model predictions and OCR must be reviewed by a person before financial or medical use.
- Mirage's documented OCR text reader supports Latin script. Other scripts need target-machine evaluation and may require a different on-device OCR strategy, which would need explicit approval because Mirage is the selected engine constraint.
- The current table reconstruction is geometry-based and heuristic. It is not claimed to be a universal table-structure-recognition solution.
