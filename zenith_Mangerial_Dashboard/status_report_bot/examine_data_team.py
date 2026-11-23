#!/usr/bin/env python3
"""Print Data Team file's latest sheet."""

import openpyxl

file_path = "data/Data Team - Daily Tracker.xlsx"
wb = openpyxl.load_workbook(file_path, read_only=True)
print(f"Sheets: {wb.sheetnames}")
# Let's check the last sheet or a recent one
if wb.sheetnames:
    sheet_name = wb.sheetnames[-1]
    print(f"\n📅 Sheet: {sheet_name}")
    ws = wb[sheet_name]
    for row_num, row in enumerate(ws.iter_rows(values_only=True), 1):
        if row_num <= 50:
            print(f"Row {row_num}: {row}")
wb.close()