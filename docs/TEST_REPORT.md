# Test Report

## Automated tests

The repository test suite uses a deterministic fake inference engine. It is intended to validate application behavior without requiring the Cactus package or downloading model weights.

Expected coverage:

- OCR-region parser and bounding-box normalization
- Row grouping and geometry-based table reconstruction
- Document result schema validation
- JSON, CSV and XLSX export generation
- Image-based document service flow using a fake Mirage adapter
- API health and upload validation

## Real Mirage test (must be run on the target Windows PC)

```powershell
.venv\Scripts\python.exe scripts\download_model.py
.venv\Scripts\python.exe scripts\smoke_test.py
```

Inspect the raw output for text blocks, boxes and scores. The smoke test does not claim OCR accuracy; compare detected text against the included sample image and your own representative documents.

## Offline test (must be run on target PC)

After the model cache is populated, disable network connectivity and run the real smoke test again. A successful result verifies that the local cache is sufficient for that installed version and machine.

## Test status in the packaged build

The test suite is included and should be run with `python -m pytest -v`. The build environment can run application tests with the fake adapter. It cannot validate actual Mirage native runtime execution on the user's Windows CPU; that remains a target-machine acceptance test.
