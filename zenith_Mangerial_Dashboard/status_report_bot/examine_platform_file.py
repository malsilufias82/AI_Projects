#!/usr/bin/env python3
"""Print data from the latest week's sheet in Platform team file."""

import openpyxl

file_path = "data/Project_Phoenix_ Status Update - Platform team.xlsx"
wb = openpyxl.load_workbook(file_path, read_only=True)
print(f"Sheets in {file_path}: {wb.sheetnames}")

# Let's check the last few sheets which are likely the latest weeks
target_sheets = ["Week Ending 21-06-2026", "Week Ending 28-06-2026"]
for sheet_name in target_sheets:
    if sheet_name in wb.sheetnames:
        print(f"\n📅 Sheet: {sheet_name}")
        ws = wb[sheet_name]
        for row_num, row in enumerate(ws.iter_rows(values_only=True), 1):
            # Print first 20 rows
            if row_num <= 40:
                print(f"  Row {row_num}: {row}")
wb.close()