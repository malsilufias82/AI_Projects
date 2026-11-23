import io
import re
from datetime import date, datetime
from typing import Any

import pdfplumber


def _normalize_header(value: Any) -> str:
    return re.sub(r"[^a-z]", "", str(value or "").lower())


def _parse_holiday_date(value: Any) -> tuple[str, int]:
    raw_date = str(value or "").strip()
    if not raw_date:
        raise ValueError("Holiday row is missing a date.")

    parsed_date: date | None = None
    date_formats = (
        "%d-%b-%y",
        "%d-%b-%Y",
        "%d %b %Y",
        "%d-%B-%Y",
        "%d %B %Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
    )
    for date_format in date_formats:
        try:
            parsed_date = datetime.strptime(raw_date, date_format).date()
            break
        except ValueError:
            continue

    if parsed_date is None:
        try:
            parsed_date = datetime.fromisoformat(raw_date).date()
        except ValueError as exc:
            raise ValueError(f"Unsupported holiday date: {raw_date}") from exc

    return parsed_date.isoformat(), parsed_date.year


def parse_holiday_pdf(contents: bytes) -> list[dict[str, Any]]:
    holidays: list[dict[str, Any]] = []

    with pdfplumber.open(io.BytesIO(contents)) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables() or []:
                if not table:
                    continue

                header_index = next(
                    (
                        index
                        for index, row in enumerate(table)
                        if {"holidayname", "day", "date", "type"}.issubset(
                            {_normalize_header(cell) for cell in row}
                        )
                    ),
                    None,
                )
                if header_index is None:
                    continue

                headers = [_normalize_header(cell) for cell in table[header_index]]
                name_index = headers.index("holidayname")
                day_index = headers.index("day")
                date_index = headers.index("date")
                type_index = headers.index("type")

                for row in table[header_index + 1 :]:
                    if max(name_index, day_index, date_index, type_index) >= len(row):
                        continue

                    holiday_name = " ".join(str(row[name_index] or "").split())
                    day = " ".join(str(row[day_index] or "").split())
                    raw_date = str(row[date_index] or "").strip()
                    holiday_type = " ".join(str(row[type_index] or "").split())
                    if not any((holiday_name, day, raw_date, holiday_type)):
                        continue
                    if not all((holiday_name, day, raw_date, holiday_type)):
                        raise ValueError("Holiday row is missing a required field.")

                    normalized_date, year = _parse_holiday_date(raw_date)
                    holidays.append(
                        {
                            "holiday_name": holiday_name,
                            "day": day,
                            "date": normalized_date,
                            "year": year,
                            "type": holiday_type,
                        }
                    )

    if not holidays:
        raise ValueError(
            'No holiday table found. The PDF must contain "Holiday Name", "Day", "Date", and "Type" columns.'
        )

    return holidays
