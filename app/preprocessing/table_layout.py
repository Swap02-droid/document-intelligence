from dataclasses import dataclass
from statistics import median
from typing import Iterable
from PIL import Image

from app.preprocessing.text_regions import TextRegion


@dataclass
class OCRLine:
    text: str
    x1: float
    y1: float
    x2: float
    y2: float
    score: float | None = None

    @property
    def center_y(self) -> float:
        return (self.y1 + self.y2) / 2

    @property
    def center_x(self) -> float:
        return (self.x1 + self.x2) / 2


def group_regions_into_lines(regions: Iterable[TextRegion], y_tolerance: float = 16.0) -> list[list[OCRLine]]:
    items = sorted(regions, key=lambda r: ((r.bbox[1] + r.bbox[3]) / 2, r.bbox[0]))
    rows: list[list[OCRLine]] = []
    row_centers: list[float] = []
    for region in items:
        x1, y1, x2, y2 = region.bbox
        line = OCRLine(region.text, x1, y1, x2, y2, region.score)
        cy = line.center_y
        if rows and abs(cy - row_centers[-1]) <= y_tolerance:
            rows[-1].append(line)
            row_centers[-1] = sum(x.center_y for x in rows[-1]) / len(rows[-1])
        else:
            rows.append([line])
            row_centers.append(cy)
    for row in rows:
        row.sort(key=lambda item: item.x1)
    return rows


def find_table_crop(image: Image.Image, regions: list[TextRegion], min_rows: int = 3) -> Image.Image | None:
    """Find a dense, repeated text block; return a padded crop for a second OCR pass."""
    rows = group_regions_into_lines(regions)
    candidates = [row for row in rows if len(row) >= 2]
    if len(candidates) < min_rows:
        return None
    # Select the longest consecutive run of multi-cell rows.
    runs: list[list[list[OCRLine]]] = []
    current: list[list[OCRLine]] = []
    for row in rows:
        if len(row) >= 2:
            current.append(row)
        elif current:
            runs.append(current)
            current = []
    if current:
        runs.append(current)
    if not runs:
        return None
    run = max(runs, key=lambda block: sum(len(row) for row in block))
    if len(run) < min_rows:
        return None
    x1 = min(line.x1 for row in run for line in row)
    y1 = min(line.y1 for row in run for line in row)
    x2 = max(line.x2 for row in run for line in row)
    y2 = max(line.y2 for row in run for line in row)
    width, height = image.size
    pad_x, pad_y = 18, 18
    left = max(0, int(x1 / 1000 * width) - pad_x)
    top = max(0, int(y1 / 1000 * height) - pad_y)
    right = min(width, int(x2 / 1000 * width) + pad_x)
    bottom = min(height, int(y2 / 1000 * height) + pad_y)
    if right - left < 100 or bottom - top < 60:
        return None
    return image.crop((left, top, right, bottom))


def rows_to_table(regions: list[TextRegion], header_hints: tuple[str, ...] = ()) -> dict:
    lines = group_regions_into_lines(regions)
    if not lines:
        return {"headers": [], "rows": []}

    def normalize(value: str) -> str:
        return " ".join(value.lower().replace("\n", " ").split())

    header_index = 0
    if header_hints:
        best_score = 0
        for index, row in enumerate(lines[:12]):
            text = " ".join(normalize(item.text) for item in row)
            score = sum(1 for hint in header_hints if hint in text)
            if score > best_score:
                best_score, header_index = score, index

    header_row = lines[header_index]
    headers = [item.text.strip() for item in header_row]
    if len(headers) == 1 and len(lines) > 1:
        # A full-row OCR string may contain delimited columns.
        parts = [part.strip() for part in headers[0].split(" | ") if part.strip()]
        if len(parts) > 1:
            headers = parts
    centers = [item.center_x for item in header_row]
    if len(centers) == 1 and len(headers) > 1:
        centers = [1000 * (i + 0.5) / len(headers) for i in range(len(headers))]

    output_rows: list[dict[str, str]] = []
    for row in lines[header_index + 1:]:
        cells = [""] * len(headers)
        for item in row:
            if not centers:
                continue
            nearest = min(range(len(centers)), key=lambda idx: abs(item.center_x - centers[idx]))
            if cells[nearest]:
                cells[nearest] += " " + item.text
            else:
                cells[nearest] = item.text
        if any(value.strip() for value in cells):
            output_rows.append({headers[i] or f"column_{i+1}": cells[i].strip() for i in range(len(headers))})

    # Avoid returning a false table when the page is mostly paragraphs.
    return {"headers": headers, "rows": output_rows}
