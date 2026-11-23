from datetime import date, datetime

import pytest

from sla import (
    activity_sla_deadlines,
    first_day_start_date,
    holiday_dates_from_records,
    parse_timestamp,
    sla_status,
)


def test_day_one_starts_same_day_before_two_pm():
    assert first_day_start_date(
        datetime(2026, 10, 9, 13, 59), set()
    ) == date(2026, 10, 9)


def test_day_one_starts_next_working_day_at_or_after_two_pm():
    holidays = {date(2026, 10, 12)}
    assert first_day_start_date(
        datetime(2026, 10, 9, 14, 0), holidays
    ) == date(2026, 10, 13)


def test_day_deadlines_skip_weekends_and_non_restricted_holidays():
    activities = [
        {"id": 1, "day": "Day1"},
        {"id": 2, "day": "Day2"},
        {"id": 3, "day": "Day3"},
        {"id": 4, "day": "Day4"},
        {"id": 5, "day": "Day5"},
        {"id": 6, "day": "Week0"},
    ]
    holidays = {date(2026, 10, 12)}

    deadlines = activity_sla_deadlines(
        activities, datetime(2026, 10, 9, 13, 0), holidays
    )

    assert deadlines == {
        "1": datetime(2026, 10, 9, 20, 0),
        "2": datetime(2026, 10, 14, 20, 0),
        "3": datetime(2026, 10, 15, 20, 0),
        "4": datetime(2026, 10, 16, 20, 0),
        "5": datetime(2026, 10, 19, 20, 0),
    }


def test_incomplete_and_completed_activity_sla_states():
    deadline = datetime(2026, 10, 9, 20, 0)

    assert sla_status(deadline, datetime(2026, 10, 8, 20, 0)) == "Within SLA"
    assert sla_status(deadline, datetime(2026, 10, 9, 19, 59)) == "SLA Warning"
    assert sla_status(deadline, datetime(2026, 10, 9, 20, 1)) == "SLA Breached"
    assert sla_status(
        deadline, datetime(2026, 10, 10, 12, 0), datetime(2026, 10, 9, 19, 0)
    ) == "Within SLA"
    assert sla_status(
        deadline, datetime(2026, 10, 10, 12, 0), deadline
    ) == "Within SLA"
    assert sla_status(
        deadline, datetime(2026, 10, 10, 12, 0), datetime(2026, 10, 9, 20, 1)
    ) == "SLA Breached"


def test_day_labels_match_day_one_to_day_five_only():
    activities = [
        {"id": 1, "day": "Day 1"},
        {"id": 2, "day": "Day2a"},
        {"id": 3, "day": "Day10"},
        {"id": 4, "day": "Week0"},
    ]

    deadlines = activity_sla_deadlines(
        activities, datetime(2026, 10, 9, 13, 0), set()
    )

    assert set(deadlines) == {"1", "2"}


def test_restricted_holidays_are_not_excluded_from_working_days():
    holidays = holiday_dates_from_records(
        [
            {"date": "2026-10-12", "type": "Public Holiday"},
            {"date": "2026-10-13", "type": " Restricted   Holiday "},
        ]
    )

    assert holidays == {date(2026, 10, 12)}


def test_invalid_saved_timestamp_is_reported():
    with pytest.raises(ValueError, match="Unsupported SLA timestamp"):
        parse_timestamp("not a timestamp")
