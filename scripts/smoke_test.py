"""Real Cactus Mirage inference smoke test; run after download_model.py."""
import json
import os
from pathlib import Path
from time import perf_counter

os.environ["CACTUS_TELEMETRY"] = "0"
os.environ["DO_NOT_TRACK"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"
ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "samples" / "sample_invoice.png"


def main():
    if not IMAGE.exists():
        raise SystemExit(f"Sample image not found: {IMAGE}")
    import cactus

    start = perf_counter()
    vision = cactus.Mirage()
    loaded = perf_counter()
    result = vision.describe(
        str(IMAGE),
        sections=["objects", "text"],
        fields=["bbox", "score"],
        max_text_lines=300,
        max_objects=80,
        max_tokens=1200,
        keywords=["invoice number", "invoice date", "description", "quantity", "unit price", "amount", "total"],
    )
    ended = perf_counter()
    print("=== RAW MIRAGE OUTPUT ===")
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    print("=== TIMING ===")
    print(f"Initialization: {loaded - start:.2f}s")
    print(f"Inference: {ended - loaded:.2f}s")
    if not isinstance(result, dict):
        raise SystemExit("Mirage returned an unexpected result type.")
    print("Smoke test completed. Inspect the OCR text and bounding boxes for correctness.")


if __name__ == "__main__":
    main()
