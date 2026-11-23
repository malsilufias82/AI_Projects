
import openpyxl
from pathlib import Path

data_dir = Path(__file__).parent / "data"
file_path = data_dir / "PMI Status Sheet.xlsx"
sheet_name = "Week ending 12-07-2026"

wb = openpyxl.load_workbook(file_path, data_only=True)
ws = wb[sheet_name]

print("=== Inspecting PMI sheet - Week ending 12-07-2026 ===")
for row_idx, row in enumerate(ws.iter_rows(values_only=True), 1):
    print(f"Row {row_idx}: {row}")

wb.close()
