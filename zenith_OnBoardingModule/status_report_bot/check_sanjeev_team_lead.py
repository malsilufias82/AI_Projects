
#!/usr/bin/env python3
from pathlib import Path
import openpyxl
from datetime import date

def parse_week_date(sheet_name):
    import re
    patterns = [
        r"(\d{1,2})-(\d{1,2})-(\d{4})",
        r"Week Ending (\d{1,2})-(\d{1,2})-(\d{4})",
        r"Week ending (\d{1,2})-(\d{1,2})",
    ]

    for pattern in patterns:
        match = re.search(pattern, sheet_name)
        if match:
            try:
                if len(match.groups()) == 3:
                    day, month, year = map(int, match.groups())
                    return date(year, month, day)
                elif len(match.groups()) == 2:
                    day, month = map(int, match.groups())
                    return date(date.today().year, month, day)
            except ValueError:
                continue
    return None

excel_path = Path(__file__).parent / "data" / "Project_Phoenix_ Status Update- Product Team.xlsx"

wb = openpyxl.load_workbook(excel_path, data_only=True)
for sheet_name in wb.sheetnames:
    week_date = parse_week_date(sheet_name)
    if week_date and week_date == date(2026,6,28):
        ws = wb[sheet_name]
        for row_idx, row in enumerate(ws.iter_rows(values_only=True), 1):
            if row_idx < 5:
                continue
            employee_name = row[3] if row[3] else ""
            if "Sanjeev" in str(employee_name):
                print(f"Row {row_idx}:")
                print(f"  Employee Name: {employee_name}")
                print(f"  Team Lead: {row[4]}")
                print(f"  Columns: {[f'{i}: {repr(val)}' for i, val in enumerate(row)]}")
                print()

wb.close()
