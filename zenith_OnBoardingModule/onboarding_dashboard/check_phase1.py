
from openpyxl import load_workbook

wb = load_workbook("data/BLK Onboarding Tracker.xlsx", data_only=True)
ws_phase1 = wb["Phase1 - Machine Setup"]

print("Phase1 sheet row 2 (employee names):")
for col_idx in range(9, 20):
    cell_val = ws_phase1.cell(row=2, column=col_idx).value
    print(f"  Column {col_idx}: {cell_val}")
