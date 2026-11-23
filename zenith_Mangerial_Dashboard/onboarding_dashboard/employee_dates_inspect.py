
from openpyxl import load_workbook

wb = load_workbook("data/BLK Onboarding Tracker.xlsx", data_only=True)
ws = wb["Phase1 - Machine Setup"]

print("=== Row 1 (Employee Names) and Row 2 (Dates) ===")
for col_idx in range(9, ws.max_column + 1):
    emp_name = ws.cell(row=2, column=col_idx).value  # Row 2 is index 1 in 0-based
    date_val = ws.cell(row=3, column=col_idx).value
    if emp_name:
        print(f"Col {col_idx}: Employee '{emp_name}', Date: {date_val}")
