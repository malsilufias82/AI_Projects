#!/usr/bin/env python3
"""Check the sheets and columns of the uploaded Excel files."""

import openpyxl
import os

data_folder = "data"
excel_files = [f for f in os.listdir(data_folder) if f.endswith(".xlsx")]

for filename in excel_files:
    file_path = os.path.join(data_folder, filename)
    print(f"\n📊 {filename}:")
    try:
        wb = openpyxl.load_workbook(file_path, read_only=True)
        print(f"  Sheets: {wb.sheetnames}")
        
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            # Get first row as headers
            headers = []
            for col in ws[1]:
                if col.value is not None:
                    headers.append(str(col.value).strip())
            print(f"  Sheet '{sheet_name}' headers: {headers}")
        wb.close()
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")