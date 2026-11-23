
#!/usr/bin/env python3
import openpyxl
from pathlib import Path

# Path to Product Engineering Excel file
excel_path = Path(__file__).parent / "data" / "Project_Phoenix_ Status Update- Product Team.xlsx"
sheet_name = "Week Ending 28-06-2026"

print(f"Opening Excel file: {excel_path}, sheet: {sheet_name}")
wb = openpyxl.load_workbook(excel_path, data_only=True)
ws = wb[sheet_name]

# Search for specific employees
target_employees = ["H N Sridhara", "Sanjeev Biswas", "Paritosh Saroj"]

print("\nChecking rows (starting from row 5):")
for i, row in enumerate(ws.iter_rows(values_only=True), 1):
    if i < 5:
        continue
    employee_name = row[3] if row[3] else ""
    if any(target in str(employee_name) for target in target_employees):
        print(f"\n=== Row {i} ===")
        print(f"  Employee: {employee_name}")
        print(f"  TL: {row[4]}")
        print(f"  Leave status (col F): {row[5]}")
        print(f"  Daily updates (cols G-L): {row[6:12]}")

wb.close()
