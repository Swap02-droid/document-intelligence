from app.preprocessing.text_regions import iter_text_regions


def test_iter_text_regions_reads_text_and_bbox():
    payload = {"text": [{"text": "Invoice", "bbox": [10, 20, 200, 60], "score": 0.9}]}
    regions = list(iter_text_regions(payload))
    assert len(regions) == 1
    assert regions[0].text == "Invoice"
    assert regions[0].bbox == (10.0, 20.0, 200.0, 60.0)
    assert regions[0].score == 0.9


def test_iter_text_regions_accepts_normalized_unit_coordinates_and_deduplicates():
    payload = {"regions": [
        {"value": "Total", "box": [0.1, 0.2, 0.4, 0.3]},
        {"value": "Total", "box": [0.1, 0.2, 0.4, 0.3]},
    ]}
    regions = list(iter_text_regions(payload))
    assert len(regions) == 1
    assert regions[0].bbox == (100.0, 200.0, 400.0, 300.0)


def test_iter_text_regions_supports_cactus_string_key_and_keeps_best_overlap():
    payload = {"text": [
        {"string": "TOTAL INR 1000", "bbox": [100, 100, 600, 180], "score": 0.4},
        {"string": "TOTAL INR 1000", "bbox": [102, 101, 599, 179], "score": 0.9},
    ]}
    regions = list(iter_text_regions(payload))
    assert len(regions) == 1
    assert regions[0].score == 0.9
