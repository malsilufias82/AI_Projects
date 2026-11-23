
import pandas as pd
from openpyxl import load_workbook

wb = load_workbook("data/BLK Onboarding Tracker.xlsx", data_only=True)
ws = wb["Phase1 - Machine Setup"]

print("=== First 50 rows of Phase1 sheet ===")
for row_idx in range(0, 50):
    row_vals = []
    for col_idx in range(0, 15):
        cell_val = ws.cell(row=row_idx+1, column=col_idx+1).value
        row_vals.append(cell_val)
    print(f"Row {row_idx}: {row_vals}")
