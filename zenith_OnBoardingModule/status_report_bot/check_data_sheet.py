
import openpyxl
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))
from config import load_config

config = load_config()

def check_sheet(file_path, target_date_str):
    print(f"\n--- Checking {file_path} ---")
    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    # Find sheet matching target date
    target_sheet = None
    for sheet_name in wb.sheetnames:
        if target_date_str in sheet_name:
            target_sheet = sheet_name
            break
    if not target_sheet:
        print(f"No sheet found matching '{target_date_str}'")
        wb.close()
        return
    print(f"Using sheet: {target_sheet}")
    ws = wb[target_sheet]
    # Print first 40 rows
    print("\nFirst 40 rows:")
    for i, row in enumerate(ws.iter_rows(values_only=True), 1):
        if i > 40:
            break
        print(f"{i:3}. {row}")
    wb.close()

check_sheet("./data/Project_Phoenix_ Status Update - Platform team.xlsx", "28-06-2026")
check_sheet("./data/Project_Phoenix_ Status Update - Platform team.xlsx", "05-07-2026")
check_sheet("./data/Project_Phoenix_ Status Update- Product Team.xlsx", "28-06-2026")
check_sheet("./data/Project_Phoenix_ Status Update- Product Team.xlsx", "05-07-2026")
check_sheet("./data/Data Team - Daily Tracker.xlsx", "26-06")  # Because Data Team's sheet is "Week ending 26-06" for 28-06-2026?
check_sheet("./data/Data Team - Daily Tracker.xlsx", "05-07")
