import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))
from config import load_config
from excel_reader import ExcelReader

config = load_config()
reader = ExcelReader(config)

all_weeks_sorted = reader._get_all_available_week_dates_sorted()  # Call existing method from reader
print("All available weeks in order:")
for week in all_weeks_sorted:
    print(f"  {week.strftime('%d-%m-%Y')}")

if len(all_weeks_sorted) >=2:
    last_two = all_weeks_sorted[-2:]
    print(f"\nLast two weeks to keep:")
    for week in last_two:
        print(f"  {week.strftime('%d-%m-%Y')}")
else:
    print("\nNot enough weeks to keep two")
