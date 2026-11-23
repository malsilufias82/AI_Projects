
#!/usr/bin/env python3
import sys
import re
from pathlib import Path
from datetime import date
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import load_config
from excel_reader import ExcelReader
from generate_team_lead_report import SkippedEmployeesTracker

def parse_week_date(sheet_name: str) -> date | None:
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
                    from datetime import datetime
                    return date(datetime.now().year, month, day)
            except ValueError:
                continue
    return None

def main():
    config = load_config()
    reader = ExcelReader(config)
    
    target_date = None
    if len(sys.argv) > 1:
        try:
            day, month, year = map(int, sys.argv[1].split("-"))
            if len(str(year)) == 2:
                year += 2000
            target_date = date(year, month, day)
        except Exception as e:
            print(f"Warning: Invalid date format, using latest week.")
    
    records, sheet_info = reader.read_employee_records(target_week_date=target_date)
    skipped_tracker = SkippedEmployeesTracker(Path(__file__).parent / "data" / "skipped_employees.json")
    
    tl_records = {}
    tl_pending = {}
    for rec in records:
        tl = rec.team_lead or "Unassigned"
        if tl not in tl_records:
            tl_records[tl] = []
        tl_records[tl].append(rec)
    
    for tl_name, team_records in sorted(tl_records.items()):
        print(f"\n=== Team Lead: {tl_name} ===")
        non_skipped = []
        tl_pending[tl_name] = []
        print("  Team members:")
        for rec in team_records:
            emp_key = f"{rec.employee_name}::{rec.team_lead}"
            is_skipped = skipped_tracker.history.get("employees", {}).get(emp_key, {}).get("is_skipped", False)
            print(f"    {rec.employee_name}: status={rec.status}, is_skipped={is_skipped}, emp_key={emp_key}")
            if is_skipped:
                print(f"      SKIPPING this employee")
                continue
            non_skipped.append(rec)
            if rec.status.lower() == "pending":
                tl_pending[tl_name].append(rec.employee_name)
                print(f"      Marked as pending")
        
        all_completed = all(rec.status.lower() == "completed" for rec in non_skipped)
        print(f"\n  Non-skipped count: {len(non_skipped)}")
        print(f"  All completed: {all_completed}")
        print(f"  Team status: {'Completed' if all_completed else 'Pending'}")
        if not all_completed:
            print(f"  Pending employees: {', '.join(tl_pending[tl_name])}")

if __name__ == "__main__":
    main()
