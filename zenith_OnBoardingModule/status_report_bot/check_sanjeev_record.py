
#!/usr/bin/env python3
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import load_config
from excel_reader import ExcelReader
from generate_team_lead_report import SkippedEmployeesTracker

def main():
    config = load_config()
    reader = ExcelReader(config)
    target_date = date(2026, 6, 28)
    records, sheet_info = reader.read_employee_records(target_week_date=target_date)
    skipped_tracker = SkippedEmployeesTracker(Path(__file__).parent / "data" / "skipped_employees.json")

    print("Records matching 'Sanjeev':")
    for r in records:
        if "Sanjeev" in r.employee_name or "Sanjeev" in r.team_lead:
            print(f"  {r.employee_name} :: {r.team_lead}")
            emp_key = f"{r.employee_name}::{r.team_lead}"
            is_skipped = skipped_tracker.is_skipped(emp_key)
            print(f"    emp_key: {emp_key}, is_skipped: {is_skipped}")
            print(f"    Tracker entry: {skipped_tracker.history.get('employees', {}).get(emp_key, 'NOT FOUND')}")

if __name__ == "__main__":
    main()
