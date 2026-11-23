
import openpyxl
import os
from pathlib import Path

reports_dir = Path(__file__).parent / "reports"

print("Checking reports for 28-06-2026 and 05-07-2026:")
for report_file in reports_dir.glob("*.xlsx"):
    if "28-06-2026" in report_file.name or "05-07-2026" in report_file.name:
        print(f"\n=== {report_file.name} ===")
        wb = openpyxl.load_workbook(report_file)
        ws = wb.active
        for row in ws.iter_rows(values_only=True):
            print(row)
        wb.close()
