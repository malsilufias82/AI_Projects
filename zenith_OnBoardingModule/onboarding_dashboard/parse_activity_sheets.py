
from openpyxl import load_workbook
import pandas as pd

wb = load_workbook("data/BLK Onboarding Tracker.xlsx")

print("=== Phase1 - Machine Setup ===")
ws_phase1 = wb["Phase1 - Machine Setup"]
print(f"Number of rows: {ws_phase1.max_row}, columns: {ws_phase1.max_column}")

# Let's read first 10 rows and 20 columns
for row_idx in range(1, min(15, ws_phase1.max_row + 1)):
    row_vals = []
    for col_idx in range(1, min(25, ws_phase1.max_column + 1)):
        cell = ws_phase1.cell(row=row_idx, column=col_idx)
        row_vals.append((col_idx, cell.value))
    print(f"Row {row_idx}: {row_vals}")


print("\n=== Day0 Phase3 - Project Trainings ===")
ws_phase3 = wb["Day0 Phase3 - Project Trainings"]
print(f"Number of rows: {ws_phase3.max_row}, columns: {ws_phase3.max_column}")

for row_idx in range(1, min(15, ws_phase3.max_row + 1)):
    row_vals = []
    for col_idx in range(1, min(25, ws_phase3.max_column + 1)):
        cell = ws_phase3.cell(row=row_idx, column=col_idx)
        row_vals.append((col_idx, cell.value))
    print(f"Row {row_idx}: {row_vals}")
