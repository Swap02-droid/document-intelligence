# Known Gaps and Next Steps

These are deliberately recorded so they are not mistaken for completed capabilities.

1. **Real Mirage CPU acceptance:** Run `scripts/download_model.py` and `scripts/smoke_test.py` on the target Windows 11 PC. Record actual output shape, load time, inference time and memory.
2. **OCR quality evaluation:** Create a small ground-truth dataset of representative invoices, statements, medical forms and reports. Measure character/field accuracy and row/column accuracy.
3. **Table structure recognition:** Current column grouping uses OCR bounding-box centers. Complex merged cells, multi-line cells, borderless tables, rotated pages and pages with multiple tables require further heuristics or a dedicated local layout strategy.
4. **Multi-page continuation:** Header repetition and headerless continuation are handled heuristically. Validate subtotals, carry-forward balances, rows split across pages and multiple tables per page.
5. **Confidence handling:** Mirage returns OCR scores and form probabilities. The first UI does not yet expose per-cell confidence. Add it after inspecting real model result envelopes and defining thresholds from a labelled dataset.
6. **Review/edit workflow:** The current UI previews but does not let users correct cells before export. A future version should allow edits and mark changed values.
7. **Job cancellation:** Not implemented in v1. A 50-page job runs to completion or failure.
8. **Persistent jobs:** Job state is in memory and is lost when the server stops. Exports remain in `temp/exports` until cleanup/manual deletion.
9. **WASM version:** The inference abstraction is prepared, but browser-side model loading, browser memory handling and browser export have not been implemented.
10. **Additional scripts/languages:** Mirage's documented OCR reader is Latin-script focused. Evaluate the languages in your real documents before broadening the supported-document claim.
11. **Production hardening:** Authentication, malware scanning, encrypted storage, formal retention controls and multi-user isolation are not included because v1 is a local desktop tool.
12. **Accuracy safeguards:** All results remain `review_required=true`. Financial totals and medical instructions must be checked against the source document.
