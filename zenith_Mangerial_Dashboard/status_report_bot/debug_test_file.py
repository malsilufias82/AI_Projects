
import openpyxl
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from excel_reader import ExcelReader
from config import load_config

config = load_config()
reader = ExcelReader(config)

file_path = Path(__file__).parent / "data" / "test_platform_team.xlsx"

wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)

for sheet_name in wb.sheetnames:
    print(f"\n=== Sheet: {sheet_name} ===")
    ws = wb[sheet_name]
    rows = list(ws.iter_rows(values_only=True))
    for i, row in enumerate(rows):
        print(f"Row {i}: {row}")

print("\n--- Now calling _parse_platform_sheet ---")

ws1 = wb["10-07-2026"]
records = reader._parse_platform_sheet(ws1, "Platform Engineering")

print(f"Number of records: {len(records)}")
for rec in records:
    print(f"  {rec.employee_name}: {rec.status}, leave={rec.is_leave}, tl={rec.team_lead}")

wb.close()
