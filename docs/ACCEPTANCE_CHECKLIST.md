# Target-machine acceptance checklist

Run this after extracting the ZIP on Windows 11.

- [ ] Python 3.11 x64 is installed (`py -3.11 --version`).
- [ ] `install.bat` completes without errors.
- [ ] `scripts\download_model.bat` initializes Mirage and downloads its cache.
- [ ] `scripts\smoke_test.py` returns a structured record containing OCR text entries with `string`, `bbox` and `score` (or a compatible documented structure).
- [ ] Compare the smoke-test output with `samples\sample_invoice.png` and record obvious misses.
- [ ] `test.bat` passes.
- [ ] `run_demo.bat` starts and successfully processes the sample image (plumbing test only).
- [ ] `run.bat` starts with real Mirage; verify the browser is `http://127.0.0.1:8000`.
- [ ] Upload `samples\sample_invoice.png`; inspect extracted fields, table preview and JSON.
- [ ] Upload `samples\sample_multipage.pdf`; verify the page count and sequential processing.
- [ ] Test JSON, CSV and XLSX downloads and open the files.
- [ ] After model cache initialization, disconnect networking and repeat the real Mirage smoke test and one app extraction.
- [ ] Stop the app and inspect/delete `temp\` if local output cleanup is required.

Record CPU model, RAM, model initialization time, page inference time, DPI and document quality when reporting results. Accuracy should be evaluated against a small ground-truth set before relying on extracted financial or medical data.
