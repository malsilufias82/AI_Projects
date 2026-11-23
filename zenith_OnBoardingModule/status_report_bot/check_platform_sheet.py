
import openpyxl
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

wb = openpyxl.load_workbook("./data/Project_Phoenix_ Status Update - Platform team.xlsx", read_only=True, data_only=True)
print("Platform team sheets:", wb.sheetnames)

target_sheet = "28-06-2026"
if target_sheet not in wb.sheetnames:
    target_sheet = wb.sheetnames[0]

print(f"Using sheet: {target_sheet}")
ws = wb[target_sheet]
print("\nFirst 30 rows:")
for i, row in enumerate(ws.iter_rows(values_only=True), 1):
    if i > 30:
        break
    print(f"{i:3}. {row}")
wb.close()

print("\n--- Product Team ---")
wb = openpyxl.load_workbook("./data/Project_Phoenix_ Status Update- Product Team.xlsx", read_only=True, data_only=True)
print("Product team sheets:", wb.sheetnames)
for sheet_name in wb.sheetnames:
    if "28-06" in sheet_name or "05-07" in sheet_name:
        target_sheet = sheet_name
        break
if not target_sheet:
    target_sheet = wb.sheetnames[0]
print(f"Using sheet: {target_sheet}")
ws = wb[target_sheet]
print("\nFirst 30 rows:")
for i, row in enumerate(ws.iter_rows(values_only=True), 1):
    if i > 30:
        break
    print(f"{i:3}. {row}")
wb.close()
