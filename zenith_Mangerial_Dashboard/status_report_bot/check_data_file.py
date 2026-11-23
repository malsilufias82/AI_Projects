
import openpyxl
from pathlib import Path

data_file = Path(r"c:\Users\anamika.mishra\Downloads\status_report_bot\status_report_bot\data\status_report.xlsx")
wb = openpyxl.load_workbook(data_file, read_only=True, data_only=True)
print(f"Sheets in status_report.xlsx: {wb.sheetnames}")
print("\n---")
for sheet_name in wb.sheetnames:
    print(f"\n=== Sheet: {sheet_name} ===")
    ws = wb[sheet_name]
    for i, row in enumerate(ws.iter_rows(values_only=True), 1):
        if i > 20:
            print("... (more rows)")
            break
        print(f"Row {i}: {row}")
wb.close()
