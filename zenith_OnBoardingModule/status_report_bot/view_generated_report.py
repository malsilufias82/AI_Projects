
import openpyxl
from pathlib import Path

reports_dir = Path(__file__).parent / "reports"
report_files = list(reports_dir.glob("status_report_week_ending_*.xlsx"))
if not report_files:
    print("No report files found!")
else:
    # Get the most recent one
    latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
    print(f"Viewing report: {latest_report.name}")
    print("="*80)
    wb = openpyxl.load_workbook(latest_report, data_only=True)
    ws = wb.active
    for row in ws.iter_rows(values_only=True):
        print("\t".join(str(cell) if cell is not None else "" for cell in row))
    wb.close()
