# Build Information

- Project: Local Document Intelligence
- Version: 1.0.0
- Build date: 2026-11-20
- Target: Windows 11 x64, Python 3.11, CPU-only
- Cactus dependency: `cactus-compute[vision]==4.2.6`
- Automated tests: **15 passed** in the packaging environment (Linux, Python 3.13.5)
- Python compile check: passed
- JavaScript syntax check (`node --check frontend/app.js`): passed
- Mirage native model test: **not run in this build environment**; run `scripts/download_model.py` and `scripts/smoke_test.py` on the target Windows machine after installation.

The automated tests use the included deterministic fake inference adapter. They verify the application pipeline, not Mirage OCR accuracy. See `docs/TEST_REPORT.md` and `docs/ACCEPTANCE_CHECKLIST.md`.
