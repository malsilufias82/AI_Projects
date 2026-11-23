
import openpyxl
from pathlib import Path

report_file = Path(r"c:\Users\anamika.mishra\Downloads\status_report_bot\status_report_bot\reports\status_report_week_ending_10-07-2026_120747.xlsx")
wb = openpyxl.load_workbook(report_file, data_only=True)
ws = wb.active
for i, row in enumerate(ws.iter_rows(values_only=True), 1):
    print(f"Row {i}: {row}")
wb.close()
