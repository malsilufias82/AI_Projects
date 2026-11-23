
import sys
from pathlib import Path
from datetime import date
sys.path.insert(0, str(Path(__file__).parent / "src"))
from config import load_config
import re
import openpyxl


def parse_week_date(sheet_name: str) -> date | None:
    """Parse week ending date from sheet name (supports multiple formats)."""
    patterns = [
        r"(\d{1,2})-(\d{1,2})-(\d{4})",
        r"Week Ending (\d{1,2})-(\d{1,2})-(\d{4})",
        r"Week ending (\d{1,2})-(\d{1,2})",
    ]
    for pattern in patterns:
        match = re.search(pattern, sheet_name)
        if match:
            try:
                groups = match.groups()
                if len(groups) ==3:
                    day, month, year = map(int, groups)
                    return date(year, month, day)
                else:
                    day, month = map(int, groups)
                    return date(date.today().year, month, day)
            except ValueError:
                continue
    return None

def get_all_available_weeks(config):
    all_weeks = set()
    for team_file in config.team_excel_files:
        try:
            wb = openpyxl.load_workbook(team_file["file_path"], read_only=True)
            for sheet_name in wb.sheetnames:
                week_date = parse_week_date(sheet_name)
                if week_date:
                    all_weeks.add(week_date)
            wb.close()
        except Exception as e:
            pass
    return sorted(list(all_weeks))

config = load_config()
today = date.today()
all_weeks = get_all_available_weeks(config)
valid_weeks = [w for w in all_weeks if w <= today]

print(f"Today is: {today.strftime('%d-%m-%Y')}")
print("\nAll available weeks on or before today:")
for idx, week in enumerate(valid_weeks):
    print(f"  {idx+1}. {week.strftime('%d-%m-%Y')}")

if len(valid_weeks)>=2:
    last_two = valid_weeks[-2:]
    print(f"\nLast two weeks: {[w.strftime('%d-%m-%Y') for w in last_two]}")
else:
    print("\nNot enough weeks available!")
