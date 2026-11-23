
import openpyxl
from pathlib import Path

data_dir = Path(__file__).parent / "data"
file_path = data_dir / "status_report.xlsx"

print("=== Inspecting status_report.xlsx ===")
wb = openpyxl.load_workbook(file_path, data_only=True)
print("Sheets:")
for sheet_name in wb.sheetnames:
    print(f"  - {sheet_name}")
    # Let's just print the first 20 rows of each sheet to see the structure
    ws = wb[sheet_name]
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i >= 20:
            break
        print(f"    Row {i+1}: {row}")
    print()

wb.close()
