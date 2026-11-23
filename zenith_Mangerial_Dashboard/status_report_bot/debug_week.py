
#!/usr/bin/env python3
import sys
import re
from pathlib import Path
from datetime import datetime, date
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import load_config
from excel_reader import ExcelReader

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
                    return date(datetime.now().year, month, day)
            except ValueError:
                continue
    return None

def check_sheet_for_date():
    config = load_config()
    reader = ExcelReader(config)
    
    target_date = None
    try:
        target_date = parse_week_date("05-07-2026")
    except Exception as e:
        print(f"Error parsing date: {e}")
        return

    print(f"Checking for sheets for date {target_date}")
    for team_file in config.team_excel_files:
        file_path = team_file["file_path"]
        team_name = team_file["team_name"]
        print(f"\nChecking {team_name} file: {file_path}")
        try:
            import openpyxl
            wb = openpyxl.load_workbook(file_path, read_only=True)
            for sheet_name in wb.sheetnames:
                week_date = parse_week_date(sheet_name)
                print(f"  Sheet: {sheet_name} → Date: {week_date}")
            wb.close()
        except Exception as e:
            print(f"  Error: {e}")

def check_sanjeev_team():
    config = load_config()
    reader = ExcelReader(config)
    
    target_date = parse_week_date("05-07-2026")
    records, sheet_info = reader.read_employee_records(target_week_date=target_date)
    print("\n\n=== Sheet info used: ===")
    for team, sheet in sheet_info.items():
        print(f"{team}: {sheet}")
    
    print("\n=== All employees: ===")
    for rec in records:
        print(f"  {rec.employee_name}: {rec.status} (Team: {rec.team}, TL: {rec.team_lead})")
    
    print("\n=== Employees under Sanjeev Biswas: ===")
    for rec in records:
        if rec.team_lead == "Sanjeev Biswas" or rec.employee_name == "Sanjeev Biswas":
            print(f"  {rec.employee_name}: {rec.status} (Team: {rec.team}, TL: {rec.team_lead})")

if __name__ == "__main__":
    check_sheet_for_date()
    check_sanjeev_team()
