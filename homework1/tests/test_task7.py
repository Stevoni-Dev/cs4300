import pytest
from datetime import date
from src.task7 import diff_days


@pytest.mark.parametrize(
    "start_date, end_date, expected",
    [
        (date(2026, 1, 1), date(2026, 1, 2), 1),
        (date(2026, 1, 1), date(2026, 1, 10), 9),
        (date(2026, 1, 10), date(2026, 1, 1), -9),
        (date(2026, 1, 1), date(2026, 1, 1), 0),
        (date(2026, 1, 31), date(2026, 2, 1), 1),
        (date(2026, 2, 28), date(2026, 3, 1), 1),
        (date(2024, 2, 28), date(2024, 3, 1), 2),
        (date(2026, 12, 31), date(2027, 1, 1), 1),
    ],
)
def test_diff_days(start_date, end_date, expected):
    assert diff_days(start_date, end_date) == expected

@pytest.mark.parametrize(
    "start_date, end_date",
    [
        ("2026-01-01", date(2026, 1, 2)),
        (date(2026, 1, 1), "2026-01-02"),
        ("2026-01-01", "2026-01-02"),
        (20260101, date(2026, 1, 2)),
        (date(2026, 1, 1), 20260102),
        (1.5, date(2026, 1, 2)),
        (date(2026, 1, 1), 1.5),
        (None, date(2026, 1, 2)),
        (date(2026, 1, 1), None),
        ([], date(2026, 1, 2)),
    ],
)
def test_diff_days_invalid_inputs(capsys, start_date, end_date):
    result = diff_days(start_date, end_date)
    captured = capsys.readouterr()
    assert captured.out == "Both arguments must be valid dates\n"  
    assert result == False