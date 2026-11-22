from dataclasses import dataclass
from typing import Any, Iterator


@dataclass
class TextRegion:
    text: str
    bbox: tuple[float, float, float, float]  # normalized 0..1000
    score: float | None = None


def _normalize_bbox(value: Any) -> tuple[float, float, float, float] | None:
    if isinstance(value, dict):
        keys = ("x1", "y1", "x2", "y2")
        if all(k in value for k in keys):
            values = [value[k] for k in keys]
        elif all(k in value for k in ("x", "y", "width", "height")):
            values = [value["x"], value["y"], value["x"] + value["width"], value["y"] + value["height"]]
        else:
            return None
    elif isinstance(value, (list, tuple)) and len(value) >= 4:
        values = value[:4]
    else:
        return None
    try:
        x1, y1, x2, y2 = (float(v) for v in values)
    except (TypeError, ValueError):
        return None
    # Mirage uses 0..1000 coordinates. Also accept pixel-like 0..1 coordinates.
    if max(abs(x1), abs(y1), abs(x2), abs(y2)) <= 1.01:
        x1, y1, x2, y2 = x1 * 1000, y1 * 1000, x2 * 1000, y2 * 1000
    if x2 < x1:
        x1, x2 = x2, x1
    if y2 < y1:
        y1, y2 = y2, y1
    if x2 <= 0 or y2 <= 0 or x1 >= 1000 or y1 >= 1000:
        return None
    return (max(0, x1), max(0, y1), min(1000, x2), min(1000, y2))


def iter_text_regions(payload: Any) -> Iterator[TextRegion]:
    """Defensive parser for Mirage's structured text-region output."""
    seen: set[tuple[str, tuple[float, float, float, float]]] = set()

    def walk(node: Any):
        if isinstance(node, dict):
            bbox = _normalize_bbox(node.get("bbox", node.get("box")))
            text = None
            for key in ("string", "text", "value", "content", "transcription", "label"):
                candidate = node.get(key)
                if isinstance(candidate, str) and candidate.strip():
                    text = candidate.strip()
                    break
            if bbox and text:
                try:
                    score = float(node.get("score", node.get("confidence", node.get("text_conf", 0))))
                except (TypeError, ValueError):
                    score = None
                key = (text, bbox)
                if key not in seen:
                    seen.add(key)
                    yield TextRegion(text=text, bbox=bbox, score=score)
            for value in node.values():
                if isinstance(value, (dict, list, tuple)):
                    yield from walk(value)
        elif isinstance(node, (list, tuple)):
            for item in node:
                yield from walk(item)

    collected = list(walk(payload))
    # Mirage may return overlapping OCR proposals for one visual text line. Keep
    # the highest-scoring proposal when boxes overlap almost completely.
    selected: list[TextRegion] = []
    for candidate in sorted(collected, key=lambda item: item.score if item.score is not None else -1, reverse=True):
        x1, y1, x2, y2 = candidate.bbox
        candidate_area = max(1.0, (x2 - x1) * (y2 - y1))
        duplicate = False
        for existing in selected:
            a1, b1, a2, b2 = existing.bbox
            ix1, iy1 = max(x1, a1), max(y1, b1)
            ix2, iy2 = min(x2, a2), min(y2, b2)
            intersection = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
            existing_area = max(1.0, (a2 - a1) * (b2 - b1))
            union = candidate_area + existing_area - intersection
            if union > 0 and intersection / union >= 0.78:
                duplicate = True
                break
        if not duplicate:
            selected.append(candidate)
    yield from selected
