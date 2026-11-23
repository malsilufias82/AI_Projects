#!/usr/bin/env python3
"""Print Product team's latest week sheet."""

import openpyxl

file_path = "data/Project_Phoenix_ Status Update- Product Team.xlsx"
wb = openpyxl.load_workbook(file_path, read_only=True)
sheet_name = "Week Ending 28-06-2026"

if sheet_name in wb.sheetnames:
    print(f"\n📅 Sheet: {sheet_name}")
    ws = wb[sheet_name]
    for row_num, row in enumerate(ws.iter_rows(values_only=True), 1):
        print(f"Row {row_num}: {row}")
wb.close()