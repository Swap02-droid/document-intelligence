from app.preprocessing.text_regions import TextRegion
from app.preprocessing.table_layout import rows_to_table, group_regions_into_lines


def test_reconstructs_simple_three_column_table():
    regions = [
        TextRegion("Date", (20, 80, 140, 120)),
        TextRegion("Description", (220, 80, 500, 120)),
        TextRegion("Amount", (780, 80, 960, 120)),
        TextRegion("2026-01-05", (20, 150, 180, 190)),
        TextRegion("Office supplies", (220, 150, 540, 190)),
        TextRegion("1250.00", (800, 150, 950, 190)),
    ]
    result = rows_to_table(regions, ("date", "description", "amount"))
    assert result["headers"] == ["Date", "Description", "Amount"]
    assert len(result["rows"]) == 1
    assert result["rows"][0]["Description"] == "Office supplies"
    assert result["rows"][0]["Amount"] == "1250.00"


def test_groups_regions_into_visual_rows():
    regions = [TextRegion("A", (10, 10, 30, 30)), TextRegion("B", (100, 12, 130, 32)), TextRegion("C", (10, 100, 30, 120))]
    rows = group_regions_into_lines(regions, y_tolerance=16)
    assert len(rows) == 2
    assert len(rows[0]) == 2
