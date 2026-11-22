# Privacy and Threat Model

## Privacy goals

- Uploaded document pixels are processed by local Python code and the local Cactus Mirage runtime.
- The app does not configure or call a remote OCR, LLM, storage or analytics service.
- Cactus telemetry is disabled using `CACTUS_TELEMETRY=0` before importing Cactus.
- The HTTP server listens on loopback (`127.0.0.1`) only.
- Uploads use random temporary names; source files are removed after processing.

## Explicit setup exception

The first install and first model initialization require internet access to download Python dependencies, Cactus runtime files and Mirage weights. Once cached, inference is designed to run offline. To validate this claim on the target PC, disconnect networking after the first successful smoke test and process the included sample.

## Data lifecycle

- During processing: one source file, one active page image, temporary crop images and in-memory job state.
- After processing: source upload is deleted; the export is retained under `temp/exports` for download.
- Cleanup: expired completed/failed jobs are removed when another job is submitted. For immediate cleanup, stop the server and delete the contents of `temp/`.

## Threats and mitigations

| Threat | Current mitigation | Remaining limitation |
|---|---|---|
| Accidental remote exposure | Bind to 127.0.0.1 | Do not change host or use a tunnel |
| Malicious/renamed uploads | Extension, signature, size and PDF page checks | Not a complete malware scanner |
| Oversized PDF pages | Page count and rendered pixel cap | Very large documents can still be CPU intensive |
| Temporary data remnants | Random names and source cleanup | Filesystem deletion is not secure erasure |
| Telemetry | Cactus telemetry env var disabled | Verify again after package upgrades |
| Incorrect extraction | Warnings and human-review flag | No OCR/model can guarantee correctness |
| Cross-site requests | No permissive CORS; loopback-only service | Single-user local tool, not a multi-user security boundary |

## Before production

Add authentication/CSRF protection if the app is ever exposed beyond a local desktop, malware scanning, strict content disarm/reconstruction where appropriate, encrypted local storage, a durable job database, explicit retention controls, structured audit logs without document contents, and a formal OCR accuracy evaluation set.
