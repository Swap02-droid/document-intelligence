import os
import threading
from typing import Any

from PIL import Image

from app.inference.base import VisionEngine


class MirageUnavailableError(RuntimeError):
    pass


class CactusMirageEngine(VisionEngine):
    """Lazy, process-wide Mirage adapter. The model is loaded once and reused."""

    def __init__(self) -> None:
        os.environ["CACTUS_TELEMETRY"] = "0"
        os.environ["DO_NOT_TRACK"] = "1"
        os.environ["HF_HUB_OFFLINE"] = "1"
        try:
            import cactus
        except Exception as exc:
            raise MirageUnavailableError(
                "Cactus Mirage is unavailable. Run install.bat and then scripts\\download_model.py. "
                f"Import error: {exc}"
            ) from exc
        try:
            # Keep CPU usage predictable on desktop machines. Set CACTUS_THREADS to tune.
            set_threads = getattr(cactus, "set_threads", None)
            if callable(set_threads):
                set_threads(max(1, int(os.getenv("CACTUS_THREADS", "2"))))
            self._model = cactus.Mirage()
        except Exception as exc:
            raise MirageUnavailableError(
                "Mirage could not initialize. Run scripts\\download_model.py while online, "
                f"then retry. Details: {exc}"
            ) from exc
        self._lock = threading.RLock()

    def describe(self, image: Image.Image, keywords: list[str] | None = None) -> dict[str, Any]:
        with self._lock:
            result = self._model.describe(
                image,
                sections=["objects", "text"],
                fields=["bbox", "score"],
                max_text_lines=300,
                max_objects=80,
                max_tokens=1200,
                keywords=keywords,
            )
        if not isinstance(result, dict):
            raise RuntimeError(f"Unexpected Mirage describe result: {type(result).__name__}")
        return result

    def extract(self, image: Image.Image, form: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            result = self._model.extract(image, form)
        if not isinstance(result, dict):
            raise RuntimeError(f"Unexpected Mirage extract result: {type(result).__name__}")
        return result


class FakeMirageEngine(VisionEngine):
    """Deterministic development engine used only by tests and DEMO_MODE."""

    def describe(self, image: Image.Image, keywords: list[str] | None = None) -> dict[str, Any]:
        return {
            "text": [
                {"text": "Date", "bbox": [40, 80, 150, 115], "score": 0.99},
                {"text": "Description", "bbox": [190, 80, 480, 115], "score": 0.99},
                {"text": "Amount", "bbox": [760, 80, 940, 115], "score": 0.99},
                {"text": "2026-01-05", "bbox": [40, 145, 170, 180], "score": 0.98},
                {"text": "Office supplies", "bbox": [190, 145, 500, 180], "score": 0.98},
                {"text": "1250.00", "bbox": [790, 145, 940, 180], "score": 0.98},
            ],
            "objects": [],
        }

    def extract(self, image: Image.Image, form: dict[str, Any]) -> dict[str, Any]:
        return {"form": {key: None for key in form}}
