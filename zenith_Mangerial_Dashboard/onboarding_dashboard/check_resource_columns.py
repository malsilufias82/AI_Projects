
import pandas as pd
from openpyxl import load_workbook

wb = load_workbook("data/BLK Onboarding Tracker.xlsx", data_only=True)
ws = wb["Resource List"]

headers = [cell.value for cell in ws[2]]
print("=== Resource List Columns ===")
for idx, h in enumerate(headers):
    print(f"Column {idx+1} (A:{chr(65+idx)}): {h}")

print("\n=== First 3 rows (including header) ===")
for row_idx in range(1, 4):
    row_vals = [cell.value for cell in ws[row_idx]]
    print(row_vals)
