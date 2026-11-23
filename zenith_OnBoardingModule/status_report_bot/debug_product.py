#!/usr/bin/env python3
"""Debug the Product Team Excel sheet structure."""

import openpyxl

file_path = "data/Project_Phoenix_ Status Update- Product Team.xlsx"
wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
sheet_name = "Week Ending 28-06-2026"
ws = wb[sheet_name]

print(f"Sheet: {sheet_name}")
print("=" * 80)
for row_idx, row in enumerate(ws.iter_rows(values_only=True), 1):
    # Print first 50 rows
    if row_idx <= 50:
        print(f"Row {row_idx}: {row}")
wb.close()