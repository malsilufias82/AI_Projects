"""Calendar-based SLA date calculations for onboarding activities."""

import re
from datetime import date, datetime, time, timedelta
from typing import Any, Iterable


SLA_DEADLINE_TIME = time(20, 0)
DAY_LABEL_PATTERN = re.compile(r"^\s*day\s*([1-5])(?:\b|[a-z])", re.IGNORECASE)


def parse_timestamp(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str) and value.strip():
        try:
            parsed = datetime.fromisoformat(value.strip())
        except ValueError as exc:
            raise ValueError(f"Unsupported SLA timestamp: {value}") from exc
    elif value is None or value == "":
        return None
    else:
        raise ValueError("SLA timestamps must be ISO-formatted strings.")

    if parsed.tzinfo is not None:
        parsed = parsed.astimezone().replace(tzinfo=None)
    return parsed


def is_working_day(value: date, holidays: set[date]) -> bool:
    return value.weekday() < 5 and value not in holidays


def next_working_day(value: date, holidays: set[date]) -> date:
    candidate = value + timedelta(days=1)
    while not is_working_day(candidate, holidays):
        candidate += timedelta(days=1)
    return candidate


def holiday_dates_from_records(records: Iterable[dict[str, Any]]) -> set[date]:
    holidays = set()
    for record in records:
        holiday_type = " ".join(str(record.get("type") or "").split()).casefold()
        if holiday_type == "restricted holiday":
            continue
        holiday_date = record.get("date")
        if not isinstance(holiday_date, str):
            raise ValueError("Holiday record is missing an ISO date.")
        try:
            holidays.add(date.fromisoformat(holiday_date))
        except ValueError as exc:
            raise ValueError(f"Unsupported holiday date: {holiday_date}") from exc
    return holidays


def activity_day_number(day_label: Any) -> int | None:
    match = DAY_LABEL_PATTERN.match(str(day_label or ""))
    return int(match.group(1)) if match else None


def first_day_start_date(
    credentials_received_at: datetime, holidays: set[date]
) -> date:
    start_date = credentials_received_at.date()
    if credentials_received_at.time() >= time(14, 0):
        start_date += timedelta(days=1)
    while not is_working_day(start_date, holidays):
        start_date += timedelta(days=1)
    return start_date


def activity_sla_deadlines(
    activities: Iterable[dict[str, Any]],
    credentials_received_at: datetime | None,
    holidays: set[date],
) -> dict[str, datetime]:
    if credentials_received_at is None:
        return {}

    day_dates = {1: first_day_start_date(credentials_received_at, holidays)}
    for day_number in range(2, 6):
        day_dates[day_number] = next_working_day(
            day_dates[day_number - 1], holidays
        )

    deadlines: dict[str, datetime] = {}
    for activity in activities:
        day_number = activity_day_number(activity.get("day"))
        if day_number is None:
            continue
        due_date = day_dates[day_number]
        if day_number > 1:
            due_date = next_working_day(due_date, holidays)
        deadlines[str(activity["id"])] = datetime.combine(
            due_date, SLA_DEADLINE_TIME
        )
    return deadlines


def sla_status(
    deadline: datetime,
    now: datetime,
    completed_at: datetime | None = None,
) -> str:
    if completed_at is not None:
        return "Within SLA" if completed_at <= deadline else "SLA Breached"
    if now < deadline and now.date() < deadline.date():
        return "Within SLA"
    if now <= deadline:
        return "SLA Warning"
    return "SLA Breached"
