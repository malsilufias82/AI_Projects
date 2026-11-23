#!/usr/bin/env python3
"""Print Data Team's week ending 26-06 sheet."""

import openpyxl

file_path = "data/Data Team - Daily Tracker.xlsx"
wb = openpyxl.load_workbook(file_path, read_only=True)
sheet_name = "Week ending 26-06"

if sheet_name in wb.sheetnames:
    print(f"\n📅 Sheet: {sheet_name}")
    ws = wb[sheet_name]
    for row_num, row in enumerate(ws.iter_rows(values_only=True), 1):
        if row_num <= 50:
            print(f"Row {row_num}: {row}")
wb.close()